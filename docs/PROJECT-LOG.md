# Project Log - Prosil Lavado MES App

## v3.2.1 (2026-04-23) - Release Actual

### Frontend Fixes:
- `updateFlowDisplay()` corregido para evitar NaN cuando ambos flow L2 son null
- Verificación de null antes de sumar flows en L2 blend
- Logging de timing (>30ms) en refreshFlowData

### Backend Optimización:
- Nuevo método `get_latest_by_codes_optimized()` en repository
- `list_latest()` ahora hace UNA sola query cuando se pasan códigos (antes hacía 2)
- Esto acelera significativamente el refresh de flow

### Estado operativo:
- Flow refresh: 100ms
- Core refresh: 2000ms  
- IDs específicos para actualización directa

---

## v3.2 (2026-04-19) - Release Anterior

### Módulos Nuevos:
- **Calidad**: quality_records, quality_specifications, lot_traceability
- **Mantenimiento**: maintenance_requests, maintenance_incidents, preventive_tasks
- **OEE**: Dashboard con disponibilidad/rendimiento/calidad
- **Reporting**: daily_reports, exportación
- **Energía**: energy_readings

### Mejoras Técnicas:
- PLC poller: reload dinámico desde app (sin reiniciar)
- Test conexión PLC real (no simulado)
- Refresh estandarizado en 500ms (frontend + poller)
- Endpoint público /settings/plc-config
- Botón "Aplicar configuración"
- Logging en frontend (console.log)
- Optimización SQLite para concurrencia (`WAL`, `busy_timeout`, `synchronous=NORMAL`)
- Apertura/cierre de proceso más rápido (menos roundtrips y commits duplicados eliminados)
- Descuento de stock por PLC con fallback a delta de parcial cuando totalizador queda fijo

### Frontend:
- Versión: v3.2
- Nuevas pantallas: Calidad, Mantenimiento, OEE, Reportes, Energía
- Procesos activos muestra valores reales (ya no usa 120/80 simulados)
- Carga crítica al login para mostrar estado de procesos de inmediato
- Optimizado refresh: menos requests, logging de timing

### Estado operativo actual:
- Poller y frontend actualizan cada 500ms
- Stock se descuenta automáticamente desde lecturas de alimentación
- Indicador PLC online/offline visible en UI

---

## v3.1 (2026-04-18)
- Stock con alertas configurables
- Dashboard mejorado con fecha/hora
- Handover de turno
- Mediciones manuales con notas
- Configuración avanzada

---

## v3.0 (2026-04-17)
- Ingreso manual de stock
- Contingencia manual

---

## v2.0-v2.9 (2026-04-17)
- Autenticación JWT con roles
- Rate limiting
- Alarmas básicas
- Auditoría
- Session 12h

---

## v1.0-v1.9 (2026-04-17)
- Eschema DB PostgreSQL
- API FastAPI
- UI Preview
- PLC poller
- Simulación
