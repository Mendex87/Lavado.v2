from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.events import AuditLog
from app.schemas.audit import AuditItem


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        *,
        user_id: int | None,
        entity_name: str,
        entity_id: str,
        action: str,
        before_json: dict | None = None,
        after_json: dict | None = None,
    ) -> AuditLog:
        row = AuditLog(
            user_id=user_id,
            entity_name=entity_name,
            entity_id=entity_id,
            action=action,
            before_json=before_json,
            after_json=after_json,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list_recent(self, limit: int = 100) -> list[AuditItem]:
        stmt = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
        rows = list(self.db.scalars(stmt).all())
        return [
            AuditItem(
                id=r.id,
                user_id=r.user_id,
                entity_name=r.entity_name,
                entity_id=r.entity_id,
                action=r.action,
                created_at=r.created_at,
            )
            for r in rows
        ]
