from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.maintenance import (
    MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceRequestResponse,
    MaintenanceIncidentCreate, MaintenanceIncidentUpdate, MaintenanceIncidentResponse,
    PreventiveMaintenanceTaskCreate, PreventiveMaintenanceTaskResponse,
    MaintenanceStatsResponse
)
from app.services.maintenance_service import MaintenanceService
from typing import Optional

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.post("/requests", response_model=MaintenanceRequestResponse)
def create_maintenance_request(
    data: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return MaintenanceService.create_request(db, data.model_dump(), current_user.id)


@router.get("/requests", response_model=list[MaintenanceRequestResponse])
def get_maintenance_requests(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return MaintenanceService.get_requests(db, status, priority, limit)


@router.get("/requests/{request_id}", response_model=MaintenanceRequestResponse)
def get_maintenance_request(request_id: int, db: Session = Depends(get_db)):
    request = MaintenanceService.get_request_by_id(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return request


@router.patch("/requests/{request_id}", response_model=MaintenanceRequestResponse)
def update_maintenance_request(
    request_id: int,
    data: MaintenanceRequestUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    request = MaintenanceService.update_request(db, request_id, data.model_dump(exclude_unset=True))
    if not request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return request


@router.post("/requests/{request_id}/acknowledge", response_model=MaintenanceRequestResponse)
def acknowledge_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    request = MaintenanceService.acknowledge_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return request


@router.post("/requests/{request_id}/start", response_model=MaintenanceRequestResponse)
def start_maintenance_work(
    request_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    request = MaintenanceService.start_work(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return request


@router.post("/requests/{request_id}/complete", response_model=MaintenanceRequestResponse)
def complete_maintenance_request(
    request_id: int,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    request = MaintenanceService.complete_request(db, request_id, resolution_notes)
    if not request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return request


@router.get("/stats", response_model=MaintenanceStatsResponse)
def get_maintenance_stats(db: Session = Depends(get_db)):
    return MaintenanceService.get_stats(db)


@router.post("/incidents", response_model=MaintenanceIncidentResponse)
def create_maintenance_incident(
    data: MaintenanceIncidentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return MaintenanceService.create_incident(db, data.model_dump(), current_user.id)


@router.get("/incidents", response_model=list[MaintenanceIncidentResponse])
def get_maintenance_incidents(
    line_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return MaintenanceService.get_incidents(db, line_id, limit)


@router.post("/incidents/{incident_id}/resolve")
def resolve_incident(
    incident_id: int,
    resolution: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    incident = MaintenanceService.resolve_incident(db, incident_id, current_user.id, resolution)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incident


@router.post("/preventive-tasks", response_model=PreventiveMaintenanceTaskResponse)
def create_preventive_task(
    data: PreventiveMaintenanceTaskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return MaintenanceService.create_preventive_task(db, data.model_dump())


@router.get("/preventive-tasks", response_model=list[PreventiveMaintenanceTaskResponse])
def get_preventive_tasks(
    overdue_only: bool = False,
    db: Session = Depends(get_db)
):
    return MaintenanceService.get_preventive_tasks(db, overdue_only)


@router.post("/preventive-tasks/{task_id}/complete", response_model=PreventiveMaintenanceTaskResponse)
def complete_preventive_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    task = MaintenanceService.complete_preventive_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task