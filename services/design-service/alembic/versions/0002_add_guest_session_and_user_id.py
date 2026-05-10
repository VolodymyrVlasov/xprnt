"""add guest_session_id and user_id to customer_designs

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-10 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customer_designs",
        sa.Column("guest_session_id", sa.String(36), nullable=True),
    )
    op.create_index(
        "ix_customer_designs_guest_session_id",
        "customer_designs",
        ["guest_session_id"],
    )
    op.add_column(
        "customer_designs",
        sa.Column("user_id", UUID(as_uuid=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_index("ix_customer_designs_guest_session_id", table_name="customer_designs")
    op.drop_column("customer_designs", "guest_session_id")
    op.drop_column("customer_designs", "user_id")
