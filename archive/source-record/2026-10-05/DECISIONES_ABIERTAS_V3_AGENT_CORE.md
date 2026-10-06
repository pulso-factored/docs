# §31 — Decisiones abiertas para el dueño del proyecto

Doce decisiones. Cada una indica pregunta, opciones, recomendación con su razón (verificada contra el SHA `86a7674`, salvo lo marcado "sujeto a verificación"), capacidades (`CAP-xx` de `section31_draft.md`) que **quedan sin construir** hasta decidirla, qué se puede avanzar sin ella y las ediciones de `section31_catalog_and_edits.md` (parte c) que esperan. Los estados `especificada` del borrador asumen la recomendación de cada decisión.

| D | Tema | Bloquea | Avanzable sin decidir |
|---|---|---|---|
| D-1 | Topología del runtime y del bridge | CAP-24..33, 40, 53; variantes in-process de CAP-07/08/16 | registry vía `serve` stock con fábricas; mock, wire, compiler (L1), cliente HTTP |
| D-2 | Quién escribe las siete fábricas; real vs doble por mundo | CAP-24, 29, 49 (etiquetas) | mock, a2, contratos |
| D-3 | Quién construye la imagen del runtime; ADR 0003 | CAP-58, 60, 62 | checkout+`uv` en CI y local (proceso host) |
| D-4 | Cómo ingerir eventos de Core | CAP-34, 35 | detección con dataset y E0 |
| D-5 | Emisor de credencial humana step_up | CAP-43 (fuente), CAP-44, CAP-45 en AWS | local con emisor de prueba |
| D-6 | Topología local de contenedores | CAP-48, 58, 59 | doctor sobre un solo runtime |
| D-7 | Sandbox del gate nativo | CAP-41 | CAP-22 (colas FIFO) |
| D-8 | Cómo leer base y alias | CAP-07, CAP-08 | receipts verificados |
| D-9 | Dónde se valida antes del PUT | CAP-16 (capa L2), CAP-17 | L1 + `/validate` |
| D-10 | Mundo mínimo y kinds del primer corte | CAP-14, 46, 49, 61 | CAP-11..13 |
| D-11 | Cadencia de CI real y gobierno del bump del pin | CAP-57 (cadencia) | jobs mock y a2 |
| D-12 | Identidad de ejecución del bridge y límites de tasa | CAP-04 (principal de run), CAP-31 | invocación con un principal y defaults |

---

## Resumen de decisiones adoptadas (provisionales)

**Estado global: ADOPTADA PROVISIONALMENTE "hasta nuevo aviso" (decisión del dueño, 03-10-2026) — la opción recomendada de cada D-n; pendiente de revisión con el equipo de agent-core.** El título "A CONFIRMAR POR EL DUEÑO" de D-1 queda sustituido por este estado.

| D | Decisión adoptada | Quién debe revisar | Afecta (CAP / U / sección) |
|---|---|---|---|
| D-1 | A: un único proceso `pulso-core-runtime` que compone Core y monta `/internal/v1/*` | Equipo agent-core (composición, `ApiDeps`, pin) | CAP-24..33, 40, 53; variantes in-process de CAP-07/08/16; §27.1, §29.3, §29.8, §31.5; C-01, C-02, C-03, C-05 |
| D-2 | A: Pulso escribe las siete fábricas; dobles etiquetados en `doubles[]` | Agent-core (contrato de fábricas) + plataforma de atención | CAP-24, 29, 49, 61; §31.5 |
| D-3 | A: imagen propia del runtime; ADR 0003 corregido | Agent-core + infra | CAP-58, 60, 62; U25; §31.11.3; ADR 0003; C-03, C-04 |
| D-4 | A: `pulso-core-exporter` con rol Postgres de sólo lectura | Agent-core (esquema de `audit_events`/`reg_events`/`outbox`) | CAP-34, 35; U49/U50; §24 M11, §31.6; C-07 |
| D-5 | A: emisor de prueba local; IdP de la organización o fuera de banda en AWS | Agent-core + seguridad/identidad de la organización | CAP-43, 44, 45; §31.8.1 |
| D-6 | A con PG16 propio para Core | Agent-core (versión PG validada) + infra | CAP-48, 58, 59; §10, §29.8, §31.11.1; C-04, C-06 |
| D-7 | A: colas FIFO precalculadas; banco stateful complementario | Agent-core (`LocalSandbox`, `ScenarioEvaluator`) | CAP-22, 41; U26; §31.7.4 |
| D-8 | A: lectura por el bridge, B como degradación | Agent-core (store de Core, N-02) | CAP-07, 08; §27.3, §31.3; C-08 |
| D-9 | A: prefiltro Rust + dry-run en el bridge + `/validate` | Agent-core (`build_candidate`/`validate_candidate`) | CAP-16 (L2), 17; §27.2 paso 4, §31.4.6; C-09 |
| D-10 | Mundo A (`attention-demo`, `contract_fixture`; C para efecto) y kinds K1 | Agent-core + plataforma de atención (mundo) | CAP-14, 46, 49, 61; §31.4.4, §31.9 |
| D-11 | A: `real-wire` diario/manual/por PR relevante; bump en PR dedicado con revisor independiente | Agent-core + responsable de CI | CAP-57; §27.6, §31.10.5 |
| D-12 | A: principal por `(tenant, rol)` con `RateLimitConfig` explícita | Agent-core (límites por principal) | CAP-04, 31; §31.5.8 |

