from datetime import datetime
from decimal import Decimal
from app.models.catalog import Quarry
from app.models.stock import QuarryStock, QuarryStockMovement
from app.repositories.stock_repository import StockRepository
from app.schemas.stock import StockIngressRequest, StockIngressResult


class StockService:
    def __init__(self, repository: StockRepository):
        self.repository = repository

    def list_quarry_stock(self):
        rows = self.repository.list_quarry_stock()
        quarries = {q.name: q for q in self.repository.db.query(Quarry).all()}
        
        # Obtener umbrales configurables desde la DB
        stock_thresholds = {}
        for row in rows:
            if row[0] in quarries:
                stock = self.repository.get_stock_by_quarry_id(quarries[row[0]].id)
                if stock:
                    stock_thresholds[row[0]] = {
                        'threshold_low': float(stock.threshold_low),
                        'threshold_critical': float(stock.threshold_critical)
                    }
        
        items = []
        for row in rows:
            name, tons = row
            quarry = quarries.get(name)
            thresholds = stock_thresholds.get(name, {'threshold_low': 80.0, 'threshold_critical': 40.0})
            
            status = 'normal'
            if tons <= thresholds['threshold_critical']:
                status = 'critical'
            elif tons <= thresholds['threshold_low']:
                status = 'low'
            
            last = self.repository.get_last_movement_by_quarry_id(quarry.id) if quarry else None
            movement_text = 'Sin movimientos'
            if last:
                movement_text = (last.created_at or datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')
            
            items.append({
                'quarry': name,
                'tons': float(tons),
                'status': status,
                'last_movement': movement_text,
                'threshold_low': thresholds['threshold_low'],
                'threshold_critical': thresholds['threshold_critical'],
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
            raise ValueError('No existe stock para la cantera indicated')

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

    def update_thresholds(self, quarry_name: str, threshold_low: float, threshold_critical: float, user_id: int) -> dict:
        """Actualiza los umbrales de alerta para una cantera"""
        quarry = self.repository.db.query(Quarry).filter(Quarry.name == quarry_name).first()
        if not quarry:
            raise ValueError(f'Cantera no encontrada: {quarry_name}')
        
        stock = self.repository.get_stock_by_quarry_id(quarry.id)
        if not stock:
            raise ValueError('No existe stock para la cantera')
        
        if threshold_critical >= threshold_low:
            raise ValueError('El umbral crítico debe ser menor al umbral bajo')
        
        stock.threshold_low = Decimal(str(threshold_low))
        stock.threshold_critical = Decimal(str(threshold_critical))
        self.repository.db.commit()
        
        return {
            'ok': True,
            'quarry': quarry_name,
            'threshold_low': threshold_low,
            'threshold_critical': threshold_critical,
        }
        self.repository.add_movement(movement)
        self.repository.db.commit()

        return StockIngressResult(
            ok=True,
            quarry=quarry.name,
            quantity_ton=qty,
            new_stock_ton=new_value,
        )
