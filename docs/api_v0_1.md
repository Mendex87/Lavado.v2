# API v0.1

Base contractual inicial para backend de la app industrial.

Estado: borrador operativo
Soporta: `DB-SCHEMA v1.1`

## Principios
- La entidad principal es el **proceso**.
- El PLC es la fuente industrial de datos de producción y estados.
- La app es la fuente de verdad operativa, trazable y administrativa.
- No se modelan enclavamientos físicos duros en API, solo contexto, permisos, eventos y avisos.
- La API debe ser estable, auditable y preparada para crecer.

## Base path
`/api/v1`

---

## 1. Auth

### POST `/auth/login`
Autentica usuario y abre sesión de operador.

**body**
```json
{
  "username": "operador1",
  "password": "***"
}
```

**response**
```json
{
  "token": "jwt-o-session-token",
  "user": {
    "id": 10,
    "username": "operador1",
    "full_name": "Operador Turno A",
    "roles": ["operador"]
  },
  "session": {
    "id": 55,
    "shift": {
      "id": 1,
      "code": "T1",
      "name": "Turno 1"
    },
    "login_at": "2026-04-17T11:00:00Z"
  }
}
```

### POST `/auth/logout`
Cierra sesión de usuario.

---

## 2. Usuarios y catálogos

### GET `/users/me`
Devuelve usuario autenticado y roles.

### GET `/shifts`
Lista turnos.

### GET `/lines`
Lista líneas.

### GET `/quarries`
Lista canteras con stock actual.

### POST `/quarries`
Crea cantera (supervisor).

### PATCH `/quarries/:id`
Edita cantera (supervisor).

### GET `/products`
Lista productos.

### POST `/products`
Crea producto.

### GET `/scales`
Lista balanzas y relación con línea/cinta.

---

## 3. Procesos

### GET `/processes/active`
Lista procesos activos por línea.

### GET `/processes/:id`
Detalle completo del proceso.
Incluye:
- operador
- turno
- entradas
- salidas
- lecturas de balanza
- eventos
- alarmas

### POST `/processes`
Abre un nuevo proceso.

**body**
```json
{
  "line_id": 2,
  "mode": "blend",
  "operator_user_id": 10,
  "supervisor_user_id": 3,
  "inputs": [
    {
      "quarry_id": 1,
      "scale_id": 5,
      "input_order": 1,
      "hopper_code": "A",
      "blend_target_pct": 80
    },
    {
      "quarry_id": 2,
      "scale_id": 6,
      "input_order": 2,
      "hopper_code": "B",
      "blend_target_pct": 20
    }
  ],
  "outputs": [
    {
      "scale_id": 9,
      "product_id": 4,
      "output_code": "L2_S1",
      "classification": "product"
    },
    {
      "scale_id": 10,
      "product_id": null,
      "output_code": "CFG_OUT",
      "classification": "discard"
    }
  ],
  "confirm_reset": true,
  "notes": "Inicio de proceso línea 2 blend"
}
```

**reglas**
- solo un proceso activo por línea
- si `confirm_reset=false`, no se abre
- debe quedar evento de apertura
- debe generarse comando lógico de reset de parciales al PLC

### POST `/processes/:id/close`
Cierra un proceso.

**body**
```json
{
  "closed_by_user_id": 10,
  "close_reason": "fin_normal",
  "notes": "cierre de producción"
}
```

### POST `/processes/:id/cancel`
Cancela un proceso.

### GET `/processes/:id/inputs`
Entradas del proceso.

### GET `/processes/:id/outputs`
Salidas configuradas del proceso.

---

## 4. Producción y lecturas

### GET `/processes/:id/readings`
Lecturas históricas de balanzas por proceso.

Filtros opcionales:
- `scale_id`
- `from`
- `to`

### POST `/processes/:id/readings/sync`
Inserta o sincroniza lecturas provenientes del PLC/integración.

