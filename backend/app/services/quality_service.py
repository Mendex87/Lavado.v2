from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.quality import QualityRecord, QualitySpecification, LotTraceability


class QualityService:
    @staticmethod
    def create_record(db: Session, data: dict) -> QualityRecord:
        record = QualityRecord(
            sample_code=data['sample_code'],
            sample_type=data['sample_type'],
            process_id=data.get('process_id'),
            product_id=data.get('product_id'),
            quarry_id=data.get('quarry_id'),
            mesh_20=data.get('mesh_20'),
            mesh_40=data.get('mesh_40'),
            mesh_80=data.get('mesh_80'),
            mesh_120=data.get('mesh_120'),
            mesh_200=data.get('mesh_200'),
            mesh_fines=data.get('mesh_fines'),
            humidity_pct=data.get('humidity_pct'),
            density=data.get('density'),
            visual_inspection=data.get('visual_inspection'),
            result_status='pending',
            sampled_by_user_id=data.get('sampled_by_user_id'),
            sampled_at=data.get('sampled_at') or datetime.utcnow(),
            notes=data.get('notes'),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def update_record(db: Session, record_id: int, data: dict) -> Optional[QualityRecord]:
        record = db.query(QualityRecord).filter(QualityRecord.id == record_id).first()
        if not record:
            return None
        for key, value in data.items():
            if value is not None and hasattr(record, key):
                setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_records(db: Session, process_id: Optional[int] = None, status: Optional[str] = None, limit: int = 50):
        query = db.query(QualityRecord)
        if process_id:
            query = query.filter(QualityRecord.process_id == process_id)
        if status:
            query = query.filter(QualityRecord.result_status == status)
        return query.order_by(QualityRecord.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_summary(db: Session) -> dict:
        total = db.query(func.count(QualityRecord.id)).scalar() or 0
        approved = db.query(func.count(QualityRecord.id)).filter(QualityRecord.result_status == 'approved').scalar() or 0
        rejected = db.query(func.count(QualityRecord.id)).filter(QualityRecord.result_status == 'rejected').scalar() or 0
        pending = db.query(func.count(QualityRecord.id)).filter(QualityRecord.result_status == 'pending').scalar() or 0
        
        avg_humidity = db.query(func.avg(QualityRecord.humidity_pct)).filter(
            QualityRecord.humidity_pct.isnot(None)
        ).scalar()
        
        return {
            'total_samples': total,
            'approved': approved,
            'rejected': rejected,
            'pending': pending,
            'average_humidity': round(avg_humidity, 2) if avg_humidity else None
        }

    @staticmethod
    def create_specification(db: Session, data: dict) -> QualitySpecification:
        spec = QualitySpecification(
            product_id=data['product_id'],
            mesh_20_min=data.get('mesh_20_min'),
            mesh_20_max=data.get('mesh_20_max'),
            mesh_40_min=data.get('mesh_40_min'),
            mesh_40_max=data.get('mesh_40_max'),
            mesh_80_min=data.get('mesh_80_min'),
            mesh_80_max=data.get('mesh_80_max'),
            mesh_120_min=data.get('mesh_120_min'),
            mesh_120_max=data.get('mesh_120_max'),
            mesh_200_min=data.get('mesh_200_min'),
            mesh_200_max=data.get('mesh_200_max'),
            mesh_fines_max=data.get('mesh_fines_max'),
            humidity_max=data.get('humidity_max'),
            is_active=True,
        )
        db.add(spec)
        db.commit()
        db.refresh(spec)
        return spec

    @staticmethod
    def get_specifications(db: Session, product_id: Optional[int] = None):
        query = db.query(QualitySpecification)
        if product_id:
            query = query.filter(QualitySpecification.product_id == product_id)
        return query.filter(QualitySpecification.is_active == True).all()

    @staticmethod
    def create_lot(db: Session, data: dict) -> LotTraceability:
        lot = LotTraceability(
            lot_number=data['lot_number'],
            process_id=data['process_id'],
            product_id=data['product_id'],
            total_ton=data['total_ton'],
            start_time=data['start_time'],
            status='in_progress',
        )
        db.add(lot)
        db.commit()
        db.refresh(lot)
        return lot

    @staticmethod
    def close_lot(db: Session, lot_id: int, end_time: datetime) -> Optional[LotTraceability]:
        lot = db.query(LotTraceability).filter(LotTraceability.id == lot_id).first()
        if not lot:
            return None
        lot.end_time = end_time
        lot.status = 'completed'
        db.commit()
        db.refresh(lot)
        return lot

    @staticmethod
    def get_lots(db: Session, process_id: Optional[int] = None, status: Optional[str] = None):
        query = db.query(LotTraceability)
        if process_id:
            query = query.filter(LotTraceability.process_id == process_id)
        if status:
            query = query.filter(LotTraceability.status == status)
        return query.order_by(LotTraceability.created_at.desc()).all()