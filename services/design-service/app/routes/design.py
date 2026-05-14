import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Header, UploadFile
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional, get_minio, get_redis
from app.schemas.design import ClaimDesignsRequest, ClaimDesignsResponse, DesignResponse
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
    x_guest_session_id: Optional[str] = Header(None, alias="X-Guest-Session-ID"),
    db: AsyncSession = Depends(get_db),
    minio: MinIOClient = Depends(get_minio),
    redis: Redis = Depends(get_redis),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    user_id: Optional[uuid.UUID] = None
    if current_user and current_user.get("sub"):
        try:
            user_id = uuid.UUID(current_user["sub"])
        except (ValueError, AttributeError):
            pass

    return await design_service.upload_customer_design(
        file=file,
        target_width_mm=targetWidth,
        target_height_mm=targetHeight,
        target_color=targetColor,
        target_dpi=targetDpi,
        db=db,
        minio=minio,
        redis=redis,
        guest_session_id=x_guest_session_id,
        user_id=user_id,
    )


@router.post("/claim", response_model=ClaimDesignsResponse)
async def claim_designs(
    body: ClaimDesignsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Claim all guest designs for a session — assigns user_id to unclaimed records."""
    user_id = uuid.UUID(current_user["sub"])
    return await design_service.claim_designs(
        guest_session_id=body.guest_session_id,
        user_id=user_id,
        db=db,
    )


@router.get("/{design_id}", response_model=DesignResponse)
async def get_design(
    design_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    minio: MinIOClient = Depends(get_minio),
    current_user: dict = Depends(get_current_user),
):
    return await design_service.get_design(design_id=design_id, db=db, minio=minio)
