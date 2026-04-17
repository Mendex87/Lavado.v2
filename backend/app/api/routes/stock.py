from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.stock_repository import StockRepository
from app.schemas.stock import QuarryStockItem
from app.services.stock_service import StockService

router = APIRouter(prefix='/stock', tags=['stock'])


@router.get('/quarries', response_model=list[QuarryStockItem])
def list_quarry_stock(db: Session = Depends(get_db)):
    service = StockService(StockRepository(db))
    return service.list_quarry_stock()
