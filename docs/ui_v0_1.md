# UI v0.1

Diseño funcional inicial de pantallas para la app industrial.

Estado: borrador operativo
Soporta:
- `DB-SCHEMA v1.1`
- `API v0.1`

## Principios de UI
- Uso rápido en planta, con mínima fricción.
- Acciones críticas bien visibles y confirmadas.
- Lectura clara a distancia.
- Pocas decisiones por pantalla.
- Prioridad a estado actual, producción y alarmas.
- Nada de esconder lo importante detrás de menús profundos.

---

# 1. Estructura general

## Menú principal
1. Inicio
2. Procesos
3. Producción
4. Stock
5. Alarmas y eventos
6. Canteras
7. Configuración

**Según rol:**
- operador: ve solo lo necesario para operar
- supervisor: ve todo

---

# 2. Pantalla de login

## Objetivo
Identificar operador y dejar trazabilidad por turno.

## Elementos
- usuario
- contraseña
- botón `Ingresar`
- reloj visible
- turno detectado automáticamente

## Comportamiento
- al iniciar sesión, se abre `user_session`
- muestra nombre, rol y turno detectado
- si el turno no coincide con lo esperado, se puede dejar aviso visible, pero no necesariamente bloquear

---

# 3. Pantalla Inicio / Dashboard

## Objetivo
Ver estado general de planta en 3 segundos.

## Bloques
### A. Líneas
Para cada línea:
- estado: `sin proceso`, `proceso activo`, `alarma`
- operador actual
- proceso actual
- modo (`simple` / `blend`)
- cantera/s activas
- toneladas parciales

### B. Alarmas activas
- lista corta y visible
- color por severidad
- acceso rápido al detalle

### C. Stock resumido
- cantera
- stock actual
- nivel visual (normal / bajo / crítico)

### D. Totalizadores clave
- totalizador general por balanza principal

## Acciones rápidas
- `Abrir proceso`
- `Cerrar proceso`
- `Ver alarmas`
- `Ver stock`

---

# 4. Pantalla Abrir proceso

## Objetivo
Guiar al operador paso a paso.

## Flujo
### Paso 1. Selección de línea
- Línea 1
- Línea 2

### Paso 2. Selección de modo
- si línea 1: puede omitirse o quedar simple por defecto
- si línea 2:
  - simple
  - blend

### Paso 3. Selección de cantera/s
- simple: una cantera
- blend: cantera A y cantera B

### Paso 4. Configuración esperada
- producto/s esperados
- salida configurable como producto o descarte
- blend objetivo % si aplica

### Paso 5. Confirmación final
Resumen:
- operador
- turno
- línea
- modo
- cantera/s
- producto/s
- salida configurable

### Paso 6. Popup obligatorio
Mensaje:
`¿Confirmar inicio de proceso? Esto reseteará los contadores parciales del PLC.`

Botones:
- `Cancelar`
- `Confirmar y abrir proceso`

## Regla UX
No mostrar todo junto en un formulario gigante. Tiene que ser guiado.

---

# 5. Pantalla Proceso activo

## Objetivo
Ser la pantalla principal durante operación.

## Cabecera
- código de proceso
- línea
- operador
- turno
- hora de inicio
- estado

## Bloque de contexto
- cantera/s activas
- modo actual
- producto/s configurados
- blend objetivo si aplica

## Bloque de producción en vivo
Por balanza:
- parcial actual
- totalizador general
- tendencia visual simple

## Bloque de salidas
- salidas de producto
- salida configurable
- clasificación actual (`producto` o `descarte`)
- humedad si existe

## Acciones disponibles
- `Cerrar proceso`
- `Registrar evento`
- `Ver detalle PLC`

## Botón peligroso
`Cerrar proceso`
con confirmación clara.

---

# 6. Pantalla Cerrar proceso

## Objetivo
Cerrar correctamente y dejar auditado el motivo.

## Campos
- motivo de cierre
  - fin normal
  - cambio de cantera
  - cambio de línea
  - parada operativa
  - mantenimiento
  - otro
- observaciones

## Resumen antes de confirmar
- toneladas de entrada
- toneladas de salida
- descarte
- alarmas registradas

## Acción final
- `Confirmar cierre`

---

# 7. Pantalla Producción

## Objetivo
Consultar producción histórica y actual.

## Filtros
- fecha desde/hasta
- línea
- cantera
- producto
- operador
- turno
- proceso

## Tabla principal
- proceso
- línea
- cantera/s
- producto/s
- entradas
- salidas
- humedad
- rendimiento
- estado

## Vista detalle
Al entrar a un proceso:
- lecturas por balanza
- resumen consolidado
- eventos
- alarmas

---

# 8. Pantalla Stock

## Objetivo
Controlar stock de cantera con trazabilidad.

## Vista principal
Por cantera:
- stock actual
- último movimiento
- estado visual

## Acciones supervisor
- `Registrar ingreso`
- `Ajustar stock`
- `Ver movimientos`

## Regla importante
El operador no debería tocar ajustes manuales.

## Pantalla de movimiento
Campos:
- tipo
- dirección
- toneladas
- motivo
- referencia
- observaciones

Todo ajuste debe quedar auditado.

---

# 9. Pantalla Canteras

## Objetivo
Administrar canteras y relaciones con productos.

## Lista
- nombre
- activa/inactiva
- productos habilitados
- stock actual

## Acciones supervisor
- crear cantera
- editar cantera
- activar/desactivar
- vincular productos posibles

---

# 10. Pantalla Alarmas y eventos

## Objetivo
Concentrar alertas operativas y trazabilidad.

## Panel de alarmas
- activas
- reconocidas
- cerradas

## Panel de eventos
- inicio de proceso
- reset parciales
- cambio de estado
- ajustes de stock
- eventos manuales

## Filtros
- línea
- severidad
- fecha
- proceso

---

# 11. Pantalla PLC / Diagnóstico (supervisor/técnico)

## Objetivo
Ver integración sin meter al operador en cosas técnicas.

## Muestra
- variables importantes PLC → app
- contexto enviado app → PLC
- último reset de parciales
- última sincronización de lecturas
- estado de comunicación

## Uso
Solo supervisor/técnico.

---

# 12. Pantalla Configuración

## Incluye
- usuarios
- roles
- turnos
- líneas
- balanzas
- productos
- reglas operativas simples

---

# 13. Reglas visuales

## Colores
- verde: normal
- amarillo: atención
- rojo: alarma / riesgo
- gris: inactivo

## Tipografía y tamaños
- números grandes para toneladas
- botones grandes
- contraste alto
- evitar texto chico tipo dashboard de oficina

## Responsive real
- debe funcionar en PC industrial / tablet / notebook
- mobile puede existir, pero no debe ser la referencia principal de diseño

---

# 14. Flujo principal de uso

## Operador
1. login
2. dashboard
3. abrir proceso guiado
4. operar mirando proceso activo
5. cerrar proceso

## Supervisor
1. login
2. dashboard
3. revisar stock / alarmas / procesos
4. ajustar stock si hace falta
5. administrar canteras / productos / configuración

---

# 15. Próxima iteración
Pendiente definir:
- wireframes por pantalla
- jerarquía exacta de componentes
- comportamiento en tiempo real
- estrategia de refresco/polling
- diseño visual industrial final
- navegación detallada entre vistas
