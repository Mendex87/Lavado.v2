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
  - se rehizo la preview v0.5 para conectarla al backend real de simulación, con controles para activar, avanzar, refrescar y resetear por línea
  - se habilitó CORS en backend para permitir pruebas de preview desde otro origen/puerto en desarrollo
  - se unificó la preview en v0.6, recuperando gestión de planta (dashboard, alta de proceso, proceso activo, stock, eventos) y dejando simulación en una pestaña separada
  - se agregó auto simulación cada 1 segundo para no depender de avance manual por click
  - se conectó la simulación al proceso activo de la línea: ahora genera eventos backend y descuenta stock cuando el proceso tiene entradas configuradas
  - se expuso `GET /api/v1/events/recent` para consumir eventos reales desde la UI unificada
  - se ejecutó una reestructura visual grande en la preview v0.7: dashboard con ambas líneas siempre visibles, tn/h como dato protagonista, logout simple, eventos y alarmas separados, y simulación dual por línea en paneles paralelos
  - se montó `app-preview/` dentro del backend FastAPI para servir la preview desde `/app-preview/` usando el mismo proceso y facilitar prueba remota sin servidor estático aparte

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

### [HYBRID DEPLOY 2026-04-18]
- Se documentó el esquema operativo híbrido recomendado: app central en VPS y `plc_poller` corriendo en la PC del taller conectada al PLC.
- Se creó `docs/hybrid_tailscale_setup.md` con el flujo exacto PC taller -> Tailscale -> VPS/backend.
- Se agregó `backend/plc_poller/env.example` para parametrizar `PLC_HOST`, `PLC_RACK`, `PLC_SLOT`, `BACKEND_URL` y polling desde la PC del taller.
- Se actualizó `backend/plc_poller/README.md` para dejar explícito este modo de despliegue como camino recomendado.

### [PLC REAL -> FRONT v0.8 2026-04-18]
- Se agregó `GET /api/v1/measurements/latest` para exponer la última lectura por punto de medición y línea.
- La preview (`app-preview/index.html`) ahora consume `measurements/latest` durante `refreshData`.
- El dashboard por línea muestra badge de lectura PLC y usa lecturas reales cuando existen (`l1_input_main`, `l1_output_1/2/3`, `l2_input_hopper_1`, `l2_output_1`) con fallback a simulación cuando no hay dato.
- Resultado: ingesta real de PLC ya puede verse en frontend sin depender solo de valores mock/simulación.
- Se agregó auto-refresh en preview cada 5 segundos al iniciar sesión (con control de concurrencia para evitar solapamientos de requests).
- Se ajustó dashboard para mostrar en "Entrada proceso" el valor parcial PLC (no totalizador general).
- `plc_poller.main` pasó a modo continuo (polling por intervalo), evitando ejecución manual por cada actualización.
- Se incorporó integración para `tn/h` real desde PLC en dashboard: nuevo punto `l1_input_tph` (y placeholder `l2_input_tph`), con consumo en UI para reemplazar el valor fijo de simulación cuando exista lectura.
- Se ajustó branding de frontend a `Prosil - Lavado` y se versionó preview a v0.9.
- Se agregó visualización explícita de totalizadores generales de balanza en dashboard (tarjeta resumen L1 + stat por línea).
- Se mejoró la lectura visual de líneas detenidas: cuando una línea no tiene proceso activo, su tarjeta en dashboard toma tono apagado para distinguirla rápido de líneas en marcha.
- Corrección de lógica de caudales L2: el dashboard ahora calcula tn/h con variables de caudal (`l2_input_tph_a`, `l2_input_tph_b`) en lugar de usar parciales de tonelaje; en simple usa A, en blend usa A+B.
- Ajuste UX dashboard L2 según modo de proceso (preview v1.0):
  - simple: lectura protagonista basada en alimentación A
  - blend: lectura protagonista como suma A+B
  - blend: detalle visible de caudal/parcial individual de balanza 2 y 3
