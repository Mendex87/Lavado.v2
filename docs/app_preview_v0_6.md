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

## Pendientes naturales
- auth real backend
- relación fuerte entre proceso, stock y simulación
- eventos persistidos en DB
- consumo real de stock por simulación
- integración con PLC real
