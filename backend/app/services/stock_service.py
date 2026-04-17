from app.models.catalog import Quarry
from app.repositories.stock_repository import StockRepository


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
                movement_text = f"{last.movement_type} {float(last.quantity_ton):.1f} t"
                if last.reference_code:
                    movement_text += f" · {last.reference_code}"
            items.append({
                'quarry': name,
                'tons': float(tons),
                'status': status,
                'last_movement': movement_text,
            })
        return items
