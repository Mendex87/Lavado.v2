from app.repositories.stock_repository import StockRepository


class StockService:
    def __init__(self, repository: StockRepository):
        self.repository = repository

    def list_quarry_stock(self):
        rows = self.repository.list_quarry_stock()
        items = []
        for row in rows:
            name, tons = row
            status = 'normal'
            if tons <= 80:
                status = 'low'
            if tons <= 40:
                status = 'critical'
            items.append({
                'quarry': name,
                'tons': float(tons),
                'status': status,
                'last_movement': 'Sin movimientos' if tons is None else 'Movimiento registrado',
            })
        return items
