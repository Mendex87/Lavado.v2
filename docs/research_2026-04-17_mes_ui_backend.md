# Research Notes - 2026-04-17

Tema: referencias útiles para UX y arquitectura de apps industriales / MES.

## Fuentes revisadas
- Tulip, "6 Manufacturing Dashboards for Visualizing Production"
- OutSystems, "Manufacturing execution system (MES) software"

## Hallazgos útiles para este proyecto

### UX / visual industrial
1. **Dashboard tipo mission control**
   - útil para vista de planta completa
   - debe mostrar estado de líneas, producción del día, alarmas y métricas principales de un vistazo
2. **Shop floor overview**
   - mapear métricas a la estructura física de planta ayuda a detectar cuellos de botella rápido
   - esto encaja muy bien con la necesidad futura de tener layout/planta visual
3. **Dashboards distintos para tiempo real vs histórico**
   - tiempo real: operadores y supervisores
   - histórico: análisis, rendimiento, mejora continua
4. **Buenas prácticas claras de diseño**
   - pocas KPIs por pantalla
   - jerarquía visual fuerte
   - alertas imposibles de perder
   - drill-down en vez de saturar la vista principal
   - vistas por rol, no por “todos ven todo”
5. **KPIs sugeridos por rol**
   - operador: estado vivo, cola de tareas, alarmas
   - supervisor: métricas por turno, comparación entre líneas, calidad
   - gerencia: resumen, throughput, impacto de downtime

### Backend / arquitectura MES
1. **MES vive entre ERP/planificación y PLC/SCADA**
   - confirma la decisión ya tomada para este proyecto
   - PLC = ejecución industrial / señales / conteos / estados
   - app = contexto operativo, trazabilidad, stock, calidad, auditoría
2. **El flujo correcto es orden -> ejecución -> evidencia -> retorno de resultados**
   - coincide con nuestro concepto de proceso
3. **Calidad y compliance embebidos en el flujo**
   - conviene que eventos, evidencias y alertas sean entidades de primera clase en backend
4. **La adopción depende mucho del UX de operador**
   - instrucciones simples
   - pantallas rápidas
   - entradas mínimas
   - consistencia entre turnos
5. **Error típico en MES: exceso de customización frágil**
   - confirma que nos conviene arquitectura modular, versionada y con capas claras
6. **Integraciones frágiles son uno de los mayores riesgos**
   - conviene definir temprano una capa de integración PLC independiente del resto del dominio

## Decisiones derivadas para nuestro proyecto
- Mantener separación entre:
  - dominio de negocio
  - integración PLC
  - UI operativa
  - reporting/histórico
- Diseñar dos vistas fuertes desde el inicio:
  - tiempo real operacional
  - histórico / análisis
- Mantener UI enfocada en roles y acciones
- Tratar eventos, alarmas, trazabilidad y resets como parte central, no accesorio
- Preparar backend con servicios separados para:
  - procesos
  - stock
  - producción
  - PLC
  - alarmas/eventos

## Impacto directo en próximos pasos
1. Crear modelos ORM reales base alineados al schema v1.1
2. Separar servicios mock de servicios de dominio
3. Preparar capa futura `integrations/plc/`
4. Pasar la preview a una UI más parecida a mission control + proceso guiado
