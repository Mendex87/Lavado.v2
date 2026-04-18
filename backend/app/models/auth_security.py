from datetime import datetime
from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModelORM


class AuthThrottle(BaseModelORM):
    __tablename__ = 'auth_throttles'
    __table_args__ = (UniqueConstraint('scope', 'key', name='uq_auth_throttle_scope_key'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    scope: Mapped[str] = mapped_column(String, nullable=False)  # user | ip
    key: Mapped[str] = mapped_column(String, nullable=False)
    fail_count: Mapped[int] = mapped_column(nullable=False, default=0)
    window_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    blocked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
