import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class SizeInput(BaseModel):
    diameter: Optional[float] = None
    radius: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None


class CalculatorRequest(BaseModel):
    size: SizeInput
    materialProductId: uuid.UUID
    coatingProductId: uuid.UUID
    cutTypeId: uuid.UUID
    quantity: int


class CartItemDraft(BaseModel):
    categoryId: uuid.UUID
    cartItemType: str
    name: str
    shortName: str
    amount: float
    totalPrice: Decimal
    pricedAt: datetime


class CalculateResponse(BaseModel):
    cartItemDraft: CartItemDraft
