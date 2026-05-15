import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PriceMultiplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    values: Optional[list] = None


class PriceMultiplierCreate(BaseModel):
    values: list[float]


class PriceMultiplierUpdate(BaseModel):
    values: list[float]


class PriceCreate(BaseModel):
    product_id: uuid.UUID
    prime_cost_eur: Optional[Decimal] = None
    fx_rate_used: Optional[Decimal] = None
    values: Optional[list] = None
    start_at: Optional[datetime] = None


class PriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    product_id: uuid.UUID
    prime_cost_eur: Optional[Decimal] = None
    fx_rate_used: Optional[Decimal] = None
    values: Optional[list] = None
    previous_price_id: Optional[uuid.UUID] = None
    next_price_id: Optional[uuid.UUID] = None
    start_at: Optional[datetime] = None
    finish_at: Optional[datetime] = None
