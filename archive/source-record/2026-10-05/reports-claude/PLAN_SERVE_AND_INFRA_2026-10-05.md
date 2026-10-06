# Plan: agent-core `serve` readiness and a production-like environment (analysis, then plan)

Author: Claude (orchestrator). Date: 2026-10-05. Status: PROPOSAL, no work started. The three exploratory agents I had launched were stopped before doing anything; nothing was changed. Facts below come from the three org-state surveys (`ORG_STATE_PLATFORM`, `ORG_STATE_AI`, `ORG_STATE_ENGINE_INFRA`, 2026-10-05) and earlier reports; items marked [U] are unverified.

## 1. Why this is the critical path

Everything we built assumes one shared Core. The infra design (ADR 0009) makes `agentcore serve` that Core for the platform assistant and copilot, our engine, evals and the registry. Our engine was proven against a LOCAL stack that runs agent-core with test doubles in places. If `serve` differs from that stack, the loop fails exactly where it matters: announce, evaluate, approve, publish. And nothing runs in a production-like place yet (nothing applied, no images pushed, platform on SQLite).

## 2. What we know (analysis)

### 2.1 agent-core `serve`
- Mature repo (about 3,235 tests, many commits per week), registry lifecycle complete (draft, candidate, evaluated, approved, published), `inherit_from`, locked policies, `reason_code`, scenario principals, OTLP and Langfuse attributes, all merged.
- Survey findings: the transfer demo does not work over `serve`; several `serve` pieces are doubles; audit replay of real runs diverges; no fixture agent has an `eval_suite`; GitHub CI is down (billing), so local validation is the only gate.
- From our own work: calibration and classifier in the local stack are doubles (documented in EV1); `serve` needs `AGENTCORE_TOOL_SERVICE_URL`, a DSN, JEV and OpenRouter values; tool definitions drift between fixtures and tool-service; `GET /v1/tools` belongs to tool-service; the engine key in staff-keys can mint human credentials (trust risk, ADR 0009).
- Unknown: exactly which components are real vs double under `serve`, with file:line; whether the platform assistant and copilot actually run end to end on `serve`; concurrency and readiness behaviour; what restart or health semantics `serve` offers.

### 2.2 Shared database
- Platform: SQLite, no migrations (schema change means deleting the DB), event_log append-only. The platform engine export reads `event_log` directly (SQLite or a Postgres read-only role).
- agent-core: Postgres (registry, runs, approvals). Local stack uses a Postgres container.
- Infra design: Postgres as a container on the core host (not RDS) in the free-plan profile [U].
- Open: the user's phrase "real shared database" implies one Postgres for all services. That requires the platform to move from SQLite to Postgres (a code change in support-platform), schemas and roles per service, a migrations strategy, and backups.

### 2.3 Data loading
- data-pipeline (dbt and DuckDB) builds 13 challenge tables (about 4.4M transactions, 15.6M digital events) in restricted, masked, analytics and isolated eval zones. tool-service reads `gold_restricted`.
- The engine consumes only aggregates (bank cells, k at least 10) and an E0 export (frozen). Today these are files on a developer machine, not in any environment.
- Open: bucket layout, who uploads, how DuckDB files or parquet reach tool-service on its host, how the engine receives cells (job input), privacy boundary (raw rows must never leave the restricted zone).

### 2.4 Service-to-service
- Design: 3 EC2 hosts (core with Postgres, platform, engine) behind CloudFront; services agent-core `serve`, llm-gateway, tool-service, platform (backend and SPA), engine, plus the OTLP forwarder [U].
- Known edges: platform to agent-core (assistant, copilot, evaluate), agent-core to gateway to OpenRouter, agent-core to tool-service to data, engine to gateway, agent-core, platform (announce, evidence). Token-based; PR 37 generates tokens and Ed25519 keys in Terraform.
- Known mismatches from the PR 37 review: engine env contract (PULSO_LLM_GATEWAY_KEY, IP-literal gateway address, PULSO_SERVICE_SEED_HEX), Core startup needs tool-service URL and artifact dirs, no merge-only reseed tooling.
- Open: DNS or service discovery, security groups, S3 access (instance profiles), egress to OpenRouter and Langfuse, ARM vs x86 images.

### 2.5 Build, run, health
- Engine image exists (PR 100, 98 MB). Other images [U]: Dockerfiles for agent-core, gateway, tool-service, platform backend and SPA need checking. ECR push and digest pinning are not exercised. Hosted CI is unavailable, so builds must be local.
- Your message mentions "the command in the task": the design uses EC2 hosts (compose or systemd [U]), not ECS tasks; I need to confirm, because it changes how commands and health checks are expressed.
- Health: unknown per service (liveness vs readiness, start period, dependency checks); restart policy and crash-loop causes are unknown.

## 3. Principles for the plan
- No `terraform apply` and no AWS mutation without your explicit order. Until then: design, code, offline validation, local rehearsal of the same topology with Podman.
- Rehearse before deploying: a "prod-like" local stack that uses the SAME images, env contract and health checks that infra will use; only the host differs.
- PRs in other repos are allowed (agent-core, support-platform, tool-service, llm-gateway, infra); you merge.
- Secrets never printed; values only in child process environments; real values are your responsibility (DSN, JEV, OpenRouter, tool-service).
- Memory is tight: audits are read-only; heavy runs one at a time.

## 4. Workstreams and sequence

