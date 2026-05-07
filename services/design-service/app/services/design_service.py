import json
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.design import DesignType
from app.repository.design_repository import design_repo
from app.schemas.design import DesignResponse
from app.utils.file_storage import BUCKET_PREVIEWS, BUCKET_UPLOADS, MinIOClient
from app.utils.preview_generator import generate_preview
from app.utils.technical_validation import validate_design_metadata

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB

CONTENT_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "pdf": "application/pdf",
}


async def upload_customer_design(
    file: UploadFile,
    target_width_mm: Optional[float],
    target_height_mm: Optional[float],
    target_color: str,
    target_dpi: int,
    db: AsyncSession,
    minio: MinIOClient,
    redis: Redis,
) -> DesignResponse:
    # 1. Validate format
    filename = file.filename or "upload"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 2. Read bytes
    file_data = await file.read()
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // 1024 // 1024} MB",
        )

    # 3. Generate object name for original
    object_name = MinIOClient.generate_object_name(filename, prefix="tmp")

    # 4. Upload original to MinIO uploads bucket
    content_type = CONTENT_TYPES.get(ext, "application/octet-stream")
    await minio.upload_file(BUCKET_UPLOADS, object_name, file_data, content_type)
    logger.info("Uploaded original: %s/%s", BUCKET_UPLOADS, object_name)

    # 5. Generate preview
    preview_bytes = await generate_preview(file_data, ext)

    # 6. Upload preview if generated
    preview_path: Optional[str] = None
    if preview_bytes is not None:
        preview_object_name = MinIOClient.generate_object_name(filename, prefix="previews")
        await minio.upload_file(BUCKET_PREVIEWS, preview_object_name, preview_bytes, "image/jpeg")
        preview_path = preview_object_name
        logger.info("Uploaded preview: %s/%s", BUCKET_PREVIEWS, preview_object_name)

    # 7. Validate metadata (stub — uses in-memory bytes)
    metadata = validate_design_metadata(
        file_data=file_data,
        file_ext=ext,
        target_dpi=target_dpi,
        target_width_mm=target_width_mm,
        target_height_mm=target_height_mm,
        target_color=target_color,
    )

    # 8. Write to DB
    customer_design = await design_repo.create_customer_design(
        db,
        filename=filename,
        path=object_name,
        preview_path=preview_path,
        metadata=metadata.model_dump(),
    )
    design = await design_repo.create_design(
        db,
        design_type=DesignType.CUSTOMER_DESIGN,
        customer_design_id=customer_design.id,
        fpd_design_id=None,
    )

    # 9. Push to Redis sync queue
    try:
        await redis.lpush(
            "sync:designs",
            json.dumps(
                {
                    "design_id": str(design.id),
                    "customer_design_id": str(customer_design.id),
                    "object_name": object_name,
                    "created_at": datetime.utcnow().isoformat(),
                }
            ),
        )
    except Exception as exc:
        logger.error("Redis lpush failed: %s", exc)

    # 10. Build response
    file_url = await minio.get_file_url(BUCKET_UPLOADS, object_name)
    preview_url: Optional[str] = None
    if preview_path:
        preview_url = await minio.get_file_url(BUCKET_PREVIEWS, preview_path)

    return DesignResponse(
        id=design.id,
        designType=design.designType,
        fileURL=file_url,
        previewURL=preview_url,
        customerDesign=design.customerDesign,
    )
