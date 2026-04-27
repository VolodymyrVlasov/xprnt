import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.models.order import OrderStatus, SuperOrderStatus


class OrderBriefResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_number_id: int
    status: OrderStatus
    total_price: Decimal
    created_at: datetime


class SuperOrderCreate(BaseModel):
    company_id: uuid.UUID
    contact_user_id: Optional[uuid.UUID] = None
    payment_type_id: uuid.UUID
    currency: str = "UAH"
    billing_period_start: Optional[datetime] = None
    billing_period_end: Optional[datetime] = None


class SuperOrderUpdate(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    status: Optional[SuperOrderStatus] = None
    total: Optional[Decimal] = None


class SuperOrderStatusUpdate(BaseModel):
    status: SuperOrderStatus


class SuperOrderAddOrder(BaseModel):
    order_id: uuid.UUID


class SuperOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_number_id: int
    company_id: uuid.UUID
    contact_user_id: Optional[uuid.UUID] = None
    payment_type_id: uuid.UUID
    currency: str
    billing_period_start: Optional[datetime] = None
    billing_period_end: Optional[datetime] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    status: SuperOrderStatus
    total: Decimal
    created_at: datetime
    updated_at: datetime
    orders: list[OrderBriefResponse] = []
