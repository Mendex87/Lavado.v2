from dataclasses import dataclass
import os


@dataclass
class PlcPollerSettings:
    plc_host: str = os.getenv('PLC_HOST', '127.0.0.1')
    plc_rack: int = int(os.getenv('PLC_RACK', '0'))
    plc_slot: int = int(os.getenv('PLC_SLOT', '1'))
    backend_url: str = os.getenv('BACKEND_URL', 'http://127.0.0.1:8010/api/v1')
    mapping_path: str = os.getenv('PLC_MAPPING_PATH', 'plc_poller/mapping.example.json')
    poll_interval_seconds: float = float(os.getenv('PLC_POLL_INTERVAL_SECONDS', '2'))
