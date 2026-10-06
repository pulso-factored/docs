# Plan C: risks, ownership and two-team parallelism (path to a REAL, durable Pulso engine)

Planner C, lens "RISKS, OWNERSHIP AND TWO-TEAM PARALLELISM". Evidence date 2026-10-04 (improvement-engine main `41492cb`, infra `dab52ab`, agent-core `c814c2b`). Read: brief; `estado-spec/00..03`; plan V3 sections 5-8, 14, 17.8, Annex D; relay file; llm-gateway adoption analysis; journal CX-0161..0182 and CL-0035..0037. Nothing was executed; hours are my estimates, not measurements. A "session" = one working day-equivalent of the Claude orchestrator running 3-5 subagents (about 6-8 focused hours on the critical lane, 15-25 agent-hours of throughput).

## 0. Headline

1. The whole gap is one chain: **Rust client + Rust-hosted HTTP surface (binding callback, broker, ingest, API) + a pipeline executor + an E0-finding-to-Core-artifact path**. Everything else (Core runtime, assets, exporter, issuer, console, goldens) exists on the Claude side and is exercised only through a Python stand-in.
2. Three facts shape the division of work: (a) Codex cannot reach GitHub or Podman, but **it shares the disk with Claude**, so Claude can be the publisher and the live-integration runner without user file transfers; (b) the hot path needs a live Core and a live gateway, which only Claude's side can run; (c) Codex's strength (pure, offline-testable semantics behind ports) is exactly what the middle of the chain needs, not its seams.
3. Proposed division: **seams are written by Claude** (new crates `core-client`, `control-api`, `engine` executor shell, integration-tested against the real Core); **semantics by Codex** (pure reducers, gates, compilers, adapters inside `crates/core`, offline, against goldens); joined by the existing Rust ports plus a new **golden transcript** contract. This needs an explicit ownership amendment from the user (decision D1, section 9).
4. Honest headline estimate (focused hours, both teams, including 1-2 review loops): T1 about 110-150 h, T2 about 140-200 h, T3 about 80-120 h, T4 about 50-80 h (conditional on user approvals). Elapsed: T1 5-7 sessions after unblock (50% confidence), T2 +6-9 (35%), T3 +4-6 (35%), T4 +3-5 (25%).
5. Real parallelism is high only until the first integration run of the executor (about session 3). After that the path is serial (integrate, debug on real Core, real-model quality loop) and limited by one Podman machine, one Cargo slot and about 5.9 GB free RAM of 15.7 GB.

## 1. Target definition: tiers of "real" (observable acceptance, honest labels)

Each tier is demonstrable on its own and carries a `target/sha/doubles[]` evidence report (existing convention). Nothing is called "autonomous" until the trigger is not a manual command.

| Tier | Name | What exists | Observable acceptance (one run an auditor can repeat) | Labels that remain |
|---|---|---|---|---|
| T0 | Today | Libraries + local-sim CLI; Python stand-in over real Core; scripted LLM | `demo/run.ps1` runs; every step labelled stand-in/simulated | all |
| T1 | Rust-driven, real Core | `pulso-engine run-once` (Rust) drives sensors, scout, verifier, builder_design, compile, dry-run, writer, native evaluation, Pulso gate, bounded revision, human approval, staging publish, alias read, ingest of the next batch and a second investigation, against the `real_local` Core stack. Rust hosts binding callback, broker and ingest on localhost | Steps 1-10 each show a Rust receipt id; the Python stand-in is absent from the process tree (a test checks `doubles[]` and the process list); the E0 finding is either mapped by an evidence-bound builder output or honestly `unlinked`; one negative path per boundary (stale hash, bot approve, lost response, binding timeout) | LLM = recorded-replay of real model output with provenance (or scripted if no key); human = local issuer `auth.simulated=true`; trigger = `manual_command`; jobs = in-memory; suite = assets hand-written; no AWS |
| T2 | Durable, autonomous, real models | `pulso-engine serve` (worker + scheduler + control-api) on PG16 with leases/SKIP LOCKED; ingest creates the trigger; real LLM through a local llm-gateway; console `provider=http` on the real API/SSE; decision made in the console; memory durable; Rust CoreEvalPackage emitter | `kill -9` of the worker mid-run resumes without duplicate effect; a new exporter batch starts a run with nobody issuing a command; one live scout/verifier/builder cycle with real tokens and a USD ledger; console shows the Rust-produced timeline | Jev not exercised unless agent-core #28 is on main; IdP = local issuer; hosted CI still red (local gate); platform = simulator |
| T3 | Continuous, hardened local | Cadence-driven campaign, at least 3 signal families, `platform_live` adapter on simulator, CAP-37/64, OTel + alarms firing/resolved locally, restore/restart/chaos smoke, retention rules, runbooks, rollback drill on the local staging alias | 24 h unattended soak: N cycles, budget respected, alarms fire on injected faults, restore proves the memory head | Real Product data only if Product answers; AWS not used |
| T4 | Deployed staging | Images by digest, Terraform apply of `engine_platform` + `bridge_services` in staging, OIDC/CD, smoke, rollback | Plan reviewed by the agent-core infra owner; apply by the user; smoke green; same demo against staging | Gated by user approvals (U-8); real IdP only if CAP-44 unblocked |

Dishonest-demo guard (from the synthesis): scripted LLM or planted-column judge shown as discovery; mapping keyed to the winning category; scripted approval shown as human; stand-in output shown as engine output; local-green quoted as hosted CI.

## 2. Backward chaining from the ten demo steps

Notation: [E] usable on main, [P] partial, [X] absent. "Tier" = first tier where the step can be honestly real.

