import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db, require_role
from src.models.user import Users
from src.repository.product import category_repo
from src.schemas.product import CategoryCreate, CategoryResponse, CategoryUpdate
from src.services.product import create_category, update_category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await category_repo.get_all(db, skip=skip, limit=limit)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category_route(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    return await create_category(db, data)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    cat = await category_repo.get_with_products(db, category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return cat


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category_route(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(require_role("manager", "admin")),
):
    return await update_category(db, category_id, data)
