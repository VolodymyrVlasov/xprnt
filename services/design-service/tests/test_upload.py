"""Tests for POST /designs/upload."""
import io
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from PIL import Image

from app.models.design import DesignType


def _make_jpeg(width: int = 100, height: int = 100, dpi: int = 300) -> bytes:
    img = Image.new("RGB", (width, height), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", dpi=(dpi, dpi))
    return buf.getvalue()


def _make_mock_customer_design(cd_id: uuid.UUID, filename: str = "test.jpg") -> MagicMock:
    cd = MagicMock()
    cd.id = cd_id
    cd.filename = filename
    cd.path = f"{cd_id}/{filename}"
    cd.previewPath = f"previews/{cd_id}_preview.jpg"
    cd.design_metadata = {
        "current": {
            "dpi": {"value": 300, "isValid": True},
            "width": {"value": 8.5, "isValid": True},
            "height": {"value": 8.5, "isValid": True},
            "color": {"value": "rgb", "isValid": True},
        },
        "target": {"dpi": 300, "width": None, "height": None, "color": "rgb"},
    }
    return cd


def _make_mock_design(design_id: uuid.UUID, customer_design: MagicMock) -> MagicMock:
    d = MagicMock()
    d.id = design_id
    d.designType = DesignType.CUSTOMER_DESIGN
    d.customerDesign = customer_design
    d.fpdDesign = None
    return d


async def test_upload_returns_201_with_correct_shape(async_client):
    client, mock_minio, mock_redis = async_client

    cd_id = uuid.uuid4()
    design_id = uuid.uuid4()
    mock_cd = _make_mock_customer_design(cd_id)
    mock_design = _make_mock_design(design_id, mock_cd)

    with patch("app.services.design_service.design_repo") as mock_repo:
        mock_repo.create_customer_design = AsyncMock(return_value=mock_cd)
        mock_repo.create_design = AsyncMock(return_value=mock_design)
        mock_repo.update_customer_design = AsyncMock(return_value=mock_cd)

        response = await client.post(
            "/designs/upload",
            files={"file": ("test.jpg", _make_jpeg(), "image/jpeg")},
            data={"targetDpi": "300", "targetColor": "rgb"},
        )

    assert response.status_code == 201
    data = response.json()

    # Top-level fields
    assert data["id"] == str(design_id)
    assert data["designType"] == "CUSTOMER_DESIGN"
    assert "fileURL" in data
    assert data["fileURL"] != ""

    # customerDesign shape
    cd = data["customerDesign"]
    assert cd["id"] == str(cd_id)
    assert cd["filename"] == "test.jpg"
    assert "path" in cd

    # metadata structure
    meta = cd["metadata"]
    assert "current" in meta
    assert "target" in meta
    current = meta["current"]
    for field in ("dpi", "width", "height", "color"):
        assert field in current
        assert "value" in current[field]
        assert "isValid" in current[field]


async def test_upload_calls_db_and_minio(async_client):
    """Verify that DB writes and MinIO uploads are called during a successful upload."""
    client, mock_minio, mock_redis = async_client

    cd_id = uuid.uuid4()
    design_id = uuid.uuid4()
    mock_cd = _make_mock_customer_design(cd_id)
    mock_design = _make_mock_design(design_id, mock_cd)

    with patch("app.services.design_service.design_repo") as mock_repo:
        mock_repo.create_customer_design = AsyncMock(return_value=mock_cd)
        mock_repo.create_design = AsyncMock(return_value=mock_design)
        mock_repo.update_customer_design = AsyncMock(return_value=mock_cd)

        response = await client.post(
            "/designs/upload",
            files={"file": ("test.jpg", _make_jpeg(), "image/jpeg")},
            data={"targetDpi": "300", "targetColor": "rgb"},
        )

    assert response.status_code == 201

    # DB creates were called
    mock_repo.create_customer_design.assert_called_once()
    mock_repo.create_design.assert_called_once()

    # Permanent path update and tmp cleanup were called
    mock_repo.update_customer_design.assert_called_once()
    mock_minio.delete_file.assert_called_once()

    # MinIO upload called at least twice (original + permanent; preview if generated)
    assert mock_minio.upload_file.call_count >= 2

    # Redis sync event was pushed
    mock_redis.lpush.assert_called_once()


async def test_upload_rejects_unsupported_extension(async_client):
    client, _, _ = async_client

    response = await client.post(
        "/designs/upload",
        files={"file": ("design.psd", b"fake data", "application/octet-stream")},
        data={"targetDpi": "300", "targetColor": "rgb"},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
