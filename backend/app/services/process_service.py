from datetime import datetime
from app.models.process import Process, ProcessInput, ProcessOutput
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.events_repository import EventsRepository
from app.repositories.process_repository import ProcessRepository
from app.schemas.process import ProcessCreateRequest
from app.services.event_service import EventService


class ProcessService:
    def __init__(self, repository: ProcessRepository):
        self.repository = repository
        self.catalog_repository = CatalogRepository(repository.db)
        self.event_service = EventService(EventsRepository(repository.db))

    def list_active(self):
        return self.repository.list_active()

    def create(self, payload: ProcessCreateRequest, operator_user_id: int | None = None) -> Process:
        if self.repository.get_active_by_line(payload.line):
            raise ValueError(f'La línea {payload.line} ya tiene un proceso activo')
        if payload.line == 1 and payload.mode != 'simple':
            raise ValueError('La línea 1 solo permite modo simple')

        shift = self.catalog_repository.get_default_shift()
        if not shift:
            raise ValueError('No hay turnos configurados')
        if operator_user_id is None:
            user = self.catalog_repository.get_user_by_username(payload.operator.lower()) or self.catalog_repository.get_user_by_username('admin')
            if not user:
                raise ValueError('No hay usuario disponible para registrar el proceso')
            operator_user_id = user.id

        process = Process(
            code=f'PR-{datetime.utcnow().strftime("%Y-%H%M%S")}',
            line_id=payload.line,
            shift_id=shift.id,
            shift_code_snapshot=shift.code,
            shift_name_snapshot=shift.name,
            operator_user_id=operator_user_id,
            mode=payload.mode,
            status='active',
            started_at=datetime.utcnow(),
            notes=payload.notes,
        )
        process = self.repository.add(process)

        quarries = {q.name: q for q in self.catalog_repository.get_quarries_by_names([i.quarry for i in payload.inputs])}
        for idx, item in enumerate(payload.inputs, start=1):
            quarry = quarries.get(item.quarry)
            if not quarry:
                raise ValueError(f'Cantera no encontrada: {item.quarry}')
            self.repository.db.add(ProcessInput(
                process_id=process.id,
                quarry_id=quarry.id,
                input_order=idx,
                hopper_code=item.hopper_code,
                blend_target_pct=item.blend_target_pct,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ))

        for item in payload.outputs:
            product = self.catalog_repository.get_product_by_name(item.product)
            self.repository.db.add(ProcessOutput(
                process_id=process.id,
                product_id=product.id if product else None,
                output_code=item.output_code,
                classification=item.classification,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ))

        self.event_service.register(
            process.id,
            event_type='process_opened',
            severity='info',
            message=f'Proceso {process.code} abierto en línea {payload.line}',
            payload={'mode': payload.mode, 'operator': payload.operator},
        )
        return process

    def close(self, code: str, reason: str):
        process = self.repository.get_by_code(code)
        if not process:
            raise LookupError('Proceso no encontrado')
        process.status = 'closed'
        process.close_reason = reason
        process.ended_at = datetime.utcnow()
        self.repository.db.add(process)
        self.event_service.register(
            process.id,
            event_type='process_closed',
            severity='info',
            message=f'Proceso {process.code} cerrado',
            payload={'reason': reason},
        )
        return process
