from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
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

APP_PREVIEW_DIR = Path(__file__).resolve().parents[2] / 'app-preview'
if APP_PREVIEW_DIR.exists():
    app.mount('/app-preview', StaticFiles(directory=APP_PREVIEW_DIR, html=True), name='app-preview')


@app.get('/')
def root():
    return {
        'name': settings.app_name,
        'env': settings.app_env,
        'api': settings.api_v1_prefix,
        'preview': '/app-preview/' if APP_PREVIEW_DIR.exists() else None,
    }


@app.get('/app-preview', include_in_schema=False)
def app_preview_redirect():
    return RedirectResponse(url='/app-preview/')
