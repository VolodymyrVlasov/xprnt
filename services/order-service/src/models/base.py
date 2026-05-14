from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )
