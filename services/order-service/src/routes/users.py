import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db, require_role
from src.models.user import Users
from src.repository.user import user_repo
from src.schemas.user import UserResponse, UserUpdate
from src.services.user import update_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Users = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    return await user_repo.get_all(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    if current_user.id != user_id:
        role_name = current_user.role.role if current_user.role else ""
        if role_name not in ("manager", "admin"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    user = await user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_route(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    if current_user.id != user_id:
        role_name = current_user.role.role if current_user.role else ""
        if role_name not in ("manager", "admin"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return await update_user(db, user_id, data)
