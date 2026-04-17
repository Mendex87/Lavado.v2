from pydantic import BaseModel


class QuarryStockItem(BaseModel):
    quarry: str
    tons: float
    status: str
    last_movement: str
