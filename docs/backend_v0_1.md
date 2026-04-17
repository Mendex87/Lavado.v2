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

## Próximos pasos recomendados
1. ampliar migración inicial hasta cubrir schema real relevante
2. alinear tipos/campos ORM con restricciones faltantes del schema SQL
3. seed inicial de catálogos mínimos
4. autenticación JWT
5. capa de integración PLC
6. reemplazar el resto de los mocks por casos de uso con DB real
