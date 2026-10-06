# Análisis A: atención, automatización y acceso

Fecha 2026-10-01. Inspección completa de manifests HTML propios, templates descomprimidos y scripts DCLogic; no librerías genéricas del bundler. No ejecución visual/backend. Cifras marcadas ejemplo/sintéticas no son resultados del banco.

## Archivo base: nueve tableros

| Tablero / ID | Experiencia y consecuencia para automejora |
|---|---|
| Cliente / `8fb7a4b6-4045-4241-aa39-e73875f00a99` | Chat móvil identifica cargo, confirma, bloquea tarjeta, abre reclamo y seguimiento. `pickYes` alterna confirmación; empieza confirmed=true. Es otro/enviar/hablar humano no ejecutan flujo real. Bloqueo y reclamo son mitigaciones, no resolución definitiva. |
| Analista / `aa680024-cd25-47ab-82a9-c5069d3c8d44` | Cola Todos/Te toca/Nuevos/Esperando, SLA, pausa/disponible/en llamada; chat/correo/transcripción, tabs Copiloto/Herramientas/Cliente, drafts, fuentes, recorrido, accesos, identity/abono/cierre. Plataforma produce eventos; engine no posee contact center. |
| Panorama / `17b0a391-6e3c-42d1-80e2-e793f969016e` | 4.412 contactos semana; árbol28%/AI51%/humano21%;1.140 mitigados luego escalados; CSAT1–4; tres insights abribles. Requiere read model con periodo/denominador/provenance y mitigación separada de cierre. |
| Tema abierto / `7488f8ea-ba74-4efc-8c40-ff616c86da6b` | Variante panorama startOpen, no detector independiente. Oportunidad enlaza patrón, casos y propuesta. |
| Propuesta / `a7d7866d-fd4c-4ca3-bb77-c9fcf55bd3f9` | Cinco ejemplos comparan humano/candidato paso a paso y tiempos;88%/120 held-out. Tarjeta, transferencia, servicio, depósito, duplicado. No dinero/fraude/disputa abierta. Paired evaluation con estados y effects, no comparación textual solamente. |
| Prueba / `aa970d1d-feaf-498a-bf94-984ec618454c` | Cuatro tabs: normal, portugués, datos ajenos, tool falla dos veces. `pick` cambia escenario prefabricado. Enviar no runner real. Promesa humano2h requiere política/cola verificable. |
| Activación / `ce2f9bd7-cdf6-4a48-b78f-2eab02eef019` | 88%/120,0inseguros/300,4pruebas humanas;10/50/100%; parar ante inseguro o >1% escalamiento perdido. `pick` sólo cambia porcentaje, no deployment. Approval vinculada a manifest/policy/eval digests; exploración humana opcional, no gate obligatorio de cada mejora. |
| Agentes / `7bf0b749-6e32-41e1-9525-7b58b621b450` | Filtros activo/prueba/propuesto; juez/disputas/movimientos/app/pagos/intereses. Proyección comercial sobre Core: outputs incluyen árbol/Flow/Jev/context/Tool, no todo agente. Intereses propone reversión: no autoridad inferida. |
| Ficha / `3ca8bf39-125c-41cc-9031-03d3923140a5` | Tabs resumen/historial/docs/versiones; permisos por tool, documentos citados,v1/v2/v2.1/volver. Registry lineage y rollback inmutable; aprendizaje/eval separados. |

## Analista: escenarios completos y handlers

Props view: copiloto/envivo/llamada/espera/saliente/correo/herramientas/errorHerramienta/cliente/recorrido/contraida/borrador/abono/cerrar/vacia/pausa/esperando/aprobado/rechazado/verificar/verificada.

- Cargo alto: árbol mitiga → agente escala → humano confirma posesión → identity → abono fuera de límite → supervisora decide. Pending tiene30min/reasignación; approved sólo informa tras efecto confirmado; rejected sigue investigación.
- Cliente molesta:4mensajes sin respuesta6min, cargo no encontrado, sin movimientos recientes. Señal de latencia/enrutamiento, no fraude probado.
- Portugués: asignación por service_agents.languages; caso de estrés aumentado explícito; sin productos. No inventar operaciones.
- Correo: sin sesión, identity antes de divulgar cuenta; hilos y drafts. Falta expiración de identity en hilo asincrónico.
- Phone entrante: IVR identidad,cola2:13, transcript/hold; AI no atiende teléfono actual; step-up antes de abono.
- Saliente regulador: origenCONDUSEF/canalphone, sin identidad; preguntas y respuesta firmada por supervisora. Origin!=channel.
- Tool error: app no entrega aviso; retry/email alternativo, distinguir attempt/sent/delivered y controlar idempotencia.
- Cierre: resuelto/no resuelto; motivos transaccional/queja/producto/técnico/comercial/retención; seguimiento mañana/dos días/ninguno, acciones y encuesta.

