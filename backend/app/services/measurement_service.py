from decimal import Decimal
from app.models.measurement import MeasurementReading
from app.repositories.measurement_repository import MeasurementRepository
from app.repositories.process_repository import ProcessRepository
from app.schemas.measurement import MeasurementIngestRequest, MeasurementIngestResult, MeasurementPointItem
from app.services.plc_mock_state import plc_mock_state


class MeasurementService:
    def __init__(self, db):
        self.db = db
        self.measurement_repository = MeasurementRepository(db)
        self.process_repository = ProcessRepository(db)

    def list_points(self, line: int | None = None) -> list[MeasurementPointItem]:
        points = []
        if line is None:
            for line_id in (1, 2):
                points.extend(self.measurement_repository.list_active_by_line(line_id))
        else:
            points = self.measurement_repository.list_active_by_line(line)
        return [
            MeasurementPointItem(
                code=point.code,
                name=point.name,
                line=point.line_id,
                point_kind=point.point_kind,
                role=point.role,
                source_mode=point.source_mode,
                plc_tag=point.plc_tag,
                affects_stock=point.affects_stock,
                affects_production=point.affects_production,
                is_active=point.is_active,
            )
            for point in points
        ]

    def ingest(self, payload: MeasurementIngestRequest) -> MeasurementIngestResult:
        process = self.process_repository.get_active_by_line(payload.line)
        points = {point.code: point for point in self.measurement_repository.get_by_codes(payload.line, [item.code for item in payload.channels])}
        created = 0

        for item in payload.channels:
            point = points.get(item.code)
            if not point:
                continue
            last = self.measurement_repository.get_last_reading(point.id)
            delta_ton = None
            if item.totalizer_ton is not None:
                last_totalizer = float(last.totalizer_ton) if last and last.totalizer_ton is not None else None
                delta_ton = item.totalizer_ton - last_totalizer if last_totalizer is not None else 0.0
                if delta_ton is not None and delta_ton < 0:
                    delta_ton = None

            self.measurement_repository.add_reading(MeasurementReading(
                measurement_point_id=point.id,
                process_id=process.id if process else None,
                source=payload.source,
                captured_at=payload.captured_at,
                partial_ton=Decimal(str(item.partial_ton)) if item.partial_ton is not None else None,
                totalizer_ton=Decimal(str(item.totalizer_ton)) if item.totalizer_ton is not None else None,
                delta_ton=Decimal(str(delta_ton)) if delta_ton is not None else None,
                raw_value_text=item.raw_value_text,
                entered_by_user_id=None,
                notes=None,
            ))
            created += 1

        if payload.reset_partials_ack:
            plc_mock_state['context']['reset_partials_requested'] = False

        self.db.commit()
        return MeasurementIngestResult(
            ok=True,
            line=payload.line,
            process_code=process.code if process else None,
            readings_created=created,
            reset_partials_ack=payload.reset_partials_ack,
        )
