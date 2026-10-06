# Pulso — especificación técnica E2E de detección y automejora

Fecha: 2026-09-29. Revisión de diseño: dos rondas adversariales corregidas y tercera comprobación dirigida completada por tres revisores independientes. No identificaron P1 residuales en los focos revisados que impidan el primer corte con fixtures; esto no certifica completitud ni seguridad productiva. Estado: propuesta técnica consolidada; no código implementado ni pruebas ejecutadas. Describe un sistema real de banco, sin implicar acceso a sus datos ni autorización para operar. Los ejemplos son ilustrativos, no hallazgos. ESCENARIOS_VALIDACION_PULSO.md especifica aceptación; REVISIONES_SPEC_PULSO.md registra revisión de diseño.

## 0. Alcance, precedencia y criterios

CONTEXTO_PULSO.md conserva las premisas confirmadas. Este spec concreta MAPA_PRODUCTO_Y_ARQUITECTURA.md, ARQUITECTURA_PULSO.md y DETALLE_MOTOR_Y_DATOS.md; sustituye sus estados ambiguos y agrega contratos de ejecución. Sus recomendaciones no son decisiones del usuario. No redefine el framework interno de atención ni implementa el builder de agentes.

Resultado esperado del núcleo: detectar un problema relevante, construir evidencia contrastable, comparar intervenciones, producir una especificación de cambio y pruebas, evaluar mediante el framework y avanzar bajo política, conservando colaboración y feedback posterior.

No existe garantía de mejora por volumen ni monotónica. Una salida válida puede ser no cambiar, insuficiencia de evidencia, mantener humano o asignar a otro equipo. El sistema no transforma una coincidencia histórica en causa ni una tool inexistente en dependencia satisfecha.

Convenciones: tiempos UTC con zona original cuando importa; happened_at separado de ingested_at; duraciones en ms internos y unidades claras en UI; importes exactos con currency, fuente/fecha FX para comparación USD, sin convertir en origen ni inventar tasas; tasas con numerador/denominador y unidad. Todos los registros tienen tenant/scope, schema_version y procedencia según clase.

## 1. E2E: dos bucles y un circuito de protección

```text
Histórico + atención AI/humana + transacciones/canales + catálogo + evaluaciones
  → ingesta validada → snapshot tratado → episodios/resultados versionados
  → agenda [monitores SQL | etiquetas Jev | exploración LLM]
  → señales → expediente → investigación/contraejemplos → alternativas
  → propuesta → candidato preparado por framework → escenarios/evaluación
  → decisión autorizada → shadow/canary/activo → resultados maduros
  → nuevas señales, regresiones, suites y propuestas

Usuario ↔ expediente/copiloto/comparador/laboratorio/catálogo/trazas
          consultas → evidencia existente
          comandos → revisión/work item/job/decisión explícita

Incidente crítico → contención determinista autorizada → investigación posterior
```

El bucle de atención usa versiones estables, no la última propuesta del investigador. El bucle de evolución no accede a acciones bancarias reales. El circuito de protección no espera inferencias del LLM. Estos son límites lógicos; no exigen microservicios separados.

## 2. Módulos y puertos de implementación

Propuesta: monolito modular Rust para control/API y workers por proceso para análisis y pruebas. Un controlador escritor activo sobre SQLite local para metadata inicial; workers acceden por puertos del controlador, no abren el archivo desde múltiples hosts. DuckDB por workspace, blobs y Parquet. SQLite no será almacenamiento compartido en filesystem de red ni un motor de escritura ilimitada: medir colas/commit latency/lock waits y pasar a adaptador relacional servidor si la topología o throughput lo exige. No ejecutar DuckDB dentro del proceso privilegiado de API. DeploymentProfile fija entorno, escritor, stores y launchers; no prometer HA por tener workers.

| Módulo lógico | Responsabilidad | Puerto externo |
|---|---|---|
| ingestion | Normalización, identidad de fuente, calidad y correcciones | HistoricalSource / TraceSource / ContextSource |
| evidence | Snapshots, treatment, episodios, outcomes, partitions | DataBroker / ArtifactStore / PartitionBroker |
| discovery | Agenda, monitores, etiquetas, research y agrupación | QuerySandbox / SemanticDecider / GenerativeModel |
| opportunities | Expediente, claims, alternativas e investigación | MetadataStore / DomainEventOutbox |
| capability_catalog | Versiones, dependencias, cobertura e impacto | CapabilityRegistry / FrameworkAdapter |
| evaluation | Suites, fixtures, ejecuciones y reportes | EvaluationRuntime / Oracle / SemanticJudge |
| governance | Políticas, permisos, gates y autorizaciones | IdentityPolicy / PromotionController |
| operations | Estado de efectos externos, releases y protección | RuntimeAdapter / RoutingControl |
| product_api | Comandos, read models y progreso | UI/copiloto/observabilidad |

No convertir cada módulo en crate/servicio obligatoriamente. Dominio sin HTTP/model SDK/SQL; adapters traducen protocolos a tipos internos. El modelo no escribe metadata ni publica artefactos sin validación del controlador.

## 3. Fronteras de datos y entidades fundacionales

### 3.1 ServiceEvent

```text
event_id, source_identity {system, record_id, revision}, schema_version
tenant_id, access_scope, source_kind, environment
happened_at, ingested_at, source_snapshot_ref
interaction_ref?, subject_ref?, episode_ref?, trace_ref?, causation_ref?
actor {kind, pseudonymous_ref?}, layer?, capability_ref?
payload: EventPayload, evidence_refs[], quality_flags[]
```

EventPayload variantes: ContactStarted, MessageObserved, IntentAssigned, TreeNodeEvaluated, ToolInvoked/Completed, HandoffRequested/Completed, ResponseSent, HumanActionObserved, OutcomeObserved, EvaluationFailure. Identificadores de tool invocación emparejan inicio/fin; error tipado y estado desconocido no equivalen a éxito. Contacto/transaction/PQR históricos se traducen solo a observaciones realmente presentes; no fabricar nodos ni tool calls. Corregir conserva identidad/revisiones y supersedes_ref.

### 3.2 EpisodeRevision y OutcomeObservation

```text
episode_id, revision, subject_scope, interaction_refs[], related_fact_refs[]
issue_identity?, linkage {exact|inferred|unlinked, method_ref, evidence_refs}
time_window, topic_assignments[], source_versions[], limitations[]

outcome_id, episode_ref, dimension, value: known|unknown
verification {method_ref, oracle_ref?, evidence_refs}
observed_at, followup {start,end,coverage,maturity,censor_reason?}
source_kind, environment, supersedes_ref?
```

Dimensiones separadas: ejecución técnica, objetivo del cliente verificado, cierre administrativo, satisfacción reportada, recontacto relacionado y costo observado. No inferir una de otra. Recontacto ausente solo es evaluable con ventana y cobertura suficientes; no contacto capturado puede ser censura. Un episodio puede contener varios productos/temas; vincular solo por cliente+proximidad no confirma mismo problema. Eventos digitales y transacciones son hechos relacionados, no causas por defecto.

EpisodeMembership conserva por relación interaction/event_ref, method_ref, evidence_refs, certainty_class, topic_revision y linkage_policy_version. La etiqueta resumida del episodio no oculta una mezcla de relaciones exactas e inferidas. Detectores declaran clases admitidas y análisis de sensibilidad; llave exacta prueba vínculo de registro, no causa.

### 3.3 CapabilitySnapshot

```text
snapshot_id, payload_hash, captured_at, scope
capabilities[{logical_id,version_hash,kind,status,owner_ref,
  input_schema_ref,output_schema_ref,eligibility_ref,exclusions_ref,
  dependency_refs,required_permissions,effect_class,coverage_refs}]
policy_refs[], taxonomy_refs[], framework_contract_version
```

Kinds: classifier, tree, agent, team, skill, knowledge, tool_contract. Separar existe/declarada, ejecutable/atestada, probada y observada. Una tool declarada en un mock no está disponible en banco. Tools incluyen errores, side effects, permisos, idempotencia y recuperación. Conocimiento incluye fuente/vigencia/ámbito; skill define procedimiento y dependencias; equipos incluyen delegación/handoff. Un CapabilityVersion no sustituye la implementación interna del framework.

## 4. Artefactos, referencias y persistencia

