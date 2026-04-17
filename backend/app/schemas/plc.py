from pydantic import BaseModel


class PlcContextPublishRequest(BaseModel):
    process_code: str
    line: int
    mode: str
    process_enabled: bool
    blend_target_a_pct: float | None = None
    blend_target_b_pct: float | None = None


class PlcPartialResetRequest(BaseModel):
    requested_by_user_id: int
    confirmed: bool


class PlcVariableItem(BaseModel):
    code: str
    name: str
    direction: str
    data_type: str
    is_active: bool


class PlcSimulatedState(BaseModel):
    process_enabled: bool
    line: int | None = None
    mode: str | None = None
    blend_target_a_pct: float | None = None
    blend_target_b_pct: float | None = None
    reset_partials_requested: bool = False
