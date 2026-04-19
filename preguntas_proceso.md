# PREGUNTAS PARA ENTENDER EL PROCESO DE LA PLANTA

Respondé una por una debajo de cada pregunta.

---

### 1. FLUJO OPERATIVO BÁSICO

**1.** ¿Cuántas líneas de producción tienen? (vi que hay L1 y L2 en el código)
dos lineas, la linea 1, tiene una sola tolva de alimentacion, la linea 2 puede alimentarse con 1 sola (modo simple) o con dos (Blend) 

**2.** ¿Cuál es la capacidad nominal de cada línea en tn/h?
entre 100 y 160 tn/h total de alimentacion de cada linea

**3.** ¿Qué productos generan? (tipos de arena, especificaciones)
no los tengo definidos aun , pero son diferentes granulometrias de arena que usan en el fracking 

**4.** ¿Cómo es el flujo típico de un turno?
- ¿Empiezan con reunión de briefing?
- ¿Hay procedimientos específicos de arranque?
- ¿Cómo terminan el turno (cierre de proceso, inventario)?
son turnos de 12 hs, donde un supervisor dice que tipo de arena/cantera van a procesar y asi se define el dia de trabajo, es muy cambiante igual quizas en el dia se lavan distintos productos por la misma linea de produccion , siempre parando y arrancando un nuevo proceso
---

### 2. ROLES Y RESPONSABILIDADES

**5.** ¿Cuántos operadores trabajan por turno?
un operador, 12 hs por turno, 24hs de produccion

**6.** ¿Hay un supervisor por turno o uno para toda la planta?
siempre hay un supervisor de planta, y luego cada turno tiene un encargado

**7.** ¿Qué diferencias de permisos tiene cada rol?
- Operador: ¿puede iniciar/cerrar procesos? ¿ingresar stock? 
- Supervisor: ¿puede hacer mediciones manuales? ¿resetear parciales?
- Admin: ¿acceso a configuración completa?

---correcto, algo asi esta pensado

### 3. PROCESOS DE PRODUCCIÓN

**8.** ¿Qué significa "modo simple" vs "modo blend" en L2?
- ¿Cuándo usan uno u otro?
simple es una cantera , blem es con dos tolvas se mezclan dos canteras distintas

**9.** ¿Cómo definen los Blend percentages (ej: 80% A, 20% B)?
depende el cliente y el producto que se quiere obtener, en la operacion se suben o bajan los hz de los motores de las tolvas de alimentacion para llegar a la proporcion que se necesita

**10.** ¿Qué sucede cuando hay un problema (atascamiento, falla de balanza)?
- ¿Cómo lo resuelven?
- ¿Quién debe intervenir?

---es un gran punto, es lo que tenemos que mejorar, mas que nada de fiabilidad de lo que marca sea real, por eso esta la parte de modificar en manual los datos de stock y eso

### 4. INTEGRACIÓN PLC

**11.** ¿Qué variables leen del PLC?
- Solo caudales (tn/h) y parciales (toneladas)?
- ¿También leen humidity, temperaturas, estados de motores?

por ahora tn/h, parciales, totales, pero luego se pueden agregar horometros de produccion para programar calibraciones y mantenimientos

**12.** ¿Con qué frecuencia hace polling del PLC? (vi 500ms en los docs)
estamos en test, pero si es en local 100ms

**13.** ¿Qué pasa cuando el PLC no responde?
- ¿Los operadores se dan cuenta inmediatamente?
- ¿Tienen procedimiento de fallback?

---no esta nada definido eso, pensemoslo, deberia seguir funcionando la app con entradas manuales

### 5. STOCK Y CANTERAS

**14.** ¿Cuántas canteras alimentan la planta?

---no hay un numero definido, debemos tener la opcion de agregar y modificar eso

**15.** ¿Cómo se maneja el stock?
- ¿Hay alertas cuando está bajo?
- ¿Quién puede ingresar material nuevo?

no hay alertas, pero estaria bueno implementarlo, para todo eso esta el supervisor

**16.** ¿Cómo calculan el rendimiento (yield) de cada cantera?
- ¿Lo usan para algo operativo o solo informativo?

---no estamos calculando, pero si seria muy interesante tenerlo, para ver los rendimintos de cada cantera

### 6. MEDICIONES Y CONTINGENCIAS

**17.** ¿Cuándo necesitan ingresar mediciones manuales?
- ¿Frecuencia diaria?
por ahora la entrada de stock va a ser manual, diario o por turno mejor dicho, las contingencias tambien hay algunas balanzas de productos que se hacen manual las cargas

**18.** ¿Qué causas típicas de medición manual existen?
- Falla de PLC
- Balanza descalibrada
- Otros

balanzas descalibradas por fallas mecanicas

**19.** ¿Cómo verifican que la medición manual es correcta?

---con los promedios de produccion, no es muy presciso

### 7. PROBLEMAS Y DOLENCIAS

**20.** ¿Qué problemas operativos enfrentan frecuentemente?
- Alarmas no reconocidas a tiempo
- Confusión entre turnos
- Datos inconsistentes
- Lentitud en la app
- Otros

confusion entre turnos y datos inconsistentes seria el principal motivo

**21.** ¿Qué información extra les gustaría ver en el dashboard que hoy no tienen?

fecha y hora , turno , que mas propondrias

**22.** ¿Qué procesos les resultan lentos o complicados de hacer en la app actual?

---no esta implementada la app, la estoy creadno desde cero, ah soy eze por cierto

### 8. INFRAESTRUCTURA

**23.** ¿El backend corre en un VPS o en una PC local?
para las pruebas en un vps, pero la idea es que el servidor sea local en la planta para no depender de internet

**24.** ¿Tienen acceso a Internet constante o hay momentos sin conexión?
casi siempre con starlink

**25.** ¿Planean usar Redis para caché o lo van a usar sin eso?

---no se que es o para que sirve

### 9. PRIORIDADES

**26.** De las mejoras que propuse, ¿cuál es la más urgente para ustedes hoy?

tener una app funcional que controle los stocks y producciones

**27.** ¿Hay algo que no funcione actualmente que necesiten corregir urgente?

---la fiabilidad de las balanzas
