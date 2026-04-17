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
        return self.db.execute(stmt).all()

    def get_stock_by_quarry_id(self, quarry_id: int) -> QuarryStock | None:
        return self.db.scalar(select(QuarryStock).where(QuarryStock.quarry_id == quarry_id))

    def add_movement(self, movement: QuarryStockMovement) -> QuarryStockMovement:
        self.db.add(movement)
        self.db.flush()
        self.db.refresh(movement)
        return movement

    def get_last_movement_by_quarry_id(self, quarry_id: int) -> QuarryStockMovement | None:
        stmt = (
            select(QuarryStockMovement)
            .where(QuarryStockMovement.quarry_id == quarry_id)
            .order_by(QuarryStockMovement.id.desc())
        )
        return self.db.scalar(stmt)
