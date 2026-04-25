import json
import time
import os
from datetime import datetime, timezone
from plc_poller.client import Snap7PlcClient
from plc_poller.config import PlcPollerSettings
from plc_poller.loader import load_mapping
from plc_poller.publisher import post_json
from plc_poller.runtime import read_line_payloads


def build_demo_payloads(mapping: dict) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    payloads = []
    for line_cfg in mapping.get('lines', []):
        payloads.append({
            'captured_at': now,
            'line': line_cfg['line'],
            'source': 'plc',
            'reset_partials_ack': False,
            'channels': [
                {'code': channel['code'], 'partial_ton': 0.0, 'totalizer_ton': 0.0}
                for channel in line_cfg.get('channels', [])
            ],
        })
    return payloads


def reload_config_if_needed(settings, backend_url):
    """Recarga la config del backend cada 10 intentos para detectar cambios de IP."""
    new_settings = PlcPollerSettings.load_from_backend(backend_url)
    if new_settings.plc_host != settings.plc_host:
        print(f"PLC IP cambiada: {settings.plc_host} -> {new_settings.plc_host}")
        return new_settings
    return settings


def check_reload_needed(backend_url):
    """Verifica si el backend indica que hay que recargar config."""
    try:
        import requests
        url = backend_url + '/settings/reload-plc'
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data.get('reload', False)
    except:
        pass
    return False


def poll_with_apply_button(backend_url):
    """Poller que responde al botón 'Aplicar configuración'."""
    settings = PlcPollerSettings.load_from_backend(backend_url)
    mapping = load_mapping(settings.mapping_path)
    current_host = settings.plc_host
    
    print('PLC poller iniciado')
    print(f'Intervalo: {settings.poll_interval_seconds}s | PLC: {settings.plc_host}')
    print('Esperando botón "Aplicar" o abra un proceso para guardar datos...')
    
    while True:
        # Check if apply button was pressed
        if check_reload_needed(backend_url):
            old_host = settings.plc_host
            settings = PlcPollerSettings.load_from_backend(backend_url)
            new_host = settings.plc_host
            print(f"¡Botón aplicar recibido! {old_host} -> {new_host}")
            print(json.dumps(settings.__dict__, indent=2))
        
        try:
            client = Snap7PlcClient(settings.plc_host, settings.plc_rack, settings.plc_slot)
            payloads = read_line_payloads(client, mapping)
            for payload in payloads:
                response = post_json(f"{settings.backend_url}/measurements/ingest", payload)
                status = response.get('status', 'unknown')
                reads = response.get('readings_created', 0)
                if status == 'idle':
                    print(f"L{payload['line']}: idle (no proceso activo)")
                else:
                    print(f"L{payload['line']}: {reads} guardados [{status}]")
            client.close()
        except RuntimeError as exc:
            print(f"Error conexión: {settings.plc_host}")
        except Exception as exc:
            print(f"Error: {exc}")
        time.sleep(settings.poll_interval_seconds)


def main() -> None:
    backend_url = os.getenv('BACKEND_URL', 'http://127.0.0.1:8010/api/v1')
    poll_with_apply_button(backend_url)


if __name__ == '__main__':
    main()
