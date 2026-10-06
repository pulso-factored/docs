# AI capability repos of pulso-factored: state on 2026-10-05

Method: fresh clones (depth 50) of origin/main under `D:\.codex\factored\tmp\survey\<repo>`; read-only; no builds, no tests run, no services started. Everything below was read in code/docs unless marked **(unverified)**. `gh` hit its rate limit midway: open PRs for agent-core are verified; for the other repos "no open PRs" comes from the check made just before the limit.

Repos in the org (pushedAt): improvement-engine (10-05), agent-core (10-05), support-platform (10-05), llm-gateway (10-05), infra (10-05), data-pipeline (10-04), tool-service (10-04), data-lab (10-04), bruno (09-30). All six asked-for repos exist. `improvement-engine`, `support-platform` and `infra` are outside the ask and were not surveyed.

## 1. What exists

### 1.1 Summary table

| Repo | Stack | Purpose | HEAD (origin/main) | Open PRs | Tests / maturity |
|---|---|---|---|---|---|
| agent-core | Python 3.12, uv, FastAPI, Postgres, pydantic | Decision engine running agents-as-versioned-data (Understand, Decide, Act, Verify, Escalate) plus the registry (proposals, eval, approval, release) | 2ad5d08 (PR #55 policy-locked) | #57 calibration run_id hash, #58 M7 normalize before PII detect | about 3,235 `def test_` across tests/; mypy strict, import-linter, ruff. GitHub CI not running since 10-03 (billing); local gate documented. Most mature |
| llm-gateway | Go 1.27, stdlib plus OTel | Stateless HTTP gateway to OpenAI-compatible endpoints; also JEV pass-through | 03d1a31 (PR #4 Langfuse/OTel content) | none | go test with conformance vectors vs the Python reference. Never run against a real provider by its author (docs/decisions-for-review.md); release.yml never run |
| tool-service | Python, uv, FastAPI, DuckDB read-only, SQLite | Tool provider over data-pipeline `gold_restricted`, for agent-core | 64c36bc | none | 7 test files on a synthetic dataset; contract tests vs shared OpenAPI 1.0.0; README claims 0-30 ms/call on 4.4M tx |
| data-pipeline | dbt plus DuckDB, medallion | bronze/silver/gold from the 13 challenge tables plus E0 sample | faed150 | none | 232 dbt checks plus about 24 pytest; full build about 6 min |
| data-lab | Python, uv | Dataset ingestion/quality, demand and learnability analyses, contracts, synthetic platform-history generator | 0e666a6 (assistant serves Portuguese, policy H1) | none | scripts and reports; no test suite seen (unverified) |
| bruno | Bruno collection | HTTP examples for agent-core `/v1` (6 requests) | e3d493c (09-29) | none | stale: README still says agent-core has no `serve` |

### 1.2 agent-core

Purpose: engine that interprets agents, flows, policies, templates, prompts, tools, decision models, language detection, injection rulesets, model profiles and knowledge snapshots as versioned entities (`agent_core/domain/entities.py`), plus an `eval_suite` entity. Business-agnostic.

Architecture (`agent_core/`): domain, interpreter, decision (Understand/Decide with JEV and calibrated thresholds), flows (graph, jsonlogic, agent nodes), guards (injection, language, PII), response (generation plus validation M8: numbers, citations, PII, language), actions (confirm, act, verify, idempotent outbox), handoff, outbound (escalation events), audit (hash-chained events, replay), registry (service, candidate, validation, evaluation, postgres, S3 blobs), api (FastAPI), adapters (llm http gateway, http tools, PolicyAuthz, grants, postgres audit/transcript, SNS), relay, composition (`serve`). 25 ADRs in `docs/adr`; ADR 0024/0025 make llm-gateway and the tool executor external services.

Public API:
- Runs (`contracts/openapi.json`): `/v1/runs`, `/v1/runs/{id}`, `/v1/runs/{id}/transcript`, `/v1/sessions/{id}/turns`, `/v1/sessions/{id}/lineage`, `/v1/handoffs/{ref}` and `/resolution`. Probes `/healthz`, `/readyz`, `/version`.
- Registry (`contracts/registry-openapi.json`): `/v1/registry/proposals` (+ `{pid}`, `/draft`, `/validate`, `/freeze`, `/evaluate`, `/approve`, `/reject`, `/reopen`, `/publish`), `/entities/{kind}/{id}`, `/versions/{kind}/{id}`, `/releases/{id}` (+ `/diff/{a}/{b}`, `/revoke`), `/aliases/{agent}/{alias}`, `/runs/{run_id}/lineage`.
- Export for ingestion (role `exporter`): `/v1/export/runs`, `/runs/{id}/events`, `/registry-events` (paginated).
- CLI `agentcore`: serve, validate, replay (fixture/audit), record, contracts, sweep, relay, blobs-backfill, migrate, registry (import/show/freeze/evaluate/approve/publish/promote).

Agents that exist (fixtures in `tests/fixtures/registry-e2e/agents`): `recepcion` (routes via directory `atencion-cliente` and transfers), `disputas` (flow `disputa-cargo`; tools buscar_transacciones, radicar_pqr, obtener_pqr, convertir_moneda; interrupt `fraude`; escalation policy by amount; es/pt), `consultas` (flow `consulta-pqr`; barely tested per runbook), `copiloto-asesor` (flow `asistir`; advisor acting with signed delegation; tools leer_productos/movimientos/pqr, obtener_handoff, leer_transcript), `constructor-chat` (flow `construir`; creates proposal, writes draft, validates; never approves or publishes). Also fixtures `registry-demo` (agent `atencion`), `registry-transfer-demo`, `registry-realflow`. These are test fixtures, not a production registry.

Registry / release / approval lifecycle (read in `registry/models.py`, `service.py`, `candidate.py`, `suite.py`, `roles.py`, ADR 0018/0020):
- States: draft, candidate (freeze, content hash), evaluated, approved, published (plus rejected/abandoned/stale). Origins: manual, builder_chat, auto_detect, import.
- Draft kinds: any entity kind, `eval_suite`, and reserved `release_settings` (interrupts, language_detection, injection_ruleset, max_input_chars, and `inherit_from` = id of a published release from which a new agent copies those settings server-side, so no admin is needed for inherited values; PR #51).
- Evaluate: harness runs the eval_suite scenarios; PR #50 binds the evaluation gateway to each target's registry so candidate prompts are really exercised. Per-agent metrics (DSL) with roles guardrail (zero tolerance), gate (not worse than base within noise, above floor) and monitor. Double yardstick (base suite plus candidate suite); loosening is flagged `yardstick_loosened` and needs a separate human approval.
- Locked: interrupts and policies can be `locked` (REG-LOCKED violation if a candidate removes, weakens or unlocks a platform guardrail); setting a policy `locked` needs `admin` (PR #55); eval report carries `guardrail_changes`.
- Roles: constructor, aprobador, admin, exporter. Approve/publish/promote/revoke/import need a human principal with `step_up`. The builder bot (`constructor-bot`) cannot be `actor=human`.
- Reject: optional closed-vocabulary `reason_code` (insufficient_evidence, wrong_target, risk, duplicate, policy_conflict, ...); `last_decision` shown in proposal detail (PR #53). Approval review shows resolved `inherit_from` settings (PR #52). `release.*` events carry agent_id, alias, before (PR #49).
- Scenario principals: `ScenarioPrincipal{id, attrs, type: customer|advisor, subject}`; an advisor needs a subject and gets a synthetic delegation (PR #54).

Runs / lineage / telemetry: hash-chained audit events; `replay` in fixture and audit modes (audit mode on real runs diverges for 3 known design reasons per plan doc). Lineage per session and per run. OTLP http/protobuf traces: spans `agentcore.api.request`, `invoke_agent`, `agentcore.decide`, `agentcore.rule`, `execute_tool`, `chat {model}`, `agentcore.transfer`; inbound `traceparent` joined and propagated to tool-service/platform; Langfuse-compatible span attributes (PR #48, merged 10-05). No content in agent-core spans (closed attribute list). `tool_source` added to `tool_called` events (PR #56).

Model routing: agent-core does not route. A `model_profile` entity holds `endpoint_alias`, `model`, temperature, max_tokens, timeout, `structured`, price. The e2e `perfil-generacion` uses alias `openrouter`, model `google/gemini-3.1-flash-lite`. The mimo/glm model policy from the user's memory is not visible in these fixtures; mapping is unverified.

Gaps stated by the repo itself (README, runbook-e2e, plan-e2e):
- In `serve` demo mode (`AGENTCORE_ALLOW_DEMO=1`) tools, authz, transcript (in memory), calibration, classifier and field catalog are doubles, unless real adapters are wired.
- Transfer by `serve` does not transfer yet (real "choose specialist" provider open); specialist flows re-ask slot `problema`.
- No demo agent has an `eval_suite`; the constructor-to-publish loop has not been exercised live.
- `invocable_by` is not enforced with the demo authz; the real `PolicyAuthz` exists.
- Postgres path of one-open-run-per-session not verified; GitHub CI down since 10-03.
- Copiloto "listen to live conversation" mode not implemented; `constructor-task` autonomous unsafe (no signal detector or cost cap).
- No SQL metrics views (TEMAS #11).

Recent merges (7 days): about 70 commits. Highlights: HttpToolExecutor and tool-service wiring, PolicyAuthz, HttpGrantActive, local e2e stack and `check`, Postgres transcript, engine tools, understand-turno calibration on synthetic data, constructor in Portuguese, OTel/Langfuse, inherit_from, evaluate with candidate prompts, reject reason, scenario principal, policy locked.

### 1.3 llm-gateway

`POST /v1/generate` (prompt, inputs as RFC 8785 canonical JSON, optional closed-subset JSON schema, `profile`, labels), exact decimal cost, typed errors (timeout, unavailable, rate_limited, invalid_output, refused), one provider call, no retries, one total deadline. `POST /v1/jev` pass-through (holds the JEV key; retries only 429/529). `/healthz`, `/v1/openapi.yaml`.

Model routing/aliases: the gateway has no model catalog or routing policy. Aliases are endpoints declared in `LLM_ENDPOINTS` (`{alias: {base_url, api_key_env}}`); the caller owns the `profile` (model, price, temperature). Consumers are Bearer tokens in `GATEWAY_CONSUMERS`. No per-consumer model policy or rate limits found (unverified beyond README/decisions).

Telemetry: OTel GenAI spans plus `langfuse.*` attributes (observation type generation, usage_details, exact cost_details, session id, release). Opt-in `LLM_GATEWAY_TRACE_CONTENT=1` puts messages/output on spans (cap 32768 bytes) so Langfuse shows them (PR #4). Default: no content.

Run: `go run ./cmd/llm-gateway` or Docker; image published to GHCR only on tag `vX.Y.Z`.

### 1.4 tool-service

Tools: `leer_productos`, `leer_perfil`, `leer_movimientos`, `buscar_transacciones`, `leer_pqr_cliente` (merges dataset cases and PQRs filed here), `radicar_pqr` (write_reversible, step_up, idempotent by engine action id, SQLite `filed_pqrs`), `obtener_pqr` (read-back). Contract `POST /v1/tools/{id}/execute`, `GET /v1/tools`, `/healthz`, `/readyz`; shared provider OpenAPI 1.0.0 in `contracts/`. Subject rules: customer reads self, advisor reads the delegated customer, any mismatch is `denied`. Returns curated columns (fraud score, email, document number excluded); classification is applied by agent-core `FieldClassifier` using the data-pipeline catalog. `registry/tools/*.yaml` are generated ToolDefs. Not here (engine tools): obtener_handoff, leer_transcript, seleccionar, convertir_moneda. Run: `TOOL_DATA_DIR=<data-pipeline>/data TOOL_SERVICE_TOKENS=agent-core:<token> uv run tool-service`.

### 1.5 data-pipeline

Medallion with dbt + DuckDB. Inputs: 13 challenge tables (S3, CSV by day) plus E0 sample (11 parquets). Silver: typed, deduped, four null types, quarantine with reasons; canonical `platform_history` models (cases, turns, tool_calls, approvals, signals, copilot_queries, ...). Gold: `gold_restricted` (clear PII; customer_cases/products/profile/transactions/digital_summary), `gold_masked`, `gold_analytics` (HMAC pseudonymized; demand, contact reasons, campaign performance, DQ marts), isolated `eval.duckdb` (labels/timeline). Publishes artifacts, `release.json`, `latest.json`, `field_classification.json`, `read_model_contract.json`. Silver volumes: customers 150,000; products 399,994; transactions 4,423,656; digital_events 15,620,994; complaints 67,095; interactions 686,121; transcripts 171,277. Holds bank-challenge data including PII in the restricted zone; no data was opened. Run: README (`pipeline.ingest_bank`, `dbt build`, `pipeline.publish`); needs dataset credentials. Pending: contact-center platform event_log feed.

### 1.6 data-lab

Data-science side: `pipeline/` (contracts, parquet conversion, quality profile), `analysis/` (demand, learnability, legacy coverage), `synthetic/platform_sample.py` and `writer_prompt.md` (synthetic platform-history sample for the AI team), `contracts/` (seed-dataset dictionary, synthetic-sample contracts), `reports/{demand,ml,platform,quality}` (aggregates, no record-level data), `docs/` (dispute policies, security questions; Spanish). Dataset itself is git-ignored.

### 1.7 bruno

6 requests for agent-core `/v1` (create run, post turn, get run, transcript, handoff, resolution) plus a `local` environment with secret vars. Stale vs. current API (no registry, lineage or export). No collections for llm-gateway or tool-service.

## 2. What can be demoed now (exact steps)

Nothing was executed in this survey. Use a clean checkout (e.g. `D:\.codex\factored\tmp\survey\agent-core`).

A. Offline, no network, no Postgres (README; most reliable):
1. `uv sync --locked`
2. `uv run agentcore validate tests/fixtures/registry-transfer-demo`
3. `uv run agentcore replay tests/fixtures/runs-transfer/transferencia.yaml --mode fixture --registry tests/fixtures/registry-transfer-demo --catalog tests/fixtures/catalogo-datos-prueba.yaml` (recepcion to disputas transfer, two audit chains)
4. `uv run agentcore replay tests/fixtures/runs/resuelto.yaml --mode fixture --registry tests/fixtures/registry-demo --catalog tests/fixtures/catalogo-datos-prueba.yaml` (also cancelado, escalado_por_monto, step_up, interrupcion, uncertain_verify)
5. `uv run pytest tests/composition/test_transfer_demo.py` (full session in process and over HTTP, with lineage)
6. Registry gate without an LLM: `uv run pytest tests/registry/test_gate.py tests/registry/test_policy_locked.py tests/registry/test_reject_reason_code.py tests/registry/test_release_settings.py tests/registry/test_evaluator.py`

B. Live local stack (`docs/runbook-e2e.md`): Docker, keys (`OPENROUTER_API_KEY` for the gateway, `AGENTCORE_JEV_API_KEY` for Understand) in `scripts\e2e\.env.e2e`; `.\scripts\e2e\setup.ps1`, `.\scripts\e2e\serve.ps1`, then `.\scripts\e2e\chat.ps1 -As customer -Agent recepcion` (dispute scenarios), `-As advisor -Agent copiloto-asesor`, `-As supervisor -Agent constructor-chat`; `.\scripts\e2e\check.ps1 [-Llm] [-Conversations]` for automatic checks; `.\scripts\e2e\report.ps1` for metrics; optional Phoenix on :6006 via `OTEL_EXPORTER_OTLP_ENDPOINT`. Langfuse: point the OTLP endpoint/headers at Langfuse (PR #48); live run unverified. Message content in Langfuse needs `LLM_GATEWAY_TRACE_CONTENT=1` on the gateway (agent-core spans carry no content). Not demonstrable live: transfer via `serve`, constructor evaluate/publish loop.

C. Real tools: run tool-service on :8095 over a published data-pipeline `data` dir, then `.\scripts\e2e\serve-tools.ps1`; chat as advisor with a customer id from the dataset (copilot answers balances, last movement, cases). Needs the dataset built locally (about 6 min dbt) and challenge credentials; runbook says authors verified it, unverified here.

D. Gateway alone: `go test ./...` offline; `go run ./cmd/llm-gateway` plus the README curl needs a provider key.

E. tool-service alone: `uv run pytest` (synthetic dataset, no network).

## 3. Gaps and risks

1. GitHub CI for agent-core has not run since 10-03 (billing); PRs #32 to #56 merged on local gates only. Highest process risk.
2. The constructor-to-publish improvement loop has no eval_suite in any demo registry; propose/evaluate/approve/publish/promote is covered by unit/contract tests (`tests/registry`) but not demoed live. An eval_suite fixture must be authored to show it.
3. Transfer recepcion to specialist works only in fixtures/in-process, not over `agentcore serve`; the threshold artifact `cal-transfer-demo.json` is hand-made.
4. Serve still has doubles (transcript in memory unless Postgres wired, calibration, classifier, permissive authz unless PolicyAuthz). Calibrations are synthetic.
5. llm-gateway never exercised against a real provider by its author; no routing or policy layer, so the mimo/glm model policy lives only in callers' model profiles. No retries or fallback by design.
6. Audit replay on real runs diverges (3 known causes); do not claim reproducible audit for real runs.
7. No SQL metrics views; metrics come from `report.py` and Phoenix.
8. data-pipeline lacks the contact-center platform event_log feed; data-lab has no tests seen; bruno stale.
9. Portuguese: engine switches es/pt only with demo thresholds; bank policy text (runbook) says Portuguese is handled by a person while data-lab H1 lets the assistant serve it; alignment unverified.
10. Open PRs: agent-core #57 and #58 (author jzapataca). Other repos' PR state is as of the check before the gh rate limit.
11. Secrets live in `scripts\e2e\.env.e2e`; never print. PowerShell scripts need UTF-8 with BOM.

## 4. Evidence (paths)

Clones: `D:\.codex\factored\tmp\survey\{agent-core,llm-gateway,tool-service,data-pipeline,data-lab,bruno}`.
- agent-core: `README.md`, `docs/runbook-e2e.md`, `docs/plan-e2e-produccion.md`, `docs/adr/0018-*.md`, `0020-*.md`, `0021-*.md`, `0024-*.md`, `0025-*.md`, `agent_core/registry/{models,service,candidate,suite,roles,http}.py`, `agent_core/registry/evaluation/*`, `contracts/openapi.json`, `contracts/registry-openapi.json`, `tests/fixtures/registry-e2e/{agents,flows,releases,model_profiles}`, `scripts/e2e/*`.
- llm-gateway: `README.md`, `api/openapi.yaml`, `docs/decisions-for-review.md`, `docs/consuming.md`, `internal/telemetry`.
- tool-service: `README.md`, `contracts/tool-provider.openapi.json`, `registry/tools`, `src/tool_service/tools`.
- data-pipeline: `README.md`, `docs/04-resumen-para-la-entrega.md`, `dbt/models/*`, `src/pipeline/*`.
- data-lab: `README.md`, `contracts/`, `synthetic/`, `reports/`.
- bruno: `README.md`, `agent-core/*.bru`.
Not read: improvement-engine, support-platform, infra.
