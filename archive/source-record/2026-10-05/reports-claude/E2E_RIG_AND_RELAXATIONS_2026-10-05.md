# E2E rig and honest relaxations (2026-10-05)

Read-only research. Sources: support-platform origin/main a451001 (RUNBOOK 4.1/9.1, slice-16/22 docs, ADR 0007, `internal.py`, `builder.py`), agent-core main 789edc0 (`scripts/e2e/*`), infra main (`service-deployment.md`, `agent-services.md`), our `scripts/dev-stack`, `scripts/demo-loop`, `docs/dev/OUTCOME_STEP.md`, `EVAL_SUITES.md`. Nothing was started.

Finding 0: the PR 16 e2e (`pnpm e2e:stack`) does NOT start anything. It expects `../stack/up.sh` + `stack/README.md` in a folder beside the repos, and that folder is not in any repo nor on this machine. We cannot "reuse" it; we reuse its contract (ports 8100/5174, accounts, `globalSetup` checks) and write our own bring-up (Stage 1 below). Ask the platform team (Juan) to commit `stack/` or send it.

## 1. Rig

### 1.1 Components, ports, RAM (host has about 2-4 GB free; Podman VM 4 GiB)

| # | Component | How | Port | RAM | Health |
|---|---|---|---|---|---|
| 1 | Postgres 16 | Podman, `stack.py` (prefix `pulso-demo`) | 55490 | ~120 MB (VM) | `pg_isready` |
| 2 | llm-gateway (Go, no Go on host) | Podman image built once | 8190 | ~40 MB (VM) | `GET /healthz` |
| 3 | agent-core `serve` | host, `uv run agentcore serve --registry-api` | 8191 (platform expects it via `CC_AGENT_CORE_URL`) | ~250 MB | `/healthz`, `/readyz` |
| 4 | support-platform API | host, `uv run cc-api`, SQLite, `CC_PORT=8100` | 8100 | ~150 MB (+64 MB per concurrent login, Argon2) | `GET /api/v1/health`, `/api/v1/meta` |
| 5 | SPA | Stage 2 only: `pnpm build` then `vite preview` (not `dev`) | 5174 | ~80 MB preview vs ~350 MB dev | HTTP 200 |
| 6 | engine `pulso run` (Rust binary, prebuilt) | host | 4190 (loopback) | ~100-150 MB | `/healthz` |
| 7 | tool-service | NOT needed for the loop (only assistant tool calls). Skip; needs `data-pipeline` dataset | 8095 | 0 | - |
| 8 | Playwright Chromium | Stage 2 only | - | 400-600 MB | - |

Budget Stage 1: about 750 MB host + 160 MB VM. Stage 2 adds about 700 MB. Run Stage 2 with nothing else (no IDE agents, no second stack). Never run `cargo` or the gateway image build at the same time as the rest.

### 1.2 Wiring table (who calls whom)

