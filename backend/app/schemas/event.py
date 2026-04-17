from datetime import datetime
from pydantic import BaseModel


class EventItem(BaseModel):
    id: int
    process_code: str | None = None
    event_type: str
    severity: str
    message: str
    created_at: datetime
