# Pulso — catálogo de escenarios de aceptación E2E

Fecha: 2026-09-29. Estado: especificación de pruebas a implementar; no ejecución ni resultados. Vinculado a SPEC_DETECCION_AUTOMEJORA.md. Given/When/Then identifica entrada, acción y efecto observable. Los fixtures son sintéticos explícitos y no contienen datos personales o bancarios reales.

## Suites y verificaciones

Tres suites distintas: contratos/seguridad del sistema, benchmark del detector y evaluación de capacidades candidatas. Que una pase no sustituye a las otras. Pruebas unitarias de validadores/cálculos, integración con persistence/sandbox/adapters y E2E de journeys; tests de crash/concurrencia y regresión incluidos. No fijar thresholds de negocio sin policy fixture declarada.

Para cada caso persistir case_id/revision, fixture_hash, policy_hash, asserted outputs/event/effects, partition y lineage. Harness observa metadata, outbox, blob refs, QueryReceipts, runtime operation logs, oráculos y proyecciones. Assertions no dependen solo de respuesta de un LLM. Pruebas deterministas usan model adapter fixture; pruebas reales de modelos se reportan separadas, con variabilidad y costo.

| ID / flujo | Given | When | Then observable |
|---|---|---|---|
| D01 / F01 | Lote y revisión de fuente ya committed | Se entrega nuevamente | Una revisión canónica; cursor y counts no se duplican |
| D02 / F01 | Campo requerido inválido | Normalización | Cuarentena con error; métrica no trata dato como cero |
| D03 / F01 | Evento original referenciado por un run | Llega corrección de fuente | Nueva revisión y aviso stale; run anterior conserva sus inputs |
| D04 / F01 | Dos motivos distintos de un cliente el mismo día | Vinculador construye episodios | No unión por solo tiempo/cliente; ambigüedad visible |
| D05 / F01 | Contacto cerrado, canal sin cobertura y ventana incompleta | Proyector calcula outcomes | Cierre known; recontacto censurado; resolución no inferida |
| D06 / F01 | Snapshot sin texto/tool traces | Se solicita semántica/patrón de acciones | Dependency/insufficient; no transcripción/acción inventada |
| D07 / F02 | Demanda y mezcla de casos cambian | Monitor calcula diferencia | Comparación declara universo/composición; cambio no presentado como causa |
| D08 / F02 | Misma trigger/input/policy run completed | Scheduler recibe trigger otra vez | No duplicar trabajo ni SignalCandidate |
| D09 / F02 | Jev uncertain o categoría other | Etiquetar contenido | Etiqueta versionada con abstención/unknown; no autoridad concedida |
| D10 / F03 | Sandbox sin red ni filesystem host | SQL intenta leer archivo host/red/cargar extensión no aprobada | Acceso bloqueado por entorno; evidencia de intento sin fuga |
| D11 / F03 | Consulta devuelve resultado limitado | LLM afirma ausencia en universo | Validación rechaza claim de completitud o exige consulta agregada completa |
| D12 / F03 | Presupuesto restante insuficiente | Solicitud de otra query/model call | No dispatch; estado de budget visible, outputs existentes preservados |
| D13 / F03 | Modelo retorna JSON inválido repetidamente | Límite de reparaciones alcanzado | InvalidModelOutput y job fallido tipado; no loop infinito |
| D14 / F04 | Dos problemas semánticamente similares de causas distintas | Dedup compara | Relación sugerida, no merge destructivo automático |
| D15 / F04 | Hallazgo recurrente sin novedad relevante | Consolida siguiente ventana | Actualiza expediente; no notificación repetitiva |
| D16 / F04 | Métrica con join 1:N susceptible a fanout | Se valida cálculo | Grano/denominador probado; no multiplicación silenciosa |
| D17 / F04 | Costos originales en distintas currencies y sin FX | Comparador pide USD | Unknown/dependency de FX; no suma incompatible ni tasa inventada |
| P01 / F05 | Propuesta exige tool inexistente | Prepare candidate | DependencyBlock y assurance explícito, no tool ficticia ejecutable |
| P02 / F05 | Árbol sin rama para timeout/unknown | Validate behavior spec | Error de contrato o handoff explícito antes de construir |
| P03 / F05 | Propuesta A y su evaluación congeladas | Builder/usuario crea A2 | Nueva revisión; autorización/eval de A no heredada |
| P04 / F05 | Permiso tool superior al disponible | Finalizar candidato | Bloqueo por scope; editar schema no amplía permisos |
| E01 / F06 | Candidate spec_only | Solicita prueba de resolución | Unsupported assurance; solo schema validation posible |
| E02 / F06 | Familia en development | Genera variantes idiomáticas | Misma partition/lineage; no selección manual reserved |
| E03 / F06 | Holdout con views runner/oracle segregadas | Investigador/copiloto solicita caso/SQL | AccessDenied; ni cache ni feedback revelan contenido |
| E04 / F06 | Cliente adversarial perfil público | Comienza conversación | No acceso al oracle, outcome esperado o estado interno del soporte |
| E05 / F06 | Tool fixture éxito técnico, objetivo sin cumplir | Evalúa caso | Técnica pass pero objetivo fail/unknown; no resolución por «gracias» |
| E06 / F06 | Baseline/candidato usan fixture equivalente | Ejecuta ambos | Estados aislados y reseteados; efectos del primero no benefician al segundo |
| E07 / F06 | Run interrumpido/general outage | Gate | Inconclusive, no ahorro probado ni rechazo del problema |
| E08 / F06 | Fallo crítico verificable y ahorro alto | Gate | Fail por seguridad; promedio no compensa |
| E09 / F06 | Evaluación nueva exige ejecución fresca | Hay reporte en cache | Nuevo run real o rechazo; no replay como ensayo fresco |
| E10 / F06 | Revisor revela caso final para reparación | Generador incorpora detalle | Caso retirado de reserved; futuro claim necesita holdout nuevo |
| R01 / F07 | Autorización válida para A/policy/scope | Nueva dependencia incompatible | CompatibilityStale; no activar sin revalidación |
| R02 / F07 | Approval expirado o solo shadow | Solicita canary/activo | Rechazo y autoridad/etapa requerida visibles |
| R03 / F07 | Runtime activó pero respuesta RPC se pierde | Reanuda operación | Consulta operation_id/key; no repetir efecto como nueva operación |
| R04 / F07 | Dos promociones esperan mismo release revision | Ambas intentan commit | Solo una obtiene transición; otra conflict/revalidation |
| R05 / F07 | Shadow | Candidato intenta efecto real | Denegado por ambiente/permisos, no solo instrucción textual |
| R06 / F07 | Episodio en versión fijada | Canary cambia allocation | Mantiene versión salvo contención explícita autorizada |
| R07 / F07 | Versión revertida tras acción bancaria | Rollback routing | No aparenta revertir acción; compensación requiere operación propia |
| R08 / F07 | Resultados inmediatos sin seguimiento maduro | Seguimiento release | No atribuye mejora definitiva de recontacto ni beneficio causal |
| U01 / F08 | Claim con evidencia existente | Usuario pregunta explicación | Respuesta con refs, sin job innecesario ni porcentaje inventado |
| U02 / F08 | Usuario pregunta causa alternativa | RequestResearch autorizado | Nueva hipótesis/work run; evidencia anterior conservada |
| U03 / F08 | Usuario dice «se ve bien» | Copiloto interpreta | No PromotionAuthorization privilegiada implícita |
| U04 / F08 | Rol sin permiso de release | Envia actor/policy falsos en payload | Identidad real domina; AccessDenied registrado |
| U05 / F08 | Usuario ve revisión vieja | Envía comando con expected_revision | StaleRevision; diff/reconfirmación para efecto privilegiado |
| U06 / F08 | UI desconectada con draft local | Reconecta stream | Dedup/cursor o refresh; draft no borrado; permisos actuales aplicados |
| U07 / F08 | Knowledge nueva versión | Publica catálogo | ImpactAssessment; consumidores/eval stale por motivo, historia intacta |
| U08 / F08 | Fuente revocada y cache hit | Explica claim | No devuelve contenido; evidencia no disponible explícita |
| I01 / F09 | Guardrail crítico preautorizado | Detecta fallo | Incidente y contención determinista antes de research LLM |
| I02 / F09 | Oportunidad silenciada | Riesgo crítico relacionado | Notificación incidente no suprimida por silencio de ahorro |
| I03 / F09 | Contención falla/timeout | UI recibe progreso | Estado pendiente/unknown, no servicio restaurado falsamente |
| W01 / §15 | Worker lease vencido, otro adquiere step | Worker viejo entrega output | Fencing rechaza commit viejo; head no sobrescrito |
| W02 / §15 | Blob escrito y crash antes commit | Recuperación | Sin referencia pública parcial; huérfano gestionable por política |
| W03 / §15 | Commit listo, publicación outbox falla | Reinicia worker | Evento reentregado idempotente; output no se recalcula ciegamente |
| W04 / §15 | Cancelación durante operación externa | Job cancela | No nuevos pasos; efecto iniciado reconciliado, no asumido anulado |
| W05 / §15 | Dos workers gastan presupuesto común | Reservan simultáneamente | Reserva atómica impide overspend del límite configurado |
| D18 / F01 | Misma identidad/revisión de fuente, otro hash | Ingesta | SourceRevisionConflict/cuarentena, no última escritura gana |
| D19 / F03 | Derivación scratch avanza revision | Misma lectura/params solicita cache | Key distinta o miss; no resultado anterior contra state nuevo |
| D20 / F03 | Workspace perdido | Reanuda run | Reconstrucción manifiesto verificada o WorkspaceUnavailable, no scratch vacío silencioso |
| D21 / F04 | Evidencia corrigida materialmente | Promoción autorizada previamente | ApprovalUseBlocked por evidence closure, no activation usando certeza anterior |
| E11 / F06 | Caso reservado runner aislado | Ejecuta diálogo | Solo CustomerView asignada; output restringido no accesible al builder |
| E12 / F06 | Tool timeout deliberado y fixture verificable | Candidato escala bien | Caso puede pasar; fallo del harness diferenciado |
| E13 / F06 | Tool fixture no bound | Arranca runtime candidato | Bloqueo explícito sin resolver tool producción |
| E14 / F06 | Derivado SQL/export/resumen usa un input reserved | Builder/copiloto intenta leerlo como development | Restricciones/lineage heredadas bloquean acceso, aunque esté agregado o renombrado |
| R09 / F07 | Stop avanzó routing generation | Activación antigua termina tarde | Fencing impide reactivar y la UI no marca active por respuesta tardía |
| R10 / F07 | Scope parcialmente candidato/unknown | Promoción nueva solapada | Bloqueo/replanificación; exposición observada/posible visible |
| U09 / F08 | Cursor fuera de retención y permiso revocado | Reconecta | Resync autorizado; evidencia no filtrada y estado del comando recuperable |
| W06 / §15 | Lease expirado pero worker antiguo continúa | Solicita model/query/runtime dispatch | Broker valida fencing; no efecto nuevo autorizado por lease antiguo |
| M01 / F10 | Detector exploratorio sin evaluación independiente | Solicita binding recurrente | Registro no activo; requiere DetectorVersion/report/decision |
| M02 / F10 | Binding actual revision y monitor candidato validado | Dos cambios concurrentes | CAS autoriza uno; versión anterior e historial preservados |
| P05 / F11 | Mensaje humano describe acción pero no tool event | Mine procedimiento | Mención no prueba ejecución ni guard satisfecha |
| P06 / F11 | Secuencia exitosa solo en casos simples | Planner baja todos los casos | Elegibilidad/counterexamples bloquean generalización; suite exige excepciones |
| A01 / F12 | Features conocidas antes del contacto y datos futuros disponibles | Construye predictor retrospectivo | PredictionCutoff excluye futuro y registra disponibilidad temporal |
| A02 / F12 | Señal de posible contacto | Planner propone mensaje proactivo | Outreach dependencia/autorización separada, no envío implícito |
| S01 / §21 | Usuario tenant A tiene permiso sobre O1 | Adjunta ref de tenant B o provenance false | AccessDenied antes de lectura; service identity no amplía delegación |
| S02 / §21 | Worker no tiene autoridad de policy admin | Solicita aumentar autonomía/publicación | Policy draft permitido según scope, activation denegada |
| S03 / §21 | Fuente revocada presente en prompt/history/scratch | Follow-up solicita model call | Context manifest bloquea; sesión/workspace contaminado se invalida o reconstruye |
| S04 / §21 | Autor no confiable envía digest correcto y assurance executable | Prepare/evaluate/promote | Assurance no aceptado sin producer/runtime autenticado |
| S05 / §21 | Provider mantiene alias pero cambia resolved model | Invoca/evalúa/cache | Diferencia registrada, dependencia/calibración revisada; repetición no fingida |
| S06 / §21 | Provider no expone versión resuelta | Publica evaluation report | version_guarantee unknown explícito; ninguna prueba de determinismo pleno |
| O01 / §22 | Restore viejo anterior a revocación/activation | Reinicia plataforma | Recovery mode cerrado; suppression/authority/routing reconciliados antes de efectos |
| O02 / §22 | Worker anterior a restore conserva token | Intenta dispatch | Recovery epoch/fence rechaza efecto antiguo |
| O03 / §22 | Backfill saturó presupuesto discrecional/CPU | Incidente requiere stop | Reserva control independiente; backfill deferred sin cursor no durable |
| O04 / §22 | Recursos operacionales realmente no disponibles | Contención solicita ejecución | Fallo/pendiente crítico visible y escalación; no restored ficticio |
| O05 / §22 | Binario/esquema/gate nuevo y jobs vivos | Deploy/migration | Drain/fence y compatibilidad; hashes viejos intactos, impacto revalidado |
| O06 / §22 | Modelos o SQL no disponibles | Discovery/gate consulta | No señal «sin problema» ni expansión basada en falta de observación |
| O07 / §22 | Proyección recibe rev3, duplicate rev3, luego rev2 | Reducer procesa | Gap replay/rebuild y no head rollback ni checkpoint que omite eventos |
| O08 / §22 | Schema/enum nuevo no soportado | Consume evento/comando | UnsupportedContractVersion, no unknown bancario ni avance silencioso |
| O09 / §22 | Audit requerido + telemetría sampleada | Saturación de observabilidad | Auditoría persistida; telemetry dropped visible sin labels arbitrarios sensibles |
| U10 / F08 | Dueño desactivado/rol sin miembros | WorkItem decisión necesaria | Routing_failed + fallback autorizado; asignación no concede acceso |
| U11 / F08 | Tool unknown y auth destino incompatible | Handoff humano/canal | Operation refs visibles; reconcile antes de repetir y auth válida solicitada |
| U12 / F08 | Usuario pospone oportunidad | Nueva investigación y cambio crítico | Motor sigue por policy; silencio no significa falso ni oculta incidente |
| U13 / F08 | Comando committed avanzó head | Retry mismo key/payload | Receipt misma operación; expected_revision antiguo no genera nuevo fallo/efecto |
| U14 / F08 | Receipt antiguo y permiso ahora revocado | Retry/lookup | Sin reejecución ni detalle sensible; retorno seguro/denegado según autoridad |
| U15 / F08 | UI sin animación | Observa candidate/job/release | Estado/razón/acciones equivalentes, unknown no es success |
| V01 / §23 | NPS fixture 6 promotores/2 pasivos/2 detractores | Calcula | NPS=40, denom 10 respuestas válidas; no media ni denominador contactos |
| V02 / §23 | CSAT scales incompatibles y no respuesta | Agrega países | No sumatoria bruta; definition incompatible/unknown y response rate explícitos |
| V03 / §23 | Propuesta tool missing con ahorro supuesto alto | Prioriza valor/esfuerzo | Effort/dependency unknown, no «fácil/costo cero»; escenario no observed |

