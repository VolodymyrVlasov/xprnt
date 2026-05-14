import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.product import PriceMultipliers, Prices
from src.repository.base import BaseRepository


class PriceMultiplierRepository(BaseRepository[PriceMultipliers]):
    def __init__(self):
        super().__init__(PriceMultipliers)


class PriceRepository(BaseRepository[Prices]):
    def __init__(self):
        super().__init__(Prices)

    async def get_by_product(self, db: AsyncSession, product_id: uuid.UUID) -> list[Prices]:
        result = await db.execute(
            select(Prices).where(Prices.product_id == product_id).order_by(Prices.start_at)
        )
        return list(result.scalars().all())

    async def get_active_for_product(self, db: AsyncSession, product_id: uuid.UUID) -> Optional[Prices]:
        result = await db.execute(
            select(Prices).where(
                Prices.product_id == product_id,
                Prices.finish_at.is_(None),
            )
        )
        return result.scalar_one_or_none()


price_multiplier_repo = PriceMultiplierRepository()
price_repo = PriceRepository()
