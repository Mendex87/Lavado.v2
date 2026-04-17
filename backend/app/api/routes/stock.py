from fastapi import APIRouter
from app.schemas.stock import QuarryStockItem
from app.services.mock_state import mock_state

router = APIRouter(prefix='/stock', tags=['stock'])


@router.get('/quarries', response_model=list[QuarryStockItem])
def list_quarry_stock():
    return mock_state['stock']
