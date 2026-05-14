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
from app.schemas.design import ClaimDesignsResponse, DesignResponse
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
    guest_session_id: Optional[str] = None,
    user_id: Optional[uuid.UUID] = None,
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

    # 3. Generate staging object name (tmp/)
    content_type = CONTENT_TYPES.get(ext, "application/octet-stream")
    tmp_object_name = MinIOClient.generate_object_name(filename, prefix="tmp")

    # 4. Upload original to MinIO uploads bucket (staging)
    await minio.upload_file(BUCKET_UPLOADS, tmp_object_name, file_data, content_type)
    logger.info("Uploaded to staging: %s/%s", BUCKET_UPLOADS, tmp_object_name)

    # 5. Generate preview
    preview_bytes = await generate_preview(file_data, ext)

    # 6. Upload preview if generated
    preview_path: Optional[str] = None
    if preview_bytes is not None:
        preview_object_name = MinIOClient.generate_object_name(filename, prefix="previews")
        await minio.upload_file(BUCKET_PREVIEWS, preview_object_name, preview_bytes, "image/jpeg")
        preview_path = preview_object_name
        logger.info("Uploaded preview: %s/%s", BUCKET_PREVIEWS, preview_object_name)

    # 7. Validate metadata
    metadata = validate_design_metadata(
        file_data=file_data,
        file_ext=ext,
        target_dpi=target_dpi,
        target_width_mm=target_width_mm,
        target_height_mm=target_height_mm,
        target_color=target_color,
    )

    # 8. Write to DB (path initially points to staging location)
    customer_design = await design_repo.create_customer_design(
        db,
        filename=filename,
        path=tmp_object_name,
        preview_path=preview_path,
        metadata=metadata.model_dump(),
        guest_session_id=guest_session_id,
        user_id=user_id,
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
                    "object_name": tmp_object_name,
                    "created_at": datetime.utcnow().isoformat(),
                }
            ),
        )
    except Exception as exc:
        logger.warning(
            "Redis lpush failed for design %s — sync event not queued: %s",
            design.id,
            exc,
        )

    # 10. Move original from staging (tmp/) to permanent location, then delete tmp
    permanent_path = f"{customer_design.id}/{filename}"
    try:
        await minio.upload_file(BUCKET_UPLOADS, permanent_path, file_data, content_type)
        await design_repo.update_customer_design(db, customer_design, {"path": permanent_path})
        await minio.delete_file(BUCKET_UPLOADS, tmp_object_name)
        logger.info("Moved '%s' → permanent '%s'", tmp_object_name, permanent_path)
    except Exception as exc:
        logger.warning(
            "Cleanup failed for design %s — tmp file '%s' may remain: %s",
            design.id,
            tmp_object_name,
            exc,
        )
        # Keep tmp_object_name as the active path on failure
        permanent_path = tmp_object_name

    # 11. Build response
    file_url = await minio.get_file_url(BUCKET_UPLOADS, permanent_path)
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


async def get_design(
    design_id: uuid.UUID,
    db: AsyncSession,
    minio: MinIOClient,
) -> DesignResponse:
    design = await design_repo.get_design_by_id(db, design_id)
    if not design:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Design not found")

    file_url = ""
    preview_url: Optional[str] = None

    if design.customerDesign:
        file_url = await minio.get_file_url(BUCKET_UPLOADS, design.customerDesign.path)
        if design.customerDesign.previewPath:
            preview_url = await minio.get_file_url(BUCKET_PREVIEWS, design.customerDesign.previewPath)

    return DesignResponse(
        id=design.id,
        designType=design.designType,
        fileURL=file_url,
        previewURL=preview_url,
        customerDesign=design.customerDesign,
    )


async def claim_designs(
    guest_session_id: str,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> ClaimDesignsResponse:
    claimed = await design_repo.claim_by_session(db, guest_session_id, user_id)
    logger.info("Claimed %d design(s) for session %s → user %s", claimed, guest_session_id, user_id)
    return ClaimDesignsResponse(claimed=claimed)
