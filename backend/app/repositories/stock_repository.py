from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.catalog import Quarry
from app.models.stock import QuarryStock, QuarryStockMovement


class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_quarry_stock(self):
        stmt = (
            select(Quarry.name, QuarryStock.current_ton)
            .join(QuarryStock, QuarryStock.quarry_id == Quarry.id)
            .order_by(Quarry.name.asc())
        )
        return list(self.db.execute(stmt).all())

    def get_last_movement(self, quarry_id: int) -> QuarryStockMovement | None:
        stmt = (
            select(QuarryStockMovement)
            .where(QuarryStockMovement.quarry_id == quarry_id)
            .order_by(QuarryStockMovement.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