Handlers reales locales: togglePause/toggleHold/toggleList/toggleRoute/select-case/tab/showDraft/hideDraft/startAbono/openClose/confirmOverlay/closeOverlay/finish identity. Muchos tools y nextAlts son `() => {}`; call validar no sabe respuesta también noop; finish sólo marca done. Cerrar modal no persiste ni valida outcome. UI approval abono es de caso, no publicación Registry.

Identity: preguntas SQ7/SQ10 para abono; SQ2/SQ10 correo; SQ4/SQ2 saliente. Ficha oculta campos mientras pregunta abierta. Correctas literales en fuente del prototipo no deben llegar a prompts/wiki/logs; `finish` no valida respuestas realmente. Falta fail/expiry/third-question real. Lectura interna preidentity necesita scope explícito; no equivale a permiso de disclosure.

## Hallazgos adversariales

- Insight pagos293/412=71%,6min/caso y54h/mes:293×6/60=29,3h; falta población/periodo del cálculo54. No copiar como métrica normativa.
- Portugués31%vs19% «casi doble» es1,63x; confianza<0,7 en38%,129/1200 asesores. Ejemplo, no evidencia original.
- Duplicados34%desacuerdo/218 y cierre1/3: desacuerdo humano no prueba mejora ni permiso; validar outcome/política.
- UI agrupa árbol/AI/humano; catálogo nivel0/nivel1. Mapear explícitamente clasificador y nuestras4capas, no eliminarL2.
- FichaR4/R6/R1–R7/umbral1M; analista reglas1–11/escaladoR10/autoridad1,5M. Policy digest versionado prevalece frente a textos.
- Ficha61%resuelto vs versión2 63%resolución segura: denominadores/ventanas no aclarados.
- Disputa abierta verde en historial puede ser éxito operacional, no cierre definitivo.
- Proactividad aparece como insight terminado; falta visibilidad de investigación/trials/rechazos/revisión autónoma.
- Editar instrucciones/volver versión deben pasar nuevo manifest/gates; no bypass.
- Texto de cierre sin resolver puede afirmar solución definitiva: asegurar consistencia y evidencia.

## Archivo(1): quince tableros de acceso

| Tablero / ID | Comportamiento |
|---|---|
| Backoffice login / `2f8333ff-d614-4dfb-a397-72fa8dd7f0e7` | Microsoft o password; rol desde cuenta; MFA;5fallos15min; ingreso auditado. |
| Backoffice MFA / `0a986da7-f048-4f2e-afae-63842ce11fae` | TOTP30s/SMS/respaldo un uso;6dígitos; confiar8h; geo/device. |
| Login error / `cffd0c2f-9b42-4c34-a98e-b7435cdbc1cc` | Variante state=error login. |
| MFA error / `d0b0e2de-9553-4195-a7b5-465d173e4cdb` | Variante state=error MFA. |
| Backoffice bloqueo / `78840005-9181-4d09-9f47-0eaa92fce4e4` |15min/recovery/Microsoft/no fui yo. |
| Web login / `205fb3f4-ebc5-4271-8d87-8e8fdb45703f` | CC/CE/CURP/DNI/Pasaporte/password;ES/PT;ayuda/apertura. |
| Web código / `8cdf39c0-95c6-42c5-8e0f-7362a3a0681b` | SMS6dígitos,5minexpiry,42scooldown,callalternativa. |
| App login / `5146f49f-e1c5-463c-ae2e-0a2491925772` |ES/PT,rememberdocument,recovery. |
| App código / `f9134fed-7bfe-4b80-aee5-d2963a0901fb` |SMS/cooldown/call;no compartir OTP por chat/teléfono. |
| Web login error / `0c0e9755-2384-41df-a4b5-ac6be9291639` | Variante login. |
| Web SMS error / `94aafec4-a58b-43c8-9d18-f87babd21408` | Variante código. |
| Web bloqueo / `91cb596a-e1e8-4b74-8fc7-fdc827d9228b` |3fallos30min;dinero/tarjetas siguen;recovery/reporte. |
| App login error / `e695cc3d-1856-473c-b682-93f07104e2d9` | Variante login. |
| App SMS error / `36c10b91-ecf1-415c-a648-fb8fb81389fc` | Variante código. |
| App bloqueo / `73cab0fa-bb1a-4e98-a2aa-220fa0dd01d4` |3fallos30min/recovery/call. |

