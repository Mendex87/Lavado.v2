# Project Log

Registro paso a paso de decisiones, cambios y entregables del proyecto.

## 2026-04-17

### [DB-SCHEMA v1.0]
- Se creó `db/schema_v1.sql` como primera versión del esquema relacional base en PostgreSQL.
- Alcance inicial: usuarios, turnos, líneas, canteras, productos, procesos, entradas/salidas de proceso, balanzas, lecturas, stock, PLC, eventos, alarmas y soporte futuro para humedad/rendimiento.

### [DB-SCHEMA v1.1]
- Se revisó funcionalmente el esquema contra la operación real de planta.
- Se creó `db/schema_v1_1.sql` con las siguientes mejoras aplicadas:
  1. `users` se desacopla de un único rol fijo y se agrega `user_roles` para soporte multi-rol.
  2. Se agrega `user_sessions` para trazabilidad de login/logout por operador.
  3. `processes` ahora guarda snapshot completo del turno (`code`, `name`, `start_time`, `end_time`).
  4. `processes` agrega `closed_by_user_id`, `close_reason` y `cancel_reason`.
  5. Se agrega índice único parcial para impedir más de un proceso activo por línea.
  6. `process_outputs` agrega `humidity_source`.
  7. `process_production` se reemplaza por `process_production_summary` para distinguir resumen consolidado de las lecturas históricas.
  8. `quarry_stock_movements` agrega `direction`, `signed_quantity_ton`, `source` y `reference_code`.
  9. `plc_variables` agrega `store_history` y `history_policy` para controlar qué variables vale la pena historizar.
  10. Se mantiene soporte futuro para sensores de humedad y snapshots de rendimiento por cantera.
- Decisión operativa asociada: desde ahora todo cambio estructural importante se registra en este archivo.

### [API v0.1]
- Se creó `docs/api_v0_1.md` como contrato base inicial del backend.
- Se definieron endpoints para:
  - autenticación y sesión de operador
  - catálogos principales
  - apertura/cierre/cancelación de procesos
  - sincronización de lecturas y totalizadores
  - stock y consumo por proceso
  - integración PLC y reset de parciales
  - eventos, alarmas, humedad y rendimiento
  - dashboard operativo resumido
- Decisión de diseño: la API se organiza alrededor del `proceso`, no alrededor de CRUDs sueltos.

### [UI v0.1]
- Se creó `docs/ui_v0_1.md` como estructura funcional inicial de pantallas.
- Se definieron las vistas principales:
  - login
  - dashboard
  - abrir proceso guiado
  - proceso activo
  - cerrar proceso
  - producción
  - stock
  - canteras
  - alarmas y eventos
  - PLC/diagnóstico
  - configuración
- Decisión de diseño: UI guiada para operador, con acciones críticas visibles y confirmadas, y sin formularios gigantes.

### [APP-PREVIEW v0.1]
- Se creó una primera vista previa navegable en `app-preview/`.
- Pantallas incluidas en esta primera iteración:
  - dashboard operativo
  - abrir proceso guiado
  - proceso activo
  - stock de canteras
- Stack usado para la preview: HTML + CSS + JS plano, priorizando velocidad de validación.
- Objetivo de esta preview: validar estructura operativa y jerarquía visual antes de pasar a implementación real de app.
- Ajuste posterior: se agregó `<base href="/app-preview/">` en `app-preview/index.html` para que CSS y JS carguen correctamente al servir la preview detrás de una subruta de Tailscale Serve.
- Mejora posterior: la preview pasó de estática a interactiva con estado mock en `app-preview/app.js`, permitiendo simular apertura de proceso, avance de producción, ajuste de stock, registro de eventos y cierre de proceso.
- Ajuste adicional: se agregaron query strings de versión en `index.html` para forzar recarga real de `app.js` y `styles.css` y evitar que el navegador siguiera usando una copia cacheada de la preview estática.
- Se agregó una prueba visible de ejecución JavaScript en la UI (`debug-banner`) para verificar sin ambigüedad si la preview está cargando el JS correcto o si sigue sirviendo archivos viejos/cacheados.

## Convención de versionado
- Mientras estemos definiendo arquitectura y datos, versionamos por componente.
- Formato inicial: `DB-SCHEMA vX.Y`.
- Cuando arranquemos la app en sí, se incorporará una versión global de proyecto/app y se registrará aquí en cada cambio.
