# Pulso: arquitectura de alto nivel

Fecha: 2026-09-29. Estado: diseño propuesto, no implementado. Enfoque actual: sistema real del banco e histórico recopilado, no arquitectura limitada a hackathon. El usuario aprobó el enfoque general de DETECCION_Y_EVOLUCION.md e indicó Rust y exploración en bases locales desechables. DETALLE_MOTOR_Y_DATOS.md concreta el motor híbrido, sandbox y almacenamiento; campos y umbrales siguen pendientes.

SPEC_DETECCION_AUTOMEJORA.md concreta la versión vigente propuesta de contratos/ejecución, incluidos estados, detector registry, particiones, autoridad, recovery y operaciones externas. Este documento sigue como mapa lógico, no contrato de implementación alternativo. ESCENARIOS_VALIDACION_PULSO.md y REVISIONES_SPEC_PULSO.md contienen aceptación y revisión de diseño, no tests ejecutados.

## 1. Fronteras

Tres módulos lógicos: Atención (framework propio; adaptador intercambiable), Inteligencia y Evolución (núcleo), Control y Colaboración (capacidades, políticas, evaluación, tareas/decisiones humanas y releases). No requieren tres servicios desplegados. Base propuesta: aplicación modular Rust y workers aislados; no microservicios obligatorios ni event streaming obligatorio. Simular un adaptador es una fase de integración, no la definición de producto. MAPA_PRODUCTO_Y_ARQUITECTURA.md amplía la experiencia, agenda autónoma, contratos de colaboración y operación; es propuesta pendiente de aprobación.

Atención ejecuta capacidad estable: clasificador -> árbol determinista -> IA nivel 1 con Jev -> IA nivel 2 con LLM -> humano. Conserva historial y emite eventos. Evolución detecta e investiga oportunidades y propone cambios; no ejecuta tools bancarias ni modifica capacidad activa. Control autoriza pruebas/promociones según políticas y registra decisiones. No todo escalamiento requiere recorrer cada capa si hay una restricción explícita de seguridad.

## 2. Componentes y propietarios

1. Adaptadores de dataset/trazas/evaluaciones: lectura e ingesta idempotente. Conservar fuente y versión. Datos no confiables no son instrucciones.
2. Normalizador y vinculador: eventos canónicos y candidatos de episodio; unión exacta o inferida etiquetada, revisión versionada.
3. Proyector de episodios y resultados: vistas derivadas reconstruibles, ventanas de observación y madurez de outcomes.
4. Motor de señales: consultas reproducibles, cohortes, recurrencia, escalamiento, cobertura y regresiones. Operación por lotes inicialmente.
5. Investigador: expedientes acotados, búsquedas autorizadas de evidencia, hipótesis, contraejemplos y límites; salidas estructuradas.
6. Planificador: consulta catálogo y políticas, recomienda el cambio mínimo y dependencias. Distingue causa bancaria de capacidad de soporte: explicar un error no repara el core bancario.
7. Constructor de propuestas: describe artefactos y suite; entrega al adaptador del framework. Construcción real de agentes fuera de alcance; conservar un seam ejecutable para evaluación.
8. Laboratorio: escenarios, cliente adversarial, entorno controlado, candidato/baseline y evaluadores independientes.
9. Registro y controlador de promoción: capacidades versionadas, resultados de gates, aprobación y despliegue gradual simulado.
10. API/centro de mando: vistas de oportunidades, evidencias, versiones, pruebas, propuestas y decisiones. La interfaz no reemplaza controles del backend.

## 3. Entidades y relaciones

