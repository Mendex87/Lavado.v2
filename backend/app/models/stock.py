from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModelORM


class QuarryStock(BaseModelORM):
    __tablename__ = 'quarry_stock'
    id: Mapped[int] = mapped_column(primary_key=True)
    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarries.id', ondelete='CASCADE'), unique=True, nullable=False)
    current_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, default=0)
    threshold_low: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, default=80.0)
    threshold_critical: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False, default=40.0)


class QuarryStockMovement(BaseModelORM):
    __tablename__ = 'quarry_stock_movements'
    id: Mapped[int] = mapped_column(primary_key=True)
    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarries.id'), nullable=False)
    process_id: Mapped[int | None] = mapped_column(ForeignKey('processes.id'))
    scale_id: Mapped[int | None] = mapped_column(ForeignKey('scales.id'))
    movement_type: Mapped[str] = mapped_column(String, nullable=False)
    direction: Mapped[str] = mapped_column(String, nullable=False)
    quantity_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    signed_quantity_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False, default='manual')
    reference_code: Mapped[str | None] = mapped_column(String)
    entered_by_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
