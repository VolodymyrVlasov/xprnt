import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.order import Orders, SuperOrderStatus, SuperOrders
from src.repository.base import BaseRepository


class SuperOrderRepository(BaseRepository[SuperOrders]):
    def __init__(self):
        super().__init__(SuperOrders)

    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[SuperOrders]:
        result = await db.execute(
            select(SuperOrders)
            .where(SuperOrders.id == id)
            .options(selectinload(SuperOrders.orders))
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        company_id: Optional[uuid.UUID] = None,
        status: Optional[SuperOrderStatus] = None,
    ) -> list[SuperOrders]:
        q = select(SuperOrders).options(selectinload(SuperOrders.orders))
        if company_id:
            q = q.where(SuperOrders.company_id == company_id)
        if status:
            q = q.where(SuperOrders.status == status)
        q = q.offset(skip).limit(limit)
        result = await db.execute(q)
        return list(result.scalars().all())

    async def get_by_company(
        self,
        db: AsyncSession,
        company_id: uuid.UUID,
        billing_period_start=None,
        billing_period_end=None,
    ) -> list[SuperOrders]:
        q = (
            select(SuperOrders)
            .where(SuperOrders.company_id == company_id)
            .options(selectinload(SuperOrders.orders))
        )
        if billing_period_start:
            q = q.where(SuperOrders.billing_period_start >= billing_period_start)
        if billing_period_end:
            q = q.where(SuperOrders.billing_period_end <= billing_period_end)
        result = await db.execute(q)
        return list(result.scalars().all())

    async def add_order(
        self, db: AsyncSession, super_order_id: uuid.UUID, order_id: uuid.UUID
    ) -> Optional[SuperOrders]:
        order = await db.get(Orders, order_id)
        if not order:
            return None
        order.super_order_id = super_order_id
        await db.commit()
        await db.refresh(order)
        return await self.get(db, super_order_id)

    async def remove_order(
        self, db: AsyncSession, super_order_id: uuid.UUID, order_id: uuid.UUID
    ) -> Optional[SuperOrders]:
        order = await db.get(Orders, order_id)
        if not order:
            return None
        order.super_order_id = None
        await db.commit()
        return await self.get(db, super_order_id)


super_order_repo = SuperOrderRepository()
