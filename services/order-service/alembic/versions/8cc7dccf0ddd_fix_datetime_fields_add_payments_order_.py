"""fix_datetime_fields_add_payments_order_id_super_orders_order_paths

Revision ID: 8cc7dccf0ddd
Revises: c684d3bf05cb
Create Date: 2026-04-27 22:18:05.623191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cc7dccf0ddd'
down_revision: Union[str, None] = 'c684d3bf05cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_USING_TSTZ = "\"{}\"::timestamp with time zone"


def upgrade() -> None:
    op.alter_column(
        'bank_requisites', 'finishAt',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using=_USING_TSTZ.format("finishAt"),
    )
    op.create_foreign_key(
        'fk_bank_requisites_update_author', 'bank_requisites', 'users',
        ['updateAuthorId'], ['id'], use_alter=True,
    )
    op.alter_column(
        'cart_item_products', 'pricedAt',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using=_USING_TSTZ.format("pricedAt"),
    )
    op.alter_column(
        'cart_items', 'pricedAt',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using=_USING_TSTZ.format("pricedAt"),
    )
    op.create_foreign_key(
        'fk_companies_head_of', 'companies', 'users',
        ['headOfId'], ['id'], use_alter=True,
    )
    op.create_foreign_key(
        'fk_companies_contact_user', 'companies', 'users',
        ['contactUserId'], ['id'], use_alter=True,
    )
    op.alter_column(
        'order_numbers', 'createdAt',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
        postgresql_using=_USING_TSTZ.format("createdAt"),
    )
    op.alter_column(
        'orders', 'finishAt',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using=_USING_TSTZ.format("finishAt"),
    )
    op.alter_column(
        'orders', 'doneAt',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using=_USING_TSTZ.format("doneAt"),
    )
    op.create_foreign_key(
        'fk_orders_order_path', 'orders', 'order_paths',
        ['orderPathId'], ['id'], use_alter=True,
    )
    op.add_column('payments', sa.Column('orderId', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_payments_order_id', 'payments', 'orders',
        ['orderId'], ['id'], use_alter=True,
    )
    op.alter_column(
        'prices', 'startAt',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
        postgresql_using=_USING_TSTZ.format("startAt"),
    )
    op.alter_column(
        'prices', 'finishAt',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using=_USING_TSTZ.format("finishAt"),
    )
    op.alter_column(
        'super_orders', 'billingPeriodStart',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using=_USING_TSTZ.format("billingPeriodStart"),
    )
    op.alter_column(
        'super_orders', 'billingPeriodEnd',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using=_USING_TSTZ.format("billingPeriodEnd"),
    )
    op.alter_column(
        'super_orders', 'invoiceDate',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        postgresql_using=_USING_TSTZ.format("invoiceDate"),
    )
    op.create_foreign_key(
        'fk_users_comment', 'users', 'comments',
        ['commentId'], ['id'], use_alter=True,
    )


def downgrade() -> None:
    op.drop_constraint('fk_users_comment', 'users', type_='foreignkey')
    op.alter_column(
        'super_orders', 'invoiceDate',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
    op.alter_column(
        'super_orders', 'billingPeriodEnd',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
    op.alter_column(
        'super_orders', 'billingPeriodStart',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
    op.alter_column(
        'prices', 'finishAt',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
    op.alter_column(
        'prices', 'startAt',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(),
        nullable=True,
    )
    op.drop_constraint('fk_payments_order_id', 'payments', type_='foreignkey')
    op.drop_column('payments', 'orderId')
    op.drop_constraint('fk_orders_order_path', 'orders', type_='foreignkey')
    op.alter_column(
        'orders', 'doneAt',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
    op.alter_column(
        'orders', 'finishAt',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
    op.alter_column(
        'order_numbers', 'createdAt',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(),
        nullable=True,
    )
    op.drop_constraint('fk_companies_contact_user', 'companies', type_='foreignkey')
    op.drop_constraint('fk_companies_head_of', 'companies', type_='foreignkey')
    op.alter_column(
        'cart_items', 'pricedAt',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
    op.alter_column(
        'cart_item_products', 'pricedAt',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
    op.drop_constraint('fk_bank_requisites_update_author', 'bank_requisites', type_='foreignkey')
    op.alter_column(
        'bank_requisites', 'finishAt',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
