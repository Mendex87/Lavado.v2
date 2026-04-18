from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModelORM


class AppSetting(BaseModelORM):
    __tablename__ = 'app_settings'
    __table_args__ = (UniqueConstraint('key', name='uq_app_setting_key'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
