from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.reporting import (
    DailyReportCreate, DailyReportResponse,
    OEESnapshotCreate, OEESnapshotResponse,
    OOEDashboardResponse, OEEByLineResponse,
    EnergyReadingCreate, EnergyReadingResponse,
    EnergySummaryResponse, ReportingSummaryResponse
)
from app.services.reporting_service import ReportingService
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/reporting", tags=["reporting"])


@router.get("/oee/dashboard", response_model=OOEDashboardResponse)
def get_oee_dashboard(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    return ReportingService.get_oee_dashboard(db, start_time, end_time)


@router.get("/oee/history", response_model=list[OEESnapshotResponse])
def get_oee_history(
    line_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    return ReportingService.get_oee_history(db, line_id, days)


@router.post("/oee/snapshot", response_model=OEESnapshotResponse)
def create_oee_snapshot(
    line_id: int,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return ReportingService.save_oee_snapshot(db, line_id, start_time, end_time)


@router.get("/daily", response_model=list[DailyReportResponse])
def get_daily_reports(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    return ReportingService.get_daily_reports(db, start_date, end_date, limit)


@router.post("/daily", response_model=DailyReportResponse)
def create_daily_report(
    data: DailyReportCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return ReportingService.create_daily_report(db, data.model_dump())


@router.get("/daily/summary", response_model=ReportingSummaryResponse)
def get_daily_summary(
    date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    if not date:
        date = datetime.utcnow()
    return ReportingService.get_report_summary(db, date)


@router.post("/energy", response_model=EnergyReadingResponse)
def add_energy_reading(
    data: EnergyReadingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return ReportingService.add_energy_reading(db, data.model_dump())


@router.get("/energy/summary", response_model=EnergySummaryResponse)
def get_energy_summary(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    return ReportingService.get_energy_summary(db, start_time, end_time)


@router.get("/energy/history", response_model=list[EnergyReadingResponse])
def get_energy_history(
    meter_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return ReportingService.get_energy_history(db, meter_id, limit)