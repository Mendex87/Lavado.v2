from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.repositories.stock_repository import StockRepository
from app.schemas.stock import QuarryStockItem, StockIngressRequest, StockIngressResult
from app.services.audit_service import AuditService
from app.services.stock_service import StockService

router = APIRouter(prefix='/stock', tags=['stock'])


@router.get('/quarries', response_model=list[QuarryStockItem])
def list_quarry_stock(db: Session = Depends(get_db)):
    service = StockService(StockRepository(db))
    return service.list_quarry_stock()


@router.post('/ingress', response_model=StockIngressResult, dependencies=[Depends(require_roles('supervisor', 'admin'))])
def add_stock_ingress(
    payload: StockIngressRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = StockService(StockRepository(db))
    try:
        result = service.add_manual_ingress(payload, entered_by_user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    AuditService(db).log(
        user_id=current_user.id,
        entity_name='stock',
        entity_id=payload.quarry,
        action='manual_ingress',
        after_json={
            'quantity_ton': payload.quantity_ton,
            'reference_code': payload.reference_code,
        },
    )
    db.commit()
    return result
