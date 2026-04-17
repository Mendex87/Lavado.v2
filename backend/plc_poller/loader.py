from __future__ import annotations

import json
from pathlib import Path


def load_mapping(path: str | Path) -> dict:
    resolved = Path(path)
    with resolved.open('r', encoding='utf-8') as f:
        return json.load(f)
