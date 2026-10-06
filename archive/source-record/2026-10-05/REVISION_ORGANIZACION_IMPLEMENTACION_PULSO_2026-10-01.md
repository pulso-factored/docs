# Iteraciones de organización de implementación

Alcance: plan §30 del spec V2, no implementación ni tickets externos. Dos rondas independientes con backend/AI, data/evaluación e infra/frontend, seguidas de rechecks concretos y validación estructural.

## Ronda 1 — Descomposición bottom-up

Problema: familias P*-* agrupaban varios comportamientos y el dibujo mezclaba dependencias técnicas con hitos. Se extrajeron features/HU/UC con productores, consumidores y handoffs propios. UI no habilita el detector, AWS no habilita el lab local, Core determinista no necesita proxy y original/E0 son adapters hermanos. Fases quedan como agrupaciones de aceptación, no barreras globales de despacho.

## Ronda 2 — Dependencias semánticas

- Bridge provisional no equivale a eligibility final: U16→U20→U35→U17.
- La suite nativa tiene productor y pin: plan/suite→compiler→writer/freeze→evaluación. Sin suite ad hoc posterior.
- Segunda iteración consume ingesta real: plataforma U29 o variante E0 con sensor/contexto E0.
- Replay preaprobado no demuestra activación de nuevas capacidades; U23-A integra gates, autoridad y aprendizaje.
- UI y fork tienen sucesores con prerequisitos explícitos; no se acepta un panel completo por tener timeline.
- Deploy mínimo no acredita full-stack; manifest selecciona sus dependencias.
- Guards/run_control van antes de los primeros efectos; la UX de comandos no introduce seguridad tardíamente.
- Hitos enumeran unidades/variantes requeridas; no aceptan successors implícitamente.

Resultado: 35 unidades base y 9 variantes/sucesores, con HU/UC, dependencias duras y handoff/negativo en tablas normativas. Cada unidad se asigna por readiness concreta; integrador distinto reúne el grupo y revisores independientes intentan romperlo. Builder y juez tienen ownership separado. TDD sigue un comportamiento RED→GREEN→refactor a la vez, incluyendo RED de integración.

## Evidencia y límites

Ejecutados Test-SpecStructure.ps1 y Test-ImplementationDag.ps1: 30 secciones, tablas/fences/enlaces válidos; 44 IDs únicos, referencias existentes y grafo acíclico. Orden topológico disponible por script, no secuencia obligatoria ni promesa de velocidad.

Rechecks cerraron las dependencias reportadas; últimos ajustes añadieron U12-E al aprendizaje E0 y enumeraron U35, variantes continuous y paneles en hitos. La revisión humana/ingeniería examina semántica; el script sólo estructura. No se ejecutó código de producto, RED/GREEN real, suites ni despliegue. El plan necesita aprobación antes de asignar implementación.
