"""Category resolution during product import: case/whitespace-insensitive, cached, ambiguity -> row error.

Uses an in-memory fake AsyncSession (no Postgres needed). The fake emulates
`lower(trim(categories.name)) = :key` in Python and asserts the real query uses it.
"""
import uuid
from types import SimpleNamespace

from sqlalchemy.sql import Select

from src.models.product import Categories
from src.models.reference import MeasurementUnits
from src.schemas.import_products import ImportProductRow
from src.services.import_service import ImportService


class FakeResult:
    def __init__(self, items):
        self._items = items

    def scalar_one_or_none(self):
        assert len(self._items) <= 1
        return self._items[0] if self._items else None

    def scalars(self):
        return SimpleNamespace(all=lambda: list(self._items))


class FakeSession:
    def __init__(self, category_names: list[str]):
        self.categories = [SimpleNamespace(id=uuid.uuid4(), name=n) for n in category_names]
        self.units = {
            "мм": SimpleNamespace(id=uuid.uuid4()),
            "шт": SimpleNamespace(id=uuid.uuid4()),
        }
        self.category_queries = 0
        self.added = []

    async def execute(self, stmt):
        if not isinstance(stmt, Select):  # SAVEPOINT / setval / etc.
            return FakeResult([])
        entity = stmt.column_descriptions[0]["entity"]
        (value,) = stmt.compile().params.values()
        if entity is Categories:
            self.category_queries += 1
            assert "lower(trim(categories.name))" in str(stmt)
            return FakeResult([c.id for c in self.categories if c.name.strip().lower() == value])
        if entity is MeasurementUnits:
            unit = self.units.get(value)
            return FakeResult([unit] if unit else [])
        raise AssertionError(f"unexpected query: {stmt}")

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        pass

    async def commit(self):
        pass


def _row(name: str, category: str) -> ImportProductRow:
    return ImportProductRow(name=name, category=category)


async def test_category_match_ignores_case_and_whitespace():
    db = FakeSession(["Наліпки"])
    report = await ImportService(db).import_products([
        _row("A", "Наліпки"),
        _row("B", "наліпки"),
        _row("C", "  НАЛІПКИ "),
    ])

    assert report.errors == 0, report.rows
    assert report.created == 3
    expected_id = db.categories[0].id
    assert {p.category_id for p in db.added} == {expected_id}
    # resolved once, then served from the per-import cache
    assert db.category_queries == 1


async def test_ambiguous_category_is_row_error_others_imported():
    db = FakeSession(["Наліпки", "НАЛІПКИ", "Банери"])
    report = await ImportService(db).import_products([
        _row("A", "наліпки"),
        _row("B", "Банери"),
        _row("C", "Наліпки "),
    ])

    assert report.created == 1
    assert report.errors == 2
    by_name = {r.name: r for r in report.rows}
    assert by_name["B"].action == "created"
    assert by_name["A"].action == "error"
    assert by_name["A"].reason == "Ambiguous category: наліпки (2 matches)"
    assert by_name["C"].reason == "Ambiguous category: Наліпки (2 matches)"
    assert [p.name for p in db.added] == ["B"]
    assert db.category_queries == 2  # "наліпки" + "банери"


async def test_missing_category_is_row_error():
    db = FakeSession(["Банери"])
    report = await ImportService(db).import_products([_row("A", "Наліпки")])
    assert report.errors == 1
    assert report.rows[0].reason == "Category not found: Наліпки"
