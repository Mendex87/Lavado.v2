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
Se dejó preparado el primer caso de prueba con una sola balanza:

- parciales en `DB13`
- totalizadores en `DB2`
- acceso optimizado quitado en ambas DB
- canal inicial: `l1_input_main`
- offsets asumidos para balanza 1: byte `0` en ambas DB (`Real`)

Si en TIA los offsets efectivos cambian, ajustar `mapping.example.json`.

## Próximo paso real
1. instalar `python-snap7`
2. confirmar conectividad IP/rack/slot al S7-1200
3. ejecutar:

```bash
cd backend
python3 -m plc_poller.main
```

4. si la lectura responde bien, sumar balanza 2, 3 y 4 con offsets `4`, `8` y `12`
