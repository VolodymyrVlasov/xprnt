"""add_short_name_to_cart_item_products

Revision ID: a88b21717708
Revises: f12346e4fe8d
Create Date: 2026-05-08 00:09:53.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a88b21717708"
down_revision: Union[str, None] = "f12346e4fe8d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cart_item_products",
        sa.Column("shortName", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cart_item_products", "shortName")
