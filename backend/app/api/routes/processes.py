from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.process_repository import ProcessRepository
from app.schemas.process import ProcessCloseRequest, ProcessCreateRequest, ProcessSummary
from app.services.process_service import ProcessService

router = APIRouter(prefix='/processes', tags=['processes'])


@router.get('/active', response_model=list[ProcessSummary])
def list_active_processes(db: Session = Depends(get_db)):
    service = ProcessService(ProcessRepository(db))
    processes = service.list_active()
    return [
        ProcessSummary(
            code=p.code,
            line=p.line_id,
            mode=p.mode,
            status=p.status,
            operator='Operador',
            started_at=p.started_at,
        )
        for p in processes
    ]


@router.post('', response_model=ProcessSummary, status_code=201)
def create_process(payload: ProcessCreateRequest, db: Session = Depends(get_db)):
    service = ProcessService(ProcessRepository(db))
    try:
        process = service.create(payload)
        db.commit()
        db.refresh(process)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ProcessSummary(
        code=process.code,
        line=process.line_id,
        mode=process.mode,
        status=process.status,
        operator=payload.operator,
        started_at=process.started_at,
    )


@router.post('/{code}/close')
def close_process(code: str, payload: ProcessCloseRequest, db: Session = Depends(get_db)):
    service = ProcessService(ProcessRepository(db))
    try:
        process = service.close(code, payload.reason)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {'ok': True, 'code': process.code, 'status': process.status}
