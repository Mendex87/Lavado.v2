from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModelORM


class PlcVariable(BaseModelORM):
    __tablename__ = 'plc_variables'
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    direction: Mapped[str] = mapped_column(String, nullable=False)
    data_type: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    line_id: Mapped[int | None] = mapped_column(ForeignKey('lines.id'))
    scale_id: Mapped[int | None] = mapped_column(ForeignKey('scales.id'))
    store_history: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    history_policy: Mapped[str | None] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PlcVariableHistory(BaseModelORM):
    __tablename__ = 'plc_variable_history'
    id: Mapped[int] = mapped_column(primary_key=True)
    plc_variable_id: Mapped[int] = mapped_column(ForeignKey('plc_variables.id', ondelete='CASCADE'), nullable=False)
    value_text: Mapped[str] = mapped_column(Text, nullable=False)
    captured_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)


class ScaleTotalizerHistory(BaseModelORM):
    __tablename__ = 'scale_totalizer_history'
    id: Mapped[int] = mapped_column(primary_key=True)
    scale_id: Mapped[int] = mapped_column(ForeignKey('scales.id'), nullable=False)
    reading_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    totalizer_ton: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False, default='plc')