- Reorganización visual dashboard (preview v1.1):
  - parte superior enfocada en alimentación por línea (L1 y L2)
  - bloque inferior horizontal para salidas/productos (4 tarjetas)
  - branding y versión frontend actualizados
- Pulido visual dashboard (preview v1.2):
  - separación más clara entre bloque protagonista de alimentación y metadata/indicadores
  - bloque de split movido a franja horizontal inferior de cada tarjeta de línea
  - métricas clave centradas para lectura rápida
- Evolución visual preview v1.4:
  - se reemplazó la barra estática de escala de alimentación por mini gráfico lineal (sparkline)
  - histórico local por línea con 1 punto por minuto (hasta 60 minutos)
- Ajuste de resolución/escala de sparkline (preview v1.5):
  - muestreo aumentado a 1 punto cada 10 segundos
  - escala fija del gráfico configurada en 0-200 tn/h
- Mejora de legibilidad del sparkline (preview v1.6):
  - líneas guía horizontales para 0, 100 y 200 tn/h
  - etiquetas visibles de escala para referencia rápida de valor
- Corrección de escala en eje vertical (preview v1.7):
  - eje Y explícito con etiquetas 0/100/200 dentro del gráfico
  - eliminación de escala horizontal inferior para evitar confusión
- Mejora operativa del gráfico de alimentación (preview v1.8):
  - ventana temporal de 30 min con resolución de 10 segundos
  - eje Y reforzado con marcas 0/50/100/150/200
  - marcador de último valor y resumen min/max/actual
- Ajuste visual del eje Y (preview v1.9):
  - se removieron etiquetas numéricas 0/50/100/150/200 del área del gráfico
  - se mantuvieron líneas guía para referencia limpia sin ruido visual
- Rediseño operativo de interfaz (preview v2.0):
  - paleta migrada a tono arena con acentos azules para identidad de lavado
  - limpieza de mensajes y etiquetas secundarias para reducir ruido visual
  - eliminación del modo simulación del menú y de la UI
  - corrección del espacio vacío en sparkline tras quitar numeración del eje
- Corrección de conexión API en móvil (preview v2.1):
  - `API base URL` por defecto ahora usa `/plant-api` (ruta real detrás del proxy)
  - autocorrección de API base en prueba de conexión cuando detecta ruta inválida
- Ajuste visual rápido (preview v2.2):
  - paleta revertida al esquema azul original previo al experimento arena
  - se conserva la simplificación de UI (sin modo simulación) y la corrección de API móvil
- Seguridad/auth por roles (bloque A, punto 1):
  - login devuelve rol efectivo (`operador`, `supervisor`, `admin`)
  - dependencias de autorización por rol en router
  - `plc/*` y `simulation/*` restringidos a supervisor/admin
  - `admin/*` restringido a admin
  - seed actualizado con asignación de roles por usuario
  - preview login actualizado para consumir rol real
- Seguridad/auth rate limit (bloque A, punto 2):
  - throttling de login por usuario e IP
  - límite: 5 fallos en 15 minutos
  - bloqueo temporal: 15 minutos con `HTTP 429`

### [GITHUB PREP 2026-04-17]
- Se creó `.gitignore` en raíz para separar código del proyecto vs archivos personales/operativos del workspace OpenClaw.
- Se creó `docs/github_publishing.md` con guía concreta para publicar el repo y seguir desde otra PC.
- Se creó `docs/repo_scope.md` para dejar explícito qué entra y qué no entra al repo compartido.
- Decisión práctica: el repo GitHub será la fuente central del código; VPS para demo/continuidad, PC del taller para desarrollo y pruebas reales con PLC.

## Convención de versionado
- Mientras estemos definiendo arquitectura y datos, versionamos por componente.
- Formato inicial: `DB-SCHEMA vX.Y`.
- Cuando arranquemos la app en sí, se incorporará una versión global de proyecto/app y se registrará aquí en cada cambio.
