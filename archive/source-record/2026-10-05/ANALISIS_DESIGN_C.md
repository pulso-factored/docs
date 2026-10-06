# Producto: Administración y app cliente — análisis C

Fecha: 2026-10-01. Fuentes read-only: `design/Plataforma de Contact Center(4).html` y `(5).html`. Se leyeron templates y `class Component extends DCLogic` de bundles anidados gzip: estos archivos no son versiones alternativas de una misma pantalla. No se afirma validación visual ni backend funcional; handlers observados cambian estado local, no persisten en un servicio.

## Archivo (4): Administración

Cuatro boards: Usuarios y roles (`74dff5fa-3e2b-448a-9547-df4973eded9b`), Herramientas y permisos (`4a70c0c7-8623-4511-bf30-301e7740004f`), Políticas y reglas (`f38c5d8b-8b14-4942-b355-2cb5fc84ada6`), Retención (`7ad321cb-89f9-4a39-89a9-82af800203ae`). Component principal: constructor `sec`, `uf`, `user`, `tool`, `rule`, `change`, `roles`; datos en `ROLE`, `LIMIT`, `tools`, `rules`, `retention`, `heads`.

### Pantallas e interacciones

| Pantalla | Presenta y permite | Qué debe aportar automejora |
|---|---|---|
| Usuarios y roles | 32 personas provenientes de service_agents; nivel, idiomas, país, estado; filtros con conteos por rol; selección de persona; toggle de roles y Guardar cambios. Roles A analista, S supervisora, U automatización, D administración. Usuario con U+D marcado cuatro ojos. | Consumir identidad/grants ya autorizados, no implementar directorio. Registrar actor proponente/aprobador y impedir self-approval en cambios gobernados. |
| Herramientas y permisos | Siete tools, versión, alcance y datos, consumidores/dependientes. Nueva consulta creada por copiloto a partir de repeated_query; bloqueo sin confirmación aparece como propuesta pendiente; aprobar/rechazar cambia banner a pasa al sandbox/rechazado. | Producir candidatos de tools además de agentes; lineage de señal/query a artefacto; validar dependientes afectados, permisos y evaluación previa a activación. No convertir aprobación de permiso en despliegue inmediato. |
| Políticas y reglas | 11 reglas de banco sintético + G1 plataforma; valor, origen, ámbito, consecuencia, versión y último cambio; proponer cambio genera nueva versión; sandbox temporal y aprobación de otra persona. | Capturar policy snapshot/digest en runs, pruebas y bundle; reevaluar componentes impactados; no aprender excepciones ni autorizar permisos por frecuencia histórica. |
| Retención | Qué se guarda, PII, duración, receptores y cadencia por entidad. Publica como propuesta a validar con Cumplimiento en tres países. | Aplicar admission/retention/deletion a snapshots, lab, evidencias y memoria derivada, sin inventar autorización ni plazos legales. Registrar borrado/anonimización y evitar resurrección desde caché o artefactos. |

### Tools y límites de responsabilidad

- `listar_transacciones v3`: lectura de cuentas del cliente autenticado; fecha/comercio/importe/divisa/ciudad/estado.
- `compras_recientes_cliente v1`: nueva lectura por patrón repeated_query, para analistas; origen aprobado por Automatización. Un query repetido no basta para publicar SQL arbitrario: revisión de alcance y presupuesto.
- `verificar_identidad v3`: dos preguntas (tercera si falla), contexto previo al contacto; nunca devuelve respuesta correcta; guarda preguntas y resultado, no respuestas. La tool controla determinísticamente; no debe entrar ese secreto a prompts/memoria.
- `bloquear_tarjeta v2`: confirmación explícita B1; propuesta de quitar confirmación, 2 componentes activos afectados. La UI de aprobar no demuestra autorización real ni regresión en dependientes.
- `crear_disputa v4`: confirmación; R2 90 días, fuera del plazo supervisora.
- `abono_provisional v1`: solo humano, saldo simulado, AP1 y límite L1 por nivel.
- `responder_regulador v1`: solo humano, firma supervisora A2; referencia a 262 complaints de dataset, no conteo calculado en este análisis.

