from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModelORM


class MaintenanceRequest(BaseModelORM):
    __tablename__ = 'maintenance_requests'
    id: Mapped[int] = mapped_column(primary_key=True)
    request_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    request_type: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default='open')
    line_id: Mapped[int | None] = mapped_column(ForeignKey('lines.id'))
    belt_id: Mapped[int | None] = mapped_column(ForeignKey('belts.id'))
    scale_id: Mapped[int | None] = mapped_column(ForeignKey('scales.id'))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reported_by_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    assigned_to_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    acknowledged_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    in_progress_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    resolution_notes: Mapped[str | None] = mapped_column(Text)


class MaintenanceIncident(BaseModelORM):
    __tablename__ = 'maintenance_incidents'
    id: Mapped[int] = mapped_column(primary_key=True)
    incident_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    maintenance_request_id: Mapped[int | None] = mapped_column(ForeignKey('maintenance_requests.id'))
    process_id: Mapped[int | None] = mapped_column(ForeignKey('processes.id'))
    line_id: Mapped[int | None] = mapped_column(ForeignKey('lines.id'))
    incident_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    downtime_minutes: Mapped[float | None] = mapped_column(Numeric(6, 2))
    production_loss_ton: Mapped[float | None] = mapped_column(Numeric(14, 3))
    reported_by_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    resolved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    resolution: Mapped[str | None] = mapped_column(Text)


class PreventiveMaintenanceTask(BaseModelORM):
    __tablename__ = 'preventive_maintenance_tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    task_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    equipment_type: Mapped[str] = mapped_column(String, nullable=False)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey('belts.id'))
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    frequency_days: Mapped[int] = mapped_column(nullable=False)
    last_performed_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    next_due_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)