---


## D-1 — Topología del runtime y del bridge

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: A) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** ¿Cuántos procesos Python hay y quién compone Agent Core? V3 decía a la vez que Rust habla con el `/v1/registry` de `agentcore serve` (§27.1) y con un `core-bridge` que "compone Core in-process" (§29.8); los informes de comunicación y de tasks lo señalaron como contradicción.

**Opciones.**
- **A (S3)**: un único proceso `pulso-core-runtime` que compone las piezas públicas de Core (`resolve_ports`, `build_api_deps`, `RegistryService`, `registry_extension`, `create_app`) y monta `/internal/v1/*`. Rust es cliente HTTP de una sola URL.
- **B**: `agentcore serve` stock con nuestras siete fábricas más un `core-bridge` aparte con acceso a las mismas bases.
- **C**: Rust como cliente HTTP puro de `serve`, sin bridge.

**Recomendación: A.** Verificado en el código: (1) la CLI `serve` no acepta extensiones, `limits` ni sustituir el `RegistryPort` (`build_api_deps` no los recibe), así que B no puede fijar el pin por `release_id` ni `RateLimitConfig`/`Quotas`/sandbox; (2) `POST /v1/runs` es síncrono y entrega el `run_id` al terminar, la salida de un nodo `agent` no es recuperable por HTTP (G0-22) y no hay `GET /v1/runs`, lo que descarta C para tasks; (3) el pin debe cubrir `RunAuthorizer` y `TurnEngine`, que resuelven por separado, y ambos leen `ports.registry` (`dataclasses.replace` lo cubre en A); (4) `ApiDeps.extensions`, `limits` y `readiness` son el mecanismo previsto para que un paquete externo monte rutas (como hace `registry_extension`). Costo: acoplamiento a ~5 funciones de composición, mitigado con pin por SHA y un job de CI que arranca la app en cada bump (CAP-57, solicitud N-06). La primera rebanada (propuesta gobernada) sigue funcionando con B si se quiere empezar antes.

**Bloquea.** CAP-24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 40, 53; las variantes in-process de CAP-07, CAP-08 y CAP-16 (L2). **Ediciones pendientes:** C-01, C-02, C-03, C-05.

---

## D-2 — Quién escribe las siete fábricas y qué se declara real o doble

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: A) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** `serve` fuera de demo exige `tools`, `authz`, `transcript`, `calibration`, `classifier`, `field-classifier` y `grant-active` como código importable que no sea `testing.*`; ninguna existe hoy fuera de los dobles de demo, y el wheel no incluye `testing`. ¿Quién las escribe y qué se llama "real"?

**Opciones.**
- **A**: Pulso escribe las siete para `pulso-evolution` (reales: executors `pulso/*`, authz de builder, transcript nulo, calibración Pulso, `grant-active` falso) y usa sandbox sembrado y un authz sintético de evaluación, **etiquetados en `doubles[]`**, para el mundo de atención de prueba.
- **B**: esperar piezas de la plataforma de atención o de agent-core.
- **C**: `AGENTCORE_ALLOW_DEMO=1` con los dobles de Core.

