from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class ProcessSummary(BaseModel):
    code: str
    line: int
    mode: Literal['simple', 'blend']
    status: Literal['active', 'closed', 'cancelled']
    operator: str
    started_at: datetime


class ProcessCreateInput(BaseModel):
    quarry: str
    hopper_code: str | None = None
    blend_target_pct: float | None = None


class ProcessCreateOutput(BaseModel):
    product: str | None = None
    classification: Literal['product', 'discard']
    output_code: str


class ProcessCreateRequest(BaseModel):
    line: int
    mode: Literal['simple', 'blend']
    operator: str
    inputs: list[ProcessCreateInput]
    outputs: list[ProcessCreateOutput]
    notes: str | None = None


class ProcessCloseRequest(BaseModel):
    reason: str
    notes: str | None = None
