from app.schemas.plc import PlcContextPublishRequest, PlcPartialResetRequest
from app.services.plc_mock_state import plc_mock_state


class PlcService:
    def list_variables(self):
        return plc_mock_state['variables']

    def get_context(self):
        return plc_mock_state['context']

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
