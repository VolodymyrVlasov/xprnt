import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.product import Categories, Products
from src.repository.product import category_repo, product_repo
from src.schemas.product import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate


async def create_category(db: AsyncSession, data: CategoryCreate) -> Categories:
    return await category_repo.create(db, data.model_dump())


async def update_category(db: AsyncSession, category_id: uuid.UUID, data: CategoryUpdate) -> Categories:
    cat = await category_repo.get(db, category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return await category_repo.update(db, cat, data.model_dump(exclude_none=True))


async def create_product(db: AsyncSession, data: ProductCreate) -> Products:
    cat = await category_repo.get(db, data.category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return await product_repo.create(db, data.model_dump())


async def update_product(db: AsyncSession, product_id: uuid.UUID, data: ProductUpdate) -> Products:
    product = await product_repo.get(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return await product_repo.update(db, product, data.model_dump(exclude_none=True))


async def deactivate_product(db: AsyncSession, product_id: uuid.UUID) -> Products:
    product = await product_repo.get(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return await product_repo.update(db, product, {"in_stock": False})
