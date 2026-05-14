import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import Users
from src.repository.base import BaseRepository


class UserRepository(BaseRepository[Users]):
    def __init__(self):
        super().__init__(Users)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[Users]:
        result = await db.execute(select(Users).where(Users.email == email))
        return result.scalar_one_or_none()

    async def get_by_company(self, db: AsyncSession, company_id: uuid.UUID) -> list[Users]:
        result = await db.execute(select(Users).where(Users.company_id == company_id))
        return list(result.scalars().all())

    async def get_by_phone(self, db: AsyncSession, phone: str) -> Optional[Users]:
        result = await db.execute(select(Users).where(Users.phone1 == phone))
        return result.scalar_one_or_none()

    async def get_by_google_id(self, db: AsyncSession, google_id: str) -> Optional[Users]:
        result = await db.execute(select(Users).where(Users.google_id == google_id))
        return result.scalar_one_or_none()


user_repo = UserRepository()
