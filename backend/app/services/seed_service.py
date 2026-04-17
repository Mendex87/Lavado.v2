from sqlalchemy.orm import Session
from app.models.catalog import Line, Quarry, Product, Role, Shift, User
from app.models.measurement import MeasurementPoint
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

        self.db.flush()
        if not self.db.query(MeasurementPoint).first():
            line_1 = self.db.query(Line).filter(Line.code == 'L1').first()
            line_2 = self.db.query(Line).filter(Line.code == 'L2').first()
            if line_1:
                self.db.add_all([
                    MeasurementPoint(code='l1_input_main', name='Entrada línea 1', line_id=line_1.id, point_kind='input', role='feed', source_mode='plc', plc_tag='l1_input_main', affects_stock=True, affects_production=False, display_order=1),
                    MeasurementPoint(code='l1_output_1', name='Salida 1 línea 1', line_id=line_1.id, point_kind='output', role='product', source_mode='plc', plc_tag='l1_output_1', affects_stock=False, affects_production=True, display_order=2),
                    MeasurementPoint(code='l1_output_2', name='Salida 2 línea 1', line_id=line_1.id, point_kind='output', role='product', source_mode='plc', plc_tag='l1_output_2', affects_stock=False, affects_production=True, display_order=3),
                    MeasurementPoint(code='l1_output_3', name='Salida 3 línea 1', line_id=line_1.id, point_kind='output', role='product', source_mode='manual', plc_tag='l1_output_3', affects_stock=False, affects_production=True, display_order=4, notes='Punto preparado para fallback manual o futura balanza'),
                ])
            if line_2:
                self.db.add_all([
                    MeasurementPoint(code='l2_input_hopper_1', name='Tolva 1 línea 2', line_id=line_2.id, point_kind='input', role='feed', source_mode='plc', plc_tag='l2_input_hopper_1', affects_stock=True, affects_production=False, display_order=1),
                    MeasurementPoint(code='l2_input_hopper_2', name='Tolva 2 línea 2', line_id=line_2.id, point_kind='input', role='feed', source_mode='plc', plc_tag='l2_input_hopper_2', affects_stock=True, affects_production=False, display_order=2),
                    MeasurementPoint(code='l2_output_1', name='Salida 1 línea 2', line_id=line_2.id, point_kind='output', role='product', source_mode='mixed', plc_tag='l2_output_1', affects_stock=False, affects_production=True, display_order=3, notes='Puede venir desde PLC o carga manual'),
                ])

        self.db.commit()
        return {'ok': True}