**body**
```json
{
  "readings": [
    {
      "scale_id": 5,
      "reading_at": "2026-04-17T11:05:00Z",
      "partial_ton": 120.0,
      "totalizer_ton": 24550.0
    }
  ]
}
```

### GET `/processes/:id/production-summary`
Resumen consolidado de producción del proceso.

### POST `/processes/:id/production-summary/rebuild`
Recalcula resumen desde lecturas.

### GET `/scales/:id/totalizers`
Historial de totalizador general de una balanza.

### POST `/scales/totalizers/sync`
Sincroniza totalizadores desde PLC.

---

## 5. Stock

### GET `/stock/quarries`
Estado actual de stock por cantera.

### GET `/stock/quarries/:quarryId/movements`
Histórico de movimientos.

### POST `/stock/quarries/:quarryId/movements`
Carga ingreso, ajuste o movimiento manual.

**body**
```json
{
  "movement_type": "adjustment",
  "direction": "in",
  "quantity_ton": 35.5,
  "signed_quantity_ton": 35.5,
  "source": "manual",
  "reference_code": "AJ-2026-0001",
  "entered_by_user_id": 3,
  "reason": "ajuste por movimiento interno"
}
```

### POST `/stock/consume-from-process/:processId`
Genera consumos de stock a partir de balanzas de entrada del proceso.

**regla**
- siempre consumir desde entradas de línea, no desde producto final

---

## 6. PLC / integración

### GET `/plc/variables`
Lista variables configuradas.

### POST `/plc/variables`
Alta de variable PLC.

### POST `/plc/variables/history`
Inserta histórico de variables seleccionadas.

### POST `/plc/process-context/:processId/publish`
Publica al PLC el contexto del proceso activo.

Debe enviar, según corresponda:
- proceso habilitado
- línea activa
- modo
- blend objetivo
- flags operativos requeridos

### POST `/plc/process-context/:processId/reset-partials`
Solicita reset de parciales al PLC con confirmación previa.

**body**
```json
{
  "requested_by_user_id": 10,
  "confirmed": true
}
```

### GET `/plc/alarms/active`
Alarmas activas provenientes del PLC o generadas por lógica de app.

---

## 7. Alarmas y eventos

### GET `/processes/:id/events`
Eventos de proceso.

### POST `/processes/:id/events`
Inserta evento manual o de sistema.

### GET `/alarms`
Lista alarmas.

### POST `/alarms/:id/ack`
Reconoce alarma.

---

## 8. Rendimiento y humedad

### GET `/quarries/:id/yield`
Resumen de rendimiento histórico de cantera.

### POST `/humidity-readings`
Inserta lectura de humedad manual o de sensor.

**body**
```json
{
  "process_output_id": 22,
  "product_id": 4,
  "sensor_code": "H-L2-P4-01",
  "humidity_pct": 7.4,
  "measured_at": "2026-04-17T11:20:00Z"
}
```

### POST `/processes/:id/yield/recalculate`
Recalcula rendimiento de cantera usando entradas, salidas y humedad disponible.

---

## 9. Dashboard operativo

### GET `/dashboard/overview`
Devuelve vista operacional resumida:
- procesos activos
- línea 1 / línea 2
- operador actual
- toneladas parciales
- totalizadores relevantes
- alarmas activas
- stock resumido

---

## Reglas funcionales globales
- no puede existir más de un proceso activo por línea
- un cambio de cantera/modo/línea implica cerrar proceso y abrir otro
- los consumos de stock salen de balanzas de entrada
- el producto final puede tener humedad y corrección posterior
- la salida configurable puede ser producto o descarte según proceso
- toda acción sensible debe quedar auditada
- el reset de parciales requiere confirmación explícita

## Próximo nivel de detalle
Pendiente para siguiente iteración:
- códigos de error estándar
- permisos por endpoint
- payloads exactos de integración PLC
- webhooks/event bus interno
- paginación/filtros estándar
- estrategia de polling vs eventos en tiempo real
