import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db, require_role
from src.models.order import CommentEntityType
from src.models.user import Users
from src.repository.comment import comment_repo
from src.schemas.comment import CommentCreate, CommentResponse

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return await comment_repo.create(
        db,
        {
            "entity_type": data.entity_type,
            "entity_id": data.entity_id,
            "text": data.text,
            "created_by": current_user.id,
        },
    )


@router.get("/", response_model=list[CommentResponse])
async def list_comments(
    entity_type: CommentEntityType,
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Users = Depends(get_current_user),
):
    return await comment_repo.get_by_entity(db, entity_type, entity_id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    obj = await comment_repo.get(db, id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    role_name = current_user.role.role if current_user.role else ""
    if obj.created_by != current_user.id and role_name not in ("manager", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete another user's comment")

    await comment_repo.delete(db, id)
