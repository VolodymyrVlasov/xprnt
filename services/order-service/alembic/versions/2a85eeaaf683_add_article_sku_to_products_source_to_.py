"""add_article_sku_to_products_source_to_order_numbers

Revision ID: 2a85eeaaf683
Revises: a88b21717708
Create Date: 2026-05-14 19:35:10.274543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a85eeaaf683'
down_revision: Union[str, None] = 'a88b21717708'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # sequence for products.article
    op.execute("CREATE SEQUENCE IF NOT EXISTS product_article_seq START 1000")

    # add article and sku to products
    op.add_column(
        "products",
        sa.Column(
            "article",
            sa.Integer(),
            sa.Sequence("product_article_seq"),
            server_default=sa.text("nextval('product_article_seq')"),
            nullable=False,
        ),
    )
    op.create_unique_constraint("uq_products_article", "products", ["article"])
    op.add_column(
        "products",
        sa.Column("sku", sa.String(64), nullable=True),
    )

    # add source to order_numbers
    order_source = sa.Enum("web", "office", name="order_source")
    order_source.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "order_numbers",
        sa.Column(
            "source",
            sa.Enum("web", "office", name="order_source"),
            nullable=False,
            server_default="office",
        ),
    )


def downgrade() -> None:
    op.drop_column("order_numbers", "source")
    op.execute("DROP TYPE IF EXISTS order_source")
    op.drop_constraint("uq_products_article", "products", type_="unique")
    op.drop_column("products", "article")
    op.drop_column("products", "sku")
    op.execute("DROP SEQUENCE IF EXISTS product_article_seq")
