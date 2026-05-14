from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.delivery import Deliveries
from src.repository.base import BaseRepository


class DeliveryRepository(BaseRepository[Deliveries]):
    def __init__(self):
        super().__init__(Deliveries)

    async def get_with_ttn(self, db: AsyncSession, has_ttn: bool) -> list[Deliveries]:
        if has_ttn:
            result = await db.execute(
                select(Deliveries).where(Deliveries.ttn_number.isnot(None))
            )
        else:
            result = await db.execute(
                select(Deliveries).where(Deliveries.ttn_number.is_(None))
            )
        return list(result.scalars().all())


delivery_repo = DeliveryRepository()
