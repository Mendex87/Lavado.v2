# Manual de Usuario - Prosil Plant App v3.2

## 1. Ingreso
- Abrir `http://localhost:8010/app-preview/`.
- Ingresar usuario y contraseña.
- Verificar que la API base sea `http://localhost:8010/api/v1`.

## 2. Pantallas principales
- `Dashboard`: estado de líneas, caudales, alarmas y stock.
- `Abrir proceso`: alta de proceso por línea (L1 simple, L2 simple/blend).
- `Procesos activos`: monitoreo y cierre de procesos.
- `Stock`: niveles por cantera y alertas.
- `Handover`: transferencia de turno con checklist.
- `Calidad`: muestras, especificaciones y lotes.
- `Mantenimiento`: solicitudes, incidentes y preventivo.
- `OEE`: disponibilidad, rendimiento, calidad.
- `Reportes`: diarios y resumen ejecutivo.
- `Energía`: consumo y potencia.

## 3. Flujo operativo recomendado
1. Verificar `PLC Online` en cabecera.
2. Revisar alarmas activas.
3. Abrir proceso en la línea correspondiente.
4. Confirmar que suban caudales y parciales.
5. Validar que el stock se descuente por alimentación.
6. Cerrar proceso al terminar el lote/turno.
7. Completar handover.

## 4. Configuración PLC
- Ir a `Configuración` (admin).
- Ajustar `PLC Host`, `Rack`, `Slot`.
- Guardar configuración.
- Presionar `Aplicar configuración` para que el poller recargue sin reiniciar.

## 5. Indicadores clave
- `PLC Online/Offline`: conectividad real.
- `Procesos activos`: cantidad y estado por línea.
- `Stock bajo/crítico`: riesgo operativo por cantera.
- `Alarmas activas`: eventos pendientes de atención.

## 6. Problemas frecuentes
- **No conecta API**: revisar `API base URL` y backend en puerto 8010.
- **PLC no conecta**: validar IP/rack/slot y red local.
- **No baja stock**: verificar proceso activo y lecturas de alimentación.
- **Vista lenta**: usar `Actualizar` manual, revisar carga de red PLC y estado de SQLite.

## 7. Buenas prácticas
- No operar con más de un proceso activo por línea.
- Registrar notas en cierres e incidencias.
- Hacer handover completo al cambio de turno.
- Confirmar alarmas críticas antes de abrir nuevo proceso.