- SourceSnapshot: fuente, periodo, versión de esquema, procedencia y referencias de registros.
- ServiceEvent: evento ocurrido, timestamp de ingesta, interacción, actor/capa, capacidad y versión, payload tipado y referencia de evidencia.
- Interaction: sesión, canal y clasificación versionada.
- Episode: problema relacionado entre interacciones; linkage_method, evidencia de unión y versión. Episodio desconocido es válido.
- OutcomeObservation: dimensión, valor/unknown, método, evidencia, fecha, ventana de seguimiento y censura. Separar ejecución técnica, objetivo del caso, valoración y recontacto.
- TopicVersion: vocabulario, jerarquía, vigencia; etiquetas nuevas son provisionales.
- CapabilityVersion: árbol/agente/equipo/skill/clasificador/conocimiento/tool-contract; versión inmutable, entradas/salidas, elegibilidad, permisos requeridos y dependencias fijadas.
- PolicyVersion: acciones permitidas, aprobaciones, límites de costo/rondas y reglas de promoción.
- Signal: detector/version, población, ventana, numerador/denominador, comparador, data_quality y evidencia.
- Opportunity: identidad estable de un expediente; agrupa señales, investigaciones y alternativas. Evidencia, hipótesis, prioridad y decisiones separadas. Evolución es propietario del contenido analítico; Control coordina colaboración/autorizaciones. Su proyección integra ambos sin reescribir artefactos pasados.
- Investigation: hipótesis soportadas/refutadas/no determinadas, consultas y contraejemplos.
- ImprovementProposal: cambio, destino, artefactos, requisitos, valor por escenarios, riesgos y fuentes.
- ScenarioFamily/ScenarioCase: familia, caso base, variaciones, procedencia, partición y oráculo esperado.
- EvaluationRun: candidato/baseline, suite, fixtures, políticas, modelos y seeds cuando estén disponibles; métricas y casos fallidos. No prometer determinismo de proveedores remotos.
- Release: versión destino, alcance y despliegue con reglas de parada.
- PromotionDecision: actor autorizado, evidencia, versión de política, decisión y razón.

Relaciones principales: SourceSnapshot -> ServiceEvents -> Interactions -> Episode -> OutcomeObservations; Signals -> Opportunity -> Investigations -> Proposals -> Candidate CapabilityVersions -> EvaluationRuns -> PromotionDecisions -> Releases. Las capacidades del release generan nuevas trazas. Cada paso referencia entradas exactas, no solo narrativa.

## 4. Contratos principales

Campos propuestos, independientes del transporte. No todos existen en el dataset: adaptadores deben declarar ausencias.

### EventEnvelope

```text
event_id, schema_version, event_type, occurred_at, ingested_at
interaction_id?, customer_ref?, episode_id?
actor_kind, service_layer?, capability_version_id?
source_kind, source_snapshot_id, source_record_ref
trace_id?, causation_id?, payload, data_quality
```

Tipos mínimos: contact.started, intent.classified, tree.node_evaluated, tool.completed, handoff.requested, response.sent, outcome.observed. Dataset puede producir observaciones históricas sin inventar transiciones de árbol o herramientas. Ingesta deduplica por identidad de fuente; correcciones conservan versiones. pseudonimización de customer_ref no elimina por sí sola riesgos de privacidad.

### EvidenceBundle

```text
bundle_id, snapshot_ids, cohort_definition, time_window
metrics[{name, numerator, denominator, unit, query_ref}]
examples[], counterexamples[], linkage_quality
limitations[], observation_maturity, provenance
```

Cada afirmación apunta a evidencia. Diferenciar métrica calculada, etiqueta inferida e hipótesis. El investigador puede generar y ejecutar SQL libre en un snapshot tratado, autorizado y aislado con espacio temporal de derivación; no consulta producción ni recibe sus credenciales. La frontera de seguridad es el laboratorio y su broker, no un catálogo de consultas predefinidas.

### ImprovementProposal

```text
proposal_id, opportunity_id, evidence_bundle_ids
baseline_capability_version_ids, target_layer
change_type, eligibility, exclusions, proposed_artifacts
required_tools, required_data, required_permissions
scenario_suite_ref, expected_effects, value_assumptions
risks, unresolved_dependencies, rollback_conditions
```

No declara disponibilidad de tool o beneficio verificado si son supuestos. Árbol, agente y equipo son posibles salidas; no obligatorias. Beneficio de bajar capa usa población elegible y diferencia de costo. Evitar doble conteo entre ahorro de atención/recontacto y reportar incertidumbre.

### RuntimeAdapter (framework propio)

```text
describe_capabilities(scope) -> CapabilitySnapshot
prepare_candidate(proposal) -> CandidateRef | DependencyBlock
run_case(candidate_ref, scenario_ref, environment_ref) -> RunResult
activate_release(release_ref, authorization_ref) -> ActivationResult
```

RunResult incluye eventos, tool calls, salida, estado del entorno, costo/latencia, escalamiento y error. Es un puerto: mock inicial y framework real después. Evaluador ve comportamiento y efectos, no necesita comprender la construcción del agente. El mock no debe decidir que el candidato es exitoso por definición ni beneficiarlo alterando fixtures.

### EvaluationReport / PromotionDecision

Reporte fija candidate y baseline, suite/env/policy versions, particiones, métricas por cohortes, fallos, seguridad, incertidumbre y alcance real/simulado. Gate determinista devuelve pass/fail/inconclusive. El generador no se autoaprueba. Seguridad es un bloqueo, no un promedio compensable con claridad o costo. Autorización de release se valida por backend; propuesta de publicar no es permiso de publicación.

