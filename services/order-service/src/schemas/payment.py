import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.models.payment import PaymentStatus


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    payment_type_id: uuid.UUID
    super_order_id: Optional[uuid.UUID] = None
    amount: Decimal
    currency: str
    fiscal_receipt_number: Optional[str] = None
    status: PaymentStatus