| Caller -> callee | URL | Credential and identity | Where it comes from |
|---|---|---|---|
| engine -> gateway | `127.0.0.1:8190` | consumer token `GATEWAY_TOKEN_AGENT_CORE` (`PULSO_LLM_GATEWAY_KEY`) | `agent-core.env`/`llm-gateway.env` (in memory only, as in demo-loop) |
| agent-core -> gateway | same | same token via `AGENTCORE_LLM_GATEWAY_TOKEN` | `stack.py` already rewrites it |
| engine -> agent-core registry/runs | `127.0.0.1:8191` | `PULSO_REGISTRY_TOKEN` = JWS `builder` principal `pulso-engine`, role `constructor`, kid `pulso-engine-dev-1` | `identity.py mint` (12 h); agent-core must list that kid in **staff-keys.json** (it does) |
| platform -> agent-core (builder reads, approve, publish, promote) | `CC_AGENT_CORE_URL=http://127.0.0.1:8191` | staff-signed registry credential, step-up for decisions; `CC_AGENT_KEYS_FILE=.agent-keys/private.json` | `uv run python -m cc_platform.scripts.gen_agent_keys --suffix dev` |
| platform -> agent-core (announce read) | same | platform-signed `engine` principal with `constructor` role (read-only) | same private.json |
| agent-core -> platform (`grant_active`) | `AGENTCORE_GRANTS_URL=http://127.0.0.1:8100`, `AGENTCORE_GRANTS_TOKEN` | bearer = `CC_INTERNAL_SERVICE_TOKEN` | needed only for assistant/copilot delegations; the builder flow does not use it. Set it anyway so the platform route exists |
| engine -> platform announce | `POST http://127.0.0.1:8100/api/v1/internal/builder/proposals/announce` | bearer `CC_INTERNAL_SERVICE_TOKEN` (engine env `PULSO_PLATFORM_SERVICE_TOKEN`); unset = 404 | one random value shared by both sides |
| SPA -> platform | `VITE_API_URL=http://127.0.0.1:8100` baked at build | session + `CC_CORS_ORIGINS` must contain the SPA origin exactly | use `["http://localhost:5174","http://127.0.0.1:5174"]` |
| poller -> engine | `127.0.0.1:4190/internal/v1/automation/triggers` | admin token (ephemeral) | `agentcore_poller.py` |
| poller -> agent-core export | `/v1/export/registry-events`, role `exporter` | exporter credential | not minted by `identity.py` today (gap G9) |

**Key merge (the main wiring risk).** Platform and engine mint different keys. agent-core's `--identity-keys` and `--staff-keys` must each be ONE file holding the union of public keys: platform `principal_keys` (kid `...-<suffix>`) plus our `pulso-engine-dev-1` and, for admin/registry import, the `TestStaffIssuer` kid. Write a small `merge_keys.py` (extend `identity.py keys` with `--platform-keys <dir>`). `testing.demo_identities` tokens stop working once the platform's keys replace them; keep the union to keep the `admin` import token.
**Roles in agent-core.** The engine's `builder` principal must hold `constructor` and never approver; the supervisor via platform is `human + step_up`.

### 1.3 Identities and login (seeded dev DB, `CC_SEED_DEMO_DATA=true`)

Password `demo1234` for all; MFA dev code `000000` (`CC_DEV_MFA_CODE`). Supervisor: Lucia Herrera `lucia.herrera@latambank.example` (Supervision, es/pt), Martin Salazar, Renata Villalba. Felipe Echeverri is Analyst+Supervision. Admin: Valeria Quintero, Carolina Pena. Analyst: Tomas Arango etc. Step-up for approve/publish/promote: the dev code `000000` (seeded accounts have no authenticator); `CC_ASSISTANT_STEP_UP_CODE` is only the customer's simulated factor. Do not use Tatiana Rojas (real TOTP, key `JBSWY3DPEHPK3PXP`) unless we want the real-TOTP path: a good second run to test `stepUpCode` with `pyotp`.

### 1.4 Start order and checks

1. `stack.py up` (own prefix/ports): postgres, gateway, migrate, registry import (`registry-e2e`: disputas, consultas), serve. Set `PULSO_SERVE_E2E=1`, `PULSO_SERVE_AGENTS=disputas,consultas` (demo loop default), but add `constructor-chat`/`recepcion` only for Stage 2 builder-chat checks.
2. `gen_agent_keys`, merge keys, restart serve (it re-reads keys every few seconds, no restart needed once file changes).
3. Platform: delete `backend/cc_platform.db` first (no migrations: ADR 0007 and slice 21/22 need a recreate), then start `cc-api` with `CC_AGENT_CORE_URL`, `CC_AGENT_KEYS_FILE`, `CC_INTERNAL_SERVICE_TOKEN`, `CC_PORT=8100`, CORS list. Check `GET /api/v1/meta` -> `agentCoreConfigured`, and `/builder/status` -> `available:true` with a supervisor session.
4. Engine `pulso run` (demo-loop environment plus `PULSO_PLATFORM_URL`).
5. Stage 2: SPA build + preview, Playwright.

