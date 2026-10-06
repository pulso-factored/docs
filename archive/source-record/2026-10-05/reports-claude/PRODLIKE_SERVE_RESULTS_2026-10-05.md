# PRODLIKE: agent-core `serve` image in the prod-like rehearsal (2026-10-05)

Lane PRODLIKE (Claude). Local synthetic only: no AWS call, no `terraform apply`, no real data, `D:\Nexus` untouched, no secret printed (values only in child
process environments, read from `agent-core.env` / `llm-gateway.env` by NAME through the rehearsal's env contract). Everything ran on the shared Podman machine
`pulso-dev` (not reconfigured), prefix `prodlike`, host ports 20530-20533.

Sources: agent-core `origin/main` `edd65df` (PR 70), infra `origin/main` `9f06c17` (PR 40), engine `origin/main` `416cecc` (PRs 112, 119, 122 merged), llm-gateway and
tool-service `main` (shallow clones under `D:\.codex\factored\tmp\prodlike-*`, no other lane's worktree touched).

**Deliverables.** Infra PR: https://github.com/pulso-factored/infra/pull/44 (branch `claude/infra-prodlike-serve`, worktree `D:\.codex\factored\worktrees\infra-claude-prodlike`). Ask for agent-core:
`ASKS\ASK_agent-core_serve_followup.md` (Spanish, ready to forward). This report.

## 1. Headline

* The image is good as a container: 316 MiB, `linux/amd64`, built in 40 s cold with Podman from its own Dockerfile, non-root (uid 10001), starts in
  `serve mode=production` with `AGENTCORE_ALLOW_DOUBLES` unset, per-dependency `/readyz`, graceful SIGTERM, fail-fast on a missing variable naming it, recovery
  from Postgres/gateway outages without a manual step, the engine's minted builder credential accepted and correctly limited.
* **It cannot run the product flows yet.** One defect (A1) blocks the transfer flow (recepcion to disputas), the dispute flow (charge matching) and every
  `eval_suite` evaluation over `serve`: the `classifier` provider needs an input key `text` that no flow produces. The survey's "transfer fails over serve" is
  still true after PRs 62 to 70; the cause is now isolated.
* Copilot (advisor) turns work end to end with mimo flash, real tool-service data, field grants and a DOUBLE of the platform grants endpoint, but about one in six
  gateway generations comes back `invalid_output` and about one in forty times out, so a single turn succeeds roughly 3 times in 4 (section 3.4).
* The engine IMAGE could not be built (the machine never had the 3 GB free RAM you set as the floor: 0.7 to 1.9 GB for four hours), so `pulso loop` ran from an
  already built host binary of the ENGPROD lane instead (section 4). The engine image, the proxy and the engine `/readyz` are NOT exercised.
* Approve, publish and promote were not automated (rule). The engine principal gets 403 `forbidden_role` on both.

## 2. Image and bring-up

| Item | Result |
|---|---|
| `podman build` of agent-core's Dockerfile (`--platform linux/amd64 --format docker`, cold pull of both pinned bases) | 316 MiB (332 MB decimal), 40 s; `GIT_SHA` baked; user 10001; `HEALTHCHECK` probes `:8000/healthz` while serve runs on 8001 under infra (compose overrides it to `/readyz`). `linux/arm64`: NOT built |
| gateway / tool-service images (our recipes) | 17 MB in 7 s / 250 MB in 9 s |
| Engine image (`build engine`, Rust) | NOT built: RAM floor never met (see section 4) |
| `up` through compose | blocked by this machine, as INFRA_RUN_HEALTH said: crun cannot enforce the daemon's default pids limit (`controller pids is not available`), also with `pids_limit: 0` or `-1`. Documented fallback implemented and used: `up --podman-run` starts the SAME rendered services with `podman run --pids-limit=0` (memory limits dropped, reported). No machine setting changed |
| `up` (Postgres 16.4 with the rendered initdb, agent databases and roles, owner-role migrate with `--app-role agent_app`, gateway, tool-service, agent-core, platform double) | healthy twice in a row in about 2 minutes after the images exist; second `up` over existing volumes keeps the same passwords (secrets derive from a persisted seed) |
| `smoke` | 9 checks pass, 0 fail, engine edge reported as slot |

## 3. Checks

Legend: pass / fail / not run. "Evidence" counts are from this run's logs and JSON (`D:\.codex\factored\tmp\prodlike-work\*.json`).

### 3.1 Probes and startup

| Check | Status | Evidence |
|---|---|---|
| `/healthz` 200, `/readyz` 200 with all dependencies up | pass | `{"status":"ready","checks":{"postgres":"ok","keys":"ok","schema":"ok","llm_gateway":"ok","tool_service":"ok"}}`; `/version` 200 |
| Startup mode line with `AGENTCORE_ALLOW_DOUBLES` unset | pass | log line `serve mode=production`; container env has neither `ALLOW_DOUBLES` nor `ALLOW_DEMO` |
| `AGENTCORE_ALLOW_DOUBLES=1` behaviour | not run | only the unset path was asked |
| DB down | pass | `/readyz` 503 `failed:["postgres","schema"]`, `/healthz` 200 (7 s into the outage and again at 0.1 s); engine edge not in the stack |
| gateway down | pass | `/readyz` 503 `failed:["llm_gateway"]` (default `AGENTCORE_READY_REQUIRE_LLM_GATEWAY=1`), `/healthz` 200 |
| tool-service down | pass | `/readyz` 200 `degraded:["tool_service"]` (optional by default), `/healthz` 200 |
| Recovery without a manual step | pass, slow | Postgres back: serve ready after 30.2 s (measured once under chaos, once by polling: still 503 at 7 s); gateway back: about 30 s; tool-service back: 2 s |
| serve STARTED while Postgres was down | pass | process alive, `/healthz` 200, `/readyz` 503, ready 2.1 s after Postgres started, nothing else done |
| Missing required variable | pass | removed `AGENTCORE_KEYS_TOKEN_MAP`, `AGENTCORE_REGISTRY_DSN`, `AGENTCORE_JEV_API_KEY` in turn: exit code 2, message names the variable, no secret value in the output (checked against every value in `agent.env`) |
| Non-root | pass | `uid=10001` inside the container |

### 3.2 Turns through the real gateway (mimo flash, synthetic customer `CLI-0000000001`, tool-service data)

The fixture model profile names `google/gemini-3.1-flash-lite`; the registry was imported from a copy with `xiaomi/mimo-v2.6-flash` (`seed --model`), and the gateway log
confirms the model. JEV (Understand) is the real service.

| Case | Status | Evidence |
|---|---|---|
| recepcion es: dispute of 120 USD, expect transfer to disputas | **fail** | "No entendi bien que necesitas" on 6 of 6 attempts with three different phrasings; cause A1 |
| recepcion pt: same, in Portuguese | **fail** | same cause; reply is in Portuguese only when the message is long and unambiguous (A3) |
| recepcion es: stolen card (interrupt) | pass | `escalated`, 0.7 s, 5 of 5 |
| disputas es: direct | **fail** | run stays `open`: `match-cargo` cannot choose a charge (A1) |
| consultas es / pt: case status | not verified | asks the radicado and escalates after `CASE-1` (`escalated`, 0.8 s, 4 of 4); the flow asks for a PQR id and the synthetic id has a different shape, cause not isolated; pt reply came back in Spanish in two attempts |
| copiloto-asesor es: card balance | partial | figure (1342.80 USD) in the answer in 4 of 6 attempts; answer time 10 to 60 s |
| copiloto-asesor pt: card balance | partial | figure in 2 of 5 attempts; answers in Portuguese once `--lang-thresholds` is supplied (A3); two attempts waited 91 to 144 s on gateway 504 timeouts |
| The failing transfer flow of the survey | **fail** | not fixed by PRs 62 to 70: A1 |

Gateway over the whole session (since its last restart): 114 generations, 92 ok (81 percent), 19 `502 invalid_output` ("el contenido no es JSON", "/tool: tipo
distinto de string", "truncated output" at `max_tokens` 400), 3 `504 timeout` (profile `timeout_s` 20); p50 4.4 s, p95 17.7 s, max 20.0 s per generation.
No `serve` 5xx and no `serve` ERROR line during any of this once the classifier directory was mounted correctly.

### 3.3 Registry flow with the engine principal (credential minted from the seed; `exercise_serve.py`)

| Step | Status | Evidence |
|---|---|---|
| create proposal as `pulso-engine` | pass | 201, `created_by=pulso-engine` (the engine's public key sits next to the staff key in `staff-keys` under `pulso-engine-local`) |
| write draft, validate, freeze | pass | 200, 200, 200; proposal state `candidate` |
| evaluate with `disputas-suite@1.0.0` | **fail (verdict)** | 200 but `verdict=failed_infra`, `HarnessUnavailable ... ['classifier']`, 1.3 s: A1 |
| approve by the engine principal | pass (denied) | 403 `forbidden_role` |
| publish by the engine principal | pass (denied) | 403 `forbidden_role` |
| forged credential (other key) | pass | 401 |
| approve / publish / promote by a human | not run | by rule; the platform is not in the stack. Only the engine-side contract was verified |
| run export (exporter-role credential) and lineage | pass | 50 runs listed, 11 to 41 events per run, lineage keys `approved_by, built_by, entities, eval_verdict, knowledge_snapshot, proposal_id`; a constructor-only credential gets 403 on export |

### 3.4 Concurrency (20 simultaneous conversations, one principal each; the first attempt with ONE principal got 20 of 20 `429 rate_limited`, A6)

| Load | Status | Evidence |
|---|---|---|
| recepcion fraud interrupt (JEV + rules, no generation) | pass | 20 of 20, 0 errors, p50 2.0 to 2.2 s, p95 2.3 to 2.6 s, wall 2.6 s (two runs) |
| copiloto-asesor card balance (JEV + tool-service + mimo flash) | **fail** | 14 of 20 and 9 of 20 (two runs), p50 13.8 to 14.2 s, p95 20.8 to 22.7 s, wall 25 to 31 s; every miss is a gateway 502 `invalid_output` or 504 timeout; 0 `serve` 5xx (A5) |

### 3.5 Chaos

| Check | Status | Evidence |
|---|---|---|
| restart Postgres while serving | pass | `/readyz` 503 at once, `/healthz` 200 throughout, ready again 30 s after Postgres returned |
| restart serve with SIGTERM during a long turn | pass | in-flight turn finished (figure in the answer), same run readable, next turn accepted after 4 s, ready 2.1 s after restart. Needs the 30 s `stop_grace_period` this PR adds; Docker's default 10 s would cut it |
| kill -9 serve during a long turn | pass with a wait | run stays `open`, next turn gets `409 turn_in_progress` for 57 s (10 attempts) until the lease expires, then continues; the same `client_turn_id` retry works (A8) |
| `agentcore sweep --once` | not run | not scheduled by infra on the EC2 hosts (I2) |

## 4. `pulso loop` against this serve (planted SYNTHETIC cells)

**What ran.** The engine IMAGE was not built (the Rust build needs about 3 GB of free host RAM; the machine showed 0.7 to 1.9 GB for the whole session while only user
applications were running, no `cargo` or `rustc`, and a waiter I left polling for 50 minutes never saw 3 GB). Rather than break the floor, I ran `pulso loop` from the debug
binary the ENGPROD lane had already built (`D:\cargo-targets\claude-engprod\debug\pulso.exe`, copied, 2026-10-05 14:17, the branch that became PRs 119 and 122) with the SAME env
contract the rehearsal renders (`pulso.env` + `common.env`: seed, kid, gateway key, with the core and gateway addresses pointed at the published loopback ports of this stack),
the planted synthetic cells of `scripts/demo-loop/planted_cells.py` (350 rows, metric M4, one planted category), `PULSO_CELLS_SOURCE=synthetic`, `PULSO_PROFILE=demo`,
`PULSO_EVAL_BEFORE_ANNOUNCE` on (the proof ran, with the agent-core venv's Python and `scripts/regression`), Scout and Builder `xiaomi/mimo-v2.6-flash`, Verifier
`xiaomi/mimo-v2.6-pro`. Not announced to a platform (none in the stack). `prodlike.py loop` (the image version of the same run) is implemented and untested for that reason.

| Result | Value |
|---|---|
| `pulso loop --check` | `auth_mode: engine builder principal (minted from the service seed, short-lived)`, `cells_present: true`, `proof: true`, `support_profile: demo`, `source: synthetic` |
| `pulso loop` | exit 0 in 112 s, USD 0.001123, `infra_failures: 0` |
| Findings | corroborated 1, reasoned 1, proposed 1, delivered 1, announced-outcome 1 (it would have been announced; `announce` was off), blocked / denied / failed 0, builder tier `flash` |
| What it proposed | a patch of `template:t/estado_pqr` (agent `consultas`: "Ya consulte tu PQR" gets the status), proof `regression_suite_proven` |
| In agent-core | proposal `01a10e18-d528-756f-8b3f-7f44b8b0bfd6`, state `draft`, `created_by=pulso-engine`, agent `consultas`, one change; receipts keep it idempotent per finding |
| Contract flag | `engine_never_approves_publishes_or_promotes: true`; nothing was approved, published or promoted |

So the engine side of the loop works against the production-mode `serve` for a prompt/template finding, minted credentials included. Note the contrast with A1: the engine's own
regression suites are prompt-only and never touch the classifier, so they pass where agent-core's `disputas-suite` cannot.

## 5. Env contract: serve-env.md against what infra renders (comparison done on `compose.agents.yaml`, `generated.tf`, `secrets.tf`, `variables.tf`)

| Variable or setting | serve-env.md | infra renders | Verdict |
|---|---|---|---|
| `AGENTCORE_REGISTRY_DSN`, `AGENTCORE_EVAL_DSN` | R, S | secrets `AGENT__...`, role `agent_app`, databases `agent_runtime` / `agent_eval` | match |
| `AGENTCORE_MIGRATE_DSN`, `AGENTCORE_MIGRATE_EVAL_DSN` | not in the doc | owner-role DSNs, swapped in by the migrate entrypoint | infra-only names; doc should say "migrate reads REGISTRY/EVAL DSN with the owner role" |
| `AGENTCORE_KEYS_FINGERPRINT`, `_TOKEN_MAP` | R, S, `kid:base64`, 32+ bytes | `k1:<base64>` generated by Terraform | match (rehearsal uses 32 random bytes) |
| `AGENTCORE_JEV_API_KEY` | R, S | secret key, seeded `CHANGE_ME` | match; a placeholder passes the "non-empty" check and fails at the first JEV call |
| `AGENTCORE_IDENTITY_KEYS_FILE`, `_STAFF_KEYS_FILE` | R / C, JSON or YAML | flags `--identity-keys`, `--staff-keys` and the env, files from `FILES__AGENT__*` | match; the engine public key must be listed under `PULSO_SERVICE_KID` (rehearsal does it) |
| `AGENTCORE_TOOL_SERVICE_URL/TOKEN`, `AGENTCORE_LLM_GATEWAY_URL/TOKEN`, `AGENTCORE_GRANTS_URL/TOKEN` | C / O | compose environment + secrets; gateway consumer `agent-serve` | match |
| `AGENTCORE_CALIBRATION_DIR`, `_CLASSIFIER_ARTIFACTS_DIR`, `_FIELD_CLASSIFICATION_FILES`, `_AUTHZ_FIELD_GRANTS_FILE`, `_AUTHZ_BIND_KEYS`, `_FX_RATES_FILE` | C / O | compose environment; artifacts synced from S3 | match by name. Content gap: `FILES__AGENT__FIELD_OVERLAY`, `FIELD_GRANTS`, `FX_RATES` are seeded `CHANGE_ME` (I4) |
| `AGENTCORE_LANG_THRESHOLDS` / `--lang-thresholds` | O, "without it the language never changes" | not set; Terraform has no `FILES__AGENT__LANG_THRESHOLDS` key, although `prod.tfvars.example` suggests it | **mismatch (I3)**; observed effect: Portuguese answered in Spanish |
| piece flags (`--tools` and six more) | defaults are the real factories | Terraform default `agent_serve_args` lists them explicitly | harmless duplicate; module paths differ from the doc's but both import |
| `AGENTCORE_AUTO_MIGRATE` | default 1; set 0 for a role without DDL | unset; serve runs as `agent_app` after the owner-role migrate | works because the ledger is current; set 0 explicitly (I6) |
| `AGENTCORE_DB_POOL_MAX` | default 0 = one connection per operation | unset, while the connection budget in shared-postgres.md assumes pooling | mismatch in assumption (I6) |
| `AGENTCORE_READY_REQUIRE_LLM_GATEWAY` (1), `_TOOL_SERVICE` (0) | O | unset | defaults apply; with autoheal they interact (I5) |
| `AGENTCORE_SHUTDOWN_GRACE_SECONDS` (25) vs orchestrator grace | must be lower than `stop_grace_period` | **no `stop_grace_period`** (Docker default 10 s) | **mismatch, fixed in this PR (I1)** |
| `AGENTCORE_MAX_INFLIGHT`, `_WORKER_THREADS`, `_RATE_*`, `_DAILY_BUDGET_USD` | O | unset | defaults; the rate limit is "demo" (A6) |
| port | image `8000` (CMD, HEALTHCHECK, EXPOSE) | `--port 8001`, healthcheck `/readyz` on 8001 | documented override |
| `agentcore sweep --once` every few minutes (section 7 of the doc) | to be scheduled by the deployer | nothing schedules it on the EC2 hosts | **gap (I2)** |
| OTEL / `AGENTCORE_TRACE_*` | O | not wired (forwarder not wired) | known (D1 of INFRA_RUN_HEALTH) |

## 6. Defects, owner and precise ask

Agent-core items are in `ASKS\ASK_agent-core_serve_followup.md` (Spanish, forwardable); the numbers match.

| ID | Defect | Owner | Ask |
|---|---|---|---|
| A1 | `classifier` provider requires input `text`; `decide` nodes pass path-keyed views (`slots.problema`). Blocks transfer, dispute matching and every evaluation | agent-core | accept the view without a magic key (`text_from` or concatenate string values); add a `serve`-mode composition test: recepcion to disputas, a charge match, an evaluate that is not `failed_infra`; add `problema` and friends to the shipped field overlay |
| A2 | `/readyz` 200 with an unusable classifier directory; the turn fails as 500 | agent-core | `artifacts` readiness check; typed 503 instead of 500 |
| A3 | language never switches without `AGENTCORE_LANG_THRESHOLDS`; kit and compose omit it | agent-core (kit) + infra (I3) | ship the file in `serve_state.py` and the reference compose; startup warning |
| A4 | fixture model profile is gemini-flash-lite, policy is mimo flash | agent-core | fixtures to mimo flash or documented override |
| A5 | mimo flash: 17 percent `invalid_output`, 3 percent timeouts; `max_tokens` 400 truncates | agent-core + llm-gateway | one repair retry, schema mode or a larger `max_tokens`, counter per agent |
| A6 | per-principal rate limit uses "demo" values; 20 starts from one principal are all 429 | agent-core | document and warn in production mode |
| A7 | body validated before authentication on `/v1/registry/*` (forged credential + bad body = 422) | agent-core | authenticate first |
| A8 | kill -9 mid-turn locks the session 57 s (`turn_in_progress`) | agent-core | document the lease and its variable |
| A9 | readiness takes about 30 s to recover | agent-core | document or shorten |
| A10 | HEALTHCHECK fixed to 8000; reference compose without `restart`, `service_started` | agent-core | minor |
| I1 | no `stop_grace_period` on agent-core | infra | **fixed in the PR** (30 s) |
| I2 | `agentcore sweep --once` not scheduled on the EC2 hosts | infra | a one-shot service plus timer (decision: ours) |
| I3 | no `FILES__AGENT__LANG_THRESHOLDS` secret key and no `--lang-thresholds` in the default args | infra (Terraform) | add the key (seed `scripts/e2e/lang-thresholds.json` content) and append the flag; not done here to avoid host replacement and Terraform test churn |
| I4 | `FIELD_OVERLAY`, `FIELD_GRANTS`, `FX_RATES` are `CHANGE_ME` | infra + data governance | the overlay is agent-core's `field-overlay.json` plus the slot names; the grant list is a governance decision |
| I5 | the compose health check is `/readyz` and the autoheal timer restarts `unhealthy` containers: a Postgres or gateway blip restarts serve (and cuts turns after 30 s) although serve heals by itself in 30 s | infra | container health on `/healthz`, readiness for the deploy gate only; or an autoheal back-off |
| I6 | `AGENTCORE_AUTO_MIGRATE`, `AGENTCORE_DB_POOL_MAX`, `AGENTCORE_READY_*` implicit | infra | set explicitly (0 / a pool that fits the 100 connections / chosen) |
| I7 | `compose.loop.yaml` described an interface the engine did not have | infra | **fixed in the PR** (command `loop`, ENGINE_PROD.md env) |
| M1 | this Podman machine cannot start containers through compose (no pids cgroup) | user decision | optional: `pids_limit` in the machine's `containers.conf`; not touched |
| E1 | the engine image was never built here (RAM floor) and the proxy / engine `/readyz` are unexercised | whoever has 3 GB | `PULSO_STACK_PREFIX=prodlike python scripts/prodlike/prodlike.py build engine --src <engine>` then `up` and `loop` |

## 7. Still missing from the support-platform team (the rehearsal replaces the first with a double)

1. Backend and SPA images (`SUPPORT_API_IMAGE`, `SUPPORT_WEB_IMAGE`) with a real `/healthz` and `/readyz`, running on Postgres instead of SQLite.
2. `GET /api/v1/internal/grants/{ref}` returning `{"active": bool}` with the shared internal bearer (a double answers it now; a revocation is never seen).
3. The announce endpoint the engine calls after a proof (`/internal/builder/proposals/announce`) and the proposal inbox for supervisors.
4. The human approval path: staff credentials with `aprobador` and `step_up` signed by the key listed in `staff-keys`, the approve and publish calls to `serve`, the release
   event back to the engine (`release.published`) and the outcome step. None of it was exercised; the engine side only proved it is refused.
5. The issuers of the customer and advisor principal credentials and of the `X-On-Behalf-Of` delegation, signed by the keys in `identity-keys`.
6. The engine's read-only database role over `event_log` and the platform exporter contract.

## 8. Not run (so nobody assumes it was covered)

Engine image, proxy, engine `/readyz`, forwarder image, `linux/arm64`, `AGENTCORE_ALLOW_DOUBLES=1`, approval and publication, key rotation, `sweep`, `relay`, OTLP and Langfuse from the
container, any real data, any AWS resource.

## 9. Reproduce

```text
$env:PULSO_STACK_PREFIX = 'prodlike'
python scripts/prodlike/prodlike.py build gateway --src <llm-gateway>; ... build tools --src <tool-service>; ... build agent --src <agent-core>
python scripts/prodlike/prodlike.py state --agent-core <agent-core>
python scripts/prodlike/prodlike.py up --podman-run --env-file <llm-gateway.env> --env-file <agent-core.env>
python scripts/prodlike/prodlike.py seed --agent-core <agent-core> --model xiaomi/mimo-v2.6-flash
python scripts/prodlike/prodlike.py smoke
uv run --project <agent-core> python scripts/prodlike/exercise_serve.py --only turns,registry,export,load,loadllm,midrun
python scripts/prodlike/prodlike.py chaos postgres   # gateway-down tools-down serve-restart serve-start-db-down serve-env-missing
python scripts/prodlike/prodlike.py down --volumes
```