Handlers propios: error depende props.state; métodos MFA cambian selección; web setEs/setPt y app toggle traducen textos. Login/OTP/recovery no implementan auth real.

Auth/SSO/MFA son IdP/plataforma. Engine recibe principal/role/scope/session/proof/expiry autenticados, nunca password/OTP. Role switch demo no autoridad. Fallos/bloqueos/demoraSMS pueden señales sanitizadas si plataforma provee events. No inferir credentials del dataset ni enrollmentMFA desde service_agents.phone. Valores5/15min,3/30min,8h,5min son ejemplos configurables, no regulaciones. Microsoft desde bloqueo requiere política unificada contra bypass; geo/document/phone/email son PII a minimizar.

## Integración recomendada

Reutilizar entidades existentes, no tabla por pantalla. Read models panorama/opportunity/proposalcomparison/scenariotrial/releasereadiness/versionhistory. Events correlacionados por case/session/actor/artefactdigest: queue/handoff, drafts accepted/edited, tools attempted/succeeded/failed, approvals, delivery, identityproof, closure/recontact. Evaluate safe resolution/mitigation/correcthandoff/effects/delivery/efforthuman; sandbox negatives y separación learning/heldout. Aprobación mínima, visibilidad máxima. UI resumen evidencia verificable sin chain-of-thought privada. Cifras necesitan denominator/window/provenance; cero fallos observados no riesgo cero.

## Ronda 2 — contraste B/C y spec §§1/6/7/16/20/24.1

Lectura cruzada de ANALISIS_DESIGN_B/C y secciones indicadas. §24.1 ya resuelve ownership, tres autoridades, estados de journey, internal-vs-disclosure, SLA y revocación. No repetir esos hallazgos como pendientes. Los siguientes son detalles implementables aún débiles en las superficies públicas de integración (debug §25 sí tiene rutas más precisas).