Failure modes seen or expected: `credentials_invalid` (kid not in the merged key files); announce 404 (token unset, AI off, registry does not know the proposal because the engine wrote to another agent-core); announce 422 (email-like text, 9+ digits, a URL in `evidenceLinks`, field over caps); announce 502/503 (agent-core down, retry is idempotent); SPA "No hay conexion" (CORS origin mismatch `localhost` vs `127.0.0.1`); `OutdatedSchemaError` (old SQLite); 10 proposals per 24 h quota in agent-core; Podman pids-limit (script passes `--pids-limit=0`); `registry-e2e` entity change needs `--reset-db`; serve exited silently once (re-up); a lane clobbering the shared `pulso-l3` stack (use prefix `pulso-demo`).

## 2. The integrated scenario, step by step

| Step | Action | Real | Stand-in | Relax |
|---|---|---|---|---|
| 0 | Seed: platform demo DB; agent-core registry-e2e; bank cells (or planted) | platform seed, agent-core registry | tool-service skipped | evidence cases: see G1 |
| 1 | Engine loop on the cell table, findings, LLM Builder writes patch, eval before announce | engine, gateway + real model, agent-core Builder run, registry draft `origin=auto_detect`, eval | `disputas`/`consultas` demo doubles for tools in serve | eval suite from `agent-core-assets/eval-suites/pulso-min` attached (EV1) because no real agent has one |
| 2 | Engine announces | real announce route, real registry confirm, real notification | none | engine must send `CASE-` ids that exist in the platform seed (G1) |
| 3 | Supervisor (Lucia) logs in, bell shows "Nueva propuesta de mejora", opens Automatizacion -> Propuestas, source "Del motor de mejora" | real SPA/API | - | SPA must render the dossier (G5) |
| 4 | Evaluate (if not done), approve with `000000` | real registry `step_up`, real platform builder | dev verifier instead of an authenticator: labelled stand-in, `CC_ENV=dev` only | (R3) |
| 5 | Publish -> `staging` alias moves, release id | real | - | - |
| 6 | "Pasar a producción" -> `prod` alias promoted | real | - | - |
| 7 | agent-core emits `release.published|promoted`; poller -> engine trigger | real if poller reads `/v1/export/registry-events`; else `explicit` trigger | exporter credential minted locally | release event carries `proposal_id` (G3) |
| 8 | Outcome step | real engine step and estimator | **post-release data is not real**: no contacts exist after the release | R1 demo clock, label on card |

## 3. Relaxations (each labelled, each fenced)

| ID | Relaxation | Honest label | Safeguard against leaking into production |
|---|---|---|---|
| R1 | **Demo clock for the outcome**: `PULSO_OUTCOME_PSEUDO_RELEASE=<month>` plus `PULSO_OUTCOME_POST_CELLS` = planted table (treated numerator cut by a known pp, `scripts/demo-loop/planted_cells.py`) or a later bank month replay; `PULSO_OUTCOME_DATA_LABEL=synthetic-planted-effect`. Already built. Add a `demo_clock:true` line in the card, dossier and the console run | Card/dossier end "DATOS SINTETICOS: efecto plantado..." and `period_kind` is `pseudo_release_historical` | Refuse the env vars unless `PULSO_PROFILE=demo`; card with a data label can never set `success_claimed` outside demo; the announce route is never fed from a demo card |
| R2 | Outcome allowed on a staging-only release: accept `release.published` as the measurement start when the demo profile is on; real mode waits for `promoted` to `prod` | Card says "measured on staging release" | Profile flag; prod config has no such key; test that without profile a staging event is `skipped:not_prod` |
| R3 | Pre-approved demo approver: dev code `000000` for Lucia (already platform behaviour for seeded accounts) | stand-in; the audit shows it | `CC_ENV=dev` only (platform prod refuses to start with dev mailbox/demo seed). Do not add anything to the engine: it never holds an approver credential |
| R4 | Demo minimum-support floors: a `demo` profile lowers the cell floor so the 8-pp planted effect on small cells passes; the card says `support_profile: demo` | on the card and dossier | Floors are read from one config object; the profile can only lower floors when the data label is `synthetic-*`; contract test |
| R5 | Evidence links: map each finding to seeded platform case ids (`CASE-...` in the seed cases of the platform) via a demo file `evidence-demo-map.json` | dossier note "casos de ejemplo, no son la evidencia" | engine sends only validated ids (already: case ids only); the map is read only in profile demo |
| R6 | Eval suite attached by script (EV1) | "suite minima Pulso" in the review | not an engine capability in prod; real suite comes from Codex T2 |
| R7 | Unlock "no release has ever happened": publish and promote through the real platform steps (R3) so the release event is real; only the post-period data is simulated | the verdict mode says which | - |

