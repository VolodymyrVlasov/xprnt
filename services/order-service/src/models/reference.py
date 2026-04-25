import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.models.base import TimestampMixin


class Roles(TimestampMixin, Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role: Mapped[str] = mapped_column(String, unique=True, nullable=False)


class Teams(TimestampMixin, Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class CompanyTypes(TimestampMixin, Base):
    __tablename__ = "company_types"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column("shortName", String, nullable=True)


class MeasurementUnits(TimestampMixin, Base):
    __tablename__ = "measurement_units"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    measurement_unit: Mapped[str] = mapped_column("measurementUnit", String, nullable=False)
    classifier: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class DeliveryTypes(TimestampMixin, Base):
    __tablename__ = "delivery_types"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class Addresses(TimestampMixin, Base):
    __tablename__ = "addresses"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    street: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    building: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    apartment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    warehouse: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class Images(TimestampMixin, Base):
    __tablename__ = "images"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column("filePath", String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class DocumentTemplates(TimestampMixin, Base):
    __tablename__ = "document_templates"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document: Mapped[str] = mapped_column(Text, nullable=False)


class Sellers(TimestampMixin, Base):
    __tablename__ = "sellers"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_type_id: Mapped[uuid.UUID] = mapped_column(
        "companyTypeId", PG_UUID(as_uuid=True), ForeignKey("company_types.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column("shortName", String, nullable=True)


class Sizes(TimestampMixin, Base):
    __tablename__ = "sizes"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id: Mapped[uuid.UUID] = mapped_column(
        "unitId", PG_UUID(as_uuid=True), ForeignKey("measurement_units.id"), nullable=False
    )
    width: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    height: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    diameter: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    radius: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    volume: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    t_shirt_size_eu: Mapped[Optional[str]] = mapped_column("tShirtSize_EU", String, nullable=True)
    t_shirt_size_age: Mapped[Optional[str]] = mapped_column("tShirtSize_age", String, nullable=True)
    roll_width: Mapped[Optional[Decimal]] = mapped_column("rollWidth", Numeric(10, 3), nullable=True)


class BankRequisites(TimestampMixin, Base):
    __tablename__ = "bank_requisites"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    seller_id: Mapped[uuid.UUID] = mapped_column(
        "sellerId", PG_UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False
    )
    is_default: Mapped[bool] = mapped_column("isDefault", default=False, nullable=False)
    bank_name: Mapped[Optional[str]] = mapped_column("bankName", String, nullable=True)
    bank_mfo: Mapped[Optional[str]] = mapped_column("bankMFO", String, nullable=True)
    iban: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    swift_code: Mapped[Optional[str]] = mapped_column("swiftCode", String, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    bank_address_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "bankAddressId", PG_UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True
    )
    account_name: Mapped[Optional[str]] = mapped_column("accountName", String, nullable=True)
    edrpou: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    legal_address_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "legalAddressId", PG_UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=True
    )
    tax_status: Mapped[Optional[str]] = mapped_column("taxStatus", String, nullable=True)
    finish_at: Mapped[Optional[str]] = mapped_column("finishAt", nullable=True)
    # update_author_id — FK to users.id, added with use_alter to avoid circular dep
    update_author_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "updateAuthorId",
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", use_alter=True, name="fk_bank_requisites_update_author"),
        nullable=True,
    )


class PaymentTypes(TimestampMixin, Base):
    __tablename__ = "payment_types"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    bank_requisite_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "bankRequisiteId", PG_UUID(as_uuid=True), ForeignKey("bank_requisites.id"), nullable=True
    )
    transaction_fee: Mapped[Optional[Decimal]] = mapped_column("transactionFee", Numeric(5, 4), nullable=True)
