import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db, require_role
from src.models.user import Users
from src.repository.price import price_multiplier_repo
from src.schemas.price import PriceMultiplierCreate, PriceMultiplierResponse, PriceMultiplierUpdate

router = APIRouter(prefix="/price-multipliers", tags=["price-multipliers"])


@router.get("/", response_model=list[PriceMultiplierResponse])
async def list_price_multipliers(db: AsyncSession = Depends(get_db)):
    return await price_multiplier_repo.get_all(db, limit=100)


@router.post("/", response_model=PriceMultiplierResponse, status_code=status.HTTP_201_CREATED)
async def create_price_multiplier(
    data: PriceMultiplierCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("admin")),
):
    return await price_multiplier_repo.create(db, {"values": data.values})


@router.get("/{id}", response_model=PriceMultiplierResponse)
async def get_price_multiplier(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    obj = await price_multiplier_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price multiplier not found")
    return obj


@router.put("/{id}", response_model=PriceMultiplierResponse)
async def update_price_multiplier(
    id: uuid.UUID,
    data: PriceMultiplierUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("admin")),
):
    obj = await price_multiplier_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price multiplier not found")
    return await price_multiplier_repo.update(db, obj, {"values": data.values})
