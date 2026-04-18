from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, require_roles
from app.api.routes import admin, alarms, audit, auth, dashboard, events, health, measurements, plc, processes, simulation, stock

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(processes.router, dependencies=[Depends(get_current_user)])
api_router.include_router(stock.router, dependencies=[Depends(get_current_user)])
api_router.include_router(events.router, dependencies=[Depends(get_current_user)])
api_router.include_router(alarms.router, dependencies=[Depends(get_current_user)])
api_router.include_router(audit.router, dependencies=[Depends(get_current_user)])
api_router.include_router(
    plc.router,
    dependencies=[Depends(get_current_user), Depends(require_roles('supervisor', 'admin'))],
)
api_router.include_router(
    simulation.router,
    dependencies=[Depends(get_current_user), Depends(require_roles('supervisor', 'admin'))],
)
api_router.include_router(dashboard.router, dependencies=[Depends(get_current_user)])
api_router.include_router(
    admin.router,
    dependencies=[Depends(get_current_user), Depends(require_roles('admin'))],
)
api_router.include_router(measurements.router)
