import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrderPathCreate(BaseModel):
    order_id: uuid.UUID
    path: Optional[str] = None
    docs_path: Optional[str] = None


class OrderPathUpdate(BaseModel):
    path: Optional[str] = None
    docs_path: Optional[str] = None


class OrderPathResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    path: Optional[str] = None
    docs_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
