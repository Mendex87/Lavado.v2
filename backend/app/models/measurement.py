from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModelORM


class MeasurementPoint(BaseModelORM):
    __tablename__ = 'measurement_points'
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    line_id: Mapped[int] = mapped_column(ForeignKey('lines.id'), nullable=False)
    point_kind: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    source_mode: Mapped[str] = mapped_column(String, nullable=False, default='plc')
    plc_tag: Mapped[str | None] = mapped_column(String)
    engineering_unit: Mapped[str] = mapped_column(String, nullable=False, default='ton')
    affects_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    affects_production: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    display_order: Mapped[int] = mapped_column(nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[str | None] = mapped_column(Text)


class MeasurementReading(BaseModelORM):
    __tablename__ = 'measurement_readings'
    id: Mapped[int] = mapped_column(primary_key=True)
    measurement_point_id: Mapped[int] = mapped_column(ForeignKey('measurement_points.id', ondelete='CASCADE'), nullable=False)
    process_id: Mapped[int | None] = mapped_column(ForeignKey('processes.id'))
    source: Mapped[str] = mapped_column(String, nullable=False)
    captured_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    partial_ton: Mapped[float | None] = mapped_column(Numeric(14, 3))
    totalizer_ton: Mapped[float | None] = mapped_column(Numeric(14, 3))
    delta_ton: Mapped[float | None] = mapped_column(Numeric(14, 3))
    raw_value_text: Mapped[str | None] = mapped_column(Text)
    entered_by_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    notes: Mapped[str | None] = mapped_column(Text)
