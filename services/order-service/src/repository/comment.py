import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.order import CommentEntityType, Comments
from src.repository.base import BaseRepository


class CommentRepository(BaseRepository[Comments]):
    def __init__(self):
        super().__init__(Comments)

    async def get_by_entity(
        self, db: AsyncSession, entity_type: CommentEntityType, entity_id: uuid.UUID
    ) -> list[Comments]:
        result = await db.execute(
            select(Comments).where(
                Comments.entity_type == entity_type,
                Comments.entity_id == entity_id,
            )
        )
        return list(result.scalars().all())


comment_repo = CommentRepository()
