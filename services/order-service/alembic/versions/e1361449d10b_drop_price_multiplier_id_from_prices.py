"""drop_price_multiplier_id_from_prices

Revision ID: e1361449d10b
Revises: 2a85eeaaf683
Create Date: 2026-05-14 23:43:12.652587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e1361449d10b'
down_revision: Union[str, None] = '2a85eeaaf683'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        'prices_priceMultiplierId_fkey',
        'prices',
        type_='foreignkey'
    )
    op.drop_column('prices', 'priceMultiplierId')


def downgrade() -> None:
    op.add_column(
        'prices',
        sa.Column('priceMultiplierId', postgresql.UUID(), nullable=True)
    )
    op.create_foreign_key(
        'prices_priceMultiplierId_fkey',
        'prices', 'price_multipliers',
        ['priceMultiplierId'], ['id']
    )
