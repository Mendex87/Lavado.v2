from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DailyReportBase(BaseModel):
    report_date: datetime
    shift_id: Optional[int] = None
    line_id: Optional[int] = None
    total_input_ton: float = 0
    total_product_a_ton: float = 0
    total_product_b_ton: float = 0
    total_discard_ton: float = 0
    avg_feed_rate_tph: Optional[float] = None
    total_production_hours: float = 0
    downtime_minutes: float = 0
    alarm_count: int = 0
    quality_samples_count: int = 0
    notes: Optional[str] = None


class DailyReportCreate(DailyReportBase):
    pass


class DailyReportResponse(DailyReportBase):
    id: int
    generated_at: datetime

    class Config:
        from_attributes = True


class OEESnapshotBase(BaseModel):
    line_id: int
    snapshot_period_start: datetime
    snapshot_period_end: datetime
    availability_pct: float
    performance_pct: float
    quality_pct: float
    oee_pct: float
    planned_production_minutes: float
    actual_production_minutes: float
    ideal_cycle_time_minutes: float
    total_output_ton: float
    good_output_ton: float


class OEESnapshotCreate(OEESnapshotBase):
    pass


class OEESnapshotResponse(OEESnapshotBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OEEByLineResponse(BaseModel):
    line_id: int
    line_name: str
    availability_pct: float
    performance_pct: float
    quality_pct: float
    oee_pct: float


class OOEDashboardResponse(BaseModel):
    lines: list[OEEByLineResponse]
    plant_avg_oee: float
    period_start: datetime
    period_end: datetime


class EnergyReadingBase(BaseModel):
    line_id: Optional[int] = None
    meter_id: str
    reading_type: str
    kwh_value: float
    power_kw: Optional[float] = None
    read_at: datetime


class EnergyReadingCreate(EnergyReadingBase):
    pass


class EnergyReadingResponse(EnergyReadingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EnergySummaryResponse(BaseModel):
    total_kwh: float
    avg_power_kw: Optional[float]
    specific_consumption_kwh_per_ton: Optional[float]
    readings_count: int


class ReportingSummaryResponse(BaseModel):
    date: datetime
    total_input_ton: float
    total_output_ton: float
    total_production_hours: float
    total_downtime_minutes: float
    avg_oee: float
    total_alarms: int
    total_quality_samples: int