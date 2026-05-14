"""add_phone_verified_google_id_auth_provider_to_users

Revision ID: f12346e4fe8d
Revises: 8cc7dccf0ddd
Create Date: 2026-05-07 23:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f12346e4fe8d"
down_revision: Union[str, None] = "8cc7dccf0ddd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("phoneVerified", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "users",
        sa.Column("googleId", sa.String(128), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("authProvider", sa.String(32), nullable=False, server_default="email"),
    )
    op.create_unique_constraint("uq_users_googleId", "users", ["googleId"])


def downgrade() -> None:
    op.drop_constraint("uq_users_googleId", "users", type_="unique")
    op.drop_column("users", "authProvider")
    op.drop_column("users", "googleId")
    op.drop_column("users", "phoneVerified")
