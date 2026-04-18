from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.schemas.audit import AuditItem
from app.services.audit_service import AuditService

router = APIRouter(prefix='/audit', tags=['audit'])


@router.get('/recent', response_model=list[AuditItem], dependencies=[Depends(require_roles('supervisor', 'admin'))])
def list_recent_audit(limit: int = 100, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return AuditService(db).list_recent(limit=limit)
