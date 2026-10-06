# Análisis de producto: supervisión y automatización (archivos 2 y 3)

Fecha: 2026-10-01. Fuentes: `design/Plataforma de Contact Center(2).html` y `(3).html`. Inspección de los ocho boards de cada archivo, sus templates anidados, componentes importados y lógica `Component extends DCLogic`. No se verificó ejecución renderizada; los comportamientos siguientes se derivan del código del prototipo, no son garantías de un backend implementado.

## 1. Cómo leer estas fuentes

Cada archivo es un bundle HTML con `__bundler/page_order`, manifest comprimido y ocho páginas. Varias páginas son estados iniciales distintos de un componente compartido mediante `dc-import`, no ocho aplicaciones independientes. Leer solamente el template del board deja fuera contenido importante: hay que decodificar el manifest de la página y el HTML importado. Los textos/arrays son fixtures locales y los handlers cambian `this.state`; no prueban persistencia, autoridad, envío bancario, LLM, evaluación o despliegue reales.

## 2. Archivo (2): supervisora

| Board / UUID | Experiencia y comportamiento observado | Contrato que necesita la plataforma |
|---|---|---|
| Equipo y colas / `5ea87af5-8401-409c-b80e-60563199e07e` | Fraudes, turno mañana, 28 analistas. Colas con pendientes, antigüedad y riesgo SLA; filtros conectado/pausa/desconectado/vacaciones; sugerencia mover dos casos en portugués a persona disponible | Snapshot de cola, idioma/habilidades, canal, capacidad y asignación. `move` cambia fixture local; «Elegir otra persona» carece de handler |
| Aviso sin interrumpir / `d3c3e11f-c056-43b0-8b21-a810f664f056` | `SuTeam toast=true`: aviso de aprobación nueva, revisar o posponer | Notificación dirigida y pendiente durable, no modal obligatorio ni pérdida al descartarla |
| Por aprobar / `69862845-b799-4d76-a024-6879f377ebee` | Cola ordenada por vencimiento, filtros solicitante humano/IA. Hechos, notas, consecuencias y decisión | Solicitud de acción con parámetros fijados, actor, caso, política, vencimiento y destino de retorno |
| Revisar analista / `25eeaede-043b-4a65-be8e-24cba2dc75a3` | Estado específico de `SuApprovals`: abono supera autoridad del asesor | Decisión autorizada y ejecución posterior separadas |
| Aprobada / `74dd20ed-69d7-469a-b798-c359fbdccc00` | Estado inicial aprobado, informa aplicación verificada y retorno al asesor | Resultado de ejecución comprobado en sistema de origen; no inferirlo del click |
| Revisar agente / `7d058278-c14e-49e0-9db5-bc940df9013a` | Disputa fuera de plazo; propone nota al agente | Excepción de política, devolución dirigida, identidad del responsable |
| Rechazada / `ba56a1bc-97e1-49aa-b67c-902c46b671af` | Estado inicial rechazado; agente explica plazo y ofrece humano | Rechazo no equivale cierre; conservar caso abierto y razón |
| Auditoría / `3e9a20c4-2051-4bb8-a1d0-0d05c610a16a` | Filtros árbol/juez/agente/persona y sólo mutaciones; selección revela herramienta, permiso, datos, handoff y verificación | Feed auditable de hechos ocurridos, inputs autorizados y efectos; vínculo a conversación |

Cuatro fixtures de aprobación: respuesta a CONDUSEF con firma, disputa a 115 días, abono COP por encima del límite Specialist y disputa a 152 días. El texto establece 30 min y reasignación a otra supervisora del turno, pero los tiempos son valores estáticos: no existe scheduler probado. Aprobación/rechazo cambia un mapa local `done`; el resultado bancario es texto predefinido. Nota visible al destinatario no tiene edición/persistencia demostrada.

Auditoría diferencia juez, árbol, agente y persona. Narra sesión → rama → bloqueo confirmado → reclamo → handoff con hechos verificados y preguntas pendientes → humano → verificación de identidad → solicitud de autoridad → ejecución a nombre del asesor. Otro caso procede de regulador y llamada saliente sin identidad del canal. Respuestas de seguridad se validan y descartan, además de ocultar campos al asesor durante la verificación: requisito importante para sandbox y telemetría, no prueba funcional del prototipo.

El propio pie separa datos `service_agents` (nombres, idiomas, canal) de estado vivo/colas/abiertos de ejemplo. No importar estos fixtures como métricas comprobadas.

