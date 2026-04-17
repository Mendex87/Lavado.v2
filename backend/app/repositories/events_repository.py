from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.events import ProcessEvent


class EventsRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, event: ProcessEvent) -> ProcessEvent:
        self.db.add(event)
        self.db.flush()
        self.db.refresh(event)
        return event

    def list_recent(self, limit: int = 50) -> list[ProcessEvent]:
        stmt = select(ProcessEvent).order_by(ProcessEvent.id.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())
