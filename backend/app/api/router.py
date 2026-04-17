from fastapi import APIRouter
from app.api.routes import admin, dashboard, events, health, measurements, plc, processes, simulation, stock

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(processes.router)
api_router.include_router(stock.router)
api_router.include_router(events.router)
api_router.include_router(plc.router)
api_router.include_router(simulation.router)
api_router.include_router(measurements.router)
api_router.include_router(dashboard.router)
api_router.include_router(admin.router)
