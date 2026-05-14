import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import TimestampMixin


class Companies(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # contact_user_id — circular with users, use_alter
    contact_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "contactUserId",
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", use_alter=True, name="fk_companies_contact_user"),
        nullable=True,
    )
    edrpou_code: Mapped[str] = mapped_column("edrpouCode", String, unique=True, nullable=False)
    itn_code: Mapped[Optional[str]] = mapped_column("itnCode", String, unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    address1: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone1: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    company_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "companyTypeId", PG_UUID(as_uuid=True), ForeignKey("company_types.id"), nullable=True
    )
    contract_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "contractId", PG_UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=True
    )
    head_of_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "headOfId",
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", use_alter=True, name="fk_companies_head_of"),
        nullable=True,
    )

    # Relationships
    users: Mapped[list["Users"]] = relationship(  # type: ignore[name-defined]
        "Users", foreign_keys="Users.company_id", back_populates="company", lazy="selectin"
    )
