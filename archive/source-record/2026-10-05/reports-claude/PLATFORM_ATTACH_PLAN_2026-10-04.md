# Attach plan: improvement engine proposals into support-platform + agent-core (2026-10-04)

Author: Claude (read-only reconnaissance). Evidence: shallow clones in the session scratchpad (support-platform `eeb73a8`, agent-core `547e608`, llm-gateway `63155b6`) and our worktree `improvement-engine-claude-w6-demo`. Nothing was run (no tests, builds, containers, model calls, AWS). Statements marked (inferred) are not read verbatim from code. Companion of `INTEGRATION_AND_DEMO_PLAN_2026-10-04.md` (same facts, different cut: this one is the attach recipe).

## 0. The 8 key facts

1. **The platform builder lists only its own index, not the registry.** `GET /api/v1/builder/proposals` reads table `builder_proposals`, filled by proposals created through the platform, found in the builder-chat answer, or tracked by id (`POST /builder/proposals/track`). Source enum is `platform | chat | tracked`. An engine-created proposal is invisible there until someone registers it. (`application/ai/builder.py` list/adopt/track; slice-16 doc §4, §8.)
2. **agent-core has no list-proposals route at main.** PR #24 (`GET /v1/registry/proposals?agent_id=&state=&created_by=`) and PR #23 (OpenAPI + `Idempotency-Key` on registry writes) were merged into stacked branches after their base (#21) had already merged: they are on `origin/ctr`, not on `main` (`git merge-base --is-ancestor` fails; `registry/http.py` has no list route and only `publish` reads the header). **PR #28 (JEV via gateway) is stranded the same way** (base `feat/http-llm-gateway`; main still has `jev_http.py` and `serve` demands `AGENTCORE_JEV_API_KEY`).
3. **The platform has no builder screens.** Backend only (S16, `/api/v1/builder/*`). `frontend/src/app/paths.ts` has no agents/proposals route; slice-16 doc says "screens are the frontend team's". The "Automatización" role and screens were removed (brief §1 out-of-scope; `/automatizacion` is a not-found). The natural home is "Supervisión · Agentes → Propuestas" with an `origin = auto_detect` filter, not a new role.
4. **Nothing can pass `candidate` today on real agents.** No `eval_suite` exists in `registry-e2e` or any seed; evaluate is `404 no existe la suite`; approve/publish need `evaluated`. Our engine already proposes `eval_suite` (op add) next to the change (BK0, real-core-live), so the pair "prompt replace + eval_suite add" is the only live path. Scenarios are hard-coded as principal type `customer` (`composition/evaluation.py:95`), so **customer-facing agents (disputas, recepcion, consultas) are evaluable; advisor-only `copiloto-asesor` very likely is not** (inferred; verify in step S0).
5. **Approval is the platform's, per call, by a human with TOTP.** `POST /builder/proposals/{id}/approve|reject|publish`, `POST /builder/aliases/{agent}/{alias}/promote` carry `stepUpCode`; the platform verifies the person's TOTP (seeded accounts: `CC_DEV_MFA_CODE=000000`), then signs a 2-minute `builder` principal at `step_up` with the **staff** key. The registry only accepts `human + step_up`; a service identity can never approve (agent-core ADR 0018 §6, `registry/roles.py`). Self-approval by the proposer is allowed (amendment 4).
6. **Our client talks to the wrong door.** `core-client` calls our `core-bridge` `/internal/v1` (JWT `aud=core-bridge`, `tenant_id`, per-route `purpose`, writer-stage commitments, `pulso-writer` Core agent from `agent-core-assets/worlds/pulso-evolution`). The team's agent-core exposes only `/v1/registry` (+ `/v1/runs`, `/v1/export`) with Ed25519 `principal+jws` credentials: no audience, no tenant, no `/internal/v1`. Our worlds (`atencion`, `atencion-tarea`) are not the real artifacts (`disputas`, `copiloto-asesor`...). We need a **direct registry writer** (core-client already has a read/approve/publish `/v1/registry` client in `registry.rs`; it lacks create/put_draft/validate/freeze) and a staff key for the engine.
7. **Proposals carry no metadata.** `Proposal` = `{proposal_id, agent_id, origin, state, base_release_id, title<=200, created_by, rev, candidate_hash, updated_at}`, `additionalProperties:false`. Origin enum already has `auto_detect` (quotas: 10 proposals/24 h, 20 evals/proposal). Provenance can only ride in `origin`, `created_by` (engine principal id), the title prefix, and per-change `docs.{description<=4000, rationale<=4000, changelog<=8000}`. Platform `ProposalDetail` returns `changes[].docs` and the registry's own `lastEval/review`, so engine evidence goes in `docs.rationale`; our structural-gate verdict (stand-in) cannot be shown natively.
8. **agent-core's e2e stack does not include the platform** (compose = Postgres only; llm-gateway as a `docker run`; `agentcore serve` runs on the host). Platform is its own `docker-compose.yml` (api 8000, web 5173) or `uv run cc-api` + `pnpm dev`. Gotchas: `scripts/e2e/serve.ps1` has no `--port` (defaults 8000, collides with the platform: run the same command with `--port 8001`); `setup.ps1` copies `scripts/e2e/.env.e2e.example`, which is **gitignored by `.env.*` and not in the repo**, so a fresh clone cannot run setup; the platform's `staff-keys.json`/`identity-keys.json` must replace the demo ones after setup's import.

