from pydantic import BaseModel


class QuarryStockItem(BaseModel):
    quarry: str
    tons: float
    status: str
    last_movement: str
    threshold_low: float = 80.0
    threshold_critical: float = 40.0


class StockIngressRequest(BaseModel):
    quarry: str
    quantity_ton: float
    reference_code: str | None = None
    reason: str | None = None


class StockIngressResult(BaseModel):
    ok: bool
    quarry: str
    quantity_ton: float
    new_stock_ton: float


class StockThresholds(BaseModel):
    low: float = 80.0
    critical: float = 40.0


class StockThresholdsConfig(BaseModel):
    quarry: str
    thresholds: StockThresholds
