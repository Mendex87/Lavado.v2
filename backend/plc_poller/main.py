import json
import time
from datetime import datetime, timezone
from plc_poller.config import PlcPollerSettings


def build_demo_payloads() -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            'captured_at': now,
            'line': 1,
            'source': 'plc',
            'reset_partials_ack': False,
            'channels': [
                {'code': 'l1_input_main', 'partial_ton': 0.0, 'totalizer_ton': 0.0},
                {'code': 'l1_output_1', 'partial_ton': 0.0, 'totalizer_ton': 0.0},
                {'code': 'l1_output_2', 'partial_ton': 0.0, 'totalizer_ton': 0.0},
            ],
        },
        {
            'captured_at': now,
            'line': 2,
            'source': 'plc',
            'reset_partials_ack': False,
            'channels': [
                {'code': 'l2_input_hopper_1', 'partial_ton': 0.0, 'totalizer_ton': 0.0},
                {'code': 'l2_input_hopper_2', 'partial_ton': 0.0, 'totalizer_ton': 0.0},
                {'code': 'l2_output_1', 'partial_ton': 0.0, 'totalizer_ton': 0.0},
            ],
        },
    ]


def main() -> None:
    settings = PlcPollerSettings()
    print('PLC poller placeholder listo')
    print(json.dumps(settings.__dict__, indent=2))
    print('Próximo paso: reemplazar build_demo_payloads() por lectura real S7 con python-snap7')
    for payload in build_demo_payloads():
        print(json.dumps(payload, indent=2))
    time.sleep(0.1)


if __name__ == '__main__':
    main()