## 1. support-platform (head `eeb73a8`)

### 1.1 Backend modules (all under `backend/src/cc_platform/`)
| Surface | Files |
|---|---|
| Ports / DTOs | `application/ai/registry.py` (AgentRegistryClient, typed DTOs mirroring `contracts/registry/*.json`), `runtime.py`, `credentials.py`, `ports.py`, `config.py` |
| Builder use cases | `application/ai/builder.py` (AgentBuilder: index, list, track, adopt, draft ops, decisions), `builder_chat.py` (chat with `constructor-chat`), `builder_step_up.py` (TOTP step-up) |
| Copilot / assistant | `application/ai/copilot.py` (S15), `customer.py`, `process.py` (AgentTurnProcess), `grants.py`, `sweep.py`, `staff.py`, `priority.py` |
| HTTP adapters | `infrastructure/ai/http_registry.py` (`/v1/registry`, httpx, 60 s), `http_runtime.py`, `ed25519_issuer.py`, `keys.py`, `memory_registry.py` (test double applying agent-core roles) |
| Routes | `api/routers/builder.py` (`/api/v1/builder/*`), `cases.py` (`GET /api/v1/cases/{id}/copilot`, `POST .../copilot/messages`), `supervision.py` (`/supervision/cases/{id}/assistant/release`), `internal.py` (`/api/v1/internal/grants/{ref}`, bearer `CC_INTERNAL_SERVICE_TOKEN`, hidden from OpenAPI) |
| Persistence | `builder_proposals`, `builder_threads` (`infrastructure/persistence/sqlalchemy/repositories/builder.py`; SQLite, no migrations) |
| Keys | `scripts/gen_agent_keys.py` -> `backend/.agent-keys/{private,identity-keys,staff-keys}.json` |
| Docs | `docs/platform/adr/0003-agent-core-integration.md`, `api/slice-14-assistant.md`, `slice-15-copilot.md`, `slice-16-agent-builder.md`, `RUNBOOK.md` §4.1, open PR #11 (ADR 0004 tool service) |

### 1.2 How the backend talks to agent-core
- Config: `CC_AGENT_CORE_URL` (runtime and registry share it: `/v1/runs`, `/v1/sessions`, `/v1/registry`), `CC_AGENT_KEYS_FILE` (private seeds; both together or the platform is people-only), `CC_AGENT_CORE_TIMEOUT_SECONDS=60`, agents: `CC_ASSISTANT_AGENT=recepcion@prod`, `CC_COPILOT_AGENT=copiloto-asesor@prod`, `CC_BUILDER_AGENT=constructor-chat@prod`, `CC_INTERNAL_SERVICE_TOKEN`.
- **Identities** (no `aud`, no tenant claim; credentials are `principal+jws` with `kid`, `exp` 10 min, 2 min at step_up): customer (`type customer`, id = dataset customer id), advisor (+ `delegation+jws` on_behalf_of the customer, signed on assignment), builder (`type builder`, roles `constructor`+`aprobador`, `+admin` for Administración, `attrs.actor=human`). **Two keys**: registry credential signed with the *staff* key (`--staff-keys`), runtime/chat credential with the *identity* key (`--identity-keys`).
- Registry client: `/v1/registry/{proposals, proposals/{id}/draft|validate|freeze|reopen|evaluate|approve|reject|publish, aliases/{agent}/{alias}, releases/{id}, releases/{a}/diff/{b}, versions/{kind}/{id}, entities/{kind}/{id}, releases/{id}/revoke}`. `publish` sends `Idempotency-Key`.

