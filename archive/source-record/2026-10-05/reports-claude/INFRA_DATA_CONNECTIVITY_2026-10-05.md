# INFRA-A: database, data loading, connectivity and Terraform gaps (2026-10-05)

Lane INFRA-A. Read-only on AWS: no apply, no credentials, no Nexus. Sources: infra `origin/main` 7251d8f (PR 37 merged; the PR 37 review is partly STALE, see section 0), improvement-engine `origin/main`, support-platform announce worktree, ADRs 0006-0009, the two briefs. Marks: [V] read in code, [U] unverified. Branch `claude/infra-data-connectivity` (worktree `D:\.codex\factored\worktrees\infra-claude-data`).

## 0. What PR 37 already fixed (do not redo)

Engine env: `PULSO__PULSO_LLM_GATEWAY_KEY`, `PULSO__PULSO_SERVICE_SEED_HEX` (64 hex, derived in HCL) and SSM `PULSO_SERVICE_KID`, `PULSO_CORE_ADDR=<core IP>:8001`, `PULSO_LLM_GATEWAY_ADDR=<core IP>:8080` (IP literals). Core: `AGENTCORE_TOOL_SERVICE_URL`, calibration/classifier dirs, S3 sync of artifacts and of the tool-service publication, merge-only reseed (`aws-prod.ps1 seed-secret-keys`). The BEL docs defect is gone. Remaining review items are in the gap list.

## 1. Database design (one Postgres 16 container on the core host)

Full design, SQL and runbook: `docs/shared-postgres.md` in the PR.

| Database | Owner | App role | Read-only | Used by |
|---|---|---|---|---|
| core_runtime, core_eval | core_owner | core_app, core_eval_app | core_exporter_ro | core-runtime (engine core-bridge, legacy) |
| agent_runtime, agent_eval | agent_owner | agent_app | - | agent-core serve (already in main) |
| platform (NEW) | platform_owner | platform_app | platform_exporter_ro (SELECT only on event_log, cases) | support-platform; engine platform-exporter |
| tools (NEW) | tools_owner | tools_app | - | tool-service (SQLite today; roles ready) |
| pulso | pulso_master | pulso_app, pulso_loader | pulso_*_ro | engine |

- Grants: CONNECT revoked from PUBLIC, one role set per database, owners used only by migrate steps, app roles DML via default privileges, exporter has NO default privileges and an explicit table allow-list (run after each platform migration), `default_transaction_read_only=on`.
- Secret injection: passwords `DB__DB_PASSWORD_<ROLE>` in the one Secrets Manager secret, rendered to `db.env` (tmpfs); DSNs `SUPPORT__CC_DATABASE_URL`, `SUPPORT__CC_MIGRATE_DATABASE_URL` (name assumed, align with platform `deploy-env.md`), `PULSO__PULSO_PG_PRODUCT_DSN` set out of band; init refuses `CHANGE_ME`.
- Backup/restore: daily EBS snapshots (DLM) plus per-database `pg_dump -Fc` to `/srv/data/backups` and `s3://<bucket>/core/backups/`; restore drill into a scratch container. Dump automation is open (P1).
- Memory (m7i-flex.large, 8 GiB): postgres limit 2048 MiB (shared_buffers 512 MB, effective_cache_size 1536 MB, work_mem 8 MB, max_connections 100 up from 40), agent-core 768, core-runtime 768, tool-service 1024, gateway 128, exporter 128, one-shot migrations 256 each: about 4.9 GiB of limits, about 3 GiB headroom. Pool budget about 65 of 100 connections. Platform/engine hosts are t3.small (2 GiB): platform 640 MiB, engine 576 MiB of limits.

## 2. Data loading design

Bucket `pulso-prod-data-<account>` (single bucket, SSE-KMS CMK with bucket key, TLS-only, versioned, public access blocked, deny-only bucket policy). Keep it single: the 5-zone `data_lake` module is a separate production path; here the zones are prefixes with identity policies plus Deny statements.

