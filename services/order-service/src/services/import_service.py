from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.product import Categories, Prices, Products
from src.models.reference import MeasurementUnits
from src.schemas.import_products import ImportProductRow, ImportReport, ImportRowResult

DEFAULT_MEASUREMENT_UNIT = "шт"


class ImportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _resolve_category(self, name: str) -> Categories | None:
        result = await self.db.execute(
            select(Categories).where(Categories.name == name)
        )
        return result.scalar_one_or_none()

    async def _resolve_measurement_unit(self, name: str) -> MeasurementUnits | None:
        result = await self.db.execute(
            select(MeasurementUnits).where(MeasurementUnits.measurement_unit == name)
        )
        return result.scalar_one_or_none()

    async def _sku_exists(self, sku: str) -> bool:
        result = await self.db.execute(
            select(Products.id).where(Products.sku == sku)
        )
        return result.scalar_one_or_none() is not None

    async def import_products(self, rows: list[ImportProductRow]) -> ImportReport:
        results: list[ImportRowResult] = []
        created = skipped = errors = 0

        for i, row in enumerate(rows, start=1):
            try:
                # 1. Resolve category
                category = await self._resolve_category(row.category)
                if not category:
                    results.append(ImportRowResult(
                        row=i, status="error", name=row.name, sku=row.sku,
                        reason=f"Category not found: {row.category}",
                    ))
                    errors += 1
                    continue

                # 2. Resolve measurement unit — default to "шт" if not provided
                unit_name = row.measurementUnit or DEFAULT_MEASUREMENT_UNIT
                unit = await self._resolve_measurement_unit(unit_name)
                if not unit:
                    results.append(ImportRowResult(
                        row=i, status="error", name=row.name, sku=row.sku,
                        reason=f"MeasurementUnit not found: {unit_name}",
                    ))
                    errors += 1
                    continue

                # 3. Check duplicate SKU
                if row.sku and await self._sku_exists(row.sku):
                    results.append(ImportRowResult(
                        row=i, status="skipped", name=row.name, sku=row.sku,
                        reason="SKU already exists",
                    ))
                    skipped += 1
                    continue

                # 4. Create product
                product = Products(
                    name=row.name,
                    short_name=row.shortName,
                    description=row.description,
                    category_id=category.id,
                    measurement_unit_id=unit.id,
                    is_deliverable=row.isDeliverable,
                    in_stock=row.inStock,
                    sku=row.sku,
                )
                self.db.add(product)
                await self.db.flush()  # get product.id without committing

                # 5. Build structured price tiers — [{from, price}] sorted by qty
                tier_map = [
                    (1,   row.price_1),
                    (5,   row.price_5),
                    (10,  row.price_10),
                    (20,  row.price_20),
                    (50,  row.price_50),
                    (100, row.price_100),
                ]
                values = [
                    {"from": qty, "price": str(p)}
                    for qty, p in tier_map
                    if p is not None
                ]

                if values:
                    price = Prices(
                        product_id=product.id,
                        prime_cost_eur=row.primeCostEUR,
                        fx_rate_used=settings.eur_uah_rate,
                        values=values,
                        start_at=datetime.now(timezone.utc),
                    )
                    self.db.add(price)
                    await self.db.flush()
                    product.active_price_id = price.id

                await self.db.commit()
                await self.db.refresh(product)

                results.append(ImportRowResult(
                    row=i, status="created", name=row.name, sku=row.sku,
                ))
                created += 1

            except Exception as exc:
                await self.db.rollback()
                results.append(ImportRowResult(
                    row=i, status="error", name=row.name, sku=row.sku,
                    reason=str(exc),
                ))
                errors += 1

        return ImportReport(
            total=len(rows),
            created=created,
            skipped=skipped,
            errors=errors,
            rows=results,
        )
