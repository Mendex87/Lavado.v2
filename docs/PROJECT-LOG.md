# Project Log - Prosil Lavado MES App

## v3.2 (2026-04-19) - Release Actual

### Módulos Nuevos:
- **Calidad**: quality_records, quality_specifications, lot_traceability
- **Mantenimiento**: maintenance_requests, maintenance_incidents, preventive_tasks
- **OEE**: Dashboard con disponibilidad/rendimiento/calidad
- **Reporting**: daily_reports, exportación
- **Energía**: energy_readings

### Mejoras Técnicas:
- PLC poller: reload dinámico desde app (sin reiniciar)
- Test conexión PLC real (no simulado)
- Refresh уніфікованний: 100ms todo
- Endpoint público /settings/plc-config
- Botón "Aplicar configuración"
- Logging en frontend (console.log)

### Frontend:
- Versión: v3.2
- Nuevas pantallas: Calidad, Mantenimiento, OEE, Reportes, Energía
- Optimizado refresh: menos requests, logging de timing

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