# Upstream survey, 2026-10-04 (read-only)

Method: shallow reads of pulso-factored repos cloned into the scratchpad, plus `gh` listings of PRs, branches and commit times. No code was run, and nothing under D:\Nexus or any repo was touched. Out of scope here (covered by spike S1): the code of agent-core, tool-service and llm-gateway. Commit times are UTC (GitHub API).

Heads read: bruno e3d493c, data-pipeline 2f36f6b, data-lab 0e666a6, support-platform eeb73a8 (+ PR 11 branch), agent-core e725e91, infra at main (PR 32 open), tool-service at main.

## Org map and ownership

Repos in the org: improvement-engine (OURS, pushed 22:23Z), agent-core, infra, tool-service, support-platform, data-pipeline, data-lab, llm-gateway, bruno. No other repos.

| Repo | Who writes | Merge pattern |
|---|---|---|
| agent-core | `juazapataca` (Juan Jose Zapata), commits co-authored with Claude. Merges by "Juan José Zapata Cadavid" via PR. | About 36 PRs in 6 days. Commit counts per day: 278 (09-29), 140, 57, 47, 27, 8 (10-04). Large trains merge in bursts of 3 to 6 PRs per day. |
| support-platform | Juan Mejia (original platform S1-S12, up to 10-03/10-04) -> repo split on 10-04. Juan Esteban Mejía (`jmejiaes`: frontend, policy, language). Zapata (AI integration S13-S17). | 11 PRs, all opened and merged on 2026-10-04 (merges between 19:31Z and 20:33Z). |
| data-pipeline | Zapata only (18 commits since 10-03, no PRs, pushes straight to main). | Several feature commits per day. |
| data-lab | Mejía team (13 commits, 1 PR). Data side split from the platform on 10-04. | Policy and contract changes only. |
| infra | Zapata, Andrés Galvis and Alexis Galvis (user's own). | PRs 27 to 31 merged. PR 32 "Hackathon foundations (single prod environment)" is open. |
| tool-service | Zapata. Created and merged on 10-04 (PR 1). | Created 21:12Z, last merge 22:14Z. |
| llm-gateway | Zapata. Last merge 10-03 16:12Z (PR 3: consumer docs, release, input caps; PR 2: `POST /v1/jev`). | Quiet since 10-03. |
| bruno | `juazapataca`, 2 commits, last 09-29. | Dormant. |

Cadence prediction: Zapata is the single point of upstream change across agent-core, support-platform, data-pipeline, infra and tool-service. He ships in whole-day bursts (agent-core 10-02 to 10-03, platform and tool-service 10-04), then moves to the next repo. Do not predict a calendar. Predict that open PR 34 and infra PR 32 merge within a day or two. Any branch or ADR named here can land within hours. Re-fetch before relying on a contract, rather than trusting this snapshot.

## 1. bruno

Purpose: a Bruno API-client collection ("endpoints of each service"). Today only agent-core's runtime `/v1`. It is not the platform, the tool-service or the gateway, and it has no registry requests. The shape is: one top-level folder per service; each service folder holds numbered `.bru` requests.

- Changes: 09-29, "colección Bruno con los endpoints de agent-core (/v1)" then "renombra la colección a bruno". Nothing since.
- Collections and requests (folder `agent-core/`, 6 requests):
  1. `POST /v1/runs`: body `{agent}`, header `Idempotency-Key`, returns 201 `{run_id, session_id, trace_id}`.
  2. `POST /v1/sessions/{id}/turns`: body `{text, channel, client_turn_id}` or `{confirm:{token,answer}}`.
  3. `GET /v1/runs/{id}`: `{run_id, status, outcome, locale, awaiting, handoff_ref, trace_id}`.
  4. `GET /v1/runs/{id}/transcript`.
  5. `GET /v1/handoffs/{ref}`.
  6. `POST /v1/handoffs/{ref}/resolution`: `{resolution_code, handoff_quality, notes}`.
- Environment `local`: `baseUrl=http://localhost:8000`, `agent=atencion`, `publicAgent=faq`, `runId`, `sessionId`, `handoffRef`. Secrets: `customerToken`, `advisorToken`, `advisorDelegation`, `anonymousToken`, `expiredToken`, `steppedUpToken`.
- Auth patterns: `Authorization: Bearer <JWS>` (Ed25519). The advisor adds `X-On-Behalf-Of: <delegation JWS>`. Only `service` and `builder` may pin `id@alias` or `id@X.Y.Z` (403 `version_pin_forbidden`). The subject is derived by the server (a foreign one gives 403 `subject_forbidden`). Errors are `application/problem+json` with `code` and `trace_id`. Step-up flow: `awaiting:"step_up"`, then retry with `steppedUpToken`. Tokens come from `agent-core/testing/demo_identities` and are TEST-key signed.
- Not covered: registry/proposals/evaluations, `/v1/export`, platform, tool-service, gateway. Its README admits it was never executed and that `agentcore serve` was not yet wired (stale: `serve` exists now).
- Means for us: low value as a map of the platform. It only confirms the runtime contract. The real maps are `agent-core/contracts/openapi.json` plus `contracts/registry/`, and platform `docs/platform/api/slice-14/15/16` (see section 4).
- Watch: whether registry or export requests are added (that would be a free request catalog for the "Builder as an agent" tests). Currently not expected.

## 2. data-pipeline (head 2f36f6b, 2026-10-04)

Purpose: dbt + DuckDB medallion pipeline (bronze, silver, gold) that turns the challenge dataset (13 tables), the E0 sample and later the platform event log into governed read-models for agent-core's tools and for analysis.

Latest changes (no PRs; direct commits, all by Zapata):
- 10-03: bronze/silver slices, canonical `platform_history` model with `source_system`, gold layers, FieldClassification catalog, governance, `gold_masked`, container image, S3 lake root and publication upload, separate dataset vs lake credentials.
- 10-04: call-center interactions and transcripts (cb86d1c), CSAT surveys in `case_close` (100d905), evaluator zone in its own `eval.duckdb` under `bronze_eval` (c925bd7), `campaign_sends` and `digital_events` completing all 13 tables (3db8835), single dbt thread (bb3bb5f), and 2f36f6b read-model contract + subject-sorted publication + demo customer links.

What the read-model contract is (docs/03-contrato-de-lectura-y-vinculo.md, `src/pipeline/read_contract.py`):
- `read_model_contract.json` is generated on every publication from the real schema, the classification catalog and the null policy. Per zone and table it carries `grain`, `key`, `subject_column` (`customer_id`, or `customer_pseudo` in the masked zone), `physical_order`, `semantics`, and per column `type`, `class`, `null_type`, `null_note`, `related_flags`. A read-model without documented grain or semantics blocks publication.
- Null types: `structural`, `state`, `derivable`, `missing_real` (never impute), `not_in_source`.
- `as_of = 2026-06-18`: the data end. "Recent" is measured against that date, not the clock.
- Read rules: always `WHERE subject = ?` taken from the verified principal; always an explicit `ORDER BY`. Measured p95 27 ms (was 97 ms) on a laptop; not measured on real infra or under load.
- Publication layout (S3 or local `PIPELINE_ROOT`): `publish/<run_id>/` immutable, then `publish/latest.json` moved last. Files: `gold_restricted.duckdb` (5 read-models, PII in clear, tool-service only), `gold_masked.duckdb` (consumers not going through agent-core; subject `customer_pseudo`), `gold_analytics.duckdb` + `parquet/` (pseudonymised aggregates), `field_classification.json` (agent-core `FieldClassification` format, 545 entries), `read_model_contract.json`, `release.json` (run_id, git sha, row counts, hashes, quarantine).
- Gold analytics marts (dbt): `case_facts`, `contact_reasons_monthly`, `demand_monthly`, `campaign_performance_monthly`, `digital_events_daily`, `dq_freshness`, `dq_null_profile`, `dq_quarantine`. Canonical (`platform_history` v0.5.1 aligned) tables: cases, case_closes, turns, tool_calls, routing_steps, approvals, copilot_queries, identity_checks, signals.
- Cadence: EventBridge Scheduler -> ECS Fargate task (infra ADR 0006, `data_pipeline` module merged in infra PR 30). Ingest of E0 is a one-off. Cadence value not stated in the repo. A full build takes about 6 min on a laptop, with 232 dbt checks.
- Consumers: tool-service (restricted; polls `latest.json` with a 60 s TTL; no push notification exists), analysts (masked), analysis/ML (analytics), agent-core (`--field-classifier`).
- Demo links: `pipeline.demo_links` deterministically maps the 19 platform seed customers to dataset customers (country and language matched; prefers ones with an E0 dispute). Output stays private under `data/demo/`. Known limits: the dataset has no Brazil or Portuguese customers (the BR seed customer 1008 is linked to a MX one; Portuguese comes only from E0 stress cases).
- Not found: no Postgres schema, no S3 path beyond `publish/`, `bronze/`, `bronze_eval/`. The `eval.duckdb` zone (labels, timeline, replay_order) is evaluator-only and must not be read by us as a feed.

Is it the "Product team data model artifact" or a new feed? It is a new, distinct data feed. It is the engineering team's governed publication of the bank dataset, not the product team's model. Its canonical model (`platform_history` v0.5.1) is the shared event contract that data-lab publishes and that the platform will emit again (ADR 0003 item 9). For dataset mode, the usable parts are the analytics parquet + `read_model_contract.json` (self-describing) and, for platform-history-shaped replay, the `canonical` tables. There is no layout that conflicts with our `db/` schemas, because nothing here is Postgres. Alignment point to check: our event/entity naming vs `platform_history` v0.5.1 and `source_system` values (`e0_sample`, `bank_complaints`, `bank_interactions`).

Means for us: opportunity (an immutable, versioned, contracted feed with a `dataset_run_id`, `as_of`, null semantics, and masked or pseudonymised variants we can read without PII). Risk: `as_of` 2026-06-18 means any "recent" window logic must use it, and the restricted zone currently has no real access control (their own brecha 1).
Watch: new files in `publish/`, a `kid`-based pseudonym rotation (re-publication changes every pseudonym), platform event-log ingestion (planned "later" in plan-v1; fixtures today), and `latest.json` notifications.

## 3. data-lab (head 0e666a6, 2026-10-04)

Purpose: data side of the hackathon: dataset ingestion/quality, dataset and synthetic-sample contracts, demand and learnability analyses, business policy documents.

- 10-04: PR 1 `policy/assistant-serves-portuguese` (0e666a6): policy H1 rewritten. Before: the virtual assistant did not serve Portuguese; Portuguese went to humans. Now: the assistant serves Spanish and Portuguese, and a handoff goes to a person who speaks the customer's language. The "client speaks Portuguese" handoff trigger was removed from the dispute rules. Rationale kept: the dataset has no Portuguese customers and only 129 of 1,200 advisers speak it.
- Same day: repo split (data side separated from platform), English naming for implementation docs, contracts reorganized into `contracts/seed-dataset/tables.json` and `contracts/synthetic-sample/{platform_history.json, evaluation.json}`.
- Earlier (10-01 to 10-02): dispute policies, risk-based identity verification, branch complaints as outbound call, platform S0.
- Content: `analysis/` (demand, learnability, legacy_coverage), `reports/{demand,ml,platform,quality}`, `synthetic/` generator. Nothing new on complaints or contacts beyond existing demand analyses. The contact and complaint data model lives in the synthetic-sample contract (`platform_history.json`).
- Means for us: the `platform_history.json` contract is the event/entity contract to align with. The H1 change means Portuguese flows are now in scope for the assistant, so any evaluation or improvement hypothesis about language/handoff must not assume Portuguese always escalates.
- Watch: edits to `contracts/synthetic-sample/*` (breaking changes to the event envelope), `docs/policies.md` (only rule 3 / H1 applies to the platform; the other rules were dropped by the platform brief).

## 4. support-platform (head eeb73a8; PR 11 open)

Purpose: LATAM Bank dispute-intake support platform (API + web app + docs), people-first, now with AI through agent-core.

Latest changes (all 2026-10-04):
- PR 3 (13 + S14): assistant-handled chat, with handoff to people.
- PR 4 (S15): analyst copilot + handoff priority.
- PR 9 (S16): agent builder backend (registry client, `/builder/*`, audit).
- PR 6 and 10 (S17 hardening): sweep for lost assistant work, `grant_active` endpoint, ADR 0004 tool service.
- PR 8: policy H1, Portuguese. PRs 1, 2, 5, 7: brief refresh, English routes, language marks.
- PR 11 (OPEN, branch `docs/adr-0004-claims`): ADR 0004 changed so the tool service receives verified claims plus `bound_params`, not a JWS (agent-core does not keep the token). Context shape: `principal {type,id,roles,scopes,attrs,auth_level}`, `subject {kind,ref}`, `on_behalf_of {subject,grant_ref,grantee,scopes}`, `run_id`, `call_id`, `release`, `turn_id`. Docs only; mirrors agent-core ADR 0025.

ADRs in `docs/platform/adr/`: 0001 architecture, 0002 (superseded), 0003 agent-core integration, 0004 tool service (status Proposed; T1 agent-core side built).

Builder (slice 16, the part closest to us) per `docs/platform/api/slice-16-agent-builder.md`:
- The platform is a client of agent-core's registry. A person acts with her own `builder` credential, minted from her session (Supervision = constructor + approver; Administration adds admin). Approve, reject, publish, promote and revoke require a fresh authenticator code (`stepUpCode`), which raises that one call to `step_up` for 2 minutes. Nothing is remembered.
- Endpoints (`/builder/*`): status, proposals list/create/track/get, `PUT .../draft` (replaces the whole draft; `expectedRev`), validate, freeze, reopen, evaluate (blocks until done; 409 `registry_gate_failed` returns the proposal to draft), approve (409 `registry_loosening_not_accepted` unless `acceptYardstickLoosened`), reject, publish (`Idempotency-Key`), alias promote (`staging`/`prod`), release revoke (Admin only), release/alias/version/entity reads, release diff, and the builder chat (`constructor-chat`, one thread per person, max 2000 chars, idempotent by `clientMessageId`).
- Proposal states: draft -> candidate -> evaluated -> approved -> published. Origin enum in `builder_proposals`: `manual|builder_chat|auto_detect|import`. Registry events carry origin; auto-improvement is meant to write proposals with `origin=auto_detect` (agent-core ADR 0018 and 0019).
- A person may approve her own proposal (agent-core ADR 0018 amendment 4): the barrier is human + step-up, not a second person. The agent builder never approves or publishes.
- Known gaps (open): no agent has an `eval_suite`, so nothing goes past `candidate` and nothing can be evaluated or published (404 `registry_not_found`). The registry had no list call (platform keeps its own index); agent-core PR 24 added `GET /v1/registry/proposals` with filters, but the platform's doc has not caught up. Response schemas for `ProposalDetail`, `ValidationReport`, `CandidateView` are not published. Platform guardrail policies cannot be edited through a proposal.

Coming (from ADR 0003 slice plan and brief; no dates):
- S17 production hardening: Postgres and migrations (platform is SQLite, no Alembic; schema change = delete the DB), real email adapter, real customer authentication, secrets, outbound-event consumption, trace ids across both systems. Track T: `/internal/agent-tools/*` in the platform vs the separate tool-service (the tool-service exists now; ADR 0004 decided on the separate service).
- Builder screens ("Supervisión · Agentes -> Propuestas", draft editor, evaluation, release/aliases, "Constructor" chat): frontend team's, from the hand-over; no screens yet.
- Events: platform event log will emit AI entities of `platform_history` (routing step, tool call, copilot query) so data-pipeline can read them; agent-core's `run.*`, `handoff.*`, `release.*` outbound events are consumed later by relay or the export API, for analytics only.
- Open points: SLA semantics for agent replies, how much agent chain is shown in audit, real customer auth.
- Not found in docs: any "case type", "copilot draft dispositions" or "automation" plan. Grep of `docs/` and backend README found no such items; automation is explicitly out of scope (brief §1, §4). Treat those as unconfirmed.
- Signal on timing: none stated. Platform S13 to S16 backend landed in one day. Postgres and migrations are called a known gap, so a schema break risk exists if we read the platform DB or its tables.

Means for us: the builder flow is the human-governed path we should feed (proposals with `origin=auto_detect` through agent-core's registry, not the platform). Risk: the missing `eval_suite` blocks any end-to-end proposal publication, so improvement proposals will stop at `candidate` until someone authors suites. Opportunity: the platform's audit, `builder_proposals` index and the platform event log (once emitted) are consumable signals.
Watch: PR 11 merge; frontend branch for builder screens; Alembic/Postgres; the `internal/grants/{grantRef}` endpoint (used by agent-core PR 36); `CC_AGENT_CORE_URL`; any `eval_suite` entity.

## 5. agent-core (docs only; head e725e91)

Purpose: the decision engine and registry (runs, sessions, handoffs, registry proposals, evaluation gate, outbound events, export).

Open PR: only 34 (`feat/tool-service-wiring`): serve with the tool-service and the published `field_classification.json` (overlay file for engine-owned fields; unclassified stays `pii_direct`); `scripts/e2e/serve-tools.ps1`; verified live with the copilot answering from the real dataset. Still demo doubles: transcript, calibration (and, per PR 35, authz needed binding).
Already merged (the brief called them open): PR 35 `PolicyAuthz` (the real AuthzPort; `AGENTCORE_AUTHZ_BIND_KEYS`, field-grants file; fail-closed, grants are governance's call) and PR 36 `grant_active` over HTTP against the platform (`GET {AGENTCORE_GRANTS_URL}/api/v1/internal/grants/{grantRef}`; bearer shared with the platform's `CC_INTERNAL_SERVICE_TOKEN`; fails closed; positive answers cached 5 s). PR 33 `HttpToolExecutor` (ADR 0025).
Branches `ctr`, `jev`, `lst` hold stale or already-merged work (the last commits are 10-02/10-03).

Docs relevant to improvement/evolution/proposals:
- ADR 0018 (proposals and publication gate): all changes are proposals through the registry API; the old self-improvement flow stops opening PRs and writes proposals with `origin=auto_detect`; each agent needs an `eval_suite` with noise margins and floors per `gate`/`guardrail` metric (ADR 0020 replaced the single-score design); no composite score, because it can hide a safety regression; unevaluated agents cannot be published.
- ADR 0019 (internal agents): the constructor is two agents (a `conversational` one for chat, a `task` one triggered by a signal, e.g. the automatic detector with `origin=auto_detect`, which needs to write proposals). Constructor writes proposals only; it never approves or publishes.
- ADR 0020 (evaluation and metrics per agent), ADR 0021 (transfer between agents), ADR 0022 (stable surfaces, expand-only migrations; the stable surface is fixed by a signature test; compatible within one major `SCHEMA_VERSION`), ADR 0023 (S3 blobs, relay, pool), ADR 0024 (llm-gateway as an external service), ADR 0025 (tool executor as an external service; contract in section 2 of the S1 scope, not repeated here).
- `docs/specs/2026-10-02-eventos-salientes-design.md` and `contracts/events/`: outbound events `run.*`, `handoff.*`, `release.published|promoted|revoked`. Export API `/v1/export` (runs, run events by cursor, registry events by cursor; new role `exporter`; run summaries without customer data). That is the channel an improvement engine can read, not the outbox. `exporter` credentials must be minted by infra's staff issuer.
- `docs/informes/2026-10-02-solicitudes-n01-n11-decisiones.md`: requests N-01 to N-11 from a dependent team (registry schemas in `contracts/registry/`, `GET /version`, alias and version reads, `eval_run_id` in gate_failed, release-level changes via reserved `release_settings` draft (N-07), export (N-08), hot reload of identity/staff keys (N-09)). Every decision there was taken overnight without review.
- `docs/plan-e2e-produccion.md` and `docs/runbook-e2e.md`: real blockers for production are tools, authz, transcript store, calibration and the FieldClassifier (being replaced now). Replay `audit` of real runs gives `diverged` (design reasons in M11: clock per turn, `result_fp`, draft with citations).
- Nothing in docs names "improvement-engine" or "Pulso engine" explicitly; the integration language is "auto_detect", "exporter", "other teams".

Means for us: the whole write path for us is registry proposals (`origin=auto_detect`) and the read path is `/v1/export` plus outbound events; both exist. The blocker is `eval_suite` content and the exporter role.
Watch: PR 34 merge; ADR 0026 or later; `contracts/registry/` response schemas; a registry list endpoint (already added on branch `lst`/PR 24, check it is in main); `eval_suite` authoring; changes to `SCHEMA_VERSION`.

## 6. Other repos worth a line (outside the list, relevant to us)

- infra: PR 32 open, "Hackathon foundations (single prod environment)" (bootstrap, network, IAM, edge, data, three-host compute, release script). Branches `docs/agent-core-delivery-contract`, `docs/infra-engine-design-alignment`, `docs/adr-0003-agent-core-workload`, `feat/i05-staging-prod-environments`, `feat/i04-terraform-reframe`. The `infra-engine-design-alignment` and `agent-core-delivery-contract` names point at our engine's deployment shape. Check them. The ADR 0006 access matrix is the definitive map of who reads which S3 prefix. Retention and `kid` rotation open.
- tool-service: new on 10-04; PR 1 accepts `subject_ref` as the subject parameter (to match PolicyAuthz bind keys). Covered by S1.
- improvement-engine: ours. Many `codex/*`, `feat/*` branches; PR 97 open ("Runnable magic demo: Rust thread, debug API for the console, pulso binary"). Not an upstream.

## Eight findings most relevant to our integration

1. Upstream's write path for improvement is explicit and already built: registry proposals with `origin=auto_detect` (ADR 0018/0019) plus human step-up approval. The constructor "task" agent exists for signal-driven proposals.
2. The read path is `/v1/export` (runs, run events, registry events, cursor-based) with a new read-only `exporter` role that infra's staff issuer must mint. Outbound events are the public channel; the outbox is not exported.
3. No agent has an `eval_suite`, so no proposal can pass `candidate` or be published. This is the real gating item for any improvement flow, and content work is unowned.
4. data-pipeline now publishes an immutable, self-describing `publish/<run_id>/` set with `read_model_contract.json`, `as_of=2026-06-18`, masked and pseudonymised variants. `gold_analytics` parquet and the contract are usable in dataset mode; there is no Postgres or `db/` overlap.
5. The platform is SQLite with no migrations, and moves to Postgres in S17; expect a schema break if anything reads its tables directly. Use the API, events and audit instead.
6. Policy H1 changed on 10-04: the assistant serves Portuguese; humans only get it on handoff. Evaluations and hypotheses that assumed Portuguese escalates are now stale.
7. PR 11 and ADR 0025 settle the tool contract: the service receives verified claims + `bound_params`, not a JWS. PRs 35 and 36 are merged, so authz and grant checks are real; PR 34 is the only open agent-core PR. Remaining demo doubles are transcript and calibration, which is where the real-production blockers remain.
8. Upstream is essentially one author (Zapata + Claude) shipping in daily bursts: 36 PRs in 6 days in agent-core, 11 platform PRs in a single day. Contracts can change within hours, so pin and re-verify.

## Surprises

- The brief listed PRs 34/35/36 as open, but only 34 is open; 35 and 36 merged on 10-04.
- bruno is much thinner than expected: 6 runtime requests and no registry or platform endpoints.
- The platform docs still say the registry has no list call, but agent-core's `GET /v1/registry/proposals` was added in PR 24 (10-02). Not confirmed that the platform adapted.
- Nothing found on "case type", "copilot draft dispositions" or automation in the platform docs.
- infra branch names `docs/infra-engine-design-alignment` and `docs/agent-core-delivery-contract` suggest upcoming deployment alignment for our engine; unread.
