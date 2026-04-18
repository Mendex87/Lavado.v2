from datetime import datetime
from decimal import Decimal
from app.models.measurement import MeasurementReading
from app.repositories.measurement_repository import MeasurementRepository
from app.repositories.process_repository import ProcessRepository
from app.schemas.measurement import (
    MeasurementIngestRequest,
    MeasurementIngestResult,
    MeasurementLatestItem,
    MeasurementManualLinePayload,
    MeasurementManualResult,
    MeasurementPointItem,
)
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

    def ingest(self, payload: MeasurementIngestRequest, entered_by_user_id: int | None = None) -> MeasurementIngestResult:
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
                entered_by_user_id=entered_by_user_id,
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

    def list_latest(self, line: int | None = None) -> list[MeasurementLatestItem]:
        points = []
        if line is None:
            for line_id in (1, 2):
                points.extend(self.measurement_repository.list_active_by_line(line_id))
        else:
            points = self.measurement_repository.list_active_by_line(line)

        items: list[MeasurementLatestItem] = []
        for point in points:
            last = self.measurement_repository.get_last_reading(point.id)
            items.append(MeasurementLatestItem(
                code=point.code,
                name=point.name,
                line=point.line_id,
                source=last.source if last else None,
                captured_at=last.captured_at if last else None,
                partial_ton=float(last.partial_ton) if last and last.partial_ton is not None else None,
                totalizer_ton=float(last.totalizer_ton) if last and last.totalizer_ton is not None else None,
                delta_ton=float(last.delta_ton) if last and last.delta_ton is not None else None,
            ))
        return items

    def manual_ingest(self, payload: MeasurementManualLinePayload, entered_by_user_id: int) -> MeasurementManualResult:
        line = int(payload.line)
        channels = []
        if line == 1:
            if payload.tph is not None:
                channels.append({'code': 'l1_input_tph', 'partial_ton': payload.tph})
            if payload.partial_ton is not None or payload.totalizer_ton is not None:
                channels.append({
                    'code': 'l1_input_main',
                    'partial_ton': payload.partial_ton,
                    'totalizer_ton': payload.totalizer_ton,
                })
        elif line == 2:
            if payload.tph is not None:
                half = payload.tph / 2
                channels.append({'code': 'l2_input_tph_a', 'partial_ton': half})
                channels.append({'code': 'l2_input_tph_b', 'partial_ton': half})
            if payload.partial_ton is not None or payload.totalizer_ton is not None:
                channels.append({
                    'code': 'l2_input_hopper_1',
                    'partial_ton': payload.partial_ton,
                    'totalizer_ton': payload.totalizer_ton,
                })
        if not channels:
            return MeasurementManualResult(ok=True, line=line, source='manual', readings_created=0)

        ingest_payload = MeasurementIngestRequest(
            captured_at=datetime.utcnow(),
            line=line,
            source='manual',
            reset_partials_ack=False,
            channels=channels,
        )
        result = self.ingest(ingest_payload, entered_by_user_id=entered_by_user_id)
        return MeasurementManualResult(
            ok=result.ok,
            line=result.line,
            source='manual',
            readings_created=result.readings_created,
        )
