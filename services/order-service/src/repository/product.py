import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.product import Categories, Products
from src.repository.base import BaseRepository


class CategoryRepository(BaseRepository[Categories]):
    def __init__(self):
        super().__init__(Categories)

    async def get_with_products(self, db: AsyncSession, id: uuid.UUID) -> Optional[Categories]:
        result = await db.execute(
            select(Categories)
            .where(Categories.id == id)
            .options(selectinload(Categories.products))
        )
        return result.scalar_one_or_none()


class ProductRepository(BaseRepository[Products]):
    def __init__(self):
        super().__init__(Products)

    async def get_by_category(
        self, db: AsyncSession, category_id: uuid.UUID, in_stock: Optional[bool] = None
    ) -> list[Products]:
        query = select(Products).where(Products.category_id == category_id)
        if in_stock is not None:
            query = query.where(Products.in_stock == in_stock)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_filtered(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[uuid.UUID] = None,
        in_stock: Optional[bool] = None,
    ) -> list[Products]:
        query = select(Products)
        if category_id:
            query = query.where(Products.category_id == category_id)
        if in_stock is not None:
            query = query.where(Products.in_stock == in_stock)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())


category_repo = CategoryRepository()
product_repo = ProductRepository()
