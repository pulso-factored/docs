# Pulso: detección proactiva y automejora

Documento vivo. Fecha de consolidación: 2026-09-29. Fuente principal: decisiones expresadas por el usuario en esta conversación. No representa implementación ni resultados experimentales.

## Alcance confirmado por el usuario

El producto se diseña como un sistema real de un banco, usando su histórico recopilado y su operación, no como una arquitectura para el dataset de la hackathon. El diferencial es identificar problemas y oportunidades, analizarlos y proponer proactivamente mejoras evaluables. El servicio debe aumentar su cobertura de escenarios automatizados a partir de nuevas interacciones. Mayor volumen no garantiza mejora: la calidad debe verificarse. Este enfoque no significa que tengamos acceso a datos reales o autorización para operar sobre ellos.

No se construirán únicamente soluciones específicas: se construirá el sistema que descubre y propone soluciones a partir del histórico del banco. La construcción interna y ejecución de agentes pertenecen a un framework propio; pueden mockearse en una primera integración, sin definir la arquitectura alrededor del mock. Las propuestas finales deben especificar árboles, agentes/equipos, skills, tools, datos, conocimiento, escenarios y evaluaciones necesarios.

El usuario pidió concretar tres contratos: evento, resultado y catálogo de capacidades. Indicó Rust como lenguaje de construcción; exploración libre mediante bases locales y desechables con datos tratados, en vez de limitar al investigador a consultas predefinidas; y versionado por nuevos artefactos inmutables con hashes y cache. Los controles específicos y la retención todavía requieren diseño. DETALLE_MOTOR_Y_DATOS.md desarrolla la propuesta técnica.

## Atención: clasificador y cuatro capas

La clasificación del motivo es una puerta de entrada, no una quinta capa de atención. Se propone usar Jev.

1. Árbol especializado por subtema: verificaciones/acciones deterministas. Un LLM de frontera lo diseña y compila mediante un proceso iterativo fuera del camino de ejecución. Si no existe árbol aplicable o no resuelve, escala.
2. Agente IA nivel 1 basado en Jev, bajo ejecución del framework propio.
3. Agente IA nivel 2 basado en LLM generativo, con capacidades de agente.
4. Humano, con contexto y acciones previas preservados.

No se han definido contratos finales, stack, umbrales ni alcance de autonomía. No confundir nivel 1 del árbol con IA nivel 1.

## Evidencia que alimenta la automejora

- Histórico recopilado del banco: contactos, PQR, eventos digitales, transacciones y entidades relacionadas, solo cuando sus campos y vínculos realmente lo permiten.
- Telemetría del servicio: mensajes, clasificación, nodos recorridos, decisiones, herramientas y resultados, escalamiento, actuación humana, resolución y recontacto.
- Evaluaciones: casos históricos, escenarios sintéticos, fallos adversariales, regresiones y comparación entre versiones.

Separar procedencia: histórico bancario, traza observada del servicio, fixture simulado, escenario generado y supuesto económico. No presentar diálogos ni tool calls simulados como registros históricos reales.

Ejemplo del usuario: un humano aplica reiteradamente una acción que termina satisfactoriamente y sin recontacto por el mismo tema; ese patrón podría incorporarse al árbol o a una capacidad más económica. Es una idea de detección, no un hallazgo confirmado. Definir elegibilidad, ventana de seguimiento y casos comparables; cierre o ausencia de recontacto no prueban causalidad.

## Evaluación y entrega progresiva: objetivos expresados

Generar casos de uso, escenarios y flujos desde contactos pasados con tratamiento adecuado de datos. Aumentar datos de evaluación y usar agentes adversariales que simulen clientes. Probar propuestas con tests y plantear canary/porcentajes graduales de usuarios.

La arquitectura contempla canary y tráfico real del servicio. Su ejecución requiere autorización y políticas; no están autorizados por estas conversaciones de diseño. Una validación inicial puede reproducirse/simularse y debe reportarse como tal. No usar casos reservados para construir ni iterar el candidato.

## Jev: documentación consultada, no integración realizada

Jev es un modelo de decisiones estructuradas, no un LLM generativo o agente autónomo. Recibe state y preguntas tipadas. Choice elige entre opciones y entrega probabilidades/confidence; Score evalúa una rúbrica y entrega probabilidades/confidence; Noul devuelve probabilidad de una condición y no tiene confidence separado. Preguntas de una misma petición se evalúan independientemente; una dependencia real requiere otra petición.

Aplicación propuesta: el framework compone decisiones de Jev, ejecuta herramientas autorizadas y actualiza estado. Las respuestas al cliente pueden ser plantillas; generación libre se reservaría a otra capacidad explícita. Cálculos, fechas, permisos y ejecución pertenecen al código. Confidence no equivale a exactitud empírica ni autorización. Evaluar español y portugués: la documentación indica entrenamiento principal en inglés y menor precisión en otros idiomas. Estado adversarial puede influir en respuestas; probar inyección y no delegar seguridad al modelo.

Fuentes oficiales:

- https://docs.typesafe.ai/introduction
- https://docs.typesafe.ai/introduction/coding-agents
- https://docs.typesafe.ai/introduction/quickstart
- https://docs.typesafe.ai/primitives
- https://docs.typesafe.ai/concepts/state
- https://docs.typesafe.ai/confidence
- https://docs.typesafe.ai/patterns/intent-routing
- https://docs.typesafe.ai/cookbooks/function_calling
- https://docs.typesafe.ai/model-jaggedness/jev-1.13
- https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery

## Estructura sugerida por el asistente, pendiente de acordar

Dos bucles: atención estable y evolución de candidatos versionados. Detectar dolor, brecha de cobertura, patrón reutilizable y regresión. Priorizar con evidencia y escenarios de valor/esfuerzo. Emitir un expediente de oportunidad y una propuesta evaluable para el framework. Automatizar investigación, propuestas y pruebas; graduar publicación por riesgo y calidad.

El usuario pidió revisión mediante agentes independientes para ampliar arquitectura, experiencia, flujos, comportamientos y contratos/entidades. Tres revisiones completadas se consolidan en MAPA_PRODUCTO_Y_ARQUITECTURA.md: expediente persistente, colaboración, agenda de exploración, catálogo/grafo de impacto, evaluación y operación diferenciadas. Es una propuesta del asistente, no decisiones aprobadas ni implementación. La versión actual de ARQUITECTURA_PULSO.md recoge esa consolidación y separa lifecycle de evidencia, dependencias y estado de jobs.

El usuario pidió bajar a especificación E2E técnica, ampliar focos de arquitectura/ingeniería/producto y revisar iterativamente mediante agentes adversariales. SPEC_DETECCION_AUTOMEJORA.md es la propuesta técnica vigente de contratos/flujos/ejecución; ESCENARIOS_VALIDACION_PULSO.md define aceptación pendiente de implementar y REVISIONES_SPEC_PULSO.md registra revisiones de diseño. No son código, resultados de tests, aprobación de contratos ni autorización bancaria.

## Persistencia Nexus

El usuario registró factored/pulso, raíz D:\.codex\factored. Registro confirmado con nexus project list el 2026-09-29. Se emitió un checkpoint del alcance confirmado mediante el CLI, con estado queued y receipt 01M3PPVSQFXYDRT9SAXNKNYY1Z en el outbox del workspace. Queued significa pendiente de importación, no memoria canónica reconciliada. No se ejecutó nexus reconcile ni se editaron archivos del vault.

La propuesta técnica inicial está en DETECCION_Y_EVOLUCION.md. Sus decisiones no están aprobadas todavía.
