import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class DesignType(str, enum.Enum):
    CUSTOMER_DESIGN = "CUSTOMER_DESIGN"
    FPD_DESIGN = "FPD_DESIGN"
    OTHER_DESIGN = "OTHER_DESIGN"


class CustomerDesigns(Base):
    __tablename__ = "customer_designs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    previewPath: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    design_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class FPDDesigns(Base):
    __tablename__ = "fpd_designs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Cross-DB reference — no FK constraint
    productId: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    designJson: Mapped[dict] = mapped_column(JSONB, nullable=False)
    previewPath: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    svgPath: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Designs(Base):
    __tablename__ = "designs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    designType: Mapped[DesignType] = mapped_column(
        Enum(DesignType, name="designtype"), nullable=False
    )
    customerDesignId: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_designs.id", ondelete="CASCADE"),
        nullable=True,
    )
    fpdDesignId: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fpd_designs.id", ondelete="CASCADE"),
        nullable=True,
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    customerDesign: Mapped[Optional[CustomerDesigns]] = relationship(
        "CustomerDesigns", lazy="joined"
    )
    fpdDesign: Mapped[Optional[FPDDesigns]] = relationship(
        "FPDDesigns", lazy="joined"
    )
