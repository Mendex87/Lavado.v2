from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MaintenanceRequestBase(BaseModel):
    request_type: str
    priority: str
    line_id: Optional[int] = None
    belt_id: Optional[int] = None
    scale_id: Optional[int] = None
    description: str
    assigned_to_user_id: Optional[int] = None


class MaintenanceRequestCreate(MaintenanceRequestBase):
    pass


class MaintenanceRequestUpdate(BaseModel):
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to_user_id: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    in_progress_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


class MaintenanceRequestResponse(MaintenanceRequestBase):
    id: int
    request_code: str
    status: str
    reported_by_user_id: int
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    in_progress_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True


class MaintenanceIncidentBase(BaseModel):
    maintenance_request_id: Optional[int] = None
    process_id: Optional[int] = None
    line_id: Optional[int] = None
    incident_type: str
    severity: str
    description: str
    downtime_minutes: Optional[float] = None
    production_loss_ton: Optional[float] = None


class MaintenanceIncidentCreate(MaintenanceIncidentBase):
    pass


class MaintenanceIncidentUpdate(BaseModel):
    downtime_minutes: Optional[float] = None
    production_loss_ton: Optional[float] = None
    resolved_by_user_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None


class MaintenanceIncidentResponse(MaintenanceIncidentBase):
    id: int
    incident_code: str
    reported_by_user_id: int
    created_at: datetime
    resolved_by_user_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None

    class Config:
        from_attributes = True


class PreventiveMaintenanceTaskBase(BaseModel):
    equipment_type: str
    equipment_id: Optional[int] = None
    task_description: str
    frequency_days: int
    next_due_at: datetime


class PreventiveMaintenanceTaskCreate(PreventiveMaintenanceTaskBase):
    pass


class PreventiveMaintenanceTaskResponse(PreventiveMaintenanceTaskBase):
    id: int
    task_code: str
    last_performed_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MaintenanceStatsResponse(BaseModel):
    open_requests: int
    in_progress: int
    completed_today: int
    incidents_this_week: int
    avg_resolution_time_hours: Optional[float] = None