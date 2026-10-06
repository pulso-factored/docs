# Pulso — registro de revisión adversarial del spec

Fecha: 2026-09-29. Revisiones independientes de diseño, sin ejecución de tests ni implementación. Artefactos revisados: SPEC_DETECCION_AUTOMEJORA.md y ESCENARIOS_VALIDACION_PULSO.md. La propuesta no se declara aprobada por el usuario ni segura para producción.

## Método

Tres agentes contribuyeron inicialmente con focos de experiencia/integración, detección/orquestación y contratos/evaluación. El coordinador sintetizó un spec único. Luego dos rondas adversariales revisaron el conjunto; primera con rotación de focos para evitar revisión limitada a la contribución propia; segunda ampliada por solicitud del usuario a ingeniería, producto, seguridad y operación. Tras incorporar fixes, una tercera comprobación dirigida verifica cierres y contradicciones restantes.

## Ronda 1 — huecos E2E

| Hallazgo | Cambio incorporado | Validación prevista |
|---|---|---|
| Revisiones de fuente duplicadas/conflictivas | SourceRecordVersion y resolved_as_of, tombstones/cuarentena | D01/D03/D18 |
| Joins inflan población | Detector grain/universe/cardinality/coverage assertions | D16 y benchmark detector |
| Scratch mutable rompe cache/retry | Workspace revision, DerivationManifest, reads vs mutations | D19/D20 |
| Corrección fuente no bloquea uso de aprobación | Evidence closure y ApprovalUseBlocked | D21 |
| Fencing solo al commit | Validación en dispatch y operation key estable | W06 |
| Missingness selectiva/links mezclados | Coverage counts y EpisodeMembership por relación | D04/D05/D16 |
| Etiqueta Jev aparenta acción ejecutada/cita garantizada | Inferred annotation, locators verificados y selección declarada | P05 |
| Cliente adversarial reservado no puede ejecutar con prohibición global | Principales generator/runner/oracle y CustomerView aislada | E03/E11 |
| Derivados lavan partición | Propagación restricciones y acceso principal/propósito | E03 más pruebas de export/derivación |
| Evaluación sin frontera equivalente al sandbox | EvaluationEnvironmentManifest, tool binding sin fallback | E06/E13 |
| Activación tardía/reactivación tras stop | Runtime apply-time CAS/fencing/generation | R09 |
| Estado parcial/unknown oculta exposición/conflicto | ReleaseReconciliationState y bloqueo solapado | R10 |
| Error deliberado vs harness failure ambiguos | Distinción de condiciones/cobertura/oráculos | E12/E07 |
| Detector descubierto no tiene release propio | F10 Registry/report/decision/mission binding | M01/M02/J04 |
| Catálogo y stream insuficientes | Authoring/import protocol y cursor/resync/checkpoint | U07/U09 |

## Ronda 2 — arquitectura de plataforma y producto

Revisores confirmaron los fixes R1 como presentes en el documento y detectaron nuevos huecos. La afirmación se refiere a cobertura escrita, no comportamiento ejecutado.

| Hallazgo | Cambio incorporado | Validación prevista |
|---|---|---|
| Restore revive datos/permisos/operaciones viejas | RecoveryManifest, suppression actual, closed mode/recovery epoch | O01/O02 |
| Backfills saturan control/protección | AdmissionPolicy, single writer, microbatches y reserva operativa | O03/O04 |
| Disponibilidad implícita/degradación indefinida | Matriz de fallas/objetivos por función, framework estable separado | O06 |
| Deploy de código/schema confundido con capacidad | PlatformDeploymentManifest, drain/fence/migrate/upcasters | O05/O08 |
| Telemetría filtra/satura | Cardinalidad acotada, redacción/sampling/audit separado | O09 |
| Cross-ref/service account amplía autoridad | AuthorizationContext servidor y delegación intersección | S01 |
| Worker puede elevar política/autonomía | PolicyRevision separado de activation authority | S02 |
| Revocación no alcanza prompt/scratch previo | ModelContextManifest completo, invalidación/reconstrucción | S03 |
| Hash/manifiesto finge atestación | TrustedProducerRegistry y adapter/runtime autenticados | S04 |
| Alias modelo finge reproducibilidad | ModelInvocationManifest/version guarantee/calibration | S05/S06 |
| Idempotencia retry después commit/revocación | Key lookup autorizado antes de repetir preconditions | U13/U14 |
| Proyección pierde orden | Aggregate revision/commit seq/gap replay y checkpoint real | O07 |
| Ownership bloqueante sin audiencia/permisos | Group routing/fallback y no privilege por assignment | U10 |
| Handoff solo promesa | HandoffContext con auth aplicable, evidencias y pending ops | U11 |
| Proactividad confunde autorización outreach | F12 frontera predictor/señal/outreach independiente | A01/A02 |
| NPS/CSAT/effort ambiguos | SurveyMetricDefinition, EffortEstimate y value provenance | V01/V02/V03 |
| Defer/motion cambian semántica producto | AttentionPreference y ActivityView accesible | U12/U15 |

