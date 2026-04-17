from __future__ import annotations

import json
from urllib import request


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode('utf-8')
    req = request.Request(
        url,
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with request.urlopen(req, timeout=15) as response:
        raw = response.read().decode('utf-8')
        return json.loads(raw) if raw else {'ok': True}
