from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging

setup_logging()
settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.app_debug)
allowed_origins = [o.strip() for o in settings.backend_cors_origins.split(',') if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get('/')
def root():
    return {
        'name': settings.app_name,
        'env': settings.app_env,
        'api': settings.api_v1_prefix,
    }