**Recomendación: A.** Las piezas del constructor (identidad builder, grants, lab) son nuestras (§29.8); las de la atención bancaria real son de la plataforma y no se simulan como reales. B no tiene dueño ni fecha; C hace que "real local" sea un doble con otro nombre y contradice §27.6. La regla R1 (todo reporte lleva `doubles[]`) mantiene la honestidad del corte.

**Bloquea.** CAP-24, CAP-29, y las etiquetas "real" de CAP-49 y CAP-61. **Ediciones pendientes:** ninguna adicional (E-21/E-23 ya recogen el hecho).

---

## D-3 — Quién construye la imagen del runtime y qué se hace con el ADR 0003

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: A) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** Agent-core no trae Dockerfile ni imagen publicada, y el ADR 0003 de `infra` (Proposed) asigna "Dockerfile y image build" a agent-core. El runtime de Pulso contiene nuestras fábricas e identidad builder.

**Opciones.**
- **A**: imagen nuestra (`pulso-core-runtime`, `agent_core` por SHA + nuestro paquete), con ADR 0003 corregido en el mismo PR que el manifest.
- **B**: pedir a agent-core una imagen base por digest y construir encima la nuestra.
- **C**: sin imagen: checkout del SHA y `uv sync` en el host (sólo local/CI).

**Recomendación: A.** La imagen debe incluir código nuestro, así que una imagen upstream sola no sirve y B añade una dependencia sin fecha para obtener algo que podemos hacer con `uv sync --locked` (Python 3.12, `uv.lock` del SHA). C no es desplegable en AWS. ADR 0003 también está desactualizado (dice que `/healthz`, `/readyz` y `agentcore migrate` no existen; en el SHA existen).

**Bloquea.** CAP-60, CAP-58 (imagen), CAP-62. **Ediciones pendientes:** C-03, C-04; corrección del ADR 0003 en `infra`.

---

## D-4 — Cómo ingerir los eventos de Core

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: A) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** Agent-core no empuja eventos (sólo proyectores puros), no hay `GET /v1/runs` ni rutas de eventos, y `export_events` exige `run_ids`. ¿Pulso consume Postgres de Core?

**Opciones.**
- **A**: exporter Python propio (`pulso-core-exporter`, misma imagen) con rol Postgres **sólo lectura** sobre `audit_events`, `reg_events` y `outbox`; contract test de esquema; Rust no toca esa base.
- **B**: pedir a agent-core un relay/endpoint de eventos y esperar.
- **C**: detectar sólo con dataset/E0 y OTel muestreado.

**Recomendación: A.** Es la única vía que existe hoy y respeta la regla de §29.8 ("Rust no accede a PG Core"). Se mitiga el acoplamiento usando las clases de `agent_core` (`PostgresAuditSink.read`, `project_*`, `check_chain`) y fallando cerrado ante drift de esquema; no se usa `PostgresOutbox.pending/mark_delivered` (mutaría el despachador de handoffs de Core). Se solicita N-08 como mejora futura. B bloquea la detección sobre eventos de Core sin plazo; C es el workaround que ya existe y no sustituye a A porque OTel muestreado no es denominador.

**Bloquea.** CAP-34, CAP-35 (y U49/U50). **Ediciones pendientes:** C-07.

---

## D-5 — Emisor de la credencial humana step_up

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: A (reinicio planificado para rotar claves)) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** Core sólo verifica JWS; approve, publish y promote exigen un builder humano `aprobador` con `step_up`. ¿Quién la emite en local y en AWS? Además, la rotación de claves exige reiniciar el runtime (los archivos se leen al arrancar): ¿se acepta una ventana planificada?

**Opciones.**
- **A**: local con emisor de prueba nuestro (`auth.simulated=true`, `kid` humano distinto del bot); en AWS el proveedor de identidad de la organización; mientras no exista, paso humano fuera de banda con `agentcore registry approve/publish/promote --credential` registrado como `out_of_band`.
- **B**: Pulso firma también las credenciales humanas con una clave propia.
- **C**: pedir a agent-core un endpoint de login/step-up.

**Recomendación: A (con reinicio planificado para rotar claves; N-09 pide recarga).** B anula el control: el bot podría fabricar aprobaciones y V3 §27.5 prohíbe que la UI "firme como humano por recibir click". C no cambia que el emisor debe ser de la organización. El contract test exige que bot y humano usen claves distintas y que ninguna clave de prueba aparezca en configuración remota.

**Bloquea.** CAP-44 (queda `dependency_blocked`), la fuente de CAP-43 fuera de local y CAP-45 en AWS.

