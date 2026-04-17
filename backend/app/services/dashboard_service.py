from app.repositories.events_repository import EventsRepository
from app.repositories.process_repository import ProcessRepository
from app.repositories.stock_repository import StockRepository
from app.schemas.dashboard import (
    DashboardActiveProcessItem,
    DashboardOverview,
    DashboardRecentEventItem,
    DashboardSimulationItem,
    DashboardStockAlertItem,
)
from app.services.simulation_state import simulation_state
from app.services.stock_service import StockService


class DashboardService:
    def __init__(self, db):
        self.db = db
        self.process_repository = ProcessRepository(db)
        self.stock_repository = StockRepository(db)
        self.events_repository = EventsRepository(db)

    def get_overview(self) -> DashboardOverview:
        processes = self.process_repository.list_active()
        stock_items = StockService(self.stock_repository).list_quarry_stock()
        events = self.events_repository.list_recent(limit=10)

        process_by_id = {process.id: process for process in processes}
        active_processes = [
            DashboardActiveProcessItem(
                code=process.code,
                line=process.line_id,
                mode=process.mode,
                status=process.status,
                operator='Operador',
                started_at=process.started_at,
            )
            for process in processes
        ]

        simulations = [
            DashboardSimulationItem(
                line=line,
                running=bool(state['running']),
                tph_input=float(state['tph_input']),
                input_ton=float(state['input_ton']),
                product_a_ton=float(state['product_a_ton']),
                product_b_ton=float(state['product_b_ton']),
                discard_ton=float(state['discard_ton']),
            )
            for line, state in sorted(simulation_state.items())
        ]

        stock_alerts = [
            DashboardStockAlertItem(**item)
            for item in stock_items
            if item['status'] in {'low', 'critical'}
        ]

        recent_events = []
        for event in events:
            process = process_by_id.get(event.process_id) if event.process_id else None
            if not process and event.process_id:
                process = self.process_repository.get_by_id(event.process_id)
            recent_events.append(
                DashboardRecentEventItem(
                    event_type=event.event_type,
                    severity=event.severity,
                    message=event.message,
                    process_code=process.code if process else None,
                    created_at=event.created_at,
                )
            )

        return DashboardOverview(
            active_processes_count=len(active_processes),
            running_simulations_count=sum(1 for item in simulations if item.running),
            stock_critical_count=sum(1 for item in stock_items if item['status'] == 'critical'),
            stock_low_count=sum(1 for item in stock_items if item['status'] == 'low'),
            active_processes=active_processes,
            simulations=simulations,
            stock_alerts=stock_alerts,
            recent_events=recent_events,
        )
