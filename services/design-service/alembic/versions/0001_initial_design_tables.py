"""initial design tables

Revision ID: 0001
Revises:
Create Date: 2026-04-26 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # customer_designs
    op.create_table(
        "customer_designs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("previewPath", sa.String(), nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column(
            "createdAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updatedAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # fpd_designs
    op.create_table(
        "fpd_designs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("productId", UUID(as_uuid=True), nullable=True),
        sa.Column("designJson", JSONB, nullable=False),
        sa.Column("previewPath", sa.String(), nullable=True),
        sa.Column("svgPath", sa.String(), nullable=True),
        sa.Column(
            "createdAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updatedAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # designs
    op.create_table(
        "designs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "designType",
            sa.Enum("CUSTOMER_DESIGN", "FPD_DESIGN", "OTHER_DESIGN", name="designtype"),
            nullable=False,
        ),
        sa.Column(
            "customerDesignId",
            UUID(as_uuid=True),
            sa.ForeignKey("customer_designs.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "fpdDesignId",
            UUID(as_uuid=True),
            sa.ForeignKey("fpd_designs.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "createdAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updatedAt",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("designs")
    op.drop_table("fpd_designs")
    op.drop_table("customer_designs")

    sa.Enum(name="designtype").drop(op.get_bind(), checkfirst=True)
