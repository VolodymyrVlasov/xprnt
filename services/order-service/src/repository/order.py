import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.order import OrderNumbers, Orders, OrderStatus
from src.repository.base import BaseRepository


class OrderNumberRepository(BaseRepository[OrderNumbers]):
    def __init__(self):
        super().__init__(OrderNumbers)

    async def create_number(self, db: AsyncSession, created_by: Optional[uuid.UUID] = None) -> OrderNumbers:
        obj = OrderNumbers(created_by=created_by)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj


class OrderRepository(BaseRepository[Orders]):
    def __init__(self):
        super().__init__(Orders)

    async def get_with_details(self, db: AsyncSession, order_id: uuid.UUID) -> Optional[Orders]:
        result = await db.execute(
            select(Orders)
            .where(Orders.id == order_id)
            .options(selectinload(Orders.cart))
        )
        return result.scalar_one_or_none()

    async def get_by_customer(
        self, db: AsyncSession, customer_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> list[Orders]:
        result = await db.execute(
            select(Orders)
            .where(Orders.customer_id == customer_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_company(
        self, db: AsyncSession, company_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> list[Orders]:
        result = await db.execute(
            select(Orders)
            .where(Orders.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(
        self, db: AsyncSession, status: OrderStatus, skip: int = 0, limit: int = 20
    ) -> list[Orders]:
        result = await db.execute(
            select(Orders).where(Orders.status == status).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_cart(self, db: AsyncSession, cart_id: uuid.UUID) -> Optional[Orders]:
        result = await db.execute(select(Orders).where(Orders.cart_id == cart_id))
        return result.scalar_one_or_none()


order_number_repo = OrderNumberRepository()
order_repo = OrderRepository()