### 1.3 What the builder lists and approval flow
- List: platform **index** only (see fact 1); `refresh` re-reads each row from the registry (`live` flag). Filters: `agentId`, `state`, `limit<=50`. No author/service-identity filter. `createdBy` and `origin` are shown per row.
- Roles: Supervisión (constructor+aprobador) and Administración; others 403. Revoke is Administración only.
- States: `draft -> candidate (freeze) -> evaluated (evaluate pass) -> approved -> published`; failed gate returns to `draft`; publish after staging moved is `proposal_stale`.
- Who approves: the logged-in person, by herself; Core call: `POST /v1/registry/proposals/{id}/approve` with body `{candidate_hash, accept_yardstick_loosened}`; `publish` moves **only `staging`**; `POST /builder/aliases/{agent}/{alias}/promote` moves `prod` (step-up again).
- Audit: `builder.*` events family `agents`.

### 1.4 Frontend
Routes in `frontend/src/app/paths.ts`: supervision `queues|team|escalations|cases/:id|audit`; admin `users|teams|audit`; analyst workspace (copilot panel backend exists). **No agents/proposals/registry route, no builder feature folder, `schema.gen.ts` not regenerated for `/builder`.** The slice-16 doc §6 gives the suggested screens (Propuestas list, detail stepper with tabs Cambios/Validación/Evaluación/Decisión, draft editor, release/alias diff, Constructor chat). Design board mentioned in slice-4 doc: `warehouse/design/source/project/Admin.dc.html` (not in the repo; `D:\.codex\factored\design\Plataforma de Contact Center*.html` are bundled exports in which I found no readable "Automatización" text).

### 1.5 Seeds and fixtures (agent-core `tests/fixtures/registry-e2e`, imported by `agentcore registry import`)
- Agents `recepcion`, `disputas`, `consultas`, `copiloto-asesor`, `constructor-chat` (all `1.0.0`); one release per agent (`recepcion-demo`, `disputas-demo`, `consultas-demo`, `copiloto-demo`, `constructor-demo`), each lists `aliases: [prod]` but `import_seed` sets **both `staging` and `prod`** to the release (`registry/service.py` import_seed). Flows `recepcion`, `disputa-cargo`, `consulta-pqr`, `asistir`, `construir`; prompts `p/copiloto`, `p/respuesta_asesor`, `p/resumen_radicado`, `p/resumen_construccion`, `p/constructor`; 24 templates; tools `leer_productos`, `leer_movimientos`, `leer_pqr_cliente`, `obtener_handoff`, `leer_transcript`, `buscar_transacciones`, `convertir_moneda`, `radicar_pqr`, `obtener_pqr`, `seleccionar`, `registry/{create_proposal,put_draft,validate,freeze,evaluate,reopen,get_*,list_versions}`, `directory/list`. **No `eval_suite`. No `list_proposals` builder tool.**
- `copiloto-asesor`: `mode conversational`, `invocable_by [advisor]`, `entry_flow asistir@1`, `understand-copiloto@1`, tools `leer_movimientos, leer_productos, leer_pqr_cliente, obtener_handoff, leer_transcript` (read only), budgets (max cost per run 1.00), prompt `p/copiloto@1.0.0` (es/pt; head `547e608` rewrote this prompt, `asistir`, `respuesta_asesor` and two fallback templates relative to `c814c2b`: any base we hold from the pin is stale, always read the base from the live registry).

### 1.6 Where engine opportunities naturally appear, and what is missing
Natural: Supervisión · Agentes · Propuestas (origin chip "Detectada por el motor" = `origin=auto_detect`), detail tab "Evidencia" (rationale), then the existing decision tab. Missing: (a) a way into the index (fact 1), (b) the screens, (c) a provenance/evidence field, (d) a `eval_suite` for any target, (e) engine service identity in staff keys, (f) a platform notification (event "propuesta del motor") optional.

## 2. agent-core (head `547e608`; registry code identical to `c814c2b`)

