import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import TimestampMixin


class Categories(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "imageId", PG_UUID(as_uuid=True), ForeignKey("images.id"), nullable=True
    )
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "teamId", PG_UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True
    )
    classifier: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    upsells_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "upsellsCategoryId", PG_UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True
    )
    crossells_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "crossellsCategoryId", PG_UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True
    )

    products: Mapped[list["Products"]] = relationship(
        "Products", foreign_keys="Products.category_id", back_populates="category", lazy="selectin"
    )


class PriceMultipliers(TimestampMixin, Base):
    __tablename__ = "price_multipliers"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class Prices(TimestampMixin, Base):
    __tablename__ = "prices"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        "productId", PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    prime_cost_eur: Mapped[Optional[Decimal]] = mapped_column("primeCostEUR", Numeric(10, 4), nullable=True)
    fx_rate_used: Mapped[Optional[Decimal]] = mapped_column("fxRateUsed", Numeric(10, 6), nullable=True)
    price_multiplier_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "priceMultiplierId", PG_UUID(as_uuid=True), ForeignKey("price_multipliers.id"), nullable=True
    )
    values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    previous_price_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "previousPriceId", PG_UUID(as_uuid=True), ForeignKey("prices.id"), nullable=True
    )
    next_price_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "nextPriceId", PG_UUID(as_uuid=True), ForeignKey("prices.id"), nullable=True
    )
    start_at: Mapped[Optional[str]] = mapped_column("startAt", nullable=True)
    finish_at: Mapped[Optional[str]] = mapped_column("finishAt", nullable=True)


class Products(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column("shortName", String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[uuid.UUID] = mapped_column(
        "categoryId", PG_UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False
    )
    image_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "imageId", PG_UUID(as_uuid=True), ForeignKey("images.id"), nullable=True
    )
    size_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "sizeId", PG_UUID(as_uuid=True), ForeignKey("sizes.id"), nullable=True
    )
    is_deliverable: Mapped[bool] = mapped_column("isDeliverable", Boolean, default=True, nullable=False)
    in_stock: Mapped[bool] = mapped_column("inStock", Boolean, default=True, nullable=False)
    package_size_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "packageSizeId", PG_UUID(as_uuid=True), ForeignKey("sizes.id"), nullable=True
    )
    measurement_unit_id: Mapped[uuid.UUID] = mapped_column(
        "measurementUnitId", PG_UUID(as_uuid=True), ForeignKey("measurement_units.id"), nullable=False
    )
    active_price_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "activePriceId", PG_UUID(as_uuid=True), ForeignKey("prices.id"), nullable=True
    )

    category: Mapped["Categories"] = relationship(
        "Categories", foreign_keys=[category_id], back_populates="products"
    )
    active_price: Mapped[Optional["Prices"]] = relationship(
        "Prices", foreign_keys=[active_price_id], lazy="selectin"
    )


class Gallery(TimestampMixin, Base):
    __tablename__ = "gallery"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        "productId", PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "categoryId", PG_UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True
    )
    file_path: Mapped[str] = mapped_column("filePath", String, nullable=False)
