from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class QualityRecordBase(BaseModel):
    process_id: Optional[int] = None
    product_id: Optional[int] = None
    quarry_id: Optional[int] = None
    sample_code: str
    sample_type: str
    mesh_20: Optional[float] = None
    mesh_40: Optional[float] = None
    mesh_80: Optional[float] = None
    mesh_120: Optional[float] = None
    mesh_200: Optional[float] = None
    mesh_fines: Optional[float] = None
    humidity_pct: Optional[float] = None
    density: Optional[float] = None
    visual_inspection: Optional[str] = None
    result_status: str = "pending"
    notes: Optional[str] = None


class QualityRecordCreate(QualityRecordBase):
    pass


class QualityRecordUpdate(BaseModel):
    mesh_20: Optional[float] = None
    mesh_40: Optional[float] = None
    mesh_80: Optional[float] = None
    mesh_120: Optional[float] = None
    mesh_200: Optional[float] = None
    mesh_fines: Optional[float] = None
    humidity_pct: Optional[float] = None
    density: Optional[float] = None
    visual_inspection: Optional[str] = None
    result_status: Optional[str] = None
    analyzed_by_user_id: Optional[int] = None
    analyzed_at: Optional[datetime] = None
    notes: Optional[str] = None


class QualityRecordResponse(QualityRecordBase):
    id: int
    sampled_by_user_id: Optional[int] = None
    analyzed_by_user_id: Optional[int] = None
    sampled_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QualitySpecificationBase(BaseModel):
    product_id: int
    mesh_20_min: Optional[float] = None
    mesh_20_max: Optional[float] = None
    mesh_40_min: Optional[float] = None
    mesh_40_max: Optional[float] = None
    mesh_80_min: Optional[float] = None
    mesh_80_max: Optional[float] = None
    mesh_120_min: Optional[float] = None
    mesh_120_max: Optional[float] = None
    mesh_200_min: Optional[float] = None
    mesh_200_max: Optional[float] = None
    mesh_fines_max: Optional[float] = None
    humidity_max: Optional[float] = None
    is_active: bool = True


class QualitySpecificationCreate(QualitySpecificationBase):
    pass


class QualitySpecificationResponse(QualitySpecificationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LotTraceabilityBase(BaseModel):
    lot_number: str
    process_id: int
    product_id: int
    total_ton: float
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "in_progress"


class LotTraceabilityCreate(LotTraceabilityBase):
    pass


class LotTraceabilityResponse(LotTraceabilityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class QualitySummaryResponse(BaseModel):
    total_samples: int
    approved: int
    rejected: int
    pending: int
    average_humidity: Optional[float] = None