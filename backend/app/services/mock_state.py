from datetime import datetime

mock_state = {
    'processes': [
        {
            'code': 'PR-2026-00019',
            'line': 1,
            'mode': 'simple',
            'status': 'active',
            'operator': 'Juan',
            'started_at': datetime(2026, 4, 17, 8, 10),
        },
        {
            'code': 'PR-2026-00021',
            'line': 2,
            'mode': 'blend',
            'status': 'active',
            'operator': 'Diego',
            'started_at': datetime(2026, 4, 17, 9, 31),
        },
    ],
    'stock': [
        {'quarry': 'Río Negro', 'tons': 420.0, 'status': 'normal', 'last_movement': 'Consumo proceso PR-2026-00019'},
        {'quarry': 'Dolavon', 'tons': 75.0, 'status': 'low', 'last_movement': 'Ajuste manual AJ-2026-0003'},
        {'quarry': 'Trelew Norte', 'tons': 190.0, 'status': 'normal', 'last_movement': 'Ingreso camión ING-2026-0021'},
    ],
}
