from app.schemas.simulation import SimulationStartRequest, SimulationStepRequest
from app.services.simulation_state import simulation_state


class SimulationService:
    def get_state(self, line: int):
        return simulation_state[line]

    def start(self, payload: SimulationStartRequest):
        state = simulation_state[payload.line]
        state.update({
            'running': True,
            'tph_input': payload.tph_input,
            'split_product_a_pct': payload.split_product_a_pct,
            'split_product_b_pct': payload.split_product_b_pct,
            'split_discard_pct': payload.split_discard_pct,
        })
        return state

    def stop(self, line: int):
        state = simulation_state[line]
        state['running'] = False
        return state

    def reset(self, line: int):
        state = simulation_state[line]
        state.update({
            'input_ton': 0.0,
            'product_a_ton': 0.0,
            'product_b_ton': 0.0,
            'discard_ton': 0.0,
            'running': False,
        })
        return state

    def step(self, payload: SimulationStepRequest):
        state = simulation_state[payload.line]
        hours = payload.seconds / 3600
        delta_input = state['tph_input'] * hours
        state['input_ton'] += delta_input
        state['product_a_ton'] += delta_input * (state['split_product_a_pct'] / 100)
        state['product_b_ton'] += delta_input * (state['split_product_b_pct'] / 100)
        state['discard_ton'] += delta_input * (state['split_discard_pct'] / 100)
        return state
