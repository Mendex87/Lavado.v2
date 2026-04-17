from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.types import JSONVariant
from app.models.base import BaseModelORM


class ProcessEvent(BaseModelORM):
    __tablename__ = 'process_events'
    id: Mapped[int] = mapped_column(primary_key=True)
    process_id: Mapped[int] = mapped_column(ForeignKey('processes.id', ondelete='CASCADE'), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[dict | None] = mapped_column(JSONVariant)


class Alarm(BaseModelORM):
    __tablename__ = 'alarms'
    id: Mapped[int] = mapped_column(primary_key=True)
    process_id: Mapped[int | None] = mapped_column(ForeignKey('processes.id'))
    line_id: Mapped[int | None] = mapped_column(ForeignKey('lines.id'))
    alarm_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    acknowledged_by_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    acknowledged_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))


class AuditLog(BaseModelORM):
    __tablename__ = 'audit_log'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    entity_name: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    before_json: Mapped[dict | None] = mapped_column(JSONVariant)
    after_json: Mapped[dict | None] = mapped_column(JSONVariant)