ArtifactRef = logical_id + revision + payload_hash + kind + schema_version. IDs tipados diferenciados de hashes. Manifiestos JSON canónico (perfil JCS/RFC 8785 propuesto); importes decimales/IDs grandes como strings tipados y normalización de dominio antes de canonicalizar. No prometer que ordenar claves arbitrariamente equivale a JCS. YAML opcional como autoría, validado y compilado antes de hashing. Artefactos: snapshots, query receipts, etiquetas, evidence bundles, research reports, proposals, suites, candidates, eval reports y policy decisions. Grandes datos en Parquet/blob, no JSON por registro.

ArtifactManifest incluye parent_refs, input_refs, producer_version, policy_refs, partition/lineage, data_classification y retention_ref. Persistir blob temporal, verificar hash, publicar create-only; después commit de metadata + evento + outbox en una transacción local. Fallo antes del commit deja huérfano recuperable, no un ref público a contenido parcial. Mantenimiento distingue unreferenced de evidencia referenciada y aplica retención; no delete genérico.

Restricciones de todas las entradas se propagan a derivados, query receipts, exports, resúmenes y caches. Join/agregación no rebajan clasificación/partición automáticamente; una desclasificación exige política/autoridad específica y auditada. Broker verifica pertenencia real de archivos/datos al scope, no solo la etiqueta declarada por quien solicita. Acceso por principal+propósito+partición además de tenant. Reportes finales muestran solo feedback permitido: detalle reservado no vuelve al contexto de construcción mediante un resumen o copiloto.

Tablas iniciales propuestas: source_cursors, event_revisions, artifact_refs, episode_heads, missions, jobs, job_steps, budget_reservations, opportunities, opportunity_links, claims, proposal_heads, capability_heads, dependency_edges, work_items, decision_records, runtime_operations, releases, domain_events, outbox, projection_offsets. Payloads grandes fuera; indexar tenant/id/revision, fuentes, relaciones y lifecycle. No cada claim exige blob independiente: puede formar parte de un EvidenceBundle versionado.

Proyecciones mutables con head_revision y eventos reconstruibles; artifacts/eval pasados no se editan. Hash no concede autoridad, evita borrado ni anonimiza. Revocación y retención invalidan acceso/caches aunque exista hash. Tombstone no sensible indica evidencia no disponible; replay puede dejar de ser posible.

## 5. Flujo F01 — fuentes a snapshot y resultados

Disparador: lote/CDC/traza, llegada tardía o corrección. HistoricalSource entrega registros/cursor/esquema; TraceSource entrega eventos de atención; ContextSource aporta incidentes/campañas/políticas con procedencia, nunca verdad implícita.

1. Rust valida esquema/identidad/scope/timestamps/unidades. Unknown permitido donde contrato lo admite; dato inválido a cuarentena con motivo, no desaparece ni se convierte en cero.
2. SourceRecordVersion fija source_id/record_id/source_revision/content_hash/change_kind/supersedes_ref. Misma identidad/revisión/hash es duplicado; misma identidad/revisión y distinto hash es SourceRevisionConflict y cuarentena, no última escritura gana. Confirmar cursor después del commit durable; entrega repetida no duplica contacto. Corrección crea revisión y dependencias afectadas.
3. DataBroker verifica propósito/autorización y aplica tratamiento. IDs pseudónimos consistentes dentro del scope permiten joins; mapa de reversión nunca en sandbox/modelo. Texto se minimiza/redacta conforme a política. Pseudonimización no es anonimización irreversible.
4. SnapshotResolutionSpec fija as_of de ingesta, fecha de negocio, regla de precedencia de revisión de cada fuente, tombstones y esquema. Materializar vista resolved_as_of con una versión elegida por identidad lógica; historial de revisiones queda aparte. Fuente sin revisiones ordenables necesita adaptación explícita, no ordenar arbitrariamente por llegada. SourceSnapshot registra resolución, cobertura, diccionario, checks, watermark por fuente y conteos incluidos/excluidos/cuarentena/unknown. Corrección retroactiva afecta nuevo snapshot, no el anterior.
5. Proyector deriva interacciones/episodios/outcomes con reglas versionadas. Exact links primero; inferred links conservan método/evidencia/ambigüedad. Revisión de unión no altera un run anterior.
6. Emite SnapshotAvailable / OutcomesMatured / SourceCorrected. Agenda decide nuevos trabajos; artefactos afectados quedan stale por causa, no borrados.

Resultado: snapshot autorizado, resultado de calidad y vistas con procedencia. Si falta texto, no ejecutar clasificador semántico sobre texto inventado. Si faltan tool traces, no atribuir una resolución a una acción concreta.

## 6. Flujo F02 — agenda y detección híbrida

ExplorationMission: mission_id, objective, authorized_scope, source/capability_refs, trigger_policy, cadence, priority, budget, autonomy_policy_ref, stop_conditions. Configuración por roles autorizados; el motor corre sin un botón por investigación. Una misión puede descubrir temas nuevos y no estar atada a un único motivo.

Scheduler Rust crea run con entradas fijadas por SnapshotAvailable/OutcomesMatured/CapabilityChanged/EvaluationFailed/UserResearchRequested/agenda. Coalesce triggers repetidos; reservar presupuesto antes de dispatch. JobKey incluye mission/version, trigger identity, input hashes y purpose. Corrección nueva no colisiona con run anterior. Reservar parte del presupuesto para exploración nueva y limitar reanálisis sin novedad.

### Carril numérico

DetectorSpec: objective, measurement_unit, unit_key, eligible_universe_ref/sql, eligibility_sql, numerator_sql, denominator_sql, comparator_sql, join_assertions, coverage_assertions, aggregation_semantics, allowed_linkage_classes, time/cohort definitions, minimum_support_policy, statistic/multiple_search_policy, output_schema y versions. SQL verificado en sandbox. Monitores iniciales: recontacto, escalamiento evitable candidato, fallo tool/canal, espera/SLA disponible, conocimiento/cobertura faltante y regresión. NPS/CSAT solo si pregunta/escala/muestra están definidas; no son etiquetas de sentimiento Jev.

Construir primero universo único al grano declarado (contacto/episodio/cliente/transacción/etc.), probar unicidad y cardinalidades de joins, derivar indicadores por unidad o pesos declarados y calcular tasas. Cada métrica incluye target_population_count/unknown, observed/eligible/evaluable_units, excluded_by_reason, unknown_outcomes y source_coverage. No ocultar cuarentena en denominador reducido; declarar «entre evaluables» cuando corresponda.

Rust verifica estructura, cardinalidades/assertions computables, unidades y temporalidad; QueryReceipt demuestra ejecución, no semántica correcta del negocio. Semántica se prueba con fixtures/oráculos del detector y contraste independiente, con revisión cuando riesgo lo exige. Estadísticas/modelos solo con método declarado. Comparación ajusta mezcla de casos/estacionalidad cuando hay soporte. Tamaño insuficiente, cambios de captura o cobertura incompleta producen evidence_insufficient, no anomalía confirmada. Monitores parametrizados por política: no valores mágicos aprobados aquí.

### Carril semántico

Jev etiqueta decisiones cerradas sobre material tratado: motivo en taxonomía con unknown, acción mencionada dentro de opciones conocidas, solicitud de aclaración, contradicción puntual. SemanticAnnotation es inferred_semantic; guarda state hash, preguntas/versiones, modelo/config, answers/probabilities y confidence donde existe, evidence_locators y selection_method (preprocesador/otro componente/ausente). Locators son IDs/offsets del material tratado exacto y Rust comprueba existencia; no atribuir generación de citas verificables al protocolo Jev. Acción mencionada/hipotética/negada no prueba tool ejecutada. Etiqueta sin soporte verificable sirve para investigar, no para probar ejecución. No modifica el evento fuente; confidence no es probabilidad empírica de acierto.

### Carril exploratorio

LLM recibe objetivo, snapshot/diccionario autorizado y capacidad vigente. Formula preguntas, explora SQL libre y propone hipótesis/cohortes no previstas. No puede declarar valores que no salen de QueryReceipts. El controlador valida salida estructurada y límites; inferencia libre no tiene permisos libres.

Los tres carriles emiten SignalCandidate: population_ref, window, metric/evidence refs, detector/model lineage, comparators, quality/limitations, novelty y provisional topic. Candidato semántico sin métrica puede abrir investigación, pero no ranking cuantitativo inventado. Cambio que es data-quality se enruta como tal, no causa bancaria.

## 7. Flujo F03 — sandbox e investigación abierta

ExplorationWorkspace: purpose, access_scope, partition_scope, snapshot_manifest_hash, treatment_version, schema/dictionary, expiry, resource_budget, engine_version y egress_policy. El launcher precarga snapshot tratado; worker no privilegiado sin red/credenciales ni host filesystem, input protegido y espacio de derivación escribible. Configuración/extensiones aprobadas fijadas por launcher. SQL no confiable exige aislamiento OS además de settings de DuckDB; no defensa regex ni prompt.