| Prioridad / gap | Contrato mínimo sugerido sin nueva tabla | Prueba concreta |
|---|---|---|
| P1 — API producto sigue conceptual | Tabla OpenAPI de `GET opportunities`, detail/proposal/evaluation, `POST expert-feedback`, `POST decision-response`, commands y command-status con schemas existentes; registrar consumer/product role por ruta. No inventar endpoints Core. | Plataforma de prueba completa insight→compare→dev trial→decision con API únicamente; validación response/request, forbidden y versiónN/N−1. |
| P1 — `DecisionRequest` requiere tipo y estado explícitos | `kind=release_authority / evidence_conflict / expert_review / dependency_authority`, artifact/hash/base/policy objetivo, allowed_responses, expires_at, status y external authority ref. Approve workflowCore no se confunde con responder feedback. Issuer humano definido en §27 se reutiliza. | Dos respuestas concurrentes: una CAS gana; expirado/stale rechazado; feedback de experto no cambia Core approval; respuesta de otrotenant no revela request. |
| P1 — opinión experta no puede sobrescribir evidencia | Artefacto append-only ExpertFeedback con actor/purpose/ref/revision/text tratado/provenance y `kind=objection|additional_evidence|interpretation`; dispara verificación sucesora, no edición del finding/refutación automática. | Objeción tardía duranteeval crea nuevo run/ref, original conserva evidence; texto malicioso no da grants; conocimiento experto sin fuente continúa assumption. |
| P1 — continuidad UI: qué hace «Ahora no» | Separar atención UI de estado del trabajo: dismissed/read/snoozed son metadata de usuario/plataforma; no pausan engine ni eliminan oportunidad. SLA humano sólo corre para request real con autoridad, no para cada insight. | Cerrar panel/relogin no cancela run; request reabrible; otro usuario sigue viendo pending; expiración se publica durable aunque SSE desconectado. |
| P1 — identidad producto→API motor no está cerrada al nivel wire | Reutilizar proveedorOIDC de debug, documentar audience/issuer/token roles→Pulso actions, scopes tenant/purpose/environment y revocation; Core JWS sigue separado. Service auth ingest no sirve para decisión humana/debug. | Token con issuer/aud erróneo, service token en humancommand, cambio de role y revocation en vuelo; no fallback a rol visibleUI ni actor enviado enbody. |
| P2 — filtros/métricas no totalmente reproducibles en UI | Query params typed país/canal/idioma/periodo/source/environment + timezone/cutoff, stable cursor y projectionrev; cada métrica n/window/denominator/unknown/method/version. Satisfacción no asumir CSATNPS; annotation datoejemplo. | Cambiar idioma sólo cambia presentación, no universo sin filtro; páginas durante arrivals no duplican; all+test no contamina producción; cálculo54h rechaza fórmula inconsistente. |
| P2 — trial libre humano no debe contaminar campaña | `dev_trial` con fixedcandidateHash/sandboxstate/actor/session/budget/trace refs, artefacto team_generated separado; streaming command-status y efecto/oracle. No forma parte del finalLocked ni pruebaestadística por sí solo. | Editar candidato mientraschat prueba mantiene versionref; retry no repite action; falla provider reflejaunknown; feedback humano no accede final. |
| P2 — capability discovery para UI incompatible upstream | Read model capabilities supported/unsupported/dependency_blocked para tool/knowledge/Flow/Jev/Agent/group/rollout; commands disponibles por autoridad + estado. Unsupportedcanary no debe mostrarse como operación real en engine. | Selector100% contra adaptador sincanary devuelve typedunsupported sin cambiaralias; nuevaTool sinexecutor muestra dependencyblocked; UIcatalog incluyekindsheterogéneos. |

### E2E cruzado recomendado

App emite ayuda contextual → plataforma preserva reftransaction/session → contact hold/identity/policy/tool events → engine ingestion → sensor no dirigido → oportunidad → candidatoFlow/decisionmodel/tool existente → pairedtrial → evaluated → request humano → credencialCore válida → staging confirmado → projectionproduct. Corrida alternativa: experto objeta duringeval, policyrevoked, notificationunknown y refreshSSE; nunca produce éxito ficticio ni stepmanualobligatorio. Las partes de atención son fixtures de integración, no construir app/SSO/colas.

### Conclusión de ronda 2

El spec está alineado semánticamente con producto y conserva autonomía. No sería todavía contrato frontend/backend independiente para integrar experiencias si no se materializa la matriz API pública/DTO/command-status/identity. Se puede resolver en U07/U21/U24/U29 existentes, sin añadir microservicios ni tablas por pantalla. Los tests genéricos403/409/SSE no prueban por sí solos los escenarios anteriores.

## Ronda 3 — revisión implementador de §§20.1/24.1/24.2/21

§20.1 cierra la mayoría de gaps de ronda2: rutas propias, estados async, OIDC separado de Core JWS, feedback append-only, tipos de decisiones, métricas y capacidades. §24.2 cierra unión de fuentes y output tools con executor existente. No es necesario añadir más servicios. Restan precisiones wire/backend, no rediseño de producto:

