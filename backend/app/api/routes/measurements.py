from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.schemas.measurement import (
    MeasurementIngestRequest,
    MeasurementIngestResult,
    MeasurementLatestItem,
    MeasurementManualOperationPayload,
    MeasurementManualResult,
    MeasurementPointItem,
    MeasurementManualHistoryItem,
)
from app.services.measurement_service import MeasurementService
from app.services.audit_service import AuditService

router = APIRouter(prefix='/measurements', tags=['measurements'])


@router.get('/points', response_model=list[MeasurementPointItem])
def list_measurement_points(
    line: int | None = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return MeasurementService(db).list_points(line=line)


@router.post('/ingest', response_model=MeasurementIngestResult)
def ingest_measurements(payload: MeasurementIngestRequest, db: Session = Depends(get_db)):
    return MeasurementService(db).ingest(payload)


@router.get('/latest', response_model=list[MeasurementLatestItem])
def list_latest_measurements(
    line: int | None = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return MeasurementService(db).list_latest(line=line)


@router.post('/manual', response_model=MeasurementManualResult)
def manual_measurements(
    payload: MeasurementManualOperationPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    _roles=Depends(require_roles('supervisor', 'admin')),
):
    try:
        result = MeasurementService(db).manual_ingest(payload, entered_by_user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    AuditService(db).log(
        user_id=current_user.id,
        entity_name='measurement',
        entity_id=f'line:{result.line}',
        action='manual_ingest',
        after_json={
            'line': result.line,
            'readings_created': result.readings_created,
            'notes': payload.notes,
        },
    )
    db.commit()
    return result


@router.get('/history', response_model=list[MeasurementManualHistoryItem])
def get_measurement_history(
    limit: int = 20,
    line: int | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Obtiene historial de mediciones manuales"""
    return MeasurementService(db).get_manual_history(limit=limit, line=line)
