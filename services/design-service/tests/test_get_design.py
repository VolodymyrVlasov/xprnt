"""Tests for GET /designs/{design_id}."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.design import DesignType


def _make_mock_customer_design(cd_id: uuid.UUID) -> MagicMock:
    cd = MagicMock()
    cd.id = cd_id
    cd.filename = "photo.jpg"
    cd.path = f"{cd_id}/photo.jpg"
    cd.previewPath = f"previews/{cd_id}_preview.jpg"
    cd.design_metadata = {
        "current": {
            "dpi": {"value": 300, "isValid": True},
            "width": {"value": 210.0, "isValid": True},
            "height": {"value": 297.0, "isValid": True},
            "color": {"value": "cmyk", "isValid": True},
        },
        "target": {"dpi": 300, "width": 210.0, "height": 297.0, "color": "cmyk"},
    }
    return cd


def _make_mock_design(design_id: uuid.UUID, customer_design: MagicMock) -> MagicMock:
    d = MagicMock()
    d.id = design_id
    d.designType = DesignType.CUSTOMER_DESIGN
    d.customerDesign = customer_design
    d.fpdDesign = None
    return d


async def test_get_design_returns_200_with_correct_shape(async_client):
    client, mock_minio, _ = async_client

    cd_id = uuid.uuid4()
    design_id = uuid.uuid4()
    mock_cd = _make_mock_customer_design(cd_id)
    mock_design = _make_mock_design(design_id, mock_cd)

    with patch("app.services.design_service.design_repo") as mock_repo:
        mock_repo.get_design_by_id = AsyncMock(return_value=mock_design)

        response = await client.get(f"/designs/{design_id}")

    assert response.status_code == 200
    data = response.json()

    # Top-level fields
    assert data["id"] == str(design_id)
    assert data["designType"] == "CUSTOMER_DESIGN"
    assert data["fileURL"] == "http://minio/bucket/file.jpg"
    assert data["previewURL"] == "http://minio/bucket/file.jpg"

    # customerDesign shape
    cd = data["customerDesign"]
    assert cd["id"] == str(cd_id)
    assert cd["filename"] == "photo.jpg"
    assert "metadata" in cd

    current = cd["metadata"]["current"]
    for field in ("dpi", "width", "height", "color"):
        assert field in current

    # Both MinIO URL calls were made (file + preview)
    assert mock_minio.get_file_url.call_count == 2


async def test_get_design_returns_404_for_unknown_id(async_client):
    client, _, _ = async_client

    with patch("app.services.design_service.design_repo") as mock_repo:
        mock_repo.get_design_by_id = AsyncMock(return_value=None)

        response = await client.get(f"/designs/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Design not found"


async def test_get_design_calls_repo_with_correct_id(async_client):
    client, _, _ = async_client

    target_id = uuid.uuid4()

    with patch("app.services.design_service.design_repo") as mock_repo:
        mock_repo.get_design_by_id = AsyncMock(return_value=None)

        await client.get(f"/designs/{target_id}")

    called_with_id = mock_repo.get_design_by_id.call_args[0][1]
    assert called_with_id == target_id
