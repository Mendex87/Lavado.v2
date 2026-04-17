# Simulation v0.1

Simulación inicial pensada para afinar la lógica operativa antes de conectar PLC real.

## Línea 1 - ejemplo base
- alimentación: `120 tn/h`
- reparto:
  - `70%` producto A
  - `20%` producto B
  - `10%` descarte

## Endpoints
- `GET /api/v1/simulation/line/{line}`
- `POST /api/v1/simulation/start`
- `POST /api/v1/simulation/step`
- `POST /api/v1/simulation/line/{line}/stop`
- `POST /api/v1/simulation/line/{line}/reset`

## Uso esperado
- iniciar simulación por línea
- avanzar en pasos controlados (ej. 60 segundos)
- observar acumulados de entrada y salidas
- ajustar splits y tph hasta que el comportamiento se parezca a planta

## Próximo paso
Conectar esta simulación al frontend real para test de operador/supervisor.
