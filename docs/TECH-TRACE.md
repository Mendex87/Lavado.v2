# Technical Trace

Bitácora técnica para reconstruir decisiones, fallas, debugging y cambios de implementación.

## Regla
Cada vez que aparezca una falla, ajuste delicado o cambio estructural importante, registrar:
- fecha
- componente
- síntoma
- causa sospechada o confirmada
- acción tomada
- resultado
- commit asociado si existe

## Estado inicial
- Proyecto en fase de definición + backend base + preview operativa temprana.
- Backend ya migrando desde mocks hacia servicios/repositorios reales.
- Preview remota útil para validar flujo, pero no es todavía la app final.

## 2026-04-22

### Componente
- Frontend + Backend + PLC Poller + SQLite

### Síntoma
- UI lenta en apertura/cierre de procesos.
- Procesos activos mostraban valores simulados (120/80 tn/h).
- Stock no se descontaba con lecturas PLC.

### Causa confirmada
- Polling muy agresivo + escritura concurrente en SQLite sin ajustes de concurrencia.
- Tarjeta de procesos usaba `state.simulation` en lugar de medición real.
- Descuento de stock dependía de `totalizer_ton` y en planta el totalizador estaba fijo; el valor que avanzaba era `partial_ton`.

### Acción tomada
- Estandarización de intervalos a 500ms (frontend `core/flow` + poller).
- Optimización SQLite: `WAL`, `busy_timeout`, `synchronous=NORMAL`, `timeout` de conexión.
- Procesos activos ahora usan caudales y parciales reales (`latestMeasurements/liveFlow`).
- Descuento automático de stock con fallback a delta de `partial_ton` cuando `totalizer_ton` no avanza.
- Carga crítica al login para render inmediato del estado de procesos.

### Resultado esperado
- Mayor fluidez general de UI y menor bloqueo por escritura simultánea.
- Datos de procesos consistentes con PLC.
- Stock consumiéndose en línea con alimentación real.
