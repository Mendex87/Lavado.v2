from pydantic import BaseModel


class QuarryStockItem(BaseModel):
    quarry: str
    tons: float
    status: str
    last_movement: str


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