Puertos genéricos: describe_schema, execute_sql, inspect_result, export_evidence. Son capacidades de laboratorio, no recetas de negocio. Permiten joins/CTE/features/tablas derivadas. QueryRequest lleva SQL/params, workspace/run/step refs, workspace_state_revision/derivation_manifest_digest, timeout y límite de salida. QueryReceipt devuelve status, schema, filas/bytes, result hash, exact SQL/params, input hashes/derivation state, truncation, engine version y errores. Un resultado truncado no prueba ausencia ni representa el universo completo.

Separar ReadQuery de DerivationCommand (DDL/DML/CTAS). Derivaciones publicadas registran identidad/consulta productora/dependencias/hash/revisión; scratch mutations avanzan workspace revision. Cache de lectura solo contra estado exacto; nunca cachear comando mutante como lectura. Ejecutar derivación con operation_key idempotente o en subworkspace nuevo. Antes de próximo paso fijar DerivationManifest, sin inputs mutables ocultos. Workspace perdido se reconstruye desde snapshot/manifiesto reproducible o devuelve WorkspaceUnavailable; no reanudar sobre scratch vacío. Sandbox serializa mutaciones por workspace y bloquea config/egress/extension changes no autorizados sin restringir preguntas de negocio.

El broker de modelos está fuera del worker y aplica egress antes de enviar: scope/país/proveedor/propósito, tratamiento y límites. Snapshot autorizado no implica que toda fila pueda salir a un proveedor. Agregados pequeños y joins pueden reidentificar. Se rechaza/transforma salida conforme a política; un rechazo no se evade reduciendo consultas.

Investigador LLM ejecuta rondas acotadas: plan → consulta → resultado real → hipótesis → contraste/contraejemplo → reporte. Model calls separados de query execution; Rust registra presupuestos y referencias. Una petición de datos no autorizados devuelve DependencyRequired o AccessDenied, no credentials. SQL inválido permite reparación limitada; sin evidencia suficiente termina inconcluso. Cancelación conserva lo ya autorizado y detiene efectos nuevos.

Claim: id, revision, kind {observed,inferred,hypothesis,assumption}, statement, population/window, evidence_refs, counterevidence_refs, status {supported,refuted,undetermined}, method/limitations. El reporte declara asociación vs hipótesis causal; no usa supported como sinónimo de causalidad. Investigación fija snapshots/catálogo/políticas y guarda decisiones relevantes, no chain-of-thought privado.

## 8. Flujo F04 — expediente, dedup y prioridad

Resolver posibles oportunidades existentes por tenant, problema provisional, producto/canal/población, ventanas y overlap de evidencia. Fingerprint identifica candidatos, no decide igualdad causal. Reglas exactas vinculan repetición del mismo detector/alcance; semejanza semántica sugiere agrupación mediante LLM/Jev según el juicio, sin fusionar irreversiblemente problemas distintos. Merge/split versionados preservan links y decisiones; revisión humana según ambigüedad/política.

Opportunity contiene identity/lifecycle, owner, claim_refs, signal/investigation/proposal refs, disposition y head_revision. Agrupar señales repetidas y presentar novedad: evidencia/cobertura/riesgo/decision changed. Una investigación nueva actualiza expediente por comando con expected_revision; conflicto reevalúa operación, no pisa actividad de otro usuario.

ValueScenario: horizonte, población elegible, adopción/exposición, effect assumptions, unit costs/margins, implementation/operating cost, effort/dependency/risk, fuente/fecha/unidad e incertidumbre. Rust calcula escenarios, conserva valor original y muestra USD solo con FX referenciado. Ahorro por menor costo de capa ≠ reducción de recontacto; usar baseline común y evitar solapar ahorros. Sin prevalencia/efecto conocido, mostrar rango/unknown, no precisión fingida. Priorización multidimensional y sensibilidad al supuesto dominante, no ranking universal de score.

Salida: expediente comprensible, evidencia vigente, alternativas candidatas a investigar y atención humana solo si aporta valor. Beneficio previsto no se aprende como beneficio realizado.

## 9. Flujo F05 — alternativas a propuesta y candidato

Planner LLM combina investigación con CapabilitySnapshot, políticas y constraints. Propone cambio mínimo: classifier question, árbol, conocimiento, skill, agente, equipo, test/detector, o intervención externa. Si un procedimiento humano parece transferible, reconstruye precondiciones, acciones, objetivo verificado y excepciones. Nunca copia una tool peligrosa porque fue frecuente.

ImprovementProposalRevision fija opportunity/evidence/baseline refs; intent/change_type; eligibility/exclusions; CapabilityDelta; dependencies; escenarios de valor/esfuerzo; riesgos; suite plan; stop/rollback conditions. CapabilityDelta describe add/replace/deprecate sobre base revision con input/output/permissions/knowledge/skill/tool refs; no ejecuta parche arbitrario del modelo.

Para árbol: especificar guards, acciones tipadas, outputs verificables y handoff, incluidos missing/unknown/error. Compilador/validator Rust del framework comprueba schemas, referencias, alcance de permisos y caminos; herramienta de construcción iterativa con LLM pertenece al framework, no este núcleo. Ninguna frontera de este spec requiere generar código Rust arbitrario ni ejecutarlo en host.

ProposalBuilder valida contratos/dependencias determinísticamente; preguntas semánticas localizadas pueden usar Jev; diseño abierto usa LLM. DependencyBlock registra tool/data/permission/framework inexistente. No llenar huecos con mocks silenciosos. Edición humana o builder crea nueva revisión con autoría.

CandidateManifest: candidate_id, proposal_ref, baseline_refs, dependency_closure, behavior_spec_ref, suite_ref, permission_scope, assurance_level {spec_only,simulated_runtime,executable_runtime}, build_ref? y framework attestation? RuntimeCandidate existe cuando el adaptador entrega artefacto ejecutable/versionado y contratos comprobables. Manifest preparado no implica agente funcionando.

FrameworkAdapter puertos: describe_capabilities; prepare_candidate(proposal_ref, operation_key); get_operation(operation_id); run_case(candidate,case,env,operation_key); plan_release(candidate,scope); activate_release(plan,authorization,operation_key); get_release_state; stop/rollback_release. Respuestas tipadas ready/dependency_block/pending/failed. El timeout requiere consulta de estado; no retry ciego. Mock implementa los mismos contratos y declara environment/assurance; no premia al candidato por construcción.

## 10. Flujo F06 — escenarios, adversarios y evaluación

ScenarioFamily fija origen histórico, synthetic/controlled o usuario experto, seed/profile, lineage raíz y partición. ScenarioCase incluye preconditions, customer goal, initial environment, permitted facts, tool fixture refs, expected assertions, allowed outcomes, stop limits y provenance. Un escenario no debe filtrar al cliente adversarial el resultado esperado ni estados internos del soporte.

PartitionBroker asigna desarrollo, validación iterativa y final reservada por familias/episodios/clientes y tiempo según tarea. Evitar hermanos del mismo caso en ambos lados; documentar tradeoff de clientes que reaparecen. Descubrimiento también usa datos de confirmación separados de exploración. Generador/copiloto/investigador no reciben holdout; acceso libre SQL es libre solo dentro de partición autorizada. Reutilizar feedback detallado del final para iterar contamina el final: crear nueva suite reservada para futuras afirmaciones.

Separar principales: generador/investigador/builder sin acceso a final; runner adversarial aislado recibe solo CustomerView del caso asignado (incluido un caso reservado); evaluador/oráculo recibe expectativas/estado privado necesarios. Runner no genera ni modifica suites, no comparte memoria con construcción y su conversación reservada no se devuelve al contexto que propone cambios. Autorizar hechos visibles para ejecutar no equivale a revelar holdout a generador.

LLM genera casos/variantes y representa cliente bajo ese protocolo; controlador restringe presupuesto, turnos, estado visible y acciones. Variantes: ambigüedad, idioma, desconocido, datos faltantes, inyección, error/timeout tool, autorización ausente, exceptions y recontacto. Variaciones sintéticas no estiman frecuencia real. Humano experto puede corregir caso mediante revisión atribuida, no alterar oráculo tras ver resultado para hacerlo pasar.

