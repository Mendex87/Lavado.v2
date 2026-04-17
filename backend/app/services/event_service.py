from datetime import datetime
from app.models.events import ProcessEvent
from app.repositories.events_repository import EventsRepository


class EventService:
    def __init__(self, repository: EventsRepository):
        self.repository = repository

    def register(self, process_id: int | None, event_type: str, severity: str, message: str, payload: dict | None = None):
        event = ProcessEvent(
            process_id=process_id,
            user_id=1,
            event_type=event_type,
            severity=severity,
            message=message,
            payload_json=payload,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return self.repository.add(event)
