from pydantic import BaseModel


class AppSettingsItem(BaseModel):
    key: str
    value: str


class AppSettingsPayload(BaseModel):
    plc_host: str
    plc_rack: str
    plc_slot: str
    plant_timezone: str
