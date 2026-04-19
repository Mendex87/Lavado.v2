from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModelORM


class HandoverRecord(BaseModelORM):
    __tablename__ = 'handover_records'
    id: Mapped[int] = mapped_column(primary_key=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    to_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    from_shift_id: Mapped[int | None] = mapped_column(ForeignKey('shifts.id'))
    to_shift_id: Mapped[int | None] = mapped_column(ForeignKey('shifts.id'))
    handover_started_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    handover_completed_at: Mapped[str | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String, nullable=False, default='pending')
    process_summary_json: Mapped[dict | None] = mapped_column(JSON)
    stock_summary_json: Mapped[dict | None] = mapped_column(JSON)
    pending_issues_json: Mapped[list | None] = mapped_column(JSON)
    notes: Mapped[str | None] = mapped_column(Text)


class HandoverChecklistItem(BaseModelORM):
    __tablename__ = 'handover_checklist_items'
    id: Mapped[int] = mapped_column(primary_key=True)
    handover_id: Mapped[int] = mapped_column(ForeignKey('handover_records.id', ondelete='CASCADE'), nullable=False)
    item_text: Mapped[str] = mapped_column(String, nullable=False)
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    checked_at: Mapped[str | None] = mapped_column(DateTime)