"""initial

Revision ID: c684d3bf05cb
Revises:
Create Date: 2026-04-25 22:28:33.717619

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c684d3bf05cb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── leaf / no-dep tables ───────────────────────────────────────────────
    op.create_table('addresses',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('district', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('street', sa.String(), nullable=True),
    sa.Column('building', sa.String(), nullable=True),
    sa.Column('apartment', sa.String(), nullable=True),
    sa.Column('warehouse', sa.String(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company_types',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('shortName', sa.String(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('delivery_types',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('document_templates',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('document', sa.Text(), nullable=False),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('images',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('filePath', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('measurement_units',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('measurementUnit', sa.String(), nullable=False),
    sa.Column('classifier', sa.String(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('price_multipliers',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('role')
    )
    op.create_table('teams',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    # ── depends on leaf tables ─────────────────────────────────────────────
    op.create_table('contracts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('documentTemplateId', sa.UUID(), nullable=False),
    sa.Column('documentPath', sa.String(), nullable=False),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['documentTemplateId'], ['document_templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sellers',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('companyTypeId', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('shortName', sa.String(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['companyTypeId'], ['company_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sizes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('unitId', sa.UUID(), nullable=False),
    sa.Column('width', sa.Numeric(precision=10, scale=3), nullable=True),
    sa.Column('height', sa.Numeric(precision=10, scale=3), nullable=True),
    sa.Column('diameter', sa.Numeric(precision=10, scale=3), nullable=True),
    sa.Column('radius', sa.Numeric(precision=10, scale=3), nullable=True),
    sa.Column('volume', sa.Numeric(precision=10, scale=3), nullable=True),
    sa.Column('tShirtSize_EU', sa.String(), nullable=True),
    sa.Column('tShirtSize_age', sa.String(), nullable=True),
    sa.Column('rollWidth', sa.Numeric(precision=10, scale=3), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['unitId'], ['measurement_units.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('categories',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('imageId', sa.UUID(), nullable=True),
    sa.Column('teamId', sa.UUID(), nullable=True),
    sa.Column('classifier', sa.String(), nullable=True),
    sa.Column('upsellsCategoryId', sa.UUID(), nullable=True),
    sa.Column('crossellsCategoryId', sa.UUID(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['crossellsCategoryId'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['imageId'], ['images.id'], ),
    sa.ForeignKeyConstraint(['teamId'], ['teams.id'], ),
    sa.ForeignKeyConstraint(['upsellsCategoryId'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # ── products (without activePriceId FK — cycle breaker) ───────────────
    op.create_table('products',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('shortName', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('categoryId', sa.UUID(), nullable=False),
    sa.Column('imageId', sa.UUID(), nullable=True),
    sa.Column('sizeId', sa.UUID(), nullable=True),
    sa.Column('isDeliverable', sa.Boolean(), nullable=False),
    sa.Column('inStock', sa.Boolean(), nullable=False),
    sa.Column('packageSizeId', sa.UUID(), nullable=True),
    sa.Column('measurementUnitId', sa.UUID(), nullable=False),
    sa.Column('activePriceId', sa.UUID(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['categoryId'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['imageId'], ['images.id'], ),
    sa.ForeignKeyConstraint(['measurementUnitId'], ['measurement_units.id'], ),
    sa.ForeignKeyConstraint(['packageSizeId'], ['sizes.id'], ),
    sa.ForeignKeyConstraint(['sizeId'], ['sizes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # ── prices (references products) ──────────────────────────────────────
    op.create_table('prices',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('productId', sa.UUID(), nullable=False),
    sa.Column('primeCostEUR', sa.Numeric(precision=10, scale=4), nullable=True),
    sa.Column('fxRateUsed', sa.Numeric(precision=10, scale=6), nullable=True),
    sa.Column('priceMultiplierId', sa.UUID(), nullable=True),
    sa.Column('values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('previousPriceId', sa.UUID(), nullable=True),
    sa.Column('nextPriceId', sa.UUID(), nullable=True),
    sa.Column('startAt', sa.String(), nullable=True),
    sa.Column('finishAt', sa.String(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['nextPriceId'], ['prices.id'], ),
    sa.ForeignKeyConstraint(['previousPriceId'], ['prices.id'], ),
    sa.ForeignKeyConstraint(['priceMultiplierId'], ['price_multipliers.id'], ),
    sa.ForeignKeyConstraint(['productId'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # deferred FK: products.activePriceId → prices.id
    op.create_foreign_key('fk_products_active_price', 'products', 'prices', ['activePriceId'], ['id'])

    # ── bank_requisites (use_alter FK to users) ───────────────────────────
    op.create_table('bank_requisites',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('sellerId', sa.UUID(), nullable=False),
    sa.Column('isDefault', sa.Boolean(), nullable=False),
    sa.Column('bankName', sa.String(), nullable=True),
    sa.Column('bankMFO', sa.String(), nullable=True),
    sa.Column('iban', sa.String(), nullable=True),
    sa.Column('swiftCode', sa.String(), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('bankAddressId', sa.UUID(), nullable=True),
    sa.Column('accountName', sa.String(), nullable=True),
    sa.Column('edrpou', sa.String(), nullable=True),
    sa.Column('legalAddressId', sa.UUID(), nullable=True),
    sa.Column('taxStatus', sa.String(), nullable=True),
    sa.Column('finishAt', sa.String(), nullable=True),
    sa.Column('updateAuthorId', sa.UUID(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['bankAddressId'], ['addresses.id'], ),
    sa.ForeignKeyConstraint(['legalAddressId'], ['addresses.id'], ),
    sa.ForeignKeyConstraint(['sellerId'], ['sellers.id'], ),
    sa.ForeignKeyConstraint(['updateAuthorId'], ['users.id'], name='fk_bank_requisites_update_author', use_alter=True),
    sa.PrimaryKeyConstraint('id')
    )

    # ── companies (use_alter FKs to users) ────────────────────────────────
    op.create_table('companies',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('contactUserId', sa.UUID(), nullable=True),
    sa.Column('edrpouCode', sa.String(), nullable=False),
    sa.Column('itnCode', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('address1', sa.String(), nullable=True),
    sa.Column('address2', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone1', sa.String(), nullable=True),
    sa.Column('phone2', sa.String(), nullable=True),
    sa.Column('companyTypeId', sa.UUID(), nullable=True),
    sa.Column('contractId', sa.UUID(), nullable=True),
    sa.Column('headOfId', sa.UUID(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['companyTypeId'], ['company_types.id'], ),
    sa.ForeignKeyConstraint(['contactUserId'], ['users.id'], name='fk_companies_contact_user', use_alter=True),
    sa.ForeignKeyConstraint(['contractId'], ['contracts.id'], ),
    sa.ForeignKeyConstraint(['headOfId'], ['users.id'], name='fk_companies_head_of', use_alter=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('edrpouCode'),
    sa.UniqueConstraint('itnCode'),
    sa.UniqueConstraint('name')
    )

    # ── payment_types (depends on bank_requisites) ────────────────────────
    op.create_table('payment_types',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('bankRequisiteId', sa.UUID(), nullable=True),
    sa.Column('transactionFee', sa.Numeric(precision=5, scale=4), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['bankRequisiteId'], ['bank_requisites.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # ── users (depends on companies, roles, teams, contracts; use_alter comments) ──
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('companyId', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('middlename', sa.String(), nullable=True),
    sa.Column('lastname', sa.String(), nullable=True),
    sa.Column('phone1', sa.String(), nullable=True),
    sa.Column('phone2', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('telegram', sa.String(), nullable=True),
    sa.Column('roleId', sa.UUID(), nullable=False),
    sa.Column('teamId', sa.UUID(), nullable=True),
    sa.Column('novaPostUserId', sa.UUID(), nullable=True),
    sa.Column('commentId', sa.UUID(), nullable=True),
    sa.Column('contractId', sa.UUID(), nullable=True),
    sa.Column('hashed_password', sa.Text(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['commentId'], ['comments.id'], name='fk_users_comment', use_alter=True),
    sa.ForeignKeyConstraint(['companyId'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['contractId'], ['contracts.id'], ),
    sa.ForeignKeyConstraint(['roleId'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['teamId'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )

    # ── now that users exists, resolve use_alter FKs on companies / bank_requisites ─
    # (Alembic emits ALTER TABLE … ADD CONSTRAINT automatically for use_alter=True)

    # ── cart, comments, deliveries, order_numbers ─────────────────────────
    op.create_table('cart',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('active', 'locked', 'ordered', 'abandoned', name='cart_status'), nullable=False),
    sa.Column('totalPrice', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('customerId', sa.UUID(), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['customerId'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('entityType', sa.Enum('order', name='comment_entity_type'), nullable=False),
    sa.Column('entityId', sa.UUID(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('createdBy', sa.UUID(), nullable=False),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['createdBy'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deliveries',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('deliveryUserId', sa.UUID(), nullable=False),
    sa.Column('deliveryTypeId', sa.UUID(), nullable=False),
    sa.Column('addressId', sa.UUID(), nullable=False),
    sa.Column('ttnNumber', sa.String(length=32), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['addressId'], ['addresses.id'], ),
    sa.ForeignKeyConstraint(['deliveryTypeId'], ['delivery_types.id'], ),
    sa.ForeignKeyConstraint(['deliveryUserId'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_numbers',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('createdAt', sa.String(), nullable=True),
    sa.Column('createdBy', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['createdBy'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gallery',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('productId', sa.UUID(), nullable=False),
    sa.Column('categoryId', sa.UUID(), nullable=True),
    sa.Column('filePath', sa.String(), nullable=False),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['categoryId'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['productId'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # ── cart_items ────────────────────────────────────────────────────────
    op.create_table('cart_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('cartId', sa.UUID(), nullable=False),
    sa.Column('categoryId', sa.UUID(), nullable=False),
    sa.Column('cartItemType', sa.Enum('configured', 'simple', name='cart_item_type'), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('shortName', sa.String(), nullable=True),
    sa.Column('amount', sa.Numeric(precision=10, scale=3), nullable=False),
    sa.Column('unitPrice', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('totalPrice', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('pricedAt', sa.String(), nullable=True),
    sa.Column('designId', sa.UUID(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['cartId'], ['cart.id'], ),
    sa.ForeignKeyConstraint(['categoryId'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # ── super_orders ──────────────────────────────────────────────────────
    op.create_table('super_orders',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('orderNumberId', sa.BigInteger(), nullable=False),
    sa.Column('companyId', sa.UUID(), nullable=False),
    sa.Column('contactUserId', sa.UUID(), nullable=True),
    sa.Column('paymentTypeId', sa.UUID(), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('billingPeriodStart', sa.String(), nullable=True),
    sa.Column('billingPeriodEnd', sa.String(), nullable=True),
    sa.Column('invoiceNumber', sa.String(), nullable=True),
    sa.Column('invoiceDate', sa.String(), nullable=True),
    sa.Column('status', sa.Enum('open', 'invoiced', 'paid', 'closed', 'cancelled', name='super_order_status'), nullable=False),
    sa.Column('total', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['companyId'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['contactUserId'], ['users.id'], ),
    sa.ForeignKeyConstraint(['orderNumberId'], ['order_numbers.id'], ),
    sa.ForeignKeyConstraint(['paymentTypeId'], ['payment_types.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('orderNumberId')
    )

    # ── cart_item_products ────────────────────────────────────────────────
    op.create_table('cart_item_products',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('cartItemId', sa.UUID(), nullable=False),
    sa.Column('productId', sa.UUID(), nullable=False),
    sa.Column('priceId', sa.UUID(), nullable=True),
    sa.Column('priceTierQty', sa.Integer(), nullable=True),
    sa.Column('pricedAt', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=3), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('priceTotal', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['cartItemId'], ['cart_items.id'], ),
    sa.ForeignKeyConstraint(['priceId'], ['prices.id'], ),
    sa.ForeignKeyConstraint(['productId'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # ── payments ──────────────────────────────────────────────────────────
    op.create_table('payments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('paymentTypeId', sa.UUID(), nullable=False),
    sa.Column('superOrderId', sa.UUID(), nullable=True),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('fiscalReceiptNumber', sa.String(), nullable=True),
    sa.Column('status', sa.Enum('pending', 'paid', 'failed', 'refunded', name='payment_status'), nullable=False),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['paymentTypeId'], ['payment_types.id'], ),
    sa.ForeignKeyConstraint(['superOrderId'], ['super_orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # ── orders (use_alter FK to order_paths) ──────────────────────────────
    op.create_table('orders',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('orderNumberId', sa.BigInteger(), nullable=False),
    sa.Column('superOrderId', sa.UUID(), nullable=True),
    sa.Column('sellerId', sa.UUID(), nullable=False),
    sa.Column('customerId', sa.UUID(), nullable=False),
    sa.Column('paymentUserId', sa.UUID(), nullable=False),
    sa.Column('deliveryUserId', sa.UUID(), nullable=False),
    sa.Column('companyId', sa.UUID(), nullable=False),
    sa.Column('managerId', sa.UUID(), nullable=True),
    sa.Column('paymentId', sa.UUID(), nullable=True),
    sa.Column('deliveryId', sa.UUID(), nullable=True),
    sa.Column('totalPrice', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('status', sa.Enum('pending', 'paid', 'execution', 'printing', 'printed', 'postprint', 'done', 'waiting_delivery', 'shipped', 'successful', 'canceled', 'returned', name='order_status'), nullable=False),
    sa.Column('orderPathId', sa.UUID(), nullable=True),
    sa.Column('cartId', sa.UUID(), nullable=False),
    sa.Column('finishAt', sa.String(), nullable=True),
    sa.Column('doneAt', sa.String(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['cartId'], ['cart.id'], ),
    sa.ForeignKeyConstraint(['companyId'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['customerId'], ['users.id'], ),
    sa.ForeignKeyConstraint(['deliveryId'], ['deliveries.id'], ),
    sa.ForeignKeyConstraint(['deliveryUserId'], ['users.id'], ),
    sa.ForeignKeyConstraint(['managerId'], ['users.id'], ),
    sa.ForeignKeyConstraint(['orderNumberId'], ['order_numbers.id'], ),
    sa.ForeignKeyConstraint(['orderPathId'], ['order_paths.id'], name='fk_orders_order_path', use_alter=True),
    sa.ForeignKeyConstraint(['paymentId'], ['payments.id'], ),
    sa.ForeignKeyConstraint(['paymentUserId'], ['users.id'], ),
    sa.ForeignKeyConstraint(['sellerId'], ['sellers.id'], ),
    sa.ForeignKeyConstraint(['superOrderId'], ['super_orders.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cartId'),
    sa.UniqueConstraint('orderNumberId')
    )

    # ── order_paths (depends on orders) ───────────────────────────────────
    op.create_table('order_paths',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('orderId', sa.UUID(), nullable=False),
    sa.Column('path', sa.String(), nullable=True),
    sa.Column('docsPath', sa.String(), nullable=True),
    sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updatedAt', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['orderId'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('order_paths')
    op.drop_table('orders')
    op.drop_table('payments')
    op.drop_table('cart_item_products')
    op.drop_table('super_orders')
    op.drop_table('cart_items')
    op.drop_table('gallery')
    op.drop_table('order_numbers')
    op.drop_table('deliveries')
    op.drop_table('comments')
    op.drop_table('cart')
    op.drop_table('users')
    op.drop_table('payment_types')
    op.drop_table('companies')
    op.drop_table('bank_requisites')
    op.drop_constraint('fk_products_active_price', 'products', type_='foreignkey')
    op.drop_table('prices')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('sizes')
    op.drop_table('sellers')
    op.drop_table('contracts')
    op.drop_table('price_multipliers')
    op.drop_table('measurement_units')
    op.drop_table('teams')
    op.drop_table('roles')
    op.drop_table('images')
    op.drop_table('document_templates')
    op.drop_table('delivery_types')
    op.drop_table('company_types')
    op.drop_table('addresses')
    op.execute("DROP TYPE IF EXISTS cart_status")
    op.execute("DROP TYPE IF EXISTS cart_item_type")
    op.execute("DROP TYPE IF EXISTS comment_entity_type")
    op.execute("DROP TYPE IF EXISTS super_order_status")
    op.execute("DROP TYPE IF EXISTS order_status")
    op.execute("DROP TYPE IF EXISTS payment_status")
