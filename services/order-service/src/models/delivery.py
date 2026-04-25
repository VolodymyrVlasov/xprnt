import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.models.base import TimestampMixin


class Deliveries(TimestampMixin, Base):
    __tablename__ = "deliveries"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_user_id: Mapped[uuid.UUID] = mapped_column(
        "deliveryUserId", PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    delivery_type_id: Mapped[uuid.UUID] = mapped_column(
        "deliveryTypeId", PG_UUID(as_uuid=True), ForeignKey("delivery_types.id"), nullable=False
    )
    address_id: Mapped[uuid.UUID] = mapped_column(
        "addressId", PG_UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False
    )
    ttn_number: Mapped[Optional[str]] = mapped_column("ttnNumber", String(32), nullable=True)
