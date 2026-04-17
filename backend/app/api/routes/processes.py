from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas.process import ProcessCloseRequest, ProcessCreateRequest, ProcessSummary
from app.services.mock_state import mock_state

router = APIRouter(prefix='/processes', tags=['processes'])


@router.get('/active', response_model=list[ProcessSummary])
def list_active_processes():
    return [p for p in mock_state['processes'] if p['status'] == 'active']


@router.post('', response_model=ProcessSummary, status_code=201)
def create_process(payload: ProcessCreateRequest):
    existing = next((p for p in mock_state['processes'] if p['line'] == payload.line and p['status'] == 'active'), None)
    if existing:
        raise HTTPException(status_code=409, detail=f'La línea {payload.line} ya tiene un proceso activo')
    if payload.line == 1 and payload.mode != 'simple':
        raise HTTPException(status_code=422, detail='La línea 1 solo permite modo simple')
    code = f"PR-2026-{len(mock_state['processes']) + 22:05d}"
    process = {
        'code': code,
        'line': payload.line,
        'mode': payload.mode,
        'status': 'active',
        'operator': payload.operator,
        'started_at': datetime.utcnow(),
    }
    mock_state['processes'].append(process)
    return process


@router.post('/{code}/close')
def close_process(code: str, payload: ProcessCloseRequest):
    process = next((p for p in mock_state['processes'] if p['code'] == code), None)
    if not process:
        raise HTTPException(status_code=404, detail='Proceso no encontrado')
    process['status'] = 'closed'
    process['closed_reason'] = payload.reason
    process['closed_at'] = datetime.utcnow()
    return {'ok': True, 'code': code, 'status': 'closed'}
