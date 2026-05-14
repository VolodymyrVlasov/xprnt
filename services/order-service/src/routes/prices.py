import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db, require_role
from src.models.user import Users
from src.repository.price import price_repo
from src.repository.product import product_repo
from src.schemas.price import PriceCreate, PriceResponse

router = APIRouter(prefix="/prices", tags=["prices"])


def _now_str() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@router.post("/", response_model=PriceResponse, status_code=status.HTTP_201_CREATED)
async def create_price(
    data: PriceCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    product = await product_repo.get(db, data.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Close the currently active price if one exists
    old_price = await price_repo.get_active_for_product(db, data.product_id)

    new_price = await price_repo.create(
        db,
        {
            "product_id": data.product_id,
            "prime_cost_eur": data.prime_cost_eur,
            "fx_rate_used": data.fx_rate_used,
            "price_multiplier_id": data.price_multiplier_id,
            "values": data.values,
            "start_at": data.start_at or _now_str(),
            "previous_price_id": old_price.id if old_price else None,
        },
    )

    if old_price:
        await price_repo.update(db, old_price, {
            "finish_at": _now_str(),
            "next_price_id": new_price.id,
        })

    # Update product's active price
    await product_repo.update(db, product, {"active_price_id": new_price.id})

    return new_price


@router.get("/product/{product_id}", response_model=list[PriceResponse])
async def get_price_history(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await price_repo.get_by_product(db, product_id)


@router.get("/product/{product_id}/active", response_model=PriceResponse)
async def get_active_price(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    price = await price_repo.get_active_for_product(db, product_id)
    if not price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active price for product")
    return price


@router.get("/{id}", response_model=PriceResponse)
async def get_price(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    price = await price_repo.get(db, id)
    if not price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    return price