## Journeys de aceptación completos

### J01 — descubrimiento discutido y mejorado

Fuente fixture con recontactos, errores de canal y cohortes de contraste → snapshot → monitor/open discovery → oportunidad → pregunta humana sobre outage → nueva investigación → claim mantenido/matizado/refutado con evidencia → dos alternativas con supuestos declarados → comparación y decisión de continuar/posponer. Verificar historial, refs, queries reales, permisos, denominadores y ausencia de causalidad automática.

### J02 — patrón humano a mejora evaluable

Trazas fixture con secuencia reusable y excepciones → outcome maduro → patrón candidato → exclusión de casos que requieren humano → árbol/skill propuesta → framework fixture prepara → suite derivada con lineage → run baseline/candidate → oráculos → gate → autorización shadow fixture → runtime confirmado → seguimiento simulado declarado. Un caso negativo debe impedir promoción si viola política, incluso con buen ahorro.

### J03 — dependencia concurrente e incidente

Propuesta evaluada + revisión humana → cambio incompatible de tool → aprobación histórica no utilizable → revalidación → release fixture → guardrail crítico → stop/rollback operation con respuesta perdida → reconciliación → incidente confirmado → investigación y regression case → nueva propuesta sin borrar fallo. Verificar que rollback no revierte efectos bancarios ya realizados por suposición.

