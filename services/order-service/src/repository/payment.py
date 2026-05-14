import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payment import Payments
from src.repository.base import BaseRepository


class PaymentRepository(BaseRepository[Payments]):
    def __init__(self):
        super().__init__(Payments)

    async def get_by_super_order(self, db: AsyncSession, super_order_id: uuid.UUID) -> list[Payments]:
        result = await db.execute(
            select(Payments).where(Payments.super_order_id == super_order_id)
        )
        return list(result.scalars().all())

    async def get_by_order_id(self, db: AsyncSession, order_id: uuid.UUID) -> list[Payments]:
        result = await db.execute(
            select(Payments).where(Payments.order_id == order_id)
        )
        return list(result.scalars().all())


payment_repo = PaymentRepository()
