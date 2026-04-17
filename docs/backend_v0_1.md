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

## Próximos pasos recomendados
1. conectar SQLAlchemy al schema real
2. crear modelos ORM base
3. agregar Alembic
4. autenticación JWT
5. capa de integración PLC
6. reemplazar estado mock por servicios + repositorios
