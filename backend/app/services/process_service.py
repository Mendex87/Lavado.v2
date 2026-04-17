from datetime import datetime
from app.models.process import Process
from app.repositories.process_repository import ProcessRepository
from app.schemas.process import ProcessCreateRequest


class ProcessService:
    def __init__(self, repository: ProcessRepository):
        self.repository = repository

    def list_active(self):
        return self.repository.list_active()

    def create(self, payload: ProcessCreateRequest) -> Process:
        if self.repository.get_active_by_line(payload.line):
            raise ValueError(f'La línea {payload.line} ya tiene un proceso activo')
        if payload.line == 1 and payload.mode != 'simple':
            raise ValueError('La línea 1 solo permite modo simple')

        process = Process(
            code=f'PR-{datetime.utcnow().strftime("%Y-%H%M%S")}',
            line_id=payload.line,
            shift_id=1,
            shift_code_snapshot='T1',
            shift_name_snapshot='Turno 1',
            operator_user_id=1,
            mode=payload.mode,
            status='active',
            started_at=datetime.utcnow(),
            notes=payload.notes,
        )
        return self.repository.add(process)

    def close(self, code: str, reason: str):
        process = self.repository.get_by_code(code)
        if not process:
            raise LookupError('Proceso no encontrado')
        process.status = 'closed'
        process.close_reason = reason
        process.ended_at = datetime.utcnow()
        self.repository.db.add(process)
        self.repository.db.commit()
        self.repository.db.refresh(process)
        return process