| Step | Immediate prerequisites | Absent pieces (smallest increments) | Tier |
|---|---|---|---|
| 10 new observations, memory published/contradicted, new investigation | exporter [E] -> **Rust ingest route** [X] -> observation store [P] -> trigger -> memory publish [P] -> steps 1-3 again | ingest route (A-2); successor trigger in reducer (B-1); memory file-backed in T1, PG in T2 (0005 outbox, B-7) | T1 file-backed, T2 durable |
| 9 staging confirmed, alias receipt | alias read via client; approve/publish (8) | alias read and readback check in executor (A-3) | T1 |
| 8 human authority fixes operation/hash | decision command; `waiting_human_approval` [X]; local issuer [E]; Core approve/publish [E] | authority state machine (B-4); JWS dispatch from Rust (A-1); console panel on real API (C-3) | T1 CLI/file prompt, T2 console |
| 7 failure -> bounded revision | eval report parsed [P: bridge persists 409 body]; builder re-invoke with diagnosis [X] | reducer revision loop with budget (B-1); builder prompt with failure facts (C-1) | T1 |
| 6 two gates, base vs candidate | native evaluation inside writer task [E]; eval suite for the candidate [hand-written assets]; Pulso gate U27 [X]; sealed plan U20 [P]; bank = double | CombinedGate (B-3); suite emitter U47 (B-5, T2); arms via `arms/run` (A-1) | T1 partial, T2 full |
| 5 concrete change, versions, diff | ChangeSpec -> DraftPlan -> dry-run [bridge E] -> writer commitment -> receipts [Python E] | Rust compile for the kinds the builder emits (B-2); client calls (A-1) | T1 |
| 4 opportunity + alternatives incl. `do_nothing` | scout/verifier facts; WorkflowBridge U16 [P]; **E0 finding -> Core artifact has no mapping** | the intellectual gap: let the builder design the artifact from signal evidence + ReadBase instead of a pre-seeded catalogue (CX journal 2026-10-03T21:12Z); validate in Rust; keep `unlinked` honest (B-2 + spike S-MAP) | T1 |
| 3 adaptive scout + separate verifier | invoke [Python E]; **binding callback** [X in Rust]; **broker lab/wiki/authorizations** [X in Rust, double today]; real model [X] | A-1 + A-2 + gateway local (D-1) + recorded replay (D-2) | T1 recorded, T2 live |
| 2 signal families, discarded candidates | sensors [E as library]; not job-driven | executor calls sensors and persists receipts (A-3, B-1) | T1 |
| 1 snapshot/E0/observations wake the engine | trigger producer [X]; E0 adapter [E] | T1 `run-once --trigger snapshot_available` labelled manual; T2 ingest/cadence -> job (A-6) | T1 manual, T2 real |

True critical path (backward-derived, serial links only):

`A-1 core-client  ->  A-3 executor shell (needs A-2 and B-1 interfaces)  ->  first full run on real Core (debug loop)  ->  demo swap C-2  ->  real-model smoke D-3`

Three side chains must land before the first full run without being on the shell's own code path: **A-2** (the binding callback is mandatory before any bridge effect), **B-1** (the vocabulary the shell executes), **B-2** (builder output -> compile). Everything else (B-5, B-6, B-7, C-3, E-*, F-*, G-*) is off the T1 path.

Nominal vs real parallelism:

| Claimed parallel | Real? | Why |
|---|---|---|
| A-1 / A-2 / B-1 / B-3 / B-4 / C-1 / D-1 | Real until first integration | disjoint crates/files; offline- or fixture-testable |
| B-2 beside the A lane | Real only once a **builder output corpus** exists | Codex cannot validate the E0 -> artifact path without real builder_design outputs; Claude must produce them first (spike S-MAP, needs a key or authored-labelled fallback) |
| Several Rust implementers | Nominal | one Cargo slot (journal: serialized `CARGO_BUILD_JOBS=2`), 5.9 GB free with the Podman VM resident |
| Several E2E runs | Nominal | one Podman machine `pulso-dev` (cgroups-disabled workaround), one PG16, one Core runtime; needs a heavy mutex |
| Cross-team reviews | Real and cheap | read-only, no cargo needed |
| Codex "supports the rest" while frozen | None until unfreeze | CX-0180; plan with defaults (section 8) |

## 3. Rust/Python split: what lives where, what moves

### 3.1 Evaluation of "Python-hosted durable worker + control-api wrapping Rust libraries"

| Criterion | Pure Rust service (spec) | Python host over Rust libs (PyO3 or CLI) |
|---|---|---|
| Spec wording | V3: "Rust conserva el control plane, procesamiento de datos, sandbox, gates y persistencia Pulso"; plan section 5 gives Codex the new app/worker/control-api; "Codex no importa Python" | Contradicts both; needs spec and plan amendments by owning teams |
| Reuse of about 50k lines of Rust domain code (jobs reducer, quota, receipts, gates, sensors) | Direct | PyO3 on Windows with Python 3.12 (runtime) vs 3.13 (host): wheel and panic-across-FFI hazards; or CLI-per-step with serialization and no shared state |
| Core call path | Rust -> HTTP/JWT -> bridge (CAP-02/05) | Could call the bridge in-process and skip the JWT hop, but then the bridge is no longer a separable service (breaks ECS shape, CAP-24/60) |
| Durable state | One owner (Rust, `migrations/`) | Two owners unless Python writes PG directly, re-implementing the U06 reducer and fences |
| Seam volume to T1 | A-1 + A-2 + A-3 about 40-58 h | Python shell about 25-35 h plus CLI/PyO3 adapters for each Rust step (15-25 h) plus later rewrite to satisfy the spec |
| Who can integration-test | Claude (live Core) | Claude |

Verdict: keep Rust. The Python-hosted variant saves little on the real critical path (the Rust semantic pieces are needed either way) and creates a second source of truth for job state. Two cheap mitigations:

1. **Pure-step rule.** Every semantic step in Rust is a pure function `(JSON in) -> (JSON out)` first and a `pulso-engine step <name>` subcommand second (A-4). This keeps a Python-hosted fallback open at near-zero cost and gives the Python e2e a black-box seam.
2. **Tripwire.** If A-1, A-2 and A-3 are not GREEN against the real Core by the end of session 4 of the Claude critical lane (about 30 focused hours), fall back to F-PY: the Python stand-in orchestrates and calls `pulso-engine step` for sensors/compile/gate. Labelled "Python-hosted shell, Rust semantics". Decision owner: the user (D3).

### 3.2 Per-CAP half placement (which half lives where; changes vs the plan)

