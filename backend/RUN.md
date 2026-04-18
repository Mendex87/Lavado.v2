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
- `GET /`
- `GET /app-preview/`
- `GET /api/v1/health`
- `POST /api/v1/auth/login` (dev seed: `eze` / `change-me`)
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

## Autenticación JWT

- Todos los endpoints operativos requieren `Authorization: Bearer <token>`.
- Excepciones públicas: `GET /api/v1/health`, `POST /api/v1/auth/login`, `POST /api/v1/measurements/ingest`.
- Expiración de token por defecto: `720` minutos (12 horas, un turno).
- Configurar `SECRET_KEY` fuerte en `.env` para producción.

### Roles por defecto (seed)

- `admin` => rol `admin`
- `eze` => rol `supervisor`
- `diego`, `juan` => rol `operador`

### Restricción de endpoints por rol

- `admin/*`: solo `admin`
- `plc/*`, `simulation/*`: `supervisor` o `admin`
- resto de endpoints operativos: cualquier usuario autenticado

## Preview incluida en el backend
Con el backend levantado, la UI preview queda servida desde el mismo proceso:

- `http://localhost:8010/app-preview/`

Eso evita depender de un server estático aparte y simplifica la prueba remota detrás de una sola URL.
La preview además autodetecta la base API desde la URL actual y guarda overrides en `localStorage`, así que al abrirla remotamente no queda apuntando a `localhost` por error.

## Proceso Python separado para PLC
Base inicial en `backend/plc_poller/`.

Ejecutar base del poller:

```bash
cd backend
python3 -m plc_poller.main
```

Primera prueba real ya aterrizada en `backend/plc_poller/mapping.example.json` con:
- `DB13` para parciales
- `DB2` para totalizadores
- una sola balanza inicial (`l1_input_main`)

Si los offsets en TIA difieren, ajustar bytes en ese archivo.

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
