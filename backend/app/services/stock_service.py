from datetime import datetime
from decimal import Decimal
from app.models.catalog import Quarry
from app.models.stock import QuarryStockMovement
from app.repositories.stock_repository import StockRepository
from app.schemas.stock import StockIngressRequest, StockIngressResult


class StockService:
    def __init__(self, repository: StockRepository):
        self.repository = repository

    def list_quarry_stock(self):
        rows = self.repository.list_quarry_stock()
        quarries = {q.name: q for q in self.repository.db.query(Quarry).all()}
        items = []
        for row in rows:
            name, tons = row
            status = 'normal'
            if tons <= 80:
                status = 'low'
            if tons <= 40:
                status = 'critical'
            quarry = quarries.get(name)
            last = self.repository.get_last_movement_by_quarry_id(quarry.id) if quarry else None
            movement_text = 'Sin movimientos'
            if last:
                movement_text = (last.created_at or datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')
            items.append({
                'quarry': name,
                'tons': float(tons),
                'status': status,
                'last_movement': movement_text,
            })
        return items

    def add_manual_ingress(self, payload: StockIngressRequest, entered_by_user_id: int) -> StockIngressResult:
        quarry = self.repository.db.query(Quarry).filter(Quarry.name == payload.quarry).first()
        if not quarry:
            raise ValueError(f'Cantera no encontrada: {payload.quarry}')
        qty = float(payload.quantity_ton)
        if qty <= 0:
            raise ValueError('La cantidad debe ser mayor a 0')

        stock = self.repository.get_stock_by_quarry_id(quarry.id)
        if not stock:
            raise ValueError('No existe stock para la cantera indicada')

        current = float(stock.current_ton)
        new_value = current + qty
        stock.current_ton = Decimal(str(new_value))
        self.repository.db.add(stock)

        movement = QuarryStockMovement(
            quarry_id=quarry.id,
            process_id=None,
            scale_id=None,
            movement_type='manual_ingress',
            direction='in',
            quantity_ton=Decimal(str(qty)),
            signed_quantity_ton=Decimal(str(qty)),
            source='manual',
            reference_code=payload.reference_code or datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            entered_by_user_id=entered_by_user_id,
            reason=payload.reason,
        )
        self.repository.add_movement(movement)
        self.repository.db.commit()

        return StockIngressResult(
            ok=True,
            quarry=quarry.name,
            quantity_ton=qty,
            new_stock_ton=new_value,
        )
