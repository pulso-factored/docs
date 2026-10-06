# Revisión de integración Agent Core — 30/09/2026

Estado: auditoría documental de diseño, no implementación ni tests de producto. Fuente upstream: commit `81227c99ce46fde38bf986698c8a02bad9241c02`, contracts/VERSION `0.5.0`. Checkout referencia readonly en `references/agent-core`.

## Lectura y método

El agente principal leyó specs modulares M0–M12 (M12 propuesta), registry rev2, gateway, índice/descomposición, temas abiertos, ADRs de registry/constructores y decisiones relevantes de Jev, escrituras, políticas, conocimiento y gateway. Revisó partes de la spec general histórica como contexto; no la tomó como sustituto de sus módulos/enmiendas. Contrastó directamente modelos de entidades/registry, rutas HTTP, suite y construcción/hash candidato. Tres agentes hicieron lectura independiente de runtime/artefactos, registry/autorización y evaluación/auditoría/gateway. Después de adaptar V2, los mismos revisores auditaron transversalmente trabajo de otros roles, no sólo su propia sección.

## Hallazgos y resolución

| Hallazgo | Resolución vigente |
|---|---|
| AgentSpec/TreeSpec/Skill propios incompatibles | §17 exporta EntityDraft Agent/Flow/DecisionModelDef/Prompt/Template/ToolDef y dependencias; skill sólo composición admitida |
| Autopublicación/canary/CAS supuestos | §§1/7/15/18/20/27: autonomía hasta evaluated, gate humano obligatorio; publish staging; promote prod distinto; canary no soportado |
| PRs/YAML como autoridad registry | PostgreSQL registry, API de propuestas; YAML import/export; Pulso guarda evidencia/receipts propios |
| Query command_key inventada | §§8/15/19/20/27: matriz recuperación por operación; sólo publish key, PUT CAS, create/promote unknown puede requerir reconcile humano |
| Core pass confundido con mejora | Gates separados, base staging vs baseline runtime, mejora/oracle/Pulso adicionales; dos cards UI |
| Expect vacío pasa sin resolución | Compiler de mérito exige expectativa ligada al bridge, evento terminal/cobertura y oracle independiente; test negativo obligatorio |
| Adversarial adaptativo no cabe en steps estáticos | Exploración dev→grabación/adjudicación→suite estática; campañas adaptativas complementarias separadas |
| Redactar raw rompe cadena audit | Verificar original en adapter confiable; original cifrado si autorizado, proyección redacted separada; si original se elimina sólo receipt, no cadena revalidable |
| Falta de capa/episodio/acciones humanas | Mapping externo versionado y cobertura; missing unknown, handoff_resolved no demuestra resolución bancaria |
| Timeout evaluate no cancela runtime | ExecutionProfile sellado, reserva conservadora, no retry concurrente, sin enforcement live se bloquea campaña fuera presupuesto |
| Holdout podría filtrarse por last_eval | Prohibición de subir final a drafts/suite registry/receipts visibles/audit/OTel; perímetro propio, no confiar en RBAC fino inexistente |
| Duplicación de gateway | Gateway Rust para motor, adaptador Python para Core; compartir proxy necesita fachada OpenAI-compatible explicitada |
| Wiki confundida con knowledge runtime | Wiki independiente; knowledge snapshot dinámico dependency_blocked, M12 pendiente |
| Recheck detecta bundle con dos schemas | §5 remite a §17 canónico por estado draft/frozen/evaluated, campos requeridos según transición |
| Freeze no devuelve closure | §27 calcula localmente desde baseline/drafts con parity golden; adopta sólo new_versions/auto_bumped de response |
| Grafo gastaba final antes de gate Core | §18: dev→Core evaluate→pass→final una vez; infra retry mismo hash; final falla/inconcluso retira familia |

## Límites y aceptación

No se modificó Agent Core ni se desplegó integración. No se ejecutaron tests upstream, schemas Rust ni servidor real; fixtures y contract CI son trabajo de implementación especificado, no evidencia actual. La raíz factored no es repo Git; no se presenta git diff --check como pasado. Los diagramas se revisaron textualmente; no se acredita render completo Mermaid.

La documentación permite implementar un mock de contratos disponible sin construir el Agent OS. Cambiar por Core real requiere smoke de composición/transporte, autenticación, catálogo/bootstrap, auditoría y executors/sandbox. Persisten dependencias upstream explícitas, no garantía de enchufe instantáneo. El motor sigue propuesta pendiente del visto bueno del usuario.

## Revisión posterior al pull — contratos 0.7.0

Fuente actual: `98d3836d81daf1109025073718574e9e9f36842e`, obtenido con pull fast-forward desde el SHA anterior. Esta revisión es del agente principal; las rondas independientes de arriba corresponden al snapshot 0.5.0, no acreditan revisión independiente del nuevo commit.

| Cambio comprobado en fuente | Ajuste documental |
|---|---|
| Registry HTTP restringe todas las rutas a builders; roles distinguen bot, supervisor y admin; decisiones humanas requieren step_up | V2 §27.5 y consolidación; revoke/import requieren admin, no sólo aprobador |
| EvalRun y ProposalDetail exponen ID/hash/base/suite en last_eval | Recuperación de evaluate por GET y comparación con ID previo; no lectura directa de tablas ni campos inventados en EvalReport |
| AgentStepPayload acepta failed/error_kind; GenerationResult distingue usage_known | Sensores separan fallo del nodo de outcome bancario y costo desconocido de cero; documentada pérdida de marca en LLMAgentPort |
| Excepción administrativa de datos y falta de auditoría de lecturas permitidas | Bot no hereda credenciales admin; lectura privilegiada exige auditoría propia |
| M12 aprobado para fase 2; collect decide rechazado; contexto reciente por despliegue | No exportar conocimiento aún inexistente; fijar config de contexto en campañas |
| El registry sigue sin delete por entidad, canary ni servidor productivo compuesto | disable compila nuevas referencias o bloquea; mocks no afirman capacidades futuras |

Se contrastaron docs modificados, modelos, permisos, handlers, gateway y pruebas fuente. No se ejecutó pytest: el Python disponible no tiene pytest y no hay entorno upstream preparado. No se acredita compatibilidad runtime, integración, despliegue ni render completo Mermaid. Las nuevas regresiones descritas son requisitos para el equipo, no tests ya implementados.
