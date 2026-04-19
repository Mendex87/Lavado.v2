from pydantic import BaseModel
from typing import Optional


class HandoverStartRequest(BaseModel):
    to_user_id: int
    from_shift_id: int
    to_shift_id: int


class ChecklistItem(BaseModel):
    id: int
    text: str
    checked: bool
    checked_at: Optional[str] = None


class HandoverPendingResponse(BaseModel):
    id: int
    from_user_id: int
    process_summary: list
    stock_summary: list
    pending_issues: list
    checklist: list[ChecklistItem]


class ChecklistResultItem(BaseModel):
    id: int
    checked: bool


class HandoverCompleteRequest(BaseModel):
    checklist_results: list[ChecklistResultItem]
    notes: Optional[str] = None


class HandoverCompleteResponse(BaseModel):
    id: int
    status: str
    completed_at: str


class HandoverHistoryItem(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    started_at: Optional[str]
    completed_at: Optional[str]
    status: str


class HandoverStartResponse(BaseModel):
    id: int
    status: str
    process_summary: list
    stock_summary: list
    checklist: list