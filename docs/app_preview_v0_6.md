# App Preview v0.6

Preview unificada sobre el backend nuevo.

## Qué reúne
- login de demo para operador/supervisor
- dashboard operativo
- alta de procesos
- vista de procesos activos
- stock
- eventos
- módulo de simulación separado

## Criterio de arquitectura
La simulación quedó en una pestaña propia para que más adelante se pueda apagar sin romper la gestión principal.

## Flujo principal
1. ingresar con usuario demo
2. probar conexión con backend
3. ejecutar seed de catálogos si hace falta
4. abrir proceso
5. seguir proceso activo desde dashboard y pestaña de procesos
6. usar simulación solo como módulo auxiliar de prueba

## Simulación
- inicio manual
- paso manual
- auto simulación cada 1 segundo
- pausa
- reset
- si hay proceso activo válido en la línea, el step ya genera evento backend y descuenta stock

## Pendientes naturales
- auth real backend
- persistencia más rica de lecturas y resúmenes de producción
- dashboard más industrial y detallado
- integración con PLC real
