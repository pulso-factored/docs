# INFRA-B: how the EC2 hosts run everything, health, and the prod-like rehearsal (2026-10-05)

Lane INFRA-B. Decisions applied: compute = EC2 hosts with compose/systemd as designed; one shared Postgres; rehearsal local with
Podman; no AWS mutation. Nothing was applied, no credentials used, no secret printed, `D:\Nexus` untouched.

Method: read the plan, the three ORG_STATE reports, the two briefs, infra `origin/main` `7251d8f` (compose bundles, Terraform
compute/data modules, scripts, ADR 0009), and for each owned service its `origin/main` Dockerfile, health code and env readers
(engine `879cd4a5`, llm-gateway `03d1a31`, tool-service `64c36bc`, agent-core `2ad5d08` for the probe facts only). Marks: [V] read in
code, [T] covered by a test I ran offline, [U] not verified, [N] not exercised.

## 1. Deliverables

| # | Item | Where |
|---|---|---|
| 1 | this report | `D:\.codex\factored\docs\reports-claude\INFRA_RUN_HEALTH_2026-10-05.md` |
| 2 | fixes + offline tests (ready PR) | PR URL in section 7; branch `claude/infra-run-health`, worktree `D:\.codex\factored\worktrees\infra-claude-run` |
| 3 | build and release runbook | `docs/runbooks/build-and-release.md` (infra repo) |
| 4 | rehearsal design + implementation | `docs/prodlike-rehearsal.md`, `scripts/prodlike/` (infra repo) |
| - | durable run/health contract | `docs/run-and-health.md` (infra repo) |

No PR was needed in llm-gateway or tool-service: both already have a Dockerfile and `/healthz` (`/readyz` in tool-service) [V].

## 2. Run and health facts per service

Common [V]: all hosts x86_64 (AMI parameter `...al2023-ami-kernel-default-x86_64`, compose plugin `docker-compose-linux-x86_64`, types
t3/m7i-flex), so images are `linux/amd64` only; arm types are accepted by a variable validation but would break user_data (P2). Images are
digest variables `<KEY>_IMAGE` rendered from SSM `/pulso/<workload>/images/<key>`. Logs: json-file 10 MB x 3 + optional CloudWatch agent.
Restart `unless-stopped`; Docker does NOT restart an unhealthy container, only deploy-stack.sh reacts to health (during a deploy).

