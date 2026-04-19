from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModelORM


class DailyReport(BaseModelORM):
    __tablename__ = 'daily_reports'
    id: Mapped[int] = mapped_column(primary_key=True)
    report_date: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    shift_id: Mapped[int | None] = mapped_column(ForeignKey('shifts.id'))
    line_id: Mapped[int | None] = mapped_column(ForeignKey('lines.id'))
    total_input_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, default=0)
    total_product_a_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, default=0)
    total_product_b_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, default=0)
    total_discard_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, default=0)
    avg_feed_rate_tph: Mapped[float | None] = mapped_column(Numeric(7, 2))
    total_production_hours: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0)
    downtime_minutes: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=0)
    alarm_count: Mapped[int] = mapped_column(nullable=False, default=0)
    quality_samples_count: Mapped[int] = mapped_column(nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text)
    generated_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)


class OEESnapshot(BaseModelORM):
    __tablename__ = 'oee_snapshots'
    id: Mapped[int] = mapped_column(primary_key=True)
    line_id: Mapped[int] = mapped_column(ForeignKey('lines.id'), nullable=False)
    snapshot_period_start: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    snapshot_period_end: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    availability_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    performance_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    quality_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    oee_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    planned_production_minutes: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    actual_production_minutes: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    ideal_cycle_time_minutes: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    total_output_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    good_output_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)


class EnergyReading(BaseModelORM):
    __tablename__ = 'energy_readings'
    id: Mapped[int] = mapped_column(primary_key=True)
    line_id: Mapped[int | None] = mapped_column(ForeignKey('lines.id'))
    meter_id: Mapped[str] = mapped_column(String, nullable=False)
    reading_type: Mapped[str] = mapped_column(String, nullable=False)
    kwh_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    power_kw: Mapped[float | None] = mapped_column(Numeric(8, 2))
    read_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)