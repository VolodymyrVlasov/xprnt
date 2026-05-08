import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_minio, get_redis
from app.schemas.design import DesignResponse
from app.services import design_service
from app.utils.file_storage import MinIOClient

router = APIRouter(prefix="/designs", tags=["designs"])


@router.post("/upload", response_model=DesignResponse, status_code=201)
async def upload_design(
    file: UploadFile = File(...),
    targetWidth: Optional[float] = Form(None),
    targetHeight: Optional[float] = Form(None),
    targetColor: str = Form("cmyk"),
    targetDpi: int = Form(300),
    db: AsyncSession = Depends(get_db),
    minio: MinIOClient = Depends(get_minio),
    redis: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    return await design_service.upload_customer_design(
        file=file,
        target_width_mm=targetWidth,
        target_height_mm=targetHeight,
        target_color=targetColor,
        target_dpi=targetDpi,
        db=db,
        minio=minio,
        redis=redis,
    )


@router.get("/{design_id}", response_model=DesignResponse)
async def get_design(
    design_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    minio: MinIOClient = Depends(get_minio),
    current_user: dict = Depends(get_current_user),
):
    return await design_service.get_design(design_id=design_id, db=db, minio=minio)
