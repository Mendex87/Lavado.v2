# Esquema híbrido: VPS + Docker + Tailscale + PC taller

Objetivo: dejar la app centralizada en la VPS y usar la PC conectada al PLC como nodo de captura industrial.

## Arquitectura

```text
PLC S7-1200
   |
   | red local industrial
   v
PC taller
  - plc_poller
  - acceso Snap7 al PLC
   |
   | Tailscale
   v
VPS
  - contenedor Docker
  - backend FastAPI
  - DB
  - preview /app-preview/
```

## Decisión operativa

- La **VPS** es el centro de la aplicación.
- La **PC taller** no hospeda la app completa, solo el lector/publicador hacia backend.
- El tráfico entre PC y VPS viaja por **Tailscale**, no por internet pública.

## Qué corre en cada lado

### VPS
- backend
- base de datos
- preview web
- lógica de procesos
- eventos
- stock
- simulación

### PC taller
- `plc_poller`
- conexión al PLC S7-1200
- publicación de lecturas a la VPS

## URL esperada del backend

La PC taller debe publicar al backend usando la dirección Tailscale de la VPS, por ejemplo:

- `http://100.x.y.z:8010/api/v1`
- o `http://nombre-vps.tailnet.ts.net:8010/api/v1`

Elegir una sola y dejarla fija en la configuración del poller.

## Variables mínimas del poller en PC taller

```bash
PLC_HOST=192.168.0.10
PLC_RACK=0
PLC_SLOT=1
BACKEND_URL=http://NOMBRE-O-IP-TAILSCALE:8010/api/v1
PLC_MAPPING_PATH=plc_poller/mapping.example.json
PLC_POLL_INTERVAL_SECONDS=2
```

## Flujo de prueba recomendado

### Etapa 1, validar backend remoto
Desde la PC taller, probar:

```bash
curl http://NOMBRE-O-IP-TAILSCALE:8010/api/v1/health
```

Debe responder algo como:

```json
{"ok":true}
```

### Etapa 2, validar poller en modo demo
Si Snap7 todavía no está instalado o no hay lectura real, correr:

```bash
cd backend
python3 -m plc_poller.main
```

Si falla conexión al PLC, el poller debe mostrar el payload esperado en modo demo.

### Etapa 3, validar ingestión real
Con PLC accesible y mapeo correcto:
- leer una sola balanza
- publicar a `/api/v1/measurements/ingest`
- revisar luego en backend:
  - `GET /api/v1/measurements/points`
  - `GET /api/v1/events/recent`

## Primer corte recomendado

No arrancar con toda la planta.
Hacer primero esta prueba mínima:

- Línea 1
- canal `l1_input_main`
- parciales en `DB13`
- totalizador en `DB2`
- un único flujo end-to-end funcionando

## Criterio de “funciona”

Se considera funcionando cuando:

1. La PC taller llega por Tailscale al backend de la VPS.
2. El poller puede leer al menos una variable real del S7-1200.
3. El backend acepta `POST /api/v1/measurements/ingest`.
4. La lectura queda persistida en backend.
5. La preview puede abrirse desde la VPS sin tocar endpoints manualmente.

## Qué evitar

- no duplicar backend en la PC taller salvo necesidad real
- no duplicar base de datos
- no mezclar el rol de la PC taller con el de servidor principal
- no exponer la red industrial fuera de Tailscale

## Próximo paso práctico

1. identificar el hostname o IP Tailscale estable de la VPS
2. confirmar el puerto expuesto del backend en la VPS
3. configurar `BACKEND_URL` del poller con esa dirección
4. hacer primera prueba real con `l1_input_main`
