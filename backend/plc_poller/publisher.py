from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode('utf-8')
    req = request.Request(
        url,
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with request.urlopen(req, timeout=15) as response:
            raw = response.read().decode('utf-8')
            return json.loads(raw) if raw else {'ok': True}
    except HTTPError as exc:
        detail = ''
        try:
            detail = exc.read().decode('utf-8')
        except Exception:
            detail = ''
        raise RuntimeError(f'HTTP {exc.code} en {url}: {detail or exc.reason}') from exc