| CAP / unit | Python half (Claude) | Rust half | Decision | Tier |
|---|---|---|---|---|
| 01,02,03 endpoint profile, HTTP client, classifier | n/a | `crates/core-client` | Claude writes (seam); sync `ureq`, no tokio | T1 |
| 04,05,06 credentials, service JWT, probe | issue/verify done | Ed25519 signer + probe in `core-client` | Claude; claims exactly per ADR 0011 (`sub=worker:<id>`, `job_id`) | T1 |
| 07 entities-by-release | route absent | none | **Cut**: Annex D.2 says the bridge materializes the candidate from its own store; Rust does not need entities | cut |
| 08,16,17 alias, dry-run, closure compare | done | client calls; compare `candidate_hash` | Claude | T1 |
| 09,25,26,27,28,30 invoke, pin, bind, facts, reconcile | done | client + **binding callback server** | Claude (A-1 client, A-2 callback) | T1 |
| 29 lab/wiki ToolDefs backend | executors done; broker is a double | broker routes over `local_lab`/`wiki_scratch` | Claude writes the HTTP wrapper (A-2) calling Codex library functions behind traits | T1 |
| 11,12 pinned wire, JCS hash parity | wire dir, vectors | Rust DTOs + hash parity | **Defer to T3**: dry-run `candidate_hash` is authoritative (spec D-9, 31.4.5); parity is verification debt, 4-6 h | T3 |
| 13,14 ChangeSpec -> `changes[]`, entity kinds | n/a | `change_compiler.rs` extension | Codex (B-2); T1 kinds = what the builder emits (Flow add/replace, Prompt, DecisionModel); others `unsupported_kind` honestly | T1 |
| 15,18,19 cascade prediction, docs, limits at compile | Core via dry-run | none | rely on dry-run | cut |
| 21,22 eval_suite from ScenarioCase, queues | hand-written assets | emitter (U47) | Codex B-5; T1 keeps assets suite labelled `suite_source=assets_handwritten`; Rust emitter T2 | T2 |
| 34,35 exporter -> ingest | exporter done | ingest route + store | Claude route (A-2) over a Codex store trait | T1 |
| 37 release correlation (U50) | exporter emits `release.*` | correlation in Rust | Claude exporter delta (C-4), Codex consumer (B-8) | T2 |
| 38,39 evaluate capture, combined gate | capture done | CombinedGate (U27) | Codex B-3 | T1 |
| 43,45 local human step-up, approve/publish | issuer done | `HumanAuthorizationPort` client + dispatch | Claude A-1 client, Codex B-4 state machine | T1 |
| 44,62 AWS IdP, joint deploy | n/a | n/a | blocked by decisions D-5/D-12 | T4 |
| 64 traceparent, known_gaps | minimal | emit | both sides | T3 |
| U06 durable jobs, U05 quota, U07 activity | n/a | PG adapters | Codex B-7 writes offline; **Claude executes the ignored PG tests** | T2 |
| U24/U32 console on real API | console done on fixtures | debug routes + SSE | Claude wrappers (A-5) over Codex read models | T2 |

Rework avoided: no Rust hash/prediction on the T1 path; no entities route; no tokio before T2; the only allowed Python/Rust duplication is the golden vectors.

## 4. Work packages

Hours are focused agent-hours including 1-2 adversarial review loops (strict TDD; reviewer distinct from author). Ranges are roughly 80% intervals. Locations are under `improvement-engine` unless stated. Owners: CL = Claude, CX = Codex, USR = user, EXT = external team.

### 4.1 Stream S: enablement (no product code; unblocks everything)

| ID | Owner | Hours | Depends on | Content | First RED / acceptance |
|---|---|---|---|---|---|
| S-01 | CL | 1-2 | none | Local bare mirror `D:\.codex\factored\mirror\improvement-engine.git` as a file remote. Claude pushes a `main` snapshot and `integration/real-v1`; Codex fetches from the path (no GitHub) | a Codex worktree fetches a Claude commit offline |
| S-02 | CL | 1-2 | S-01 | Cargo offline dependency admission: add `ureq`, `ed25519-dalek`, `tiny_http`, `uuid` and their transitive deps to the workspace, `cargo fetch --locked` into the shared registry; spike SP-B proves a Codex worktree builds with `--offline --locked` | build green offline in a Codex worktree |
| S-03 | CX | 1-3 | USR unfreeze | Commit (not push) each dirty worktree's WIP to a local branch with a one-line manifest (what, tests passing, overlaps) | manifest in journal; branch heads recorded |
| S-04 | CL | 3-5 | S-01, S-03 | Publisher role: triage S-03 branches (6.2), cherry-pick onto fresh `main`, run the local gate, open consolidated PR W1 preserving Codex authorship | PR body carries the local evidence digest |
| S-05 | CL | 3-5 | none | `scripts/verify-local-all.ps1`: Rust gate + `core-bridge` + `bridge-contract` + `e2e-core` (opt-in Podman) + `debug-console` (`npm ci/test/build`) + `platform-*` + infra `terraform fmt/validate/test`; one JSON receipt. Replaces hosted CI as merge evidence until Actions is fixed | receipt lists suites as passed/failed/not_run |
| S-06 | CL | 1 | none | Heavy-gate protocol: `Global\pulso-heavy` mutex used by cargo build/test, Podman E2E and Playwright; preflight `insufficient_memory` if free RAM < 3 GB; per-lane `CARGO_TARGET_DIR` | script used by S-05 |
| S-07 | CL | 1 | none | Journal tag protocol (5.4) and 1-page strawman of pipeline commands (feeds C-2) | tags greppable |
| S-08 | USR | 0.5 | none | Answer U-1..U-9 (section 8) and D1-D3 | answers or defaults taken |

### 4.2 Stream A: seams in Rust (Claude; new crates, disjoint from Codex files)

| ID | Hours | Depends on | Content | First RED | Real deps |
|---|---|---|---|---|---|
| A-0 | 2-3 | S-02 | Workspace skeleton: members `crates/core-client`, `crates/control-api`, `crates/engine` (bin `pulso-engine`: `run-once`, `step <name>`, later `serve`); lint config; features | `cargo metadata --locked` lists members; one smoke test per crate | none |
| A-1 | 12-18 | A-0 | `core-client`: endpoint profile (reach, probe, pin `c814c2b`/contract 1.3.0); `ureq` with timeouts; response classifier (200-with-violations is not success; unknown shape closed; timeout after a mutable dispatch = `unknown`, never a blind retry); Ed25519 service JWT (`kid`, `jti`, `exp` <= 5 min, `sub=worker:<id>`, `job_id`); `Idempotency-Key` + `request_digest` (JCS of body); typed calls: version, invoke(stage), read run/facts, reconcile, dry-run, alias read, admissions, `arms/run`, credentials issue, approve/publish/promote with the JWS held only in memory; implements the existing ports `CoreTaskPort`, governed writer, native-evaluation admission. Retires `SUPPORTED_CONTRACT_SHA=53e729d`/0.5.0 | RED 1: `bridge-contract/examples` goldens decoded and classified (same key + other digest = Conflict). RED 2: a live test where the real bridge accepts our JWT | Core image on `pulso-dev` (Claude only) |
| A-2 | 12-18 | A-0, S-02 | `control-api` minimal, `tiny_http` + thread pool: JWT verify (aud=control-api, scope binding/observations, `jti` replay); `POST /internal/v1/core-task-bindings` (CAS on the external-command row); broker group (`/artifacts/{id}`, `/authorizations/check`, `/lab/sessions*`, `/wiki/read\|explore\|transform`, `/sandbox/*` thin over U26); exporter ingest with ACK after commit. Handlers call Codex library functions behind small traits so HTTP code holds no domain logic | RED: the `e2e-core` binding/broker/ingest black-box tests run unchanged against this server instead of `e2e-fixtures`; the double and the real server must pass the same file | PG16, Core image |
| A-3 | 14-22 | A-1, A-2, B-1 interface | `engine` executor shell `run-once`: loads RunConfig, drives the reducer (B-1) by executing its commands (invoke, dry-run, write, evaluate, approve, publish, alias read); persists each command before dispatch; emits the NDJSON/world feed the console already consumes and `doubles[]`. T1 job store is in-memory with a file snapshot (a crash loses at most the current command, reconciled via the bridge) | RED: golden transcript `scout_completed -> verifier invoke` replays through the shell with a fake bridge; then live | Core image; gateway or replay |
| A-4 | 4-6 | A-3 | `pulso-engine step <name>` pure-step subcommands with JSON schemas under `contracts/engine-steps/` | step output equals the in-process call on the same fixture | none |
| A-5 | 10-16 (T2) | A-2, B-7 | Debug routes + SSE (`id=sequence`, 410 resubscribe, 202 commands) over Codex read models (`debug_console.rs`, `run_timeline_v2.rs`). Spike first (2 h): is `tiny_http` SSE adequate? If not, axum/tokio in this crate only | RED: `debug-console` conformance tests run against the real API | PG16 |
| A-6 | 16-26 (T2) | B-7, A-3 | `serve`: worker (claim loop, leases, fences, SKIP LOCKED), scheduler (cadence, coalesce two triggers into one root job), restart recovery, lost NOTIFY recovered by polling, admission quota/grant | RED: two triggers -> one root job; kill -9 mid-command -> one effect | PG16 |