EvaluationEnvironmentManifest fija tool bindings por entorno, runtime/version/attestation, principals/views, network/credentials/files permitidos, fixture inicial/reset, captura de efectos, límites y assurance. Launcher valida antes del run; sin binding se bloquea/falla explícitamente, jamás fallback a producción. Mismos límites de aislamiento/egress que investigación, adaptados al runtime y a los modelos vía broker. Copias equivalentes de objetos no sustituyen aislamiento OS/permisos de herramientas.

EvaluationPlan fija baseline/candidate, dependency hashes, suite/partition, environment/fixtures, oracle/rubric/question/model/policy versions, repetitions/seeds cuando aplique, cache policy y criterios. Baseline/candidate usan entornos inicialmente equivalentes y aislados, fixture reset por caso; evitar efectos compartidos. Repeticiones no prometen proveedor determinista.

RunResult conserva eventos, respuesta, herramientas/efectos, estado final, costo/latencia/escalamiento, error e incompletitud. Oráculos Rust verifican estado/acciones/permisos/objetivo contra fixtures; Jev puede juzgar aspectos cerrados de claridad/coherencia; LLM evaluador independiente puede criticar lenguaje/aspectos abiertos, sin anular un fallo de seguridad ni reutilizar el generador como aprobación. Un cliente que dice «gracias» no es oráculo de objetivo alcanzado.

EvaluationReport separa correctness, safety, eligibility/exceptions, escalation, coverage, cost/latency y calidad semántica por cohortes/familias, con unknown/inconclusive. Reporte determina assurance real: spec_only valida forma/dependencias, simulated_runtime comportamiento en fixtures, executable_runtime comportamiento en entorno definido; ninguno prueba impacto productivo por sí solo.

Distinguir timeout/error de tool deliberado (condición de caso evaluable cuyo escalamiento puede pasar), fallo del harness (condición no producida/resultados no observables) y outcome indeterminado del candidato. Policy decide incompletitudes bloqueantes/cobertura por caso/suite.

GateDecision Rust, sobre política fijada: identidad de candidato/ejecución comprobada; fallo crítico verificable → fail; evaluabilidad/cobertura insuficiente → inconclusive; resolución/escalamiento, cohortes/regresiones y eficiencia satisfacen márgenes declarados → pass. Seguridad no compensa con ahorro ni promedio. Umbrales/calibración pendientes, no defaults universales. El gate evalúa, no autoriza release automáticamente. Evaluar además detector: benchmark con oportunidades/negativos conocidos, false positives/duplicates/evidence fidelity, útil/no automatizable y costo por investigación, distinguiendo patrones insertados de naturales.

## 11. Flujo F07 — promociones, compatibilidad y resultados

ImpactAssessment calcula capability y data/evidence closure, consumidores, conflictos con propuestas concurrentes, población y cobertura. Corrección material/revocación de fuente propaga ApprovalUseBlocked a claims/propuestas/suites/candidatos/autorizaciones afectados. Policy determina recálculo/revalidación/rebuild. Antes de promoción comprobar versión activa/dependencias/evidencia/política/suite/permisos vigentes y gate aplicable. Cambios relevantes → CompatibilityStale y revalidación necesaria. Evaluaciones pasadas siguen válidas como historia de inputs anteriores, no como permiso sobre inputs nuevos.

PromotionAuthorization fija actor o service identity, authority/policy, candidate/eval/compatibility refs, etapa permitida, scope/exposure, expiry, reason y idempotency. Preparar, autorizar shadow, autorizar canary y autorizar activo son decisiones distintas. Una autorización puede ser automática solo si política delegó esa clase/alcance.

ReleasePlan define baseline/target, cohort eligibility, assignment version, etapa, pinned dependencies, guardrails, observation windows y rollback target. Shadow no tiene permisos de efectos bancarios; compara decisiones en replay/sandbox o entradas seguras sin efectos. Canary asignación estable por episodio/subject scope según diseño de seguimiento; hashing solo decide cohort, no privacidad. Episodio en curso pinnea versión salvo contención crítica. Cohortes/denominadores y censura explícitos.

Controller persiste RuntimeOperation antes del efecto, llama con clave idempotente y reconcilia respuesta/estado. Runtime/routing comprueba al aplicar expected_routing_generation, dependency/policy/authorization validity y fencing del efecto. Stop avanza generación e invalida activaciones previas pendientes; respuesta tardía no reactiva. Adapter declara soporte CAS/fencing; sin garantía, bloquear automatización de efectos o usar RoutingControl que sí la provea. Validar antes de RPC no cierra TOCTOU por sí solo.

ReleaseReconciliationState separa desired_plan de observed_routing_generation y scope_statuses {baseline,candidate,unknown,stopped}, exposure_refs/actual versions, operation_ref, observed_at y unresolved_effects. Receipt accepted, efecto confirmado y convergencia son distintos. Partial/unknown puede tener clientes ya expuestos: UI muestra alcance observado/posible, no «pending» vacío. Bloquear promociones solapadas incompatibles mientras unknown; permitir observación/contención compatible. Resolver requiere evidencia de runtime/routing, no flag manual sin fundamento.

Stop/rollback son nuevas operaciones/eventos; compensaciones de acciones previas solo si dominio las permite, rollback de versión no revierte automáticamente una transferencia.

OutcomeObservation posterior compara esperado/observado en ventanas maduras y exposición conocida. Shadow no prueba resolución de cliente; canary simulado no prueba causalidad bancaria. Si hay asignación apropiada/exposición completa puede habilitar estimación de efecto con método; sin ello asociación postrelease. Nuevas trazas, fallos y outcomes alimentan investigación y casos de regresión, no training automático del modelo ni self-modification en vivo.

## 12. Flujo F08 — usuario, catálogo y otras features

Queries: bandeja por rol, expediente/revisión, explain_claim, compare_proposals, eval_cases, dependency_impact, traces y release_followup. Query result lleva revision/generated_at/freshness/access restrictions. Tres operaciones de aplicación: query(view,scope,filters,revision?), submit(command), subscribe(scope,resume_after). Cursor opaco scoped a principal/propósito/autorización y secuencia durable; snapshot devuelve projection_checkpoint/cursor coherentes. Stream incluye event_id/object_revision/command_id y revalida acceso. Cursor expirado, gap o cambio de permisos → resync_required y nueva proyección autorizada; no retransmitir contenido revocado. Receipt command devuelve aceptación/operation_ref/event ref, no vista actual instantánea. UI deduplica, conserva drafts y sincroniza hasta checkpoint.

CollaborationCommand: command_id, actor, target_ref, expected_revision, action enum, typed payload, reason, evidence_refs, idempotency_key. Tenant/autoridad obtenidos de sesión/broker, no confiados desde el modelo. Namespace key = tenant/purpose/operation type/target; hash canónico del comando validado. Validate contract → verificar autoridad actual → lookup key → si ya committed devolver receipt autorizado de la operación sin reaplicar expected_revision ni reenviar efecto → si nuevo check revision/preconditions → transición + audit/outbox → ack/job/work_item. Mismo key con otro payload conflict. Revocación actual puede negar acceso al receipt/detalle sin reejecutar; no devuelve evidencia antigua. Cambios concurrentes en comando nuevo privilegiado requieren reconfirmación.

Acciones: AddComment, ContestClaim, RequestResearch, RequestAlternative, RestrictScope, AssignOwner, Prioritize, Defer, Merge/Split, ReviseProposal, RequestEvaluation, AuthorizePromotion, StopRelease. No cada comentario crea job; una objeción relevante queda vinculada al claim y genera solicitud según política. Autorizar no se deduce de texto positivo.

| Feature integral | Entrada al núcleo | Salida y comportamiento |
|---|---|---|
| Chat/atención y humano | Eventos, clasificaciones, acciones, escalamiento y outcomes | Contexto estable y nuevas versiones promovidas mediante framework |
| Constructor conversacional | Intención humana/borrador y constraints | ProposalRevision → prepare_candidate; no publicación directa |
| Oficina/ficha de agentes | Capabilities, jobs, evaluación y uso observado | Actividad real, versiones, fallos/coverage; no tasa bruta de ranking de asesores |
| Knowledge | Versión/fuente/vigencia/owner | Cambio genera impacto, claims/proposals stale y pruebas focalizadas |
| Skills | Procedimiento/contrato/dependencias | Propuesta de add/update/reuse; compatibilidad y evaluación |
| Tools | Schemas/permisos/effect/errors/disponibilidad | Planner usa solo contratos declarados; ejecución real delegada al framework |
| Observabilidad | Traces/correlations y versiones | Drilldown desde claim/caso/release, separando atención de jobs internos |
| Centro de mando | Proyecciones de oportunidades/incidentes/work items | Intervención por rol, estado de evolución/servicio y costos observados |