Demo dataset: two levels. A (honest): real bank cells; expected cards inconclusive, shows the guard. B (planted): same bank tables, post tables with the treated cell cut by 8 pp, as validated in OUT1 (improved, -7.16 pp). Run both and show both; B alone must never be presented as a result.

## 4. Integration gaps this rig exposes

| # | Gap | Owner | Effort |
|---|---|---|---|
| G1 | `evidenceLinks` are opaque ids derived from findings (DEMO_LOOP.md), but announce needs `CASE-` ids; today they would be dropped or mismatch | engine (map) + platform (confirm ids exist) | S (demo map), M real |
| G2 | `stack/` bring-up missing from repos | platform (Juan) | S |
| G3 | Release events lack `proposal_id`/agent alias on runs; platform events carry no `release` field | agent-core PR 49 + platform exporter | M |
| G4 | Approver does not see the inherited values (base release vs candidate) | platform SPA + agent-core read | M |
| G5 | SPA proposal page shows only registry `docs`; the dossier lives only in the notification; needs `source=engine` rendering and "Pasar a produccion" | platform frontend | M |
| G6 | Does `track`/adopt read the real agent-core: yes, `announce_proposal` does a constructor read with a platform-signed `engine` credential. Unverified live: that agent-core accepts that role for a proposal created by our `pulso-engine` principal | platform + agent-core | S to verify in Stage 1 |
| G7 | TOTP for engine proposals: same path as human ones (`stepUpCode`); verify wrong code counts toward lock | platform | S |
| G8 | Notification link opens `automationProposalPath`, depends on slice 22 route being merged with PR 17 | platform | S |
| G9 | Exporter credential for the poller not minted by `identity.py`; trigger records are in memory (restart loses them) | engine | M |
| G10 | Key-file merge tool; today the two worlds mint separate keys | engine dev-stack | S |
| G11 | No eval suite for any real agent: nothing evaluable/approvable without R6 | Codex T2 | L |

## 5. Staged plan

**Stage 1: API-level integrated run (no browser), about 1 day.** `stack.py up`, platform up (8100), merge keys, engine run with `-Announce` against the real route, then a script using `requests` to: log in as Lucia (`demo1234`, MFA `000000`), read notifications and `/builder/proposals`, evaluate, approve, publish, promote, with `stepUpCode`. Exit criteria: proposal `source:"engine"` visible, audit rows, `staging` and `prod` aliases moved. Closes G6, G7, G10.
**Stage 2: SPA browser e2e, about 1 day after Stage 1.** Build the SPA, add `engine-proposal.spec.ts` in `frontend/e2e-stack` style (same `accounts.ts`, `stack-api.ts`): bell, Automatizacion, detail, approve, publish, "Pasar a produccion". Expect the dossier gap (G5) to show as a failing assertion; take screenshots. Needs the platform team for the fix.
**Stage 3: release and outcome, about 1 day.** Poller (or `explicit`) delivers the release event, outcome card in demo profile (R1, R2), both datasets (A and B). Card, console run, dossier all say "simulated". Closes G3 (as far as possible), G9. Real post-release data remains out of reach until a real release has live contacts; do not claim otherwise.
