from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.measurement import MeasurementIngestRequest, MeasurementIngestResult, MeasurementPointItem
from app.services.measurement_service import MeasurementService

router = APIRouter(prefix='/measurements', tags=['measurements'])


@router.get('/points', response_model=list[MeasurementPointItem])
def list_measurement_points(line: int | None = None, db: Session = Depends(get_db)):
    return MeasurementService(db).list_points(line=line)


@router.post('/ingest', response_model=MeasurementIngestResult)
def ingest_measurements(payload: MeasurementIngestRequest, db: Session = Depends(get_db)):
    return MeasurementService(db).ingest(payload)
