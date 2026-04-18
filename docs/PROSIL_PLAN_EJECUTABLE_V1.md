# Prosil - Plan Ejecutable v1 (enfocado)

## Objetivo
Pasar de MVP funcional a operación robusta de planta, sin dispersarnos.

## Norte técnico
1. Operación segura (auth, permisos, trazabilidad)
2. Continuidad operativa (modo degradado/manual)
3. Visibilidad en tiempo real + histórico útil
4. Confiabilidad de despliegue (backup, health, rollback)

---

## Bloque A - Crítico ahora (Sprint 1-2)

1. **Roles reales y permisos por endpoint** (operador/supervisor/admin)
2. **Rate limit en login** + bloqueo temporal por intentos
3. **Modo degradado operativo** (carga manual cuando falla PLC)
4. **Alarmas básicas con acknowledge** (thresholds por línea)
5. **Auditoría mínima** (login, apertura/cierre proceso, cambios críticos)
6. **Sesión de 12h por turno** (ya implementada, validar auto-logout UX)

**Criterio de salida Bloque A:**
- No hay operación crítica sin autenticación
- Si PLC cae, la operación puede continuar
- Alarmas visibles y registradas

---

## Bloque B - Estabilidad y operación (Sprint 3-4)

7. **Histórico de mediciones** con ventana útil (30 min / 24 h / 7 días)
8. **Dashboard operativo mejorado** (estado línea, alarmas, tendencia limpia)
9. **Handoff de turno** (nota obligatoria al cierre de turno)
10. **Backups automáticos de DB** + prueba de restore
11. **Health checks y monitoreo base** (API, DB, poller, latencia ingest)

**Criterio de salida Bloque B:**
- Datos históricos confiables
- Recuperación ante incidente validada
- Traspaso entre turnos trazable

---

## Bloque C - Profesionalización (Sprint 5-6)

12. **CI/CD básico** (lint + tests + deploy controlado)
13. **Logging estructurado JSON** (request id / proceso / línea)
14. **Reportes operativos** (producción por turno/línea)
15. **Documentación de operación** (runbook corto + troubleshooting real)

**Criterio de salida Bloque C:**
- Entregas más seguras y rápidas
- Diagnóstico de fallas más simple
- Reportería utilizable por supervisión

---

## Parking (no ahora)
- Microservicios
- IA/predicción
- Gemelo digital
- Multi-planta
- OPC UA avanzado

---

## Estado actual (hoy)
- ✅ Auth JWT + login real
- ✅ Endpoints protegidos
- ✅ Expiración token 12h
- ✅ UI enfocada en operación (sin modo simulación)
- ⏭️ Siguiente recomendado: **roles/permisos + rate limit + alarmas ack**

---

## Regla de ejecución
Trabajar por bloques cerrados:
- implementación
- validación funcional
- commit + push
- nota breve de qué quedó listo y qué falta
