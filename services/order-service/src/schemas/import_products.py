from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel


class ImportProductRow(BaseModel):
    article: Optional[int] = None
    name: str
    shortName: Optional[str] = None
    description: Optional[str] = None
    category: str                    # resolved by name → id
    isDeliverable: bool = True
    inStock: bool = True
    measurementUnit: Optional[str] = None  # defaults to "шт" if not provided
    primeCostEUR: Optional[Decimal] = None
    width: Optional[Decimal] = None
    height: Optional[Decimal] = None
    rollWidth: Optional[Decimal] = None
    price_1: Optional[Decimal] = None
    price_5: Optional[Decimal] = None
    price_10: Optional[Decimal] = None
    price_20: Optional[Decimal] = None
    price_50: Optional[Decimal] = None
    price_100: Optional[Decimal] = None


class ImportRowResult(BaseModel):
    row: int
    action: Literal["created", "updated", "skipped", "error"] = "created"
    name: Optional[str] = None
    sku: Optional[str] = None
    reason: Optional[str] = None


class ImportReport(BaseModel):
    total: int
    created: int
    updated: int
    skipped: int
    errors: int
    rows: list[ImportRowResult]