| Prefix | Zone | Content | Writer | Readers |
|---|---|---|---|---|
| `landing/<dataset>/` | restricted (PII) | raw 13 tables, E0 raw. NOT needed in AWS if the pipeline runs on the operator machine (recommended: do not upload) | operator (PUT only) | loader, break-glass, through the S3 VPC endpoint |
| `lake/bronze/`, `lake/gold_restricted/` | restricted | only if the pipeline runs in AWS | loader | loader, break-glass |
| `lake/publish/<run>/gold_restricted.duckdb`, `field_classification.json` | restricted (PII in clear, classified) | data-pipeline publication | operator | core host role (tool-service) only, plus loader/break-glass |
| `lake/publish/<run>/gold_masked.duckdb`, `gold_analytics.duckdb`, `parquet/` | masked/analytics | publication | operator | per IAM |
| `lake/publish/latest.json` | pointer | uploaded LAST | operator | core host |
| `lake/gold_analytics/bank_cells/` | analytics (aggregates, k>=10) | `cells.ndjson` + `MANIFEST.json` (sha256, k_min, rows, metrics) | operator | engine host |
| `engine/inputs/e0/<version>/` | masked | E0 frozen export | operator | engine host only |
| `core/artifacts/{calibrations,classifiers,registry-seed}/`, `core/blobs/`, `core/backups/` | internal | data team / agent-core / dumps | operator, core host | core host |

IAM per instance profile [V hackathon_iam]: core reads `lake/publish/*` and `core/artifacts/*` and read/writes `core/*`; engine reads `lake/gold_masked`, `lake/gold_analytics`, read/writes `engine/*`; platform has no data prefixes. Bucket Deny keeps `gold_restricted` readable only by loader, break-glass and the core role, so even a widened identity policy cannot expose it.

Who uploads, reproducible commands (operator machine, profile `pulso-prod`, KMS key from `terraform output kms_key_arn`):
1. Build locally: data-pipeline dbt/DuckDB produces `publish/<run>/`.
2. `aws s3 sync <run dir> s3://<bucket>/lake/publish/<run>/ --sse aws:kms --sse-kms-key-id <arn> --exclude latest.json`
3. `aws s3 cp latest.json s3://<bucket>/lake/publish/latest.json --sse aws:kms --sse-kms-key-id <arn>` (last, atomic switch).
4. Cells: `bank_cells.py` on the raw data -> `cells.ndjson`; `aws s3 cp` to `lake/gold_analytics/bank_cells/` with MANIFEST. E0: `aws s3 sync` to `engine/inputs/e0/<version>/`.
5. Core host: `sudo systemctl restart pulso-stack` picks the publication up.
A wrapper `aws-prod.ps1 publish` (with checksum manifest and the pointer-last rule) is P1; today `upload` only writes `landing/`.

How tool-service reads: download-at-start (existing start script copies only `gold_restricted.duckdb` and `field_classification.json` to `/srv/data/tools/data/publish/<run>/`, pointer last, read-only mount, DuckDB file opened read-only). No mount of S3 (latency, no FUSE). No publication: tool-service answers `data_unavailable`, the rest starts.

How the engine receives cells and E0: files on the engine host, `PULSO_CELLS_NDJSON` and `PULSO_E0_SAMPLE_ROOT` (engine reads these as paths). GAP: the engine start script does not sync `engine/inputs/` yet (P1; since nothing is applied, changing user_data costs nothing now; after apply it replaces the host). The engine reads the platform through the read-only role, never the platform API for raw rows.

Privacy rules: raw rows and the restricted zone never leave the operator machine and the core host; engine reads aggregates only (k>=10, no ids, no free text) plus E0 (masked/synthetic enrichment); `platform_exporter_ro` limited to `event_log`, `cases`; Langfuse receives engine/gateway/agent-core spans with masking in the forwarder (no raw bank/E0 rows); privacy checks as tests: cells file validator (k>=10, forbidden columns) in the publish wrapper, plus the Deny-statement tests already in `hackathon_data`.
Finding: `engine_host_can_load` defaults to TRUE, so the engine role can read `landing/`, `lake/bronze/` and the restricted gold. That contradicts "engine reads aggregates only". The PR sets `engine_host_can_load = false` in `prod.tfvars.example` (default left, human decision D1).

## 3. Connectivity

Hosts: core (postgres, agent-core serve, core-runtime, core-exporter, llm-gateway, tool-service), platform (support API :8000, web, Caddy :80), engine (pulso :8080 behind Caddy). Private zone `pulso.internal` (`core.`, `platform.`, `engine.`). Engine clients accept only IP literals for plain HTTP, so the engine uses SSM-held private IPs; others may use DNS.

