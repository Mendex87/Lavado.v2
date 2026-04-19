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
        """Prueba de conexión con el PLC usando la config真实的"""
        from app.models.settings import AppSetting
        from app.db.session import get_db
        import time
        
        # Obtener config del PLC
        db_gen = get_db()
        db = next(db_gen)
        try:
            rows = db.query(AppSetting).filter(AppSetting.key.in_(['plc_host', 'plc_rack', 'plc_slot'])).all()
            config = {r.key: r.value for r in rows}
        finally:
            db.close()
        
        plc_host = config.get('plc_host', '192.168.10.77')
        plc_rack = int(config.get('plc_rack', 0))
        plc_slot = int(config.get('plc_slot', 1))
        
        # Intentar conexión real
        start = time.time()
        try:
            from plc_poller.client import Snap7PlcClient
            client = Snap7PlcClient(plc_host, plc_rack, plc_slot)
            client.connect()
            elapsed = (time.time() - start) * 1000
            client.close()
            self.is_connected = True
            self.last_communication = datetime.utcnow()
            return {
                'success': True,
                'connected': True,
                'response_time_ms': round(elapsed, 1),
                'message': f'Conexión exitosa a {plc_host}',
                'timestamp': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            self.is_connected = False
            elapsed = (time.time() - start) * 1000
            return {
                'success': False,
                'connected': False,
                'response_time_ms': round(elapsed, 1),
                'message': f'Error conectando a {plc_host}: {str(e)}',
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
