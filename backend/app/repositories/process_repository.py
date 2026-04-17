from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.process import Process


class ProcessRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_active(self) -> list[Process]:
        stmt = select(Process).where(Process.status == 'active').order_by(Process.line_id.asc())
        return list(self.db.scalars(stmt).all())

    def get_by_code(self, code: str) -> Process | None:
        stmt = select(Process).where(Process.code == code)
        return self.db.scalar(stmt)

    def get_active_by_line(self, line_id: int) -> Process | None:
        stmt = select(Process).where(Process.line_id == line_id, Process.status == 'active')
        return self.db.scalar(stmt)

    def add(self, process: Process) -> Process:
        self.db.add(process)
        self.db.flush()
        self.db.refresh(process)
        return process