| Caller | Callee | Protocol / port | Auth | Secret from |
|---|---|---|---|---|
| CloudFront | platform Caddy | HTTP 80 | `X-Origin-Verify` header | `COMMON__ORIGIN_VERIFY` |
| CloudFront (`/pulso/*`) | engine Caddy | HTTP 8080 | same header | same |
| platform API | Postgres `platform` | PG 5432 | password (platform_app) | `SUPPORT__CC_DATABASE_URL` |
| platform API | agent-core serve | HTTP 8001 | Ed25519 principal/delegation credentials | `FILES__SUPPORT__AGENT_PRIVATE_KEYS` |
| agent-core | platform API (grant_active) | HTTP 8000 | bearer | `AGENT__AGENTCORE_GRANTS_TOKEN` = `SUPPORT__CC_INTERNAL_SERVICE_TOKEN` |
| agent-core | llm-gateway | HTTP 8080 (compose net) | bearer | `AGENT__AGENTCORE_LLM_GATEWAY_TOKEN` |
| agent-core | tool-service | HTTP 8080 (compose net) | bearer | `AGENT__AGENTCORE_TOOL_SERVICE_TOKEN` / `TOOLS__TOOL_SERVICE_TOKENS` |
| agent-core | Postgres agent_* | PG (compose net) | agent_app | `AGENT__AGENTCORE_REGISTRY_DSN` |
| agent-core | JEV | HTTPS 443 out | api key | `AGENT__AGENTCORE_JEV_API_KEY` |
| llm-gateway | OpenRouter | HTTPS 443 out | api key | `GATEWAY__OPENROUTER_API_KEY` |
| engine | llm-gateway (core:8080) | HTTP 8080 | bearer | `PULSO__PULSO_LLM_GATEWAY_KEY` |
| engine | agent-core serve (core:8001) | HTTP 8001 | Ed25519 credential signed with engine seed (`builder`) | `PULSO__PULSO_SERVICE_SEED_HEX`, SSM `PULSO_SERVICE_KID` |
| engine | platform API (:8000) | HTTP | bearer | `PULSO__PULSO_PLATFORM_SERVICE_TOKEN` (NEW) |
| engine | Postgres `platform` (read-only) | PG 5432 | platform_exporter_ro | `PULSO__PULSO_PG_PRODUCT_DSN` (NEW) |
| engine | Postgres `pulso` | PG 5432 | pulso_app | `PULSO__PULSO_DATABASE_URL` |
| tool-service | local DuckDB, SQLite | file | - | synced from S3 |
| hosts | S3, ECR, SSM, Secrets Manager | HTTPS | instance profile (IMDSv2) | - |
| forwarder | Langfuse US | HTTPS 443 out | basic pk:sk | not deployed yet (gap) |

```
 viewers --> CloudFront ----------------------------+--------------------------------+
   default (/, /api/*, /api/v1/ws WS)               | /pulso/*                       |
                                                    v                                v
   +-------- platform host (t3.small) --+    +----- engine host (t3.small) ---+
   | Caddy:80 -> web, API:8000          |    | Caddy:8080 -> pulso:8080       |
   +--^--------^------------------------+    +--+------+------+------+--------+
      |8000    |8001 (api->agent)                 |8001  |8080  |5432  |8000 (announce)
      |grants  v                                  v      v      v      v
   +--+--- core host (m7i-flex.large) -------------------------------------+
   | agent-core:8001 --> gateway:8080 --> OpenRouter (443)                 |
   |        |--> tool-service:8080 --> gold_restricted.duckdb (local)      |
   | postgres:5432 (agent_*, platform, tools, pulso, core_*)               |
   | core-runtime:8000 (legacy), exporter                                  |
   +--- S3 (VPC gateway endpoint) / ECR / SSM / Secrets Manager -----------+
```

Security groups [V]: platform 80/8080 from the CloudFront prefix list only; core 8000 from engine+platform, 8001 from engine+platform, 8080 from engine, 5432 from platform+engine; platform 8000 from core (+ engine, NEW); egress by sibling SG plus 443 anywhere and DNS to the VPC resolver. No NAT in free_plan: hosts hold public IPs, inbound only via SG.
Discovery: Route 53 private zone records per host; engine uses IP literals from SSM (rewritten on apply if an instance is replaced).
CloudFront: two origins; default behaviour (platform) carries `/api/*` and the WebSocket `/api/v1/ws` (CachingDisabled + AllViewer policy forwards Upgrade); `/pulso/*` to engine. [U] WebSocket idle: CloudFront closes idle origin connections at the origin read timeout, so the platform needs a ping under 30 s (ask to platform team; brief P2 covers reconnect). `/api/v1/internal/*` is blocked at Caddy; internal calls use the VPC port 8000, never the edge.
Egress: OpenRouter, JEV, Langfuse: 443 to anywhere (no allow-list without NAT). OTLP forwarder: not deployed. Recommended: a sidecar on the core host (gateway and agent-core export OTLP over the compose network; engine reaches it via a new SG edge core:4318 from engine), holding the Langfuse keys in the secret `FORWARDER__*`; needs the forwarder bind address configurable (engine script listens on loopback only) and an image.

