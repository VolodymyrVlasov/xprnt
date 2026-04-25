import enum
import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import TimestampMixin


class CartStatus(str, enum.Enum):
    active = "active"
    locked = "locked"
    ordered = "ordered"
    abandoned = "abandoned"


class CartItemType(str, enum.Enum):
    configured = "configured"
    simple = "simple"


class Cart(TimestampMixin, Base):
    __tablename__ = "cart"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[CartStatus] = mapped_column(
        Enum(CartStatus, name="cart_status"), default=CartStatus.active, nullable=False
    )
    total_price: Mapped[Decimal] = mapped_column("totalPrice", Numeric(10, 2), default=0, nullable=False)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "customerId", PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    currency: Mapped[str] = mapped_column(String(3), default="UAH", nullable=False)

    items: Mapped[list["CartItems"]] = relationship(
        "CartItems", back_populates="cart", lazy="selectin", cascade="all, delete-orphan"
    )


class CartItems(TimestampMixin, Base):
    __tablename__ = "cart_items"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id: Mapped[uuid.UUID] = mapped_column(
        "cartId", PG_UUID(as_uuid=True), ForeignKey("cart.id"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        "categoryId", PG_UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False
    )
    cart_item_type: Mapped[CartItemType] = mapped_column(
        "cartItemType", Enum(CartItemType, name="cart_item_type"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column("shortName", String, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column("unitPrice", Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column("totalPrice", Numeric(10, 2), nullable=False)
    priced_at: Mapped[Optional[str]] = mapped_column("pricedAt", nullable=True)
    design_id: Mapped[Optional[uuid.UUID]] = mapped_column("designId", PG_UUID(as_uuid=True), nullable=True)

    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    products: Mapped[list["CartItemProducts"]] = relationship(
        "CartItemProducts", back_populates="cart_item", lazy="selectin", cascade="all, delete-orphan"
    )


class CartItemProducts(TimestampMixin, Base):
    __tablename__ = "cart_item_products"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_item_id: Mapped[uuid.UUID] = mapped_column(
        "cartItemId", PG_UUID(as_uuid=True), ForeignKey("cart_items.id"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        "productId", PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    price_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "priceId", PG_UUID(as_uuid=True), ForeignKey("prices.id"), nullable=True
    )
    price_tier_qty: Mapped[Optional[int]] = mapped_column("priceTierQty", nullable=True)
    priced_at: Mapped[Optional[str]] = mapped_column("pricedAt", nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_total: Mapped[Decimal] = mapped_column("priceTotal", Numeric(10, 2), nullable=False)

    cart_item: Mapped["CartItems"] = relationship("CartItems", back_populates="products")
