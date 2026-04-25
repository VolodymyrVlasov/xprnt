import enum
import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.models.base import TimestampMixin


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class Payments(TimestampMixin, Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_type_id: Mapped[uuid.UUID] = mapped_column(
        "paymentTypeId", PG_UUID(as_uuid=True), ForeignKey("payment_types.id"), nullable=False
    )
    super_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "superOrderId", PG_UUID(as_uuid=True), ForeignKey("super_orders.id"), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="UAH", nullable=False)
    fiscal_receipt_number: Mapped[Optional[str]] = mapped_column("fiscalReceiptNumber", String, nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"), default=PaymentStatus.pending, nullable=False
    )
