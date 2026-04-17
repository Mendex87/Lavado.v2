from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModelORM


class Process(BaseModelORM):
    __tablename__ = 'processes'
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    line_id: Mapped[int] = mapped_column(ForeignKey('lines.id'), nullable=False)
    shift_id: Mapped[int] = mapped_column(ForeignKey('shifts.id'), nullable=False)
    shift_code_snapshot: Mapped[str] = mapped_column(String, nullable=False)
    shift_name_snapshot: Mapped[str] = mapped_column(String, nullable=False)
    operator_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    supervisor_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    user_session_id: Mapped[int | None] = mapped_column(ForeignKey('user_sessions.id'))
    mode: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    closed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    close_reason: Mapped[str | None] = mapped_column(String)
    cancel_reason: Mapped[str | None] = mapped_column(String)
    notes: Mapped[str | None] = mapped_column(Text)


class ProcessInput(BaseModelORM):
    __tablename__ = 'process_inputs'
    id: Mapped[int] = mapped_column(primary_key=True)
    process_id: Mapped[int] = mapped_column(ForeignKey('processes.id', ondelete='CASCADE'), nullable=False)
    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarries.id'), nullable=False)
    scale_id: Mapped[int | None] = mapped_column(ForeignKey('scales.id'))
    input_order: Mapped[int] = mapped_column(nullable=False)
    hopper_code: Mapped[str | None] = mapped_column(String)
    blend_target_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))


class ProcessOutput(BaseModelORM):
    __tablename__ = 'process_outputs'
    id: Mapped[int] = mapped_column(primary_key=True)
    process_id: Mapped[int] = mapped_column(ForeignKey('processes.id', ondelete='CASCADE'), nullable=False)
    scale_id: Mapped[int | None] = mapped_column(ForeignKey('scales.id'))
    product_id: Mapped[int | None] = mapped_column(ForeignKey('products.id'))
    output_code: Mapped[str] = mapped_column(String, nullable=False)
    classification: Mapped[str] = mapped_column(String, nullable=False)
    expected_humidity_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    humidity_source: Mapped[str | None] = mapped_column(String)


class ProcessScaleReading(BaseModelORM):
    __tablename__ = 'process_scale_readings'
    id: Mapped[int] = mapped_column(primary_key=True)
    process_id: Mapped[int] = mapped_column(ForeignKey('processes.id', ondelete='CASCADE'), nullable=False)
    scale_id: Mapped[int] = mapped_column(ForeignKey('scales.id'), nullable=False)
    reading_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    partial_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    totalizer_ton: Mapped[float | None] = mapped_column(Numeric(14, 3))


class ProcessProductionSummary(BaseModelORM):
    __tablename__ = 'process_production_summary'
    id: Mapped[int] = mapped_column(primary_key=True)
    process_id: Mapped[int] = mapped_column(ForeignKey('processes.id', ondelete='CASCADE'), nullable=False)
    process_output_id: Mapped[int | None] = mapped_column(ForeignKey('process_outputs.id', ondelete='SET NULL'))
    scale_id: Mapped[int] = mapped_column(ForeignKey('scales.id'), nullable=False)
    product_id: Mapped[int | None] = mapped_column(ForeignKey('products.id'))
    classification: Mapped[str] = mapped_column(String, nullable=False)
    wet_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, default=0)
    humidity_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    humidity_source: Mapped[str | None] = mapped_column(String)
    dry_ton: Mapped[float | None] = mapped_column(Numeric(14, 3))
    summarized_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
