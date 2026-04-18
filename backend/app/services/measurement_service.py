from datetime import datetime
from decimal import Decimal
from app.models.catalog import Quarry
from app.models.process import ProcessInput
from app.models.stock import QuarryStockMovement
from app.models.measurement import MeasurementReading
from app.repositories.stock_repository import StockRepository
from app.repositories.measurement_repository import MeasurementRepository
from app.repositories.process_repository import ProcessRepository
from app.schemas.measurement import (
    MeasurementIngestRequest,
    MeasurementIngestResult,
    MeasurementLatestItem,
    MeasurementManualOperationPayload,
    MeasurementManualResult,
    MeasurementPointItem,
)
from app.services.plc_mock_state import plc_mock_state


class MeasurementService:
    def __init__(self, db):
        self.db = db
        self.measurement_repository = MeasurementRepository(db)
        self.process_repository = ProcessRepository(db)
        self.stock_repository = StockRepository(db)

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

    def manual_ingest(self, payload: MeasurementManualOperationPayload, entered_by_user_id: int) -> MeasurementManualResult:
        line = int(payload.line)
        process = self.process_repository.get_active_by_line(line)
        if not process:
            raise ValueError(f'No hay proceso activo en línea {line}')

        channels: list[dict] = []
        if payload.feed_l1_partial_ton is not None:
            channels.append({'code': 'l1_input_main', 'partial_ton': payload.feed_l1_partial_ton})
        if payload.feed_l2_h1_partial_ton is not None:
            channels.append({'code': 'l2_input_hopper_1', 'partial_ton': payload.feed_l2_h1_partial_ton})
        if payload.feed_l2_h2_partial_ton is not None:
            channels.append({'code': 'l2_input_hopper_2', 'partial_ton': payload.feed_l2_h2_partial_ton})

        if payload.product_1_partial_ton is not None:
            channels.append({'code': 'l1_output_1', 'partial_ton': payload.product_1_partial_ton})
        if payload.product_2_partial_ton is not None:
            channels.append({'code': 'l1_output_2', 'partial_ton': payload.product_2_partial_ton})
        if payload.product_3_partial_ton is not None:
            channels.append({'code': 'l2_output_1', 'partial_ton': payload.product_3_partial_ton})
        if payload.product_4_partial_ton is not None:
            channels.append({'code': 'l1_output_3', 'partial_ton': payload.product_4_partial_ton})

        if not channels:
            return MeasurementManualResult(ok=True, line=line, source='manual', readings_created=0, stock_updates=[])

        ingest_payload = MeasurementIngestRequest(
            captured_at=datetime.utcnow(),
            line=line,
            source='manual',
            reset_partials_ack=False,
            channels=channels,
        )
        result = self.ingest(ingest_payload, entered_by_user_id=entered_by_user_id)
        stock_updates = self._apply_manual_stock_discounts(process.id, payload, entered_by_user_id)
        return MeasurementManualResult(
            ok=result.ok,
            line=result.line,
            source='manual',
            readings_created=result.readings_created,
            stock_updates=stock_updates,
        )

    def _apply_manual_stock_discounts(self, process_id: int, payload: MeasurementManualOperationPayload, user_id: int) -> list[dict]:
        inputs = (
            self.db.query(ProcessInput)
            .filter(ProcessInput.process_id == process_id)
            .order_by(ProcessInput.input_order.asc())
            .all()
        )
        if not inputs:
            return []

        allowed_quarry_ids = {int(i.quarry_id) for i in inputs}
        discounts_by_quarry: dict[int, float] = {}

        def quarry_id_by_name(name: str | None) -> int:
            if not name:
                raise ValueError('Falta indicar cantera para el parcial manual de alimentación')
            q = self.db.query(Quarry).filter(Quarry.name == name).first()
            if not q:
                raise ValueError(f'Cantera no encontrada: {name}')
            if int(q.id) not in allowed_quarry_ids:
                raise ValueError(f'La cantera {name} no pertenece al proceso activo de la línea')
            return int(q.id)

        if payload.feed_l1_partial_ton is not None:
            qid = quarry_id_by_name(payload.feed_l1_quarry)
            discounts_by_quarry[qid] = discounts_by_quarry.get(qid, 0.0) + float(payload.feed_l1_partial_ton)

        if payload.feed_l2_h1_partial_ton is not None:
            qid = quarry_id_by_name(payload.feed_l2_h1_quarry)
            discounts_by_quarry[qid] = discounts_by_quarry.get(qid, 0.0) + float(payload.feed_l2_h1_partial_ton)

        if payload.feed_l2_h2_partial_ton is not None:
            qid = quarry_id_by_name(payload.feed_l2_h2_quarry)
            discounts_by_quarry[qid] = discounts_by_quarry.get(qid, 0.0) + float(payload.feed_l2_h2_partial_ton)

        updates = []
        for quarry_id, qty in discounts_by_quarry.items():
            if qty <= 0:
                continue
            stock = self.stock_repository.get_stock_by_quarry_id(quarry_id)
            if not stock:
                continue
            current = float(stock.current_ton)
            stock.current_ton = Decimal(str(current - qty))
            self.db.add(stock)

            movement = QuarryStockMovement(
                quarry_id=quarry_id,
                process_id=process_id,
                scale_id=None,
                movement_type='process_consumption_manual',
                direction='out',
                quantity_ton=Decimal(str(qty)),
                signed_quantity_ton=Decimal(str(-qty)),
                source='manual',
                reference_code=f'process:{process_id}',
                entered_by_user_id=user_id,
                reason='Descuento por carga manual de parciales de alimentación',
            )
            self.stock_repository.add_movement(movement)
            updates.append({'quarry_id': quarry_id, 'discount_ton': round(qty, 3), 'new_stock_ton': round(current - qty, 3)})

        self.db.commit()
        return updates