Reglas: R1 identidad; R3 titular; H1 portugués humano; R2 90 días; B1 confirmación bloqueo; AP1 cargo identificado/no reconocido/<3 reclamos/tarjeta presente; L1 Junior COP300k/Mid-Senior800k/Senior1.2m/Specialist1.5m; A1 aprobación 30min y reasignación conservando dueño del caso; afirmaciones al cliente solo con evidencia `turn.evidence_ids`; R4 >COP1m o H2 persona; A2 regulador; G1 cuatro ojos. Todas sintéticas. COP y equivalentes MX/AR requieren política FX explícita, no inferir conversión fiable solo por relación de transactions.

Retención propuesta: case/case_close 5 años hora, turn original2/enmascarado5 años hora, routing_step5 años hora, copilot_query1 año diario, tool_call/approval5 años realtime, suggestion1 año diario, signal/component vida+5 años realtime. `routing_step` dice sin PII pero identificadores vinculables requieren clasificación; transcript enmascarado destinado a equipo agentes, no se deduce autorización para proveedor externo. Cabecera contrato histórico v0.2.0 está desactualizada respecto E0 0.5.1; los periodos no son regulación verificada.

### Huecos y escenarios negativos

Guardar roles, Proponer regla y Buscar persona no tienen conducta persistente comprobada. Rechazar anuncia nota pero no captura nota. Nada prueba G1 server-side, auto-escalamiento A1, degradación por usuario ausente, concurrencia, revocación, in-flight runs ni rollback de permisos. Se requiere separar aprobación financiera del caso, revisión de permiso/policy y aprobación de release. Pruebas: proponente=aprobador denegado, aprobación obsoleta tras policy change, dos administradores concurrentes, suspensión usuario/revocación token, tool sin confirmación rechazada aunque LLM diga sí, expiración/aprobador unavailable, borrado propagado a derivados, candidato antes permitido ahora inválido. Handlers realmente presentes: `toggleRole(k)`, `rail.pick`, `userFilters.pick`, `people.pick`, `tools.pick`, `approveChange`, `rejectChange`, `rules.pick`; todos actualizan `setState` local. Su ausencia de integración no demuestra un defecto del futuro producto.

## Archivo (5): app cliente

Ocho boards: Inicio `34fe1906-1c31-4937-ad24-1170c875d1bb`; Movimientos `5cfe3701-41d5-49d3-95e9-0cd4ed410a24`; Detalle `f5aa5533-1ddf-4cbf-8a0c-aa3b61eb9e60`; Ayuda contextual `82c630c9-035e-40e1-b834-075f6ebdabb5`; Detalle en reclamo `bd3329d2-89e4-463d-97fa-17466f8a6901`; Productos `33b1e65c-9594-4e0a-99e5-7d843b57146b`; Soporte `cbfb638c-027f-44db-9677-c918b13bc77c`; Seguimiento `481fd671-d729-4f57-8b8f-eda39e83fc9d`.

### Experiencias

