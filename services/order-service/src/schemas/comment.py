import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.models.order import CommentEntityType


class CommentCreate(BaseModel):
    entity_type: CommentEntityType
    entity_id: uuid.UUID
    text: str


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    entity_type: CommentEntityType
    entity_id: uuid.UUID
    text: str
    created_by: uuid.UUID