Se corrigió además E03 del catálogo de escenarios para no contradecir el runner con CustomerView del caso reservado.

## Comprobación final dirigida

Completada por los tres revisores tras incorporar correcciones R2. Arquitectura operacional verificó recovery/admisión/degradación/deploy/telemetría; dominio verificó autoridad/revocación/atestación/modelos/idempotencia/orden; experiencia verificó políticas/budgets/ownership/handoff/outreach/medición/accesibilidad. No reportaron P1 residuales concretos en sus focos que bloqueen el primer corte con fixtures explícitos.

Esto no demuestra ausencia de todos los defectos ni valida runtime/banca real. Los revisores mantienen pendientes pruebas de aislamiento, identidad/permisos, routing CAS/fencing, retención del proveedor, carga y recuperación. Ningún test se ejecutó: se revisó cobertura y coherencia documental. El catálogo de aceptación incorpora casos derivados de ambas rondas y deberá traducirse a pruebas durante implementación.

## Riesgos aceptados como pendientes, no eliminados por escribir el spec

## Dos rondas adicionales para la guía visual: R4 y R5

Tres revisores independientes trabajaron desde arquitectura operacional, dominio/contratos y experiencia de producto. R4 inspeccionó la primera guía; R5 revisó el texto corregido buscando defectos nuevos. La inspección gráfica de páginas renderizadas corresponde al autor, no a los agentes. Estas son revisiones documentales, no pruebas ejecutadas.

| Ronda | Vacío encontrado | Cambio incorporado |
|---|---|---|
| R4 · arquitectura | SQL exploratorio sin protocolo físico durable; control del modelo ambiguo | Rama/export/blob/CAS, NextAction, ownership de publicación y ModelOperation |
| R4 · dominio | Procedimientos, oráculos y cobertura insuficientemente ejecutables | ProcedureSpec/ChangeSpec tipados, autoridad del oráculo, trazabilidad y evolución de taxonomía |
| R4 · producto | Pipeline sin decisión comprensible ni loop humano completo | Comparación de alternativas, mecanismo de intervención, dossier y feedback con disposiciones |
| R5 · arquitectura | FinishResearch y conflictos concurrentes incompletos; identidad no incluía todos los inputs | Borrador durable, estados terminales, política de conflictos y AnalysisInputManifest |
| R5 · dominio | Unknown podía confundirse con false; métricas podían comparar poblaciones distintas | Lógica de tres valores, resultados de assertions y plan comparativo congelado |
| R5 · producto | HOW difícil de encontrar; automatización parecía depender siempre del humano | Parte II explícita, referencias cruzadas y construcción delegada; ejemplo de fallo, regresión y reevaluación |

Los cambios aparecen en SPEC_VISUAL_PULSO.md (secciones 23–26 y recorridos relacionados), SPEC_DETECCION_AUTOMEJORA.md (25–26) y el catálogo de aceptación. Cada ronda reportó hallazgos de severidad P2 en sus focos; no se interpreta como garantía de ausencia de defectos. Sigue pendiente validar comportamiento en software real.

## Riesgos de implementación que siguen abiertos

Comprobación del artefacto de lectura: PDF de 32 páginas y 27 diagramas vectoriales generado desde SPEC_VISUAL_PULSO.md. Se renderizaron todas las páginas y se inspeccionaron texto, tablas, índice y flujos; se corrigieron índice autorreferente, ruta de error que atravesaba un nodo y pseudocódigo partido. El generador usa handles de render independientes y copia los píxeles para evitar previews inconsistentes. Evidencia de render: tmp/pulso_spec_visual_verified. Esto verifica presentación documental, no ejecución del sistema.

- Esquemas/bindings/datos efectivos del banco no inspeccionados en esta etapa.
- Umbrales estadísticos/económicos, reglas de privacidad/retención/egress y autoridad de despliegue aún requieren configuración/autorización.
- Aislamiento OS, CAS/fencing externo, identidad/retención de proveedores, desempeño por idioma, carga y recovery exigen pruebas del entorno real.
- Framework interno no implementado; assurance diferencia spec, fixture e integración.
- Las revisiones no demuestran eficacia financiera, causalidad ni cumplimiento legal.
