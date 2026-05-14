import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import TimestampMixin


class Contracts(TimestampMixin, Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_template_id: Mapped[uuid.UUID] = mapped_column(
        "documentTemplateId", PG_UUID(as_uuid=True), ForeignKey("document_templates.id"), nullable=False
    )
    document_path: Mapped[str] = mapped_column("documentPath", String, nullable=False)


class Users(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        "companyId", PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    middlename: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    lastname: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone1: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    telegram: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role_id: Mapped[uuid.UUID] = mapped_column(
        "roleId", PG_UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "teamId", PG_UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True
    )
    nova_post_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "novaPostUserId", PG_UUID(as_uuid=True), nullable=True
    )
    # comment_id — circular with comments table, use_alter
    comment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "commentId",
        PG_UUID(as_uuid=True),
        ForeignKey("comments.id", use_alter=True, name="fk_users_comment"),
        nullable=True,
    )
    contract_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        "contractId", PG_UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=True
    )
    hashed_password: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone_verified: Mapped[bool] = mapped_column(
        "phoneVerified", Boolean, default=False, nullable=False, server_default="false"
    )
    google_id: Mapped[Optional[str]] = mapped_column(
        "googleId", String(128), unique=True, nullable=True
    )
    auth_provider: Mapped[str] = mapped_column(
        "authProvider", String(32), default="email", nullable=False, server_default="email"
    )

    # Relationships
    role: Mapped["Roles"] = relationship("Roles", foreign_keys=[role_id], lazy="selectin")  # type: ignore[name-defined]
    company: Mapped["Companies"] = relationship(  # type: ignore[name-defined]
        "Companies", foreign_keys=[company_id], back_populates="users", lazy="selectin"
    )
