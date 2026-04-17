# Backend

Base backend para la app industrial de planta.

## Stack inicial
- FastAPI
- SQLAlchemy 2
- PostgreSQL
- Alembic

## Ejecutar
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Variables de entorno
Copiar `.env.example` a `.env` y ajustar valores.
