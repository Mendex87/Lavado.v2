from fastapi import APIRouter
from app.schemas.simulation import SimulationStartRequest, SimulationState, SimulationStepRequest
from app.services.simulation_service import SimulationService

router = APIRouter(prefix='/simulation', tags=['simulation'])
service = SimulationService()


@router.get('/line/{line}', response_model=SimulationState)
def get_simulation_state(line: int):
    return service.get_state(line)


@router.post('/start', response_model=SimulationState)
def start_simulation(payload: SimulationStartRequest):
    return service.start(payload)


@router.post('/step', response_model=SimulationState)
def step_simulation(payload: SimulationStepRequest):
    return service.step(payload)


@router.post('/line/{line}/stop', response_model=SimulationState)
def stop_simulation(line: int):
    return service.stop(line)


@router.post('/line/{line}/reset', response_model=SimulationState)
def reset_simulation(line: int):
    return service.reset(line)
