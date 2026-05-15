import csv
import io
from decimal import Decimal, InvalidOperation

from src.schemas.import_products import ImportProductRow


def _parse_bool(value: str) -> bool:
    return str(value).strip().lower() in ("true", "1", "yes")


def _parse_decimal(value: str) -> Decimal | None:
    v = str(value).strip().replace(",", ".")
    if not v:
        return None
    try:
        return Decimal(v)
    except InvalidOperation:
        return None


def _row_to_model(row: dict, row_num: int) -> ImportProductRow:
    # Normalize keys: strip whitespace, lowercase
    normalized = {k.strip().lower(): v for k, v in row.items()}

    def get(key: str) -> str:
        return str(normalized.get(key.lower(), "") or "").strip()

    name = get("name")
    category = get("category")

    if not name:
        raise ValueError(f"Row {row_num}: missing required field 'name'")
    if not category:
        raise ValueError(f"Row {row_num}: missing required field 'category'")

    measurement_unit = get("measurementunit") or None  # None → service defaults to "шт"

    return ImportProductRow(
        name=name,
        shortName=get("shortname") or None,
        description=get("description") or None,
        category=category,
        isDeliverable=_parse_bool(get("isdeliverable") or "true"),
        inStock=_parse_bool(get("instock") or "true"),
        measurementUnit=measurement_unit,
        sku=get("sku") or None,
        primeCostEUR=_parse_decimal(get("primecosteur")),
        price_1=_parse_decimal(get("price_1")),
        price_5=_parse_decimal(get("price_5")),
        price_10=_parse_decimal(get("price_10")),
        price_20=_parse_decimal(get("price_20")),
        price_50=_parse_decimal(get("price_50")),
        price_100=_parse_decimal(get("price_100")),
    )


def parse_csv(content: bytes) -> list[ImportProductRow]:
    text = content.decode("utf-8-sig")  # handle BOM
    reader = csv.DictReader(io.StringIO(text))
    rows: list[ImportProductRow] = []
    for i, row in enumerate(reader, start=2):  # row 1 = header
        name = str(row.get("name", "") or "").strip()
        if not name:
            continue
        rows.append(_row_to_model(row, i))
    return rows


def parse_xlsx(content: bytes) -> list[ImportProductRow]:
    import openpyxl

    wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    ws = wb.active

    rows_iter = ws.iter_rows(values_only=True)
    headers = [str(h).strip() if h is not None else "" for h in next(rows_iter)]

    result: list[ImportProductRow] = []
    for i, raw_row in enumerate(rows_iter, start=2):
        row = {headers[j]: (str(v).strip() if v is not None else "") for j, v in enumerate(raw_row)}
        name = row.get("name", "").strip()
        if not name:
            continue
        result.append(_row_to_model(row, i))

    wb.close()
    return result