1. Inicio: productos/tarjetas (bloqueada en reclamo, activa, vencida), cupo, últimos movimientos, solicitar producto, pagar/transferir/bloquear/ayuda. CTA pide dato pendiente para reclamo. Pagar/transferir y retiro son enlaces `#`, no features implementadas.
2. Movimientos: tabs Todos/Ingresos/Gastos, agrupación mes, transacciones con estado reclamo, búsqueda. Ingresos vacío muestra texto desde marzo. Tabs Todos/Gastos usan la misma lista de seis egresos; vacío no demuestra consulta universal del histórico.
3. Detalle: monto exacto, timestamp, comercio, categoría/tipo/ciudad/tarjeta/estado/ref; pedir ayuda conserva transaction context. En reclamo muestra bloqueo y acceso al expediente en lugar de abrir duplicado. Descargar comprobante no demuestra generación.
4. Ayuda contextual: chat asistente explícitamente automático, opción persona; cuatro motivos (no reconocido, monto incorrecto, duplicado, libre). No reconocido pide confirmar bloqueo+reclamo; monto solicita importe esperado+humano; duplicado afirma un solo cargo e invita evidencia; libre texto. Handler solo selecciona respuesta fija. No se muestra envío libre, adjunto ni respuesta confirmación/acción.
5. Productos: tres tarjetas con saldo usado, tasa sin periodicidad explicitada, vencimiento y estado. Catálogo cuenta/débito/préstamo/inversión/seguro; crédito revisado humano. No confundir estos CTAs con capacidades del engine.
6. Soporte: entrada genérica chat y motivos no reconocido/bloquear/pago no reflejado/app; expedientes existentes incluyen uno abierto desde oct2024 sin respuesta y otro esperando dato; llamada con número placeholder.
7. Seguimiento: expediente cargo no reconocido; pregunta si compró entradas (no pregunta de identidad); sí/no lo añade al caso y analista lo ve. Timeline recibido, bloqueado, primera respuesta, esperando respuesta/revisando respuesta, respuesta final dentro15 días hábiles. `answered` local es único estado real de simulación, no prueba recepción analista ni cumplimiento SLA. Ambas opciones tienen `sc-camel-on-click="{{answer}}"`: el handler `answer()` conserva sólo `answered=true`, no distingue respuesta sí/no. Otros handlers presentes: `tabs.pick` (movimientos) y `options.pick` (motivo contextual). La navegación usa `href` a componentes `.dc.html`; `#` marca acciones sin destino de producto.

### Afectación del servicio, sin construir la app

Automejora debe consumir selección transaction/product y origen de entrada, identidad sesión verificable, intent inicial frente al inferido, acciones tool y evidencia, solicitud de humano, claims previas/recontacto, estado esperando cliente, respuesta solicitada/recibida y outcomes; estas son fuentes potenciales, no columnas garantizadas presentes. Diferenciar contacto que origina claim, seguimiento de claim existente y respuesta solicitada por banco. Deduplicar journey entre canales/casos con identificadores externos autorizados, no parecido textual. Modelar latencia de cliente vs agente/proceso, SLA por calendario/policy y guardrail contra cerrar éxito antes de resultado.

Punto de valor adicional: descubrir expedientes envejecidos/sin respuesta, preguntas que resuelven confusión entre compra no asistida y no reconocida, entradas contextuales que evitan consultas repetidas, duplicación de soporte. Una pregunta de aclaración eficaz no autoriza resolver fraude ni bloquear tarjeta automáticamente.

### Casos y pruebas a incorporar

- Snapshot transaction antes del contacto; no mezclar valores futuros o synthetic UI con historia real.
- Conservar contexto seleccionado al escalar, pero volver a validar titular/estado en tool boundary.
- Respuesta sí/no idempotente, tardía, doble, de otra sesión, cambio mientras analista actúa; no equivaler a aprobación financiera ni identidad.
- Doble claim en app/llamada; transaction ya reclamada; tarjeta bloqueada desde otro canal; motivo cambia a monto/duplicado/libre.
- Recontacto no significa falla si es respuesta solicitada; abandono no significa resolución; claim esperando cliente no prueba incumplimiento de atención sin regla reloj.
- SLA15 días hábiles depende país/festivos/inicio/pausas; no asumir universal. Fechas UI2025 y expiry2026 son snapshots, no estado actual.
- El prototipo no prueba cuatro capas, traces, failed tools, legal pauses, reanudación, canary ni outcomes. Esos contratos permanecen técnicos.

## Diferencia y conclusión

(4) configura gobierno/autoridad de capacidades; (5) muestra entradas y efectos vistos por cliente. Ambos pertenecen a plataforma integral. Engine lee historia/telemetría y propone bundles compatibles: nueva tool lectura, flujo/árbol de aclaración, policy-safe routing/context/skills/tests. Publicación pasa por validación/evaluación y autoridad de plataforma. Diseño amplía oportunidades más allá de quejas sin forzar una clase ganadora.

