from __future__ import annotations

from datetime import datetime, timezone
from plc_poller.client import PlcAddress, Snap7PlcClient


def read_line_payloads(client: Snap7PlcClient, mapping: dict) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    reset_ack = False
    flags = mapping.get('flags') or {}
    reset_address = flags.get('reset_partials_ack')
    if reset_address:
        reset_ack = bool(client.read(PlcAddress(**reset_address)))

    payloads: list[dict] = []
    for line_cfg in mapping.get('lines', []):
        channels = []
        for channel in line_cfg.get('channels', []):
            item = {'code': channel['code']}
            partial_address = channel.get('partial')
            totalizer_address = channel.get('totalizer')
            if partial_address:
                item['partial_ton'] = client.read(PlcAddress(**partial_address))
            if totalizer_address:
                item['totalizer_ton'] = client.read(PlcAddress(**totalizer_address))
            channels.append(item)
        payloads.append({
            'captured_at': now,
            'line': line_cfg['line'],
            'source': 'plc',
            'reset_partials_ack': reset_ack,
            'channels': channels,
        })
    return payloads