Copiloto LLM interpreta solicitud abierta en CommandDraft o responde usando referencias. Jev puede clasificar intención entre comandos conocidos; Rust valida campos/autoridad/alcance y exige confirmación explícita para efectos privilegiados. La confirmación puede ser conversacional si referencia inequívocamente acción/versión/alcance pendientes y satisface el mismo protocolo que un botón; seguridad en comando/política, no en widget. Texto de documentos o contactos es dato, nunca instrucción de control. Comparación/contraejemplos se muestran con historial, no reescritura silenciosa.

AuthoringSession/DraftSpec conserva autoría conversacional sin fingir capability operativa. Ciclo común catálogo: RevisionSubmitted(actor/source identity,base_ref,kind,scope,vigencia) → validación de contrato/procedencia → rechazo o CapabilityVersionRegistered → ImpactAssessment → bindings actualizados solo por decisión aplicable. Importación externa y edición humana simultáneas producen conflicto de base, no overwrite. Fuente publicada no actualiza todos los releases pinneados. Tools exigen attestation de disponibilidad aparte del schema y permisos aparte de autoría; secrets son refs protegidas, no contenido del draft.

ResponsibilityRoutingPolicy asigna a grupos responsables (servicio/canales/core/comercial/riesgo) y resuelve audiencia autorizada, fallback y vencimientos. Owner desactivado/rol vacío → unassigned/routing_failed visibles y escalación, no decisión perdida. Asignar no concede acceso; work item lleva resumen permitido y acceso a detalle independiente. Una oportunidad transversal puede tener varios responsables y una decisión con autoridad distinta.

AttentionPreference es distinta de evidencia/lifecycle: usuario/rol, alcance, razón, expiry, material-change override y critical exceptions. Defer no rechaza claim, no detiene misión ni entrena al detector por falta de clicks. ActivityView incluye estado/etapa/razón/timestamps/relaciones y acciones permitidas, accesible sin color/avatar/motion; accepted/running/blocked/unknown/confirmed nunca se confunden por animación.

HandoffContext (puerto del framework): episode/interaction refs, pinned capability/routing, motivo y layer destino, verified_facts con evidencia, preguntas ya respondidas, pendientes/runtime operation refs, actor/source provenance, audience_scope y auth_attestation_ref/expiry/applicability. Destino recibe vista autorizada; autenticación no se copia como booleano universal, sino se valida para canal/acción. Tool unknown se reconcilia antes de repetir; handoff no transfiere permisos ni promete contexto cross-channel sin vínculo/autorización. Una contención puede reencaminar episodio con motivo/historia conservados.

## 13. Flujo F09 — incidentes y salud del sistema

OperationalIncident: severity, source/guardrail, affected release/capability/dependencies, evidence, containment operation, owner, lifecycle y investigation refs. Guardrails deterministas autorizados detienen/enrutan/revierten sin LLM; fallo del modelo o broker no suspende reglas de seguridad. Si contención externa falla, marcar incident/unconfirmed y escalar, no fingir restauración.

Separar métricas de salud de atención (quality/outcomes/tools/latency/cost), evolución (ingestion lag/jobs/budgets/LLM/sandbox), calidad de detección y valor posterior. Suprimir notificación de una oportunidad no suprime incidente crítico. Eventos de incidentes generan nuevo research/regression suite con procedencia.

## 14. Matriz determinismo, Jev y LLM

| Trabajo | Ejecutor | Límite |
|---|---|---|
| Ingesta, linkage exacto, ventanas, métricas, costos, gates, permisos | Rust/SQL/reglas versionadas | No pedir aritmética/autoridad a modelo |
| Motivo conocido, tipo de acción, criterio semántico puntual | Jev Choice/Score/Noul | Unknown/abstención; no SQL, procedimientos abiertos ni validación final |
| Tema nuevo, hipótesis, SQL exploratorio, alternativas | LLM investigador/planner | Datos tratados, presupuesto, evidencia y schemas validados |
| Especificación de árbol/skill/agent | LLM diseño + compilador/framework | Ejecución determinista y acciones autorizadas; build fuera del núcleo |
| Cliente adversarial y variantes | Generador LLM y runner LLM separados | Generador sin final; runner solo CustomerView asignada, sin oráculo/estado privado ni memoria de construcción |
| Resultado del caso y seguridad | Oráculo Rust + jueces semánticos auxiliares | Texto satisfecho o juez LLM no invalida estado real |
| Autonomía/release/contención | Rust + política/autoridad | Probabilidad del modelo no es permiso |

Jev devuelve Choice/Score con probabilidades y confidence; Noul devuelve probabilidad sin confidence separado. Preguntas en la misma petición son independientes; agrupar las que comparten state y separar solo dependencia real. Adapter Rust conserva protocolo/model/version de preguntas y valida respuestas; no asumir SDK Rust nativo. Timeout/malformed → error tipado/abstención/fallback según política. Umbrales se calibran por tarea/idioma, no copiar ejemplos de documentación.

## 15. Jobs durables, budgets, caches y errores

JobRun: identity/mission/opportunity, inputs/policy, status, budget/reservations, cancel flag y parent. JobStep: type/dependencies, input refs, state, attempt, lease_owner/expiry, fencing token, output refs, errors y cost usage. Step graph acíclico; expansión dinámica crea pasos explícitos limitados, no bucle LLM invisible.

Worker reclama por CAS/transaction; heartbeat y lease. Broker/query/runtime validan lease/fencing/cancelación en cada dispatch, además de comprobar fencing al commit para que worker vencido no publique. Operation key del efecto es estable entre intentos (no incorpora fencing nuevo para fingir efecto distinto). Reanudación reutiliza outputs committed de inputs fijados; nuevo input crea run/revisión, no cambia en medio. Cancellation bloquea dispatch/commit no permitido y conserva historia. Cancellation/lease expiry no garantizan parar efecto/cobro externo ya iniciado: reconciliar operación/reserva y registrar posible costo duplicado si proveedor no ofrece idempotencia.

Retries: transitorio (red/rate limit) acotado con backoff; invalid contract/denied no retry automático; SQL/model output reparable solo rondas permitidas; domain insufficient es resultado, no excepción. External timeout: reconcile primero. Reserve budget atómico por tenant/mission/run antes del paso; charge usage reportada o estimada pendiente si desconocida, evitando overspend concurrente; límites duros de tiempo/turnos/tokens/query bytes. No refund ciego de una llamada que pudo cobrarse.

Cache key: tenant/purpose/access+partition scope, policy/version, input hashes incluyendo derivation state revision/manifest, query/params o prompt/questions, producer/engine/model/config. Revocación revalida aun en hit; sin cross-tenant ni cross-holdout. Lecturas contra revision exacta; mutaciones sin cache read. Orden y semántica SQL deterministas cuando se compara equivalencia. Evaluación registra execution_id/repetition/cache_hits; no presentar cache de reporte final como ensayo nuevo. Cache disabled/fresh cuando política exige independencia.

Error taxonomy: InvalidInput, SchemaMismatch, AccessDenied, DataQualityInsufficient, DependencyMissing, BudgetExceeded, ModelUnavailable, InvalidModelOutput, QueryRejected/Failed/TimedOut, ArtifactUnavailable, StaleRevision, CompatibilityStale, RuntimeUnknown, EvaluationInconclusive. Progreso UI diferencia no encontrado/fallido/inconcluso/cancelado/bloqueado.

## 16. Flujo F10 — automejora de detectores

No enviar detectores al framework de atención. DetectorRegistry/agenda son propietarios de este camino, compartiendo artifacts/policies/jobs/evaluación sin añadir servicio.

DetectorProposalRef → DetectorVersion (DetectorSpec + SQL/question/taxonomy/input versions, scope, output contract y budget) → DetectorEvaluationReport → MonitorRegistrationDecision → MissionMonitorBinding. DetectorVersion kind propio en registro de discovery, relacionado con catálogo mediante dependency edges, no agente disfrazado.

Preparar valida grain/join/coverage contracts, inputs, semántica sobre fixtures con patrones/negativos/correcciones, costo/missingness/estabilidad, múltiples búsquedas y contraste independiente. Evaluación del detector descubierto no usa el periodo/cohorte explorado para confirmar su hallazgo. Referencias de ground truth cuando existen; ausencia de oracle se declara y no inventa precision/recall. Detector puede quedarse experimental/inconcluso sin binding recurrente.

