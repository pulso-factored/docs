# Team Claude: consolidated implementation status (as of 2026-10-04 01:20 UTC)

Author: Claude (documentation consolidator). Language: English (spec is Spanish).
Scope: what Team Claude built for the Pulso <-> Agent Core integration, the real support-platform source (spec V3 section 32), the debug console and the infra slices; what is merged, what is open or local-only, evidence, divergences, blockers, next steps.

## 0. How this was verified

All PR facts below were read directly from GitHub with `gh api` / `gh pr view` at 2026-10-04T01:15Z (not from remote-tracking refs).

| Repo | `main` head | Open PRs |
|---|---|---|
| `pulso-factored/improvement-engine` | `83516eb` (PR #86 merge, 2026-10-04T01:13:54Z) | none (PR #87, Codex, merged 01:11:48Z as `aec3904` just before #86) |
| `pulso-factored/infra` | `10a51b9` (PR #27 merge, 2026-10-04T00:35:22Z) | #28 `feat/data-lake-module` (not ours, data-pipeline team; stacked on #27) |
| `pulso-factored/agent-core` (read-only for us) | `c814c2b` (PR #30 merge, 2026-10-03T21:03Z) | none |

The user merged all of: improvement-engine #80, #82, #85, #86 and infra #26. Each is confirmed merged (SHAs below). Local evidence is authoritative because the GitHub Actions budget is exhausted (journal CL-0017); every PR body states "local validation".

## 1. Merged on `main` (Team Claude work)

### 1.1 improvement-engine (author `aleuse`, all by Team Claude unless marked)

| PR | Merge SHA | Merged (UTC) | Title / content |
|---|---|---|---|
| #74 | `fc7db60` | 10-03 14:18 | L7 fixture-backed debug console (React/TS/Vite): SSE graph, a11y and contract suites |
| #76 | `6107f10` | 10-03 19:49 | Core bridge runtime (`core-bridge/`), `platform-sim/`, `agent-core-assets/`, `local/core` stack, `scripts/core/pin-watch`, `e2e-core/`, `demo/`, first `local-identity/`; pin `789d6c8` (wire MANIFEST `890edd7a...`) |
| #77 | `589e8dd` | 10-03 19:50 | Console demo narrative panels (alternatives, gate attempts, hypotheses, hook states) and world loading |
| #79 | `4a1fa7b` | 10-03 20:45 | Local human issuer in the Core stack, key delivery from env (ADR 0009), demo steps 8-10, CI parity fix |
| #80 | `f4fbfa9` | 10-03 21:54 | Platform source (spec section 32): `platform-contract/`, `platform-sim/platform_live/`, `platform-exporter/`, console "Sources" view |
| #82 | `5ec0530` | 10-03 23:37 | Alias-read and authoring dry-run routes (no longer 501), `bridge-contract/` pack, agent-core pin bump `789d6c8` -> `894fa65` (ADR 0010, dual-pin) |
| #85 | `a4ccb0a` | 10-04 00:28 | Console typed `DebugApi` seam (http/fixture/stand-in providers), SSE resume, gated commands |
| #86 | `83516eb` | 10-04 01:13 | Annex D alignment (ADR 0011): worker `sub`, `job_id` binding, `Idempotency-Key`, `ArmRequest` names, derived `evaluation_context_ref`, `CoreVersion` fields |

PRs #81 and #84 (title "Claude/pl platform", empty body, merged 10-03 22:03 and 23:42, SHAs `0b0c919` and `594be4e`) are merge commits of the `claude/pl-platform` branch into `main` and carry no separate content. Codex PRs merged in the same window (not ours): #75, #78, #83, #87.

### 1.2 infra (Team Claude)

| PR | Merge SHA | Merged (UTC) | Title / content |
|---|---|---|---|
| #17 | `9c0e95d` | 10-03 14:21 | L9: Core workload modules, release manifest/plan validators, deploy runbook |
| #23 | `994cb62` | 10-03 16:45 | Engine platform workloads on the shared foundation (`engine_platform_enabled=false` by default) |
| #24 | `3446f6f` | 10-03 19:56 | Reconcile with merged Agent Core pieces (#19/#21/#22); engine ECR via shared module; overlap and engine plan doc |
| #25 | `ee0da71` | 10-03 19:55 | CI fix: quote `-chdir` so the Agent Core scale-out test step runs (main had been red since #22) |
| #26 | `c5ff691` | 10-03 23:37 | `bridge_services` module (`core-runtime`, `core-exporter`, `platform-exporter`), `workload` ephemeral key volume and read-only root FS, pin text moved to `894fa65` |

infra #27 (ADR 0006 data pipeline as a batch workload, `10a51b9`) and #28 (open, `data_lake` module) are by the data-pipeline side (`jzapataca`), not Team Claude.

## 2. Local-only or open

| Item | State |
|---|---|
| Pin bump `894fa65` -> `c814c2b` | **In progress** (another agent). Branch `claude/r4-pin-c814c2b` in worktree `improvement-engine-claude-a`, local commits `e55f7a8` (`synthesise_args` starts from Core's real serve-parser defaults, fixes the `lang_thresholds` `AttributeError`) and `a44003e` (constants, wire with only MANIFEST changed, bridge-contract, fixtures, ADR 0012); one uncommitted journal file and `.reports/exporter-report.json`. No GitHub PR exists for it (`gh pr list --head claude/r4-pin-c814c2b` is empty). Not claimed as done here. |
| Rust client for `bridge-contract/` and the Codex control-api | Not Team Claude (see section 6). |
| L10 (plan 17.3) | Not started. |
| infra: OIDC push role for the new engine/bridge ECR repos, `core-migrate`, sweep, alarms for the new services, CI coverage of the module `terraform test` files | Not done (not in #26); `ci.yml` is Codex-owned, a request goes through the journal. |
| console: operator screens per `BACKOFFICE_CONSOLE_PLAN_CLAUDE.md` phases 1-4 | Only phase 0 (seam) is merged; see that file's status block. |

## 3. Test evidence (counts copied from the PR bodies; local, PG16 on the team Podman machine, one suite at a time)

| PR | Evidence |
|---|---|
| #76 | core-bridge 529 passed/5 skipped; platform-sim 206; agent-core-assets 22; parity mock 166, a2 165; Pester `local/core` 89; local-identity 71 (7 real-Core proof tests); e2e-core 33 live passed on the real image |
| #79 | core-bridge 529 passed, 13 skipped, 1 failed once (Windows ephemeral-port exhaustion; the file re-ran alone: 12 passed); platform-sim 206; agent-core-assets 22; e2e-core 44 passed in the earlier package |
| #80 | platform-contract 26 passed with no drift; platform-sim `plive` 20, rest 206; platform-exporter 51 passed (real postgres:16 and SQLite, 0 skipped); ci.yml python parts 11 OK (1 skipped); debug-console vitest 121, build ok; 26-mutant check on the exporter |
| #82 | core-bridge 563 passed/13 skipped; platform-sim 228 (a2 227); agent-core-assets 22; bridge-contract real 297, mock 157 passed/25 skipped/115 xfailed; wire mock 186, a2 185; Pester 100 + python 20; e2e-core 44 passed/1 skipped on the rebuilt image |
| #85 | debug-console vitest 199 (27 files), contract 29/29 (48 provider cases), typecheck and build clean; 24-mutant check; Playwright not run |
| #86 | core-bridge full 637 passed/15 skipped; platform-sim 246 passed/2 skipped; bridge-contract real 337, mock 7 passed/29 skipped/149 xfailed; wire mock 186, a2 185; agent-core-assets 22; 12-mutant check (11 killed, 1 equivalent) |
| infra #23 | Python 101 tests; module tests identity 4, compute 3, engine_platform 11, core_vpc_endpoints 6, workload_iam 18, workload 14, envs 4+4; zero diff at defaults |
| infra #24 | Python 114 OK; fmt, init+validate staging/prod; env tests 5/5 each |
| infra #26 | `bridge_services` 18, `workload` 18, `workload_iam` 18, `engine_platform` 11, staging 9, prod 9, Python 123 OK; 16/16 mutations caught after tightening |

Not run anywhere (stated in the PRs): `real-wire` (needs an external `agentcore serve`), Rust jobs (no Rust touched), ubuntu leg, postgres:17 service job, Playwright for #85. Known pre-existing failure left alone: infra `core_data` `task_statements_stay_inside_the_workload_iam_rules` on Terraform 1.16.4 (CI pins 1.10.5). No AWS call was ever made.

## 4. Architecture map (what each directory is)

| Component | Path | Role |
|---|---|---|
| core-bridge | `improvement-engine/core-bridge/` | `pulso_core_runtime`: composes the pinned Agent Core with Pulso's `/internal/v1` API (service JWT, per-route audiences, `jti` replay), invoke + receipts CAS + reconcile, protected writer and `pulso/*` tools, native evaluation (admission, arms, isolated eval DB), tenant/stage guards, read-only observation exporter, image, `ci.ps1`; alias-read and dry-run routes (#82); Annex D alignment (#86) |
| wire snapshot | `core-bridge/wire/agent_core@<sha>/` | Generated schemas of the pinned Core (250 files at `894fa65`), drift gate in CI parity |
| bridge-contract | `improvement-engine/bridge-contract/` | Published `/internal/v1` contract for the Rust client: OpenAPI 3.1 + 28 JSON Schemas generated from the runtime models, goldens recorded from the real runtime, conformance kit, per-route README |
| platform-contract | `improvement-engine/platform-contract/` | JSON Schemas for the allow-listed support-platform tables and event catalog (one model, drift gate), golden examples, conformance suite; credential tables have no schema |
| platform-sim | `improvement-engine/platform-sim/` | Doubles: registry mock (18 routes), a2 harness (real `RegistryService`, in-memory), bridge mock, ingest fixture; `platform_live/` simulator of the 11-table platform model with fault injection (late events, gaps, unknown types, `teams` evolution) |
| platform-exporter | `improvement-engine/platform-exporter/` | Read-only cursor over `event_log`, emits `PlatformObservationBatch` (persist before POST, idempotency key = batch digest, retry until durable ack), engine-level read-only enforcement, redaction, quarantine, gap/late-event findings, as-of extract, per-attempt EdDSA service JWTs |
| agent-core-assets | `improvement-engine/agent-core-assets/` | Generic Scout/Verifier/Builder/Writer stages and worlds, expected state, validator |
| local-identity | `improvement-engine/local-identity/` | Sandbox-only human issuer (session assertions, Core human Principal JWS for approve/publish/promote/revoke); never for staging/prod |
| local Core stack | `improvement-engine/local/core/`, `scripts/core/` | Standalone Podman stack (`real_local`), doctor/smoke with CAP-63 scan, `pin-watch` upstream drift monitor |
| e2e-core | `improvement-engine/e2e-core/` | Codex stand-in (Python) driving the real stack: scout -> verifier -> builder -> writer -> admission -> evaluate-only -> arms -> exporter -> chain check; human approval; honest `e2e-report.json` with `doubles[]` |
| demo | `improvement-engine/demo/` | `pwsh demo/run.ps1`: plan section 2 demo steps 3-10 on the real stack, every step marked `real`/`stand-in`/`simulated`, feeds the console |
| debug-console | `improvement-engine/debug-console/` | Internal backoffice of the detection/self-improvement system (not a product UI). Fixture-backed screens, demo panels, Sources view, typed `DebugApi` seam with `http`/`fixture`/`stand-in` providers, SSE resume/410 recovery, gated commands |
| infra modules | `infra/terraform/modules/` | `engine_platform` (control-api, worker, migrate, sandbox-lab; off by default), `bridge_services` (core-runtime, core-exporter, platform-exporter; off by default), additive `workload` options (`read_only_root_filesystem`, `ephemeral_volumes` at `/run/pulso-keys`), engine ECR through the shared `ecr` module, Core workload modules and release validators (#17), `workload_iam` exact-ARN PassRole |

## 5. Known divergences and limitations

- Agent Core pin: `main` pins `894fa65` (contracts `1.3.0`; the version file is not a drift detector, identity is SHA + MANIFEST digest). Dual-pin rule (ADR 0010): the runtime keeps `assert_compat` valid on both the previous and the new pin. Agent Core `main` is already `c814c2b`; the bump is in progress.
- Agent Core PRs #23 (registry OpenAPI, `Idempotency-Key` on writes), #24 (proposal listing) and #28 (JEV through the llm-gateway) were merged into stacked side branches and are **not on `main`** (re-verified 2026-10-04: heads `5705e58`, `19e7a10`, `3499f94` are not ancestors of `c814c2b`). We do not plan on them.
- Mock divergences: the mock keeps its own conventions (bare error codes, 400 for `invalid_request`, `state_read`/`task_invoke` purposes); the bridge-contract mock suite carries 149 xfails, each with a divergence id. The mock does not simulate `release_settings`, `/version` or export.
- Annex D aliases (`mode`, `seed_manifest_ref`, `agent_id` on arms) are deprecated for one release and disappear in the next contract revision. `evaluation_context_ref` (`evc-` formula) exists only in ADR 0011 and `contract.json`; the Rust client must copy it exactly, including the `|` rule. Arms `deadline` is format-checked only.
- Agent Core 409 `idempotency_conflict` is ambiguous (different body vs same key in flight); #82 retries within `lease_ttl` by matching the text `sigue en curso` until Core ships a distinct code. F-04 (run/transcript read isolation) is only partially fixed upstream; service/builder principals depend on the `AuthzPort`.
- Platform exporter: meta-events (`exporter.*`) collide with the section 24.2 `platform_event` DTO until a discriminator revision (platform-contract 1.1.0 ready, Codex routes by prefix). Source-completeness gaps documented: backfill requests lost after exporter state loss, permanently missing sequence, `start_sequence=0`. Event payload shapes are simulator assumptions until Product publishes them.
- Console: field names of several debug routes and the 410 body shape are provisional until Codex's control-api publishes them; several screens still use the legacy client and show a `provider-partial` notice. Remaining LOW items are listed in `debug-console/docs/journal-c-0002-review.md`.
- Evidence honesty: nothing here is a joint H4 run, a real-profile result or an improvement claim. Doubles in use: scripted llm-gateway, control-api, lab-broker, bank, ingest, codex-standin, human-issuer, fixture API/SSE, mechanism_proxy judge. `mypy --strict` is not clean (agent_core ships no `py.typed`).
- infra: nothing applied, no AWS call; module tests use mock providers. Secret names and the Cloud Map name `core-runtime` are unconfirmed against the agent-core slice.

## 6. Blocked on Codex

- **control-api HTTP surface.** The Rust `control-api` service (session/CSRF/Problem envelope, evolution routes, debug routes, SSE, decisions with `HumanAuthorizationPort`) does not exist yet. The console runs on fixtures and the stand-in; `provider=http` is a config switch away once it exists; e2e-core and demo use the Codex stand-in.
- **E0 -> Core flow mapping.** The engine side that turns an E0 finding into a `ChangeSpec`/`DraftPlan` and calls the bridge (dry-run, invoke, admission, arms) is Codex's; the Rust DTOs must be reconciled against `core-bridge/wire/agent_core@894fa65` and `bridge-contract/` (the Rust client should be generated or checked against that pack). Item AM-24 (run ids 6 or 9, not 7), AM-32, AM-38..AM-42, AM-45 still await Codex confirmation.
- **Codex work not published.** Codex's environment cannot reach GitHub, so some of its branches are local only (journal CX-0165..CX-0176: P1 explanation read model `f7df465`/`a848968` unpushed, P2 `ValueModel@1` in progress). Until those are carried to GitHub by the user, no joint run can include them.
- **CI coverage.** `.github/workflows/ci.yml` is Rust-only; Python suites, console checks, bridge-contract and Terraform module tests run only locally. A workflow change is Codex-owned.
- **Joint H4 and platform source:** the exporter -> control-api ingest, PL-C1 adapter (`platform_live` in the U29 path) and the E2E of PL-L6 need Codex's ingest endpoint or its stand-in.

## 7. Blocked on others

- **Agent Core team** (relay file `AGENT_CORE_RELAY_FOR_USER.md`): PRs #23/#24/#28 not on `main`; F-04 partial; distinct 409 code for in-flight idempotency (N8-02); export cursor caveats (N8-03); rolling-deploy safety (N8-04); `contracts/VERSION` bump (N8-08); release id change note (N8-07); `resolve_ports` should read `lang_thresholds` with `getattr` (found in bump 3); builder tools / `registry-e2e` overlap question (c814c2b); bridge schema DDL ownership, Fargate key delivery (now covered by `ephemeral_volumes`), exporter SG, secret layout, single `pulso-core-runtime` service name, who records `pin_manifest_digest`.
- **Product team** (relay via the user): the nine questions in `PLATFORM_DATA_MODEL_IMPACT_CLAUDE.md` section 7 (read mechanism, payload schema per `event_type`, `sequence` contiguity, `complaint_id`, AI-layer facts, demo marker, `teams` timeline, retention). Until answered, `platform_live` shapes are simulator assumptions.
- **Cloud/security owners:** OIDC provider and subjects, state bucket/bootstrap, controlled egress profile, KMS policy, alarm destinations (infra OPEN_GAPS). Nothing can be applied without them.
- **llm-gateway team:** first tagged image and digest, per-consumer policy, `Idempotency-Key`, error `code` field (questions Q1-Q15 in the relay file).

## 8. Recommended next steps (in order)

1. Land the `c814c2b` pin bump PR (branch `claude/r4-pin-c814c2b`); it carries the `synthesise_args` fix. Use ADR 0012 (ADR 0011 is now Annex D alignment). Then update `contracts/agent_core/pin.json` and the Dockerfile `CORE_SHA` with the Codex-owned files through the journal.
2. Carry the repo-doc follow-ups of section 10 in one docs PR per repo.
3. Ask the user to relay `AGENT_CORE_RELAY_FOR_USER.md` (sections A-C) to the Agent Core team and section D to the Product team.
4. Rust client work for Codex against `bridge-contract/`: first the dry-run and alias reads, then invoke/admission/arms; use the golden fixtures and conformance kit.
5. Console operator screens (backoffice plan phases 1-2) on fixtures, then flip to `http` when control-api publishes the contract (`gen:contract` after Codex's `contracts/product/`).
6. Joint H4 with the Codex assembly and the real control-api; exporter against the real ingest.
7. infra: OIDC push roles for the new ECR repos, `core-migrate`, sweep and alarms for the new services; request CI coverage for module tests.
8. Remove the merged Claude worktrees and containers listed below once the user agrees.

## 9. Worktrees and containers still in use (read 2026-10-04)

| Item | State | Action |
|---|---|---|
| `worktrees/improvement-engine-claude-a` (`claude/r4-pin-c814c2b`) | **In use** by the pin-bump agent; 2 local commits, uncommitted journal and `.reports/exporter-report.json` | Keep until the PR is open |
| `worktrees/improvement-engine-claude-c` (`claude/c-console-seam`, `b2d1ef1`) | Merged via #85; clean | Can be removed |
| `worktrees/improvement-engine-claude-u` | Not a registered git worktree (stale directory copy, no `.git`) | Can be deleted after user check |
| `worktrees/infra-claude-u` (`claude/u-infra-bridge-exporters`, `98f8a36`) | Merged via #26; clean | Can be removed |
| Branch `claude/pl-platform` (`76c6252`) | Merged via #80, #81, #84 | Local branch can be deleted |
| Podman machine `pulso-dev` (rootless) | Running | Ours; keep. `pulso-codex` is Codex's, untouched |
| Container `pulso-claude-r4-pg` (postgres:16-alpine) | Up, belongs to the pin-bump agent | Remove when that agent finishes |
| Containers `u-rev-console` (Exited), `u-rev-api` (Created) | Leftovers of the console review | Can be removed |
| Containers `pulso-local-postgres-1`, `pulso-local-localstack-1` | Created, Codex's local stack | Not ours, untouched |
| Images on `pulso-dev` (`pulso-core-runtime:*`, `pulso-platform-sim:*`, `pulso-platform-exporter:*`, dangling) | About 465 MB each for the runtime, accumulated per pin/commit | Prune old tags after the bump PR |

## 10. Repo doc follow-ups (checkouts NOT edited; a later PR per repo should carry them)

The local checkouts are stale (`improvement-engine` on `feat/l0-engine-foundation`, `infra` on `feat/U01-config-and-tool-probes`), so the list below was derived from `main` read through `gh api`.

improvement-engine:
1. `README.md` ("Current slice") stops at Layer 0 / U07 and the local compose stack; it never mentions `core-bridge/`, `bridge-contract/`, `platform-contract/`, `platform-sim/`, `platform-exporter/`, `agent-core-assets/`, `local-identity/`, `local/core`, `e2e-core/`, `demo/` or `debug-console/`. Add a short "Python integration packages" index with one line and a link per directory.
2. `core-bridge/README.md`: pin text and paths still say `789d6c8` (`wire/agent_core@789d6c8/`, "SHA `789d6c89...`"); main is at `894fa65` (the bump to `c814c2b` will change it again). ADR list stops at `0008`; add `0009` key delivery, `0010` pin `894fa65` (dual-pin), `0011` Annex D alignment (and `0012` after the bump). Journals list stops at `claude-0009`. Mention `bridge-contract/` and the dry-run/alias routes.
3. `debug-console/docs/README.md` "Known gaps vs plan 17.3.7" is stale: it does not describe the typed `DebugApi` seam and providers (#85), the Sources view (#80) or the demo panels (#77), and "No CI job runs these yet" should point at the Codex-owned workflow request.
4. `docs/gaps/OPEN_GAPS.md`: add rows for (a) Rust client against `bridge-contract/` (owner Codex), (b) control-api HTTP surface for the console (`provider=http`), (c) CI coverage for Python/console/bridge-contract suites (workflow is Codex-owned), (d) Product answers for `platform_live` payload shapes.
5. `platform-sim/README.md` is current on the pin (`894fa65`) but does not list `platform_live/` in its table (it has its own README); add a row. `platform-sim` mock counts (route table 18, 228 tests) should match #82/#86 evidence (246 passed at #86).
6. `CLAUDE.md` is a one-line pointer and `CONTEXT.md` is 7 lines: no change needed, but `AGENTS.md` (Codex-owned) should list the new top-level Python directories as Team Claude paths if it keeps an ownership table.
7. ADR index: `docs/adr/` (0001-0005) and `core-bridge/docs/adr/` (0001-0011) have no index file; add a one-page index linking both series and noting that the next core-bridge ADR is `0012`.

infra:
1. `README.md`: "Modules `workload`, `workload_iam`, `ci_roles` and `auxiliary_roles` ... are not yet wired into `envs/*`" is stale: `engine_platform` (#23) and `bridge_services` (#26) are wired into `staging` and `prod` behind switches that default off. Add short "Engine platform workloads" and "Bridge and exporter services" sections, and mention ADR 0006 once it is accepted (the README is intentionally untouched while the ADR is only proposed).
2. `docs/architecture/deployment-status.md`: the status matrix has rows for the Core, LLM gateway and data pipeline workloads but none for engine platform (`control-api`, `worker`, `migrate`, `sandbox-lab`) or `bridge_services` (`core-runtime`, `core-exporter`, `platform-exporter`); add both ("declared, off by default, nothing applied"). The Agent Core section still says Core has no image/ECR; refresh against `ecr` module and #26.
3. `docs/gaps/OPEN_GAPS.md`: the last row "pulso-core-runtime image key delivery" says signer and exporter key files have no Fargate delivery path; #26 added `ephemeral_volumes` and improvement-engine ADR 0009 materialises keys from env, so reduce it to the remaining item (images must pre-create state dirs owned by uid 10001). Add rows for: OIDC push role for the new ECR repo, `core-migrate`/sweep/alarms for the new services, CI coverage for module `terraform test` files, and the unconfirmed secret names and Cloud Map name `core-runtime`.
4. ADR index: `docs/adr/` has 0001-0006 and no index; add one. `AGENTS.md`/`CONTEXT.md`: no stale merged-work statements found.