| | engine `pulso` | llm-gateway | tool-service | OTLP forwarder |
|---|---|---|---|---|
| Dockerfile | yes, engine repo root [V] | yes, repo root [V] | yes, repo root [V] | **none** in engine repo; I added `docker/otlp-forwarder.Dockerfile` (infra) |
| Base / arch | node:22.16-alpine, rust:1-bookworm (floating), debian:bookworm-slim (floating); amd64 | golang:1.27, distroless static nonroot (floating); amd64 | python:3.12-slim, `uv:latest` (floating); root user, no HEALTHCHECK; amd64 | python:3.12-slim-bookworm; stdlib only; amd64 |
| Size | 98.1 MB (measured earlier by the engine lane, Podman) | 17 MB, amd64, built with Podman docker format [V live] | 250 MB, amd64 [V live] | not built [N] |
| Digest pinning | tag-pinned bases; pinned at release time by registry digest | same | same, plus unpinned uv | same |
| Entrypoint / command | `pulso` / `run` | `/llm-gateway` | `tool-service` (uvicorn) | `python .../otlp_forwarder.py --port 4318` |
| Env NAMES (value source) | secrets (generated): `PULSO_ADMIN_TOKEN`, `PULSO_DEBUG_TOKEN` (**was missing**), `PULSO_LLM_GATEWAY_KEY`, `PULSO_SERVICE_SEED_HEX`; secret out of band: `PULSO_DATABASE_URL`; SSM: `PULSO_DATA_MODE` (placeholder), `PULSO_SERVICE_KID`, `PULSO_LLM_GATEWAY`, `PULSO_BASE_PATH` (**was missing**), `PULSO_CORE_ADDR`, `PULSO_LLM_GATEWAY_ADDR`, `PIPELINE_ROOT`; compose: `PULSO_STORAGE_BUCKET/PREFIX`, `PULSO_CORE_URL` | SSM: `GATEWAY_CONSUMERS`, `LLM_ENDPOINTS`; generated: `GATEWAY_TOKEN_{AGENT_CORE,AGENT_SERVE,ENGINE,SUPPORT_PLATFORM}`; out of band: `OPENROUTER_API_KEY` (+3 other providers), `JEV_API_KEY`; optional `LISTEN_ADDR`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `LLM_GATEWAY_TRACE_CONTENT` | generated: `TOOL_SERVICE_TOKENS`; compose: `TOOL_DATA_DIR`, `TOOL_FILED_DB`, `HOST`, `PORT`; optional `TOOL_POINTER_TTL_S` | out of band: `LANGFUSE_BASE_URL`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`; baked `PULSO_O11Y_ALLOW_EXTERNAL=1` |
| Port | 8080 (behind Caddy; CloudFront -> proxy) | 8080, now published to the engine host (SG) | 8080 internal | 4318 on 127.0.0.1 only, sidecar netns |
| Volumes | `/srv/data/pulso` -> `/var/lib/pulso` | none | `/srv/data/tools/data` ro (S3 publication), `/srv/data/tools/state` | none |
| Liveness | `/healthz` | `/healthz` | `/healthz` | `/healthz` |
| Readiness | `/readyz`: migrations applied + DB answers + tasks alive (compose uses it as the container health) | none exists | `/readyz` (dataset + store); not used as container health on purpose | none |
| Compose probe | `pulso healthcheck`, 15s/5s/5 retries/60s start | `/llm-gateway -healthcheck`, 15s/5s/5/10s (**was disabled**) | python urllib `/healthz`, 15s/5s/5/20s | `/healthz`, 15s/5s/5/10s (fragment) |
| Checks dependencies | yes (DB) | no | readyz only | no |
| Crash-loop causes | exit 2 config: missing/short/equal debug+admin tokens, `PULSO_DATA_MODE` = CHANGE_ME; exit 1 task died; root-owned `/srv/data/pulso` (**fixed**) | exit 2 on bad `GATEWAY_CONSUMERS`/`LLM_ENDPOINTS` or an empty consumer token | exit with named reason on missing tokens/data dir | exit 1 without the three Langfuse variables |
| Order | none across hosts; retries migrations every 2 s; first boot needs the manual DB steps (`30_pulso_logins.sql`) or `/readyz` stays 503 | none; consumers wait `service_healthy` (**was service_started**) | none; agent-core waits `service_healthy` | after its producer is healthy |
| Limits vs instance | 512 MB / 2 GiB | 128 MB / 8 GiB | 1024 MB / 8 GiB (DuckDB: set memory limit) | 96 MB each |
| agent-core serve | placeholder: BRIEF_agent-core_serve; encoded today as `serve ... --registry-api` :8001, `/readyz`, one-shot `agent-core-migrate`, 768 MB. Image HEALTHCHECK probes 8000 (compose overrides to 8001). |
| platform backend / SPA | placeholder: BRIEF_platform_prod_ready; encoded as api :8000 probe `GET /` (weak), web :80, proxy :80; `/srv/data/support` is NOT chowned by prepare (uid unknown) |

Core host budget [V]: 4352 MB of limits + 512 MB one-shot on 8192 MB (53 percent; Terraform test caps 70 percent). Engine 576/2048,
platform 640/2048. `t3` is burstable (credit surcharge).

## 3. Mismatches: infra encoding vs what the images do (ranked)

Line numbers are on `origin/main` 7251d8f before the PR.

### P0 (stack cannot work as designed) - all three fixed in the PR

| # | Mismatch | Evidence | Effect |
|---|---|---|---|
| P0-1 | llm-gateway not published, while the engine calls `<core IP>:8080` and the SG opens 8080 from the engine | `deploy/hackathon/core/compose.yaml:75-84` has no `ports`; `terraform/envs/hackathon/main.tf:296-297`; `hackathon_network/main.tf:311-322`; `hackathon_compute.tftest.hcl:73-75` asserted "never published"; ADR 0009 line 32 wrongly said "already published" | every engine model call fails; loop dead |
| P0-2 | engine cannot start: `PULSO_DEBUG_TOKEN` exists nowhere; `PULSO_ADMIN_TOKEN` is a `CHANGE_ME` placeholder (<24 chars) | `hackathon_data/secrets.tf:44`, `generated.tf` | `pulso run` exits 2 (non-loopback bind demands two different tokens, ENGINE_IMAGE.md); restart loop; deploy rolls back |
| P0-3 | `/srv/data/pulso` is created root-owned, mounted over the image's uid-10001 work/store dirs | `prepare.sh.tftpl:28-29` chowns only exporter | engine cannot write its work/store: crash |

### P1 (works only with manual luck, or fails on reboot/first boot)

| # | Mismatch | Evidence | Status |
|---|---|---|---|
| P1-1 | gateway health check disabled with a wrong reason ("no tool in the image"): the binary has `-healthcheck`; consumers only `service_started` | `core/compose.yaml:81-82`, `:43-44`; `compose.agents.yaml:65-71` | fixed (probe + `service_healthy` for core-runtime and agent-core, agent-core also for tool-service) |
| P1-2 | engine console/API behind CloudFront: Caddy strips `/pulso` while the engine, with `PULSO_BASE_PATH`, serves only under the prefix and tells the console `apiBase`; the variable was not set | `engine/Caddyfile:20`, `config.rs:211`, `run/http.rs:47` | fixed (keep prefix, SSM `PULSO_BASE_PATH=/pulso`) |
| P1-3 | reboot: `/run/pulso` is tmpfs; docker restarts old containers before `pulso-stack-prepare`, bind sources vanish or point to deleted inodes | `user_data.sh.tftpl:163-164` | fixed (`--force-recreate` in the boot unit) |
| P1-4 | boot unit has no retry: one transient S3/SSM/ECR error leaves the host up with nothing running | `user_data.sh.tftpl:153-171` | fixed (`Restart=on-failure`, 30 s) |
| P1-5 | local Podman release builds drop HEALTHCHECK (OCI format) and are not forced to amd64 | `release-engine.ps1:74` | fixed |
| P1-6 | engine first boot: `pulso_app` has no LOGIN until `30_pulso_logins.sql`, which needs the engine migrations first; `PULSO_DATA_MODE` is `CHANGE_ME` | `10_init.sh`, `30_pulso_logins.sql:1-3`, `ssm.tf:15` | NOT fixed: human steps (decision D3) |
| P1-7 | Docker does not restart unhealthy containers; a hung `pulso`/`agent-core` stays until the next deploy | all compose files, `pulso/README.md` last bullet | NOT fixed: decision D2 |
| P1-8 | engine env vs code: `PULSO_MODEL_PORT` (default scripted) and `PULSO_CORE_PORT=live` (bridge-based, not `serve`) are not set; `PULSO_LLM_GATEWAY=enabled` alone does not make the roles use the gateway | `config.rs:235`, INFRA_PR37_REVIEW | NOT fixed: engine-side work |
| P1-9 | the engine image runs `pulso run` only; the value loop (`steps_cli`, Python scorers, demo-loop scripts) is not in it | `Dockerfile`, `scripts/demo-loop/run.ps1` | NOT fixed: decision D4 |
| P1-10 | OTLP forwarder: no image recipe, no wiring; binds loopback only | `otlp_forwarder.py:200` | recipe + sidecar fragment added, NOT wired (decision D1) |
| P1-11 | platform `/srv/data/support` not chowned; platform probe is `GET /` | `prepare.sh.tftpl:28`, `platform/compose.yaml:24` | pending the platform brief |

### P2

* `user_data.sh.tftpl:117` downloads the compose plugin from GitHub without a checksum; `compose.postgres.yaml:8` pulls `postgres:16.4` by tag from Docker Hub (unpinned, anonymous rate limit).
* Floating bases: `rust:1-bookworm`, `debian:bookworm-slim`, distroless `nonroot`, tool-service `uv:latest` and no `USER`/`HEALTHCHECK` (compose compensates).
* `variables.tf:42` accepts t4g (arm64) while the AMI and compose download are x86_64.
* `.env.example` lacked `AGENT_IMAGE`, `TOOLS_IMAGE` and named the core image `agent-core` (fixed in the PR).
* `core-exporter` has no probe (no listener; justified in the file).
* agent-core image HEALTHCHECK targets 8000 while serve runs on 8001 (compose overrides).
* `restart` + `mem_limit` are enforced by tests; `t3` CPU credit surcharge is not budgeted.

## 4. What the PR changes (all offline-tested)

`deploy/hackathon`: gateway `ports 8080:8080` + `-healthcheck` + comments; `service_healthy` edges; Caddy keeps `/pulso`; `.env.example`
image names; new opt-in `core/compose.observability.yaml` (two forwarder sidecars, not wired). `terraform`: `allowed_ports` core gains
8080; `prepare.sh.tftpl` chown; `user_data.sh.tftpl` `--force-recreate` + `Restart=on-failure`; `generated.tf` two 48-char random
tokens; `secrets.tf`, `ssm.tf` (`PULSO_BASE_PATH`); tftest expectations updated. `scripts/release-engine.ps1`: `--platform linux/amd64`,
`--format docker` for Podman. `docker/otlp-forwarder.Dockerfile`. Docs: ADR 0009, architecture, hackathon-deploy, service-deployment,
secrets-keys corrected where they said the gateway was published/unprobed. New: run-and-health, build-and-release, prodlike-rehearsal.

Apply impact: `user_data` changes mean `user_data_replace_on_change` would REPLACE the three hosts on the next apply (data volumes
persist). Harmless while nothing is applied; if an apply happens first, expect instance replacement. The existing secret version ignores
changes: the two new tokens reach an existing secret only through `aws-prod.ps1 seed-secret-keys` (merge-only).

## 5. Rehearsal (`scripts/prodlike/`)

One command up (`prodlike.py up`), one smoke (`smoke`), chaos (`postgres`, `gateway`), RAM-guarded one-at-a-time `build`. It renders the
real bundles; the unit tests assert health checks, restart, limits, user, command, `depends_on` conditions and env file names are identical
to the hosts, and that the env contract keys all exist in Terraform. Slots (dropped, reported): agent-core serve, platform backend/SPA, core
runtime; the eight loop steps (detect ... outcome) are listed as `slot` because every one needs agent-core serve or the platform (and detect
needs a loop runner against the stack). Implemented smoke: gateway liveness/auth/(paid call with `--live`), Postgres init, tool-service
catalogue, engine edge. Deviations are printed by `render` and listed in `docs/prodlike-rehearsal.md`.

## 6. Test evidence

* Python contract suite: 220 tests before, 259 after, all green (`python -m unittest discover -s tests`), includes docs consistency.
* New: `tests/test_run_health_contract.py` (16 tests, RED first: 11 failed), `tests/test_prodlike.py` (23).
* Terraform (offline, mock providers): `hackathon_compute` 33/33, `hackathon_data` 29/29, `envs/hackathon` 25/25 after the first set of changes;
  final re-run after all changes: 33/33, 29/29, 25/25, `terraform fmt -check -recursive` clean.
* Live on Podman (machine `pulso-dev`, prefix `infb`): `prodlike.py build gateway` and `build tools` OK; compose accepted the rendered files and
  created networks, volumes and containers. `up` itself is BLOCKED BY THE MACHINE: crun cannot set `memory.max`, then `controller pids is not
  available` even with `pids_limit: 0` (docker-compose cannot send the `--pids-limit=0` that `podman run` accepts). The rehearsal now falls back
  by itself for memory and reports it; pids needs a machine config change I did not make (it is shared with other lanes).
* By hand with the rendered env files and `podman run --pids-limit=0`: gateway image probe exits 0, `/healthz` 200, no-bearer generate 401;
  tool-service as uid 10001: `/healthz` 200, 7 tools, `/readyz` 503 without a publication; with a root-owned `/state` it crashes
  (`unable to open database file`), the same class as P0-3. That finding made `up` chown the volumes that prepare.sh gives to uid 10001.
* NOT exercised [N]: the engine image (RAM 0.8 to 1.1 GB free with another lane's Postgres and gateway running; needs about 3 GB), Postgres init
  through the rendered initdb, the proxy, `smoke`, `chaos`, the forwarder image, any AWS call, `pulso run` with the new tokens, Caddy prefix
  behaviour in a browser. Local images `localhost/infb-gateway:local` and `localhost/infb-tools:local` remain in the Podman store.

## 7. PR

https://github.com/pulso-factored/infra/pull/40 (branch `claude/infra-run-health`, 3 commits, ready for review; you merge). No PR in llm-gateway or tool-service (not needed).

## 8. Needs a human decision

* D1. Wire the OTLP forwarder now? Needs `LANGFUSE__*` secret keys, `FORWARDER_IMAGE`, `langfuse` service env; Langfuse full content is already authorized.
* D2. Auto-restart unhealthy containers (autoheal sidecar or systemd timer)? Recommended for pulso and agent-core.
* D3. Engine first-boot DB: keep the manual master steps (db-bootstrap) or add a one-shot migration job running as the master role.
* D4. Which process runs the improvement loop on the engine host (`pulso run` only, or a driver with `steps_cli`)? Decides whether the prod-like loop smoke can ever be green without extra images.
* D5. Accept host replacement on the next apply because of the `user_data` change (only matters if an apply precedes review).
* D6. Pin the compose plugin by checksum and mirror `postgres` by digest into ECR (needs fetching the checksum; I did not download anything).