| Prioridad / referencia | Problema preciso | Fix mínimo y test |
|---|---|---|
| P1 / §24.2 PlatformEvent | `source_sequence` se lista como campo requerido, pero texto permite fuentes sin secuencia. Dos implementadores podrían rechazar dichas fuentes o inventar contador. | Declarar `source_sequence: optional`, scope/ref del stream sólo si existe; digest/event_id siempre requeridos. Test fuente sin seq admitida con coverage unknown y mismoID/digest dedup; distinto digest conflict. |
| P1 / §20.1 commands vs §19 jobs | CommandStatus exige accepted/running/succeeded/failed/unknown, pero jobs tienen queued/retry_wait/waiting_dependency/complete/dead y ledger externo otros estados. Falta resolver command_ref→owner y mapping, en especial reverify con jobs descendientes. | CommandRef tipado `{kind:job|external_command,id}` o artifact común con refs; tabla mapping y completion del comando al recibo de su operación, no todo el run. Test crash/retry_wait/dependencyunknown/complete reconstruye mismo status_url sin tabla adicional. |
| P1 / §20.1 DecisionRequest | approve/reject apuntan proposal/hash; publish apunta proposal aprobada; promote/revoke apuntan release/alias. `target hash/revision` y candidate current no bastan para todas operaciones. | Unión por operation con proposal_ref/hash/rev o release_ref/expected_alias según upstream. Nunca fabricar CAS Core donde no existe; reconciliación §27. Tests promote sobre release activa, revoke de release prod denegado, refresh alias concurrente unknown/stale según evidencia real. |
| P1 / §20.1 trial | POST devuelve command_status pero no existe DTO de resultado detallado/trial ni ruta de readback definida. receipt_ref sin enlace accesible no basta para chat pasos/veredicto. | `GET /trials/{id}` o command.resulting_ref resuelve ruta autorizada existente; TrialProjection incluye hash/config/scenario/environment/stage, transcript tratado, receipts/effects/oracle result/cost. Test API-only enviartrial→poll→ver acciones y efectos, y trialunknown/redacted. |
| P2 / §§6/20/20.1 | Contratos generales exigen idempotency_key en cuerpo; nuevaAPI prescribe header. `expected_revision` podría referir projection_revision vs mutablehead vs decisión. | Header autoridad wire, adaptar a command interno; schema define expected_revision como domain/headrevision en cada ruta; projectionrevision nunca usada para CAS autoritativo. Test header/body discrepante denegado o bodycampo prohibido; snapshot viejo pero domainrevision igual no falso409. |
| P2 / §20.1 decisiones | Estado responded dice respuesta durable pero efecto externo puede unknown. Expiry+sweeper o nuevo request podría repetir operación mientras anterior sigue incierta. | Response consume request una vez; status responded separado commandstatus. Expiry sólo pending por CAS; unknown mantiene linkedcommand y no crea reintento externo automático. Test respuestaendeadline con sweeper, ackperdido y dobleclick no segundo efecto. |
| P2 / §20.1 OIDC / §25 debug | `evolution:debug` y roles debug_viewer/operator no tienen mapping explícito; JWT offline + JWKS no garantiza revocación inmediata. | Mapping versionado a acciones/roles, no debug genérico grants mutación; revocation por grant overlay verificado en frontera, failclosed ante estado ausente para mutación. Test viewer token con scopedebug no pausa; admin suspendido token aún válido no publica. |
| P2 / §20.1 feedback | Texto “tratado” no aclara dónde se sanea y rechazo de pii/refsfinal antes de artifact duradero. | API admission guard limita bytes/formato, valida refs/tenant/partition y redacta/rechaza antes de PG/S3/jobs/log. Test feedback conOTP ficticio, finalref, cross-tenantref y promptinjection conserva sólo audit permitido. |

### Cobertura versus implementación

Los schemas/OpenAPI referenciados son entregables a materializar en U07/U21, no archivos hoy presentes: raíz `contracts/` no existe al inspeccionar este workspace. Esto no invalida spec propuesto, pero significa que una aprobación debe distinguir diseño leído de contrato wire compilado. U24 se define como consola técnica; §20.1 le asigna flowproducto para contractconsumer. Aclarar que dicho recorrido es consumidor de prueba/headless, no autorización de construirF8 o un segundofrontend.

Veredicto: arquitectura/ownership alineados y suficientemente precisos para iniciar los primeros cortes; no afirmar interfazAPI100%cerrada hasta resolver mappings anteriores y versionar fixtures/schemas. Son fixes pequeños que evitan incompatibilidad backend/front, sin sobreingeniería.

## Ronda 4 — cierre de contrato y auditoría inversa §§1–15

§20.2 resuelve los ocho gaps anteriores: CommandRef discriminado, resultado trial, targetdecision discriminado, reauth externa sin almacenar JWS, CAS/expiry/revision y admission. No aparecen bloqueos arquitectónicos nuevos. Quedan dos incoherencias normativas concretas a corregir antes de implementar mapping API, y una ruta a cerrar con su primer test:

