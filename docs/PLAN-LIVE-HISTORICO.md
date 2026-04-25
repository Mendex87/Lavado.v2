# Plan Live + Historico + Stock

## Objetivo

Separar el sistema en 2 capas:

1. `Dato vivo`
   - Para pantalla operativa.
   - Refresco rapido.
   - No depende del historico guardado en DB.

2. `Historico + stock oficial`
   - Para trazabilidad y control real.
   - Se guarda con una cadencia baja y controlada.
   - Solo cuando hay al menos una linea con proceso activo.

## Regla principal

Solo se registra historico si hay al menos una linea operando.

- Si `L1` o `L2` tienen proceso activo: se guarda.
- Si ninguna linea tiene proceso activo: no se guarda nada.
- Si una linea esta activa y el valor es `0`: igual se guarda.

## Arquitectura propuesta

### 1. Canal live

Crear un flujo para dato vivo que use el frontend.

Frecuencia sugerida:

- Poller live: `0.5 s`
- Frontend live refresh: `0.5 s`

Que debe incluir:

- `l1_input_tph`
- `l1_input_main.partial`
- `l1_totalizer_general`
- `l2_input_tph_a`
- `l2_input_tph_b`
- `l2_input_hopper_1.partial`
- `l2_input_hopper_2.partial`
- `l2_totalizer_general`
- timestamp de lectura
- estado de linea activa/inactiva

Implementacion sugerida:

- endpoint nuevo: `/measurements/live`
- origen de datos: memoria/cache o una estructura chica de ultimo valor
- no usar `measurement_readings` para alimentar la UI principal

## 2. Historico

Guardar historico solo en estos momentos:

1. apertura de proceso
2. checkpoint cada `1 min`
3. cierre de proceso

Regla del checkpoint:

- corre cada 1 minuto
- si hay al menos una linea activa, guarda snapshot
- si no hay lineas activas, no hace nada

### Que guardar en el historico

Guardar solo valores utiles para produccion y stock.

#### Linea 1

- `l1_input_main.partial_ton`
- `l1_totalizer_general.totalizer_ton`
- `l1_input_tph.partial_ton`

#### Linea 2

- `l2_input_hopper_1.partial_ton`
- `l2_input_hopper_2.partial_ton`
- `l2_totalizer_general.totalizer_ton`
- `l2_input_tph_a.partial_ton`
- `l2_input_tph_b.partial_ton`

#### Opcional segun necesidad

- salidas de producto si ya son confiables

## 3. Stock oficial

El stock oficial no conviene moverlo cada `0.5 s`.

Conviene actualizarlo en:

1. checkpoint cada `1 min`
2. cierre de proceso
3. movimientos manuales de stock

### Regla de stock

- stock persistido: por checkpoint
- stock visual opcional: puede mostrarse estimado en vivo
- stock oficial DB: solo checkpoint/cierre/manual

## Beneficios

### Operativos

- dashboard mas fluido
- menos titileo
- dato vivo independiente de la DB historica

### Tecnicos

- menos inserts en SQLite
- menos dependencia entre UI e historico
- mas robustez si falla un cierre o una escritura puntual

### De negocio

- trazabilidad suficiente sin generar basura
- stock mas auditable
- base mas clara para produccion 24/7

## Implementacion por fases

## Fase 1

Crear canal live.

- agregar endpoint `/measurements/live`
- agregar almacenamiento de ultimo valor por codigo/linea
- cambiar dashboard para leer live en vez de `latest`

Resultado esperado:

- pantalla actualiza cada `0.5 s`
- UI ya no depende del historico

## Fase 2

Crear checkpoint historico de 1 minuto.

- timer separado en poller o backend
- guardar solo si hay linea activa
- guardar aunque el valor sea `0`

Resultado esperado:

- DB baja mucho de volumen
- trazabilidad se mantiene

## Fase 3

Mover stock oficial al checkpoint.

- descontar stock por snapshot de 1 minuto
- reforzar cierre final de proceso
- mantener manuales inmediatos

Resultado esperado:

- stock estable
- menos escrituras
- mejor auditabilidad

## Fase 4

Limpieza final de UI.

- sacar textos de prototipo
- dejar copy mas operativo
- revisar cards de lineas, stock y procesos

## Decisiones ya tomadas

- live a `0.5 s`
- checkpoint a `1 min`
- historico solo con linea activa
- si linea activa y valor `0`, igual se guarda
- stock oficial por checkpoint y cierre

## Pendientes para ejecutar

1. implementar `/measurements/live`
2. conectar dashboard a `/measurements/live`
3. crear checkpoint de 1 minuto
4. mover stock oficial a checkpoint
5. limpiar textos finales de UI

## Recomendacion final

Este enfoque es mejor que usar una sola capa para todo.

La regla objetivo pasa a ser:

- `pantalla = dato vivo`
- `DB = historico util`

Eso simplifica operacion, mejora fluidez y reduce ruido en la base.
