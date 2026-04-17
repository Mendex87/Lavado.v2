# Backend v0.1

Estado: scaffold ejecutable

## Objetivo
Dejar una base real de backend para empezar a reemplazar mocks por datos de base y PLC.

## Incluye
- FastAPI como framework
- configuración centralizada por `.env`
- router principal `/api/v1`
- endpoints iniciales:
  - `GET /api/v1/health`
  - `GET /api/v1/processes/active`
  - `POST /api/v1/processes`
  - `POST /api/v1/processes/{code}/close`
  - `GET /api/v1/stock/quarries`
- estado mock interno para pruebas tempranas

## Avance adicional
- Se agregaron modelos ORM base para:
  - catálogos y usuarios
  - procesos
  - stock
  - PLC / totalizadores
  - eventos, alarmas y auditoría
- Se agregó `backend/app/db/init_db.py` para inicialización rápida de metadata en entorno de desarrollo.
- Se preparó Alembic con:
  - `backend/alembic.ini`
  - `backend/alembic/env.py`
  - `backend/alembic/versions/20260417_0001_initial_models.py`
- Se agregaron repositorios y servicios iniciales para procesos y stock.
- Las rutas `processes` y `stock` ya dejaron de leer directo del mock central y ahora pasan por servicios/repositorios.
- Se agregaron rutas y servicios iniciales para contrato PLC simulado:
  - `GET /api/v1/plc/variables`
  - `GET /api/v1/plc/context`
  - `POST /api/v1/plc/publish-context`
  - `POST /api/v1/plc/reset-partials`
- Se agregó `POST /api/v1/admin/seed` para sembrado mínimo de catálogos base en desarrollo.
- Se agregó capa inicial de simulación operativa:
  - `GET /api/v1/simulation/line/{line}`
  - `POST /api/v1/simulation/start`
  - `POST /api/v1/simulation/step`
  - `POST /api/v1/simulation/line/{line}/stop`
  - `POST /api/v1/simulation/line/{line}/reset`

## Ejecución rápida en desarrollo
- se habilitó modo de desarrollo simple usando `SQLite` local cuando no se define `DATABASE_URL`
- esto permite levantar backend y probar endpoints sin depender todavía de PostgreSQL
- los tipos JSON quedaron compatibles con SQLite en desarrollo y con JSONB en PostgreSQL
- se habilitó CORS configurable (`BACKEND_CORS_ORIGINS`) para permitir que la preview/app de prueba consuma la API desde otro origen durante desarrollo

## Avance adicional
- la simulación ya se vincula con el proceso activo de la línea cuando existe
- cada paso de simulación puede generar eventos persistidos en backend
- si el proceso tiene entradas configuradas, la simulación descuenta stock y deja movimiento asociado
- se agregó `GET /api/v1/events/recent` para alimentar la UI con eventos reales

## Próximos pasos recomendados
1. persistir resúmenes de producción y lecturas por balanza en cada step relevante
2. ampliar migración inicial hasta cubrir schema real relevante
3. alinear tipos/campos ORM con restricciones faltantes del schema SQL
4. endurecer seed inicial y valores por defecto
5. autenticación JWT
6. enriquecer relación stock/eventos con más detalle operativo
7. capa de integración PLC real (snap7/opc/modbus según estrategia)
