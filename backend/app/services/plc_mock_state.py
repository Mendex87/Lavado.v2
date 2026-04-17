plc_mock_state = {
    'context': {
        'process_enabled': False,
        'line': None,
        'mode': None,
        'blend_target_a_pct': None,
        'blend_target_b_pct': None,
        'reset_partials_requested': False,
    },
    'variables': [
        {'code': 'process_enabled', 'name': 'Proceso habilitado', 'direction': 'app_to_plc', 'data_type': 'bool', 'is_active': True},
        {'code': 'line_active', 'name': 'Línea activa', 'direction': 'app_to_plc', 'data_type': 'int', 'is_active': True},
        {'code': 'mode_blend', 'name': 'Modo blend', 'direction': 'app_to_plc', 'data_type': 'bool', 'is_active': True},
        {'code': 'l1_entry_partial_ton', 'name': 'Parcial entrada línea 1', 'direction': 'plc_to_app', 'data_type': 'real', 'is_active': True},
        {'code': 'l2_tolva_a_partial_ton', 'name': 'Parcial tolva A línea 2', 'direction': 'plc_to_app', 'data_type': 'real', 'is_active': True},
        {'code': 'l2_tolva_b_real_partial_ton', 'name': 'Parcial tolva B real línea 2', 'direction': 'plc_to_app', 'data_type': 'real', 'is_active': True},
    ],
}
