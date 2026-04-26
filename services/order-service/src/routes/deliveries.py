import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db, require_role
from src.models.user import Users
from src.repository.delivery import delivery_repo
from src.schemas.delivery import DeliveryCreate, DeliveryResponse

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.post("/", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    data: DeliveryCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    return await delivery_repo.create(db, data.model_dump())


@router.get("/", response_model=list[DeliveryResponse])
async def list_deliveries(
    has_ttn: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    if has_ttn is not None:
        return await delivery_repo.get_with_ttn(db, has_ttn)
    return await delivery_repo.get_all(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=DeliveryResponse)
async def get_delivery(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    obj = await delivery_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    return obj


@router.put("/{id}", response_model=DeliveryResponse)
async def update_delivery(
    id: uuid.UUID,
    ttn_number: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    obj = await delivery_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    if ttn_number is not None:
        return await delivery_repo.update(db, obj, {"ttn_number": ttn_number})
    return obj
