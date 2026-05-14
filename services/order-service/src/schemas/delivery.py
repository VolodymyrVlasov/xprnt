import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DeliveryCreate(BaseModel):
    delivery_user_id: uuid.UUID
    delivery_type_id: uuid.UUID
    address_id: uuid.UUID
    ttn_number: Optional[str] = None


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    delivery_user_id: uuid.UUID
    delivery_type_id: uuid.UUID
    address_id: uuid.UUID
    ttn_number: Optional[str] = None
