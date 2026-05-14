from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel


class ImportProductRow(BaseModel):
    name: str
    shortName: Optional[str] = None
    description: Optional[str] = None
    category: str                    # resolved by name → id
    isDeliverable: bool = True
    inStock: bool = True
    measurementUnit: str             # resolved by name → id
    sku: Optional[str] = None
    primeCostEUR: Optional[Decimal] = None
    fxRateUsed: Optional[Decimal] = None
    price_1: Optional[Decimal] = None
    price_10: Optional[Decimal] = None
    price_20: Optional[Decimal] = None
    price_50: Optional[Decimal] = None
    price_100: Optional[Decimal] = None


class ImportRowResult(BaseModel):
    row: int
    status: Literal["created", "skipped", "error"]
    name: Optional[str] = None
    sku: Optional[str] = None
    reason: Optional[str] = None


class ImportReport(BaseModel):
    total: int
    created: int
    skipped: int
    errors: int
    rows: list[ImportRowResult]
