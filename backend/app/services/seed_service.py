from sqlalchemy.orm import Session
from app.models.catalog import Line, Quarry, Product, Role, Shift, User
from app.models.stock import QuarryStock


class SeedService:
    def __init__(self, db: Session):
        self.db = db

    def run(self):
        if not self.db.query(Role).first():
            self.db.add_all([
                Role(code='operador', name='Operador'),
                Role(code='supervisor', name='Supervisor'),
            ])
        if not self.db.query(Shift).first():
            from datetime import time
            self.db.add_all([
                Shift(code='T1', name='Turno 1', start_time=time(6, 0), end_time=time(14, 0), is_active=True),
                Shift(code='T2', name='Turno 2', start_time=time(14, 0), end_time=time(22, 0), is_active=True),
                Shift(code='T3', name='Turno 3', start_time=time(22, 0), end_time=time(6, 0), is_active=True),
            ])
        if not self.db.query(Line).first():
            self.db.add_all([
                Line(code='L1', name='Línea 1', is_active=True),
                Line(code='L2', name='Línea 2', is_active=True),
            ])
        if not self.db.query(Quarry).first():
            self.db.add_all([
                Quarry(code='RIO_NEGRO', name='Río Negro', is_active=True),
                Quarry(code='DOLAVON', name='Dolavon', is_active=True),
                Quarry(code='TRELEW_NORTE', name='Trelew Norte', is_active=True),
            ])
        if not self.db.query(Product).first():
            self.db.add_all([
                Product(code='P30_70', name='30/70', is_active=True),
                Product(code='P50_140', name='50/140', is_active=True),
                Product(code='P4', name='Producto 4', is_active=True),
            ])
        if not self.db.query(User).first():
            self.db.add_all([
                User(username='admin', full_name='Administrador', password_hash='change-me', is_active=True),
                User(username='diego', full_name='Diego', password_hash='change-me', is_active=True),
                User(username='juan', full_name='Juan', password_hash='change-me', is_active=True),
                User(username='eze', full_name='Eze', password_hash='change-me', is_active=True),
            ])

        self.db.flush()
        stock_defaults = {
            'RIO_NEGRO': 420.0,
            'DOLAVON': 140.0,
            'TRELEW_NORTE': 190.0,
        }
        for quarry in self.db.query(Quarry).all():
            row = self.db.query(QuarryStock).filter(QuarryStock.quarry_id == quarry.id).first()
            if not row:
                self.db.add(QuarryStock(quarry_id=quarry.id, current_ton=stock_defaults.get(quarry.code, 0.0)))

        self.db.commit()
        return {'ok': True}
