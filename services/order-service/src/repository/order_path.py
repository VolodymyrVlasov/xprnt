import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.order import OrderPaths, Orders
from src.repository.base import BaseRepository


class OrderPathRepository(BaseRepository[OrderPaths]):
    def __init__(self):
        super().__init__(OrderPaths)

    async def get_by_order(self, db: AsyncSession, order_id: uuid.UUID) -> Optional[OrderPaths]:
        result = await db.execute(
            select(OrderPaths).where(OrderPaths.order_id == order_id)
        )
        return result.scalar_one_or_none()

    async def create_for_order(
        self,
        db: AsyncSession,
        order_id: uuid.UUID,
        path: Optional[str],
        docs_path: Optional[str],
    ) -> OrderPaths:
        obj = await self.create(db, {"order_id": order_id, "path": path, "docs_path": docs_path})
        # Link back to orders.order_path_id
        order = await db.get(Orders, order_id)
        if order:
            order.order_path_id = obj.id
            await db.commit()
        return obj


order_path_repo = OrderPathRepository()
