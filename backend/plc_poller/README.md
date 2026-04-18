# PLC Poller (Python separado, mismo repo)

Este proceso queda pensado para leer el PLC Siemens S7-1200 sin agregar otro dispositivo intermedio.

## Objetivo
- leer tags/DBs del PLC
- transformar a `measurement points`
- enviar snapshots al backend con `POST /api/v1/measurements/ingest`

## Estado actual
Base de estructura lista y preparada para `python-snap7`.

## Archivos clave
- `mapping.example.json`: mapa ejemplo de DB/bytes/bits del PLC
- `env.example`: variables sugeridas para correr desde la PC del taller
- `client.py`: wrapper base para `python-snap7`
- `runtime.py`: transforma lecturas del PLC en payloads por línea
- `publisher.py`: publica al backend
- `main.py`: arranque principal

## Flujo esperado
1. leer configuración de conexión al PLC
2. cargar mapa de canales del archivo JSON
3. leer direcciones reales del S7
4. armar payload por línea
5. publicar al backend
6. reintentar si falla la red/API

## Primera prueba real aterrizada
Se dejó preparado el primer caso de prueba con una balanza + feed-rate:

- parciales en `DB13`
- totalizadores en `DB2`
- acceso optimizado quitado en ambas DB
- canal de entrada: `l1_input_main`
- canal de alimentación actual (tn/h): `l1_input_tph`
- offsets ejemplo: `l1_input_main` en byte `0` y `l1_input_tph` en byte `4` (ambos `Real`)

Si en TIA los offsets efectivos cambian, ajustar `mapping.example.json`.

## Modo recomendado de despliegue

- backend y preview en la VPS
- `plc_poller` ejecutando en la PC del taller
- publicación al backend usando la IP o hostname Tailscale de la VPS

Ver detalle en `docs/hybrid_tailscale_setup.md`.

## Próximo paso real
1. instalar `python-snap7`
2. copiar `env.example` a un `.env` local propio o exportar variables equivalentes
3. confirmar conectividad IP/rack/slot al S7-1200
4. confirmar conectividad desde la PC al backend de la VPS por Tailscale
5. ejecutar:

```bash
cd backend
python3 -m plc_poller.main
```

6. si la lectura responde bien, sumar balanza 2, 3 y 4 con offsets `4`, `8` y `12`