## 3. Archivo (3): automatización

| Board / UUID | Experiencia y estados | Implicación para automejora |
|---|---|---|
| Panorama / `544d6fc6-4874-436e-a8da-f1d45629ae1a` | KPIs semanales, cierre por árbol/IA/persona, mitigaciones que no cierran; tres temas requieren atención | Proyección resumida de oportunidades, salud y versión con denominadores independientes |
| Tema abierto / `6102a28a-f248-4e5f-a6a4-4674a35da393` | Mismo Home con `startOpen`: panel de evidencia, pasos humanos, impacto y CTA | Oportunidad durable accesible desde insight, no distinta entidad por cada pantalla |
| Árbol / `7e80ea30-4bc9-4950-8c5d-73bffafa9e79` | Filtros cierran/mitigan/en prueba; seis ramas con origen, condiciones, orden de acciones, permisos, resultado y handoff | Output debe abarcar Flow determinista y ramas, no únicamente Agent; trazabilidad señal → artefacto → versión |
| Agentes / `bde93a55-221a-4ba2-b4e2-16b88ac8c429` | Activo/en prueba/propuesto; juez, árbol, agentes mixtos y reversión de intereses propuesta | Catálogo de capacidades UX puede agrupar artefactos Core heterogéneos; «agente» visual no obliga Agent runtime |
| Ficha / `cd932689-9098-42c8-9247-164ee910892f` | Resumen, historial, documentos base, versiones; tools con permisos, límites y fuentes | Paquete versionado con evaluación, referencias de conocimiento, policy refs y outcomes; comparar versiones sin mezclar escenarios |
| Propuesta / `292ca049-095b-41e9-99f8-729a7e066fac` | Cinco ejemplos lado a lado humano/candidato, tiempos y acciones; 88% en 120 held-out | Replay comparable, evidencia por caso y evaluación agregada; ejemplos no constituyen evaluación suficiente |
| Probar / `f715ad8a-b9ef-4105-90d3-15aaaea6a70a` | Normal, portugués, intento acceso a otro cliente y tool fallida; chat y pasos | Escenarios reales reproducibles, autorización de consulta y errores externos; el prototipo sólo cambia pestaña fixture |
| Activar / `46b9d8dd-69f7-4a76-afe4-ba6bd8be1df6` | Gates held-out, seguridad y prueba humana; seleccionar 10/50/100%; detener ante inseguridad o >1% escalamiento perdido | Release request distinto de acción bancaria; selección es local, activar carece de efecto backend demostrado |

### Temas y tipos de output presentes

1. Pagos pendientes: secuencia repetida en 293/412 casos, consultar estado/corte → explicar plazo → abrir caso tras 48 h. Output puede ser rama y flujo, con agente sólo si la variación lo requiere.
2. Portugués: 31% vs 19% escalamiento, confianza baja y cobertura idioma. Output puede ser ajuste del clasificador/Jev, sus ejemplos y test bilingües, o configuración de routing; no necesariamente agente nuevo.
3. Duplicados: humanos discrepan en 34% de 218 casos y piden comprobante/reversión antes de disputa. Output regla/flujo/contexto y evaluación nueva. Discrepancia no prueba que humano tenga razón: es señal investigable.
4. Intereses: propuesta basada en 118 casos; implica mutación financiera y autoridad, no autorización implícita por haber encontrado patrón.

Árbol incluye cargo no reconocido, movimientos, estado de reclamo, app, fraude urgente y pago >48h. Distingue consultas cerradas con confirmación de mitigación seguida de handoff. La capacidad de resolver correctamente incluye escalar: no optimizar sólo contención. Fraude urgente va directo a humano; no exigir escalamiento por todas las capas si política ordena bypass.

## 4. Diferencias y tensiones a resolver en el spec

