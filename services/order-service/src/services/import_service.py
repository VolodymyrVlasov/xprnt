import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.product import Categories, Prices, Products
from src.models.reference import MeasurementUnits, Sizes
from src.schemas.import_products import ImportProductRow, ImportReport, ImportRowResult

DEFAULT_MEASUREMENT_UNIT = "шт"


class ImportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._mm_unit_id: uuid.UUID | None = None

    async def _resolve_mm_unit(self) -> uuid.UUID:
        if self._mm_unit_id is not None:
            return self._mm_unit_id
        result = await self.db.execute(
            select(MeasurementUnits).where(MeasurementUnits.measurement_unit == "мм")
        )
        unit = result.scalar_one_or_none()
        if not unit:
            raise RuntimeError("MeasurementUnit 'мм' not found — run seeds first")
        self._mm_unit_id = unit.id
        return self._mm_unit_id

    async def _get_or_create_size(
        self,
        width: Decimal | None,
        height: Decimal | None,
        roll_width: Decimal | None,
        mm_unit_id: uuid.UUID,
    ) -> uuid.UUID | None:
        if width is None and height is None and roll_width is None:
            return None

        stmt = select(Sizes).where(
            Sizes.unit_id == mm_unit_id,
            Sizes.width == width,
            Sizes.height == height,
            Sizes.roll_width == roll_width,
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing.id

        new_size = Sizes(
            unit_id=mm_unit_id,
            width=width,
            height=height,
            roll_width=roll_width,
        )
        self.db.add(new_size)
        await self.db.flush()
        return new_size.id

    async def import_products(self, rows: list[ImportProductRow]) -> ImportReport:
        mm_unit_id = await self._resolve_mm_unit()
        results: list[ImportRowResult] = []
        created = updated = skipped = errors = 0

        for i, row in enumerate(rows, start=2):  # row 1 = header
            await self.db.execute(text("SAVEPOINT sp_row"))
            try:
                # --- Resolve category ---
                cat_result = await self.db.execute(
                    select(Categories).where(Categories.name == row.category.strip())
                )
                category = cat_result.scalar_one_or_none()
                if not category:
                    raise ValueError(f"Category not found: {row.category}")

                # --- Resolve measurementUnit ---
                unit_name = row.measurementUnit.strip() if row.measurementUnit else DEFAULT_MEASUREMENT_UNIT
                unit_result = await self.db.execute(
                    select(MeasurementUnits).where(
                        MeasurementUnits.measurement_unit == unit_name
                    )
                )
                unit = unit_result.scalar_one_or_none()
                if not unit:
                    raise ValueError(f"MeasurementUnit not found: {unit_name}")

                # --- Resolve or create Size ---
                size_id = await self._get_or_create_size(
                    row.width, row.height, row.rollWidth, mm_unit_id
                )

                # --- Build price values list ---
                tiers = [
                    (1,   row.price_1),
                    (5,   row.price_5),
                    (10,  row.price_10),
                    (20,  row.price_20),
                    (50,  row.price_50),
                    (100, row.price_100),
                ]
                price_values = [
                    {"from": qty, "price": str(price)}
                    for qty, price in tiers
                    if price is not None
                ]

                # --- UPSERT LOGIC ---
                existing_product = None
                if row.article is not None:
                    res = await self.db.execute(
                        select(Products).where(Products.article == row.article)
                    )
                    existing_product = res.scalar_one_or_none()

                if existing_product:
                    # UPDATE MODE
                    existing_product.name = row.name
                    existing_product.short_name = row.shortName
                    existing_product.description = row.description
                    existing_product.is_deliverable = row.isDeliverable
                    existing_product.in_stock = row.inStock
                    existing_product.category_id = category.id
                    existing_product.measurement_unit_id = unit.id
                    if size_id:
                        existing_product.size_id = size_id

                    if price_values:
                        # Close existing active price
                        if existing_product.active_price_id:
                            await self.db.execute(
                                update(Prices)
                                .where(Prices.id == existing_product.active_price_id)
                                .values(finish_at=datetime.now(timezone.utc))
                            )
                        # Create new price
                        new_price = Prices(
                            product_id=existing_product.id,
                            prime_cost_eur=row.primeCostEUR,
                            fx_rate_used=settings.eur_uah_rate,
                            values=price_values,
                        )
                        self.db.add(new_price)
                        await self.db.flush()
                        existing_product.active_price_id = new_price.id

                    await self.db.flush()
                    await self.db.execute(text("RELEASE SAVEPOINT sp_row"))
                    results.append(ImportRowResult(
                        row=i, action="updated", name=row.name, sku=None
                    ))
                    updated += 1

                else:
                    # CREATE MODE
                    product_kwargs: dict = dict(
                        name=row.name,
                        short_name=row.shortName,
                        description=row.description,
                        category_id=category.id,
                        is_deliverable=row.isDeliverable,
                        in_stock=row.inStock,
                        measurement_unit_id=unit.id,
                    )
                    if size_id:
                        product_kwargs["size_id"] = size_id
                    if row.article is not None:
                        product_kwargs["article"] = row.article

                    new_product = Products(**product_kwargs)
                    self.db.add(new_product)
                    await self.db.flush()

                    if price_values:
                        new_price = Prices(
                            product_id=new_product.id,
                            prime_cost_eur=row.primeCostEUR,
                            fx_rate_used=settings.eur_uah_rate,
                            values=price_values,
                        )
                        self.db.add(new_price)
                        await self.db.flush()
                        new_product.active_price_id = new_price.id
                        await self.db.flush()

                    await self.db.execute(text("RELEASE SAVEPOINT sp_row"))
                    results.append(ImportRowResult(
                        row=i, action="created", name=row.name, sku=None
                    ))
                    created += 1

            except Exception as e:
                await self.db.execute(text("ROLLBACK TO SAVEPOINT sp_row"))
                results.append(ImportRowResult(
                    row=i, action="error", name=getattr(row, "name", None),
                    sku=None, reason=str(e)
                ))
                errors += 1

        # Reset sequence to avoid collisions with manually set article values
        await self.db.execute(
            text("""
                SELECT setval(
                    'product_article_seq',
                    GREATEST((SELECT COALESCE(MAX(article), 1000) FROM products), 1000)
                )
            """)
        )
        await self.db.commit()

        return ImportReport(
            total=len(rows),
            created=created,
            updated=updated,
            skipped=skipped,
            errors=errors,
            rows=results,
        )
