from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.schemas.settings import AppSettingsItem, AppSettingsPayload
from app.services.settings_service import SettingsService

router = APIRouter(prefix='/settings', tags=['settings'])


@router.get('', response_model=list[AppSettingsItem], dependencies=[Depends(require_roles('admin'))])
def get_settings(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    data = SettingsService(db).get_all()
    return [AppSettingsItem(key=k, value=v) for k, v in data.items()]


@router.put('', response_model=list[AppSettingsItem], dependencies=[Depends(require_roles('admin'))])
def put_settings(payload: AppSettingsPayload, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    data = SettingsService(db).upsert(payload)
    return [AppSettingsItem(key=k, value=v) for k, v in data.items()]
