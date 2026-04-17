from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.events_repository import EventsRepository
from app.repositories.process_repository import ProcessRepository
from app.schemas.event import EventItem

router = APIRouter(prefix='/events', tags=['events'])


@router.get('/recent', response_model=list[EventItem])
def list_recent_events(db: Session = Depends(get_db)):
    events = EventsRepository(db).list_recent(limit=50)
    process_repo = ProcessRepository(db)
    items = []
    for event in events:
        process_code = None
        if event.process_id:
            process = process_repo.get_by_id(event.process_id)
            process_code = process.code if process else None
        items.append(EventItem(
            id=event.id,
            process_code=process_code,
            event_type=event.event_type,
            severity=event.severity,
            message=event.message,
            created_at=event.created_at,
        ))
    return items
