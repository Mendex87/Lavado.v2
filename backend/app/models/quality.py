from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModelORM


class QualityRecord(BaseModelORM):
    __tablename__ = 'quality_records'
    id: Mapped[int] = mapped_column(primary_key=True)
    process_id: Mapped[int | None] = mapped_column(ForeignKey('processes.id'))
    product_id: Mapped[int | None] = mapped_column(ForeignKey('products.id'))
    quarry_id: Mapped[int | None] = mapped_column(ForeignKey('quarries.id'))
    sample_code: Mapped[str] = mapped_column(String, nullable=False)
    sample_type: Mapped[str] = mapped_column(String, nullable=False)
    mesh_20: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_40: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_80: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_120: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_200: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_fines: Mapped[float | None] = mapped_column(Numeric(5, 2))
    humidity_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    density: Mapped[float | None] = mapped_column(Numeric(6, 3))
    visual_inspection: Mapped[str | None] = mapped_column(Text)
    result_status: Mapped[str] = mapped_column(String, nullable=False, default='pending')
    sampled_by_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    analyzed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    sampled_at: Mapped[object] = mapped_column(DateTime(timezone=True))
    analyzed_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)


class QualitySpecification(BaseModelORM):
    __tablename__ = 'quality_specifications'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    mesh_20_min: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_20_max: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_40_min: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_40_max: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_80_min: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_80_max: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_120_min: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_120_max: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_200_min: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_200_max: Mapped[float | None] = mapped_column(Numeric(5, 2))
    mesh_fines_max: Mapped[float | None] = mapped_column(Numeric(5, 2))
    humidity_max: Mapped[float | None] = mapped_column(Numeric(5, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class LotTraceability(BaseModelORM):
    __tablename__ = 'lot_traceability'
    id: Mapped[int] = mapped_column(primary_key=True)
    lot_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    process_id: Mapped[int] = mapped_column(ForeignKey('processes.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    total_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    start_time: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String, nullable=False, default='in_progress')
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)