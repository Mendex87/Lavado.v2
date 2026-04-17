# Technical Trace

Bitácora técnica para reconstruir decisiones, fallas, debugging y cambios de implementación.

## Regla
Cada vez que aparezca una falla, ajuste delicado o cambio estructural importante, registrar:
- fecha
- componente
- síntoma
- causa sospechada o confirmada
- acción tomada
- resultado
- commit asociado si existe

## Estado inicial
- Proyecto en fase de definición + backend base + preview operativa temprana.
- Backend ya migrando desde mocks hacia servicios/repositorios reales.
- Preview remota útil para validar flujo, pero no es todavía la app final.
