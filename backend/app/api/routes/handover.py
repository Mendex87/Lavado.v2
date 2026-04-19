from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.services.handover_service import HandoverService
from app.schemas.handover import (
    HandoverStartRequest,
    HandoverStartResponse,
    HandoverPendingResponse,
    HandoverCompleteRequest,
    HandoverCompleteResponse,
    HandoverHistoryItem,
)

router = APIRouter(prefix='/handover', tags=['handover'])


@router.post('/start', response_model=HandoverStartResponse)
def start_handover(
    payload: HandoverStartRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Inicia un handover de turno"""
    try:
        result = HandoverService(db).start_handover(
            from_user_id=current_user.id,
            to_user_id=payload.to_user_id,
            from_shift_id=payload.from_shift_id,
            to_shift_id=payload.to_shift_id,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get('/pending', response_model=HandoverPendingResponse)
def get_pending_handover(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Obtiene el handover pendiente para el usuario actual"""
    result = HandoverService(db).get_pending_handover(current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail='No hay handover pendiente')
    return result


@router.post('/complete', response_model=HandoverCompleteResponse)
def complete_handover(
    payload: HandoverCompleteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Completa un handover de turno"""
    try:
        # Obtener el ID del handover pendiente
        pending = HandoverService(db).get_pending_handover(current_user.id)
        if not pending:
            raise HTTPException(status_code=404, detail='No hay handover pendiente para completar')
        
        result = HandoverService(db).complete_handover(
            handover_id=pending['id'],
            checklist_results=[item.model_dump() for item in payload.checklist_results],
            notes=payload.notes,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get('/history', response_model=list[HandoverHistoryItem])
def get_handover_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Obtiene el historial de handovers"""
    return HandoverService(db).get_handover_history(current_user.id, limit)