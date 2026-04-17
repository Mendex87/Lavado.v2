from pydantic import BaseModel


class SimulationStartRequest(BaseModel):
    line: int
    tph_input: float
    split_product_a_pct: float
    split_product_b_pct: float
    split_discard_pct: float


class SimulationStepRequest(BaseModel):
    line: int
    seconds: int = 60


class SimulationState(BaseModel):
    line: int
    running: bool
    tph_input: float
    split_product_a_pct: float
    split_product_b_pct: float
    split_discard_pct: float
    input_ton: float
    product_a_ton: float
    product_b_ton: float
    discard_ton: float
