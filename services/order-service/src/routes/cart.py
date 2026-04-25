import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import Users
from src.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from src.services.cart import (
    add_item,
    create_cart,
    get_cart,
    lock_cart,
    remove_item,
    update_item,
)

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart_route(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Users] = Depends(get_current_user),
):
    customer_id = current_user.id if current_user else None
    return await create_cart(db, customer_id=customer_id)


@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart_route(cart_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await get_cart(db, cart_id)


@router.post("/{cart_id}/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_item_route(
    cart_id: uuid.UUID, data: CartItemCreate, db: AsyncSession = Depends(get_db)
):
    return await add_item(db, cart_id, data)


@router.put("/{cart_id}/items/{item_id}", response_model=CartResponse)
async def update_item_route(
    cart_id: uuid.UUID,
    item_id: uuid.UUID,
    data: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await update_item(db, cart_id, item_id, data)


@router.delete("/{cart_id}/items/{item_id}", response_model=CartResponse)
async def remove_item_route(
    cart_id: uuid.UUID, item_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await remove_item(db, cart_id, item_id)


@router.post("/{cart_id}/lock", response_model=CartResponse)
async def lock_cart_route(cart_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await lock_cart(db, cart_id)
