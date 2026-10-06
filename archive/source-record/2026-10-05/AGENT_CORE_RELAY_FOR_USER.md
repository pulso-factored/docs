# Relay for the Agent Core team (from Team Claude, Pulso consumer)

Forward as is. Updated after re-verifying agent-core `main` at `894fa65` (2026-10-03, PR #29), which the team said fixes our 10 findings. We re-ran every repro against a fresh checkout with a throwaway Postgres 16: details and evidence in `AGENT_CORE_PIN_FINDINGS_CLAUDE.md` (Section 0 status notes, Section 9) and `LLM_GATEWAY_ADOPTION_CLAUDE.md`. Thank you for PR #29.

**Status refresh 2026-10-04 (UTC, Team Claude, verified with `gh api`).** agent-core `main` is now `c814c2b` (PR #30 merged 2026-10-03T21:03Z, 6 commits on top of `894fa65`; wire byte-identical, only `composition/{builder_tools,serve,serve_ports}.py` changed under `agent_core/`). improvement-engine `main` pins `894fa65` (PR #82 merged); the bump to `c814c2b` is in progress on our side (not yet a PR; see `AGENT_CORE_PIN_BUMP_3_ANALYSIS_CLAUDE.md`). Re-checked today: PRs #23, #24 and #28 are still NOT on `main` (heads `5705e58`, `19e7a10`, `3499f94` are not ancestors of `c814c2b`; `registry_openapi.py`, `contracts/registry-openapi.json` and `jev_gateway.py` do not exist on `main`). Sections A (items 11-12), B (items 7-9) and D below were added or refreshed in this pass; everything else is unchanged and still open unless marked.

## Fixed, verified (no action needed)

F-01 (eval replay), PR27-01 (sweep with S3 blobs; the sweep job must get the same `AGENTCORE_BLOB_BUCKET` env as `serve`), F-02 (concurrent same-key runs: now 1 run plus 409s), F-03 (opt-in `Agent.input_schema` plus rule AG-04), PR27-02 (outbox unknown type), NF-01 (admin gate for interrupts, `locked`, cap 100000, `release_changes` review), NF-02 (commit-ordered export cursor), F-06 (spend-only limits, `Retry-After`, env knobs), F-08 (UTF-8 CLI output).

## A. Still open for the Agent Core team (priority order)

1. **N8-01 (S2) PRs #23, #24 and #28 are not on `main`.** They were merged after their parent PR had already merged, so they landed in stacked side branches (`ccr-a4781bdb-dnrn7q` head `5705e58`, `feat/registry-contratos` head `19e7a10`, `feat/http-llm-gateway` head `3499f94`); `git merge-base --is-ancestor` against `origin/main` is false for all three and their files (`registry_openapi.py`, `contracts/registry-openapi.json`, `list_proposals`, `jev_gateway.py`) do not exist at `894fa65`. Please retarget/re-merge them into `main`, or confirm they are intentionally held. We will not plan on them until they are on `main`.
2. **F-04 (S2, PARTIAL) Run/transcript read isolation.** The hard rule now covers customer and anonymous principals only. An advisor without delegation still reads a customer's run with a permissive `AuthzPort` (200 in our probe), and service/builder principals depend entirely on the port. Please extend the hard rule (advisor needs a valid delegation for that subject; service needs an explicit scope) and ship a port contract-test kit.
3. **N8-02 (S3) `409 idempotency_conflict` is now ambiguous.** It means both "same key, different body" and "same key still in flight or held by a crashed attempt for `lease_ttl` (60 s)". There is no `Retry-After`, and reserved-but-uncommitted rows are invisible to `get_run_idempotency` (`result_json IS NOT NULL`). Please use a distinct code (for example `idempotency_in_progress`) with `Retry-After`, and say what a consumer reconciling after a timeout should read.
4. **N8-03 (S3) Export cursor caveats.** (a) After `migrate` all pre-existing runs share one `change_xid` and `limit` counts commits, so the first page returns every legacy run unbounded (we reproduced 5 legacy rows with one xid); (b) the cursor is bounded by `pg_snapshot_xmin`, so any long transaction in the database stalls the export for every consumer; (c) old-version pods update `runs` without `change_xid`, so closes are not re-exported during a rolling deploy; (d) the volatile-default `ADD COLUMN` rewrites `runs` under an exclusive lock. Please document or mitigate (backfill with distinct values in batches, a note on deploy order, a bounded first page).
5. **N8-04 (S3) Rolling-deploy safety of the new SQL.** An old pod reading a reserved `run_idempotency` row (`result_json NULL`) fails in `RunResult.model_validate(loads(None))` (code reading). Document "migrate, then all pods" or make old readers tolerant.
6. **N8-08 (S3) `contracts/VERSION` is still 1.3.0** although `Agent`, `Interrupt`, `Release`, `ReleaseDetail`, `ReleaseSettings`, `StoredRelease` and `RunSummary` changed (`RunSummary.cursor` is required) and a new validation rule (AG-04) can make previously publishable task flows unpublishable. Please bump the contract version (minor) or publish a changelog consumers can key on.
7. **N8-07 (S3) Release ids change** for releases that carry interrupts (`locked` default false enters the hash): our `attention-demo` release went from `rel-98130317a1003849` to `rel-da313458b550780a`. Please state in the changelog that ids of releases with interrupts change, and that the `registry-demo` seed is now `locked: true`.
8. **N8-05 (S3) Outbox rows of an unknown type are skipped silently** (they stay pending forever, uncounted, no alert, no dead-letter). Please expose a counter or dead-letter path so a rolling deploy cannot hide undelivered messages.
9. **N8-06/N8-09 (S3/S4)** Rate-limit in-flight accounting is per process (burst bound is N replicas x max_hits; say so in the docs and echo the effective limits at startup); `put_draft` accepts `max_input_chars` above the cap and only `freeze` rejects it.
10. **PR #30** (MERGED 2026-10-03T21:03Z as `c814c2b`): the note for its authors still applies on `main`, because we did not re-run it at `c814c2b` (JEV rejects `interrupt: enum []` with a 500 for releases without interrupts; `respond(await)` + `collect` drops the user message). Please confirm whether the merged version fixed either.
11. **`resolve_ports` reads `args.lang_thresholds` with attribute access (S3, found in bump 3).** Embedders that build the `argparse.Namespace` by hand (we do, in `synthesise_args`) get `AttributeError` at startup on `c814c2b`; only PG-backed tests catch it. Please use `getattr(args, "lang_thresholds", None)` or document the minimal args contract (same shape as earlier `ServePorts` additions). We work around it by starting from the real parser defaults.
12. **c814c2b builder tools and `registry-e2e` overlap (question, not a defect).** (a) Is `RoutedTools` plus the constructor service principal in `run_serve` meant to become a reusable helper (for example `compose_builder_tools(ports, registry_service)`) for embedders that do not call `run_serve`? Otherwise we keep our own protected builder composition. (b) `tests/fixtures/registry-e2e` reuses ids and versions of `registry-demo` with different bytes (`decision_models/match-cargo@2.0.0`, `decision_models/understand-turno@1.0.0`, `language_detection/lang-es-pt@1.0.0`, `model_profiles/perfil-generacion@1.0.0`, `prompts/p/resumen_radicado@1.0.0`, and all ten `tools/registry/*@1.0.0`); immutable digests make loading both into one registry a conflict. Please confirm they are only ever loaded into separate registries. We do not load them.

Next tier (unchanged, not re-run at `894fa65`): F-07 (scenarios cannot express task agents, subjects or principal types), F-05 (`serve` outside demo), PR27-03..05 (pool sizing and readiness, S3 rollback hazard, relay head-of-line), NF-03 (export scope), NF-04 (key reload failures are silent), F-09..F-12, F-14, F-15. F-10 (405 maps to `invalid_request`) re-observed live at `894fa65`.

## B. Infra questions (Core workload slice)

1. Who owns the `pulso_bridge` schema DDL in the eval database? The runtime applies it at startup with `AGENTCORE_EVAL_DSN`; may that role create it, or should the `migrate` task run it?
2. Will the Core workload slice add an optional tmpfs volume to `workload` (ADR 0003 item 12), or is ephemeral task storage acceptable for key files delivered from Fargate secrets?
3. Which module opens the exporter security group toward `control-api` and the Core database? We will consume its output as `core_callback_security_group_ids`.
4. Is this secret layout acceptable: `core/bridge-signers` (4 seeds), `core/exporter-keys` (2 seeds), reuse of `core/bridge-service-key`, `core/llm-gateway-token`?
5. Should `core/jev` and `core/llm-endpoints` be dropped from the Core workload slice, given the composed runtime consumes the gateway only (ADR 0004)?
6. Is a shared Cloud Map namespace `<env>.pulso.internal` acceptable, and who creates it?
7. Pin text: CLOSED on our side. infra PR #26 (merged 2026-10-03T23:37Z) moved ADR 0003 and the release fixtures to `894fa65`, keeping `86a7674` as history. Still open: who records the real `pin_manifest_digest` for the release manifest (and it moves again with the `c814c2b` bump).
8. `bridge_services` (infra #26) names its ECS services `pulso-core-runtime`, `pulso-core-exporter`, `pulso-platform-exporter` (log groups `/pulso/<env>/pulso-*`). Will the Core workload slice deploy its own `pulso-core-runtime`, or is ours the single runtime? We must not both declare the same service, log group or Cloud Map name.
9. Secret value shapes we assume: `core/db-exporter`, `core/bridge-service-key`, `core/identity-keys`, `core/staff-keys`, `core/llm-gateway-token` are whole-secret strings; `core/db-app` has JSON keys `registry_dsn` and `eval_dsn`. Is that how you will create them? Also open (infra#26 plan section 9): who opens the Core database security group for our runtime and exporter (ours is opt-in, `manage_core_database_ingress`, default off); whether the additive `read_only_root_filesystem` and `ephemeral_volumes` in the shared `workload` module are acceptable to you (see also `docs/architecture/agent-core-overlap-and-engine-plan.md` section 9 in infra).

## C. LLM gateway and agent-core questions (consumer view)

Gateway:
- **Q1** Per-consumer policy: allowlist of `(endpoint_alias, model)` and caps on `price`, `max_tokens`, `timeout_s` (today any authenticated caller can pick any model and price). Planned, or must cost control stay at the provider keys?
- **Q2** Server-side rate and concurrency limits per consumer and alias (today 120 parallel calls all pass).
- **Q5** Can the response and errors carry a provider request id and the resolved route/provider alias? Our audit receipts cannot fill them today.
- **Q6** Two active tokens per consumer (rotation without downtime) and an authenticated check route (`GET /v1/whoami` or authenticated `/readyz`) instead of our empty-body POST probe.
- **Q7** Any plan for `Idempotency-Key` dedupe? A timed-out call may still bill and we cannot detect it.
- **Q8** When is the first `v0.x` tag and GHCR digest published, and is private GHCR pull from AWS or ECR mirroring planned? Infra deploys digests only. Also: HEALTHCHECK is ignored in OCI builds (declare `["/llm-gateway","-healthcheck"]` in the task definition).
- **Q10** Error `message` strings are Spanish; can a stable `code` field be added?

Agent-core:
- **Q4** PR #28 (JEV through the gateway's `/v1/jev`) says merged, but it was merged into the stacked branch `feat/http-llm-gateway` and is NOT on `main` (see A1). `894fa65` still reads `AGENTCORE_JEV_API_KEY` and calls `api.typesafe.ai`. Please land it on `main`, or tell us it is intentionally held back.
- **Q11** Can `serve` offer a strict mode that fails startup when the gateway env is absent, instead of `UnconfiguredLLMGateway` answering `unavailable` on every call?
- **Q12** `HttpLLMGateway` maps `unauthorized` to `unavailable`; can it expose a distinct reason or counter so readiness can alert on a bad token?
- **Q13** Can `labels` carry `tenant`/`job`/`stage` so gateway and provider logs join our ledger?
- **Q14** `LLMAgentPort` does not propagate `usage_known`; any plan to fix it so budgets treat unknown cost correctly?
- **Q15** Is `HttpLLMGateway` safe for concurrent runs (single `httpx.Client`), and what pool size is expected for parallel stages?

## D. For the Product team (relayed by the user; source `PLATFORM_DATA_MODEL_IMPACT_CLAUDE.md` section 7, spec V3 section 32.6)

Not for the Agent Core team; kept here so one relay file carries every question that only the user can route. Status: the platform source contract, simulator and exporter are implemented and merged (improvement-engine#80) against the data model as published; every payload shape below is a simulator assumption until Product answers.

0. Roadmap for Phase 2 data (routing, tool calls, approvals, identity, suggestions): will it follow the `platform_history` 0.5.1 entities, and in which release does each arrive?
1. How will Pulso read the platform: read-only database access, a replica, an exported snapshot or feed, or an API with `after_sequence` paging?
2. Payload schema per `event_type` (especially `turn.created`, `case.assigned`, `case.status_changed`, `case.closed`): which fields, and does any payload carry message text?
3. Is `event_log.sequence` contiguous even after rolled-back transactions? Can `ingested_at` be trusted as the commit time?
4. Will `origin`, `topic`, `complaint_id` ever exist on real cases? Without `complaint_id`, is there a planned customer id mapping to the bank dataset?
5. Will AI-layer facts (tool calls, identity checks, approvals, close outcome `resolved`, CSAT) be captured by the platform, and when? This decides which detector families can ever run on the real source.
6. Which rows are demo (`customers.simulator`, `suggestions`)? Is there a stable marker to exclude them?
7. Timeline for `teams`, `staff.team_id`, `admin_roster` and the new event types; will event types be versioned?
9. Retention and redaction rules for message text and staff data, and whether the data may reach hosted models or must stay local (E0 rule: local only).
