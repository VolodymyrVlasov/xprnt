import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.models.order import OrderStatus, SuperOrderStatus


class OrderCreate(BaseModel):
    cart_id: uuid.UUID
    seller_id: uuid.UUID
    payment_type_id: uuid.UUID
    delivery_type_id: Optional[uuid.UUID] = None
    delivery_address_id: Optional[uuid.UUID] = None
    currency: str = "UAH"


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_number_id: int
    customer_id: uuid.UUID
    company_id: uuid.UUID
    seller_id: uuid.UUID
    status: OrderStatus
    total_price: Decimal
    currency: str = "UAH"
    cart_id: uuid.UUID
    super_order_id: Optional[uuid.UUID] = None
    payment_id: Optional[uuid.UUID] = None
    delivery_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    finish_at: Optional[datetime] = None
    done_at: Optional[datetime] = None


class SuperOrderCreate(BaseModel):
    company_id: uuid.UUID
    payment_type_id: uuid.UUID
    currency: str = "UAH"


class SuperOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_number_id: int
    company_id: uuid.UUID
    payment_type_id: uuid.UUID
    status: SuperOrderStatus
    total: Decimal
    currency: str
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
