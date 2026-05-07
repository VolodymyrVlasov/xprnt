import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_current_user_optional, get_db
from src.models.cart import CartStatus
from src.models.user import Users
from src.repository.cart import cart_repo
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

_STAFF_ROLES = ("manager", "admin", "prepress", "postpress")


def _assert_cart_access(cart, current_user: Optional[Users]) -> None:
    """Raise 403 if an authenticated non-staff user doesn't own the cart."""
    if current_user is None:
        return  # anonymous access allowed — caller knows the cart_id
    role_name = current_user.role.role if current_user.role else ""
    if role_name in _STAFF_ROLES:
        return
    if cart.customer_id is not None and cart.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.post("/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def create_cart_route(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Users] = Depends(get_current_user_optional),
):
    customer_id = current_user.id if current_user else None
    return await create_cart(db, customer_id=customer_id)


@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart_route(
    cart_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Users] = Depends(get_current_user_optional),
):
    cart = await get_cart(db, cart_id)
    if current_user and cart.customer_id:
        _assert_cart_access(cart, current_user)
    return cart


@router.post("/{cart_id}/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_item_route(
    cart_id: uuid.UUID,
    data: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Users] = Depends(get_current_user_optional),
):
    cart = await cart_repo.get(db, cart_id)
    if cart:
        _assert_cart_access(cart, current_user)
    return await add_item(db, cart_id, data)


@router.put("/{cart_id}/items/{item_id}", response_model=CartResponse)
async def update_item_route(
    cart_id: uuid.UUID,
    item_id: uuid.UUID,
    data: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Users] = Depends(get_current_user_optional),
):
    cart = await cart_repo.get(db, cart_id)
    if cart:
        _assert_cart_access(cart, current_user)
    return await update_item(db, cart_id, item_id, data)


@router.delete("/{cart_id}/items/{item_id}", response_model=CartResponse)
async def remove_item_route(
    cart_id: uuid.UUID,
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[Users] = Depends(get_current_user_optional),
):
    cart = await cart_repo.get(db, cart_id)
    if cart:
        _assert_cart_access(cart, current_user)
    return await remove_item(db, cart_id, item_id)


@router.post("/{cart_id}/lock", response_model=CartResponse)
async def lock_cart_route(
    cart_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    cart = await cart_repo.get(db, cart_id)
    if cart:
        _assert_cart_access(cart, current_user)
    return await lock_cart(db, cart_id)


@router.post("/{cart_id}/claim", response_model=CartResponse)
async def claim_cart_route(
    cart_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Assign an anonymous cart to the authenticated user."""
    cart = await cart_repo.get(db, cart_id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    if cart.customer_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart already claimed")
    if cart.status != CartStatus.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is not active")
    await cart_repo.update(db, cart, {"customer_id": current_user.id})
    return await get_cart(db, cart_id)