- Archivo 2 trata decisiones bancarias en casos; archivo 3 trata decisiones de release/mejora. No unir ambos en una aprobación genérica sin tipo y autoridad diferenciados.
- Agrupar IA en el panorama no borra cuatro capas: guardar `layer` real y `artifact_kind`, presentar agrupación explícita. La ficha muestra «Nivel 0 + nivel 1» pero no representa claramente AI avanzada nivel 2.
- Regla R4/R6 en ficha versus reglas 6/7/10 en auditoría y R2 en aprobación no forman política consistente. Límites sin moneda en ficha no son ejecutables; referenciar versión real/simulada de policy, importe y moneda.
- 293 × 6 min = 29,3 h, no 54 h. La proyección mensual podría usar otra ventana/volumen, pero no lo define: demanda fórmula y procedencia.
- 31/19 = 1,63, «casi doble» es interpretación editorial, no prueba causal. Igual duración humana no descarta distinto mix de dificultad.
- Propuesta dice «mismo resultado en 5/5» aunque un ejemplo ofrece aviso futuro y otro confirma cierre; equivalencia requiere oracle semántico explícito y evaluación de efectos.
- Sandbox promete humano en <2h: no emitir compromiso sin SLA autorizado y capacidad. En UI fixture no existe timer ni handoff real.
- «0 inseguros/300», «88%/120» no son certificación general. Mostrar universo, n exacto, fecha, plan/digest, oracle y limitaciones estadísticas.
- 10/50/100% puede existir como selector de intención; motor no permite saltar gates ni ejecutar canary real en E0. Porcentajes corresponden a elegibles del tipo, no toda la base.
- Casos mixtos de producción y prueba en ficha demandan badge/origen y exclusión de tests en KPIs productivos.
- UI dice `products` y `complaints` cambiadas; nuestro dataset histórico permanece inmutable, efectos sandbox van a overlays/tablas nuevas y recibos verificables.
- `WhatsApp` aparece en diseño, no asumir soporte del dataset E0. Contexto de autenticación debe venir de plataforma, no del nombre del canal.

## 5. Contratos propuestos al equipo integrador (no modificar Core sin acuerdo)

Automejora publica read models: oportunidad con problema/evidencia/impacto/estado; candidato con bundle de artefactos y diff; evaluación con casos, grupos, resultados y efectos; release con elegibilidad/riesgo/versiones/fase; timeline autónoma con progreso, bloqueo y decisión pendiente. Plataforma administra asignaciones, presencia, envío al cliente y ejecución financiera; Core ejecuta Flow/decide/Agent/tools bajo permisos. Engine consume señales de todas esas capas, incluidas decisiones humanas, secuencias, fallos de tool, baja confianza y rechazos.

Necesarios para integración: IDs de caso/contacto, actor humano/IA, artefacto y versión, etapa, fecha ocurrida e ingerida, outcome, razón de handoff, inputs/fuentes autorizadas, operación y recibo de efecto, solicitud/decisión de autorización y devolución. Guardar facts verificados separado de inferencias y cuestiones abiertas. No guardar respuestas de seguridad en traces/wiki/UI.

Visibilidad autónoma: estas pantallas empiezan cuando propuesta está lista. Completar spec con investigación/evaluación/iteración visibles automáticamente; «Ahora no» pospone atención sin borrar trabajo; prueba humana es ayuda opcional configurable, no requisito universal que vuelva manual toda la mejora.

## 6. Pruebas de contrato prioritarias

1. Una oportunidad produce árbol, cambio Jev o Flow+Agent según evidencia, no sólo Agent nuevo.
2. Escalar/mitigar no cuenta como cierre; confirmación de consulta enlazada a outcome.
3. Decisión aprobada, ejecución pendiente/fallida y efecto verificado son estados separados.
4. Doble aprobación/reasignación y concurrencia no ejecutan dos abonos; rechazo devuelve razón sin cerrar caso.
5. Read model respeta scope de usuario, sesión y PII; respuestas de seguridad nunca salen del boundary.
6. Handoff entrega facts con evidencia y pendientes sin repetir mutaciones.
7. KPI excluye escenarios de evaluación y casos fuera de ventana; impacto exhibe fórmula/moneda/cohorte.
8. Release pausa por incidente y mantiene baseline; backend rechaza saltos de porcentaje sin gates vigentes.
9. Candidato sin policy/plazo/fuente suficiente bloquea publicación, no inventa horario de corte.
10. Fallo de tool y prompt injection generan resultados observables y evaluaciones reales, no textos de éxito por click.

## 7. Inventario de handlers y límites de interacción

Los componentes originales usan `sc-camel-on-click` y sus imports `onClick`: ambos son bindings; no confundir el segundo con ausencia de interacción.

