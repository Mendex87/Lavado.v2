from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.measurement import MeasurementPoint, MeasurementReading


class MeasurementRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_active_by_line(self, line_id: int) -> list[MeasurementPoint]:
        stmt = (
            select(MeasurementPoint)
            .where(MeasurementPoint.line_id == line_id, MeasurementPoint.is_active.is_(True))
            .order_by(MeasurementPoint.display_order.asc(), MeasurementPoint.id.asc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_codes(self, line_id: int, codes: list[str]) -> list[MeasurementPoint]:
        if not codes:
            return []
        stmt = (
            select(MeasurementPoint)
            .where(MeasurementPoint.line_id == line_id, MeasurementPoint.code.in_(codes))
        )
        return list(self.db.scalars(stmt).all())

    def get_last_reading(self, measurement_point_id: int) -> MeasurementReading | None:
        stmt = (
            select(MeasurementReading)
            .where(MeasurementReading.measurement_point_id == measurement_point_id)
            .order_by(MeasurementReading.captured_at.desc(), MeasurementReading.id.desc())
        )
        return self.db.scalar(stmt)

    def add_reading(self, reading: MeasurementReading) -> MeasurementReading:
        self.db.add(reading)
        self.db.flush()
        self.db.refresh(reading)
        return reading
