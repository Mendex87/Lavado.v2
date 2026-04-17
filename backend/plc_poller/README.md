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

## Próximo paso real
1. instalar `python-snap7`
2. copiar `mapping.example.json` a un archivo real
3. reemplazar direcciones ejemplo por DB/byte/bit reales del S7-1200
4. ejecutar:

```bash
cd backend
python3 -m plc_poller.main
```
