from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.company import Companies
from src.repository.base import BaseRepository


class CompanyRepository(BaseRepository[Companies]):
    def __init__(self):
        super().__init__(Companies)

    async def get_by_edrpou(self, db: AsyncSession, edrpou_code: str) -> Optional[Companies]:
        result = await db.execute(select(Companies).where(Companies.edrpou_code == edrpou_code))
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Companies]:
        result = await db.execute(select(Companies).where(Companies.name == name))
        return result.scalar_one_or_none()


company_repo = CompanyRepository()
