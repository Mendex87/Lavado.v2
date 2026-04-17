from datetime import datetime
from app.models.process import ProcessInput
from app.models.stock import QuarryStockMovement
from app.repositories.events_repository import EventsRepository
from app.repositories.process_repository import ProcessRepository
from app.repositories.stock_repository import StockRepository
from app.schemas.simulation import SimulationStartRequest, SimulationStepRequest
from app.services.event_service import EventService
from app.services.simulation_state import simulation_state


class SimulationService:
    def __init__(self, db=None):
        self.db = db
        self.process_repository = ProcessRepository(db) if db else None
        self.stock_repository = StockRepository(db) if db else None
        self.event_service = EventService(EventsRepository(db)) if db else None

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
        if self.event_service and self.process_repository:
            process = self.process_repository.get_active_by_line(payload.line)
            self.event_service.register(
                process.id if process else None,
                event_type='simulation_started',
                severity='info',
                message=f'Simulación iniciada en línea {payload.line}',
                payload=state,
            )
            self.db.commit()
        return state

    def stop(self, line: int):
        state = simulation_state[line]
        state['running'] = False
        if self.event_service and self.process_repository:
            process = self.process_repository.get_active_by_line(line)
            self.event_service.register(
                process.id if process else None,
                event_type='simulation_stopped',
                severity='info',
                message=f'Simulación pausada en línea {line}',
            )
            self.db.commit()
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
        if self.event_service and self.process_repository:
            process = self.process_repository.get_active_by_line(line)
            self.event_service.register(
                process.id if process else None,
                event_type='simulation_reset',
                severity='warning',
                message=f'Simulación reseteada en línea {line}',
            )
            self.db.commit()
        return state

    def step(self, payload: SimulationStepRequest):
        state = simulation_state[payload.line]
        hours = payload.seconds / 3600
        delta_input = state['tph_input'] * hours
        state['input_ton'] += delta_input
        state['product_a_ton'] += delta_input * (state['split_product_a_pct'] / 100)
        state['product_b_ton'] += delta_input * (state['split_product_b_pct'] / 100)
        state['discard_ton'] += delta_input * (state['split_discard_pct'] / 100)

        if self.db and self.process_repository and self.stock_repository and self.event_service:
            self._apply_process_effects(payload.line, delta_input)
        return state

    def _apply_process_effects(self, line: int, delta_input: float):
        process = self.process_repository.get_active_by_line(line)
        if not process:
            self.event_service.register(
                None,
                event_type='simulation_without_process',
                severity='warning',
                message=f'Avance de simulación en línea {line} sin proceso activo',
                payload={'line': line, 'delta_input': delta_input},
            )
            self.db.commit()
            return

        inputs = list(self.db.query(ProcessInput).filter(ProcessInput.process_id == process.id).order_by(ProcessInput.input_order.asc()).all())
        if not inputs:
            self.event_service.register(
                process.id,
                event_type='simulation_without_inputs',
                severity='warning',
                message=f'Proceso {process.code} sin entradas configuradas para descontar stock',
                payload={'delta_input': delta_input},
            )
            self.db.commit()
            return

        total_target = sum(float(i.blend_target_pct or 0) for i in inputs)
        if total_target <= 0:
            total_target = 100.0 if len(inputs) == 1 else float(len(inputs))

        for item in inputs:
            ratio = (float(item.blend_target_pct or 100.0) / total_target) if len(inputs) > 1 or item.blend_target_pct is not None else 1.0
            consumed = delta_input * ratio
            stock = self.stock_repository.get_stock_by_quarry_id(item.quarry_id)
            if stock:
                stock.current_ton = max(0.0, float(stock.current_ton) - consumed)
                self.db.add(stock)
            self.stock_repository.add_movement(QuarryStockMovement(
                quarry_id=item.quarry_id,
                process_id=process.id,
                scale_id=None,
                movement_type='simulation_consumption',
                direction='out',
                quantity_ton=consumed,
                signed_quantity_ton=-consumed,
                source='simulation',
                reference_code=process.code,
                entered_by_user_id=1,
                reason=f'Consumo simulado línea {line}',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ))

        self.event_service.register(
            process.id,
            event_type='simulation_step',
            severity='info',
            message=f'Simulación aplicada en {process.code}, +{delta_input:.3f} tn entrada',
            payload={'line': line, 'delta_input': delta_input},
        )
        self.db.commit()