| Componente | Estado/handlers efectivos en fuente | Controles meramente visuales |
|---|---|---|
| SuTeam | `f`, `moved`, `toast`; `move`, filtro `f.pick`, `dismissToast` | Elegir otra persona |
| SuApprovals | `f`, `cur`, `done`; filtro, seleccionar item, `approve`, `reject`, `goNext`; presets ana/martin y aprobada/rechazada | Cuenta atrás/reasignación se describen pero no corren como timers; nota sugerida no demuestra escritura de feedback |
| SuAudit | `f`, `sel=8`, `acts`; filtros, seleccionar fila, `toggleActs` | Buscar, Exportar, enlace a conversación no son query/export persistidos demostrados |
| Home | `open=-1` o `0`; `n.pick`, `close` | Semana e idioma no tienen handlers de filtro; «Ahora no» sólo cierra panel |
| Tree | `f`, `sel`; filtro y rama `pick` | Pausar rama sin handler; sandbox es enlace |
| Agents | `f`; filtros todos/activos/prueba/propuestos | Crear agente sin handler; algunas fichas son href `#` |
| AgentDetail | `t`; pestañas resumen/historial/docs/versiones | Editar instrucciones sin handler; retirada/volver es dato visible, no rollback ejecutable |
| Proposal | `i`; selector de cinco casos | Tiempos y equivalencia son fixtures; no ejecuta comparación |
| Sandbox | `k=2`; selector de cuatro escenarios | Enviar sin handler, chat no libre ni generación LLM; continuar sólo navega |
| Approve | `j=0`; selector 10/50/100% | Activar sin handler ni canary, gates y cumplimiento son textos fijos |

La fuente define tamaños fijos 1440×900 y scroll interno en algunos paneles; no prueba responsividad, foco de modales, navegación por teclado completa ni retención del estado entre boards.

## 8. Ronda 2 adversarial: cruce con A/C y spec técnico

Leídos análisis A/C y spec §§16–18,20,24.1,27–29. El spec ya protege bridge causal, denominadores, dos gates, autoridad separada y canary no nativo: no reemplazar esas garantías con la simplificación del prototipo. Persisten detalles de integración de producto que conviene hacer normativos mediante proyecciones/artefactos existentes, sin tablas por pantalla.

