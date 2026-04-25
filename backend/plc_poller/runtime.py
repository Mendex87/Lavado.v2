from __future__ import annotations

import math
from datetime import datetime, timezone
from plc_poller.client import PlcAddress, Snap7PlcClient


def _safe_float(value):
    try:
        f = float(value)
    except Exception:
        return None
    if math.isfinite(f):
        return f
    return None


def read_line_payloads(client: Snap7PlcClient, mapping: dict) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    reset_ack = False
    flags = mapping.get('flags') or {}
    reset_address = flags.get('reset_partials_ack')
    if reset_address:
        reset_ack = bool(client.read(PlcAddress(**reset_address)))

    payloads: list[dict] = []
    for line_cfg in mapping.get('lines', []):
        line_num = line_cfg['line']
        channels = []
        for channel in line_cfg.get('channels', []):
            code = channel['code']
            item = {'code': code}
            partial_address = channel.get('partial')
            totalizer_address = channel.get('totalizer')
            
            if partial_address:
                val = _safe_float(client.read(PlcAddress(**partial_address)))
                item['partial_ton'] = val
            if totalizer_address:
                val = _safe_float(client.read(PlcAddress(**totalizer_address)))
                item['totalizer_ton'] = val
            channels.append(item)
        
        payloads.append({
            'captured_at': now,
            'line': line_num,
            'source': 'plc',
            'reset_partials_ack': reset_ack,
            'channels': channels,
        })
    return payloads