### 4.3 Stream B: semantics in Rust (Codex; inside `crates/core`, offline, against goldens)

All B packages are testable without GitHub or Podman except B-7. They add modules and do not change existing port signatures (a `[CONTRACT-CHANGE]` stanza first if unavoidable).

| ID | Hours | Depends on | Content | First RED | Notes |
|---|---|---|---|---|---|
| B-1 | 10-16 | S-03 | `pipeline.rs`: pure reducer `(state, event) -> (state, commands[])` for sense, scout, verify, opportunity (incl. `do_nothing`), builder_design, compile, dry-run, write, evaluate, gate, revise (budget N), waiting_human, publish, observe, successor. Absorbs the dirty `p2-u12-u13-runner-compose` and `u13a` work where sound. Publishes `contracts/pipeline/transcripts/*.json` | RED: transcript "scout completed -> verifier command with a distinct actor" fails before implementation | Publishes first (contract C-2) |
| B-2 | 12-20 | S-MAP corpus, B-1 | E0 finding -> Core artifact: validate builder `pulso_change_spec` against evidence (no invented refs, alternatives incl. `do_nothing`); extend `change_compiler.rs` to Flow add/replace, Prompt, DecisionModel `changes[]`; route stays `unlinked` unless the builder output is evidence-bound; no category-keyed mapping, tested by renaming/permuting the winning category. Folds in dirty `e0-core-draft-binding` | RED: renamed-category fixture gives the same route and different support | Highest-risk package |
| B-3 | 8-14 | S-04 (u26-r2 seed) | U27 `CombinedGate` + `ImprovementEvidence` over sealed U20 plan + native report + paired scenario results; unsafe/unknown/low power block; native `pass` never substitutes the Pulso gate | RED: native pass + unknown improvement = not eligible | Pure |
| B-4 | 6-10 | B-1 | U21 authority: `DecisionRequest`, `waiting_human_approval`, intent -> operation+hash binding, TTL, kill switch; fail/rebase needs a new candidate | RED: no human -> stays `evaluated` | Pure |
| B-5 | 8-12 (T2) | B-2, C-6 | U47 `CoreEvalPackage` emitter from `ScenarioCase` incl. `queue_order_sensitive`; output validated by Claude with `agentcore validate` | RED: shape equals a Core-accepted suite fixture | Validation by CL |
| B-6 | 10-16 (T2/T3) | S-04 (pl-c4) | PL-C1 `platform_live` adapter on platform-contract 1.1.0, PL-C2 capability profile, PL-C4 source policy (dirty `pl-c4`), PL-C5 stop-at-insight, PL-C6 spec text | RED: unsupported family -> `not_evaluable`, not zero | Offline against `platform-sim` fixtures |
| B-7 | 14-24 (T2) | S-04 (0005) | PG adapters: job store (`pulso_jobs`), quota window, temporal successor outbox (0005), memory head; `migrations/0006+` | ignored PG tests written by CX, executed by CL on `pulso-dev` | Only B package needing Podman |
| B-8 | 10-18 (T3) | A-6 | U50 release-correlation consumer, U31 detector evolution, U32 diagnosis SQL, U34 durable run control | per unit | |
| B-9 | 3-5 per wave | any | Independent adversarial reviews of Claude seam PRs (read-only) | n/a | Standing duty |

### 4.4 Stream C: Python, console, local stack (Claude)

| ID | Hours | Depends on | Content | First RED |
|---|---|---|---|---|
| C-1 | 10-16 | D-1 | Real-model readiness: prompts/Flows in `agent-core-assets` for scout/verifier/builder_design on a real model; `SpendMeteringGateway` fixes (usage_known, failed-call spend, over-cap, pre-reservation); strict gateway mode; outage reported as `unavailable`, not `escalate(low_confidence)` | RED: gateway outage is not low_confidence |
| C-2 | 6-10 | A-3 | Swap `e2e-core` and `demo/` to the Rust binary; keep issuer, exporter, console; new `doubles[]`; negative suite | RED: `demo-report.json` has no stand-in step among 1-9 |
| C-3 | 8-14 (T2) | A-5 | Console `provider=http` on the real API; decision panel; Sources view on ingest | Playwright run against the real API |
| C-4 | 6-10 | A-2 | Exporter CAP-37 `release.*` and CAP-64 `traceparent`; `pulso-bootstrap core` CLI + `bootstrap-report.json` | RED: batch carries release correlation |
| C-5 | 6-10 (T2) | A-6 | Joint local compose `scripts/dev.ps1 up --with-core` with `pulso-api`, `pulso-worker`, `core-runtime`, `platform-exporter`, `debug-console`; `doctor` aggregator | `doctor` green on a clean clone |
| C-6 | 2-3 | B-2 | Core-accepted eval suite goldens for B-5 | fixtures validated by `agentcore validate` |

### 4.5 Stream D: real models and cost (Claude + user)

