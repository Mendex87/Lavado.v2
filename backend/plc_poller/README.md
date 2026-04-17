# PLC Poller (Python separado, mismo repo)

Este proceso queda pensado para leer el PLC Siemens S7-1200 sin agregar otro dispositivo intermedio.

## Objetivo
- leer tags/DBs del PLC
- transformar a `measurement points`
- enviar snapshots al backend con `POST /api/v1/measurements/ingest`

## Estado actual
Base de estructura lista. La conexión real al PLC se implementará después con `python-snap7`.

## Flujo esperado
1. leer configuración de conexión al PLC
2. leer tags de puntos activos
3. armar payload por línea
4. publicar al backend
5. reintentar si falla la red/API
