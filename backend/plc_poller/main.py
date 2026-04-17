import json
import time
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


def main() -> None:
    settings = PlcPollerSettings()
    mapping = load_mapping(settings.mapping_path)
    print('PLC poller base listo')
    print(json.dumps(settings.__dict__, indent=2))
    print('Mapa cargado desde', settings.mapping_path)
    try:
        client = Snap7PlcClient(settings.plc_host, settings.plc_rack, settings.plc_slot)
        payloads = read_line_payloads(client, mapping)
        for payload in payloads:
            response = post_json(f"{settings.backend_url}/measurements/ingest", payload)
            print(json.dumps({'payload': payload, 'response': response}, indent=2))
        client.close()
    except RuntimeError as exc:
        print(str(exc))
        print('Modo demo, payloads esperados:')
        for payload in build_demo_payloads(mapping):
            print(json.dumps(payload, indent=2))
    time.sleep(0.1)


if __name__ == '__main__':
    main()
