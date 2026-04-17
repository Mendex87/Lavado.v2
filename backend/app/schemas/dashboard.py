from datetime import datetime
from pydantic import BaseModel


class DashboardActiveProcessItem(BaseModel):
    code: str
    line: int
    mode: str
    status: str
    operator: str
    started_at: datetime


class DashboardSimulationItem(BaseModel):
    line: int
    running: bool
    tph_input: float
    input_ton: float
    product_a_ton: float
    product_b_ton: float
    discard_ton: float


class DashboardStockAlertItem(BaseModel):
    quarry: str
    tons: float
    status: str
    last_movement: str


class DashboardRecentEventItem(BaseModel):
    event_type: str
    severity: str
    message: str
    process_code: str | None = None
    created_at: datetime


class DashboardOverview(BaseModel):
    active_processes_count: int
    running_simulations_count: int
    stock_critical_count: int
    stock_low_count: int
    active_processes: list[DashboardActiveProcessItem]
    simulations: list[DashboardSimulationItem]
    stock_alerts: list[DashboardStockAlertItem]
    recent_events: list[DashboardRecentEventItem]
