import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    team_id: Optional[uuid.UUID] = None
    classifier: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    team_id: Optional[uuid.UUID] = None
    classifier: Optional[str] = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    team_id: Optional[uuid.UUID] = None
    classifier: Optional[str] = None
    image_id: Optional[uuid.UUID] = None


class PriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    prime_cost_eur: Optional[Decimal] = None
    values: list | None = None
    start_at: datetime | None = None
    finish_at: datetime | None = None


class ProductCreate(BaseModel):
    name: str
    short_name: Optional[str] = None
    description: Optional[str] = None
    category_id: uuid.UUID
    measurement_unit_id: uuid.UUID
    size_id: Optional[uuid.UUID] = None
    is_deliverable: bool = True
    in_stock: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    size_id: Optional[uuid.UUID] = None
    is_deliverable: Optional[bool] = None
    in_stock: Optional[bool] = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    short_name: Optional[str] = None
    description: Optional[str] = None
    category_id: uuid.UUID
    measurement_unit_id: uuid.UUID
    size_id: Optional[uuid.UUID] = None
    is_deliverable: bool
    in_stock: bool
    active_price_id: Optional[uuid.UUID] = None
    active_price: Optional[PriceResponse] = None