| Prioridad / contrato faltante o demasiado genérico | Solución concreta compatible | Prueba y unidad existente |
|---|---|---|
| Alta: Home necesita embudo y cierre por capa, pero las tres categorías UX esconden IA1/IA2 y mitigación | `MetricProjection` con metric_ref, window, grain, numerator, denominator, unit, coverage, world, layer_grouping_ref y provenance. `closed_by` mutuamente exclusivo por GoalOutcome; `mitigated_by` multivaluado no se suma al total cerrado. Faltan datos → unknown | U29/U30: episodio tree→IA1→IA2→human cuenta una resolución, tres handoffs y mitigación sin doble cierre; varias goals no mezclan grano caso/objetivo |
| Alta: Home sólo dice qué requiere atención, no ciclo autónomo completo | `ActivityProjection` enlaza opportunity/campaign/run/job y etapa actual; estado observed/investigating/refuted/eligible/building/testing/revising/stopped/ready_for_decision/dependency_blocked. Usa eventos/artefactos actuales, no nueva state machine paralela. Añade intento, último progreso, bloqueo y próxima acción | U24/E13: UI puede observar desde run vacío hasta revisión fallida, sin humano; detener por budget muestra condición para wakeup y no desaparece |
| Alta: Proposal ejemplos comparativos pueden revelar final_locked | `ComparisonProjection` sirve sólo casos dev/aprobados para inspección; baseline receipt, candidate_hash, case refs tratados, pasos/efectos/outcome, adjudicación, tiempos y diferencias. Resultado final sólo resumen autorizado, sin prompts/casos/oracles/trazas detalladas al builder | U20/U24/E08: usuario con constructor abre Proposal y no obtiene canario final por API/exports/SSE; ejemplos destacados no se usan como denominador del 88% |
| Alta: «Mismo resultado» hoy mezcla cierre, apertura de caso y notificación futura | Definir equivalencia conforme bridge/oracle: efecto confirmado, handoff correcto, respuesta sustentada, goal outcome y pendientes. Vista permite equivalent/different/unsafe/unknown, nunca sólo «Igual» fijo | U27: abrir reclamo no equivale resolver disputa; ofrecer aviso sin entrega posterior no empata notificación recibida; candidato eficiente pero unsafe falla |
| Alta: Sandbox libre no coincide con tabs de fixtures | `TrialRequest` referencia bundle pinneado, dev manifest, scenario/fixture y perfil; admite input humano como caso exploratorio, no modifica suite final ni gate. Dev libre crea trial nuevo con scope/seed/receipts y resultado, sin acceso bancario real | U19/U20/U26: tool timeout, prompt injection, ES/PT y scope ajeno corren ejecutor real; input libre no sobrescribe prueba sellada y nunca autoaprueba candidate |
| Alta: Approve muestra tres gates y rollout10/50/100, Core sólo publica staging y promoción humana | `ReleaseReadinessProjection` separa native_core_gate, pulso_improvement_gate, optional_expert_trial, approval, publication, runtime_activation y exposure. Comandos según capabilities; rollout UI es intención unsupported o `pulso_extension_simulation`, no endpoint Core ficticio | U21/U23-A/E11: approve no dice activo; publish confirmado sólo staging; selección100 no fabrica cohortes; dependencia no disponible conserva output y claridad |
| Alta: «se detiene solo» contradice soporte actual de rollback/promoción humana | Autoalarma y stop_request son autónomos; detener exposición requiere recibo de PlatformReleasePort real/simulado. Sin ese puerto marcar capability missing antes de canary, sin prometer parada. Revoke Core humano y aliasprod no equivalen cortar cohortes | U23-A/U29: alerta unsafe con plataforma caída → exposure_unknown + incidente, no stopped ficticio; sinpuerto no empieza exposición |
| Alta: G1 de admin exige otro aprobador, Core permite self-approval | En Pulso crear validation receipt de separación actor/autor para candidato gobernado; bloqueo previo a emitir request Core y condición revalidada al publish. Registrar autor bot/humano y política. No afirmar protección global si writer externo publica directo Core | U21/U35: editorhumano=aprobador denegado aunque Core lo permita; botconstructor→humano válido; policy cambiado trasapprove invalida readiness |
| Media: cambio permiso (4) afecta varios consumidores, spec declara regresión pero UI requiere números verificables | Proyección affected_consumers desde closure/catálogo fijado, completeness y refs de suites impactadas. Permiso aprobado aún requiere executor/policy vigente y candidate reevaluado; scope desconocido bloquea activación, no0consumidores | U17/U18/U35: propuesta quitar confirmación encuentra dependientes; catálogo incompleto unknown; misma tool en varias rutas dispara regresiones sin duplicar universo |
| Media: documentación y versiones en ficha mezclan conocimiento de atención y wiki de aprendizaje | Proyección con artifact_kind, audience, approved status, source/policy refs, exact version e independent wiki ref. Skill conceptual se compila al subset Core; ToolDef sin executor sigue bloqueada | U17/U33: publicar memoria no activa KnowledgeSnapshot; referencia knowledge pendiente visible, no fuente de respuesta autorizada |
| Media: aportación experta/rechazo deben alimentar motor sin convertirse en verdad | `ExpertFeedback` artefacto con actor/purpose/targetref/version, kind objection/correction/hypothesis y evidencerefs opcionales. Nuevo trigger investiga y versiona; no altera evidencia previa ni gold final | U24/U22: «Ahora no» sólo pospone atención; objeción nueva dispara revisión, no borra oportunidad; consejo contradicho por datos queda refutado con provenance |

### Fronteras de gobernanza que no deben confundirse

1. Admin (4) modifica roles/policy/retención de plataforma; engine consume snapshot y revocación. Roles visuales A/S/U/D no son automáticamente roles Registry: mapping externo validado issuer/principal/role/step-up.
2. Supervisora (2) autoriza acción financiera particular; consentimiento cliente (5) indica intención/confirmación, no grant ni aprobación de release.
3. Automatización (3) inspecciona paquetes y solicita publicación; Core exige staff humano firmado. Cambiar de rol en demo no emite esa autoridad.
4. Baja confianza Jev, desacuerdo asesor y consulta repetida generan hipótesis; permisos y políticas no se aprenden por frecuencia. El candidato puede proponer cambio de Policy pero no imponerlo ni evaluar contra policy debilitada por sí mismo.

### Lo que ya está suficientemente especificado y no requiere nuevas entidades

- ChangeSpec/CapabilityBundle y EntityDraft upstream cubren los outputs; no crear Proposal UI adicional como autoridad.
- LayerAttempt/EffectReceipt/InteractionObservation cubren journey y efectos; sumar metadata como versiones de contrato, no tabla por cada board.
- Wiki, artefactos, edges y run events cubren memoria, feedback y actividad autónoma; las nuevas proyecciones se reconstruyen desde ellos.
- Protocolos frozen/continuous E0 y baseline/oracle independientes ya separan aprendizaje de evaluación. Nuevas experiencias no habilitan usar labels ni final_locked.