| ID | Hours | Depends on | Content | Acceptance |
|---|---|---|---|---|
| D-1 | 2-4 | U-4 key | Build llm-gateway from source at the pinned commit (Go image, about 33 s), run on `pulso-dev` with consumer tokens and one provider alias; health check declared explicitly | authenticated empty-body probe returns 400; one `generate` returns cost |
| D-2 | 3-5 | D-1 | Recorder/replayer in the `core-bridge` llm adapter storing `(prompt digest, inputs digest, output, model, tokens, cost)` with provenance; replay refuses on digest mismatch; label `llm=recorded_real@<date>` | replay is byte-stable; automated suites use replay only |
| S-MAP | 4-8 | D-1 or D-2 | **Spike, first**: feed the existing E0 SignalBundle (`output/e0-current-main-explained-2026-10-04`) to the real builder_design stage on real Core with a real model; keep outputs as a corpus for B-2. Without a key: an authored-by-Claude corpus labelled `authored_not_model`, valid for pipeline mechanics only | 3+ outputs with provenance, valid or invalid |
| D-3 | 2-4 | A-3, D-1 | Live smoke of scout/verifier/builder through the gateway with a USD ledger; ceiling enforced by Claude-side reservation | ledger equals gateway sum |
| D-4 | 4-6 (T2) | D-3 | Cost governance: per-run/per-day ceiling in `RunConfigRevision`, circuit breaker on repeated `refused`/`invalid_output`, unknown cost blocks the claim | breaker test |

### 4.6 Streams E-G (T2-T4)

| ID | Owner | Hours | Tier | Content |
|---|---|---|---|---|
| E-1 | CX+CL | 8-12 | T2 | Durable memory end to end: wiki diff -> lint -> PG/S3 CAS -> ingested observation -> successor -> use/contradict/forget; restart keeps the head |
| E-2 | CL | 6-10 | T2 | Rollout/rollback of a published proposal on the local staging alias: rollback receipt, readback, drill test |
| E-3 | CX | 6-10 | T2 | Original-dataset profile separate from E0 (namespaces, no label/future leakage), at least 2 families each |
| F-1 | CX+CL | 12-20 | T3 | Observability: Rust OTel emission, span links API -> queue -> worker -> Core, alarm table (stalled work, budget breaker, evidence gaps, API errors) with firing/resolved proven locally |
| F-2 | CL | 8-14 | T3 | Restart/chaos/restore: PG restart, worker kill, collector loss, backup/restore of Pulso PG and Core DB, 24 h soak |
| F-3 | CX | 6-10 | T3 | Retention and privacy: rules table (E0 local only; no hosted model sees E0 text unless Product/user allow), retention job, redaction tests; incident runbook skeleton |
| F-4 | CX | 10-16 | T3 | Families 3-6 of the 13, counter-evidence, detector evolution U31 |
| G-1 | CL + EXT (jzapata) | 10-16 | T4 | Reconcile infra overlap (relay B1-B9), images by digest in the shared registry, OIDC/CD workflows, `core-migrate`, sweep, alarm wiring |
| G-2 | USR + CL | 6-10 | T4 | Plan review, staging apply, smoke, rollback drill |
| G-3 | CL | 6-10 | T4 | Joint H4 on AWS; real IdP only if CAP-44 unblocked |

### 4.7 Not in the spec: where each belongs

