from fastapi import APIRouter
from app.api.routes import health, processes, stock

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(processes.router)
api_router.include_router(stock.router)