## Segunda pasada adversarial: cruces A/B/C y spec

Se revisaron análisis A/B y §§3/5/6/21/24/24.1/28/30 de V2. §24.1 ya resuelve correctamente la separación de tres autoridades, requested_reply frente a recontacto, mitigación frente a resolución, scopes internos y clocks/SLA; no repetirlos como pendientes generales. Persisten estos detalles concretos:

| Prioridad | Ubicación y brecha | Ajuste/contrato y test concreto |
|---|---|---|
| Alta | §21 afirma «No necesita invocar una tool por cada lectura», mientras §29.4 exige ToolExecutor para `lab/query`, `wiki/read`, `wiki/explore`. Libre navegación y API nativa no están redactadas igual. | Declarar que no hay wizard ni catálogo limitado por pregunta; sí capacidades read generales por frontera Core. Agente no tiene shell/filesystem host. Test `wiki/explore` libre dentro grant y lectura host denegada. |
| Alta | §24.1 dice policy change invalida eligibility/release; §6 fija config in-flight; §§5/21 revocación inmediata. Falta distinguir nueva revisión no revocatoria de revocación urgente. | PolicyRevision con vigencia, tipo de cambio y affected refs; pre-run pin reproducible, frontera verifica revocación vigente en cada acción/publicación. Cambio compatible no cancela todas las investigaciones; incompatible bloquea candidato afectado; no insinuar revoke automático upstream sin comando/autoridad. Test policy cambia entre approve/publish y entre tool authorize/dispatch. |
| Alta | Diseño Admin propone tool lectura nueva; §29.5 exige executor, pero «tools nuevas» puede interpretarse como código ejecutable arbitrario creado por builder. | Primer alcance: query plan/param schema autorizado que usa executor existente, o referencia a implementación aprobada. Código/executor nuevo queda dependency_blocked hasta build/test/autoridad externa; ToolDef publicado no demuestra capacidad. Test SQL bounded otro titular/PII/función prohibida y falta executor. |
| Alta | Diseño Admin retención difiere por entidad y receptor/cadencia; §6 RunConfig dueño único de retención podría parecer capaz de ampliar regla administrativa. | Config del motor sólo puede restringir política externa; effective retention=min de límites autorizados aplicables, nunca prolongar por nuevo run/config. Test downgrade purga prompts/FTS/wiki/cache/results; restore aplica tombstones; metadata mínima de audit no conserva payload eliminado. |
| Media | Journey §24.1 declara extensiones pero el wire PlatformObservationBatch §24 acepta EngineEvent nativo. Requested_reply/presencia/acciones humanas no son necesariamente EngineEvent. | Dos adapters/contratos de fuente explícitos dentro ingesta común, sin inventar campos en JSON Core extra=forbid. O bien batch union tipado por source_schema_ref. Test producer Core sin atributo→unknown; producer plataforma con requested_reply validado, cursor separado, no doble conteo timeline. |
| Media | Diseño seguimiento sí/no pierde valor local; spec exige respuesta tardía/doble/cross-session, pero no enumera resultado factual ni correlación de solicitud. | Evento plataforma `reply_requested`/`reply_received` con request_ref, response_ref tratada, available_at y status; propiedad respuesta se guarda en plataforma, engine sólo proyección autorizada. Test sí/no producen observaciones distintas y no cambian identidad/consentimiento. |
| Media | §3 PII directa ausente prompts, §24 raw firmado puede guardarse restringido, diseño prototipo contiene respuestas identidad literales. | Source extraction debe excluir scripts/answers del input para investigación; éstos sólo documentación inspeccionada, jamás fixtures libremente enviados. API debug debe aplicar permisos también a detalles/raw/transcript/export, no sólo ocultar UI. Test prompt/archive/log/export secretos y enlaces cross-tenant. |
| Media | Diseño financiero COP, ficha no dice moneda/tasa periodicidad; §3 USD con fuente pero no política explícita por acción. | Valor negocio USD usa daily_exchange_rates por fecha/ref cuando disponible o supuesto; autorización monetaria usa moneda/FX policy vigentes de sandbox, no tasa de presentación. Test límite exacto±unidad mínima, FX ausente no autoriza acción y producto vencido snapshot no estado live. |
| Media | §30 asigna pruebas producto a unidades existentes pero no hace visibles todos los negativos nuevos en U29/U30/U33. | Matriz UC→unidad→fixture→nivel debe incluir requested_reply no failure, outcome partial, permission stale, retention/restore, delivery unknown, tool creation sin executor. DAG verde no prueba cobertura semántica. |

