from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


def _get_db_url() -> str:
    url = settings.ORDER_DB_URL
    # Ensure asyncpg driver prefix
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


engine = create_async_engine(_get_db_url(), echo=settings.ENV == "dev")
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
