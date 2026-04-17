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
- Corrección funcional posterior: la simulación ahora soporta un proceso activo por línea, evita abrir un segundo proceso sobre una línea ocupada, desactiva blend en Línea 1 y oculta opciones no válidas según línea/modo.

### [BACKEND v0.1]
- Se creó `backend/` como scaffold real del backend.
- Stack inicial elegido: FastAPI + SQLAlchemy 2 + PostgreSQL + Alembic.
- Se agregaron archivos base:
  - `backend/app/main.py`
  - `backend/app/core/config.py`
  - `backend/app/db/session.py`
  - `backend/app/api/router.py`
  - rutas iniciales de `health`, `processes`, `stock`
  - schemas Pydantic y estado mock inicial
  - `backend/requirements.txt`
  - `backend/.env.example`
  - `backend/README.md`
  - `docs/backend_v0_1.md`
- Decisión práctica: arrancar con backend ejecutable y mocks internos para luego reemplazar capa por DB real y conexión PLC, en vez de seguir solo con especificaciones.
- Avance posterior:
  - se agregaron modelos ORM base alineados al schema `DB-SCHEMA v1.1`
  - se cubrieron catálogos, usuarios, procesos, stock, PLC, eventos, alarmas y auditoría
  - se agregó `backend/app/db/init_db.py` para inicialización rápida en desarrollo
  - se preparó Alembic base para migraciones
  - se agregó primera migración inicial mínima (`roles`, `users`)
  - se incorporaron repositorios y servicios iniciales para `processes` y `stock`
  - las rutas de procesos y stock dejaron de depender directamente del mock central
  - se agregó contrato PLC simulado en backend (`variables`, `context`, `publish-context`, `reset-partials`)
  - se agregó `admin/seed` para poblar catálogos mínimos de desarrollo
  - se agregó capa de simulación productiva por línea con TPH y splits configurables para testear comportamiento de planta antes de conectar PLC real
  - se dejó backend ejecutable en modo desarrollo con SQLite local para pruebas rápidas sin depender todavía de PostgreSQL levantado

### [RESEARCH 2026-04-17]
- Se revisaron referencias externas de UX y arquitectura MES/industrial.
- Documento generado: `docs/research_2026-04-17_mes_ui_backend.md`
- Hallazgos clave incorporados:
  - separar dashboards operativos en tiempo real vs análisis histórico
  - diseñar por rol y acción, no por volumen de datos
  - mantener la capa MES/app entre ERP/planificación y PLC/SCADA
  - tratar alertas, evidencia, calidad y trazabilidad como entidades centrales

### [TRACEABILITY 2026-04-17]
- Se creó `docs/TECH-TRACE.md` como bitácora técnica específica para fallas, debugging y cambios delicados.
- Se agregó `backend/.gitignore` para evitar ensuciar el repo con cachés, entornos y secretos locales.
- Se agregó `backend/app/core/logging.py` y se activó logging base en `backend/app/main.py`.
- Decisión práctica: desde ahora cualquier falla significativa de preview, backend, migraciones o integración PLC debe dejar rastro técnico en `TECH-TRACE.md`, además del resumen general en `PROJECT-LOG.md`.

### [GITHUB PREP 2026-04-17]
- Se creó `.gitignore` en raíz para separar código del proyecto vs archivos personales/operativos del workspace OpenClaw.
- Se creó `docs/github_publishing.md` con guía concreta para publicar el repo y seguir desde otra PC.
- Se creó `docs/repo_scope.md` para dejar explícito qué entra y qué no entra al repo compartido.
- Decisión práctica: el repo GitHub será la fuente central del código; VPS para demo/continuidad, PC del taller para desarrollo y pruebas reales con PLC.

## Convención de versionado
- Mientras estemos definiendo arquitectura y datos, versionamos por componente.
- Formato inicial: `DB-SCHEMA vX.Y`.
- Cuando arranquemos la app en sí, se incorporará una versión global de proyecto/app y se registrará aquí en cada cambio.