- Registry API `/v1/registry` (installed with `serve --registry-api`): create (body `{agent_id, origin: manual|builder_chat|auto_detect|import, title}`), get, put draft (`{expected_rev, changes[{kind, content, docs}]}`, replaces whole draft; limits 50 changes, 256 KiB/entity, 200 flow nodes; platform guardrail policies cannot be edited, interrupts change needs admin), validate, freeze, reopen, evaluate (`{suite_id, suite_version?}`), approve, reject, publish (`Idempotency-Key` header mandatory), promote (`POST /aliases/{agent}/{alias}`), alias get, versions, entities, release get/diff/revoke, run lineage. Roles (`registry/roles.py`): any non-human `builder` with `constructor` may create/put/validate/freeze/reopen/evaluate; approve/reject/publish/promote need `aprobador`+human+step_up; revoke/import need `admin`+human+step_up; `exporter` reads `/v1/export/{runs, runs/{id}/events, registry-events}`.
- States: `draft, candidate, evaluated, approved, published`. Release ids are `release_id_for(candidate_hash)`.
- Principals: Ed25519 JWS, kid-keyed files `--identity-keys` (runs) and `--staff-keys` (registry), reloaded every ~5 s. Demo constructor identity: `constructor-bot`, role `constructor`, not human (`composition/serve.py:89`).
- Artifact kinds: 11 `EntityKind` (agent, flow, decision_model, policy, template, prompt, tool, language_detection, injection_ruleset, model_profile, knowledge_snapshot), draft-only `eval_suite`, `release_settings`. Eval suite scenarios: `scripted` (principal `{id, attrs}` run as `customer`, steps start/turn/confirm, seeded tool replies, `expect`, `assertions`); `dataset` scenarios disabled.
- Tools: `ToolDef` in the registry; ADR 0025 `HttpToolExecutor` (`agent_core/adapters/tools/http_executor.py`), enabled with `serve --tools agent_core.adapters.tools:http_tool_executor` + `AGENTCORE_TOOL_SERVICE_URL/TOKEN/TIMEOUT_S`; calls `POST {url}/v1/tools/{id}/execute` with verified claims; the service (repo `pulso-factored/tool-service`) implements tools by name. Publishing a release does not check that the service implements a tool (ADR 0025 "Abierto"). PR #34 (open) wires the service plus the field catalog into the e2e stack (`serve-tools.ps1`).
- Outbound: events `run.started|closed|transferred`, `handoff.created|resolved`, `release.published|promoted|revoked` (`contracts/events/catalog.json`), and `/v1/export/registry-events` for proposal lifecycle (role `exporter`).
- Local e2e stack (PR #32): `scripts/e2e/{setup,serve,chat,report,down}.ps1`, `compose.yml` (Postgres 16 on 127.0.0.1:55432, volume e2e-pgdata), DB `agentcore_eval` for evaluations, llm-gateway container `llm-gateway-e2e` on 8080 (needs `OPENROUTER_API_KEY`), `serve` on host at 8000 with `--registry-api`, agents `recepcion,disputas,consultas,copiloto-asesor,constructor-chat`, demo doubles for tools/authz/transcript/calibration (`AGENTCORE_ALLOW_DEMO=1`). **It does not include the platform.** `AGENTCORE_JEV_API_KEY` is required by `serve` at main (fact 2). Runbook: `docs/runbook-e2e.md`.

## 3. Our side: calls vs what the platform expects

Calls our engine would make today to create a draft against a real artifact (`seams/crates/core-client/src/writer.rs`): `authoring_dry_run` (`POST /internal/v1/core-authoring/dry-run`), seal draft plan, `core-tasks/invoke` stage `writer` with `RegistryMutationCommitment` (`create_proposal`, `put_draft`, `freeze`), `read_alias` (`GET /internal/v1/core-state/aliases/{agent}/{alias}`), arms via `/evaluation/*`; approve/publish via `/v1/registry` with a human-issuer command JWS (`registry.rs`, `e2e-core/.../core_hooks.py`). BK0 `contracts/artifact-kinds/matrix.json` (pin `c814c2b`, digest `sha256:ae0ffc15...`): propose supported only for `prompt` (replace) and `eval_suite` (add), real-core-live; every other kind `denied(kind_not_supported)` by our compile step; `tool` validate/evaluate/publish `blocked(executor-registration)`; `decision_model` with provider jev `blocked(jev)`; `release_settings` `denied` by the bridge. Head `547e608` changes for BK0: **registry unchanged**; new `HttpToolExecutor` (tool blocker softens only if tool-service implements the tool) and e2e fixtures (new real prompt texts). BK0 digest stays valid; the `tool` row note needs a `[CONTRACT-CHANGE]` only when we exercise it.

### Mismatch table
| # | Topic | Ours | Theirs | Fix |
|---|---|---|---|---|
| M1 | Transport | `/internal/v1` on core-bridge, JWT `iss=control-api aud=core-bridge sub=worker:* purpose jti` | `/v1/registry`, `principal+jws` | direct `RegistryHttpWriter` (our code) |
| M2 | Identity | bridge bot `pulso-constructor:<tenant>`; human authorization JWS from local issuer | engine needs its own kid in `staff-keys.json`; `type builder`, roles `[constructor]`, no `actor=human`; humans are the platform's | their config + our signer (principal payload as `ed25519_issuer.py` `_principal`) |
| M3 | Tenant | `tenant_id` mandatory on routes | none in Core or platform | drop on this path; keep a constant in our run record |
| M4 | Target artifacts | `atencion`, `atencion-tarea`, `pulso-*` assets, releases `demo`/`demo-task` | `disputas` etc., release ids `rel-<hash>` assigned at import | read base from live registry; map via new SMAP entries |
| M5 | Alias | staging read-back | builder bases on `staging`; platform agents default `@prod` | demo: set `CC_COPILOT_AGENT=...@staging` or promote prod after publish |
| M6 | Origin | `CREATE_ORIGIN=builder_chat` (default of `DraftPlan`) | `auto_detect` is the engine's origin (quotas, ADR 0018) | `DraftPlan::with_origin("auto_detect")` exists: make it the default for this path |
| M7 | Provenance | engine-run record, console | `Proposal` has no metadata | title prefix `[motor:<opp-id>]`, `docs.rationale` summary + evidence ids + gate verdicts + console URL; ASK a metadata object |
| M8 | Idempotency | bridge derives `pulso-w:` keys, commitment match | HTTP create/put_draft/freeze take no `Idempotency-Key` at main (#23 stranded); no list (#24 stranded) | local ledger `opp-id -> proposal_id` written before any retry; deterministic title marker; ASK the two merges |
| M9 | Gates | structural gate GSIpy (stand-in) + Core native evaluation via admissions/arms | registry `evaluate` with an `eval_suite`; gate failure returns proposal to draft | engine ships suite with the change; our gate verdict is rationale text only |
| M10 | Approval | local human-issuer JWS (`authorize(op,target)`), single-use binding checks | platform TOTP step-up, person's principal | drop our authorizer on this path; approval is entirely the platform's |
| M11 | Naming/versions | engine picks versions | semver must be higher than base; `agent_id` `^[a-z0-9][a-z0-9_/-]*$`; entity content carries `id`+`version`; prompt ids like `p/resumen_radicado` | compile reads base `GET /v1/registry/entities/prompt/p/resumen_radicado` |
| M12 | Numbers | integers/strings only (good) | decimals as numeric strings | keep |
| M13 | Registration in platform | none | index source enum `platform|chat|tracked` | see S4 options |

## 4. The ATTACH PLAN (smallest end-to-end slice)

**Slice "S-ATTACH-1"**: the engine detects an opportunity in the platform's data (our existing sources), creates a `disputas` proposal in agent-core registry (`origin=auto_detect`, **replace `p/resumen_radicado` 1.0.0 -> 1.0.1** plus **add `eval_suite` for `disputas`**), freezes it, the proposal appears in the platform builder list with the engine's evidence, a supervisor evaluates, approves with TOTP via the platform, publishes (`staging` moves to the new release), and our run closes by reading the alias/registry-event.

Why `disputas` + `p/resumen_radicado`: customer-facing, evaluable with customer-principal scripted scenarios, one prompt used by one node (`disputa-cargo` `responder_ok`), matches the runbook's own example ("shorter summary on filing"), prompt replace is the only change kind real-core-live in BK0. `copiloto-asesor` `p/copiloto` is a valid propose/validate/freeze target but evaluation is unverified (fact 4).

### Steps (type: our code | their code | config)
| Step | Type | What | Hours |
|---|---|---|---|
| S0 | our | Run offline gates vs head: BK0 drift test (`python -m pytest contracts/artifact-kinds/tests` with `AGENT_CORE_REF` pointing at a `547e608` checkout), core-client golden/pin tests; confirm registry diff empty; read-only probe of copilot evaluability (unit-level, no model) | 2 |
| S1 | config | agent-core operator adds our engine public key (kid `pulso-engine-<yy-mm>`) to the `staff-keys.json` that `serve --staff-keys` loads (principal id `pulso-improvement-engine`); we keep the seed in a git-ignored file | 0.5 (+ask) |
| S2 | our | `RegistryHttpWriter` in `seams/crates/core-client` (new `principal.rs` signer + create/put_draft/validate/freeze/get/entity-read methods in `registry.rs`), `origin=auto_detect`, local ledger, no `Idempotency-Key` assumption, error mapping of `registry_*` problems (quota 429 terminal, 409 stale terminal, 5xx unknown-outcome like `Transport{sent:true}`) | 8 |
| S3 | our | Compile for real targets: SMAP entry for `disputas`/`p/resumen_radicado`, read base version, semver bump, `docs` with provenance (<=4000/8000 chars), draft = `[prompt replace, eval_suite add]` (integers/strings only) | 8 |
| S3b | our | Author the `disputas` eval suite (scripted, customer principal, 3-4 scenarios from `tests/composition/test_e2e_agents.py` flows: resolved dispute, escalate by amount, injection, not found; seeded tool replies; metrics must exist on the agent or use agent-core default yardstick, to confirm against `registry/evaluation/yardstick.py`) | 6 |
| S4 | their (one of three, ask) | How the proposal enters the platform list. **A (recommended)**: `POST /api/v1/internal/builder/proposals` (bearer `CC_INTERNAL_SERVICE_TOKEN`, body `{proposalId}`) calling the existing `adopt` with a new source `engine` (enum + column; SQLite no migrations: recreate). **B**: agent-core lands #24, platform lists registry proposals with `origin=auto_detect` merged into its index. **C (no change, demo-grade)**: supervisor uses "Seguir una propuesta por id" (`POST /builder/proposals/track`), id displayed by our console | A: 4 platform; B: 2 agent-core + 4 platform; C: 0 |
| S5 | their | Frontend screens Supervisión · Agentes · Propuestas (list with origin chip, detail with Evidencia tab, decision dialog with TOTP). If late: Swagger `http://127.0.0.1:8000/api/v1/docs` / Bruno collection (`pulso-factored/bruno`) against the real `/builder/*` backend | frontend team (not our hours) |
| S6 | their/our | Evaluate: `POST /api/v1/builder/proposals/{id}/evaluate {suiteId}` by the supervisor (blocks seconds-minutes, needs gateway+JEV keys); or our engine calls registry `evaluate` itself (constructor role suffices; 20 evals per auto_detect proposal) | 1 |
| S7 | their | Human: approve (`candidate_hash`, `stepUpCode`), publish (`Idempotency-Key` + `stepUpCode`) -> `GET /builder/aliases/disputas/staging` shows new release; optional promote to prod | 0.5 manual |
| S8 | our | Close the loop: poll `GET /v1/registry/aliases/disputas/staging` and `/v1/registry/proposals/{id}` (and `/v1/export/registry-events` if we get `exporter`); write run record `approved_by_human`, `published_release`, `staging_moved`; no claim of improvement beyond the registry's own eval | 6 |
| S9 | our | Doubles labelling: `doubles[]` for the structural gate (stand-in), our sources; real: registry, platform approval | 2 |
| S10 | our | One live test gated by env (`PULSO_REAL_PLATFORM=1`) running S2-S3 against the local stack; documentation | 4 |

Total our side about 36-40 agent-hours (S0 2, S2 8, S3 8, S3b 6, S8 6, S9 2, S10 4, buffer); their side: 0.5 agent-core config, 4 platform (S4A), frontend screens unestimated.

### Local run recipe (Windows, Docker Desktop for agent-core Postgres+gateway; nothing below was executed)
1. agent-core, once: obtain the missing env template (ASK); otherwise create `scripts\e2e\.env.e2e` by hand with `AGENTCORE_KEYS_FINGERPRINT`, `AGENTCORE_KEYS_TOKEN_MAP`, `GATEWAY_TOKEN_AGENT_CORE`, `OPENROUTER_API_KEY`, `AGENTCORE_JEV_API_KEY`, and (inferred) `AGENTCORE_REGISTRY_DSN=postgresql://agentcore:agentcore-dev-only@127.0.0.1:55432/agentcore`, `AGENTCORE_EVAL_DSN=...:55432/agentcore_eval`, `AGENTCORE_LLM_GATEWAY_URL=http://127.0.0.1:8080`, `AGENTCORE_LLM_GATEWAY_TOKEN=<GATEWAY_TOKEN_AGENT_CORE>`, `AGENTCORE_ALLOW_DEMO=1`. Then `cd agent-core; .\scripts\e2e\setup.ps1` (Postgres 55432, migrate, creates demo keys in `.e2e/`, imports `registry-e2e`, builds gateway container).
2. Platform keys: `cd support-platform\backend; uv sync; uv run python -m cc_platform.scripts.gen_agent_keys --suffix 2026-10` -> `.agent-keys/`. Copy `identity-keys.json` and `staff-keys.json` over `agent-core\.e2e\` and add the engine's kid/public key under `principal_keys` of `staff-keys.json` (format `{"principal_keys": {"<kid>": "<b64url pubkey>"}}`).
3. agent-core serve on 8001 (the e2e script cannot change the port): in the agent-core dir, `. .\scripts\e2e\_env.ps1; Import-E2EEnv; uv run agentcore serve --port 8001 --identity-keys .e2e\identity-keys.json --staff-keys .e2e\staff-keys.json --registry-api --lang-thresholds scripts\e2e\lang-thresholds.json --agents "recepcion,disputas,consultas,copiloto-asesor,constructor-chat" --tools testing.e2e_demo:tools --classifier testing.e2e_demo:classifier_provider --field-classifier testing.e2e_demo:field_classifier --calibration testing.e2e_demo:calibration`.
4. Platform API: `cd support-platform\backend; $env:CC_AGENT_CORE_URL="http://127.0.0.1:8001"; $env:CC_AGENT_KEYS_FILE=".agent-keys/private.json"; $env:CC_INTERNAL_SERVICE_TOKEN="<random>"; uv run cc-api` (8000). Web: `cd ..\frontend; pnpm install; pnpm dev` (5173). Sign in with a seeded Supervisión account, password `demo1234`, code `000000` (see RUNBOOK §5).
5. Engine side (S2+): point `core-client` at `http://127.0.0.1:8001/v1/registry` with the engine seed. No Podman core stack is needed for this slice.
6. Check: `curl http://127.0.0.1:8001/v1/...` needs a staff JWS; use the platform's `GET /api/v1/builder/status`, `.../builder/aliases/disputas/staging`.
Expected RAM (estimates, not measured): Docker Desktop VM 1.5-2 GB with Postgres 16 (about 150 MB) and llm-gateway (about 30 MB); `agentcore serve` 350-450 MB; platform API 250 MB; Vite 250 MB (or nginx container 20 MB); browser 500 MB; total about 3-3.5 GB. Our Podman `real_local` stack would add 1536 MiB steady (`local/core/lib/memory.ps1`), not needed here.
Hard dependency for evaluate and chat: real LLM keys (OpenRouter via gateway and JEV key). Without them everything up to `candidate` works; evaluation does not.

## 5. ASKs (one sentence each, forwardable via the user)

agent-core team:
1. Please merge PR #23 and #24 into `main` (they were merged into stacked branches and are not on `main`), so the registry has `GET /v1/registry/proposals?created_by=&origin=&state=` and `Idempotency-Key` on create/put_draft/freeze.
2. Please do the same for PR #28 (JEV via gateway, also stranded) and tell us whether `AGENTCORE_JEV_API_KEY` is still required at main.
3. Please add a `metadata`/`provenance` object (or `source_ref`) to `Proposal` and `EntityDraft docs` for engine-originated proposals, bounded and non-secret, returned by `GET /proposals/{id}`.
4. Please add our engine's public key to the staff-keys of the shared environment under a non-human `builder` principal `pulso-improvement-engine` with role `constructor` only, and confirm the `auto_detect` quotas (10/24 h, 20 evals) are intended for us.
5. Please commit `scripts/e2e/.env.e2e.example` (it is ignored by `.env.*`) and let `serve.ps1` take a `-Port` so it can run beside the platform.
6. Please ship an `eval_suite` for `disputas` (or tell us to author it) and tell us whether scenarios can run as `advisor` with a delegation, which decides if `copiloto-asesor` can ever be evaluated.
7. Please confirm that a published release moves only `staging`, how running sessions see an alias move, and whether publishing checks that the tool service implements every `ToolDef` of the release.

support-platform team:
8. Please add a service-authenticated way to put an engine proposal in the builder list (internal `POST` with `CC_INTERNAL_SERVICE_TOKEN` and source `engine`), or switch the list to the registry listing once #24 lands.
9. Please build Supervisión · Agentes · Propuestas with an origin filter and an "Evidencia" tab showing `changes[].docs.rationale`, and regenerate `schema.gen.ts` for `/builder`.
10. Please tell us which seeded Supervisión account and TOTP method to use in the shared demo, and whether staging or prod is what the copilot/assistant should read in the demo (`CC_COPILOT_AGENT`, `CC_ASSISTANT_AGENT` default to `@prod`).
11. Please confirm that the engine may read `GET /builder/*` only as a human session (we will not), so the engine reads the registry directly with its own key.

## 6. What to mock if their side is late
- Screens late: drive the real `/api/v1/builder/*` backend from Swagger/Bruno; the platform step-up and the registry are real, only the UI is missing.
- Index registration late: option C (track by id); script it as a curl in the demo.
- Engine key not yet in staff-keys: run against a local agent-core where we own `--staff-keys` (step 2 above); label `real-narrow` not `real`.
- No LLM keys: stop at `candidate` live; for the verdict use Core native evaluation from our Podman stack (`local/core`, real_local) on our `atencion` world and label the platform half `stand-in`.
- Idempotency/list missing: keep the ledger; cap at one proposal per opportunity per day.
- Metadata field missing: title prefix plus `docs.rationale` block `engine-evidence:` (ids, hashes, gate verdicts, console URL), no personal data, 4000 char cap.

## 7. Feasibility by improvement kind at head Core `547e608` (BK0 = pinned `c814c2b`; registry code identical)

| Kind of improvement | Registry/Core | Our engine (BK0) | Verdict |
|---|---|---|---|
| Prompt change (replace) e.g. `p/resumen_radicado`, `p/copiloto` | supported | `supported`, real-core-live | **Feasible now**; evaluable on customer-facing agents; copilot evaluation unverified |
| Add `eval_suite` | supported (draft-only kind) | `supported`, real-core-live | **Feasible now**; precondition for any gate |
| Template (`t/*`, messages/fallbacks) / prompt-variant | supported by Core | `denied(kind_not_supported)` until BKT | Feasible after BKT (offline goldens, stand-in) |
| Policy (non-protected thresholds) | supported; protected policies refused `registry_forbidden` (ADR 0009) | denied until BKT | Feasible after BKT; protected ones never |
| Flow / decision tree (compiled `flow`) | supported; validation G0 rules, 200-node cap; needs agent bump | denied until BKF; only a flow dry-run violation case has evidence | Feasible after BKF; most work |
| Decision model (`decision_model`) | `jev` provider: Core at main still calls JEV directly (key); gateway path (#28) stranded | `blocked(jev)` | **Blocked** for `jev` models until #28 reaches main; `rule`/`classifier` providers feasible after BKD |
| New tool (`tool` + `tools_allowed` of the agent) | ToolDef is data; real execution needs `HttpToolExecutor` (merged, ADR 0025) and the tool implemented in `tool-service` by name (code in another repo); `risk_class read` only for us | denied; `blocked(executor-registration)` | **Blocked** on tool-service; a ToolDef-only proposal can be validated/frozen but would publish a tool nobody serves |
| New agent | entity `agent` + flows + prompts + templates + decision model + release | denied (BKA, plus BKF/BKT/BKD prerequisites) | Blocked until the other kinds exist; first publish of a new agent also has no `staging` base |
| Release settings / interrupts | admin human only | denied by bridge | Never by the engine |

Jev status (PR #28): merged, but into `feat/http-llm-gateway`, not `main`; llm-gateway main already serves `POST /v1/jev` (`internal/httpapi/jev.go`). Until the merge or until we have a JEV key, anything touching `understand`/`decide` with JEV stays `blocked(jev)` in BK0, and customer-facing agent evaluation also needs the key at main.

## 8. Risks
1. Stranded PRs (#23, #24, #28): our design may assume features that are not on `main` of the repo the platform runs; mitigated by S2 not depending on them.
2. Duplicate proposals on retry (no HTTP idempotency) and quota burn (10/24 h) if the engine loops.
3. Evaluation cost and keys: evaluate runs the real agent with real LLM calls (20 evals/proposal cap, per-run budget 1.00 USD in agent budgets; per-proposal cost cap deferred in agent-core).
4. Evidence mismatch: platform gate shows Core's yardstick, our structural gate is a stand-in; do not present it as the platform's verdict.
5. Whole-draft replace plus `expected_rev`: a human editing the draft in the platform invalidates our later write (`proposal_stale`); the engine must write once and stop.
6. Staging moves under us (another publish): `proposal_stale` on publish; the human must refreeze; engine should observe and mark the run `superseded`.
7. Platform is SQLite/single-process, `CC_ENV=prod` refuses to start, simulated channels: demo-only.
8. Self-approval is allowed by design: do not claim four-eyes governance.
9. Our worlds and assets (`atencion`, `pulso-*`) are not the real artifacts: SMAP catalogue and goldens need real-artifact entries; copilot prompt changed between pin and head.
10. Contract drift: platform pins agent-core contract `1.3.0`; head still `1.3.0`, but the unpublished response schemas (`ProposalDetail`, `ValidationReport`, `CandidateView`) mean our client types are hand-written.

## 9. Evidence index
- Platform: `docs/platform/api/slice-16-agent-builder.md`, `adr/0003-agent-core-integration.md`, `RUNBOOK.md` §4.1, `backend/src/cc_platform/{application/ai,infrastructure/ai,api/routers}/*`, `frontend/src/app/paths.ts`, `docs/platform/ENGINEERING_BRIEF.md` (amendment 2026-10-04).
- agent-core: `agent_core/registry/{http,service,roles,quotas,suite}.py`, `agent_core/composition/{evaluation,serve,serve_ports}.py`, `contracts/registry/*`, `contracts/events/catalog.json`, `docs/adr/0018,0019,0025`, `docs/runbook-e2e.md`, `scripts/e2e/*`, `tests/fixtures/registry-e2e/*`; PR states via `gh pr view` (#23 base `ccr-a4781bdb-dnrn7q`, #24 base `feat/registry-contratos`, #28 base `feat/http-llm-gateway`); `git diff c814c2b 547e608 -- agent_core/registry` is empty.
- Ours: `seams/crates/core-client/src/{routes,client,jwt,writer,registry,authoring,pins}.rs`, `contracts/artifact-kinds/{README.md,matrix.json,DIGEST.json}`, `core-bridge/README.md` and `docs/adr/0003`, `agent-core-assets/README.md`, `local/core/README.md`, `e2e-core/THREAD01.md`, `e2e-core/src/claude_standin/core_hooks.py`.
