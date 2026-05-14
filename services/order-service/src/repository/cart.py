import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.cart import Cart, CartItemProducts, CartItems, CartStatus
from src.repository.base import BaseRepository


class CartRepository(BaseRepository[Cart]):
    def __init__(self):
        super().__init__(Cart)

    async def get_with_items(self, db: AsyncSession, cart_id: uuid.UUID) -> Optional[Cart]:
        result = await db.execute(
            select(Cart)
            .where(Cart.id == cart_id)
            .options(
                selectinload(Cart.items).selectinload(CartItems.products)
            )
        )
        return result.scalar_one_or_none()

    async def get_active_for_user(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[Cart]:
        result = await db.execute(
            select(Cart).where(
                Cart.customer_id == user_id,
                Cart.status == CartStatus.active,
            )
        )
        return result.scalar_one_or_none()


class CartItemRepository(BaseRepository[CartItems]):
    def __init__(self):
        super().__init__(CartItems)

    async def get_item(
        self, db: AsyncSession, cart_id: uuid.UUID, item_id: uuid.UUID
    ) -> Optional[CartItems]:
        result = await db.execute(
            select(CartItems).where(
                CartItems.id == item_id,
                CartItems.cart_id == cart_id,
            )
        )
        return result.scalar_one_or_none()


class CartItemProductRepository(BaseRepository[CartItemProducts]):
    def __init__(self):
        super().__init__(CartItemProducts)


cart_repo = CartRepository()
cart_item_repo = CartItemRepository()
cart_item_product_repo = CartItemProductRepository()
