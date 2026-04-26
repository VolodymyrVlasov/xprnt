import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from src.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    payment_type_id: uuid.UUID
    order_id: Optional[uuid.UUID] = None
    super_order_id: Optional[uuid.UUID] = None
    amount: Decimal
    currency: str = "UAH"
    fiscal_receipt_number: Optional[str] = None

    @model_validator(mode="after")
    def check_one_target(self) -> "PaymentCreate":
        if not self.order_id and not self.super_order_id:
            raise ValueError("Either order_id or super_order_id must be provided")
        if self.order_id and self.super_order_id:
            raise ValueError("Provide either order_id or super_order_id, not both")
        return self


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payment_type_id: uuid.UUID
    super_order_id: Optional[uuid.UUID] = None
    amount: Decimal
    currency: str
    fiscal_receipt_number: Optional[str] = None
    status: PaymentStatus