### J04 — descubrir y convertir un nuevo detector

Mission abierta → investigador descubre cohort/patrón no predefinido → consultas/checks → contraste reservado → DetectorSpec candidato → pruebas de semántica/costo/missingness/dedup → autorización dentro de ámbito → monitor programado → nuevas señales con versión del detector → drift/data-quality feedback. No convertir una consulta exploratoria sobreajustada en vigilancia sin evaluación.

## Qué no prueban estas suites

## Casos HOW derivados de las dos rondas adicionales

Estos casos son criterios de aceptación pendientes de implementación y ejecución.

| ID | Dado | Cuando | Entonces |
|---|---|---|---|
| H01 | Una derivación sobre W4 | Crash antes de CAS | W4 sigue vigente; scratch no se publica y retry parte del parent confirmado |
| H02 | FinishResearch con DraftCommitted | Crash antes de publicación | Recovery retoma validación/publicación sin perder borrador ni crear investigación duplicada |
| H03 | Resultado listo y expediente editado | Concurrente comentario o restricción de scope | Comentario se conserva; restricción exige revalidación, nunca overwrite silencioso |
| H04 | Mismos registros con nueva taxonomía o episodios | Se ejecuta detector | Manifest e identidad reflejan los inputs nuevos; cache incompatible no se reutiliza |
| H05 | Guard con Unknown o ramas solapadas | Se valida/ejecuta árbol | Lógica ternaria correcta; sin exclusividad o prioridad falla validación; tool error no es false |
| H06 | Output válido pero objetivo no observable | Se evalúa candidato | Contract pass y goal unknown separados; gate no declara resolución |
| H07 | Candidato escala casos costosos | Comparación con baseline | Población congelada conserva casos; continuación no observada produce costo parcial |
| H08 | Equipo con delegación circular sin límite | Framework valida TeamChange | Dependency block, no candidato ready ni release |
| H09 | Histórico únicamente closed=true | Se propone oráculo | Resolución queda unknown; cierre no obtiene autoridad de objetivo |
| H10 | Una categoría se divide | Se compara histórico con categorías nuevas | Mapping y cobertura explícitos; no reparto proporcional sin evidencia |
| H11 | Diez paráfrasis de una sola ruta | Se calcula cobertura | Una familia no demuestra diez ramas; requisito sin assertion sigue uncovered |
| H12 | Modelo enviado y respuesta perdida | Worker agota lease | Usage pendiente; no costo cero ni retry ilimitado |
| H13 | Política delega preparación y evaluación | Propuesta automática válida | Mismo builder sin aprobación manual por paso; release requiere autoridad propia |
| H14 | Propuesta rechazada por prioridad | Motor aprende feedback | No-change temporal conserva evidencia; hipótesis no se marca refutada |
| H15 | Juez semántico evalúa comparación | Recibe inputs | Sin identidad/justificación del candidato; rúbrica fijada y desacuerdo reportado |

## Límites de la evidencia de aceptación

No prueban prevalencia/beneficio real del banco, cumplimiento legal definitivo, eficacia universal del modelo, seguridad absoluta ni integración real donde solo hay mocks. Informar por separado: schema/contract validation, fixture runtime, model-in-loop, integración autorizada y resultados productivos maduros.

Antes de efectos reales: suite de aislamiento del launcher real, identidad/permisos del runtime, CAS/fencing de routing efectivo, retención/egress del proveedor, carga/admisión y restore cerrado. Una prueba fixture que rechaza acceso al host no prueba el aislamiento del host real. Esta lista sigue pendiente de ejecución.