MonitorRegistrationDecision fija actor/policy, detector version/report, mission revision, scope/cadence/budget y expected binding revision. Registry hace CAS de binding, conserva versión anterior y emite MonitorRegistered para scheduler. No modifica por sí sola attention release. Rollback/unbind monitor detiene dispatch futuro sin borrar señales/expedientes; Jobs en curso preservan inputs originales o se cancelan según política. Outputs posteriores conservan detector version y nueva evidencia puede revelar false positives/drift, abrir revisión y pruebas, sin autohabilitar query arbitraria.

## 17. Flujo F11 — extraer procedimientos reutilizables

Entrada: episodios/trazas con acciones verificables, outcomes y seguimiento suficiente; no reconstruir actos humanos ausentes a partir de un cierre. Normalizar acciones en ActionToken {tool_contract/version, action_kind, precondition_evidence, result_category, temporal_order, actor/layer, permission_scope}. SQL ordena por tiempo/secuencia disponible y conserva ambigüedad de orden. Rust extrae secuencias/prefijos repetidos acotados por soporte/longitud/costo de búsqueda; ramas y loops no se reducen a un texto concatenado.

SemanticAnnotation Jev ayuda a agrupar menciones de procedimientos conocidos; LLM propone vocabulario nuevo o interpretación de rutas, nunca falsifica tool events. ProcedureCandidate reúne precondiciones observadas, pasos/branches, objetivos verificados, excepciones, contraejemplos y cobertura. Comparar cohortes por complejidad, producto/canal/riesgo/idioma y sensibilidad a linkage/ventana. Si faltan precondiciones, quedan RequiredEvidence y no se convierten en guard verdadera.

Planner propone automatización parcial o mejorar skill/conocimiento manteniendo juicio humano. Transfer a árbol exige guards verificables, actions autorizadas, error/unknown/handoff y suite de excepción; a IA1/Jev solo decisiones acotadas con estado/tool updates del framework; a IA2 razonamiento abierto. Frecuencia y resultado observado producen candidato a evaluación, no prueba causal ni permiso de acción. El objetivo no es bajar siempre de capa, sino mejorar resultado/costo/riesgo del episodio.

## 18. Flujo F12 — anticipación de fricción y contacto

Detección proactiva incluye oportunidades antes del contacto, no únicamente optimizar atención pasada. Entradas autorizadas: secuencias de errores digitales/transacciones, repetición de intentos, cambios de estado y contexto temporal disponible. PredictionCutoff fija qué información era conocida en ese momento; no usar contact_future, complaint futura o estado corregido después como feature retrospectiva.

RiskSignal distingue «fricción observada» de «contacto futuro estimado»; guarda feature_spec/cutoff/window/coverage/model-or-rule version. Rust/SQL reglas explicables iniciales; un modelo estadístico futuro necesita contrato/calibración/prueba temporal propios, no Jev adivinando probabilidad desde una tabla. Jev etiqueta motivo de texto disponible si existe; LLM investiga explicaciones/cohortes y recomienda intervención. Medir precisión/recall cuando hay labels observables, lead_time y costo de alertas con clases negativas y censura; no declarar performance sin benchmark.

Salida por defecto: expediente agregado y/o contexto preventivo para la próxima atención autorizada. Contactar proactivamente al cliente, alterar producto/cuenta o iniciar campaña es otro efecto: OutreachProposal con consentimiento/eligibilidad/canal/frecuencia/riesgo/authority y adapter correspondiente. Este spec no concede autorización de outreach; puede recomendarlo como dependencia. El motor no convierte propensión en mensaje automático ni confunde estimación individual con culpa/causa de mora.

## 19. Implementación propuesta por cortes

```text
src/domain/        ids, refs, events, outcomes, proposals, policies, decisions
src/application/   ingest, discover, investigate, evaluate, collaborate, promote
src/ports/         sources, sandbox, models, artifact/metadata, framework
src/adapters/      persistence, isolated workers, model HTTP, runtime fixture
src/api/           commands, queries, authorized progress stream
tests/fixtures/    explicit synthetic sources, tool envs, reference opportunities
tests/contracts/   port schemas, idempotency, unknown/timeouts and lineage
tests/e2e/         complete journeys including crash/concurrency/denied paths
```

Diseño de módulos, no scaffold creado. No fijar versiones de librerías hasta implementar y verificar APIs/licencias. Jev vía adapter de protocolo oficial, LLM provider intercambiable; ninguna dependencia de SDK decide el dominio.

1. Camino vertical seguro: fixture de histórico/trazas → snapshot → monitor SQL → expediente → objeción → investigación → dos propuestas con datos/costos explícitos. Incluye manifest/ledger/budget/denied access desde inicio.
2. Candidato y laboratorio: framework fixture, oráculos, particiones, adversarial scenarios, baseline vs candidate y gate; assertions de efecto y no solo texto. Trace y UX progresan con eventos reales.
3. Continuidad: cambios de knowledge/tools, invalidación/concurrencia, discovered detector promovido, feedback limitado y regresiones. Mantener una mission abierta de exploración además de monitores.
4. Integración autorizada: fuentes/framework reales, operación de releases/incident guards y resultados maduros. Contratos definidos antes, efectos reales no autorizados ahora. Una demo puede simular estas integraciones declaradamente sin afirmar eficacia productiva.

## 20. Fuentes técnicas verificadas y límites

Consultadas el 2026-09-29. Las decisiones arquitectónicas de este documento son nuestras propuestas, no recomendaciones oficiales de estas fuentes.