### WS1. SERVE: measure first, then fix (starts first; blocks the rest)
1. Inventory `serve` (file:line): real vs double for calibration, classifier, JEV and judge, tool-service calls, transcript store, authz, registry store, telemetry, secrets, health endpoints.
2. Live exercise against a local stack with the models in our policy: recepcion, disputas, consultas, copiloto-asesor; the failing transfer flow; freeze, evaluate, approve, publish with an `eval_suite`; GET /v1/tools; run export; lineage. Table: works, fails, root cause.
3. Fix the small items as ready PRs in agent-core (RED test first); write asks for large ones (`ASK_agent-core_serve.md`).
4. Define the `serve` env contract and readiness contract that infra and the engine depend on.
DoD: `SERVE_READINESS` report with a capability table (real, double, broken) and reproduction commands; engine and platform smoke flows pass on `serve`; every remaining double is listed with owner and effort.
Effort: 1 to 2 days of agent time; the fix list may extend it.

### WS2. DATABASE
1. Decide the topology (see decision D1).
2. If platform moves to Postgres: PR in support-platform (SQLAlchemy dialect, schema bootstrap, a minimal migrations tool, read-only role for the exporter, tests on both SQLite and Postgres).
3. One Postgres, separate databases or schemas and roles per service; connection strings injected from Secrets Manager or SSM; backups and restore drill documented.
DoD: platform and agent-core run against one local Postgres container with per-service roles; restore drill documented.

### WS3. DATA AND S3
1. Bucket layout and zones (raw restricted, gold, masked, analytics, engine inputs, artifacts) with IAM per service and no cross-zone leakage; encryption and lifecycle.
2. Loader: reproducible command that builds the gold tables (data-pipeline) and publishes to the bucket; tool-service fetch strategy (download DuckDB or parquet at start, or mount); engine input publisher (bank cells) and E0 export placement.
3. Privacy checks as tests (no row-level data outside restricted zone).
DoD: from an empty bucket to tool-service answering a real query and the engine reading cells, rehearsed locally with MinIO or the local filesystem equivalent, and a runbook for the real bucket.

### WS4. CONNECTIVITY
1. Topology table and diagram: caller, callee, protocol, port, auth, where the secret comes from.
2. Security groups, service discovery or fixed private DNS, CloudFront origins and paths, egress rules, OTLP forwarder egress to Langfuse.
3. Fix the PR 37 review mismatches (engine env contract, gateway address, seed keys, tool-service URL, artifact dirs) in infra.
DoD: the local prod-like rehearsal talks only through the documented edges; Terraform plan (offline) matches the table.

### WS5. IMAGES, RUN COMMANDS, HEALTH
1. Per service: Dockerfile, architecture (EC2 type), size, build command, tag and digest pinning, run command and env contract (names only), ports, volumes, resource limits.
2. Readiness vs liveness endpoints, start period, retries, restart policy, startup ordering (DB, migrations, seed keys), what crash-loops.
3. Local build and push runbook (no CI): build, scan, push to ECR, pin digests, rollout and rollback.
DoD: every service builds from a clean checkout with one command, starts with only the documented env, passes its health check, and recovers when its dependency restarts (chaos test in the rehearsal).

### WS6. PROD-LIKE REHEARSAL (integrates 1 to 5; overlaps ENV1)
Local Podman topology using the infra env contract: Postgres, agent-core `serve`, gateway, tool-service, platform backend and SPA, engine, forwarder. Run the full loop and the demo script on it.
DoD: one command up, one command smoke test (detect, propose, prove, announce, approve, publish, release, outcome), green; health and restart behaviour demonstrated.

### WS7. DEPLOY READINESS (needs your orders)
Offline `terraform plan` review, state key migration plan, secrets checklist, apply order, cost check for the chosen profile, rollback. Nothing is applied until you say so.

## 5. Order and parallelism
Wave A (now, read-mostly, low RAM): WS1 inventory, WS4 and WS5 audits (three read-only agents), WS2 and WS3 design docs.
Wave B: WS1 live exercise and fixes (one heavy), WS5 image builds one at a time, WS2 platform Postgres PR.
Wave C: WS6 rehearsal, WS3 loader, WS4 infra fixes.
Wave D: WS7 with your authorization.
Running lanes that continue unchanged: ENV1 (integrated rig, becomes the seed of WS6), ART2, SIG1.

## 6. Decisions I need from you
- D1. One Postgres for platform, agent-core and tool-service (my recommendation: yes, on the core host for this single environment, separate databases and roles), which means moving the platform off SQLite. OK?
- D2. Compute model: confirm EC2 hosts with compose or systemd (as designed) rather than ECS tasks. If you meant ECS, say so, it changes WS5.
- D3. Data in S3: confirm the raw restricted tables may be uploaded to your account bucket (restricted zone, encrypted), or should only the gold and masked zones go.
- D4. Accept the trust risk of the engine key in staff-keys for the hackathon, or prefer a dedicated principal (agent-core PR).
- D5. Target of the rehearsal: local Podman only, or also a throwaway AWS apply later (only on your explicit order).

## 7. Risks
`serve` doubles may be deeper than a few PRs; platform to Postgres is a real change without migrations; agent-core owners must merge our PRs; free-plan limits (memory of the core host with Postgres, agent-core, gateway and tool-service on one instance [U]); no hosted CI, so regressions are caught only by our local gates.