---

## D-6 — Topología local de contenedores

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: A con PG16 propio para Core) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** ¿Un solo proyecto Compose con Core dentro, o dos stacks (el de agent-core más el de Pulso), y qué runtime de contenedores?

**Opciones.**
- **A**: un compose (`improvement-engine/local`) con `postgres` (Pulso, 54329), `postgres-core` (PG16), `core-runtime`, `core-exporter`, redes `pulso-internal` (internal) y `core-egress`.
- **B**: dos proyectos unidos por una red externa; Core como proceso host con `uv run`.
- **C**: A pero con PG17 compartido.

**Recomendación: A con PG16 propio para Core.** El compose de agent-core sólo aporta Postgres 16 (bind `127.0.0.1:5432`) y, con imagen propia (D-3), un segundo stack sólo añade `host.docker.internal` y orden entre proyectos. PG16 es la versión que valida el CI de Core; compartir PG17 exige antes un contract test (sujeto a verificación). La red `pulso-internal` es `internal: true`, por lo que `core-runtime` necesita `core-egress` para LLM/Jev. Runtime: Docker o Podman, uno por máquina, registrado por `doctor`; si Podman rootless no delega `pids`, `doctor` lo reporta y la decisión de `--cgroups=disabled` sigue siendo humana. B queda como fallback de depuración rotulado `host_process`.

**Bloquea.** CAP-48, CAP-58, CAP-59 (checks de red). **Ediciones pendientes:** C-04, C-06.

---

## D-7 — Sandbox del gate nativo de evaluación

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: A ahora, revisar B tras el primer E2E real) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** `serve` cablea `LocalSandbox` (colas FIFO por tool, sin estado ni matching por argumentos) y `max_workers=1`. ¿El banco sandbox stateful (U26) entra al `evaluate` nativo?

**Opciones.**
- **A**: primer corte con colas FIFO precalculadas desde una traza de referencia del banco (CAP-22); el banco stateful sólo en `PulsoScenarioHarness` y la campaña complementaria, declarado complementario.
- **B**: inyectar el banco stateful en `ScenarioEvaluator` (posible sólo con D-1 = A).

**Recomendación: A ahora, revisar B tras el primer E2E real.** B cambia el significado de "pass nativo" (otro mundo de datos que el de la suite grabada) y exige paridad por test de contrato por SHA; A es compatible con `serve` stock y con V3 §29.8 ("no un SandboxPort genérico"). Los escenarios que dependan de estado o argumentos se marcan `not_evaluable_native`.

**Bloquea.** CAP-41 (`dependency_blocked`). **Ediciones pendientes:** ninguna.

---

## D-8 — Cómo leer la base y el alias vigente

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: A, con B como degradación) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** El registry HTTP no ofrece lectura de alias, versiones ni listado de propuestas; sólo se conoce `staging` creando una propuesta (consume cuota `auto_detect`).

**Opciones.**
- **A**: lectura de sólo lectura expuesta por el bridge (`GET /internal/v1/core-state/aliases/...`) sobre el store de Core, más receipts verificados.
- **B**: sondeo con `POST /proposals` y `lineage`/eventos como evidencia (`ObservedAlias`).
- **C**: esperar el endpoint upstream (N-02).

**Recomendación: A, con B como degradación.** Es construible por nosotros sin cambiar Core (el store lo expone en proceso) y evita gastar cuota; la interfaz exacta del store se cubre con el contract CI. Sin A, prod nunca se afirma activo (`alias_unknown`). Se pide N-02 igualmente.

**Bloquea.** CAP-07 y CAP-08 (variante autoritativa). **Ediciones pendientes:** C-08.

---

## D-9 — Dónde se valida antes de escribir el draft

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: A) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** La validación completa (`G0-*`, `AG-*`, `MT-*`, `REG-*`) vive en Python. ¿Se reimplementa en Rust, se delega siempre a `POST …/validate` o se corre en el bridge?

**Opciones.**
- **A**: prefiltro Rust (reglas independientes de la base) + **dry-run en el bridge** con `build_candidate`/`validate_candidate` del SHA, sin crear propuesta ni gastar cuota + `/validate` y `freeze` autoritativos.
- **B**: reimplementar ~25 reglas en Rust.
- **C**: sólo prefiltro + `/validate`.

