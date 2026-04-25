from sqlalchemy import select, func, desc
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

    def get_latest_by_point_ids(self, point_ids: list[int]) -> dict[int, MeasurementReading]:
        if not point_ids:
            return {}
        latest_ids_subq = (
            select(
                MeasurementReading.measurement_point_id.label('mp_id'),
                func.max(MeasurementReading.id).label('latest_id'),
            )
            .where(MeasurementReading.measurement_point_id.in_(point_ids))
            .group_by(MeasurementReading.measurement_point_id)
            .subquery()
        )
        stmt = (
            select(MeasurementReading)
            .join(latest_ids_subq, MeasurementReading.id == latest_ids_subq.c.latest_id)
        )
        rows = list(self.db.scalars(stmt).all())
        return {int(r.measurement_point_id): r for r in rows}

    def get_latest_by_codes_optimized(self, codes: list[str]) -> list[tuple[MeasurementPoint, MeasurementReading | None]]:
        """Optimizado: obtiene puntos y latest readings en una sola query."""
        if not codes:
            return []
        
        points_subq = (
            select(MeasurementPoint)
            .where(MeasurementPoint.code.in_(codes))
            .subquery()
        )
        
        latest_subq = (
            select(
                MeasurementReading.measurement_point_id,
                MeasurementReading.captured_at,
                MeasurementReading.partial_ton,
                MeasurementReading.totalizer_ton,
                MeasurementReading.delta_ton,
                MeasurementReading.source,
                func.row_number()
                .over(
                    partition_by=MeasurementReading.measurement_point_id,
                    order_by=desc(MeasurementReading.id)
                ).label('rn')
            )
            .where(MeasurementReading.measurement_point_id.in_(
                select(MeasurementPoint.id).where(MeasurementPoint.code.in_(codes))
            ))
            .subquery()
        )
        
        stmt = (
            select(MeasurementPoint, latest_subq.c.captured_at, latest_subq.c.partial_ton, 
                   latest_subq.c.totalizer_ton, latest_subq.c.delta_ton, latest_subq.c.source)
            .outerjoin(latest_subq, (MeasurementPoint.id == latest_subq.c.measurement_point_id) & (latest_subq.c.rn == 1))
            .where(MeasurementPoint.code.in_(codes))
            .order_by(MeasurementPoint.display_order.asc(), MeasurementPoint.id.asc())
        )
        
        rows = self.db.execute(stmt).fetchall()
        result = []
        for row in rows:
            point = row[0]
            reading = None
            if row[1]:  # captured_at not null
                reading = MeasurementReading(
                    id=0,
                    measurement_point_id=point.id,
                    captured_at=row[1],
                    partial_ton=row[2],
                    totalizer_ton=row[3],
                    delta_ton=row[4],
                    source=row[5],
                )
            result.append((point, reading))
        return result