## 4. Gap list (Terraform vs needs)

| # | P | Gap | Effort | Status |
|---|---|---|---|---|
| 1 | P0 | IMDSv2 hop limit 1: containers cannot use the instance profile, so agent-core blob store, engine job store (S3) and any sidecar fail | 0.1 d | FIXED in PR (in-place) |
| 2 | P0 | llm-gateway not published on the core host, yet the engine targets core:8080 and the SG opens it | 0.1 d | FIXED in PR |
| 3 | P0 | No `platform` / `tools` databases and roles, no read-only exporter role; platform on SQLite | 0.5 d infra (+ platform PR) | FIXED infra side in PR |
| 4 | P0 | Engine cannot reach the platform (no SG edge, no URL/token/DSN env) for announce + evidence | 0.3 d | FIXED in PR (flag `platform_database_enabled`) |
| 5 | P0 | `engine_host_can_load=true` gives the engine PII/restricted read | decision | tfvars example set false; default needs OK (D1) |
| 6 | P0 | Engine code: serve credentials. Live port still uses core-bridge env (`PULSO_BRIDGE_ADDR`, human seed, E2E fixtures); the value loop wants `PULSO_REGISTRY_TOKEN`, a builder credential that serve expires in minutes. The engine must mint Ed25519 credentials from `PULSO_SERVICE_SEED_HEX`+kid | 1-2 d (engine, ours) | OPEN, engine lane |
| 7 | P0 | Postgres init on an existing volume is manual; platform migrations need the owner DSN. Depends on platform brief P1/P2 | platform team | OPEN |
| 8 | P1 | Engine start script has no sync of `engine/inputs` (cells, E0) | 0.3 d | OPEN |
| 9 | P1 | OTLP forwarder sidecar + Langfuse secret + SG edge | 1 d (+ forwarder image) | OPEN |
| 10 | P1 | Backup automation (pg_dump sidecar to S3) and restore drill evidence | 0.5 d | doc only |
| 11 | P1 | `aws-prod.ps1 publish` (pointer-last, manifest, cells validator) | 0.5 d | OPEN |
| 12 | P1 | Platform and engine bearer shared (`CC_INTERNAL_SERVICE_TOKEN`); per-consumer tokens | platform | ask |
| 13 | P1 | Trust: engine key in staff-keys can mint approver credentials, and all hosts read the whole secret (accepted by you; split secret per host would reduce it) | 1 d | accepted |
| 14 | P1 | Migrate role vs runtime role in the same DSN for core-runtime (review leftover) | 0.2 d | OPEN |
| 15 | P2 | Tool-service DSN support (uses the `tools` DB), ARM vs x86 images, hosted CI, `*.tftest.hcl` in the workflow | various | OPEN |
| 16 | P2 | RDS/TLS inside VPC for Postgres (no TLS now) | 0.5 d | accepted |

## 5. PR

See the PR URL in the hand-off. Content: items 1-4 and 5 (example), `docs/shared-postgres.md`, contract tests (`tests/test_shared_postgres_contract.py`), tftests in network, compute, data and env, journal 0022. All offline (mock providers).

## 6. Data-pipeline ask (doc only)

Ask to data-pipeline: (a) a `publish` command that writes `publish/<run>/` plus `MANIFEST.json` (sha256 per file) and `latest.json` last; (b) a cells exporter wrapper around `bank_cells.py` that fails on k<10 or id-like columns; (c) confirm that `parquet/` under a run contains only analytics-zone data (our Deny covers only `gold_restricted.duckdb`).

## 7. Human decisions

D1 flip the default `engine_host_can_load` to false (needs your OK; example already false). D2 do not upload raw `landing/` at all (recommended) versus upload encrypted. D3 same bearer for engine and agent-core on the platform (accept for now). D4 enable `platform_database_enabled` only after the platform Postgres PR is merged. D5 order for any apply.
