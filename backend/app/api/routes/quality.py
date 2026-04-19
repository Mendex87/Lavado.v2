from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.quality import (
    QualityRecordCreate, QualityRecordUpdate, QualityRecordResponse,
    QualitySpecificationCreate, QualitySpecificationResponse,
    LotTraceabilityCreate, LotTraceabilityResponse,
    QualitySummaryResponse
)
from app.services.quality_service import QualityService
from app.models.quality import QualityRecord
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/quality", tags=["quality"])


@router.post("/records", response_model=QualityRecordResponse)
def create_quality_record(
    data: QualityRecordCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return QualityService.create_record(db, data.model_dump())


@router.get("/records", response_model=list[QualityRecordResponse])
def get_quality_records(
    process_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return QualityService.get_records(db, process_id, status, limit)


@router.get("/records/{record_id}", response_model=QualityRecordResponse)
def get_quality_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(QualityRecord).filter(QualityRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return record


@router.patch("/records/{record_id}", response_model=QualityRecordResponse)
def update_quality_record(
    record_id: int,
    data: QualityRecordUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    record = QualityService.update_record(db, record_id, data.model_dump(exclude_unset=True))
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return record


@router.get("/summary", response_model=QualitySummaryResponse)
def get_quality_summary(db: Session = Depends(get_db)):
    return QualityService.get_summary(db)


@router.post("/specifications", response_model=QualitySpecificationResponse)
def create_specification(
    data: QualitySpecificationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return QualityService.create_specification(db, data.model_dump())


@router.get("/specifications", response_model=list[QualitySpecificationResponse])
def get_specifications(
    product_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return QualityService.get_specifications(db, product_id)


@router.post("/lots", response_model=LotTraceabilityResponse)
def create_lot(
    data: LotTraceabilityCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return QualityService.create_lot(db, data.model_dump())


@router.get("/lots", response_model=list[LotTraceabilityResponse])
def get_lots(
    process_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return QualityService.get_lots(db, process_id, status)


@router.patch("/lots/{lot_id}/close", response_model=LotTraceabilityResponse)
def close_lot(lot_id: int, db: Session = Depends(get_db)):
    lot = QualityService.close_lot(db, lot_id, datetime.utcnow())
    if not lot:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return lot


from app.models.quality import QualityRecord
from datetime import datetime