No pedir construir directorio/colas/app ni nuevo servicio auth; los contratos/fixtures de estas fronteras sí son necesarios para probar el engine sin suplantar la plataforma. Son observaciones técnicas sobre claridad de implementación; no se afirma que el backend futuro tenga estos defectos.

## Tercera pasada: cierre técnico de contrato

Se releen §§20.1/24.1/24.2/21 y sus enlaces §§3/5/6/9/19/28/30. Cambios positivos verificados: lectura21 reconoce executor general;24.2 separa union Core/plataforma, policy pin/revocación, retención no ampliable y executor nuevo no disponible;20.1 scopes por objeto, respuesta CAS, trials dev y métricas versionadas. Persisten reconciliaciones concretas:

| Severidad | Hallazgo preciso | Fix mínimo y evidencia de aceptación |
|---|---|---|
| Alta | §19 declara `POST /v1/decisions/{id}/respond`; §20.1 declara `/decisions/{id}/responses`. Equipo frontend/back no tiene una sola ruta normativa. | Elegir responses (o respond) y actualizar todas las menciones, prefijo `/v1` incluido. U07/U21 contract fixture real request y status para ruta exacta; no crear dos rutas accidentalmente. |
| Alta | §6 `observe_platform` recibe lote InteractionObservation, pero §24.2 recibe union source y reducer produce InteractionObservation. §24 texto anterior presenta envelope EngineEvent exclusivo. | §6 resumir wire union PlatformObservationBatch y salida normalized; §24 envelope viejo limitarlo explícitamente a core_event. Golden core/platform/mixed prueban parsing/schema y separación raw firmado/proyección. |
| Media | §24.2 PlatformEvent lista source_sequence requerido mientras permite fuente sin secuencia; §24 batch from_seq/to_seq y recuperación de gaps aparentan obligatorios para todos. | source_sequence nullable cuando SourceContract declara ausencia; posición transporte broker sí puede existir independientemente. Si tampoco hay posición, offset_or_watermark tipado, dedup event_id y coverage unknown, sin alegar orden completo. Test producer sin seq, reorder, late y mismo ID distinto digest. |
| Media | §24.2 incluye received_at pero eventos plataforma deben respetar available_at en replay igual que §28. Política recibida tarde no puede verse retroactivamente. | Disponibilidad de PlatformEvent=received_at (o clock autorizado documentado), occurred_at se usa ventana; timestamp futuro/inconsistente quality finding. Test response/policy ocurrió antes pero llegó después del corte, invisible hasta recepción; ventanas sucesoras no mutan snapshot. |
| Media | §20.1 comandos devuelven command_ref/status_url; §5 external_commands sólo efectos externos y trabajos internos viven en jobs/artifacts. Falta definir ref discriminada para `GET /commands/{id}`. | CommandRef identifica job interno o comando externo con tenant/type sin tabla adicional. GET resuelve ambos, audita permisos y oculta otro tenant. Test status tras restart/timeouts para trial, feedback y Registry, no ID collision ni pérdida del request. |
| Media | Retención legal hold externa ya bien limitada, pero retención de audit/restore y manifests no define cómo reconocer hold válido. | ExternalPolicyRef o HoldReceipt con autoridad/version/scope/expiry y tratamiento; sin receipt ignora flag. No table nueva. Test hold vencido/revocado y ampliación config rechazada; dataset fuente readonly no se borra por purga derivada. |

