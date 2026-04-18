from sqlalchemy.orm import Session
from app.models.catalog import Line, Quarry, Product, Role, Shift, User, UserRole
from app.models.measurement import MeasurementPoint
from app.models.stock import QuarryStock
from app.core.security import get_password_hash, is_password_hash


class SeedService:
    def __init__(self, db: Session):
        self.db = db

    def run(self):
        def ensure_measurement_point(line_id: int, code: str, **kwargs):
            exists = self.db.query(MeasurementPoint).filter(MeasurementPoint.code == code).first()
            if exists:
                return
            self.db.add(MeasurementPoint(code=code, line_id=line_id, **kwargs))

        if not self.db.query(Role).first():
            self.db.add_all([
                Role(code='operador', name='Operador'),
                Role(code='supervisor', name='Supervisor'),
                Role(code='admin', name='Administrador'),
            ])
        else:
            role_codes = {r.code for r in self.db.query(Role).all()}
            if 'admin' not in role_codes:
                self.db.add(Role(code='admin', name='Administrador'))
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
                User(username='admin', full_name='Administrador', password_hash=get_password_hash('change-me'), is_active=True),
                User(username='diego', full_name='Diego', password_hash=get_password_hash('change-me'), is_active=True),
                User(username='juan', full_name='Juan', password_hash=get_password_hash('change-me'), is_active=True),
                User(username='eze', full_name='Eze', password_hash=get_password_hash('change-me'), is_active=True),
            ])
        else:
            users = self.db.query(User).all()
            changed = False
            for u in users:
                if not is_password_hash(u.password_hash):
                    u.password_hash = get_password_hash(u.password_hash)
                    changed = True
            if changed:
                self.db.flush()

        self.db.flush()

        roles_by_code = {r.code: r for r in self.db.query(Role).all()}
        users_by_username = {u.username: u for u in self.db.query(User).all()}

        default_assignments = {
            'admin': ['admin'],
            'eze': ['supervisor'],
            'diego': ['operador'],
            'juan': ['operador'],
        }
        for username, role_codes in default_assignments.items():
            user = users_by_username.get(username)
            if not user:
                continue
            for role_code in role_codes:
                role = roles_by_code.get(role_code)
                if not role:
                    continue
                exists = (
                    self.db.query(UserRole)
                    .filter(UserRole.user_id == user.id, UserRole.role_id == role.id)
                    .first()
                )
                if not exists:
                    self.db.add(UserRole(user_id=user.id, role_id=role.id))

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
        line_1 = self.db.query(Line).filter(Line.code == 'L1').first()
        line_2 = self.db.query(Line).filter(Line.code == 'L2').first()
        if line_1:
            ensure_measurement_point(
                line_1.id,
                code='l1_input_main',
                name='Entrada línea 1',
                point_kind='input',
                role='feed',
                source_mode='plc',
                plc_tag='l1_input_main',
                affects_stock=True,
                affects_production=False,
                display_order=1,
            )
            ensure_measurement_point(
                line_1.id,
                code='l1_input_tph',
                name='Alimentación actual línea 1 (tn/h)',
                point_kind='input',
                role='feed_rate',
                source_mode='plc',
                plc_tag='l1_input_tph',
                affects_stock=False,
                affects_production=False,
                display_order=2,
                notes='Valor instantáneo de alimentación en tn/h',
            )
            ensure_measurement_point(
                line_1.id,
                code='l1_output_1',
                name='Salida 1 línea 1',
                point_kind='output',
                role='product',
                source_mode='plc',
                plc_tag='l1_output_1',
                affects_stock=False,
                affects_production=True,
                display_order=3,
            )
            ensure_measurement_point(
                line_1.id,
                code='l1_output_2',
                name='Salida 2 línea 1',
                point_kind='output',
                role='product',
                source_mode='plc',
                plc_tag='l1_output_2',
                affects_stock=False,
                affects_production=True,
                display_order=4,
            )
            ensure_measurement_point(
                line_1.id,
                code='l1_output_3',
                name='Salida 3 línea 1',
                point_kind='output',
                role='product',
                source_mode='manual',
                plc_tag='l1_output_3',
                affects_stock=False,
                affects_production=True,
                display_order=5,
                notes='Punto preparado para fallback manual o futura balanza',
            )
        if line_2:
            ensure_measurement_point(
                line_2.id,
                code='l2_input_hopper_1',
                name='Tolva 1 línea 2',
                point_kind='input',
                role='feed',
                source_mode='plc',
                plc_tag='l2_input_hopper_1',
                affects_stock=True,
                affects_production=False,
                display_order=1,
            )
            ensure_measurement_point(
                line_2.id,
                code='l2_input_tph',
                name='Alimentación actual línea 2 (tn/h)',
                point_kind='input',
                role='feed_rate',
                source_mode='plc',
                plc_tag='l2_input_tph',
                affects_stock=False,
                affects_production=False,
                display_order=2,
                notes='Valor instantáneo de alimentación en tn/h',
            )
            ensure_measurement_point(
                line_2.id,
                code='l2_input_tph_a',
                name='Alimentación A línea 2 (tn/h)',
                point_kind='input',
                role='feed_rate_a',
                source_mode='plc',
                plc_tag='l2_input_tph_a',
                affects_stock=False,
                affects_production=False,
                display_order=3,
                notes='Caudal instantáneo de alimentación A en tn/h',
            )
            ensure_measurement_point(
                line_2.id,
                code='l2_input_tph_b',
                name='Alimentación B línea 2 (tn/h)',
                point_kind='input',
                role='feed_rate_b',
                source_mode='plc',
                plc_tag='l2_input_tph_b',
                affects_stock=False,
                affects_production=False,
                display_order=4,
                notes='Caudal instantáneo de alimentación B en tn/h',
            )
            ensure_measurement_point(
                line_2.id,
                code='l2_input_hopper_2',
                name='Tolva 2 línea 2',
                point_kind='input',
                role='feed',
                source_mode='plc',
                plc_tag='l2_input_hopper_2',
                affects_stock=True,
                affects_production=False,
                display_order=5,
            )
            ensure_measurement_point(
                line_2.id,
                code='l2_output_1',
                name='Salida 1 línea 2',
                point_kind='output',
                role='product',
                source_mode='mixed',
                plc_tag='l2_output_1',
                affects_stock=False,
                affects_production=True,
                display_order=6,
                notes='Puede venir desde PLC o carga manual',
            )

        self.db.commit()
        return {'ok': True}
