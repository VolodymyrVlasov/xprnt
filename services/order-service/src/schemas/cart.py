import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.models.cart import CartItemType, CartStatus


class CartItemProductCreate(BaseModel):
    product_id: uuid.UUID
    name: str
    amount: Decimal
    price: Decimal
    price_id: Optional[uuid.UUID] = None
    price_tier_qty: Optional[int] = None
    priced_at: Optional[datetime] = None
    price_total: Optional[Decimal] = None
    short_name: Optional[str] = None


class CartItemCreate(BaseModel):
    category_id: uuid.UUID
    cart_item_type: CartItemType = CartItemType.simple
    name: str
    short_name: Optional[str] = None
    amount: Decimal
    unit_price: Decimal
    design_id: Optional[uuid.UUID] = None
    total_price: Optional[Decimal] = None
    priced_at: Optional[datetime] = None
    products: list[CartItemProductCreate] = []


class CartItemUpdate(BaseModel):
    amount: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    name: Optional[str] = None


class CartItemProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cart_item_id: uuid.UUID
    product_id: uuid.UUID
    name: str
    amount: Decimal
    price: Decimal
    price_total: Decimal
    price_id: Optional[uuid.UUID] = None
    price_tier_qty: Optional[int] = None
    priced_at: Optional[datetime] = None
    short_name: Optional[str] = None


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cart_id: uuid.UUID
    category_id: uuid.UUID
    cart_item_type: CartItemType
    name: str
    short_name: Optional[str] = None
    amount: Decimal
    unit_price: Decimal
    total_price: Decimal
    priced_at: Optional[datetime] = None
    design_id: Optional[uuid.UUID] = None
    products: list[CartItemProductResponse] = []


class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: CartStatus
    total_price: Decimal
    customer_id: Optional[uuid.UUID] = None
    currency: str
    items: list[CartItemResponse] = []
