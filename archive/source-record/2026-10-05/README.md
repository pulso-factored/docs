# Pulso — índice de documentación

**Estado:** este workspace reúne specs, auditorías y bitácoras; los repositorios actuales son `pulso-factored/improvement-engine` y `pulso-factored/infra`. Para afirmar qué está implementado, verificar el `main` vigente de cada repo; los documentos históricos de abajo no sustituyen esa verificación.

**Entrada para ingeniería:** [Engineering reference](engineering-reference/README.md) es un nuevo manual técnico en desarrollo, separado del paquete para jueces. Su primera slice describe frontera de producto y runtime con un snapshot explícito; todavía es un borrador de workspace, no documentación publicada en el repo del motor.

## Especificación canónica

- [Tech spec V3](TECH_SPEC_PULSO_AUTOMEJORA_V3.md): fuente vigente del comportamiento y arquitectura objetivo del motor. No demuestra por sí sola que cada capacidad esté implementada.
- [Bitácora Pulso](BITACORA_PULSO.md): registro cronológico del trabajo material, decisiones y verificaciones; no sustituye la especificación ni una inspección del código.

## Contexto y auditorías históricas

- [Auditoría navegada del producto](AUDITORIA_NAVEGADA_PRODUCTO.md): recorrido publicado por ocho grupos, interacciones representativas, defectos de fixture y contraste bidireccional con V2. Dictámenes independientes backend/frontend, AI/Core y data/infra enlazados en la auditoría; no certifica runtime ni todos los controles externos.

- [Alineación con producto y diseños](ANALISIS_PRODUCTO_DESIGN.md): seis HTML/52 boards y PDF21, cuatro rondas independientes, mapa por secciones y contratos producto V2; cierre documental con limitaciones de ejecución visual explícitas.

- [Actualización E0 0.5.1](REVISION_E0_0_5_1_2026-10-01.md): schema/políticas/identidad nuevos respecto al spec previo; auditoría física local y cambios de adapter/oracle/plan.

- [Revisión de organización](REVISION_ORGANIZACION_IMPLEMENTACION_PULSO_2026-10-01.md): dos iteraciones independientes del plan; features/HU/UC → DAG → hitos, con validación de dependencias y disciplina TDD.

- Plan de construcción: [V2 §30](TECH_SPEC_PULSO_AUTOMEJORA_V2.md#30-plan-de-construcción-paralela-cortes-verticales-tdd-e-integración) organiza P0–P5, paquetes paralelos, integrador independiente, TDD vertical y gates adversariales; pendiente aprobación, no implementación iniciada.

- [Auditoría preimplementación](AUDITORIA_PREIMPLEMENTACION_PULSO_2026-10-01.md): nueva revisión de garantías distribuidas, evaluación, persistencia y bootstrap; complementa el cierre documental anterior.

- [Auditoría final del spec](REVISION_FINAL_SPEC_PULSO_2026-10-01.md): revisión global independiente y comprobación estructural; cierre documental, no tests de implementación.

- Automejora sobre Agent Core: V2 §29 compone flujos/reglas, juicios Jev con DecisionModelDef y nodos agent sólo para razonamiento abierto; no un agente por etapa. Control plane Rust y outputs derivados de E0. Pin `53e729d`; divergencias de VERSION, transferencia y dos EvalSuite documentadas.

- Histórico enriquecido E0: V2 §28 incorpora `pulso_muestra_e0` como fuente complementaria de primera clase y campañas congeladas/continuas del mismo motor; labels y señales precalculadas quedan aislados del descubrimiento.

- [Tech spec V2](TECH_SPEC_PULSO_AUTOMEJORA_V2.md): contrato técnico **propuesto para aprobación** del motor de detección y automejora. No afirma software implementado. La sección 26 define cómo documentaremos arquitectura, flujos, contratos, operación, decisiones y pruebas cuando comience la construcción.
- [Bitácora Pulso](BITACORA_PULSO.md): registro cronológico de trabajo material y decisiones desde el 30-09-2026. No sustituye el spec ni una documentación de implementación actualizada.
- [Contratos y alineación Agent Core](AGENT_CORE_CONTRATOS_Y_ALINEACION.md): referencia upstream fijada en SHA `53e729d`, contrato `0.5.0`; API, lifecycle, artefactos, errores y límites del mock. V2 §§17/24/27/29 define su aplicación al motor.
- [Auditoría de integración](REVISION_AGENT_CORE_2026-09-30.md): rondas independientes y adversariales, hallazgos resueltos y límites de verificación; no prueba integración ejecutada.

## Antecedentes, no contrato vigente

- [Tech spec V1](TECH_SPEC_PULSO_AUTOMEJORA_V1.md): versión sustituida por V2 en decisiones de implementación.
- [Revisiones adversariales](REVISIONES_SPEC_PULSO.md): evidencia histórica de las rondas de revisión de specs anteriores; no es bitácora continua ni validación de código.
- Los demás documentos de esta carpeta son exploración de producto, arquitectura y escenarios previos. Pueden aportar contexto, pero una afirmación que discrepe de V2 requiere nueva decisión explícita antes de implementarse.

## Regla de mantenimiento

Una vez aprobada V2 y creados los repos, el código, las migraciones, los contratos versionados y las pruebas verifican el comportamiento real. La documentación técnica explica ese estado actual; los ADR registran el porqué; la bitácora conserva la historia. Cada PR debe actualizar los documentos afectados y registrar qué se comprobó realmente. No se guardan CSV bancarios, PII ni secretos en esta documentación.