**Recomendación: A.** B duplica la fuente de verdad y deriva con cada SHA; C obliga a un round-trip por iteración (aceptable, pero sin paridad de `candidate_hash` ni de cascada antes de congelar, porque `ReleaseDetail` no expone `interrupts`, idioma, ruleset ni `max_input_chars`). Observado: con el código del SHA en memoria, el caso `disputa-cargo@1.1.0` da `candidate_hash` `a6d50a8f…`, cascada `atencion@1.0.1` y los cuatro negativos esperados. Requiere D-1 = A para el bridge.

**Bloquea.** CAP-16 (capa L2) y CAP-17 (paridad). **Ediciones pendientes:** C-09.

---

## D-10 — Mundo mínimo y kinds del primer corte

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: mundo A ahora (C para demostrar efecto) + kinds K1) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** ¿Sobre qué mundo se hace el primer E2E real y qué entidades puede producir Pulso en el primer corte?

**Opciones de mundo.** **A**: `attention-demo` (copia pinneada de `registry-demo` más suite en YAML traducida de `demo_suite` y ampliada), declarado `contract_fixture`: prueba contrato, no mejora. **B**: `registry-realflow` (3 agentes, calibración JSON) desde el inicio. **C**: mundo propio con baseline realmente ejecutado.

**Opciones de kinds.** **K1**: `flow`, `template`, `policy`, `prompt`, `decision_model`, `eval_suite`, y `agent` sólo por cascada o campos autorizados; fuera `tool`, `model_profile`, `language_detection`, `injection_ruleset`, `knowledge_snapshot`, cambios a nivel release y agente nuevo. **K2**: K1 más agente nuevo.

**Recomendación: A ahora y C para demostrar efecto; K1.** `registry-demo` no trae `eval_suites/` y su suite vive en código; sin suite no hay vara anterior. El mundo demo permite cerrar el contrato wire con un caso dorado verificado; el efecto real exige un baseline y un candidato ejecutados en un simulador independiente (V3 §27.2 paso 6). K1 respeta lo que Core permite por la vía registry: `ReleaseDecl` se deriva de la base y una tool nueva sin executor es `dependency_blocked`.

**Bloquea.** CAP-14, CAP-46, CAP-49, CAP-61. **Ediciones pendientes:** ninguna.

---

## D-11 — Cadencia del CI real y gobierno del bump del pin

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: A) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** ¿Con qué frecuencia corre el corte (b) y quién aprueba un cambio de SHA?

**Opciones.** **A**: `real-wire` diario, manual y en cualquier PR que toque el adaptador, el mock, el manifest o el pin; bump en PR dedicado con ADR y revisor independiente (el integrador aprueba, no escribe). **B**: sólo manual. **C**: en cada commit.

**Recomendación: A.** §27.6 declara (b) como smoke/integración periódica y no en cada commit; B deja el drift sin detector entre bumps; C hace el CI ordinario frágil y lento. Los tiempos (`real-wire` ≤ 20 min, `contract-drift` ≤ 5 min) son iniciales y se miden. Quién es el revisor independiente es una asignación humana.

**Bloquea.** La cadencia de CAP-57 (no su contrato).

---

## D-12 — Identidad de ejecución del bridge y límites de tasa

**Estado: ADOPTADA PROVISIONALMENTE (opción recomendada: A) — pendiente de revisión con el equipo de agent-core.**

**Pregunta.** Core limita por principal (30 solicitudes por 60 s y 5 USD/día por defecto, contados en el runtime). Un solo principal builder del bridge compartiría contador entre tenants y jobs. ¿Cómo se identifica el bridge y qué límites se fijan?

**Opciones.** **A**: un principal por `(tenant, rol)` con `RateLimitConfig` explícita derivada del presupuesto sellado de Pulso (sólo posible con D-1 = A). **B**: principal único y tope muy alto. **C**: dejar los defaults.

**Recomendación: A.** La reserva USD de Pulso sigue siendo la autoridad de presupuesto (Core excluye costos desconocidos y no cancela runs); el límite de Core es una segunda barrera, no la primera. B mezcla tenants en un contador y debilita la atribución; C hace que la 31.ª invocación en un minuto reciba 429 sin que Pulso lo haya previsto. El `id` y los `attrs` del principal no llevan datos sensibles (se proyectan a eventos).

**Bloquea.** El principal de run de CAP-04 y CAP-31.