## 5. Flujos

### A. Dataset a oportunidad

Ingesta -> normalización -> métricas/episodios elegibles -> señal -> deduplicación -> investigación -> consulta de catálogo -> propuesta. Posibles finales: descartar, evidencias insuficientes, no automatizable, dependencia pendiente o candidata a evaluación. Temas concretos se seleccionan por evidencia disponible, no se inventan.

### B. Resolución humana a automatización

Trazas -> secuencias comparables -> patrón de precondiciones/acciones/resultados -> contraejemplos -> contraste con permisos -> propuesta de bajar a árbol/IA1. Si hay juicio difícil o riesgo, conservar escalamiento o proponer mejora parcial. Dataset por sí solo no prueba qué acción ejecutó un asesor si no hay detalle; usar trazas simuladas identificadas.

### C. Fallo a mejora

Evaluación/traza -> caso fallido -> análisis de tipo de fallo (clasificación, herramienta, fuente, decisión o respuesta) -> nueva prueba -> propuesta localizada -> comparación con baseline y regresiones -> aprobación/rechazo. Retener errores y propuestas rechazadas para evitar ciclos repetidos.

### D. Promoción

Candidato validado -> aprobación según política -> shadow sin acciones externas -> canary por episodio estable -> activo/revertido. La arquitectura contempla operación real; pruebas iniciales pueden ser simuladas y deben etiquetarse. Outcome inmediato no sustituye recontacto maduro. Fallo crítico detiene; gates y umbrales definidos antes del run. Ninguna ejecución bancaria real está autorizada por este diseño.

## 6. Estados y consistencia

Separar lifecycle y dimensiones: oportunidad (open/archived/merged, con disposición y razón), propuesta (draft/evaluating/evaluated/withdrawn), release (shadow/canary/active/paused/rolled_back). Evidencia soportada/insuficiente, dependencias, resultado pass/fail/inconclusive, asignación y actualidad no son estados del mismo enum. Autorización se registra como decisión sobre versiones exactas. Rechazar candidato no descarta el problema. Fallo técnico del job no equivale a rechazo de negocio. Detalle de la consolidación propuesta en MAPA_PRODUCTO_Y_ARQUITECTURA.md.

Jobs idempotentes, retries limitados y presupuestos. Inputs/versiones fijados por run; si cambian catálogo o política antes de promoción, revalidar. Capabilities no se modifican in-place; releases apuntan a versiones. Escritos de estado y eventos del workflow se confirman juntos o se emiten mediante outbox transaccional. Tolerar ingesta repetida y outcomes tardíos; reconstruir proyecciones. No prometer entrega exactly-once.

## 7. Datos, seguridad y almacenamiento

Datos fuente y artifacts/evidence bundles en archivos/almacenamiento de objetos; metadatos, relaciones, estados y resultados indexados en almacenamiento relacional. Vistas analíticas para señales. No requiere base vectorial inicialmente: agregar búsqueda semántica solo si textos y consultas lo justifican. Telemetría operacional del servicio separada de logs del motor de evolución para que reintentos del investigador no se cuenten como contactos.

Dataset aislado de trazas reales del prototipo, simulaciones y escenarios generados mediante source_kind y environment. Retención/masking/minimización antes de enviar datos a proveedores; referencias a fuentes en vez de copiar conversaciones enteras a cada artefacto. Logs no incluyen secrets. Replay no debe ejecutar tools bancarias reales. Canary no habilita permisos nuevos.

## 8. Primer corte y siguiente paso

Construir adaptadores del histórico disponible, motor híbrido, expedientes, investigación/propuesta, contratos, suites y evaluación de propuestas ejecutables en sandbox. Integrar framework de atención y core mediante puertos; simulaciones iniciales se etiquetan. La evaluación de una propuesta de agente compleja puede ser solo validación de contrato si no existe ejecutor; no presentarla como prueba de resolución.

Siguiente corte recomendado: concretar EventEnvelope, OutcomeObservation y CapabilitySnapshot y recorrer un episodio ilustrativo completo de colaboración: descubrimiento -> pregunta/objeción humana -> investigación revisada -> alternativas -> evaluación -> decisión -> seguimiento. Añadir comandos con revisión esperada y autorización, sin reemplazar los contratos fundacionales. Elegir el primer caso vertical antes de implementar el sistema integral.
