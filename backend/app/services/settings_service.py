from sqlalchemy.orm import Session
from app.models.settings import AppSetting
from app.schemas.settings import AppSettingsPayload


class SettingsService:
    DEFAULTS = {
        'plc_host': '192.168.10.77',
        'plc_rack': '0',
        'plc_slot': '1',
        'plant_timezone': 'America/Sao_Paulo',
    }

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> dict[str, str]:
        rows = self.db.query(AppSetting).all()
        data = {r.key: r.value for r in rows}
        for k, v in self.DEFAULTS.items():
            data.setdefault(k, v)
        return data

    def upsert(self, payload: AppSettingsPayload) -> dict[str, str]:
        data = {
            'plc_host': payload.plc_host.strip(),
            'plc_rack': payload.plc_rack.strip(),
            'plc_slot': payload.plc_slot.strip(),
            'plant_timezone': payload.plant_timezone.strip(),
        }
        for key, value in data.items():
            row = self.db.query(AppSetting).filter(AppSetting.key == key).first()
            if row:
                row.value = value
                self.db.add(row)
            else:
                self.db.add(AppSetting(key=key, value=value))
        self.db.commit()
        return self.get_all()
