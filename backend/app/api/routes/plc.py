from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.plc import PlcContextPublishRequest, PlcPartialResetRequest, PlcSimulatedState, PlcVariableItem
from app.schemas.plc_contract import PlcContractLineSnapshot
from app.services.plc_contract_service import PlcContractService
from app.services.plc_service import PlcService

router = APIRouter(prefix='/plc', tags=['plc'])
service = PlcService()


@router.get('/variables', response_model=list[PlcVariableItem])
def list_variables():
    return service.list_variables()


@router.get('/context', response_model=PlcSimulatedState)
def get_context():
    return service.get_context()


@router.get('/line/{line}/contract', response_model=PlcContractLineSnapshot)
def get_line_contract(line: int, db: Session = Depends(get_db)):
    return PlcContractService(db).get_line_snapshot(line)


@router.post('/publish-context', response_model=PlcSimulatedState)
def publish_context(payload: PlcContextPublishRequest):
    return service.publish_context(payload)


@router.post('/reset-partials', response_model=PlcSimulatedState)
def reset_partials(payload: PlcPartialResetRequest):
    try:
        return service.request_partial_reset(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
