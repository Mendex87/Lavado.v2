# Run backend locally

## Desarrollo rápido
Desde `backend/`:

```bash
python3 -m pip install --break-system-packages --user -r requirements.txt
cp .env.example .env
python3 -m app.db.init_db
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

## Base por defecto
En desarrollo queda usando SQLite local:
- `DATABASE_URL=sqlite+pysqlite:///./plant_app.db`

Luego se puede volver a PostgreSQL cambiando `DATABASE_URL` o las variables `POSTGRES_*`.

## Endpoints útiles para prueba
- `GET /api/v1/health`
- `POST /api/v1/admin/seed`
- `GET /api/v1/processes/active`
- `GET /api/v1/stock/quarries`
- `GET /api/v1/dashboard/overview`
- `GET /api/v1/plc/variables`
- `GET /api/v1/plc/context`
- `GET /api/v1/plc/line/1/contract`
- `POST /api/v1/plc/publish-context`
- `POST /api/v1/plc/reset-partials`
- `GET /api/v1/measurements/points`
- `POST /api/v1/measurements/ingest`
- `GET /api/v1/simulation/line/1`
- `POST /api/v1/simulation/start`
- `POST /api/v1/simulation/step`

## Proceso Python separado para PLC
Base inicial en `backend/plc_poller/`.

Ejecutar placeholder:

```bash
cd backend
python3 -m plc_poller.main
```

## Ejemplo de simulación línea 1
Payload inicial sugerido:

```json
{
  "line": 1,
  "tph_input": 120,
  "split_product_a_pct": 70,
  "split_product_b_pct": 20,
  "split_discard_pct": 10
}
```