- [Jev primitives](https://docs.typesafe.ai/primitives): preguntas tipadas e independencia; respalda la semántica acotada de la sección 14.
- [Jev confidence](https://docs.typesafe.ai/confidence): distribución/confidence y umbrales dependientes del caso; no certifica precisión bancaria.
- [Jev intent routing](https://docs.typesafe.ai/patterns/intent-routing): clasificación compuesta con ruteo en código; ejemplos de umbrales no adoptados.
- [DuckDB security](https://duckdb.org/docs/current/operations_manual/securing_duckdb/overview): SQL no confiable requiere aislamiento además de configuración; respalda la frontera del sandbox.
- [JCS RFC 8785](https://www.rfc-editor.org/rfc/rfc8785): canonicalización y representación de alta precisión; perfil propuesto para manifiestos.
- [SQLite backup](https://www.sqlite.org/backup.html): mecanismos de snapshot/backup consistente de la base; no garantiza coherencia automática con blobs/routing externos.
- [NPS — Bain](https://www.netpromotersystem.com/about/measuring-your-net-promoter-score): cálculo por categorías, no promedio de puntuaciones.

Pendientes antes de uso real: esquema/permiso/fuentes efectivos, método de linkage por fuente, políticas de privacidad/retención/egress por país, desempeño Jev por idioma/tarea, umbrales estadísticos y de gates, unidad económica/FX, autonomía por riesgo, contratos del framework y reglas de compensación de efectos bancarios. Se representan como config/dependency, no se inventan ni impiden implementar con fixtures honestos.

## 21. Seguridad, autoridad y ciclo de vida de modelos/datos

### Autoridad efectiva y políticas

AuthorizationContext emitido por servidor: principal, tenant, purpose, originating_actor/request, delegated_scope, allowed_actions, partition_scope, authorization_epoch y expires_at. Cada referencia directa/transitiva se resuelve contra objeto real/lineage, no sus etiquetas declaradas. Autoridad efectiva = delegación autorizada ∩ propósito ∩ scope ∩ política vigente. Sin contexto común para join se rechaza; workers no heredan toda autoridad de service account. Cross-tenant ref válido es AccessDenied antes de leer/copiar. Jobs automáticos usan delegación de mission/policy explícita, no actor sin límites.

PolicyRevision (borrador/versionado) y PolicyActivationDecision (autoridad de administración/gobierno) distintos. LLM/worker pueden proponer scopes/presupuesto/autonomía pero no activarlos ni concedérselos. Registrar delegación/epoch y audit; ampliar autonomía exige autoridad que ya posee derecho de concederla. Revocación bloquea dispatch/efectos nuevos; trabajo suspendido no conserva permisos por existir. Política nueva puede reducir permisos sin recompilar agentes.

TrustedProducerRegistry fija clases de artefactos permitidas por productor autenticado. Assurance ejecutable se registra a partir de FrameworkAdapter autenticado con operación/build/candidato/environment/scope comprobados, no campo del JSON del LLM. Runtime comprueba autorización/fencing al efecto. Hash acredita integridad, no autoría. Transporte autenticado y ACL del store son base; firmas adicionales solo con gestión/verificación de claves definida.

### Contexto completo y revocación

ModelContextManifest enumera TODO contexto efectivo (incluidos mensajes previos, archivos, tool resultados y estado de sesión), refs/lineage/epoch y tratamiento; broker revalida antes de cada llamada. Texto inline sensible debe registrarse como artefacto tratado o derivado, no esconderse fuera del manifiesto. Revocar fuente pausa jobs/sessions/workspaces dependientes y obliga reconstrucción autorizada o terminación; quitar ref conservando texto no cumple. Enforcement práctico: destruir/aislar workspace contaminado y abrir otro, invalidar conversation session y cache; no volver a enviar historial revocado.

Retention/DeleteJob incluye fuentes tratadas, derivados/caches, contextos, traces, stdout/spill, transcripciones SDK y backup expiry. SuppressionLedger se consulta antes de reingesta y restore. Ya enviado a proveedor no puede «retraerse» por promesa local: registrar entrega y tratamiento/retención contractuales, solicitar proceso soportado; no afirmar borrado remoto sin confirmación. Historia de decisiones puede conservar refs no sensibles/tombstones, sin el contenido eliminado.

### Identidad de modelos y supply chain

ModelInvocationManifest: provider/endpoint, requested_model, resolved_model/deployment/version si disponible, version_guarantee {pinned,observable_only,unknown}, prompt/question/rubric/template hashes, request_builder version, parámetros, policy/egress/context refs, usage/cache, provider response identity y observed_at. Alias nominal no fija comportamiento; no usar como identidad reproducible plena. Si versión no resoluble, cache lifetime/epoch de deployment explícito y uncertainty reportada; ejecución fresca no finge repetición idéntica.

Model/prompt/judge routing cambios se registran en ModelConfigurationRevision y dependencias. Benchmark de calibración por tarea/idioma e intervalos/drift definidos en policy; pérdida de calibración pausa juicios/gates afectados o usa fallback, no seguridad dependiente del LLM. El rollout de prompts/modelos también se evalúa; no puede escapar al sistema por no ser un «agente». Binarios/runtime/extensiones/fixtures admitidos tienen identidad/version/digest de distribución y productor, sin código arbitrario generado en host.

## 22. Operación de plataforma y evolución del software

### Admisión y recursos

AdmissionPolicy global además de budgets por job: procesos/CPU/RAM/disco/scratch/output/concurrencia, queue limits y clases protección/reconciliación/control, ingesta, consultas humanas, monitores y exploración/backfill. Reservar capacidad operacional para incidentes; agotamiento discrecional de research no bloquea contención/reconciliación autorizada. Reserva no es permiso ilimitado: si falta recurso operacional, registrar fallo de protección y escalar. Framework/RoutingControl tiene guardrails preautorizados independientes cuando el controlador no está disponible.

Backfills usan microbatches/checkpoints y coalesce triggers; fairness por tenant/mission. Pause source reads sin confirmar cursor de datos no durables. Queue full → deferred/rejected explícito; no cola infinita ni retries masivos. Fuente lag/gaps degrada cobertura/outcome maturity/gates, no solo dashboard. Single-writer serializa transacciones cortas; ninguna query LLM larga retiene transaction/lock del ledger.

Objetivos operacionales a fijar por DeploymentProfile: latencia comando/query/progreso, lag ingesta/señal, reconcile/containment, recovery RPO/RTO, límites de backlog y budgets. Medir p50/p95/p99 cuando se definan; no inventar SLA/99.9% o zero-loss. Pruebas de carga usan fixtures y host concreto para decidir cuándo cambiar metadata adapter/topología.

### Degradación explícita

| Falla | Comportamiento permitido |
|---|---|
| LLM/Jev | Investigación semántica espera/fallback; monitores deterministas continúan si datos válidos |
| Sandbox | No nueva evidencia SQL; no ausencia de problema por falta de resultados |
| Controlador Pulso | Framework conserva versiones estables previamente activas; no nuevas promociones; guardrails independientes solo si integrados/atestados |
| Autoridad/policy no verificable | Nuevos efectos privilegiados fail closed; contención preautorizada según contrato independiente |
| Telemetría atrasada | Freshness insuficiente, expansión/release pausado según policy; atención no forzada a depender de investigación |
| Metadata/blob inconsistente | Recovery mode, sin egress/efectos nuevos, faltantes visibles |

### Backup y restore

RecoveryManifest fija metadata/ledger checkpoint, inventario verificable de blobs refs/hashes, esquema/config y suppression/control checkpoint. Backup de SQLite por mecanismo consistente, no copiar live DB olvidando archivos asociados; blobs referenciados hasta checkpoint verificados y retención coherente. Restore inicia sin dispatch/egress/efectos, verifica refs/hashes/missing, aplica revocación/suppression actual desde autoridad de control separada o permanece cerrado si no se puede verificar.

Crear recovery epoch/fencing namespace reconocido por brokers/routing; no reutilizar generación restaurada como verdad externa. Reconstruir proyecciones; reconciliar operations unknown y routing observado; revalidar expiraciones/policies/authority; RecoveryReady auditable habilita clases de trabajo por separado. Backup viejo no resucita datos suprimidos ni permisos revocados. No prometer replay/restore completo de evidencia eliminada. Simulacro de recuperación prueba consistencia, RPO/RTO y fences, separado de pruebas unitarias.

### Deploy del software, esquemas y protocolos

PlatformDeploymentManifest: binary/build/config/schema/adapter versions, producer identity, contracts supported, migration/upcaster refs, rollback compatibility y smoke requirements. Despliegue de plataforma distinto de Release de capacidad. Inicialmente pause/drain escritor/jobs, fence procesos, backup coherente, migración controlada, restart/reclaim, smoke y reopen. Atención estable reside en framework separado, no se promete continuidad si ambos están en mismo deployment.

Artefactos antiguos conservan bytes/hash/schema; upcasters producen vistas/derivados versionados, no mutan pasado. Event/command enum/schema desconocido → UnsupportedContractVersion, no unknown bancario ni ignorar evento y avanzar checkpoint. Cambios de normalizador/gate/interpreter/defaults disparan impacto semántico/revalidación. Rollback binario solo si schema/contracts compatibles; si no, roll-forward/migración explícita, no downgrade ciego.

API admite límites payload/size/depth/rate, schemas soportados y ErrorEnvelope {code,retryability,safe_details,operation_ref?,revision?,correlation_id}. DomainEvent incluye aggregate_id/revision, event_id y commit_sequence; reducers aplican revisiones ordenadas, gap → replay/rebuild, duplicado/no-op, evento viejo no retrocede head. Checkpoint cubre solo eventos realmente reducidos; publicación outbox puede ser at-least-once y fuera de orden, sin falsa actualidad.

### Observabilidad y assurance operacional

Métricas con dimensiones acotadas (job kind/provider/status/cohort definida), no cliente/job/query IDs como labels ilimitados. Correlaciones en traces/ledger con acceso/redacción/retención/budget de bytes. Sampling para telemetría, nunca eliminar auditoría requerida de decisiones/efectos; medir dropped telemetry. Observability store no única fuente de verdad. SQL/prompts/errores/plans pueden ser sensibles.

Antes de efectos reales deben verificarse aislamiento OS real, mounts/red/credentials, identidad/runtime permissions, routing CAS/fencing, control plane recovery y política/model provider. Mocks prueban controlador, no esas garantías. DeploymentAssuranceReport fija entorno, pruebas y limitaciones; promotion policy puede exigir ese reporte vigente además del evaluation report del candidato.

## 23. Definiciones de medición y experiencia responsable

SurveyMetricDefinition: pregunta/versión/tipo, scale/favorable_categories, survey unit, invitación/respondiente/valid response refs, duplicates/invalidations, periodo/cohorte/weights y country/language scope. NPS estándar 0–10: 100 × (promotores 9–10 menos detractores 0–6) / respuestas válidas; pasivos 7–8 en denominador. CSAT fija escala/criterio favorable en su definición, no top-two universal. Cero respuestas → unknown, no score 0. Reportar response rate/cobertura/no respuesta y no agregar escalas incompatibles. Sentimiento inferido es otra métrica, no encuesta.

EffortEstimate separa construcción/integración/pruebas/autorizaciones/operación, unidad (horas/días/categoría definida), estimator/method/ref, assumptions, unknowns y revision. Tool faltante no cuesta cero; «fácil» LLM no dato observado. ValueScenario separa costo de investigar del de implementar/mantener; ajuste humano crea revisión/diff y sensitivity, no modifica evidencia observada. El beneficio priorizado nunca compensa un riesgo bloqueante.

BusinessOutcomeDefinition vincula métrica a objetivo/periodo/eligibility/baseline y control de doble conteo. Ahorro de servicio, ingresos incrementales y riesgo evitado no se suman sin escenarios compatibles. Error crítico puede ser relevante aunque no sea frecuente; concentración tipo Pareto no exige 20/80 exacto. Recomendación visible explica beneficio/esfuerzo/riesgo dominante, unknowns y por qué no se recomienda otra alternativa.

## 24. Ejemplo técnico de un episodio de colaboración

IDs ilustrativos, sin números del banco. SourceSnapshot S1 tiene resolved_as_of y seguimiento observado; CapabilitySnapshot C1 describe tree T1, IA1 y tool read_status v1. Mission M1 ejecuta monitor D1 y research con scope development. QueryReceipt Q1 prueba concentración de recontactos a grain episodio; Claim K1 es observed y K2 («la demora explica el contacto») hypothesis, no causal.

Oportunidad O1/rev1 vincula K1/K2. Usuario U pregunta por incidente canal: comando H1 RequestResearch(expected_revision=1) se valida bajo delegación U, registra hipótesis HYP2 y Job J2 con S1/C1 fijados. SQL Q2 contrasta cohortes y exclusions; se publica EvidenceBundle E2 y O1/rev2. Otro comando H1 reintentado devuelve receipt J2, no job nuevo.

Planner genera P1/rev1 (ampliar árbol informativo) y P2/rev1 (mejorar skill manteniendo IA2), más no-change. Tool solo lee estado: ninguna propuesta promete reparar la transacción. Si P1 requiere tool desconocida, DependencyBlock; si read_status permite objetivo acotado, adapter autenticado prepara candidate A1 con assurance simulated_runtime en fixture.

Suite V1 development/validation, familias F1/F2 con casos éxito/unknown/timeout/permiso ausente, oráculo independiente verifica explicación+handoff y ausencia de writes. Run EV1 compara T1/A1 con fixture reset. Timeout deliberado con handoff correcto puede pasar; harness outage inconclusive. Gate G1 refiere policy GP1. Si pasa, Authorization AU1 solo shadow/scope X y ReleasePlan RP1; efecto confirmado por RuntimeOperation RO1 y routing generation, no por chat.

Si knowledge cambia o fuente S1 queda corregida, ImpactAssessment marca usos de AU1 stale; no se promueve canary con autorización shadow ni con evidencia invalidada. Seguimiento simulado produce OutcomeObservation con source_kind/environment explícitos; no «ahorro realizado». Este mismo expediente conserva preguntas, versiones, alternativas y decisiones, y permite regresar de trace/caso al contexto de comparación.

## 25. Concreciones HOW de la nueva revisión independiente

SPEC_VISUAL_PULSO.md desarrolla diagramas y explicación del diseño; secciones 23–26 agregan los siguientes contratos, pendientes de implementar:

- NextAction enum: DescribeSchema, ReadQuery, Derive, InspectResult, RequestSemanticJudgment, FinishResearch, DeclareBlocked. Primer corte secuencial por workspace, validar/ejecutar/commit antes de otro modelo; sin mutaciones a metadata/release desde el LLM.
- DerivationRequest fija operation_key/base revision/parent manifest/SQL/params/auth/budget; rama temporal → export consistente → blobs verificados → CAS del workspace head. Crash antes de commit reanuda parent, después devuelve receipt; no confiar en scratch. Estado persistido de DB por mutación para fixtures pequeños como default propuesto.
- publish_research fija expected_opportunity_revision, artifact/evidence refs, claim drafts, signal refs y key. Evidence valida referencias; Opportunities publica preservando objeciones concurrentes; Discovery no pisa heads.
- Signal identity fija tenant/scope, detector version, snapshot, population spec, window y metric spec; narrativa no entra. Opportunity match es búsqueda relacionada, no unique key de causa.
- ModelOperation fija context/invocation/reservation/dispatch/usage/output. Cache autorizado antes de reserva externa; timeout postdispatch mantiene usage pendiente. Sin cota proveedor, presupuesto económico es estimado, no garantía de factura máxima.
- ProcedureSpec DSL: Check/Read/Act/Respond/Handoff/Finish; Exists/Equals/In/Compare/And/Or/Not, truth=true/false/unknown. Fields/guards válidos antes de acción; RequiredEvidence para huecos; validar reachability/bindings/salidas/ciclos con límites. Primer algoritmo: prefijos compartidos por objetivo/eligibilidad y contraste de excepciones, sin causalidad inferida.
- ChangeSpec tipado Tree/Skill/Agent/Team/Knowledge/ToolRequirement/DataRequirement/ClassifierChange; goal/input/output/dependencies/constraints/handoff según kind; requisitos satisfied/unresolved/incompatible. Team valida owners/delegation/shared context/aggregation/stop. No construir tool/data mediante schema.
- OracleSpec fija objective contract, authority sources, assertions, unknown dimensions y provenance authoritative_rule/expert_defined/historical_verified/synthetic_assumption. Assertions Rust FinalState/TraceContains/ActionForbidden/HandoffRequired/OutputContractSatisfied/BudgetWithin. Missing detalle histórico → unknown, no closed=true como éxito.
- CoverageRequirement enlaza requisito/condición/criticidad/casos/assertions/observación. Case generated ≠ condition reached ≠ assertion checked. Jueces semánticos blindados a identidad/justificación, criterios separados y calibración/desacuerdo.
- TopicRevision/TaxonomyChange versionan definición/examples/exclusions y mappings equivalent/broader/narrower/split/merge/unresolved. Clasificador viejo/nuevo eval→anotación shadow→activación autorizada; fuentes históricas intactas, split no reparte cifras sin evidencia y sin ruta usa fallback.
- DecisionComparison separa inviabilidad, escenarios comparables, dominancia justificada y sensibilidad. Prioridad de research distinta de construir. intervention_mechanism liga causa candidata→efecto de intervención→prueba; la explicación de estado no repara core.

Revisiones nuevas de diseño y sus cierres se registran en REVISIONES_SPEC_PULSO.md; no equivalen a pruebas de ejecución.

## 26. Cierres de la segunda ronda adicional: transiciones y evaluación

La guía visual es el punto de entrada legible; este documento conserva la referencia técnica. Todos los contratos siguientes son diseño propuesto, no implementación validada.

- FinishResearch persiste un borrador antes de publicar: DraftCommitted → ValidateResearch → PublishResearch → Published, AwaitingConflictResolution o Rejected. El job puede recuperarse sin volver a pedir al modelo que invente la investigación. Un timeout no equivale a rechazo ni éxito.
- Publicación concurrente: comentarios/asignación no invalidan evidencia por sí mismos; hipótesis nuevas quedan untested y abren investigación; cambio de scope exige revalidar o crear nueva investigación; corrección de fuente marca evidencia stale; merge/split requiere destino explícito. Nunca sobrescribir el head silenciosamente.
- AnalysisInputManifest referencia versiones de fuentes, episodios, outcomes, anotación semántica, taxonomía, capacidades y madurez observacional. Es input efectivo de identidad de señal y cache, no únicamente el snapshot de las tablas.
- InputValue = Known(value) | KnownAbsent | Unknown(reason). Null depende del schema; no se convierte universalmente a false. AND(false, unknown)=false; OR(true, unknown)=true; NOT(unknown)=unknown. Guards son excluyentes o tienen prioridad explícita validada. Error de tool tiene salida propia y no es una condición falsa.
- AssertionResult = pass | fail | unknown | not_applicable, con evidencia y motivo. No observar una acción prohibida solo prueba ausencia si la captura fue completa. OutputContractSatisfied no sustituye el objetivo de resolución; dimensiones requeridas unknown bloquean el gate correspondiente.
- EvaluationPlan congela población comparativa, cohortes, versiones de elegibilidad, denominador y frontera de costos. Comparar población común y reportar cobertura específica; no excluir después casos caros para mejorar el candidato. Handoff sin continuación medida produce costo parcial, no ahorro completo.
- Construcción automática y edición humana usan el mismo CandidateBuildRequest bajo PolicyDelegation. Automatización no requiere aprobación manual en cada transición, pero el efecto permitido y el ámbito están acotados; una política de release sigue siendo independiente.
- Iteración concreta: fallo en development → caso de regresión con lineage → candidato con salida segura → reevaluación baseline/candidate. La capacidad activa permanece intacta. Comparar árbol con skill que preserve escalamiento: la alternativa técnicamente más compleja no gana por defecto.
