from datetime import datetime
from pydantic import BaseModel


class AlarmItem(BaseModel):
    id: int
    line: int | None
    alarm_type: str
    severity: str
    message: str
    started_at: datetime
    acknowledged: bool
    acknowledged_at: datetime | None
    acknowledged_by_user_id: int | None


class AlarmAckResult(BaseModel):
    ok: bool
    alarm_id: int
