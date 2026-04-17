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

## Próximos pasos recomendados
1. alinear tipos/campos ORM con schema SQL final y restricciones faltantes
2. agregar Alembic
3. migrar rutas mock a servicios con sesión DB real
4. autenticación JWT
5. capa de integración PLC
6. reemplazar estado mock por repositorios y casos de uso
