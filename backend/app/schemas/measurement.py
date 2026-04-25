from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class MeasurementPointItem(BaseModel):
    code: str
    name: str
    line: int
    point_kind: str
    role: str
    source_mode: str
    plc_tag: str | None = None
    affects_stock: bool
    affects_production: bool
    is_active: bool


class MeasurementChannelIngestItem(BaseModel):
    code: str
    partial_ton: float | None = None
    totalizer_ton: float | None = None
    raw_value_text: str | None = None


class MeasurementIngestRequest(BaseModel):
    captured_at: datetime
    line: int
    source: str = 'plc'
    reset_partials_ack: bool = False
    channels: list[MeasurementChannelIngestItem]


class MeasurementIngestResult(BaseModel):
    ok: bool
    line: int
    process_code: str | None = None
    status: str = "active"  # "active" o "idle"
    readings_created: int
    reset_partials_ack: bool


class MeasurementLatestItem(BaseModel):
    code: str
    name: str
    line: int
    source: Optional[str] = None
    captured_at: Optional[datetime] = None
    partial_ton: Optional[float] = None
    totalizer_ton: Optional[float] = None
    delta_ton: Optional[float] = None


class MeasurementManualOperationPayload(BaseModel):
    line: int
    feed_l1_partial_ton: Optional[float] = None
    feed_l1_quarry: Optional[str] = None
    feed_l2_h1_partial_ton: Optional[float] = None
    feed_l2_h1_quarry: Optional[str] = None
    feed_l2_h2_partial_ton: Optional[float] = None
    feed_l2_h2_quarry: Optional[str] = None
    product_1_partial_ton: Optional[float] = None
    product_2_partial_ton: Optional[float] = None
    product_3_partial_ton: Optional[float] = None
    product_4_partial_ton: Optional[float] = None
    notes: Optional[str] = None


class MeasurementManualResult(BaseModel):
    ok: bool
    line: int
    source: str
    readings_created: int
    stock_updates: list[dict] = []


class MeasurementManualHistoryItem(BaseModel):
    id: int
    line: int
    source: str
    created_at: datetime
    entered_by_user_id: int
    readings_summary: str
    stock_discount_summary: Optional[str] = None
