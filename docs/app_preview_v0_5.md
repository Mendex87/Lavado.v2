# App Preview v0.5

Preview simplificada y conectada al backend real de simulación.

## Objetivo
Permitir pruebas rápidas desde PC o remoto para afinar:
- TPH de entrada
- splits de producto A / producto B / descarte
- avance controlado por pasos de tiempo
- lectura visual de acumulados por línea

## Comportamiento
- la UI prueba conexión con backend
- permite elegir línea
- permite activar simulación
- permite avanzar la simulación por segundos definidos
- permite refrescar estado y resetear la línea
- muestra bitácora visible de acciones

## Configuración de API
Campo editable `API base URL`.

Ejemplos:
- mismo host con proxy: `/api/v1`
- backend local en PC: `http://localhost:8010/api/v1`
- backend remoto explícito: `https://host/api/v1`

## Requisito técnico agregado
Se habilitó CORS en backend para que la preview pueda hablar con la API aun si corre desde otro puerto/origen en desarrollo.
