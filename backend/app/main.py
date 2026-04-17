from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging

setup_logging()
settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.app_debug)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get('/')
def root():
    return {
        'name': settings.app_name,
        'env': settings.app_env,
        'api': settings.api_v1_prefix,
    }