Checks complementarios requeridos: `evolution:debug` no concede `evolution:operate/decision`; read scope sin object/purpose no entrega blob/export; JWKS unknown kid/rotación y token revocado no reusa download URL ilimitada. Legal hold no exime separación final_locked. `platform_policy_changed` es aviso/evidencia; payload observado no concede permisos sin autoridad verificada. Propiedad tenant debe provenir binding servicio autorizado, no sólo envelope autodeclarado. Mapear a U05/U07/U29/U33/U34, no crear features por pantalla.

No se encontraron razones para alterar readonly fuente, diez tablas, separación PG Core/eval/control o stack. Se requieren fixes de nomenclatura/contrato y regresión, no agregar microservicios. La inspección es documental y no acredita pruebas implementadas.

## Cuarta pasada de cierre: seguridad/data/infra

Estado comprobado: §6 observe_platform ahora es batch tipado→reducer; §19/20.1 response route canónica `respond`; §24 envelope acepta unión, secuencias nullable y coverage limitada; §20.2 define CommandRef discriminada y lookup, JWS efímero y reauth, TrialPlan/oneOf/readback, scopes/admission, hold externo. Estos cambios cierran hallazgos ronda3, con pruebas asignadas.

**Un ajuste mínimo pendiente:** §20.2 dice «E0 sin recepción usa disponibilidad del snapshot etiquetada». §28.2 usa disponibilidad por evento con ingestion_lag=0 asumido y §29.8 disponibilidad por campo. Un snapshot de bytes completo no habilita todos sus eventos/campos al empezar replay. Reemplazar frase por referencia normativa a §28.2/§29.8: disponibilidad de cada evento/campo al reloj replay, supuesto versionado cuando falta recepción, nunca snapshot completo como permiso temporal. Test U04/U23: bytes de cierre/approval/CSAT están físicamente en snapshot pero invisibles antes de su available_at; preguntas SQ3 final no visibles al inicio.

### Cobertura inversa por sección

| Sección | Producto/seguridad que se confirmó cubierto | Unidad y comprobación futura |
|---|---|---|
| 3 | Datos originales readonly, SourceRef, joined worlds sin falso PK, PII y USD | U03/U04/U08: digests intactos, otro cliente fuera grant, mapping explícito |
| 5 | Diez tablas sin espejo banco, lineage/tombstones, CAS y durabilidad | U02/U06/U33: tx/restart, head stale, restore aplica revocación |
| 6 | Config fija, puertos claros, policy externa no suplantada | U05/U07/U29: schema/union/grant/actor, config no amplía política |
| 9 | Logs-métricas-trazas fuente auxiliar, eventos durable, cardinalidad/población | U29/U30: collector caído no inventa ausencia, denominator separado |
| 19–20.2 | Producto API/read models, comandos status, trials, JWS separado, scopes/admission | U07/U21/U24/U27: token no persiste, expired reauth, concurrent CAS, final refs denegadas |
| 24–24.2 | Core wire intacto y producer propio, policy revision vs revocación, tools executor | U17/U29/U30: unknown capability, late/conflict/coverage, new tool sin executor bloqueada |
| 25 | Debug interno sin banco raw/shell, roles diferenciados, requested vs confirmed | U24/U32/U34: export/cross-tenant/fork/retry unknown, E2E consola |
| 26 | Git/CI/Terraform/docs, check/head manifest y runbooks | U01/U25/U28: version/pin/permissions, reproducir stack, rollback/smoke autorizado |
| 28 | E0 complementa, labels sealed, disponibilidad temporal y contexto identidad | U04/U20-E/U23/U36: negativos identidad/oracle, temporal field leak, no envíos externos |
| 30 | Tests producto mapeados sin nuevas tablas/features por pantalla, TDD/reviewer independiente | Matriz Uxx→UC→test→SHA/entorno, no DAG como prueba implementación |

Veredicto documental: listo para comenzar implementación incremental después de reconciliar una frase temporal; no implica producto implementado ni casos/fixtures/tests existentes. Los escenarios y fronteras cubren diseño sin apropiarse de app, supervisión, IdP o finanzas. No pedir ampliaciones de scope para cerrar esta revisión.