### Límite de revisión

Este cruce constata coherencia documental con el pin indicado por spec; no vuelve a ejecutar tests Core ni afirma wiring del runtime. No se debe presentar UI fixture como soporte actual de await_approval/subflow/call_agent/canary: el spec conserva explicitamente las capacidades deshabilitadas y coordinación externa.

## 9. Ronda 3 final: implementación de las nuevas §§20.1/24.1/24.2

Las nuevas secciones resuelven la mayoría de hallazgos anteriores: API Pulso separada, scopes/grants, DTOs, comandos CAS, feedback append-only, trials dev, capabilities, métricas y tres autoridades. No detecté contradicción nueva que convierta canary UI en capacidad Core: continúa explícitamente unsupported/simulation. Mantener las restricciones anteriores de §§17/18/27 como invariantes del reducer, no sólo etiquetas UI.

### Hallazgos residuales concretos

| Gravedad | Problema implementable | Aclaración propuesta y test |
|---|---|---|
| Alta | `DecisionResponse` se encola y el bridge obtiene JWS humano, pero el emisor delegado y duración de step-up no están definidos. Worker podría actuar después de expirar sesión, o guardar credencial en command payload | Definir `HumanAuthorizationPort` externo, sin IdP nuevo: autorización ligada a operación/target/revisión, expira y se revalida al dispatch; JWS sólo en transporte efímero, jamás artifact/log/PG. Si issuer no permite emitir después del click, ejecutar operación externa durante ventana autorizada sin transacción PG, o dejar `waiting_human_reauthentication` y nueva autorización. Test cola demora más que TTL: cero petición privilegiada; logout/revoke cancela dispatch, recepción incierta sigue reconcile |
| Media | DecisionRequest agrupa approve/reject/publish/promote/revoke, pero target candidate/hash no sirve igual para revoke/promote que para approve | Unión discriminada por operation: approve/reject fija proposal_id,candidate_hash,rev; publish agrega key y approved receipt; promote fija release_id,target_alias,expected observed alias; revoke fija release_id y razón. No añadir esos campos al wire upstream si no existen. Test opción/tipo equivocado422; release huérfana no se presenta como prod activa |
| Media | TrialRequest admite scenario_ref o input, pero no determina si son mutuamente excluyentes ni cuándo fija namespace/identidad/candidato | DTO oneOf: fixture_trial o exploratory_trial. Resolver dev manifest, pinned release/runtime config y principal sandbox antes de job; guardar TrialPlan artifact inmutable con seed/clock/budget/oracle. Texto libre no es oracle ni gold automáticamente. Test ambos/ninguno422, hash stale409, snapshot revocado403, resultado siempre sandbox y sin tocar final |
| Media | `MetricProjection.source_kind` escalar no representa métrica basada en historial + supuesto de costo + efecto sandbox | Mantener source_kind del resultado primario y dependencies/provenance refs por factor; valor escenario lo expresa ValueModel, no KPI observado. Agregación no convierte heterogeneidad en observado. Test costo supuesto + volumen real conserva assumption y no aparece en ahorro realizado |
| Media | PlatformEvent propone `source_sequence` siempre presente aunque indica fuentes sin secuencia | Campo nullable + SourceContract declara sequence_mode y completeness; dedup source/event_id/digest sigue posible, ordered completeness no. Test evento sin sequence válido bajo contrato apropiado produce coverage_unknown, no error falso ni cadena completa |
| Media | ToolDef propuesto reutilizando executor general con query template podría permitir cambiar operación semántica sin verificar executor/template autorizados | Capability receipt vincula executor_ref/version, template_digest,args_schema,scope/risk/grants y catálogo snapshot. Query template sólo lectura aprobada con parámetros acotados; no SQL libre de LLM en atención. Test template cambiado tras evaluación invalida readiness; resultado incluye source cutoff y autorización por cliente |

### Cómo implementar sin ampliar arquitectura

