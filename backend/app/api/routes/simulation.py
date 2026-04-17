from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.simulation import SimulationStartRequest, SimulationState, SimulationStepRequest
from app.services.simulation_service import SimulationService

router = APIRouter(prefix='/simulation', tags=['simulation'])


@router.get('/line/{line}', response_model=SimulationState)
def get_simulation_state(line: int, db: Session = Depends(get_db)):
    return SimulationService(db).get_state(line)


@router.post('/start', response_model=SimulationState)
def start_simulation(payload: SimulationStartRequest, db: Session = Depends(get_db)):
    return SimulationService(db).start(payload)


@router.post('/step', response_model=SimulationState)
def step_simulation(payload: SimulationStepRequest, db: Session = Depends(get_db)):
    return SimulationService(db).step(payload)


@router.post('/line/{line}/stop', response_model=SimulationState)
def stop_simulation(line: int, db: Session = Depends(get_db)):
    return SimulationService(db).stop(line)


@router.post('/line/{line}/reset', response_model=SimulationState)
def reset_simulation(line: int, db: Session = Depends(get_db)):
    return SimulationService(db).reset(line)
