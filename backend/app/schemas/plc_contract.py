from pydantic import BaseModel


class PlcContractInputItem(BaseModel):
    quarry: str
    hopper_code: str | None = None
    blend_target_pct: float | None = None


class PlcContractOutputItem(BaseModel):
    output_code: str
    classification: str
    product: str | None = None


class PlcContractContext(BaseModel):
    process_code: str | None = None
    process_enabled: bool
    line: int
    mode: str | None = None
    mode_blend: bool
    blend_target_a_pct: float | None = None
    blend_target_b_pct: float | None = None
    reset_partials_requested: bool
    inputs: list[PlcContractInputItem]
    outputs: list[PlcContractOutputItem]


class PlcContractLineSnapshot(BaseModel):
    line: int
    has_active_process: bool
    context: PlcContractContext
