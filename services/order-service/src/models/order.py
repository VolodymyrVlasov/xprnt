import enum
import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import TimestampMixin


class SuperOrderStatus(str, enum.Enum):
    open = "open"
    invoiced = "invoiced"
    paid = "paid"
    closed = "closed"
    cancelled = "cancelled"


class OrderStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    execution = "execution"
    printing = "printing"
    printed = "printed"
    postprint = "postprint"
    done = "done"
    waiting_delivery = "waiting_delivery"
    shipped = "shipped"
    successful = "successful"
    canceled = "canceled"
    returned = "returned"


class CommentEntityType(str, enum.Enum):
    order = "order"


class OrderNumbers(Base):
    __tablename__ = "order_numbers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[Optional[str]] = mapped_column("createdAt", nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        "createdBy", PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )


class Comments(TimestampMixin, Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[CommentEntityType] = mapped_column(
        "entityType", Enum(CommentEntityType, name="comment_entity_type"), nullable=False
    )
    entity_id: Mapped[uuid.UUID] = mapped_column("entityId", PG_UUID(as_uuid=True), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        "createdBy", PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )


class SuperOrders(TimestampMixin, Base):
    __tablename__ = "super_orders"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number_id: Mapped[int] = mapped_column(
        "orderNumberId", BigInteger, ForeignKey("order_numbers.id"), unique=True, nullable=False
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        "companyId", PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    contact_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "contactUserId", PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    payment_type_id: Mapped[uuid.UUID] = mapped_column(
        "paymentTypeId", PG_UUID(as_uuid=True), ForeignKey("payment_types.id"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="UAH", nullable=False)
    billing_period_start: Mapped[Optional[str]] = mapped_column("billingPeriodStart", nullable=True)
    billing_period_end: Mapped[Optional[str]] = mapped_column("billingPeriodEnd", nullable=True)
    invoice_number: Mapped[Optional[str]] = mapped_column("invoiceNumber", String, nullable=True)
    invoice_date: Mapped[Optional[str]] = mapped_column("invoiceDate", nullable=True)
    status: Mapped[SuperOrderStatus] = mapped_column(
        Enum(SuperOrderStatus, name="super_order_status"), default=SuperOrderStatus.open, nullable=False
    )
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)


class OrderPaths(TimestampMixin, Base):
    __tablename__ = "order_paths"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(
        "orderId", PG_UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False
    )
    path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    docs_path: Mapped[Optional[str]] = mapped_column("docsPath", String, nullable=True)


class Orders(TimestampMixin, Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number_id: Mapped[int] = mapped_column(
        "orderNumberId", BigInteger, ForeignKey("order_numbers.id"), unique=True, nullable=False
    )
    super_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "superOrderId", PG_UUID(as_uuid=True), ForeignKey("super_orders.id"), nullable=True
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        "sellerId", PG_UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        "customerId", PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    payment_user_id: Mapped[uuid.UUID] = mapped_column(
        "paymentUserId", PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    delivery_user_id: Mapped[uuid.UUID] = mapped_column(
        "deliveryUserId", PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        "companyId", PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "managerId", PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    payment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "paymentId", PG_UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True
    )
    delivery_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "deliveryId", PG_UUID(as_uuid=True), ForeignKey("deliveries.id"), nullable=True
    )
    total_price: Mapped[Decimal] = mapped_column("totalPrice", Numeric(10, 2), default=0, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"), default=OrderStatus.pending, nullable=False
    )
    # order_path_id — circular with order_paths, use_alter
    order_path_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "orderPathId",
        PG_UUID(as_uuid=True),
        ForeignKey("order_paths.id", use_alter=True, name="fk_orders_order_path"),
        nullable=True,
    )
    cart_id: Mapped[uuid.UUID] = mapped_column(
        "cartId", PG_UUID(as_uuid=True), ForeignKey("cart.id"), unique=True, nullable=False
    )
    finish_at: Mapped[Optional[str]] = mapped_column("finishAt", nullable=True)
    done_at: Mapped[Optional[str]] = mapped_column("doneAt", nullable=True)

    cart: Mapped["Cart"] = relationship("Cart", foreign_keys=[cart_id], lazy="selectin")  # type: ignore[name-defined]
