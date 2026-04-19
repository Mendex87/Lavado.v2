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


@router.get('/plc-config', tags=['public'])
def get_plc_config_public(db: Session = Depends(get_db)):
    """Endpoint público para que el PLC poller lea la configuración sin auth."""
    from app.models.settings import AppSetting
    
    rows = db.query(AppSetting).filter(AppSetting.key.in_(['plc_host', 'plc_rack', 'plc_slot'])).all()
    config = {r.key: r.value for r in rows}
    
    return {
        'plc_host': config.get('plc_host', '192.168.10.77'),
        'plc_rack': config.get('plc_rack', '0'),
        'plc_slot': config.get('plc_slot', '1'),
        'backend_url': 'http://127.0.0.1:8010/api/v1',
    }


@router.get('/reload-plc', tags=['public'])
def check_reload_plc():
    """Endpoint para que el PLC poller verifique si debe recargar config."""
    import os
    flag_file = '.apply_config_pending'
    if os.path.exists(flag_file):
        try:
            os.remove(flag_file)
            return {'reload': True}
        except:
            return {'reload': False}
    return {'reload': False}


@router.post('/reload-plc', tags=['public'])
def trigger_reload_plc():
    """Endpoint para notificar al PLC poller que debe recargar."""
    import os
    flag_file = '.apply_config_pending'
    try:
        with open(flag_file, 'w') as f:
            f.write('')
        return {'status': 'ok', 'message': 'Notificado'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}