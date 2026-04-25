import uuid
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cart import Cart, CartItemProducts, CartItems, CartStatus
from src.repository.cart import cart_item_product_repo, cart_item_repo, cart_repo
from src.schemas.cart import CartItemCreate, CartItemUpdate


async def create_cart(db: AsyncSession, customer_id: Optional[uuid.UUID] = None) -> Cart:
    return await cart_repo.create(
        db, {"customer_id": customer_id, "status": CartStatus.active, "total_price": Decimal("0.00")}
    )


async def get_cart(db: AsyncSession, cart_id: uuid.UUID) -> Cart:
    cart = await cart_repo.get_with_items(db, cart_id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart


async def add_item(db: AsyncSession, cart_id: uuid.UUID, data: CartItemCreate) -> Cart:
    cart = await cart_repo.get_with_items(db, cart_id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    if cart.status != CartStatus.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is not active")

    total_price = data.unit_price * data.amount
    item = await cart_item_repo.create(
        db,
        {
            "cart_id": cart_id,
            "category_id": data.category_id,
            "cart_item_type": data.cart_item_type,
            "name": data.name,
            "short_name": data.short_name,
            "amount": data.amount,
            "unit_price": data.unit_price,
            "total_price": total_price,
            "design_id": data.design_id,
        },
    )

    for prod in data.products:
        await cart_item_product_repo.create(
            db,
            {
                "cart_item_id": item.id,
                "product_id": prod.product_id,
                "name": prod.name,
                "amount": prod.amount,
                "price": prod.price,
                "price_total": prod.price * prod.amount,
            },
        )

    # Recalculate cart total
    await _recalculate_cart_total(db, cart)
    return await cart_repo.get_with_items(db, cart_id)  # type: ignore[return-value]


async def update_item(
    db: AsyncSession, cart_id: uuid.UUID, item_id: uuid.UUID, data: CartItemUpdate
) -> Cart:
    item = await cart_item_repo.get_item(db, cart_id, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    updates = data.model_dump(exclude_none=True)
    if "amount" in updates or "unit_price" in updates:
        amount = updates.get("amount", item.amount)
        unit_price = updates.get("unit_price", item.unit_price)
        updates["total_price"] = unit_price * amount

    await cart_item_repo.update(db, item, updates)

    cart = await cart_repo.get_with_items(db, cart_id)
    await _recalculate_cart_total(db, cart)  # type: ignore[arg-type]
    return await cart_repo.get_with_items(db, cart_id)  # type: ignore[return-value]


async def remove_item(db: AsyncSession, cart_id: uuid.UUID, item_id: uuid.UUID) -> Cart:
    item = await cart_item_repo.get_item(db, cart_id, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    await cart_item_repo.delete(db, item_id)

    cart = await cart_repo.get_with_items(db, cart_id)
    await _recalculate_cart_total(db, cart)  # type: ignore[arg-type]
    return await cart_repo.get_with_items(db, cart_id)  # type: ignore[return-value]


async def lock_cart(db: AsyncSession, cart_id: uuid.UUID) -> Cart:
    cart = await cart_repo.get(db, cart_id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    if cart.status != CartStatus.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is not active")
    return await cart_repo.update(db, cart, {"status": CartStatus.locked})


async def _recalculate_cart_total(db: AsyncSession, cart: Cart) -> None:
    total = sum((item.total_price for item in cart.items), Decimal("0.00"))
    await cart_repo.update(db, cart, {"total_price": total})
