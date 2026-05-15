import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import AsyncSessionLocal
from src.models.reference import CompanyTypes, DeliveryTypes, MeasurementUnits, Roles, Teams
from src.models.user import Users
from src.services.auth import hash_password

logger = logging.getLogger(__name__)


async def seed_reference_data() -> None:
    async with AsyncSessionLocal() as db:
        await _seed_roles(db)
        await _seed_teams(db)
        await _seed_company_types(db)
        await _seed_measurement_units(db)
        await _seed_delivery_types(db)


async def seed_admin_user() -> None:
    async with AsyncSessionLocal() as db:
        await _seed_admin(db)


# ── helpers ────────────────────────────────────────────────────────────────

async def _seed_roles(db: AsyncSession) -> None:
    for role_name in ["admin", "manager", "prepress", "postpress", "client"]:
        result = await db.execute(select(Roles).where(Roles.role == role_name))
        if not result.scalar_one_or_none():
            db.add(Roles(role=role_name))
            logger.info("Seeded role: %s", role_name)
    await db.commit()


async def _seed_teams(db: AsyncSession) -> None:
    for name in ["Препрес", "Постпрес", "Менеджери"]:
        result = await db.execute(select(Teams).where(Teams.name == name))
        if not result.scalar_one_or_none():
            db.add(Teams(name=name))
            logger.info("Seeded team: %s", name)
    await db.commit()


async def _seed_company_types(db: AsyncSession) -> None:
    entries = [
        {"name": "Фізична особа", "short_name": "ФО"},
        {"name": "ФОП", "short_name": "ФОП"},
        {"name": "Товариство з обмеженою відповідальністю", "short_name": "ТОВ"},
        {"name": "Акціонерне товариство", "short_name": "АТ"},
    ]
    for entry in entries:
        result = await db.execute(select(CompanyTypes).where(CompanyTypes.name == entry["name"]))
        if not result.scalar_one_or_none():
            db.add(CompanyTypes(**entry))
            logger.info("Seeded company type: %s", entry["name"])
    await db.commit()


async def _seed_measurement_units(db: AsyncSession) -> None:
    entries = [
        {"measurement_unit": "шт", "classifier": "EA"},
        {"measurement_unit": "м²", "classifier": "MTK"},
        {"measurement_unit": "м.п.", "classifier": "MTR"},
        {"measurement_unit": "компл", "classifier": "SET"},
        {"measurement_unit": "мм", "classifier": "MM"},
    ]
    for entry in entries:
        result = await db.execute(
            select(MeasurementUnits).where(MeasurementUnits.measurement_unit == entry["measurement_unit"])
        )
        if not result.scalar_one_or_none():
            db.add(MeasurementUnits(**entry))
            logger.info("Seeded measurement unit: %s", entry["measurement_unit"])
    await db.commit()


async def _seed_delivery_types(db: AsyncSession) -> None:
    entries = [
        {"name": "Нова Пошта", "description": "Доставка Новою Поштою"},
        {"name": "Самовивіз", "description": "Самовивіз з офісу"},
        {"name": "Кур'єр", "description": "Кур'єрська доставка по Києву"},
    ]
    for entry in entries:
        result = await db.execute(select(DeliveryTypes).where(DeliveryTypes.name == entry["name"]))
        if not result.scalar_one_or_none():
            db.add(DeliveryTypes(**entry))
            logger.info("Seeded delivery type: %s", entry["name"])
    await db.commit()


async def _seed_admin(db: AsyncSession) -> None:
    # Find admin role
    role_result = await db.execute(select(Roles).where(Roles.role == "admin"))
    admin_role = role_result.scalar_one_or_none()
    if not admin_role:
        logger.warning("Admin role not found — run seed_reference_data() first")
        return

    # Check if any admin user exists
    result = await db.execute(
        select(Users).where(Users.role_id == admin_role.id).limit(1)
    )
    if result.scalar_one_or_none():
        return  # Admin already exists

    # Create a placeholder company for admin
    from src.models.company import Companies
    company_result = await db.execute(
        select(Companies).where(Companies.edrpou_code == "00000000")
    )
    company = company_result.scalar_one_or_none()
    if not company:
        company = Companies(
            edrpou_code="00000000",
            name="xprnt",
        )
        db.add(company)
        await db.flush()

    admin_user = Users(
        email="admin@xprnt.com",
        hashed_password=hash_password("Admin123!"),
        name="Admin",
        lastname="xprnt",
        phone1="+380000000000",
        company_id=company.id,
        role_id=admin_role.id,
    )
    db.add(admin_user)
    await db.commit()
    logger.info("Seeded admin user: admin@xprnt.com")