1. **Estados: §15 versus §20.2.** Ledger durable §15 usa `prepared→sent→confirmed|rejected|unknown→reconciled`; §20.2 mapea `pending/dispatching/uncertain`, que no pertenecen al reducer. Jobs `deferred/superseded` de §15 no están mapeados. Fix: mantener reducer§15 como autoridad, mapear prepared→accepted, sent→running, confirmed→succeeded conreceipt, rejected→failed, unknown→unknown, reconciled según receipt; deferred→accepted y superseded→failed/code superseded. Efecto incierto dominajobcomplete. Test table-driven exhaustivo por enum + receipt/outcome. No introducir otro enum persistido.
2. **Rutas públicas: §15 versus §20.1/20.2.** API mínima §15 todavía presenta `/v1/opportunities`, `/v1/proposals` y `/v1/activity`, mientras productAPI canónica es `/api/v1/evolution/...`. No basta coexistencia sin decidir consumer/alias. Fix sustitución del párrafo §15: remitir a §20.1/20.2 como canónico; superficies extra run/discovery/release/memory/observation se enumeran en misma base sólo cuando consumer/test lo requiera. Mantener internalplatform/debug/gateway propios. Test OpenAPI enumera una única ruta por operationID, no alias casual.
3. **Trial turn continuado:** §20.2 define comportamiento y CAS pero no ruta/método del turno. No bloquea trial single-shot ni bootstrap; sí bloquea integrar chat exploratorio libre. Fix mínimo `POST /trials/{id}/turns` con treatedinput/expectedrevision/idempotency y202CommandRef, nunca nuevo initialtrial. Contracttest dos turns concurrentes, turno tras cierre y scopeotra sesión. Resolver en U20/U24 antes de trial multitur n.

### Auditoría inversa: cambios de producto en texto anterior

Leí §§1–15 por conjuntos (norte/ownership; datos/arquitectura; persistencia/contratos; flujos/operación; casos/DoD/contract). No recomiendo reescribir todo ni duplicar tabla de pantallas. Reemplazos útiles:

- §1: ownership y visibilidad ya correctos; sumar referencia a producto local como punto de partida UX y API canónica, sin ampliar F7/F8.
- §3: fuentes complementarias ya correctas; referencia puntual a unión platformevent§24.2 y requestedreply protege interpretación de recontacto. No redefinir joins históricos por diseño.
- §5: `pulso_decisions` expresa autoridadhumana pero ahora también evidencehelp/dependencyhelp; aclarar que payloadtipado DecisionRequest en artefacto y tabla mantiene lifecycle/index, no añadir todas columnas de pantalla. Schema antes de tests de U21.
- §6: observeplatform ya actualizado a batchunión; idempotency interna no contradice headerwire porque §20.2 distingue correctamente. No otro cambio requerido.
- §7: F1–F8 cubren autonomía/efectos/ownership; referenciar feedback→reverify/trialsdev como entradas excepcionales, no convertir en fases humanas obligatorias.
- §§8–10: pools/o11y/deployment separados ya coherentes; producto nuevo no requiere IdP/runtime atención propios ni nuevos microservicios.
- §11: S6 integra API/feed/debug; agregar cross-reference a testsconsumer headless §20.2, no browserF8. Modelo de métricas/proyecciones también en S3/S6 para no retrasarlo al frontendfinal.
- §12: DoD preserva visión; no liberar implementación sin aprobación. `razonamiento operativo` se debe leer como summary receipts, no CoT; §20.1 ya normativo.
- §13: añadir `design/`+análisis como fuentes de producto, explicitly fixtures no políticas reales. Facilita trazabilidad más que nuevoADR.
- §14: contratos CSAT1–5 frente diseño1–4 son fuentes distintas; conservar fuente real con unit/scale, no convertir silenciosamente. Existe restricción semántica §§20.1/24.1. No copiar 54h/umbral1M/PT como verdades.
- §15: dos reemplazos esenciales arriba (reducer/mapping y API canónica). Son las únicas contradicciones concretas de las primeras15 que impiden implementadores distintos coincidir.

### Veredicto cerrado

Listo para llevar a TDD incremental tras sustituir los dos párrafos contradictorios; ruta de turno queda criterio de aceptación del corte de trial interactivo. No exigir otro ciclo de diseño global ni implementación de plataforma. Compatibilidadwire ejecutable/SSOreal/Coreconnect siguen gates de implementación honestos, no cosas acreditadas por esta revisión documental. Diseño, contrato propuesto y sistema construido son estados distintos.
