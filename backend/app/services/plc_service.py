from datetime import datetime
from app.schemas.plc import PlcContextPublishRequest, PlcPartialResetRequest
from app.services.plc_mock_state import plc_mock_state


class PlcService:
    def __init__(self):
        self.last_communication = datetime.utcnow()
        self.is_connected = True  # Por ahora simulado
    
    def list_variables(self):
        return plc_mock_state['variables']

    def get_context(self):
        return plc_mock_state['context']
    
    def get_status(self):
        """Retorna el estado de conexión con el PLC"""
        variables_count = len(plc_mock_state.get('variables', []))
        active_vars = [v for v in variables_count if v.get('is_active', True)]
        
        return {
            'connected': self.is_connected,
            'last_communication': self.last_communication.isoformat() if self.last_communication else None,
            'variables_count': variables_count,
            'active_variables_count': len(active_vars),
            'plc_host': '192.168.1.100',  # Obtener de settings
            'plc_rack': '0',
            'plc_slot': '1',
        }
    
    def test_connection(self):
        """Prueba de conexión con el PLC"""
        # Por ahora retorna éxito simulado
        # En producción, aquí iría la lógica real de conexión al PLC
        self.is_connected = True
        self.last_communication = datetime.utcnow()
        
        return {
            'success': True,
            'connected': True,
            'response_time_ms': 45,
            'message': 'Conexión exitosa con PLC',
            'timestamp': datetime.utcnow().isoformat(),
        }

    def publish_context(self, payload: PlcContextPublishRequest):
        plc_mock_state['context'] = {
            'process_enabled': payload.process_enabled,
            'line': payload.line,
            'mode': payload.mode,
            'blend_target_a_pct': payload.blend_target_a_pct,
            'blend_target_b_pct': payload.blend_target_b_pct,
            'reset_partials_requested': False,
        }
        return plc_mock_state['context']

    def request_partial_reset(self, payload: PlcPartialResetRequest):
        if not payload.confirmed:
            raise ValueError('El reset requiere confirmación explícita')
        plc_mock_state['context']['reset_partials_requested'] = True
        return plc_mock_state['context']
