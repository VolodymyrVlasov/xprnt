import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.reference import (
    DeliveryTypes,
    MeasurementUnits,
    PaymentTypes,
    Roles,
    Sellers,
    Sizes,
    Teams,
)
from src.repository.base import BaseRepository


class RoleRepository(BaseRepository[Roles]):
    def __init__(self):
        super().__init__(Roles)

    async def get_by_name(self, db: AsyncSession, role: str) -> Optional[Roles]:
        result = await db.execute(select(Roles).where(Roles.role == role))
        return result.scalar_one_or_none()


class TeamRepository(BaseRepository[Teams]):
    def __init__(self):
        super().__init__(Teams)


class DeliveryTypeRepository(BaseRepository[DeliveryTypes]):
    def __init__(self):
        super().__init__(DeliveryTypes)


class PaymentTypeRepository(BaseRepository[PaymentTypes]):
    def __init__(self):
        super().__init__(PaymentTypes)


class SellerRepository(BaseRepository[Sellers]):
    def __init__(self):
        super().__init__(Sellers)


class MeasurementUnitRepository(BaseRepository[MeasurementUnits]):
    def __init__(self):
        super().__init__(MeasurementUnits)


class SizeRepository(BaseRepository[Sizes]):
    def __init__(self):
        super().__init__(Sizes)

    async def get_by_unit(self, db: AsyncSession, unit_id: uuid.UUID) -> list[Sizes]:
        result = await db.execute(select(Sizes).where(Sizes.unit_id == unit_id))
        return list(result.scalars().all())


role_repo = RoleRepository()
team_repo = TeamRepository()
delivery_type_repo = DeliveryTypeRepository()
payment_type_repo = PaymentTypeRepository()
seller_repo = SellerRepository()
measurement_unit_repo = MeasurementUnitRepository()
size_repo = SizeRepository()
