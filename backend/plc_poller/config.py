from dataclasses import dataclass
import os
import requests
import json


@dataclass
class PlcPollerSettings:
    plc_host: str = '127.0.0.1'
    plc_rack: int = 0
    plc_slot: int = 1
    backend_url: str = os.getenv('BACKEND_URL', 'http://127.0.0.1:8010/api/v1')
    mapping_path: str = os.getenv('PLC_MAPPING_PATH', 'plc_poller/mapping.example.json')
    poll_interval_seconds: float = float(os.getenv('PLC_POLL_INTERVAL_SECONDS', '5'))
    _loaded_from_backend: bool = False

    @classmethod
    def load_from_backend(cls, backend_url: str = None) -> 'PlcPollerSettings':
        """Carga la configuración desde el backend ( endpoint público /settings/plc-config )."""
        url = (backend_url or os.getenv('BACKEND_URL', 'http://127.0.0.1:8010/api/v1')) + '/settings/plc-config'
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                settings = cls(
                    plc_host=data.get('plc_host', '127.0.0.1'),
                    plc_rack=int(data.get('plc_rack', 0)),
                    plc_slot=int(data.get('plc_slot', 1)),
                    backend_url=data.get('backend_url', 'http://127.0.0.1:8010/api/v1'),
                    mapping_path=os.getenv('PLC_MAPPING_PATH', 'plc_poller/mapping.example.json'),
                    poll_interval_seconds=float(data.get('poll_interval_seconds', 5)),
                    _loaded_from_backend=True,
                )
                print('Configuración cargada desde backend')
                return settings
        except Exception as e:
            print(f'No se pudo cargar config del backend: {e}')
            print('Usando configuración por defecto')
        
        # Fallback a configuración por defecto
        return cls()
