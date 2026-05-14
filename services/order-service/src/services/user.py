import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import Users
from src.repository.user import user_repo
from src.schemas.user import UserCreate, UserUpdate
from src.services.auth import hash_password


async def create_user(db: AsyncSession, data: UserCreate) -> Users:
    existing = await user_repo.get_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return await user_repo.create(
        db,
        {
            "name": data.name,
            "middlename": data.middlename,
            "lastname": data.lastname,
            "email": data.email,
            "phone1": data.phone1,
            "phone2": data.phone2,
            "telegram": data.telegram,
            "company_id": data.company_id,
            "role_id": data.role_id,
            "hashed_password": hash_password(data.password),
        },
    )


async def update_user(db: AsyncSession, user_id: uuid.UUID, data: UserUpdate) -> Users:
    user = await user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return await user_repo.update(db, user, data.model_dump(exclude_none=True))