| Topic | Home | WP | Default if undecided |
|---|---|---|---|
| Deployment pipeline (build, push, deploy, rollback) | infra repo, Claude | G-1, G-2 | manual runbook, no auto-deploy |
| Runtime ops, incident handling | runbooks, Claude + Codex | F-1, F-3 | skeleton at T3 |
| Secrets | names in env/manifests; values only in ignored files or AWS secrets | S-08, G-1 | local ignored env; never in a repo |
| Cost/budget governance | RunConfig (Codex), reservation (Claude), gateway policy (EXT) | D-4 | client-side ceiling and ledger |
| Tenant model | single tenant `pulso-dev`; tenant id already in every claim | none | multi-tenant deferred |
| Product Phase 2 data | Product team (relay D) | B-6 | simulator + labelled assumption; E0 primary |
| llm-gateway policy | EXT, mirrored client-side | D-4 | gateway as is |
| Observability | F-1 | | local LGTM profile (exists, #88) |
| Data retention | F-3 | | E0 local only |
| Rollout/rollback of proposals | E-2 | | alias move with receipt; publish != promote |
| Human approval UX | B-4 + C-3 | | CLI/file prompt at T1, console at T2 |
| Load | F-2 smoke only | | broader load after T4 |

## 5. Parallelization design

### 5.1 Ownership matrix (disjoint file sets; amends plan section 5)

| Path (improvement-engine) | Owner | Notes |
|---|---|---|
| `crates/core/src/**` (existing and new semantic modules), `crates/source-adapters`, `crates/runner` | CX | no port-signature change without `[CONTRACT-CHANGE]` |
| `crates/core-client/`, `crates/control-api/`, `crates/engine/` (new) | CL | Codex reviews; pure modules from Codex only via a journal ask |
| `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, `.github/workflows/*`, `scripts/verify-local-*.ps1`, `local/compose.yaml`, `scripts/dev.ps1` | CL as single integrator (replaces the plan's "Codex single integrator" because Claude publishes) | Codex requests deps via `[DEP-ASK]`; default approve for std-class crates |
| `migrations/**` | CX | CL asks via `[ASK]`; numbering reserved by Codex |
| `contracts/pipeline/`, `contracts/engine-steps/` | CX produces, CL consumes | `schema_version:"1"` |
| `contracts/engine-run/` | CL produces, CX consumes | evidence report schema |
| `core-bridge/`, `agent-core-assets/`, `platform-*`, `e2e-core/`, `demo/`, `local-identity/`, `bridge-contract/`, `debug-console/`, `local/core/` | CL | unchanged |
| `docs/flows/engine-*`, `docs/journal/codex-*` | CX | |
| `docs/flows/core-*`, `docs/journal/claude-*`, `docs/plan-real/*` | CL | |
| `infra` repo | CL with jzapata (EXT) | never duplicate shared VPC/RDS/S3; defer to agent-core infra |

If the user rejects the amendment (D1 = no): A-1..A-3 revert to Codex; Claude delivers a **seam kit** (conformance tests, goldens, Python reference of each seam, live-run harness) and still publishes and runs live. T1 slips about 2-3 sessions because each live debug iteration needs a Claude run (Codex has no Podman) and each publication a Claude transfer.

### 5.2 Subagents per lane (loaded machine: one Podman VM, 5.9 GB free of 15.7 GB, 12 logical cores)

System-wide caps: at most **5 agents active**, **1 cargo build/test** (slot via mutex, `CARGO_BUILD_JOBS=2`), **1 Podman E2E**, Playwright `workers=1`. Python and read-only agents are light.

| Lane | Implementers | Reviewers | Peak concurrent | Notes |
|---|---|---|---|---|
| A (Rust seams, CL) | 2 (A-1 and A-2 in parallel; A-3 after) | 1 shared, never an author | 3 | authors write in parallel and queue cargo runs |
| B (Rust semantics, CX) | 2 (B-1+B-4; B-2+B-3) | 1 independent | 3, only 1 cargo | keep Codex's existing Cargo-slot discipline |
| C (Python/console, CL) | 1-2 | 1 | 2 | pytest light; Podman suites via mutex |
| D (models, CL) | 1 | 0-1 | 1 | needs the key; short |
| S (enablement) | 1 | 0 | 1 | first session only |

The machine, not team size, is the limit: plan on Claude 3-4 agents plus Codex 2 agents in heavy sessions, never more than 5 working at once. The orchestrator does not code on the critical path.

### 5.3 Contracts and who publishes first

| # | Contract | Publisher -> consumer | When | Form |
|---|---|---|---|---|
| C-0 | Bridge OpenAPI + goldens + ADR 0011/0012; platform-contract 1.1.0 | CL -> CX | exists | `bridge-contract/`, `platform-contract/` (on main) |
| C-1 | Port stability list: `CoreTaskPort`, `JevDecisionPort`, governed writer, native-evaluation admission, `DurableJobStore`, observation store traits are **frozen** until T1 ends | CX -> CL | session 0-1, about 1 h | journal stanza naming trait, file, digest |
| C-2 | `pipeline.v1` event/command vocabulary + golden transcripts | CX -> CL, with CL review against real Core behaviour | first 2 sessions | `contracts/pipeline/transcripts/*.json`, tested by both sides; Claude's S-07 strawman seeds the command list |
| C-3 | Engine run evidence report (`target/sha/doubles[]`, per-step receipt ids, labels) | CL -> CX | session 1 | JSON schema in `contracts/engine-run/` |
| C-4 | Black-box conformance: console API tests and `e2e-core` binding/broker/ingest tests parametrized by base URL | CL -> A-2/A-5 and CX | sessions 1-2 | existing tests, small delta |
| C-5 | Builder output corpus (real model, provenance) | CL -> CX (B-2) | S-MAP | `agent-core-assets/corpus/builder_design/*.json` |
| C-6 | Core-accepted eval suite goldens | CL -> CX (B-5) | before B-5 | fixtures |
| C-7 | Engine-steps JSON schemas | CX -> CL | with B-1 | `contracts/engine-steps/` |

The only mutual blocker is C-2. It is defused by letting Claude start A-3 against the first transcript revision plus a fake reducer built from it, and Codex start B-1 from Claude's strawman.

### 5.4 Cheapest reliable coordination protocol

The channel stays the shared journal (user rule). Cost control:

1. **One stanza format, at most 8 lines, tag first**: `[CONTRACT-PUBLISHED id@rev path digest]`, `[CONTRACT-CHANGE id reason migration]`, `[ASK from->to need-by default-if-silent]`, `[DEP-ASK crate version reason]`, `[BLOCKED wp reason default-taking]`, `[DONE wp evidence-digest]`, `[HANDOFF branch head manifest]`, `[FINDING severity ref]`. Long reasoning goes to `docs/journal/*`.
2. **Default-if-silent is mandatory in every ASK.** Silence for one session means the default is taken, so neither team idles.
3. **Read protocol**: start each session with the last 20 `## ... CL|CX-nnnn` headings, filter by tag; nobody reads the 350 KB journal.
4. **Code transfer without the user**: Codex commits to local branches and posts `[HANDOFF]`; Claude fetches from the worktree path, cherry-picks onto fresh `main` in the integration worktree, runs `verify-local-all.ps1`, and puts the receipt in the PR body. Claude -> Codex goes through the local mirror (S-01).
5. **Wave cadence**: one consolidated PR per wave per repo, stacked on the previous wave's branch (never wait for merges). Waves: W1 publish Codex backlog; W2 A-0..A-2 + B-1 transcripts; W3 A-3 + B-2/B-3/B-4 + C-2 (T1); W4 A-5/A-6/B-7/C-3 (T2 core); W5 real models, memory, cost; W6 T3 hardening.
6. **State table**: the first journal stanza of each session is a 10-row table (WP, state, evidence, next, blocker, default). Nothing else is status reporting.
7. **Review exchange**: Codex reviews Claude's Rust read-only; Claude reviews Codex's U27/PL outputs black-box.

### 5.5 What Codex can do without GitHub or Podman, and what must be transferred

Needs only cargo `--offline --locked` plus the dependency cache from S-02: B-1, B-2 (once the corpus is on disk), B-3, B-4, B-5, B-6, pure parts of B-8, reviews, docs, fixtures, spec amendments. B-7 PG tests are written offline and executed by Claude; spike SP-A checks whether Codex can reach a loopback PG port, in which case it runs them itself.

Transfers, all performed by Claude: code out of Codex worktrees (cherry-pick), main snapshot into the mirror, dependency cache, corpus and fixtures. The user's own actions: lift the freeze, merge PRs, answer the asks in section 8.

| Blocked party | Waiting for | Does meanwhile |
|---|---|---|
| Claude | C-2 transcripts | A-1, A-2 (no reducer needed), C-1, D-1/D-2/S-MAP, S-05, console API conformance, G-1 plan-only |
| Claude | Codex unfreeze | all of lanes A, C, D, S (new files only); dirty worktrees read-only as reference |
| Codex | live Core behaviour | works against goldens and the corpus |
| Codex | builder corpus | B-1, B-3, B-4 first; B-2 starts with fixtures then switches to the corpus |
| Codex | Cargo slot | writes tests, docs, reviews while another lane holds the slot |

## 6. Prioritization, cuts and deferrals

### 6.1 Order and reasoning

| Rank | Item | Value | Risk reduced | Unblocking power |
|---|---|---|---|---|
| 1 | S-01..S-04 (mirror, deps, publish backlog) | medium | work exists but is not integrable | all Codex work and publication |
| 2 | S-MAP spike (real builder over E0 signal) | very high | attacks the only intellectual gap first, with real outputs | feeds B-2; tells us whether mapping is feasible before about 40 h are spent |
| 3 | A-1 and A-2 in parallel | very high | the entire Rust half of the Core integration | A-3 and every live run |
| 4 | B-1 transcripts, B-3, B-4 | high | defines the executor contract; U27 is the second gate | A-3, C-2 |
| 5 | A-3 + C-2 (T1 integration) | very high | proves the chain on live Core | everything after |
| 6 | D-1..D-3 real models | high | model quality and cost unknown | T2 claim |
| 7 | A-6, B-7 durable `serve`; A-5; C-3 | high | spec core: durability, inspection without a shell | T2 |
| 8 | B-5, E-1, E-2 | medium-high | removes remaining stand-ins in steps 6 and 10 | T2 completeness |
| 9 | F-*, B-6, B-8 | medium | operability, breadth | T3 |
| 10 | G-* | medium, gated | deployment reality | T4 |

### 6.2 Triage of Codex's 7 dirty worktrees (CX-0182)

| Worktree / branch | Value for the chain | Action |
|---|---|---|
| `p2-u12-u13-runner-compose` (16 files) | high: closest thing to runner composition | commit; mine for B-1; do not publish as is |
| `e0-core-draft-binding` | high for B-2 | commit; fold into B-2 |
| `u26-stateful-sandbox-r2` (`paired_scenario.rs`) | high for B-3 | commit; seed of U27 |
| `p4-temporal-successor` (migration 0005, local commit `75a613f`) | high for T2 | publish in W1 if the gate is green |
| `pl-c4-platform-privacy-guard` | medium (T2/T3) | W1 or W4 |
| `u13a-verified-candidate-admission` | medium | review; fold or drop |
| `p1-scout-platform-signal`, `p4-consolidated` | low-medium | review; probably subsumed |

### 6.3 Cut or defer (explicit)

Cut from T1-T2: CAP-07 entities route; CAP-15/18/19 Rust cascade/docs/limits (dry-run is authoritative); JCS hash parity (to T3); breadth beyond 2 families per source (T3 reaches 6; 13 is H5); U34-F/FE forks; U32 panels beyond timeline/investigation/gates/decision; U31 detector evolution (T3); real Jev (blocked by agent-core #28); remote IdP and prod promote/canary (CAP-44); multi-tenant; load beyond smoke; hosted CI green as a gate; Terraform apply before T4; browser matrix beyond Chromium.
Not cut despite cost: durable worker (T2), independent verifier actor, bounded revision loop, `do_nothing`, honest `unlinked`, human gate, labelled doubles.

## 7. Risk register (cross-team and external)

| ID | Risk | P/I | Mitigation | Owner |
|---|---|---|---|---|
| X-01 | Codex stays frozen | high/high | D1 + defaults in section 8: Claude builds all new files alone; Codex WIP read-only reference | USR |
| X-02 | E0 finding cannot become a valid Core artifact through a real model | medium/high | S-MAP first; bounded revisions; if infeasible keep `unlinked` honest and use another candidate chosen by sensors; original dataset as second source; never key a mapping to the winning category | CL+CX |
| X-03 | Real-model quality and cost unpredictable (invalid_output, refusals, spend) | high/medium | D-2 replay for repeatability; D-4 breaker; reserve before each call; suites use replay only | CL |
| X-04 | Rust seam volume underestimated (server + client + executor on Windows) | medium/high | pure-step rule, tripwire F-PY at session 4, sync `ureq`/`tiny_http` to avoid the async tax | CL |
| X-05 | Machine overload (Podman VM 10.4 GB + cargo + PG + Core + console) | high/medium | mutexes, preflight, one E2E at a time, `CARGO_BUILD_JOBS=2`, per-lane target dirs; ask user to free RAM in E2E windows | CL |
| X-06 | Contract drift between independently built halves surfacing late | high/high | golden transcripts; conformance tests run against both double and real from day 1; `contract_revision` in every report | CL+CX |
| X-07 | Offline cargo cache lacks new deps for Codex | medium/medium | S-02 and spike SP-B; vendor if needed | CL |
| X-08 | Hosted CI red hides regressions; merges rest on local evidence | high/medium | S-05 aggregated gate, receipt in PR body; ask for Actions budget | USR |
| X-09 | Podman instability (cgroups workaround, partially verified backend) | medium/high | fixture profile first; doctor smoke before any `real_local` label; rootful connection for limits | CL |
| X-10 | Core quotas (10 proposals/24 h, 20 evals/proposal) throttle soak | medium/medium | fresh Core DB per run; injected clock in soak | CL |
| X-11 | Claude is both orchestrator and Rust seam author (context overflow, bus factor) | medium/medium | subagents write; orchestrator keeps the state table; every WP ends with a handoff file | CL |
| X-12 | Spec/plan drift after the ownership change | medium/medium | additive journal amendment + plan section 5 note; owning team edits its part of the spec | CL |
| X-13 | Agent-core PRs #23/#24/#28 never land; no Jev | high/medium | no Jev in T1-T2; judgments via `agent` nodes with schema; relay asks | EXT |
| X-14 | Product Phase 2 data never arrives | medium/medium | E0 primary, simulator for platform families, labelled | EXT |
| X-15 | Shared infra overlap with agent-core workload (service names, DB ingress, Cloud Map) | medium/medium | defer to jzapata; plan-only until answers; relay B1-B9 | EXT |
| X-16 | Optimistic "done" claims (journal "integrated" meant crate-private) | medium/medium | every DONE needs a receipt with target/sha/doubles; no percentage reporting | CL |

## 8. Exact asks to relay, each with a default to proceed

### 8.1 To the user (decisions and actions)

| # | Ask | Needed by | Default if no answer |
|---|---|---|---|
| U-1 | Lift the Codex freeze (CX-0180) for B-1..B-4 and S-03; Codex stays on offline pure work | before session 1 | Claude proceeds alone on lanes A, C, D, S; Codex idle; T1 slips 1-2 sessions |
| U-2 | Approve the ownership amendment: Claude writes `crates/core-client`, `crates/control-api`, `crates/engine` and is single integrator of Cargo/CI/compose; Codex keeps `crates/core` semantics | before A-0 | Claude writes them as new files anyway (no Codex file touched) and records the amendment in the journal for later ratification |
| U-3 | Authorize Claude to publish Codex-authored commits (cherry-pick, original author preserved) and to host a local mirror under `D:\.codex\factored\mirror` | S-01 | take it: nothing leaves the machine except normal PRs |
| U-4 | LLM access: provider, model(s), a key placed by the user in an ignored env file (variable name only, e.g. `LLM_PROVIDER_KEY`), a USD ceiling. Proposed: 20 USD total for the T1 smoke, 2 USD per run, 10 USD per day | before D-1 | recorded and scripted only; live smoke `not_run`; T1 label `llm=scripted/authored`; T2 live claim blocked |
| U-5 | GitHub Actions: top up the budget or approve a self-hosted runner; check why job logs return 404 | any | S-05 local gate is the merge evidence |
| U-6 | Merge wave PRs W1..W6 in order, about a day after opening | per wave | stacked branches keep work moving; nothing waits |
| U-7 | Free RAM (close other heavy apps) during announced E2E windows | per E2E | mutex + preflight skips with `insufficient_memory` |
| U-8 | AWS (T4 only): account/region, state bucket and OIDC trust owner, authorization to `terraform apply` in staging, monthly budget ceiling | before G-2 | G-1 plan-only; T4 not started |
| U-9 | Debate decisions D1-D3 (section 9) | session 1 | the recommended option of each |

### 8.2 To the agent-core team (via the user; item numbers refer to `AGENT_CORE_RELAY_FOR_USER.md`)

| # | Ask | Default |
|---|---|---|
| AC-1 | Land PRs #23, #24, #28 on `main` or say they are held (A1, Q4) | plan without them; Jev `not_exercised` |
| AC-2 | Distinct `idempotency_in_progress` code with `Retry-After` (N8-02) | bridge disambiguates with a reconcile read |
| AC-3 | `resolve_ports` should use `getattr(args, "lang_thresholds", None)` (A11) | keep our `synthesise_args` workaround |
| AC-4 | Contract version bump or changelog; release-id change note (N8-08, N8-07) | pin-watch drift gate |
| AC-5 | Run/transcript read isolation for advisor/service principals (F-04) | our `AuthzPort` is restrictive; no claim of upstream isolation |
| AC-6 | Export cursor caveats and rolling-deploy order (N8-03/04) | fresh DB per run locally; document order |
| AC-7 | Infra overlap B1-B9 (schema DDL owner, Cloud Map owner, single `pulso-core-runtime`) | ours is the single runtime; names per infra #26; plan-only |

### 8.3 To the Product team

| # | Ask | Default |
|---|---|---|
| PR-1 | Read mechanism (replica, snapshot, feed, API); payload per `event_type`; contiguity of `event_log.sequence` (relay D1-D3) | exporter + simulator assumptions, labelled |
| PR-2 | Phase 2 roadmap for tool calls, approvals, identity, close outcomes (D0, D5, D7) | only case/turn/assignment families; others `not_evaluable` |
| PR-3 | Stable marker for demo rows; retention; whether message text may reach hosted models (D6, D9) | E0 stays local; platform text never sent to hosted models |

### 8.4 To the llm-gateway owners

| # | Ask | Default |
|---|---|---|
| GW-1 | First tag and GHCR digest; private pull from AWS (Q8) | build from source commit `63155b6` locally |
| GW-2 | Per-consumer allowlist and price/token caps (Q1); server-side rate limit (Q2) | our client-side ceiling and ledger |
| GW-3 | Provider request id and resolved alias in responses (Q5); stable error `code` (Q10) | leave receipt fields `unknown` |
| GW-4 | Two active tokens per consumer and an authenticated whoami (Q6); `Idempotency-Key` (Q7) | free 400 probe; timeouts recorded as unknown cost |

## 9. Decisions to debate (the three that most change the plan)

| ID | Question | Recommended | Why debate |
|---|---|---|---|
| D1 | Should Claude write the Rust seam crates (client, control-api, executor shell) and be integrator of Cargo/CI/compose, with Codex owning pure semantics? | Yes | Faster live debugging (only Claude has Core, Podman, GitHub); but it overrides plan section 5 and puts Rust volume on the orchestrator |
| D2 | Engine hosting stack: sync `ureq` + `tiny_http` first (axum only if SSE fails) vs axum/tokio from day one | Sync first | Avoids async rework and a heavy build on a loaded machine; SSE with long-lived threads is acceptable at demo scale; costs a possible later migration |
| D3 | Tripwire fallback F-PY (Python shell over pure-step Rust CLI) at session 4 if the Rust shell is not live on real Core | Keep as insurance | It dilutes the spec's "Rust control plane" if triggered; the alternative is accepting the slip |

Secondary points worth a look: JCS hash parity deferred to T3; eval suite from assets (labelled) in T1; recorded-replay as the T1 model label; Claude as publisher of Codex commits.

## 10. Timeline in working sessions (not calendar promises)

Assumes U-1..U-3 answered in session 0. Confidence = chance the milestone lands inside the stated window.

| Session | Claude lane (critical) | Codex lane | Milestone |
|---|---|---|---|
| 0 | S-01, S-02, S-05 draft, S-06, S-07, strawmen of C-2/C-3 | unfreeze; S-03 | mirror up, deps cached, backlog committed |
| 1 | A-0, A-1 and A-2 start, D-1, S-MAP | B-1 transcripts rev 1, B-3, B-4 | corpus; C-1, C-2 rev 1 published |
| 2 | A-1 live vs real bridge; A-2 passes `e2e-core` black-box tests; S-04 and W1 PR | B-1 rev 2, B-2 on corpus, B-3 GREEN | W1 open; client and broker GREEN live |
| 3 | A-3 vs fake reducer, then real B-1 | B-2 compile for Flow/Prompt, B-4 GREEN | first full run attempt on `real_local` (scripted/recorded) |
| 4 | debug loop, C-2 swap, negatives | B-2 hardening, reviews of A | **tripwire check**; W2/W3 PRs |
| 5-6 | D-2 replay, C-1 prompts, D-3 live smoke if key | reviews, B-5 start | **T1** (50% within 5-7 sessions) |
| 7-9 | A-6 serve, A-5 API, C-3 console | B-7 durable, E-3 | restart test; console on real API |
| 10-12 | D-3/D-4 live loop, E-1/E-2, C-5 compose | B-5, E-1 | **T2** (35% within 11-16) |
| 13-18 | F-1, F-2 soak, B-6, F-4 | B-6, B-8, F-3, F-4 | **T3** (35% within 15-22) |
| 19-23 | G-1, G-2, G-3 | support | **T4**, only after U-8 (25%) |

Slip drivers, in order: (1) real builder quality (X-02), (2) Codex unfreeze, (3) machine contention, (4) Rust seam volume, (5) key and budget availability. The fastest honest improvement: answer U-1, U-2 and U-4 on day one.

## 11. Definition of done per WP (common)

Strict TDD through a public interface; independent adversarial review (1-3 loops) by an agent that did not write the code; `verify-local-all.ps1` receipt; journal `[DONE]` stanza with digest; ADR when a boundary decision is taken (client crate choice, sync stack, ownership amendment); docs in English; every report carries `target`, `sha`, `doubles[]`, `contract_revision=pulso-two-teams-1`; no secret and no E0 text in any artifact; nothing changed under `D:\Nexus`.
