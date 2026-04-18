from datetime import datetime
from pydantic import BaseModel


class AuditItem(BaseModel):
    id: int
    user_id: int | None
    entity_name: str
    entity_id: str
    action: str
    created_at: datetime
