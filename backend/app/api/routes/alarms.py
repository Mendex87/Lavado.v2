from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.alarm import AlarmAckResult, AlarmItem
from app.services.alarm_service import AlarmService
from app.services.audit_service import AuditService

router = APIRouter(prefix='/alarms', tags=['alarms'])


@router.get('/active', response_model=list[AlarmItem])
def list_active_alarms(db: Session = Depends(get_db)):
    return AlarmService(db).list_active()


@router.post('/{alarm_id}/ack', response_model=AlarmAckResult)
def acknowledge_alarm(
    alarm_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AlarmService(db)
    try:
        service.acknowledge(alarm_id=alarm_id, user_id=current_user.id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    AuditService(db).log(
        user_id=current_user.id,
        entity_name='alarm',
        entity_id=str(alarm_id),
        action='ack_alarm',
        after_json={'alarm_id': alarm_id},
    )
    db.commit()
    return AlarmAckResult(ok=True, alarm_id=alarm_id)
