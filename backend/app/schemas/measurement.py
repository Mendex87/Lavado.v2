from datetime import datetime
from pydantic import BaseModel


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
    readings_created: int
    reset_partials_ack: bool


class MeasurementLatestItem(BaseModel):
    code: str
    name: str
    line: int
    source: str | None = None
    captured_at: datetime | None = None
    partial_ton: float | None = None
    totalizer_ton: float | None = None
    delta_ton: float | None = None


class MeasurementManualLinePayload(BaseModel):
    line: int
    tph: float | None = None
    partial_ton: float | None = None
    totalizer_ton: float | None = None


class MeasurementManualResult(BaseModel):
    ok: bool
    line: int
    source: str
    readings_created: int