1. `contracts/product` contiene unions/request DTOs y response fixtures; validación de refs y scopes en app antes de handlers. OpenAPI sale de esos contratos, no de pantallas.
2. Read-model builders ensamblan artifacts/receipts/edges paginados del tenant; redactor autoriza cada ref antes de serializar. Final aggregate permitido no implica que todos sus child refs puedan abrirse.
3. `RegistryWorkflow` reduce estado desde receipts confirmados, no respuestas locales de la UI. `DecisionRequest` fija operación exacta; response CAS produce command/job. Authority proof se verifica en dispatch sin persistir secreto.
4. `EvalCampaign` fija TrialPlan y ComparisonProjection desde manifest dev; final conserva acceso independiente. Resumen muestra los dos gates y cobertura, nunca sólo verde global.
5. `CapabilityAvailability` es snapshot verificable de adaptadores/runtime/config; available depende de executor/prueba/permiso, simulated identifica world, unsupported no degrada a éxito por fixture.
6. `MetricProjection` deriva del mismo MetricSpec que usa el sensor y muestra fórmula/denominador. Clasificación, mitigación, cierre y handoff son dimensiones diferentes.

### Regresiones finales mínimas

- Policy revocada después de freeze y antes de approve/publish bloquea ambas operaciones, aunque escenario histórico siga reproducible.
- Browser recibe202 y pierde respuesta; reload observa command unknown, no release activa. Segunda respuesta distinta409 y misma key recupera command original.
- Expert conoce ejemplos dev; no puede descargar final por comparison, details links, logs, export o feedback que cite ref final.
- Multiartefacto Tool+Flow+Agent requiere executor y dependientes compatibles; si una parte no soportada, propuesta visible bloqueada, no activación parcial.
- Publish sólo staging; promueve humano autorizado; rollback sin alias readback confirmado conserva unknown. Selector100% jamás altera alias por sí mismo.
- Grouping AI combina IA1/IA2 en panorama pero detail preserva ambas y una sola resolución por objetivo.

Conclusión: con estas aclaraciones, las nuevas proyecciones son compatibles con la arquitectura existente. La brecha mayor restante es el transporte de autorización humana para operaciones asíncronas; no resolverla fabricando JWS ni guardando tokens en artefactos. Pruebas propuestas son contrato de implementación, no verificaciones ya ejecutadas.

## 10. Ronda 4 de cierre: veredicto y precisiones mínimas

Revisadas nuevas §20.2 y conjuntos §§16–23/27–29. Contrastados `registry/http.py`, `registry/service.py`, `registry/models.py` y `registry/roles.py` del checkout Core; SHA verificado `53e729d624c8284e906249df84c1a1df84cc8d40`. No ejecuté tests upstream. La autorización humana asíncrona, target discriminado, TrialPlan y factor provenance ya están definidos; la antigua observación alta queda resuelta documentalmente. Ningún cambio de producto habilita auto-publicación, dinero, canary o nodos deshabilitados.

Sólo tres precisiones acotadas requieren alineación antes de fixtures wire:

1. **Target promote:** endpoint real es `POST /aliases/{agent_id}/{alias}`. El target de §20.2 no lleva agent explícito. Agregar agent_ref/id o especificar que adapter resuelve y valida `ReleaseDetail.agent_id` del receipt fijado, no desde input arbitrario. Test release de otro agente rechazada y body upstream mantiene sólo release_id/reason.
2. **release_hash:** `ReleaseDetail` nativo tiene release_id/status/agent_id/entities/knowledge_snapshot/proposal_id/base_release_id/published_by/published_at, no release_hash. Definir hash target como digest Pulso del manifest/closure inmutable y map verificable a release_id; no solicitar campo upstream inexistente ni volver hash una validación de alias. Test mock exacto sin release_hash permite adapter; digest modificado bloquea intención.
3. **Clock E0:** §20.2 refiere disponibilidad del snapshot sin recepción, mientras §28.2 define replay con disponibilidad asumida del timestamp de cada evento/lag0. Alinear: ingesta real snapshot es reloj de recepción local; replay usa el supuesto histórico explícito de §28.2. Test modo replay y observed no comparten automáticamente `available_at`; no afirmar latencia productiva observada.

**Veredicto:** implementable incrementalmente bajo contratos propuestos, con estos tres ajustes mínimos. No necesita otra ronda de ampliación de producto ni nuevas entidades. La implementación debe producir schemas/fixtures y pruebas TDD por corte; «ready para construir» no significa deployment/Core integration completados. Capabilities no soportadas permanecen dependencias visibles sin bloquear investigación sobre fuentes disponibles.
