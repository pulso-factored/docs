# Plan v4: incremental path to a real, durable, continuous Pulso system, DEMO-0 first

Status: final plan; supersedes v3 and does not patch it. Baselines: improvement-engine main 853b029 (1683 tracked files), agent-core main c814c2b (pin), llm-gateway main 63155b6. Facts below come from read-only inspection and from the reviews; `gh` was re-run at authoring for the agent-core PRs and the gateway tags. Hours are focused lane-hours (implementation, own tests, one review loop), ranges are about 80% bands, English throughout. Every number in this document is computed by the checker of section 8.2 from the table of section 8.

## 0. Goal restated (faithful to the user's request)

Not the 24-hour scenario. Implement incrementally and reach, as early as possible, a REAL system that integrates (1) the real product platform (Product team: cases, turns, assignments, event_log), (2) agent-core with its capabilities and execution (registry, runs, evaluation, approval, publication), (3) the real infrastructure (AWS, Terraform, deployed services) and (4) the real llm-gateway. It uses the initial dataset and the augmented dataset (E0 and the bank CSVs authorized for local tests and our own infrastructure). It is a durable, continuous engine that really runs: it ingests the data, searches for signals, analyses problems and opportunities, and loops signals -> problems/opportunities -> improvement proposals expressed as agent-core artifacts of any kind (tools, flows, compiled trees, agents, Jev decision models, prompts, eval suites, policies, templates, combinations, plus honest negatives for denied kinds) -> through agent-core -> executed for real with real models -> interacting with the product: the real "magic demo" of the spec, and beyond. The plan covers everything still missing per the spec and what the spec does not specify, grouped and prioritised for parallel execution by subagents and by two teams (Claude holds the main thread, Codex supports), and was reviewed by backward chains and adversarial passes until feasible (section 17).

## 1. The plan in sixteen lines

1. Organizing principle: DEMO-0 first, evolution after. DEMO-0 = the first real, honest end-to-end run (section 2.3). The demo path is 16 WPs (76-111 h, 5.6% of the hours) and is entirely Claude's. Everything else is the evolution path, scheduled behind it in waves, never ahead of it.
2. Headline: time to DEMO-0 is about 6.4 sessions at capacity A (5.7-7.3; 8, range 7.2-9.3, if the wave-0 enabling pack shares the same agents), 4.9 at B (4.3-5.7), 3.7 at C; serial floor 25.5 h (G1 > M3 > Q1r > GT0). Confidence medium-low: capacities are assumptions re-baselined at TW-1 (section 13).
3. DEMO-0 uses the user's decision: roleplay rung. Our own Claude subagents simulate the LLMs and Jev behind a real HTTP path through the real llm-gateway; they receive only TREATED payloads (spec pre-ModelPort treatment), enforced by a payload scanner at the shim (TPS); labelled `agent_roleplay` in `doubles[]`. Later DEMOs climb: recorded replay (CI), local GPU model, real hosted model.
4. Independence rule (user directive): no Claude WP has a hard edge to a Codex WP, directly or transitively, for any gate; Codex WPs depend only on Claude's wave-0 frozen artifacts. Where the real system would consume Codex output, Claude owns a labelled stand-in behind the same port; Codex output is an optional swap-in (`~` edges), never gating. The checker prints 0 Claude->Codex hard edges.
5. Strangler order kept: S1 Python host (DEMO-0), S2 Rust steps called by the Python host (DEMO-1a), S3a Rust shell run-once (DEMO-1), S3b durable worker (DEMO-2); retirement gates RG-1..RG-4; DEMO-3 on AWS staging; DEMO-4 and DEMO-5 breadth.
6. Ownership computed from the table: Claude 72.8% (low) to 72.5% (high) of all 1337-2024 remaining hours and 70.5% to 70.0% through T1b; Codex 27.2-27.5% overall and 29.5-30.0% through T1b; per tier and per wave in 8.1.
7. Artifact breadth is a first-class stream B (propose, validate, evaluate, publish per kind, plus denied-kind negatives): Claude owns the live implementation, Codex owns offline goldens, semantics and conformance suites.
8. Data: raw E0 and CSV rows never reach any third-party model; treated payloads may reach the roleplay responder (condition confirmed in ask 1); hosted real models need the user's separate sentence (U-9).
9. Environment is measured before it is improved: capacity levels A (current), B (software-only, ENV0 decides), C (needs hardware from the user, three options with cost).
10. Partition: 29 lanes (17 Claude, 12 Codex) with a TOTAL path map (1683 of 1683 tracked files owned, 0 ties) and per-lane migration, ADR and journal ranges; single integrator for `lib.rs`, Cargo files and CI; nested `seams/` workspace; L-BRIDGE lane for the Python bridge.
11. Consolidation trains: one PR per 25-35 lane-hours per team, stacked, restack rule, at most 3 open PRs per team; legacy worktrees retired first (WTR1, WTR2).
12. Contracts: 13 contracts reconciled with the code; C-1, C-7, C-11 exist today; the rest are draft v0 at wave 0 (CF0, FRZ0) and frozen at the first gate that exercises them (CF1).
13. Review loops by class RC1/RC2/RC3 (1-3 loops) are explicit WPs (CRV1-4 by independent Claude reviewers, REV1-5 by Codex as optional second reviewers); hours are inside the totals.
14. Asks are ordered: one-sentence user decisions first (ask 1 = confirm the treated-payload condition), then external relays; silence is never approval; every ask has a safe default.
15. Tripwires TW-0..TW-3 are WPs with objective criteria.
16. If Codex is frozen, nothing on the Claude path shifts; only the optional swap-ins and Codex breadth (364-557 h) are delayed.

## 2. Definition of "real"

### 2.1 Honesty vocabulary

Every step line of a run report carries one status and one data class. `doubles[]` is generated BY THE ENGINE from observed facts (URL that answered, image digest, Core `/internal/v1/version` and manifest digest, gateway `model` echo, receipt provider, scanner id), never hand-written. Reports (`contracts/engine-run/`, G1) carry `target`, `sha`, `contract_revision` and `host` per step.

| Status | Meaning |
|---|---|
| `real` | real dependency, real data path, engine-driven, full coverage promised by the tier |
| `real-narrow` | real dependency and path, one family, kind or path only |
| `local-model` | real small model on our hardware; quality claims bounded by the measured schema-valid rate |
| `agent_roleplay` | real HTTP path and real gateway; backend answered by role-playing subagents; plumbing and mapping only, `quality_claims: forbidden` |
| `recorded` | digest-keyed replay of a recorded response, with provenance; never shown as live |
| `stand-in` | real downstream driven by a Python host, fixtures or a Claude implementation of a Codex-owned semantic |
| `simulated` | synthetic source or scripted actor (platform-sim, local issuer as human) |
| `blocked(<dep>)` | named external dependency (Jev PR #28, CAP-41 bank, CAP-44 IdP, Product Phase 2) |

Secondary labels (additive tags on a status): `semantics=claude-standin`, `compile=claude-standin`, `gate=claude-authored`, `suite=claude-standin`, `authority=claude-standin`, `hash=core-authoritative`, `base_world=seeded`, `suite=assets_handwritten`, `treated=scanner:<id>`, `scheduled-ingest`, `unsupported_source`. Ladder rungs (3.1) map to statuses: rung 0 `real`, rung 1 `agent_roleplay`, rung 2 `recorded`, rung 3 `stand-in` or `simulated`.

Honesty tests (owner G1; they bite): (1) `real` while a receipt provider is `agent_roleplay`, `recorded` or scripted fails; (2) a receipt whose data class is E0, CSV or original-treated and whose provider is third-party (hosted, or `agent_roleplay`) fails unless the payload carries a passing scanner id for the treated allow-list, and a hosted REAL model additionally needs `third_party_ok` with a journal reference to the user's sentence; (3) a mapping keyed to the winning category fails the rename and permute mutation test; (4) per-port Core double provenance and model price source are listed, and a template-fallback stage output fails; (5) world, suite, simulator effect and judge carry `author` fields and the suite is sealed before the candidate exists; (6) a report with `host=python` cannot carry a label above DEMO-1a; (7) scout and verifier use distinct actors and different model identities; (8) a tracked file with E0 markers or a `data=E0` receipt body fails the push scan (DC0).

### 2.2 Data classes (binding rule, user decision applied)

| Class | Where it may run | Which model may see it |
|---|---|---|
| `synthetic` (independently authored) | anywhere | any model, including hosted with a capped key |
| `treated payload` (what the engine itself sends to a model after the spec's pre-ModelPort treatment: pseudonymised ids, no raw sensitive fields, no identity answers) | anywhere | roleplay responder and local model, only through the scanner allow-list (TPS); hosted real model only after U-9 |
| `E0/CSV raw` (rows, raw conversation text, derived extracts) | local host and our own infrastructure (user lifted this for local tests); never committed to git (digests and counts only) | local processes only; NEVER a third-party model, hosted or roleplay |
| ops (job rows, run events, receipts, ledger) | anywhere | n/a |

Standing rule (user decision, U-13 resolved with a condition): the roleplay responder receives only the payloads the engine itself sends to a model, in treated form, never raw E0/CSV rows or raw conversation text; the scanner at the gateway shim rejects or redacts anything not on the allow-list and has a test (TPS first RED: a raw E0 row sent to the shim is rejected). The user may lift or widen it later; rung-ups (local GPU, hosted real) are later DEMOs, not blockers. The same rule binds all developer agents, Claude and Codex (both hosted third parties): they work from schemas, digests and synthetic fixtures, not raw E0 text; the Codex onboarding brief (G0f) states it. The step 2 -> 3 hand-off is therefore: local sensors run on raw E0 (local process, real detection) and emit signals; the engine's pre-ModelPort treatment produces the treated payload; the scanner admits it; only then does the roleplay scout see it (review A H8).

### 2.3 Demos, tiers and gates (each demo re-runs the same thread with fewer doubles)

| Demo | Tier | Gate WP | Stage | What exists and what is observable | Doubles that remain (each has a scheduled rung-up) |
|---|---|---|---|---|---|
| DEMO-0 | T0 | GT0 | S1 | Executable `demo/run.ps1`: ingests the real E0 package locally, existing sensors detect signals by sealed ranking (no planted column, no hard-coded winner), scout and verifier investigate, builder (a model) proposes an agent-core artifact (Replace Prompt plus Add EvalSuite, the path proven on Core) validated by dry-run, REAL Core runs the evaluation arms and both gates, human approval, publish to local staging, alias read, observation. Replay green and one live run. `E2E-THREAD-01` ratchet with all ten steps | model and Jev `agent_roleplay` through the real gateway path (rung-up: replay for CI in DEMO-0 itself, local GPU and hosted real in DEMO-1a/2); host `stand-in(python)` (DEMO-1); issuer `simulated` (real approver session at DEMO-1, U-15); product side `simulated` with a real Core alias read (real Product inbound at T3); Jev only via the shim and our Python port test (agent-core PR 28 is not on main, so Core stages are `llm_structured`) |
| DEMO-1a | T0.5 | GT05 | S2 | Rust steps (recompute, validation, compile, gate) called by the Python host; model rung-up to the local GPU model with a measured schema-valid rate | `semantics=claude-standin`; host python |
| DEMO-1 | T1a | GT1A | S3a | Rust shell, run-once, control-api lite, authority state machine, thin memory; one real recorded CLI approval | jobs in memory; trigger manual; Codex semantics are stand-ins |
| DEMO-2 | T1b | GT1B | S3b | PG jobs, worker, `kill -9` survives, ingest batch starts a run unaided; Python host demoted | label `scheduled-ingest` (not "continuous") |
| DEMO-3 | TA | GTA | | same thread on AWS staging, alarm fired and resolved, rollback drill | prod untouched; Product outbound `blocked(product-phase-2)` |
| DEMO-4, DEMO-5 | T2, T3 | GT2, GT3 | | hardening, then breadth: flow, template, policy, decision model, agent, bundle, tool, Jev(blocked) with evidence | remote IdP, bank, real Product DB, Jev in Core |

"Continuous" in the spec means the prequential replay protocol (spec 28.4/28.5); until the replay driver (RPL1 stand-in or DREPLAY swap-in) lands, a scheduler plus queue is called `scheduled-ingest`.

## 3. Dependency services: current state and the ladder

### 3.1 Ladder rule

Rungs, labelled in `doubles[]`: rung 0 the real service; rung 1 real path with `agent_roleplay` backend; rung 2 digest-keyed recorded replay; rung 3 fixtures or stand-ins. Start on the highest rung that is available, permitted by the data class and within budget; climb when the real service passes the same black-box contract test file as the lower rung; never descend silently (a lower rung is a deliberate run-config choice, auto-relabelled); every rung runs the SAME test file.

### 3.2 Services table

| Service | State now (evidence) | Gaps | Start rung and climb | Owner |
|---|---|---|---|---|
| llm-gateway (main 63155b6) | Go; aliases via `LLM_ENDPOINTS`, `api_key_env` mandatory, per-request profile, `structured: prompted` schema subset, no retry, 1 MiB; per-consumer bearer auth via `GATEWAY_CONSUMERS`; `/v1/jev` merged (PR 2, needs `JEV_API_KEY`); tag-triggered `release.yml` exists (PR 3) but no tag or release was ever pushed (`gh`: 0 tags, 0 releases); never run against a real provider | no per-consumer alias or model allowlist, rate limit, idempotency, cost log; caller owns price; no GHCR digest | rung 1 now (built from SHA, alias `roleplay`); rung 2 replay; rung 0 local model or hosted capped key after U-4; EXT-3 asks for a tag | CL (M1, M0RP, TPS, M2a) |
| agent-core (main c814c2b, contract 1.3.0) | real Core image drives scout, verifier, builder, writer, arms; 44 live e2e tests; ships a Dockerfile and `docs/plan-e2e-produccion.md` (TA5 checks them first); `gh` today: PRs 23 and 24 (registry contract, proposals listing) and 28 (Jev through gateway) are merged=true into side branches `ccr-a4781bdb-dnrn7q`, `feat/registry-contratos`, `feat/http-llm-gateway`, NOT main (matches the user's relay) | ambiguous 409 `idempotency_conflict` (N8-02); Core-side doubles (tools, authz, classifier, calibration, transcript); template fallback when gateway env unset; quotas (10 proposals/24 h, 20 evals/proposal); pin moved 5 times in about 21 h with `VERSION` constant | rung 0 now; per-port double provenance; Jev `blocked(jev)` Core-side; EXT-1 | CL (G2, K1-K3, L-BRIDGE) |
| Product platform | Phase 1: cases, turns, assignments, `event_log`; no AI features; platform-contract 1.1.0, exporter and simulator are ours | read mechanism unknown; no Phase 2 dates | rung 3 simulator with a real Core alias read (PX0); inbound read-only real at T3 (P3); EXT-2 | CL (PX0, P1, P2py, P3) |
| Infra/AWS | Terraform declaration-only; nothing ever applied; shared foundations owned by the agent-core infra owner; OIDC, CD, bootstrap open | no account, state backend, SSO, mailbox | plan-only, local Podman stack as staging stand-in; first apply at TA4 after GT1B; never ahead of the demo path | CL (TA0-TA6) |
| Codex engine (main 853b029) | libraries plus one local-sim CLI; 587 tests; `core_task.rs` pinned 0.5.0 digest-only; compiler takes one Flow shape; `durable_jobs.rs` trait without claim-next; migrations 0001-0004 (three files numbered 0002); Rust tree has 521 pub types and 59 `compile_fail` references (G0gr re-measures); `pub(crate)` seals | no worker, scheduler, control-api, Core client, PG adapters | consumed as merged code (sensors via the existing binary); new Codex work is an optional swap-in only | CX |
| Podman and capacity | `pulso-dev` and `pulso-codex` are both distros of ONE WSL2 VM capped by `.wslconfig` at 10 GB and 8 CPUs; host free RAM about 1.7 GB measured 2026-10-04; no sccache, mold, lld, nextest or ollama on the host; no compiler in the VM; the 33-minute gate is Codex's root `--workspace` script and Codex has no Podman | one stack at a time; port exhaustion; cgroups workaround | measure first (ENV0) | CL |
| GitHub Actions | budget exhausted; hosted CI Rust-only and red | no hosted evidence | `verify-local-all` receipt in every PR body | CL |

### 3.3 The roleplay gateway shim (M0RP, TPS, RPP, M5a)

- Design: `roleplay-llm` exposes OpenAI `POST /v1/chat/completions` and `/v1/models` behind the real gateway (alias `roleplay`, model `agent_roleplay@1`, price 0), or any gateway-compatible endpoint; agent-core runs call it through `AGENTCORE_LLM_GATEWAY_URL` and token like any model. Each request (system = Core stage prompt, user = canonical inputs, tools, schema hints) is scanned (TPS), then written to a queue directory with its digest; the shim long-polls under the gateway `timeout_s` (120-300) until a response file appears; Core's invoke timeout is 600 s, so no gateway or bridge change is needed.
- Multi-turn: scout and verifier are agent nodes with tools; the shim returns OpenAI `tool_calls`, Core executes them, the next request carries the tool result; the responder is stateless per request like a real API. Usage is returned flagged `usage_estimated`; faults (timeout after send, 502 `invalid_output` with usage) come from a scripted side channel, never from a subagent.
- Responder protocol (RPP, documented runbook): the orchestrator runs a lane of fresh-context subagents, one per request or stage batch; each reads only its queue file (prompt digest recorded) and writes only its response file; scout, verifier and builder use distinct responders; none is the implementer or reviewer of the code under test; the responder takes ONE of the agent slots, so live runs are scheduled in windows when an implementer is idle.
- Budget (estimate, measured by SNET and RPP): one DEMO-0 live run is about 40-60 calls (scout about 15, verifier 8, builder 5, writer 3, evaluation arms about 12) at 20-90 s each, i.e. 15-90 minutes of one slot; 4-8 live runs per session; everything else replays.
- Record and replay (rung 2): key = digest of the canonical request; the same request replays deterministically so CI needs no live agents; a drift test fails with the digest diff instead of going live silently; a prompt revision costs a re-record (2-4 lane-hours). Synthetic and treated-payload corpora are committable; anything derived from raw E0 stays in a git-ignored local directory with a digest manifest.
- Jev: the shim also serves `/v1/jev` (gateway side exists) to test the pass-through and our Python and Rust `JevDecisionPort` (M5a, M5b); Core-side Jev is `blocked(jev)` until PR 28 lands on main, so DEMO-0 uses `llm_structured` stages.
- Rung-up schedule (evolution DEMOs): recorded replay for CI (DEMO-0, M3); local GPU model (ENV9, SMOKE, DEMO-1a); hosted real model on synthetic (M4, after U-4); hosted real on treated E0 payloads (after U-9, DEMO-2); each swaps the backend only, same test file.

## 4. Strangler order and retirement of the Python host

| Stage | Host | What moves | Feasibility |
|---|---|---|---|
| S1 (DEMO-0) | Python host (`e2e-core/codex_standin`, core-bridge stages) | the model path becomes real (gateway plus roleplay); E0 detection runs through the existing sensors | no cargo seam, no Codex; the one cargo action is building the existing local-sim binary |
| S2 (DEMO-1a) | Python host calls `pulso-engine step` | semantics as JSON-in/JSON-out Rust steps in `seams/crates/steps`, authored by Claude over the frozen schemas (no sealed Codex types are touched) | sensors wrap the existing binary; recompute, validation, compile (Prompt plus EvalSuite) and gate are Claude stand-ins labelled `semantics=claude-standin` |
| S3a (DEMO-1) | Rust shell, jobs in memory | executor, control-api lite, authority state machine stand-in, thin memory | resume-after-kill from CAS-stored inputs |
| S3b (DEMO-2) | Rust worker on PG | durability | PGJ, worker, triggers |

Python host freeze rule: after GT0 it gets glue only; new semantics enter as Rust steps behind `contracts/engine-steps/`. RG-1 (GT05): every step the ratchet marks `real-narrow` is served by a Rust step. RG-2 (GT1A): the ratchet is green on the Rust shell and for 3 recorded runs both hosts give the same ordered command sequence and `candidate_hash`. RG-3 (GT1A): all negatives pass including resume-after-kill. RG-4 (GT1B): `demo/run.ps1` defaults to the Rust host; the Python host moves to `e2e-core/legacy_host`, deprecated, deleted by Q2. RG-5 (GT3): a Claude stand-in is retired only if its swap-in passed the conformance test (SWA, SWP, SWC, SWB, SWL). If TW-1 or TW-2 trips, the Python host stays the carrier with Rust steps, labelled, and the plan is re-based, not abandoned. Stage names S3a/S3b are kept; the object store is always called "blob store" (BLOB1) to avoid the S3 collision.

## 5. The ten demo steps walked backward, by demo

| # | Step | DEMO-0 | DEMO-1a/1 | DEMO-2 | Still not real |
|---|---|---|---|---|---|
| 10 | New observations, memory, successor | `simulated` (platform-sim emits `release.*` and effects, author separated; P2py) | thin memory note, confirm and contradict (MEM1) | durable memory head | real Product source before T3; effect authored by us |
| 9 | Staging confirmed by alias receipt | `real-narrow` (Core alias read on local staging) | same, Rust client (K2) | same | not AWS before DEMO-3 |
| 8 | Human only for authority | `simulated` (local issuer) | `real-narrow` at DEMO-1: one recorded CLI approval with the decision card (U-15) | durable `waiting_human` plus notification (H1n) | remote IdP and bank step-up blocked |
| 7 | Failure to bounded revision | `stand-in(python)` | rule-driven in Rust (V3r) | same | LLM-driven revision T2 (V3L) |
| 6 | Base vs candidate, two gates | arms `real-narrow` on Core, verdict `stand-in`, suite `assets_handwritten` | gate stand-in in Rust (GSI), suite sealed before arms | same | Rust suite emitter EVE T2; Codex gate is a swap-in |
| 5 | Concrete change, versions, diff | compile `stand-in(python)`, dry-run and writer receipts on Core | compile in Rust (CMP), then writer path K3 | same | other kinds are stream B (T2/T3) |
| 4 | Opportunity, mechanism, alternatives, `do_nothing` | `agent_roleplay` builder, validated against ReadBase, no catalogue | same plus local model | same | quality claims need `local-model` or hosted evidence |
| 3 | Scout and separate verifier | `agent_roleplay` scout and a distinct verifier plus deterministic recompute, treated payloads only | recompute in Rust (STP1), broker grants (E5R) | same | sqlite lab until DUCK |
| 2 | Signal families, discards | `real-narrow`: existing sensors on raw E0 locally, one family | Rust wrapper | same | 13 families are Codex breadth (DFAM1-3) and swap-in |
| 1 | Data wakes the engine | `manual_command` | manual | `scheduled-ingest` (E7) | real Product trigger T3; prequential replay T2 |

## 6. Independence design, dependency graph and critical paths

Rules, enforced by the checker (8.2):
1. No Claude WP has a hard dependency on a Codex WP (printed count: 0). Gates are computed over Claude-only edges.
2. Codex WPs depend only on the wave-0 frozen artifacts (`FROZEN:` line below): G0f, G0gr, CONTR, CF0, FRZ0, BK0, ENV0, ENV4. FRZ0 publishes the digest-pinned pack Codex verifies against: C-7 signature, C-8 ChangeSpec and ScenarioCase schemas, C-9 transcript seed, C-10 gate result shape, a builder-output corpus v0, arm-report goldens and PG claim traces recorded from the existing tests. Where a Codex lane would need a running service, the recorded transcript replaces it: DPGc uses the PG claim traces, DEVAL and BKE the arm-report goldens, DMAPV and BKF the builder corpus; none needs Podman, live PG or a live Core.
3. Swap-ins are `~` edges from a Claude WP to a Codex WP: SWA (compile, gate, recompute, validation), SWP (pipeline, authority), SWC (conformance on PG), SWB (kind modules and goldens), SWL (replay, oracle, detectors, memory), and the optional reviews RVC1-3. They depend on a Claude gate, gate nothing, are never critical, and each carries a conformance test that lets Claude adopt the Codex implementation; a stand-in is retired only through GT3 (RG-5).
4. Hand-offs are versioned artifacts (digest-pinned packs, train tags) plus the journal; each team's PR train is independent; nobody waits on the other's branches.

FROZEN: ENV0 ENV4 G0f G0gr CONTR CF0 FRZ0 BK0

Graph (hard edges, Claude path): `G1 > M3 > Q1r > GT0` (DEMO-0, depth 25.5 h; M0RP, DC0, ED0, TPS, RPP, M5a, SMAP, M2a, P2py feed it in parallel). `G0f > CONTR > FRZ0 > CMP > E3b > CRV1 > GT05` (39.5 h). `G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A > GT1B` (118.5 h; the checker prints it with all gates). `K0 > K1 > K2 > K3` is the integration spine; the ENV0 > ... > K3 chain is 62.0 h because K0 needs ENV2 and ENV4; K3 does not wait on any compiler (K3fx fixture). Critical path (float at most 4 h to GT1B, midpoint hours): 20 WPs, 145.5 h, all Claude. Serial depth in lows-highs: GT0 21-30, GT05 32-47, GT1A 95-139, GT1B 96-141, GTA 125-189 hours. The earlier "158 h in 19 packages" mixed a sum of parallel branches with the serial chain; the serial chain is the depth above.

Hidden gates (cause most slips): (1) the S-MAP outcome (finding to valid artifact), first read in DEMO-0 with `unlinked` and `not_evaluable` as valid endings; (2) real-model behaviour on stage schemas, measured at DEMO-1a (SMOKE), so every label before it is `agent_roleplay`; (3) the compile writer path is a Core stage with a sealed `RegistryMutationCommitment`, not HTTP routes (K3); (4) cargo slot, Podman and RAM (ENV0); (5) pin churn (G2).

## 7. Environment and capacity (measured first, improved second)

Machine model (corrected): both Podman machines are distros of one WSL2 VM capped at 10 GB (`.wslconfig`) with 8 CPUs; stopping or resizing a distro frees almost nothing; the lever is `.wslconfig` (global, needs `wsl --shutdown`) and host RAM (about 1.7 GB free now). No sccache, mold, lld, nextest or ollama on the host; no cargo or compiler in the VM. The full 33-minute gate is Codex's Windows root script (fmt, clippy and test `--workspace`, 45 integration test binaries in `crates/core`, bundled sqlite); Codex cannot reach Podman. `rust-lld` ships with the toolchain, so ENV2 needs no install. No speedup number below is sourced: every one is "to measure" in ENV0 and kept only if it shows at least 1.3x or 5 minutes saved.

| Level | Content | Needs | Capacity (lane-hours per session, an assumption re-baselined at TW-1) |
|---|---|---|---|
| A current | 1 orchestrator + 3 implementers + 1 reviewer (a live responder displaces an implementer); one cargo slot; one stack; replay-mode gate; at most 8+1 Claude and 4+1 Codex worktrees | no approval | 14-18 |
| B software-only, decided by ENV0 | host lld and debug profile (ENV2), vendored deps (ENV4), separate target dirs (G0e), fast and full gate tiers (ENV6), then conditional: Linux build container inside the existing VM with sccache and nextest (ENV1, ENV3, ENV5), pytest sharding (ENV7), local model runtime (ENV9) | ENV1 needs an ADR (ENVADR) because AGENTS.md says no development in WSL, user ack U-14a, and approval to download a toolchain image (U-14b); the root gate stays Windows | 18-24 |
| C hardware or runners | ENV11 lane scheduler, ENV12 build farm | user supplies one of three options (indicative list prices, not quotes): C1 host RAM to 32-48 GB and `.wslconfig` memory 24 GB, about USD 80-200; C2 a second Linux box with 64 GB for builds and stacks, about USD 800-1500 used; C3 an on-demand 16 vCPU 64 GB cloud runner or a self-hosted Actions runner (U-6), about USD 0.5-1.0 per hour, about USD 100-250 per month at 8 h x 22 days | 35-45 |

Default (silence): ENV0, ENV2, ENV4, ENV6, ENV8 only on the existing machines; ENV8 measures and writes recommended `.wslconfig` values as an ask; no machine is stopped, created or resized; ENV1, ENV9, ENV12 wait for their sentences. The demo path needs none of ENV (no seam crates; the single cargo action is building the existing binary). Environment WPs run behind DEMO-0 unless ENV0 shows they shorten the demo path.

`seams/` consequences: a nested `[workspace]` works (tested by reviewer C: root `cargo metadata` and `seams/` both succeed; no `exclude` is needed; the root `rust-toolchain.toml` 1.98.1 is inherited); hosted CI and Codex's root gate do not see `seams/` and it has its own `Cargo.lock`, so mitigation is the `seams` leg of `verify-local-all` (`cargo fmt/clippy/test --manifest-path seams/Cargo.toml --locked`, asserted by Pester), the receipt in every PR body, and a hosted workflow for `seams/` added by the CI integrator (X-FACADE) when Actions return (U-6). Because Claude owns stand-ins, no `seams` crate depends on `crates/core` (K0 dependency-graph test), so `seams/` never recompiles `crates/core` and its vendored closure is only the new packages (`ureq` without TLS, `tiny_http`, `ed25519-dalek`, UUIDv7, JCS; about 25-35); adopting Codex code (swap-ins) happens in a separate crate `seams/crates/swap` behind a cargo feature, created only at swap-in time.

## 8. Work packages (machine-readable table)

Columns: `id | name | stream | lane | owner | hours_low | hours_high | deps | wave | tier | critical | demo_path | first_red | acceptance`. Owner CL = Claude (orchestrator plus subagents), CX = Codex. A `~` before a dep marks an optional swap-in edge (Claude WP, Codex dep, never gating). `critical` = Y when the WP has at most 4 midpoint hours of float on the longest chain to GT1B (computed). `demo_path` = Y for the 16 WPs of DEMO-0. Waves: W0 = DEMO-0 sprint plus the enabling pack (G0f, G0gr, CONTR, CF0, FRZ0, BK0, XSTUB, which run on spare slots and only feed Codex independence); W1 DEMO-1a; W2 DEMO-1; W3 DEMO-2; W4 hardening and breadth (T2); W5 T3, AWS, T5. Streams: ENV environment; G governance and honesty; C contracts; M models and cost; Q integration and E2E; P platform; E engine and control-api; K core-client; V evaluation and memory; H human authority; B artifact breadth; D Codex domain, reviews, conformance; I console, observability and ops; A AWS. Hours include implementation, own tests and the first review loop; later loops are the CRV and REV WPs. Gate WPs are 1-2 h evidence packages. External work (EXT, U asks) has no hours.

| id | name | stream | lane | owner | hours_low | hours_high | deps | wave | tier | critical | demo_path | first_red | acceptance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G0f | OWNERS.md with generated path map and test, journal tags, state table, Team trailer, Codex onboarding brief | G | L-GOV | CL | 2 | 3 | - | W0 | T0 | Y | N | owners test fails on the 1683 tracked files with no map | 0 unowned and 0 tied tracked paths at 853b029 plus rules for new paths; brief states data-class rule for all developer agents |
| G0gp | Facts refresh: pins, gateway SHA, agent-core main, PR states, DB versions | G | L-GOV | CL | 2 | 3 | - | W0 | T0 | N | Y | facts.json schema test fails when a SHA is missing | facts.json with SHAs and gh state of agent-core PRs 23, 24, 28 |
| G0gr | Pub-surface audit (pub types, serde derives, compile_fail), post-merge review of PR 93, PG16 and PG17 preflight | G | L-GOV | CL | 4 | 6 | - | W0 | T0 | Y | N | audit script fails when counts are absent | measured counts replace 521 and 59; export request list for WDX; ADR and journal maxima read |
| G1 | engine-run report schema, doubles[] generator, honesty and author-separation tests | G | L-GOV | CL | 9 | 12 | - | W0 | T0 | N | Y | honesty test 1 fails: real status with a scripted receipt provider | 8 honesty tests green; report carries target, sha, contract_revision, host per step |
| CONTR | contracts/engine-steps JSON in/out schemas and port list (draft v0) | C | L-GOV | CL | 3 | 4 | G0f | W0 | T0 | Y | N | schema validation fails on a sample step | schemas for sensors, recompute, validation, compile, gate; digest published |
| CF0 | Contract freeze 0: freeze C-2, C-12, C-13; digest and stubs for draft contracts C-3..C-10 | C | L-GOV | CL | 3 | 4 | CONTR,G0f | W0 | T0 | Y | N | digest pin test fails with no published digest | journal CONTRACT-PUBLISHED entries; allocation tables (migrations, ADR, journal) published |
| XSTUB | Codex: empty module stubs and [[test]] entries for every planned module in one commit | D | X-FACADE | CX | 2 | 3 | G0f | W0 | T0 | N | N | cargo check fails on a mod line without file | root gate green; no behaviour; lib.rs and core Cargo.toml untouched afterwards by other lanes |
| DC0 | Data-class gate: gw-e0 and gw-hosted profiles, internal network, content scanner, push scan, split corpora | G | L-MODEL | CL | 5 | 7 | - | W0 | T0 | N | Y | scanner fails on a tracked file with an E0 marker | honesty test 8 green; E0 profile has no key and no external route |
| SNET | Spike: container-to-host reachability, clock skew, multi-minute call tolerance | G | L-E2E | CL | 2 | 3 | - | W0 | T0 | N | Y | probe fails when Core cannot reach the host shim | report with 5-minute call result; spike rewritten test-first |
| M1 | Real llm-gateway in the local Core stack from pinned SHA, stage policy, alias via LLM_ENDPOINTS, smoke | M | L-MODEL | CL | 4 | 6 | G0gp,SNET | W0 | T0 | N | Y | smoke fails: gateway alias returns 404 | real gateway answers Core stage call; dummy api_key_env documented for local endpoints |
| M0RP | agent_roleplay shim: OpenAI endpoint, queue, multi-turn tool_calls, digest record and replay, fault channel | M | L-MODEL | CL | 8 | 12 | - | W0 | T0 | N | Y | replay test fails on a digest drift | same request replays by digest; drift test shows diff; tool_calls round trip |
| M3 | Stage hardening against gateway schema subset, synthetic recorded corpus, replay mode | M | L-MODEL | CL | 6 | 9 | M0RP,G1 | W0 | T0 | N | Y | schema-subset test rejects an unsupported keyword | 4 stages (scout, verifier, builder, writer) pass in replay with 0 schema rejects |
| SMAP | S-MAP-lite harness: finding to builder to dry-run with 10 recorded outputs, design-input producer, new C-8 JSON schemas | M | L-MODEL | CL | 8 | 12 | M0RP,DC0,ED0 | W0 | T0 | N | Y | harness fails: dry-run rejects the first recorded builder output | 10 outputs recorded; counts of valid, unlinked, not_evaluable reported; no mapping keyed to winning category |
| M2a | Spend ceilings on the single Python ledger, kill switch, reconciliation hook | M | L-MODEL | CL | 3 | 4 | M1 | W0 | T0 | N | Y | ceiling test fails when a call exceeds the cap | run stops at ceiling; ledger equals gateway sum within 1 token |
| P2py | Simulator release events, fast-forward clock, effect realism with author separation | P | L-PLAT | CL | 6 | 9 | G1 | W0 | T0 | N | Y | sim test fails: no release.* event after publish | release events plus effect series authored apart from the judge |
| Q1r | E2E-THREAD-01 ratchet in replay and live with all ten steps on the Python host | Q | L-E2E | CL | 5 | 7 | G1,M3,M1,P2py,ED0 | W0 | T0 | N | Y | ratchet test file with ten red steps | replay green; live once; every step labelled; host=python |
| GT0 | Gate DEMO-0: first real end-to-end run: E0 ingested locally, signals detected, builder proposals validated by dry-run, real Core evaluation, local-issuer approval, publish to local staging, simulated observation; labelled doubles listed | Q | L-GOV | CL | 1 | 2 | Q1r,SMAP,M2a,DC0,ED0,TPS,RPP,M5a | W0 | T0 | N | Y | gate evidence script fails on a missing receipt | replay green and one live run through the gateway path with agent_roleplay; doubles[] lists model=agent_roleplay, jev=agent_roleplay, issuer=simulated, product=simulated, host=python; scanner passed every payload |
| BK0 | Artifact-kind capability matrix as a contract with propose, validate, evaluate, publish verbs and denied-kind list | B | L-GOV | CL | 4 | 6 | CONTR,G0gr | W0 | T0 | N | N | matrix test fails when a kind has no verb row | contracts/artifact-kinds covers every EntityKind and release_settings; digest published as frozen artifact |
| FRZ0 | Wave-0 frozen artifact pack: C-7 signature, C-8 ChangeSpec and ScenarioCase schemas, C-9 transcripts seed, C-10 gate result shape, builder-output corpus v0, arm-report goldens, PG claim traces recorded from existing tests | C | L-GOV | CL | 8 | 12 | CONTR,G0f | W0 | T0 | N | N | pack digest test fails when a golden is missing | pack published with digest; Codex lanes verify only against it (no Core, PG or Podman) |
| M5a | Roleplay JEV server behind gateway /v1/jev, plus Python JevDecisionPort test (DEMO-0 uses llm_structured stages; Core-side Jev stays blocked(jev) until agent-core PR 28 is on main) | M | L-MODEL | CL | 4 | 6 | M0RP | W0 | T0 | N | Y | pass-through test fails on header strip | gateway forwards to the roleplay JEV; port handles 200, 4xx, 502; real upstream needs JEV_API_KEY (U-4) |
| ED0 | E0 ingest and local detection: run the existing local-sim and sensor binaries on the E0 package locally, sealed ranking, discards recorded, findings feed the builder through the design-input producer | Q | L-E2E | CL | 5 | 8 | DC0 | W0 | T0 | N | Y | rename and permute mutation test: winning category changes with the label | detection output derived from E0 locally; no planted column; honesty test 3 green; data=E0 receipts show only local providers |
| TPS | Treated-payload scanner at the roleplay shim: allow-list from the spec pre-ModelPort treatment (pseudonymised ids, no raw sensitive fields, no identity answers); reject or redact anything else | M | L-MODEL | CL | 5 | 7 | - | W0 | T0 | N | Y | scanner test: a raw E0 row sent to the shim is rejected | 100 treated payloads pass, 20 raw rows and raw conversation texts rejected; test runs in CI replay |
| RPP | Responder protocol and runbook: queue directory, one fresh-context subagent per request or stage batch, distinct responders for scout, verifier, builder, one agent slot, call budget, latency budget | M | L-MODEL | CL | 3 | 4 | M0RP | W0 | T0 | N | Y | protocol test: a responder that sees the repo instead of the queue file is rejected | documented lane of subagents driven by the orchestrator; measured calls and minutes per live run in the report |
| ENV0 | Baseline timings in both accounts (cold and warm core test --no-run, link share, host free RAM, gate minutes, worktree count) and keep/cut table | ENV | L-ENV | CL | 2 | 3 | - | W1 | T0.5 | Y | N | baseline.ps1 --check fails without baseline.json | baseline.json for Claude and Codex accounts; keep/cut table; every speedup claim in the plan cites it |
| ENVADR | ADR: Linux build container inside the existing WSL VM versus AGENTS.md rule no development in WSL | G | L-GOV | CL | 1 | 2 | ENV0 | W1 | T0.5 | N | N | test asserts AGENTS.md WSL rule cites an ADR | ADR merged from the L-GOV block (0200-0209); user ack U-14a quoted in journal; root gate stays Windows |
| ENV2 | Host lld, line-tables-only debug profile, Defender exclusion for target dirs, per-account config | ENV | L-ENV | CL | 1 | 2 | ENV0 | W1 | T0.5 | Y | N | script reproduces link-time metric before and after | kept only if >=1.3x or >=5 min saved on core test --no-run, else reverted and recorded |
| ENV4 | cargo vendor into shared read-only dir with per-account source replacement; closure includes crates/core 189 packages | ENV | L-ENV | CL | 2 | 3 | ENV0 | W1 | T0.5 | Y | N | cargo build --offline --locked fails in clean CARGO_HOME | both accounts build the seams skeleton and root tests --no-run offline; new package list |
| ENV6 | Fast gate and full gate wrappers: Codex gate unchanged as a leg, seams leg with manifest-path and locked, Pester asserts | ENV | L-ENV | CL | 3 | 4 | ENV0 | W1 | T0.5 | N | N | Pester asserts verify-local-all runs the root script and the seams leg | seams-only change runs no root workspace test; receipt JSON with minutes |
| ENV8 | Memory plan: measure .wslconfig and host headroom, heavy-slot lock file; no machine is stopped, created or resized | ENV | L-ENV | CL | 1 | 2 | ENV0 | W1 | T0.5 | N | N | two processes contend, only one acquires the lock | lock honoured by both accounts; recommended .wslconfig values written as a user ask only |
| G0e | Per-lane CARGO_TARGET_DIR and slot protocol | G | L-ENV | CL | 1 | 2 | ENV8 | W1 | T0.5 | N | N | two lanes with equal target dir fail the check | each lane has its own target dir; documented in the lane brief |
| G2 | pin-watch and bump lane (initial; later bumps 2-4 h each) | G | L-BRIDGE | CL | 4 | 6 | - | W1 | T0.5 | N | N | pin-watch test fails on a pin bump without manifest digest | gate on SHA plus manifest digest; one generated pin-constants file |
| WTR1 | Worktree inventory and retirement of merged legacy worktrees on the Claude side; cap rule | G | L-ENV | CL | 2 | 3 | ENV0 | W1 | T0.5 | N | N | inventory script lists unmerged worktrees | registered worktrees below 25 before W1 starts; unmerged ones listed for the user |
| WTR2 | Codex-side worktree inventory and retirement | G | X-REV | CX | 1 | 2 | ENV0 | W1 | T0.5 | N | N | inventory script lists unmerged worktrees | Codex-owned worktrees merged or listed; combined count reported |
| G0d | verify-local-all receipt script (root gate leg, seams leg, replay mode, E0 scanner hook) | G | L-ENV | CL | 4 | 6 | ENV6,G0f | W1 | T0.5 | N | N | Pester asserts receipt has the seams leg and the scanner | receipt JSON in every PR body |
| ENV10 | Codex-side probe: offline build from the vendor dir, own target dir, timings, loopback PG reachability | ENV | X-REV | CX | 1 | 2 | ENV4 | W1 | T0.5 | N | N | probe fails when the vendor dir is unreadable | report with minutes and whether PG is reachable |
| PX0 | Product consumption contract: registry alias resolution plus release.* exposure events; platform-sim reads the real Core alias | P | L-PLAT | CL | 4 | 6 | G1 | W1 | T0.5 | N | N | sim conformance fails: alias read returns nothing | spec amendment; label simulated(product-consumer) until EXT-2 answers |
| M4 | Hosted smoke on synthetic data with capped key | M | L-MODEL | CL | 3 | 4 | M2a,M3 | W1 | T0.5 | N | N | smoke fails without the cap env | scout 3 of 3 schema-valid on a hosted model, receipt provider shown; blocked until U-4 |
| ENV9 | Local GPU model runtime on the RTX 3060 (name, source and size need approval) | ENV | L-ENV | CL | 4 | 8 | ENV8 | W1 | T0.5 | N | N | runtime smoke fails: no completion | rung-up to local model: model digest in receipt; heavy slot; needs the optional download sentence (U-14b) |
| SMOKE | Local-model smoke: scout and verifier 3 of 3 schema-valid, builder 2 of 3 with one regeneration | M | L-MODEL | CL | 4 | 8 | ENV9,M3,M1 | W1 | T0.5 | N | N | smoke asserts schema-valid rate and fails at 0 of 3 | rung-up DEMO: scout and verifier 3 of 3, builder 2 of 3 schema-valid on the local model; status local-model; payload scanner stays on |
| ENV1 | Linux build container inside the existing VM (conditional on ENV0 and ADR) | ENV | L-ENV | CL | 4 | 6 | ENV0,ENVADR | W1 | T0.5 | N | N | container build fails: no toolchain | warm seams build time recorded; kept only if >=1.3x on Claude seams builds |
| ENV3 | sccache in the Linux build container (conditional) | ENV | L-ENV | CL | 2 | 3 | ENV1 | W1 | T0.5 | N | N | cache hit-rate check fails at 0 | kept only if ENV0 rule is met |
| ENV5 | cargo-nextest archive and partitioned runs in the container (conditional) | ENV | L-ENV | CL | 2 | 3 | ENV1 | W1 | T0.5 | N | N | partitioned run misses a test | all tests run once across partitions |
| ENV7 | pytest sharding with PG schema per shard (conditional on RAM) | ENV | L-ENV | CL | 4 | 6 | ENV8 | W1 | T0.5 | N | N | shard test fails on a shared schema | core-bridge suite sharded 2-way with identical pass set |
| DMAPV | Evidence-bound design-intent validation, do_nothing, no invented refs | D | X-MAP | CX | 6 | 10 | FRZ0 | W1 | T0.5 | N | N | validation test rejects an invented evidence ref | 10 SMAP outputs: valid, unlinked or not_evaluable decided without catalogue |
| CT1 | core_task.rs 0.5.0 to 1.3.0 typed contract change via CONTRACT-CHANGE stanza | D | X-COMPILE | CX | 3 | 5 | G0gr | W1 | T0.5 | N | N | core_task test fails on 1.3.0 fields | digest-only constants replaced; bridge goldens parsed; Claude review recorded |
| WDX | pub exports and DTO facades for composite steps in crates/core | D | X-FACADE | CX | 6 | 8 | G0gr,CF0,XSTUB | W1 | T0.5 | N | N | export test fails: facade not nameable outside crate | facade list from G0gr exported; sealed constructors unchanged; compile_fail guards still pass |
| DMAPC | Compiler: Replace Prompt plus Add EvalSuite, multi-operation, authorization chain; digest from bridge dry-run | D | X-COMPILE | CX | 12 | 18 | FRZ0,WDX,CT1 | W1 | T0.5 | N | N | compile test fails on a two-operation spec | Prompt+EvalSuite spec compiles; precondition digest hash=core-authoritative; compile_fail guards intact |
| DGATE | U27 combined gate on the paired_scenario seed | D | X-GATE | CX | 7 | 10 | G0gr,CF0 | W1 | T0.5 | N | N | gate test fails when one of two gates is skipped | both gates required; result shape C-10 draft; offline goldens |
| DVREC | Pure verifier recompute function | D | X-GATE | CX | 3 | 5 | CONTR | W1 | T0.5 | N | N | recompute test fails on a tampered numerator | recompute matches 5 fixtures bit for bit |
| DWIRE | Pure sensor entry points over input views; namespace and canary REDs | D | X-SENS | CX | 4 | 8 | CONTR | W1 | T0.5 | N | N | namespace canary fails when original and enriched mix | entry points callable through step schema; canaries red then green |
| DORIGm | Original dataset minimum slice: 2 families, separate namespaces, unsupported_source negative | D | X-SRC | CX | 8 | 10 | DWIRE | W1 | T0.5 | N | N | negative test fails when original-only passes as supported | 2 families on sealed ranking, no hardcoded category; negative green |
| K0 | seams workspace skeleton declaring every crate, own [workspace], edition 2024, dependency-graph test, vendor build | K | L-CLIENT | CL | 3 | 4 | ENV2,ENV4,G0gr | W1 | T0.5 | Y | N | graph test fails: abi depends on crates/core | root gate unaffected; abi and core-client free of crates/core; engine, eval, pg may depend on it |
| TW0 | Tripwire TW-0 evidence: seams builds offline in Claude account, CF0 published, Codex side if U-1 | G | L-GOV | CL | 1 | 2 | CF0,K0 | W1 | T0.5 | N | N | tripwire script fails on missing journal entry | TW-0 verdict recorded; Codex part BLOCKED if U-1 silent |
| REV1 | Independent review wave (Codex) of S1 and S2 PRs and DTO checks | D | X-REV | CX | 4 | 6 | - | W1 | T0.5 | N | N | review checklist has an open finding | reviews train tag published by Claude in the journal; findings closed; verdict in journal (optional second reviewer, gates nothing) |
| GT05 | Gate T0.5: Rust steps called by Python host with semantics=claude-standin; RG-1; kinds proven: prompt, eval_suite; one stage measured on local or hosted model | Q | L-GOV | CL | 1 | 2 | E3b,GT0,CRV1,SMOKE,PX0 | W1 | T0.5 | N | N | gate script fails when a step is still stand-in | ratchet flips steps 2,3,4,5,6 to real-narrow per step with host column |
| STP1 | Step stand-ins in seams/crates/steps: sensor wrapper over existing local-sim binary, verifier recompute, intent validation (labelled stand-in vs Codex semantics) | E | L-ENGINE | CL | 8 | 12 | CONTR,FRZ0,K0 | W1 | T0.5 | N | N | recompute test fails on a tampered numerator | 3 steps JSON in and out through the step schema; Python host calls them |
| CMP | Compile stand-in: Replace Prompt plus Add EvalSuite over bridge-contract DTOs, digest from dry-run, denied-kind negatives | E | L-ENGINE | CL | 9 | 13 | CONTR,FRZ0,K0 | W1 | T0.5 | N | N | compile test fails on a two-operation spec | compiles the FRZ0 corpus; 4 denied kinds return the named reason; label compile=claude-standin |
| GSI | Gate stand-in: two-gate verdict over arm reports, author is not judge (label gate=claude-authored) | E | L-ENGINE | CL | 6 | 9 | CONTR,FRZ0,K0 | W1 | T0.5 | N | N | gate test fails when one gate is skipped | verdict equals FRZ0 gate goldens on 5 cases |
| E3b | Python host glue: steps called through the step schema, ratchet flips per step with host and semantics columns | E | L-ENGINE | CL | 5 | 7 | STP1,CMP,GSI | W1 | T0.5 | N | N | ratchet steps 2 to 6 still stand-in(python) | steps flip to real-narrow with semantics=claude-standin |
| CRV1 | Independent Claude review of S1 and S2 PRs by distinct fresh-context reviewers (loops per class) | D | L-GOV | CL | 4 | 6 | E3b | W1 | T0.5 | N | N | review checklist has an open finding | findings closed; reviewer differs from author |
| RVC1 | Claude review of Codex W0-W1 train: facades, compiler, gate, validation (optional) | D | L-GOV | CL | 4 | 6 | ~DMAPC,~DGATE,~WDX,~DMAPV | W1 | T0.5 | N | N | review script lists unreviewed Codex commits | Codex commits reviewed by a distinct actor |
| TRN1 | Claude consolidation train integrator for W1: lane merges in dependency order, one PR per 25 to 35 lane-hours, restack rule, local receipt | G | L-GOV | CL | 6 | 9 | - | W1 | T0.5 | N | N | train script fails when a lane branch is out of order | trains merged with receipts; stacked trains restacked within one fast gate |
| TRX1 | Codex train integrator for W1: lane merges into one train PR per 25 to 35 lane-hours, restack rule, root gate receipt | G | X-FACADE | CX | 2 | 4 | - | W1 | T0.5 | N | N | train script fails when a lane branch is out of order | trains merged with root gate receipts |
| DPLAT | platform_live adapter PL-C1, C2, C4, C5 | D | X-SRC | CX | 5 | 9 | G0gr | W1 | T1a | N | N | adapter test fails on a read-write grant | read-only snapshot adapter; PL-C4 guard test green |
| FX22a | Spec-22 wire fixture families 1 to 11 with goldens | D | X-SRC | CX | 8 | 10 | CF0 | W1 | T1a | N | N | fixture validator fails on a missing family | 11 families validated by validate_fixtures |
| DJC | claim-next on DurableJobRepository: trait addition, in-memory reference, REDs | D | X-CONF | CX | 3 | 5 | CF0,FRZ0 | W1 | T1b | N | N | claim-next test fails: two claimers get the same job | trait signature frozen as C-7; in-memory reference green |
| TA0 | AWS asks and offline plan review | A | L-INFRA | CL | 2 | 3 | - | W1 | TA | N | N | plan review checklist fails with no account assumptions | asks drafted; offline terraform validate on current tree; gaps listed |
| K1 | core-client transport: Ed25519 JWT, classifier, idempotency, generated pin constants | K | L-CLIENT | CL | 10 | 14 | K0 | W2 | T1a | Y | N | same Idempotency-Key twice makes 2 runs against FakeCore | 1 run on the real image for 2 identical keys; classifier table 100% of bridge-contract errors |
| K2 | core-client typed invoke, arms, admissions, dry-run, alias read (own 1.3.0 DTOs; no crates/core edit) | K | L-CLIENT | CL | 11 | 16 | K1 | W2 | T1a | N | N | golden decode fails for run envelope | 11 bridge-contract operations typed; FakeCore generated from goldens |
| K3fx | Fixture compiled ChangeSpec (Replace Prompt plus Add EvalSuite) from bridge-contract goldens so K3 does not wait on the compiler | K | L-CLIENT | CL | 2 | 3 | K0,SMAP | W2 | T1a | N | N | fixture fails dry-run against FakeCore | fixture accepted by real dry-run once; used by K3 tests |
| K3 | Draft-plan artifact, commitment sealing, writer-stage invoke, readback, dry-run | K | L-CLIENT | CL | 18 | 26 | K2,E5L,K3fx | W2 | T1a | Y | N | writer test fails: commitment mismatch not detected | Prompt+EvalSuite published to staging alias on the real image; readback equals commitment |
| E1 | JobHandler ABI, run-once harness, CAS-persisted inputs, resume-after-kill test | E | L-ENGINE | CL | 11 | 18 | K0,CF0 | W2 | T1a | Y | N | kill between handlers loses an input | kill -9 between two handlers resumes with identical event sequence |
| E2 | Executor: linear driver then live wiring | E | L-ENGINE | CL | 14 | 20 | E1,K2 | W2 | T1a | N | N | executor fails a 3-handler golden sequence | ten steps run on the Rust shell against the real image |
| E9s | Spike: tiny_http SSE and disconnect detection | E | L-CAPI | CL | 2 | 2 | K0 | W2 | T1a | N | N | disconnect not detected within 5 s | verdict on tiny_http versus axum with numbers |
| MIG0 | Migration runner, role bootstrap, widen job status, order the three 0002 files | E | L-PG | CL | 6 | 10 | K0 | W2 | T1a | N | N | runner schema differs from union of existing test setups | empty PG gains the same schema as existing tests; gaps in numbering tolerated |
| E5L | control-api lite: artifacts, authorization-checks, core-task-bindings | E | L-CAPI | CL | 14 | 20 | K1,E1,MIG0,E9s | W2 | T1a | Y | N | black-box test file fails against the Rust server | same test file green against double and Rust server; roleplay scout served |
| E4R | control-api rest: ingest ACK and quarantine, health, JWT replay store | E | L-CAPI | CL | 10 | 14 | E5L | W2 | T1a | N | N | ingest gap test fails to quarantine | PL-02/03/04 cases green; replay of a JWT rejected |
| E5R | Lab and wiki broker rest: grants, QueryReceipt, wiki read | E | L-CAPI | CL | 8 | 11 | E5L | W2 | T1a | N | N | grant test fails: expired grant accepted | QueryReceipt for a sqlite lab query; wiki read |
| V1 | Eval package: assets suite sealed before arms, six evaluate outcomes | V | L-EVAL | CL | 10 | 14 | K3 | W2 | T1a | Y | N | sealed-suite test fails when suite changes after arms | six outcomes captured from real arm reports |
| V2 | Gate wiring over real arm reports, author is not judge | V | L-EVAL | CL | 4 | 6 | V1,GSI | W2 | T1a | Y | N | author-equals-judge test fails | verdict from both gates; fails when authors coincide |
| V3r | Rule-driven bounded revision (max 2 attempts) | V | L-EVAL | CL | 5 | 7 | V2 | W2 | T1a | N | N | third attempt not refused | failure leads to revision then stop; budget unchanged |
| DEVAL | U47 CoreEvalPackage emitter from ScenarioCase, six-outcome capture | D | X-GATE | CX | 8 | 12 | DMAPV,DGATE | W2 | T1a | N | N | emitter test fails for an unseen scenario shape | eval_suite generated from 3 non-shipped scenarios; goldens from 3 real arm reports |
| H1 | Human authority: DecisionRequest, waiting_human, issuer port, approve then publish, alias read | H | L-AUTH | CL | 10 | 14 | V2,E1,AUS | W2 | T1a | Y | N | approve without both gates is accepted | decision card shows diff, gates, hash, alternatives, cost; one recorded CLI approval |
| P1 | Retarget platform-exporter to the real ingest contract | P | L-PLAT | CL | 4 | 6 | E4R | W2 | T1a | N | N | exporter batch rejected by control-api | platform-sim batch reaches /internal/v1/platform/observations |
| P2R | Release correlation in ingest and successor trigger | P | L-PLAT | CL | 6 | 8 | E4R,P2py,H1 | W2 | T1a | Y | N | release event creates no successor | release.* event starts the successor run |
| MEM1 | Thin memory: note artifact, wiki read, confirm or contradict | V | L-MEM | CL | 8 | 12 | E5R,P2R | W2 | T1a | Y | N | note test fails to contradict a prior claim | one note confirmed and one contradicted with evidence refs |
| K5a | Reconcile: lost response, 429, crash after write | K | L-CLIENT | CL | 5 | 6 | K2 | W2 | T1a | N | N | lost-response test creates a duplicate | 3 fault cases yield exactly one effect |
| IN0 | One-command compose project and doctor aggregate | I | L-ENV | CL | 6 | 10 | E5L,M1 | W2 | T1a | N | N | doctor fails with a stopped service | one command starts the stack; doctor green |
| BOOT | pulso-bootstrap core CLI and bootstrap-report.json (CAP-48) | I | L-BRIDGE | CL | 5 | 8 | G0gp | W2 | T1a | N | N | bootstrap report schema fails when empty | report lists seeded assets and digests on a fresh Core |
| BRG1 | Bridge route and mock gap requests from K2 and K3; CAP-07 decision recorded as amendment | I | L-BRIDGE | CL | 3 | 5 | K2 | W2 | T1a | N | N | bridge contract test fails for a requested route | each request answered or amended; goldens regenerated |
| DPL1 | PL-02, 03, 04 ingest gating fixtures: ACK, quarantine, gap | D | X-SRC | CX | 5 | 7 | DPLAT | W2 | T1a | N | N | fixture fails: gap not quarantined | 12 fixtures green offline; consumed by E4R |
| DPL2 | PL-06 to PL-10 detector REDs and capability profile ending at insufficient_* | D | X-SENS | CX | 8 | 12 | DPLAT,DWIRE | W2 | T1a | N | N | PL-10 fails: detector claims data Phase 1 lacks | 5 cases green; insight stops at insufficient_* |
| DDOC1 | PL-C6 spec text and amendment index | D | X-DOC | CX | 2 | 3 | DPLAT | W2 | T1a | N | N | doc link test fails for PL-C6 | amendment text merged |
| FX22b | Spec-22 families 12 to 22 plus read_model fixtures | D | X-SRC | CX | 8 | 10 | FX22a | W2 | T1a | N | N | fixture validator fails on a missing family | families 12-22 validated |
| FX22p | contracts/product fixtures for the Product consumer contract | P | L-PLAT | CL | 3 | 5 | PX0 | W2 | T1a | N | N | product fixture fails validation | contracts/product validated and consumed by platform-sim |
| BKN | Denied-kind negatives: tool_without_executor, unsupported_capability, release_level_change, blocked(jev) | B | X-ARTIF | CX | 4 | 6 | BK0,DMAPC | W2 | T1a | N | N | negative test accepts a tool proposal | 4 negatives return the named reason offline |
| BKNL | Live denied-kind negatives on real Core dry-run | B | L-E2E | CL | 2 | 3 | CMP,Q1r | W2 | T1a | N | N | live negative passes a denied kind | 4 negatives labelled by the engine; no publish |
| BKX | Dispatch in change_compiler to artifact_kind modules | B | X-COMPILE | CX | 4 | 6 | DMAPC,BK0 | W2 | T1a | N | N | dispatch test fails for an unregistered kind | new kinds register without editing compiler logic |
| Q1 | E2E-THREAD-01 on the Rust shell; Python host becomes regression twin; negatives | Q | L-E2E | CL | 5 | 8 | MEM1,V3r,K5a,IN0,Q1r,E2,K3,E3b | W2 | T1a | Y | N | ratchet step 1 stays stand-in | 10 steps with host=rust; negatives green; resume-after-kill |
| REV2 | Independent review wave (Codex) of R1 seam PRs: JWT, idempotency, hash, egress, loops 2 and 3 | D | X-REV | CX | 8 | 12 | - | W2 | T1a | N | N | review checklist has an open finding | reviews R1 seam train tag (JWT, idempotency, hash, egress, loops 2 and 3); optional, gates nothing |
| TW1 | Tripwire TW-1: K2 live on the real image | G | L-GOV | CL | 1 | 1 | K2 | W2 | T1a | N | N | tripwire script fails with no receipt | same key twice gives one run; scout receipt with tokens and cost |
| TW2 | Tripwire TW-2: E5L suite green on Rust server with roleplay scout | G | L-GOV | CL | 1 | 1 | E5L | W2 | T1a | N | N | tripwire script fails with no receipt | verdict recorded |
| TW3 | Tripwire TW-3: at least 6 of 10 ratchet steps hosted by Rust shell | G | L-GOV | CL | 1 | 1 | E2,V2,H1 | W2 | T1a | N | N | tripwire script counts host=python steps | verdict recorded |
| CF1 | Contract freeze 1: freeze C-3, C-8, C-10 (after GT05) and C-4, C-5 (after TW-1) | C | L-GOV | CL | 2 | 3 | GT05,TW1 | W2 | T1a | N | N | digest pin test fails for a changed draft | frozen digests published; CONTRACT-CHANGE stanza rules active |
| GT1A | Gate T1a: ratchet on Rust shell; RG-2, RG-3; kinds proven: prompt, eval_suite, denied-kind negatives; E0 run with data=E0 and local model only | Q | L-GOV | CL | 1 | 2 | Q1,CRV2,GT05,BKNL,CF1 | W2 | T1a | Y | N | gate script fails on a stand-in step | 3 recorded runs give identical command sequence and candidate_hash; honesty test 2 green |
| AUS | U21 authority state-machine stand-in inside seams/crates/authority | H | L-AUTH | CL | 5 | 8 | E1 | W2 | T1a | N | N | state test allows approve without both gates | all transitions covered; label authority=claude-standin |
| CRV2 | Independent Claude review of R1 seam PRs (JWT, idempotency, hash, egress; loops 2 and 3) | D | L-GOV | CL | 8 | 12 | K3 | W2 | T1a | N | N | review checklist has an open finding | findings closed; reviewer differs from author |
| RVC2 | Claude review of Codex T1a-T1b work (optional) | D | L-GOV | CL | 4 | 6 | ~DEVAL,~DPL2,~BKN,~DPIPE,~DAUTH,~DPGc | W2 | T1a | N | N | review script lists unreviewed Codex commits | all reviewed |
| TRN2 | Claude consolidation train integrator for W2: lane merges in dependency order, one PR per 25 to 35 lane-hours, restack rule, local receipt | G | L-GOV | CL | 8 | 12 | - | W2 | T1a | N | N | train script fails when a lane branch is out of order | trains merged with receipts; stacked trains restacked within one fast gate |
| TRX2 | Codex train integrator for W2: lane merges into one train PR per 25 to 35 lane-hours, restack rule, root gate receipt | G | X-FACADE | CX | 2 | 4 | - | W2 | T1a | N | N | train script fails when a lane branch is out of order | trains merged with root gate receipts |
| DPGc | Backend-generic conformance suite over DurableJobRepository | D | X-CONF | CX | 6 | 10 | DJC | W2 | T1b | N | N | suite fails on a backend that double-claims | suite green on in-memory reference; PG claim traces from FRZ0 replay offline; PG run is SWC |
| BKF | Flow and compiled-tree kind: propose, validate and compile modules plus goldens (offline) | B | X-ARTIF | CX | 10 | 14 | BK0,DMAPV | W2 | T1b | N | N | flow compile test fails on add-flow of 4 keys | add and replace Flow goldens; queue-order cases |
| BKT | Template, policy and prompt-variant kinds: propose, validate, compile (offline) | B | X-ARTIF | CX | 8 | 12 | BK0,DMAPV | W2 | T1b | N | N | policy compile test fails | goldens per kind incl. authorized-field limits |
| BKD | Decision-model kind (classifier, llm_structured, rule providers): propose, validate, compile (offline) | B | X-ARTIF | CX | 8 | 12 | BK0,DMAPV | W2 | T1b | N | N | calibration-unchanged test fails | goldens; calibration rule enforced; Jev provider returns blocked(jev) |
| BKA | Agent kind (replace authorized fields) plus cascade prediction expected_derived versus auto_bumped (CAP-19) | B | X-ARTIF | CX | 6 | 9 | BK0,DMAPV | W2 | T1b | N | N | cascade test: auto_bumped differs from expected_derived | cascade equality asserted on 3 fixtures |
| BKJ | Jev decision-model kind: propose and validate, honest blocked(jev) ending | B | X-ARTIF | CX | 3 | 5 | BK0 | W2 | T1b | N | N | Jev kind passes as supported | blocked(jev) asserted by the engine |
| PGC | Conformance suite for the Rust job repository, written by L-PG against the frozen C-7 signature | E | L-PG | CL | 5 | 8 | E1,FRZ0 | W2 | T1b | N | N | suite fails on a repository that double-claims | suite green on in-memory and PG; claim traces from FRZ0 |
| PGJ | PgJobRepository: claim-next (SKIP LOCKED), lease, fencing delta on existing pulso_jobs, migration 0050+ | E | L-PG | CL | 16 | 24 | MIG0,E1 | W3 | T1b | N | N | 2 workers claim one job | conformance PGC green; fencing token rejects stale writer; trait is the seams abi trait |
| E6w | Worker loop: lease, heartbeat, fencing, graceful shutdown | E | L-PG | CL | 10 | 14 | PGJ,E2 | W3 | T1b | N | N | worker keeps a job after lease loss | graceful stop leaves no lease; restart resumes |
| E7 | Triggers: cadence, ingest batch, snapshot registration, coalescing; liveness metric and restart policy | E | L-ENGINE | CL | 8 | 12 | E6w,E4R,P1 | W3 | T1b | N | N | ingest batch starts no run | exporter batch starts a run unaided; stall alarm metric present; compose restart policy |
| E8s | Durability subset: kill -9, 2 workers, PG restart, lost NOTIFY | E | L-PG | CL | 8 | 12 | E6w,PGC | W3 | T1b | N | N | kill -9 duplicates an effect | 0 duplicate effects across 4 faults |
| RC1 | Run control pause and cancel (U34) | E | L-ENGINE | CL | 6 | 9 | E6w | W3 | T1b | N | N | cancel leaves a running job | pause and cancel persisted across restart |
| H1b | Durable waiting_human and approval across restart | H | L-AUTH | CL | 3 | 5 | H1,PGJ | W3 | T1b | N | N | approval lost after restart | approval resumes the run after kill |
| H1n | Human notification adapter (webhook or file sink) for waiting_human with SLA timer | H | L-AUTH | CL | 4 | 6 | H1 | W3 | T1b | N | N | waiting_human emits no notice | notice emitted within 60 s; SLA breach alarm |
| DPIPE | Pure reducer pipeline swapped in behind the ABI | D | X-FACADE | CX | 6 | 10 | CF0,FRZ0 | W3 | T1b | N | N | pipeline transcript differs from linear driver | C-9 transcripts rev1 equal |
| DAUTH | U21 authority state machine (full) | D | X-FACADE | CX | 4 | 8 | CF0,FRZ0 | W3 | T1b | N | N | state test allows approve without gates | all transitions covered; compile_fail guards intact |
| REV3 | Independent review wave (Codex) of PG, worker SQL and fencing | D | X-REV | CX | 5 | 8 | - | W3 | T1b | N | N | review checklist has an open finding | reviews PG and worker train tag; optional, gates nothing |
| GT1B | Gate T1b: kill -9 survives; ingest batch starts a run; Python host demoted (RG-4) | Q | L-GOV | CL | 1 | 2 | E7,E8s,H1b,GT1A,CRV3,H1n,RC1 | W3 | T1b | Y | N | gate script fails on a duplicate effect | durable run; label scheduled-ingest; demo/run.ps1 defaults to Rust |
| BKC | Combination bundle: multi-kind, closure, 50-change limit, base precondition digest (CAP-13, 15, 17, 20, 22) | B | X-ARTIF | CX | 8 | 12 | BKF,BKA | W3 | T1b | N | N | bundle test fails over the 50-change limit | bundle of 3 kinds compiles; limits at 50 and 51 verified |
| BKE | Per-kind evaluation suite emitters and goldens: flow, decision model, agent, policy | B | X-GATE | CX | 10 | 14 | BK0,DEVAL | W3 | T1b | N | N | suite emitter fails for a flow queue-order case | one sealed suite per kind offline |
| CRV3 | Independent Claude review of PG, worker SQL, fencing, authority | D | L-GOV | CL | 5 | 8 | E8s | W3 | T1b | N | N | review checklist has an open finding | findings closed; reviewer differs from author |
| TRN3 | Claude consolidation train integrator for W3: lane merges in dependency order, one PR per 25 to 35 lane-hours, restack rule, local receipt | G | L-GOV | CL | 5 | 8 | - | W3 | T1b | N | N | train script fails when a lane branch is out of order | trains merged with receipts; stacked trains restacked within one fast gate |
| TRX3 | Codex train integrator for W3: lane merges into one train PR per 25 to 35 lane-hours, restack rule, root gate receipt | G | X-FACADE | CX | 2 | 4 | - | W3 | T1b | N | N | train script fails when a lane branch is out of order | trains merged with root gate receipts |
| DORIG | Original dataset path beyond the minimum slice (remaining families, namespaces) | D | X-SRC | CX | 6 | 10 | DORIGm | W3 | T2 | N | N | namespace test fails on a mixed query | all original families on sealed ranking |
| DREPLAY | Prequential and frozen replay protocol, replay clock, cohorts (spec 28.4) | D | X-LEARN | CX | 14 | 20 | DWIRE | W3 | T2 | N | N | replay test uses data after the cutoff | cohort replay reproducible by digest; goldens from FRZ0 |
| DORACLE | Policy oracle fixtures and security questions, not_evaluable default | D | X-GATE | CX | 8 | 12 | DWIRE | W3 | T2 | N | N | oracle returns pass without fixtures | 12 fixtures and 6 security questions |
| SB1 | U36 sandbox identity semantics | D | X-GATE | CX | 5 | 8 | DGATE | W3 | T2 | N | N | identity reuse across runs is accepted | identity per run enforced |
| RC2 | Fork semantics over durable_run_events (U34-F, FE) | D | X-LEARN | CX | 8 | 12 | DAUTH | W3 | T2 | N | N | fork test shares a parent sequence | fork replays by digest |
| CONF2 | Conformance suites for FakeCore versus bridge goldens and control-api black-box file (offline) | D | X-CONF | CX | 6 | 10 | CF0,FRZ0 | W3 | T2 | N | N | suite fails when FakeCore drifts from a golden | suite green on goldens; consumed later by swap-in |
| DFAM1 | Signal families 1 to 4: detectors, negatives and discards, fixtures | D | X-SENS | CX | 12 | 18 | DWIRE | W3 | T2 | N | N | family test finds no discard | 4 families each with positive, negative and discard fixtures |
| DFAM2 | Signal families 5 to 8 | D | X-SENS | CX | 12 | 18 | DFAM1 | W3 | T2 | N | N | family test finds no discard | 4 families covered |
| M2f | Full spend governance: per day and tenant, breaker, ledger versus gateway reconciliation | M | L-MODEL | CL | 8 | 10 | GT1B | W4 | T2 | N | N | breaker test fails to open at the daily cap | ledger equals gateway sum on 3 runs; kill switch under 10 s |
| K4 | JCS content-hash parity and wire drift (CAP-11, CAP-12) | K | L-CLIENT | CL | 6 | 9 | GT1A | W4 | T2 | N | N | parity vector fails for a non-ASCII key | all wire vectors of pin c814c2b match |
| K5f | Reconcile full: 409 ambiguity, evaluation_result_lost | K | L-CLIENT | CL | 3 | 4 | K5a | W4 | T2 | N | N | 409 idempotency_conflict misclassified | 3 ambiguity cases yield one effect |
| H2 | Authority full flows, rollout and rollback (ProposalRollout), kill-switch race, revoke with step-up issuer | H | L-AUTH | CL | 14 | 20 | AUS,H1b | W4 | T2 | N | N | rollback test leaves the alias on the candidate | publish, promote, revoke and rollback each leave a receipt; race test green |
| V3L | LLM-driven revision with per-attempt budget | V | L-EVAL | CL | 10 | 14 | V3r,M2f | W4 | T2 | N | N | third attempt exceeds the budget | 2 attempts within budget; revision cites the failed gate |
| EVE | Eval-suite emitter stand-in from ScenarioCase (U47) in seams/crates/eval | V | L-EVAL | CL | 7 | 10 | V1,FRZ0 | W4 | T2 | N | N | emitter fails for an unseen scenario shape | suite emitted for 3 non-shipped scenarios; label suite=claude-standin |
| ORC1 | Policy oracle reader with not_evaluable default (stand-in) | V | L-EVAL | CL | 4 | 6 | V2 | W4 | T2 | N | N | oracle returns pass without fixtures | not_evaluable by default; 5 fixtures |
| RPL1 | Prequential and frozen replay driver with replay clock over cohorts (stand-in for the spec continuous label) | E | L-ENGINE | CL | 9 | 13 | E7 | W4 | T2 | N | N | replay run uses future data | frozen and prequential runs reproducible by digest |
| SBL | Sandbox identity binding in core-bridge sandbox port (U36 stand-in) | I | L-BRIDGE | CL | 4 | 6 | BRG1 | W4 | T2 | N | N | sandbox call without identity is accepted | identity bound per run; cross-run use rejected |
| PGQ | PG window for quota and grant (U05) | E | L-PG | CL | 6 | 9 | E6w | W4 | T2 | N | N | grant window test lets an expired grant pass | quota window enforced across restart |
| BLOB1 | Blob store trait: PG-CAS default plus S3-compatible adapter on MinIO; AWS S3 at TA4 | E | L-PG | CL | 8 | 12 | MIG0 | W4 | T2 | N | N | blob round trip fails digest check | artifact bodies round trip via PG-CAS and MinIO |
| C1 | Console http provider, SSE with resume, decision panel, debug read routes | I | L-CONSOLE | CL | 16 | 24 | E4R,H1 | W4 | T2 | N | N | console contract test fails on resume | SSE resume after disconnect; decision panel shows gates |
| CON2 | U32 model, eval and memory panels in debug-console | I | L-CONSOLE | CL | 8 | 12 | C1,E5R | W4 | T2 | N | N | panel test fails with no data | three panels render from debug routes |
| Q2 | E2E-THREAD-02 chaos matrix, tamper, leakage, tenant tests; delete legacy host | Q | L-E2E | CL | 10 | 14 | GT1B | W4 | T2 | N | N | tamper test is accepted | chaos matrix of 8 faults green; legacy host removed |
| Q3 | Observability: metrics contract and alarm table with firing and resolved proof | I | L-OPS | CL | 8 | 12 | E4R | W4 | T2 | N | N | alarm test never fires | alarm fires and resolves within 5 min in the local stack |
| Q3c | traceparent code in control-api and core-client (CAP-64) | I | L-CAPI | CL | 3 | 5 | E4R | W4 | T2 | N | N | request without traceparent is accepted | traceparent propagated on every hop |
| QKG | known_gaps.json by SHA (CAP-64, U53) | Q | L-E2E | CL | 3 | 5 | Q1r | W4 | T2 | N | N | report without known_gaps fails | known_gaps listed per SHA in every run report |
| O1a | Runbooks (8), secrets lifecycle, retention table, redaction canaries | I | L-OPS | CL | 20 | 30 | Q3 | W4 | T2 | N | N | canary secret leaks into a log | 8 runbooks drilled once; canaries clean |
| M5b | Rust JevDecisionPort test against the roleplay JEV server | K | L-CLIENT | CL | 3 | 5 | M5a,K2 | W4 | T2 | N | N | port test fails on a 502 | port handles 200, 4xx, 502 |
| RC3 | Run fork (U34-F and FE) and live fork on durable runs | E | L-ENGINE | CL | 6 | 9 | RC1 | W4 | T2 | N | N | fork shares the parent idempotency key | fork run independent of parent; events linked |
| BKFL | Flow and compiled-tree kind, live: compile, dry-run, evaluate on real arms, approve, publish (own implementation) | B | L-BREADTH | CL | 10 | 14 | BK0,K3,V1 | W4 | T2 | N | N | flow dry-run test fails for add-flow of 4 keys | flow proposal published to staging alias and read back |
| BKTL | Template, policy and prompt-variant kinds, live | B | L-BREADTH | CL | 7 | 10 | BK0,K3,V1 | W4 | T2 | N | N | policy publish test fails | 3 kinds published and read back |
| BKDL | Decision-model kind (non-Jev providers), live, calibration unchanged | B | L-BREADTH | CL | 7 | 10 | BK0,K3,V1 | W4 | T2 | N | N | calibration change is accepted | decision model published; calibration digest unchanged |
| BKAL | Agent kind (authorized fields) with cascade prediction, live | B | L-BREADTH | CL | 7 | 10 | BK0,K3,V1 | W4 | T2 | N | N | cascade mismatch not detected | auto_bumped equals expected_derived on 3 cases |
| BKCL | Combination bundle live: closure, 50-change limit, forced limits at plus and minus 1 (CAP-56) | B | L-BREADTH | CL | 9 | 13 | BKFL,BKAL,BKTL | W4 | T2 | N | N | limit 51 accepted | bundle of 3 kinds published; limits verified at 50 and 51 |
| GT2 | Gate T2: kinds proven: flow, template, policy, decision_model, agent, bundle; chaos, console, spend, replay stand-in | Q | L-GOV | CL | 1 | 2 | BKCL,BKDL,Q2,C1,H2,M2f,ORC1,RPL1,EVE,CRV4,Q3,O1a | W4 | T2 | N | N | gate script fails on a missing kind | E2E-THREAD-02 green; third-party reproduction of GT0 run |
| CRV4 | Independent Claude review of T2 PRs | D | L-GOV | CL | 8 | 12 | Q2 | W4 | T2 | N | N | review checklist has an open finding | findings closed |
| REV4 | Independent review wave (Codex) of T2 PR tags; optional | D | X-REV | CX | 8 | 12 | - | W4 | T2 | N | N | review checklist has an open finding | findings closed |
| ENV11 | Lane scheduler with slot tokens (needs capacity beyond A) | ENV | L-ENV | CL | 4 | 6 | ENV8 | W4 | T2 | N | N | scheduler lets two stacks run | slot tokens enforced |
| ENV12 | Build farm: build container per Rust lane and a second stack (needs hardware, level C) | ENV | L-ENV | CL | 4 | 8 | ENV1,ENV3 | W4 | T2 | N | N | two builds collide on a target dir | 3 concurrent builds with no collision |
| TRN4 | Claude consolidation train integrator for W4: lane merges in dependency order, one PR per 25 to 35 lane-hours, restack rule, local receipt | G | L-GOV | CL | 8 | 12 | - | W4 | T2 | N | N | train script fails when a lane branch is out of order | trains merged with receipts; stacked trains restacked within one fast gate |
| TRX4 | Codex train integrator for W4: lane merges into one train PR per 25 to 35 lane-hours, restack rule, root gate receipt | G | X-FACADE | CX | 2 | 4 | - | W4 | T2 | N | N | train script fails when a lane branch is out of order | trains merged with root gate receipts |
| DFAM3 | Signal families 9 to 13 and detector evolution (U31) | D | X-SENS | CX | 14 | 20 | DFAM2 | W4 | T3 | N | N | detector evolution test regresses a metric | 13 families total; evolution gated by sealed holdout |
| DDIAG | Diagnosis SQL (U32 backend) over the sqlite lab | D | X-SENS | CX | 6 | 10 | DFAM1 | W4 | T3 | N | N | diagnosis query leaks a row | 5 diagnosis queries with receipts |
| DMEM1 | Learning protocol P4 and P5 temporal rules | D | X-LEARN | CX | 8 | 12 | DREPLAY | W4 | T3 | N | N | memory use before publication accepted | temporal rules enforced |
| DMEM2 | Durable memory and governed use breadth | D | X-LEARN | CX | 9 | 14 | DMEM1 | W4 | T3 | N | N | governed use without grant accepted | 10 governed-use cases |
| DSCEN1 | ScenarioFactory and counterfactual proxies | D | X-SCEN | CX | 8 | 12 | DEVAL | W4 | T3 | N | N | factory output differs by seed | 3 scenario families |
| DSCEN2 | Value kernels (value_model extensions) | D | X-SCEN | CX | 6 | 10 | DSCEN1 | W4 | T3 | N | N | value kernel unit mismatch accepted | kernels with unit tests |
| SB2 | U26 stateful bank sandbox world (real bank stays blocked CAP-41) | D | X-SCEN | CX | 8 | 12 | DSCEN1 | W4 | T3 | N | N | bank state leaks across runs | stateful world with 6 scenarios |
| DSRC | Additional source adapters (remaining original sources) | D | X-SRC | CX | 8 | 12 | DORIG | W4 | T3 | N | N | adapter accepts an unsupported source | each remaining source validated on sealed samples |
| DDOC | Spec text, additive amendments, status corrections for CAP-58 and CAP-61 | D | X-DOC | CX | 6 | 10 | DDOC1 | W4 | T3 | N | N | status table disagrees with code | status table matches the code at the baseline |
| DSPEC | Spec text for artifact kinds, breadth gates and stand-in swap protocol | D | X-DOC | CX | 4 | 6 | BK0 | W4 | T3 | N | N | link test fails for a missing section | amendments merged |
| TA1 | Local release script by digest, SBOM, audit, deploy manifest | A | L-INFRA | CL | 8 | 12 | IN0 | W4 | TA | N | N | manifest without digest accepted | release by digest; SBOM and audit in receipt |
| TA2 | Infra deltas: fixtures to pin c814c2b, engine alarms, core-migrate task, ECS Exec | A | L-INFRA | CL | 10 | 16 | Q3,TA1 | W4 | TA | N | N | infra contract test fails on stale pin | deltas planned offline |
| REV5 | Independent review wave (Codex) of T3 and TA PR tags; optional | D | X-REV | CX | 6 | 10 | - | W5 | T3 | N | N | review checklist has an open finding | findings closed |
| M6 | Rust model transport for the engine (U10): gateway client crate | K | L-CLIENT | CL | 10 | 14 | M2f,K1 | W5 | T3 | N | N | transport test fails on a timeout | engine calls the gateway under the ledger |
| BKOL | Tool kind live: executor registration in Pulso-owned runtime factories (bank stays blocked) | B | L-BRIDGE | CL | 8 | 12 | BK0,BKFL | W5 | T3 | N | N | tool proposal passes with no executor | sandbox tool proposed, dry-run, evaluated, published |
| BKJL | Jev decision-model kind live against the roleplay JEV; real Core side blocked(jev) | B | L-BREADTH | CL | 4 | 6 | BK0,M5a | W5 | T3 | N | N | Jev kind passes as supported | blocked(jev) shown; roleplay path exercised |
| BKEL | Per-kind evaluation suites live (own emitters) for flow, decision model, agent, policy | B | L-EVAL | CL | 8 | 12 | EVE,BKFL,BKDL,BKAL | W5 | T3 | N | N | suite changed after arms is accepted | sealed suite per kind on real arms |
| DUCK | DuckDB lab replacement for sqlite lab | E | L-CAPI | CL | 10 | 14 | E5R | W5 | T3 | N | N | query result differs from sqlite | same QueryReceipts on 20 queries |
| CAMP | Campaigns and alternatives portfolio | V | L-EVAL | CL | 10 | 16 | V3L | W5 | T3 | N | N | campaign shares a budget | campaign of 3 alternatives with do_nothing |
| P3 | Real Product source: read-only snapshot, PL-C4 guard in deployed path | P | L-PLAT | CL | 8 | 12 | P1 | W5 | T3 | N | N | guard test allows a write grant | inbound read-only run ends at insufficient_*  |
| P4 | Phase 2 readiness: superset profile, target registry and alias mapping | P | L-PLAT | CL | 8 | 14 | PX0,P1 | W5 | T3 | N | N | profile test lights an absent detector | superset profile tests green |
| WIKI | Wiki free exploration and transform | V | L-MEM | CL | 8 | 12 | E5R | W5 | T3 | N | N | wiki write without grant accepted | exploration within grants |
| DMEMC | Memory breadth live: durable head, confirm and contradict at scale | V | L-MEM | CL | 8 | 12 | MEM1,E7 | W5 | T3 | N | N | memory head lost after restart | durable head survives kill -9 |
| GT3 | Gate T3: kinds proven add tool, Jev(blocked), bundle with tool; stand-in retirement RG-5 decided per swap-in | Q | L-GOV | CL | 1 | 2 | BKOL,BKJL,BKEL,M6,CAMP,DMEMC,WIKI | W5 | T3 | N | N | gate script fails on a missing kind | matrix families by kinds with evidence |
| SWA | Swap-in: adopt Codex compile, gate, recompute, validation behind the step schema after conformance | E | L-ENGINE | CL | 6 | 9 | GT1A,~DMAPC,~DGATE,~DVREC,~DMAPV,~WDX | W5 | T3 | N | N | conformance test fails when outputs differ from the stand-in on FRZ0 cases | identical results on 20 cases; stand-in retired only by GT3 decision |
| SWP | Swap-in: adopt Codex pipeline reducer and authority state machine | E | L-ENGINE | CL | 5 | 8 | GT1A,~DPIPE,~DAUTH | W5 | T3 | N | N | transcript differs from the linear driver | C-9 transcripts equal; authority transitions equal |
| SWC | Swap-in: run Codex conformance suite on PG | E | L-PG | CL | 2 | 3 | GT1B,~DPGc,~CONF2 | W5 | T3 | N | N | suite fails on PG | receipt in PR body |
| SWB | Swap-in: adopt Codex per-kind modules and goldens against the live kinds | B | L-BREADTH | CL | 6 | 9 | GT2,~BKF,~BKT,~BKD,~BKA,~BKC,~BKE,~BKJ,~BKN,~BKX | W5 | T3 | N | N | golden differs from the live compile output | all Codex goldens green against live output |
| SWL | Swap-in: adopt Codex replay, oracle, detectors and memory breadth | E | L-ENGINE | CL | 5 | 8 | GT2,~DREPLAY,~DORACLE,~DFAM3,~DMEM2,~DSCEN2 | W5 | T3 | N | N | adoption test differs from stand-in | equal on FRZ0 cohorts |
| RVC3 | Claude review of Codex T2-T3 work (optional) | D | L-GOV | CL | 5 | 8 | ~DREPLAY,~DORACLE,~DFAM3,~DMEM2,~BKF,~BKC | W5 | T3 | N | N | review script lists unreviewed Codex commits | all reviewed |
| TRN5 | Claude consolidation train integrator for W5: lane merges in dependency order, one PR per 25 to 35 lane-hours, restack rule, local receipt | G | L-GOV | CL | 6 | 10 | - | W5 | T3 | N | N | train script fails when a lane branch is out of order | trains merged with receipts; stacked trains restacked within one fast gate |
| TA3 | First real terraform plan and fix cycle | A | L-INFRA | CL | 10 | 18 | TA0,TA2 | W5 | TA | N | N | plan fails on IAM or KMS | clean plan for staging |
| TA4 | First slice on staging (control-api, worker, PG) at the T1b gate | A | L-INFRA | CL | 8 | 14 | TA3,GT1B | W5 | TA | N | N | apply of the saved plan fails | slice answers health; human-approved apply |
| TA5 | Core, gateway and exporters on AWS; first check agent-core c814c2b Dockerfile and runbook | A | L-INFRA | CL | 10 | 20 | TA4 | W5 | TA | N | N | thread against staging fails | thread against staging URLs |
| TA6 | Alarm destinations, budgets, kill-switch and restore drills, soak | A | L-INFRA | CL | 20 | 32 | TA4 | W5 | TA | N | N | alarm mailbox unconfirmed | alarm fired and resolved; restore drill |
| LAB28 | Lab session lifecycle on staging (U28): create, TTL, revoke, tenant isolation | A | L-INFRA | CL | 6 | 10 | TA4 | W5 | TA | N | N | cross-tenant lab session accepted | isolation test green |
| GTA | Gate DEMO-3: the same demo thread against AWS staging URLs; kinds proven as GT1B | Q | L-GOV | CL | 1 | 2 | TA5,TA6,GT1B | W5 | TA | N | N | gate script fails on a local URL | thread against staging; alarm fired and resolved; rollback drill; prod untouched |
| O1b | Threat model, independent security review, remaining ops | I | L-OPS | CL | 20 | 30 | O1a | W5 | T5 | N | N | threat model has no abuse case | review findings closed |
| T5a | Load, chaos at spec numbers, 72h soak on compressed clock | Q | L-E2E | CL | 30 | 45 | Q2 | W5 | T5 | N | N | soak run breaks at hour 1 | 72h compressed soak with 0 duplicate effects |
| T5b | Security review fixes and retention and restore drills | Q | L-OPS | CL | 15 | 25 | O1b | W5 | T5 | N | N | restore drill fails | restore within the stated RPO and RTO |
| T5c | Browser and a11y matrix, DoD pack, third-party reproduction | Q | L-E2E | CL | 15 | 20 | Q2 | W5 | T5 | N | N | a11y check finds a blocker | spec DoD checklist signed with evidence |

### 8.1 Computed results (output of the checker below on this file)

| Quantity | Low | High |
|---|---|---|
| All remaining work: 214 WPs, tiers T0..T5 | 1337 h | 2024 h (midpoint 1680; with 10% churn about 1850) |
| Claude (CL) | 973 | 1467 |
| Codex (CX) | 364 | 557 |
| Claude / Codex share | 72.8% / 27.2% | 72.5% / 27.5% |
| Through T1b (tiers T0, T0.5, T1a, T1b): total, Claude | 679 total, 479 | 1018 total, 713; Claude 70.5% / 70.0% |
| Demo path (16 WPs) / evolution path | 76 / 1261 (5.7%) | 111 / 1913 (5.5%) |

Per tier, total and (Codex): T0 102-149 (2-3); T0.5 152-235 (57-88); T1a 275-403 (62-91); T1b 150-231 (79-123); T2 302-450 (81-124); T3 201-309 (83-128); TA 75-127 (0); T5 80-120 (0). Claude share of the lows by tier: 98.0%, 62.5%, 77.5%, 47.3%, 73.2%, 58.7%, 100%, 100%.

Per wave, total (Claude share low/high; WPs; lanes): W0 102-149 (98.0/98.0%; 23; 5); W1 170-262 (57.1/57.3%; 44; 16); W2 308-454 (70.8/70.5%; 50; 21); W3 172-264 (38.4/37.9%; 24; 12); W4 326-488 (73.3/72.5%; 44; 22); W5 259-407 (97.7/97.5%; 29; 14). Waves W1 and W3 are Codex-heavy by design (Codex runs its offline breadth lanes while Claude integrates); W5 is Claude-heavy because AWS and soak are Claude's. Why not lower: stand-ins for the Codex semantics are Claude WPs (CMP, GSI, STP1, AUS, PGC, EVE, ORC1, RPL1, SBL and the live per-kind WPs, about 117-172 h) and the user fixed the independence rule; Codex lanes grow in breadth (families, scenario kernels, memory breadth, per-kind goldens, conformance, spec text), not in criticality.

Gates (edges over Claude-only hard dependencies; counts and minimal-cut hours of the ancestor sets): GT0 15 ancestors, 76-111 h; GT05 33, 147-221 h; GT1A 60, 334-493 h; GT1B 71, 404-599 h; GT2 88, 553-815 h; GT3 86, 514-759 h; GTA 80. Independence counts: Claude->Codex hard edges 0; Codex->Claude edges to non-frozen WPs 0 (31 edges to the frozen pack); optional swap-in edges 39; no gate has a Codex or swap-in ancestor.

### 8.2 The checker (run on this file; it exits non-zero on any violation)

`python check_plan.py v4-plan.md D:\path\to\improvement-engine-main-ro` parses the table, the `FROZEN:` line and the `owners` block of section 9.1, and checks: unique ids, no dangling deps, acyclic, tier and wave monotone along hard edges, one owner per lane, non-empty `first_red` and `acceptance`, the independence rule (counts printed), gates free of Codex and swap-in ancestors, the `critical` column (float at most 4 h to GT1B), the demo path closed and Claude-only, every lane has a path map, and (with the repo argument) every tracked path at 853b029 has exactly one owner by the most specific glob.

```python
import re,sys,collections,subprocess
txt=open(sys.argv[1],encoding='utf-8').read()
rows=[[c.strip() for c in l.strip().strip('|').split('|')] for l in txt.splitlines()
      if l.startswith('| ') and l.count('|')==15 and not l.startswith('| id ')]
F=set(re.search(r'^FROZEN: (.*)$',txt,re.M).group(1).split())
T={t:i for i,t in enumerate('T0 T0.5 T1a T1b T2 T3 TA T5'.split())}
by={r[0]:r for r in rows}; assert len(by)==len(rows),'dup id'
lo=lambda r:int(r[5]); hi=lambda r:int(r[6]); mid=lambda r:(lo(r)+hi(r))/2
hard=lambda r:[d for d in r[7].split(',') if d!='-' and d[0]!='~']
opt=lambda r:[d[1:] for d in r[7].split(',') if d[0]=='~']
for r in rows:
    assert lo(r)<=hi(r) and r[10] in 'YN' and r[11] in 'YN' and r[12] and r[13],r[0]
    for d in hard(r)+opt(r): assert d in by,(r[0],d)
    for d in hard(r): assert T[by[d][9]]<=T[r[9]] and by[d][8]<=r[8],('mono',r[0],d)
order=[];seen=set()
def vis(n,p=()):
    assert n not in p,'cycle '+n
    if n in seen:return
    for d in hard(by[n]):vis(d,p+(n,))
    seen.add(n);order.append(n)
for n in by:vis(n)
lane=collections.defaultdict(set)
for r in rows:lane[r[3]].add(r[4])
assert all(len(v)==1 for v in lane.values()),'lane with two owners'
# independence
c2x=[(r[0],d) for r in rows if r[4]=='CL' for d in hard(r) if by[d][4]=='CX']
x2c=[(r[0],d) for r in rows if r[4]=='CX' for d in hard(r) if by[d][4]=='CL' and d not in F]
x2f=[(r[0],d) for r in rows if r[4]=='CX' for d in hard(r) if by[d][4]=='CL' and d in F]
sw=[(r[0],d) for r in rows for d in opt(r)]
assert all(by[a][4]=='CL' and by[d][4]=='CX' for a,d in sw),'optional edge must be Claude swap-in <- Codex'
print('Claude->Codex hard edges:',len(c2x),'| Codex->Claude edges to non-frozen:',len(x2c),'| Codex->frozen:',len(x2f),'| optional swap-in edges:',len(sw))
assert not c2x and not x2c
def anc(n,a=None):
    a=set() if a is None else a
    for d in hard(by[n]):
        if d not in a:a.add(d);anc(d,a)
    return a
gates=[r[0] for r in rows if r[0].startswith('GT')]
def cpm(g):
    A=anc(g)|{g};ES={}
    for n in [n for n in order if n in A]:ES[n]=max([ES[d]+mid(by[d]) for d in hard(by[n])]+[0])
    end=ES[g]+mid(by[g]);LF={n:end for n in A}
    for n in reversed([n for n in order if n in A]):
        for d in hard(by[n]):LF[d]=min(LF[d],LF[n]-mid(by[n]))
    return A,ES,end,{n:LF[n]-mid(by[n])-ES[n] for n in A}
for g in gates:
    A=anc(g)
    assert not [x for x in A if by[x][4]=='CX' and x not in F or opt(by[x])],('gate depends on Codex or swap-in',g)
    A,ES,end,fl=cpm(g)
    n=g;ch=[g]
    while [d for d in hard(by[n])]:n=max(hard(by[n]),key=lambda d:ES[d]+mid(by[d]));ch.append(n)
    print(g,'serial depth %.1f h'%end,'| gate ancestors',len(A)-1,'(all Claude or frozen) | chain',' > '.join(reversed(ch)))
A,ES,end,fl=cpm('GT1B')
assert {r[0] for r in rows if r[10]=='Y'}=={n for n in A if fl[n]<=4},'critical column mismatch'
D={r[0] for r in rows if r[11]=='Y'}
assert all(by[n][4]=='CL' and set(hard(by[n]))<=D and not opt(by[n]) for n in D),'demo path must be closed and Claude-only'
def S(f):return sum(lo(r) for r in rows if f(r)),sum(hi(r) for r in rows if f(r))
def share(f):
    a=S(f);b=S(lambda r:f(r) and r[4]=='CL');return a,b,'%.1f%% / %.1f%%'%(100*b[0]/a[0],100*b[1]/a[1])
print('WPs',len(rows),'| all',share(lambda r:True))
print('through T1b',share(lambda r:T[r[9]]<=3))
for t in T:print('tier',t,share(lambda r:r[9]==t))
for w in sorted({r[8] for r in rows}):print('wave',w,share(lambda r:r[8]==w),'WPs',sum(r[8]==w for r in rows),'lanes',len({r[3] for r in rows if r[8]==w}))
print('demo path',S(lambda r:r[0] in D),'WPs',len(D),'evolution',S(lambda r:r[0] not in D))
print('critical to GT1B',sum(r[10]=='Y' for r in rows),'WPs, midpoint hours',sum(mid(by[n]) for n in A if fl[n]<=4))
own=re.search(r'```owners\n(.*?)```',txt,re.S).group(1)
assert {l.split(': ')[0] for l in own.splitlines()}>=set(lane),'lane without path map'
if len(sys.argv)>2:
    def conv(p):
        o='';i=0;b=0
        while i<len(p):
            c=p[i]
            if p.startswith('**',i):o+='.*';i+=2;continue
            if c=='*':o+='[^/]*'
            elif c=='{':o+='(?:';b+=1
            elif c=='}':o+=')';b-=1
            elif c==',' and b:o+='|'
            elif c=='.':o+=r'\.'
            else:o+=c
            i+=1
        return re.compile('^'+o+'$')
    RU=[(l.split(': ')[0],conv(g),len(g.replace('*',''))) for l in own.splitlines() for g in l.split(': ',1)[1].split(' ; ')]
    def owner(f):
        m=sorted([(s,l) for l,r,s in RU if r.match(f)],reverse=True)
        return None if not m or (len(m)>1 and m[0][0]==m[1][0] and m[0][1]!=m[1][1]) else m[0][1]
    fs=[f for f in subprocess.check_output(['git','-C',sys.argv[2],'ls-files']).decode().split(chr(10)) if f]
    bad=[f for f in fs if not owner(f)];print(len(fs),'tracked paths,',len(bad),'unowned or tied');assert not bad
```

## 9. Partition for maximum parallelism

Scope is not reduced; it is partitioned. 214 WPs sit in 29 lanes (17 Claude, 12 Codex). Each lane owns disjoint paths and builds against frozen contracts, recorded packs and fakes; Claude lanes never wait on Codex lanes and vice versa.

### 9.1 Total path map (every tracked path of improvement-engine main 853b029 and of the infra repo belongs to exactly one lane)

Rule: the most specific glob wins; a tie fails the test. `{a,b}` is alternation. Paths marked "to create" do not exist yet (`crates/core/src/artifact_kind_*.rs`, `policy_oracle.rs`, `pipeline.rs`, `authority.rs`, `replay_*.rs`, `scenario_*.rs`, `detectors/`, `tests/conformance/`, `contracts/{pipeline,artifact-kinds,product,engine-*,control-api}`, `roleplay-llm/`, `local/{pg,observability,compose.d}`, `seams/**`, `docs/{reviews,spec-amendments,reports,runbooks,security,lanes}`, `agent-core-assets/{corpus,eval-suites}`, `scripts/{env,gov,dc}`); the OWNERS test (G0f) also covers them and extends the map for new journal and ADR files by the block table below. Existing files at 853b029: all 1683 tracked paths map (the checker prints it).

```owners
X-FACADE: Cargo.toml ; Cargo.lock ; rust-toolchain.toml ; .github/** ; scripts/verify-local-ci.ps1 ; scripts/run-local-*.ps1 ; scripts/init-local-env.ps1 ; tests/run-local-*.Tests.ps1 ; tests/test_postgres_ci_caller_contract.py ; crates/core/Cargo.toml ; crates/core/src/lib.rs ; crates/core/src/{debug_console,durable_run_events,model_provider,quota_grant,run_activity,run_config,run_timeline_v2,workflow_bridge}.rs ; crates/core/src/{pipeline,authority}.rs ; crates/core/tests/{model_provider,artifact_repository,model_attempt_repository,postgres_artifact_migration,postgres_run_events,tracer,quota_grant,run_activity,run_config}.rs ; contracts/pipeline/** ; migrations/0001_* ; migrations/0002_model_attempt_ledger.sql ; migrations/0003_* ; migrations/003[0-9]_*
X-CONF: crates/core/src/durable_jobs.rs ; crates/core/tests/durable_jobs.rs ; crates/core/tests/conformance/** ; migrations/004[0-2]_*
X-COMPILE: crates/core/src/{change_compiler,core_task}.rs ; crates/core/tests/{change_compiler,core_task}.rs
X-MAP: crates/core/src/{e0_builder_design,e0_core_draft_binding,e0_investigation_plan,e0_mechanism_resolution,e0_opportunity_qualification,e0_proposal_assembly}.rs ; crates/core/tests/{e0_investigation_plan,e0_mechanism_resolution}.rs
X-ARTIF: crates/core/src/artifact_kind_*.rs ; crates/core/tests/artifact_kind_*.rs ; migrations/004[3-4]_*
X-GATE: crates/core/src/{evaluation_plan,final_eligibility,paired_scenario,native_evaluation,e0_safety_oracle,independent_verifier,governed_registry,jev_decision,sandbox,policy_oracle}.rs ; crates/core/tests/{sandbox,evaluation_plan,final_eligibility,paired_scenario,native_evaluation_admission,e0_safety_oracle,independent_verifier,governed_registry,jev_decision,sandbox_identity,policy_oracle}.rs ; migrations/002[5-9]_*
X-SENS: crates/core/src/{autonomous_scout,deterministic_sensor,e0_deterministic_sensor,e0_query_lab,enriched_history,local_lab,local_simulation,platform_sensor,signal_portfolio}.rs ; crates/core/tests/{autonomous_scout,deterministic_sensor,e0_deterministic_sensor,e0_query_lab,enriched_history,local_lab,local_simulation,platform_sensor,platform_scout}.rs ; crates/core/src/detectors/** ; crates/runner/** ; migrations/004[5-6]_*
X-SRC: crates/core/src/{original_contact_projection,platform_discovery,platform_discovery_verifier,platform_observations,platform_source_policy,source_validation}.rs ; crates/core/tests/{original_contact_projection,platform_observations,platform_source_policy,postgres_platform_observations,source_validation}.rs ; crates/source-adapters/** ; contracts/*.schema.json ; contracts/{README.md,__init__.py,validate_fixtures.py} ; contracts/fixtures/** ; contracts/sources/** ; tests/test_artifact_envelope_contract.py ; tests/test_source_snapshot_partition_inventory.py ; migrations/0002_pulso_platform_observations.sql ; migrations/(001[5-9]|002[0-4])_*
X-LEARN: crates/core/src/{memory_store,governed_memory_use,memory_temporal_protocol,e0_frozen_memory_cycle,e0_frozen_memory_publication,e0_frozen_summary,e0_frozen_verifier,run_fork,wiki_scratch}.rs ; crates/core/src/replay_*.rs ; crates/core/tests/{governed_memory_use,memory_temporal_protocol,run_fork,wiki_scratch,postgres_memory_temporal_receipts,published_memory}.rs ; crates/core/tests/replay_*.rs ; migrations/0002_pulso_memory_control.sql ; migrations/0004_* ; migrations/(000[5-9]|001[0-4])_*
X-SCEN: crates/core/src/{value_model}.rs ; crates/core/src/scenario_*.rs ; crates/core/tests/{value_model}.rs ; crates/core/tests/scenario_*.rs ; migrations/004[7-9]_*
X-DOC: docs/IMPLEMENTATION_STATUS.md ; docs/architecture/** ; docs/data/** ; docs/gaps/** ; docs/platform-observations.md ; docs/local-e0-e2e-runner.md ; docs/spec-amendments/codex/**
X-REV: docs/reviews/codex/**
L-GOV: AGENTS.md ; CLAUDE.md ; CONTEXT.md ; README.md ; OWNERS.md ; .gitattributes ; .gitignore ; docs/BITACORA_PULSO.md ; docs/agents/** ; docs/adr/** ; docs/journal/00[0-9][0-9]-* ; docs/spec-amendments/claude/** ; docs/reports/gates/** ; docs/reviews/claude/** ; docs/lanes/** ; contracts/engine-run/** ; contracts/engine-steps/** ; scripts/gov/** ; contracts/artifact-kinds/**
L-ENV: local/compose.yaml ; scripts/env/** ; scripts/verify-local-all.ps1 ; scripts/verify-local-fast.ps1 ; scripts/dev.ps1 ; tests/test_local_compose_contract.py ; seams/xtask/** ; local/.env.example ; local/.secrets/**
L-MODEL: roleplay-llm/** ; local/core/gateway/** ; scripts/dc/** ; agent-core-assets/worlds/** ; agent-core-assets/corpus/** ; core-bridge/src/pulso_core_runtime/llm/** ; core-bridge/src/pulso_core_runtime/stages/** ; core-bridge/tests/llm/** ; core-bridge/tests/runtime/test_stages*
L-BRIDGE: core-bridge/** ; bridge-contract/** ; agent-core-assets/** ; local/core/** ; scripts/core/**
L-E2E: e2e-core/** ; demo/** ; docs/reports/e2e/**
L-PLAT: platform-contract/** ; platform-exporter/** ; platform-sim/** ; contracts/product/** ; seams/crates/control-api/src/correlation/** ; migrations/007[0-4]_*
L-CLIENT: seams/Cargo.toml ; seams/Cargo.lock ; seams/crates/core-client/** ; seams/crates/model-client/**
L-ENGINE: seams/crates/abi/** ; seams/crates/engine/** ; contracts/engine-handlers/** ; seams/crates/steps/**
L-CAPI: seams/crates/control-api/** ; contracts/control-api/** ; migrations/008[5-9]_*
L-PG: seams/crates/pg/** ; seams/crates/worker/** ; local/pg/** ; migrations/00[56][0-9]_*
L-EVAL: seams/crates/eval/** ; agent-core-assets/eval-suites/** ; migrations/009[0-4]_*
L-AUTH: seams/crates/authority/** ; local-identity/** ; migrations/008[0-4]_*
L-MEM: seams/crates/memory/** ; migrations/007[5-9]_*
L-CONSOLE: debug-console/**
L-OPS: docs/runbooks/** ; docs/security/** ; docs/contracts/metrics.md ; local/observability/**
L-BREADTH: seams/crates/artifacts/**
L-INFRA: infra:**
```

New numbered files: migrations by range (existing 0001 and 0003 and `0002_model_attempt_ledger` X-FACADE; `0002_pulso_memory_control` and 0004 X-LEARN; `0002_pulso_platform_observations` X-SRC; MIG0 orders the three 0002 files lexically and never edits applied files; tests `include_str!` those names). Codex: X-LEARN 0005-0014, X-SRC 0015-0024, X-GATE 0025-0029, X-FACADE 0030-0039, X-CONF 0040-0042, X-ARTIF 0043-0044, X-SENS 0045-0046, X-SCEN 0047-0049. Claude: L-PG 0050-0069, L-PLAT 0070-0074, L-MEM 0075-0079, L-AUTH 0080-0084, L-CAPI 0085-0089, L-EVAL 0090-0094, reserve 0095-0099. ADRs (current maximum 0005): Claude 0100-0269 in blocks of 10 in alphabetical lane order (L-AUTH 0100, L-BREADTH 0110, L-BRIDGE 0120, L-CAPI 0130, L-CLIENT 0140, L-CONSOLE 0150, L-E2E 0160, L-ENGINE 0170, L-ENV 0180, L-EVAL 0190, L-GOV 0200, L-INFRA 0210, L-MEM 0220, L-MODEL 0230, L-OPS 0240, L-PG 0250, L-PLAT 0260); Codex 0300-0395 in blocks of 8 (X-ARTIF 0300, X-COMPILE 0308, X-CONF 0316, X-DOC 0324, X-FACADE 0332, X-GATE 0340, X-LEARN 0348, X-MAP 0356, X-REV 0364, X-SCEN 0372, X-SENS 0380, X-SRC 0388). Journal files follow the repo convention `docs/journal/NNNN-<lane>-<slug>.md` (last is 0067; 0068-0099 L-GOV; Claude lanes from 0100 in blocks of 16 in the same order, Codex from 0400). The shared BITACORA is outside the repo (`D:\.codex\factored\docs\pulso_implementation_shared-_bitacora.md`): one consolidated entry per team about every 15 minutes (ids CL-/CX-) from the team's orchestrator; lanes write only their repo journal files. Spec amendments follow the existing precedent `V3_SUCCESSOR_AMENDMENTS_CLAUDE.md` in the shared docs folder (Codex `docs/spec-amendments/codex/`), mirrored once per train.

| Lane | Team | WPs | Hours | Review class |
|---|---|---|---|---|
| L-AUTH | CL | 5 | 36-53 | RC1 |
| L-BREADTH | CL | 7 | 50-72 | RC1 |
| L-BRIDGE | CL | 5 | 24-37 | RC2 |
| L-CAPI | CL | 6 | 47-66 | RC1 (auth, replay), RC2 rest |
| L-CLIENT | CL | 10 | 71-101 | RC1 |
| L-CONSOLE | CL | 2 | 24-36 | RC3 |
| L-E2E | CL | 9 | 77-113 | RC2 |
| L-ENGINE | CL | 13 | 98-147 | RC2 (authority and gate stand-ins RC1) |
| L-ENV | CL | 16 | 46-75 | RC3 |
| L-EVAL | CL | 8 | 58-85 | RC2 |
| L-GOV | CL | 33 | 120-183 | RC3 |
| L-INFRA | CL | 8 | 74-125 | RC2 (apply is human-approved) |
| L-MEM | CL | 3 | 24-36 | RC2 |
| L-MODEL | CL | 12 | 61-89 | RC1 (ledger, scanner), RC2 rest |
| L-OPS | CL | 4 | 63-97 | RC3 |
| L-PG | CL | 8 | 61-92 | RC1 |
| L-PLAT | CL | 7 | 39-60 | RC2 |
| X-ARTIF | CX | 7 | 47-70 | RC2 |
| X-COMPILE | CX | 3 | 19-29 | RC1 |
| X-CONF | CX | 3 | 15-25 | RC2 |
| X-DOC | CX | 3 | 12-19 | RC3 |
| X-FACADE | CX | 8 | 26-45 | RC1 (authority), RC3 rest |
| X-GATE | CX | 6 | 41-61 | RC2 |
| X-LEARN | CX | 4 | 39-58 | RC2 |
| X-MAP | CX | 1 | 6-10 | RC2 |
| X-REV | CX | 7 | 33-52 | RC3 (own reports reviewed by Claude RVC) |
| X-SCEN | CX | 3 | 22-34 | RC2 |
| X-SENS | CX | 6 | 56-86 | RC2 |
| X-SRC | CX | 7 | 48-68 | RC2 |

`crates/core/Cargo.toml`, `lib.rs`, the root `Cargo.toml`/`Cargo.lock`, `.github/**` and the Codex gate scripts have ONE integrator, X-FACADE (XSTUB adds empty `mod` stubs and `[[test]]` entries for every planned module in one wave-0 commit, so other Codex lanes own only their files afterwards). `seams/Cargo.toml` and `seams/Cargo.lock` have one integrator, L-CLIENT (K0 declares every crate up front; a new dependency is a `[DEP-ASK]`). The `verify-local-ci.ps1` double ownership of v3 is gone: Codex gate scripts and their Pester tests are X-FACADE; Claude's gate wrappers are the new files `scripts/verify-local-all.ps1` and `verify-local-fast.ps1` (L-ENV), which call the Codex script unchanged as a leg. L-BRIDGE owns `core-bridge/**` (except `llm/`, `stages/` and their tests, which are L-MODEL), `bridge-contract/**`, `agent-core-assets/**` (except worlds, corpus, eval-suites), `local/core/**` (except `gateway/`) and `scripts/core/**`; K2 and K3 request route or mock changes from it through BRG1.

K2 and `core_task.rs`: K2 touches no `crates/core` file (its own 1.3.0 DTOs); the `core_task.rs` 0.5.0 -> 1.3.0 change is CT1, Codex-executed under a `[CONTRACT-CHANGE]` stanza with Claude's recorded review; nothing on the Claude path waits for it. Consent clause (U-2, optional): only if the user wants Claude to execute edits in Codex-owned files while Codex is frozen, one sentence names the files; default none, because the stand-ins make it unnecessary.

### 9.2 Contracts: the 13, reconciled with the code (digest-pinned, append-only, same black-box test file against double and real)

| # | Contract | State at 853b029 | Published by | Frozen |
|---|---|---|---|---|
| C-1 | Core wire: `bridge-contract/` OpenAPI (11 operations), schemas, conformance, examples | exists | L-BRIDGE | now |
| C-2 | run report schema, `doubles[]`, honesty tests | to create (G1) | L-GOV | CF0 |
| C-3 | step JSON in/out (`contracts/engine-steps/`) | to create (CONTR); only 171 types derive serde, so steps use DTOs | L-GOV | CF1 (after GT05) |
| C-4 | job handler ABI crate `seams/crates/abi` | to create (E1) | L-ENGINE | CF1 (after TW-1) |
| C-5 | `CoreClient` trait and `FakeCore` from C-1 goldens | to create (K2) | L-CLIENT | CF1 |
| C-6 | `contracts/control-api/openapi.yaml`; the existing double is `e2e-core/src/codex_standin/*.py` | to create (E5L) | L-CAPI | CF1 |
| C-7 | `DurableJobRepository` (`durable_jobs.rs:111`) plus claim-next signature | trait exists, claim-next to add (DJC) | FRZ0 signature, X-CONF | CF0 |
| C-8 | `ChangeSpec` and `ScenarioCase` schemas (no such Rust types exist: only `UntrustedChangeSpec` and non-deserialisable `AuthorizedChangeSpec`) | new schemas in FRZ0, Codex implements to them | L-GOV | CF1 |
| C-9 | pipeline transcripts rev1 | seed in FRZ0 | L-GOV, X-FACADE | CF1 |
| C-10 | gate result shape | shape in FRZ0; Codex fills semantics | L-GOV | CF1 |
| C-11 | `platform-contract/` 1.1.0 event catalogue plus `release.*` | exists, `release.*` added by PX0 | L-PLAT | now |
| C-12 | roleplay queue protocol, scanner allow-list, ledger schema | to create (M0RP, TPS, RPP) | L-MODEL | CF0 |
| C-13 | allocation tables (migrations, ADR, journal, OWNERS) | this section | L-GOV | CF0 |

Draft contracts are `provisional` at CF0 and consumers start against the published digest; freezing happens at the first gate that exercises them (CF1), so CF0 is not a rewrite point. Narrow waists: C-1, C-4, C-3, C-6, C-5, C-2, C-7. Change protocol: a breaking change is a new versioned file plus `[CONTRACT-CHANGE id reason migration]`.

### 9.3 Conflict matrix

| Shared item | Rule |
|---|---|
| `local/compose.yaml`, `scripts/dev.ps1` | only L-ENV; per-lane fragments `local/compose.d/<lane>.yaml` are owned by that lane and pulled in with `include`; `tests/test_local_compose_contract.py` must stay green |
| Gate and CI scripts | Claude wrappers L-ENV; Codex gate X-FACADE |
| Docs indexes | generated at train time by the integrator from `docs/lanes/<lane>/**` |
| Spec | additive amendments per team; the owning team folds them |
| `OWNERS.md` | generated; a test fails on unowned or doubly-owned paths |
| Integration branches | `train/<wave>-<team>` built by the team integrator (TRN, TRX) from `lane/<lane>/<wave>` |
| Vendor dir `D:\.codex\factored\vendor` | read-only, ENV4; Codex read access is ask U-17 |

### 9.4 Waves and parallel width

Width = lanes with WPs in the wave (checker output); the live count is bounded by capacity and worktrees. W0 DEMO-0 sprint plus enabling pack: 5 lanes (Claude L-GOV, L-MODEL, L-E2E, L-PLAT; Codex X-FACADE for XSTUB); GT0 at the end. W1 DEMO-1a: 16 lanes; W2 DEMO-1: 21; W3 DEMO-2: 12; W4: 22; W5: 14. Claude lanes per wave 4, 8, 12, 4, 15, 13 and Codex 1, 8, 9, 8, 7, 1 against caps of 8+1 and 4+1 live worktrees: live = min(lanes, cap), the rest queue in the order of the lane list of that wave (critical-chain lanes first). Serial spine inside each wave: W0 G1 > M3 > Q1r; W1 CMP > E3b; W2 K1 > K2 > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1; W3 PGJ > E6w > E7; W5 TA4 > TA6.

### 9.5 Consolidation trains, worktrees, restack

- One consolidated PR per 25-35 lane-hours per team (not per feature, not per wave): about 5, 5, 9, 3, 10, 11 Claude PRs and 1, 4, 4, 5, 4, 1 Codex PRs over W0..W5; at most 3 open per team; each PR carries the `verify-local-all` receipt and `doubles[]` in the body. Lane branches `lane/<lane>/<wave>` merge into `train/<wave>-<team>` in dependency order; fast gate after each merge, full gate once per train.
- Never wait for a merge: a train branches from the head of the PR it stacks on. Restack rule: when the base PR changes, the integrator rebases the stacked train in the same session, re-runs the fast gate and the tests of files touched by the change, and the owning lane resolves conflicts; no one rewrites another lane's branch.
- Worktrees: 58 are registered today. WTR1 (Claude) and WTR2 (Codex) inventory and remove merged ones and list the unmerged for the user; target at most 25 registered before W1 starts; afterwards live worktrees are capped per wave as in 9.4 (counting legacy ones). Idle lanes hold none.
- Each team's PR train is independent: Claude trains go through `gh`, Codex trains through its GitHub connector; hand-over of unpublished work is a `git bundle` in `D:\.codex\factored\exchange\`.

### 9.6 Subagents inside a lane and the tripwires

Per active lane at capacity A: one implementer (strict TDD, the WP's first RED); test authors and reviewers are pooled and hold no worktree (a lane's concurrency = min(width, available implementers)); at B and C the pools grow. Work needing no cargo slot (schemas, goldens, fakes, Python, SQL design, runbooks, Terraform plans, TypeScript, docs) runs in parallel with Rust lanes. Review loops by class: RC1 3 loops (correctness against RED and goldens; adversarial: forgery, replay, egress, fencing, budget; verification of fixes plus mutation tests), RC2 2 loops (semantics; edge cases and negatives), RC3 1 loop at train level against a checklist. Loops 2 and 3 are the WPs CRV1-4 (distinct fresh-context Claude reviewers, gating) and REV1-5 (Codex, optional second reviewer), plus RVC1-3 (Claude reviewing Codex, optional). Tripwires (objective; none waits on the user): TW-0 (WP) seams build offline in the Claude account and CF0 published, Codex side only if U-1; TW-1 K2 live on the real image (same `Idempotency-Key` twice gives one run, scout receipt with tokens and cost); red means stop Rust server work, Track R reduces to steps and conformance; TW-2 E5L suite green on the Rust server with a roleplay scout; red means stay on the Python host with Rust steps and re-base; TW-3 at least 6 of 10 ratchet steps hosted by the Rust shell (the ratchet records `host` per step); red means re-plan RG gates with the user informed.

## 10. Coordination protocol between teams

1. Hand-offs happen only through versioned artifacts (digest-pinned packs, contract files, train tags) and the journal; no team blocks on the other's branches. Claude->Codex edges go only to wave-0 frozen artifacts; Codex->Claude flow is optional swap-ins.
2. Journal tags: `[CONTRACT-PUBLISHED]`, `[CONTRACT-CHANGE]`, `[ASK]`, `[DEP-ASK]`, `[BLOCKED]`, `[DONE]`, `[HANDOFF]`, `[FINDING]`, at most 8 lines each, first line UTC timestamp and team; `[DONE]` carries target, sha, `doubles[]`, agent-hours, tests added, gate minutes (telemetry for recalibration). One 10-row state table at the start of each session. `[ASK]` carries a default only where the default is safe; silence is never approval (two-team plan sections 16.6 and 17.1).
3. Codex lanes run offline: against the FRZ0 pack, goldens and fixtures only; no Podman, live PG or live Core. Claude never runs Codex tests for it on the Claude path; PG runs of Codex suites are the optional SWC.
4. Codex onboarding brief at unfreeze (G0f, one page): current main, the G0gr export list, `seams/` is Claude's, lane map, ranges, vendor dir, the data-class rule for developer agents.
5. Blocked behaviour: nobody idles; a blocked lane records `[BLOCKED]`, takes the documented default and moves on. Humans of agent-core and Product are never contacted directly; the user relays one consolidated message (journal reaches only Codex).
6. Nexus: checkpoint receipts go through `nexus checkpoint --stdin` in the workspace outbox with an allowlisted project id and a stable idempotency key; nobody writes the vault.

## 11. Methodology compliance (every standing rule)

| Rule | How honoured |
|---|---|
| Strict TDD | every WP names a first RED in the table; spikes (SNET, E9s) are rewritten test-first |
| Independent adversarial reviews, 1-3 loops | classes RC1-RC3 per lane (9.1 table, 9.6); CRV and REV WPs are in the totals |
| Consolidated worktrees and PRs, limited worktrees | 9.5: one PR per 25-35 lane-hours, caps, legacy 58 retired, restack rule |
| Local CI before PR | `verify-local-all` receipt in every PR body (G0d, ENV6); replay-mode E2E is the pre-PR gate, live per train |
| Real dependencies via Podman, machine per team | Claude's `pulso-dev` stack; Codex has none usable, so its lanes are offline by design |
| Never depend on a merge | trains stack on the PR head; independence rule |
| Parallelize with subagents | 9.4, 9.6; roleplay responder lane (3.3) |
| Two teams coordinate only through the shared journal | section 10 |
| Each team owns its part | 9.1 path map; consent clause for crossings |
| Spec is the source of truth; additive amendments by the owning team | amendments per team; the stand-in label and PX0 are amendments |
| Humans of other teams unreachable | EXT-1..3 relays |
| Infra: one company, shared foundations, defer to the agent-core infra owner (jzapata), never duplicate | TA0 asks first; TA5 reuses agent-core's Dockerfile and runbook where they fit |
| Stay in scope (consume agent-core and llm-gateway, do not build their internals) | the shim is a test double behind their HTTP contract; no Core or gateway edits |
| debug-console is OUR backoffice, not the product UI | C1, CON2 |
| Docs in English; never touch D:\Nexus | all; no WP reads or writes it |
| Do not stop on failures | `[BLOCKED]` plus default plus next WP; red tripwires re-base |
| AGENTS.md rules (Windows first, no development in WSL without an ADR) | ENVADR plus user ack before ENV1; root gate stays Windows |

## 12. What is not in the spec, and where it goes

| Topic | Decision | WP | Tier |
|---|---|---|---|
| Machine and build environment | measure first, three levels | ENV0-ENV12 | T0.5-T2 |
| Deployment pipeline | local release script by digest, SBOM, audit, human apply of a saved plan | TA1 | TA |
| Runtime ops, incidents | eight runbooks, single operator today | O1a | T2 |
| Secrets lifecycle, retention, redaction canaries | uncommitted env files locally, loaded by a human on AWS | O1a, TA4 | T2/TA |
| Cost and budget governance | one owner: the Python ledger; ceilings, breaker, kill switch, reconciliation | M2a, M2f, TA6 | T0/T2 |
| Tenant model | single tenant per environment, RLS-ready, cross-tenant tests | Q2 | T2 |
| Product Phase 2 availability | capability profile, superset tests; outbound `blocked(product-phase-2)` | PX0, DPL2, P4 | T0.5-T3 |
| llm-gateway policy gaps | enforced in our runtime; EXT-3 | M2a, TPS | T0 |
| Observability, liveness | traceparent, metrics, alarm firing and resolved, stall metric | Q3, Q3c, E7 | T1b/T2 |
| Data retention, E0 replacement | data classes, tombstone erasure | O1a, DC0 | T0/T2 |
| Rollout and rollback of published proposals | `ProposalRollout`, human-gated revoke | H2 | T2 |
| Human approval UX and notification | decision card (CLI) then console panel; notification adapter with SLA | H1, H1n, C1 | T1a-T2 |
| Blob store (spec says PG plus S3) | PG-CAS first, S3-compatible adapter, AWS S3 at TA4 | E1, BLOB1 | T1a/T2 |
| CAPs: 11 and 12 JCS parity, 13-15 and 17-22 compile breadth, 23 release_settings denied, 48 bootstrap CLI, 56 forced limits, 64 known_gaps | each has a WP | K4, BK0-BKCL, BOOT, QKG, Q3c | T0-T2 |
| U05 PG window, U10 Rust model transport, U26 and U36 sandbox, U28 lab session, U32 panels, U34 run control and fork | each has a WP | PGQ, M6, SB1, SB2, SBL, LAB28, CON2, RC1-RC3 | T1b-T3 |
| Spec-22 fixture families, PL-02..04 and PL-06..10, PL-C6 | Codex offline fixtures; Claude's E4R has its own tests | FX22a, FX22b, FX22p, DPL1, DPL2, DDOC1 | T1a |
| Prequential replay and oracle (28.3-28.5) | Claude stand-ins, Codex protocol as swap-in | RPL1, ORC1, DREPLAY, DORACLE | T2 |
| Hosted CI | `verify-local-all` receipts are merge evidence | G0d | T0.5 |
| Spend of AWS | low hundreds of USD per month for staging, to be computed in TA3 (estimate) | TA3 | TA |

## 13. Estimates, minimum cut and sessions

Hours: 1337-2024 raw (midpoint 1680, about 1850 with a 10% churn allowance for pin bumps, environment tails and re-records; review loops are explicit WPs, not hidden). Through T1b: 679-1018 (midpoint 848, about 933 with churn). The minimum viable cut is the ancestor set of each gate (8.1); never cut: independent verifier actor, `do_nothing`, honest `unlinked`, human gate, bounded revision, negatives, `doubles[]`, budget ceiling, data-class gate, treated-payload scanner.

Sessions per gate (a session is about 8 wall hours; capacity per section 7 is an assumption, so this is a model, not data; rule: sessions = max(capacity bound, serial floor), bound = 1.10 x Claude-ancestor midpoint hours / capacity, floor = 1.10 x serial depth / 7.5 h; only DEMO-0 is dated, the rest are conditional ranges that re-baseline at TW-1):

| Gate | Serial depth | A 14-18: central (range) | B 18-24 | C 35-45 (floor binds) |
|---|---|---|---|---|
| DEMO-0 (GT0) demo path only | 25.5 h | 6.4 (5.7-7.3) | 4.9 (4.3-5.7) | 3.7 |
| DEMO-0 with the enabling pack on the same agents (+27 h) | 25.5 h | 8 (7.2-9.3) | 6 (5.4-7.2) | 4.0 |
| DEMO-1a (GT05) | 39.5 h | 12.7 (11.2-14.5) | 9.6 (8.4-11.2) | 5.8 |
| DEMO-1 (GT1A) | 117.0 h | 28.4 (25.3-32.5) | 21.7 (19.0-25.3) | 17.2 |
| DEMO-2 (GT1B) | 118.5 h | 34.5 (30.6-39.4) | 26.3 (23.0-30.6) | 17.4 |
| DEMO-3 (GTA) | 157.0 h | 41.6 (36.9-47.5) | 31.7 (27.7-36.9) | 23.0 |
| DEMO-4 (GT2) | 142.0 h | 47.0 (41.8-53.7) | 35.8 (31.4-41.8) | 20.8 |
| DEMO-5 (GT3) | 154.0 h | 43.8 (38.9-50.0) | 33.3 (29.2-38.9) | 22.6 |

Reading: DEMO-0 is the only near-term promise (about 6 sessions, medium-low confidence, about 60% by 7 at A); the Claude path to DEMO-1 and DEMO-2 is long because Claude now carries the stand-ins itself, and that is the price of independence; breadth lanes run in parallel and finish earlier than their gates. If Codex is frozen nothing on this table changes.

## 14. Risks

| # | Risk | P/I | Mitigation |
|---|---|---|---|
| R1 | DEMO-0 builder output cannot become a valid artifact (S-MAP) | medium/high | `unlinked` and `not_evaluable` are valid endings; builder-only validated against ReadBase; mapping never keyed to the winning category |
| R2 | `agent_roleplay` read as model quality | medium/high | status vocabulary, honesty tests, `quality_claims: forbidden`, SMOKE measures |
| R3 | E0 text reaches a third party (responder, developer agent, git) | medium/high | TPS scanner, DC0 push scan, treated-only rule, agents work from schemas |
| R4 | Roleplay latency (15-90 min per live run) and one responder slot | high/medium | replay by digest, 4-8 live runs per session, live windows |
| R5 | Claude concentration: 72-73% of hours and the whole critical path on one team | high/medium | per-lane journals, pooled reviewers, trains, Codex independent lanes, tripwires |
| R6 | Stand-ins diverge from Codex semantics | medium/medium | swap-in conformance tests on FRZ0 cases; RG-5; labels in `doubles[]` |
| R7 | Cargo and RAM contention (1.7 GB free host, 10 GB VM) | high/medium | ENV0 first, replay gate, one stack, caps; hardware options C1-C3 |
| R8 | Contract drift between lanes | high/high | digest pins, FRZ0 pack, same black-box file on double and real |
| R9 | Pin churn (5 bumps in 21 h, `VERSION` constant) | high/medium | G2 gate on SHA plus manifest digest |
| R10 | agent-core PRs 23, 24, 28 never reach main; N8-02 ambiguous 409 | high/medium | no Core-side Jev; reconcile read disambiguates |
| R11 | Hosted CI red hides regressions | high/medium | local receipts; U-6 |
| R12 | Podman instability (cgroups, ports) | medium/high | doctor smoke before any `real` label |
| R13 | First AWS apply fails | high/medium | 10-18 h budgeted (TA3), offline plan early |
| R14 | Python host becomes permanent | medium/high | freeze rule, RG-1..4, deletion in Q2 |
| R15 | Core quotas (10 proposals/24 h, 20 evals/proposal) throttle live runs | medium/medium | fresh Core DB per run, injected clock |
| R16 | Optimistic "done" claims | medium/medium | every `[DONE]` needs a receipt with `doubles[]` |
| R17 | ENV gains smaller than hoped | medium/medium | ENV0 rule: keep only at least 1.3x or 5 min |

## 15. Asks (order: the user's one-sentence decisions first, then external relays; silence is never approval)

Each ask lists the safe default taken without an answer; "NO DEFAULT" means the item stays undone. None blocks the demo path.

| # | Ask | Safe default |
|---|---|---|
| 1 (U-13, resolved with a condition) | Confirm in one sentence: the roleplay responder receives only treated payloads (after the spec's pre-ModelPort treatment), never raw E0/CSV rows or raw conversation text, enforced by the shim scanner; you may lift it later | treated payloads only |
| 2 (U-1) | Lift the Codex scope freeze (CX-0180) for offline lanes only (no Podman, no live PG) | Claude path proceeds alone; Codex breadth and swap-ins wait |
| 3 (U-14a) | Acknowledge the ADR that allows a Linux build container inside the existing WSL VM despite AGENTS.md | measure only; ENV1 stays undone |
| 4 (U-14b) | Approve named downloads: Linux toolchain image, optional sccache and nextest, optional local model (name, source, size) | none downloaded; rung-up to local GPU waits |
| 5 (U-9) | May treated E0 payloads go to a hosted REAL model (rung-up DEMO-2)? NO DEFAULT for yes | nothing leaves local or own infra except treated payloads to the roleplay responder |
| 6 (U-4) | Optional hosted key in an ignored env file with a hard cap (suggest USD 20 through DEMO-1a, 100 through T2, 2 per run, 10 per day), synthetic data only; and `JEV_API_KEY` for the real gateway `/v1/jev` | no hosted calls; Jev only through the shim |
| 7 (U-15) | A 15-minute approver session at DEMO-1 to perform one recorded CLI approval | local issuer `simulated` |
| 8 (U-16) | Human notification channel for `waiting_human` (webhook or mailbox) | file sink |
| 9 (U-17) | Give the Codex account read access to the vendor dir and permission for `cargo build --offline` (ENV10) | Codex builds with its own cache |
| 10 (U-14c) | Hardware or runner option C1, C2 or C3 (section 7) | capacity A or B |
| 11 (U-12) | Review-loop classes of 9.6 and the spike exemption from strict TDD | full ritual for every WP, no exemption |
| 12 (U-2, optional) | Consent for Claude to edit named Codex-owned files while Codex is frozen | none; stand-ins used |
| 13 (U-5) | AWS: staging account and region, SSO profile, state bucket, owner of shared foundations (defer to the agent-core infra owner), alarm mailbox, monthly ceiling, approval of each apply | offline plan only |
| 14 (U-6, U-7, U-8) | GitHub Actions budget or a self-hosted runner; announced free-RAM windows for live runs; standing delegation to merge consolidated trains with a green local receipt | local receipts; live run skipped with `insufficient_memory`; PRs wait for the user, never merged by default |
| EXT-1 | agent-core team: land or hold PRs 23, 24, 28; distinct `idempotency_in_progress` code (N8-02); changelog and manifest digest per pin; advisor-principal isolation; Core workload slice and one `pulso-core-runtime` name in AWS; overlap of `registry-e2e` with `e2e-core` | plan without them; no Core-side Jev; plan-only AWS |
| EXT-2 | Product team: read mechanism and payload per `event_type`; `event_log.sequence` contiguity; Phase 2 roadmap; demo-row marker; retention; whether text may reach hosted models; which registry and alias the Product runtime resolves; approver identity | simulator and capability profile; no outbound action |
| EXT-3 | llm-gateway owners: push the first tag (`release.yml` exists) and GHCR digest; per-consumer alias allowlist and price caps; rate limit; provider request id echo; `Idempotency-Key`; stable error `code`; `/v1/jev` status | build from SHA 63155b6; client-side ceiling and ledger |

## 16. Residual uncertainties (falsifiers, read-only first)

1. Whether Codex's account can read the vendor dir, build offline and reach a loopback PG (ENV10, ask 9).
2. Whether the spec's pre-ModelPort treatment is already a callable function or must be re-implemented to define the scanner allow-list (TPS reads it first).
3. Whether `local-sim` E0 output feeds the builder design input without a new adapter (ED0, SMAP).
4. Whether Core agent nodes tolerate multi-minute model calls (SNET) and whether the responder lane can run as stateless background subagents.
5. Real gains of ENV items (all "to measure"); Windows versus Linux parity.
6. Whether the agent platform allows the concurrent agents assumed at B and C.
7. PG 16 (Core runtime) versus 17 (engine CI) behaviour (G0gr preflight).
8. Whether Core quotas bite the roleplay live runs; the `usage_estimated` metering path of the shim against the reservation logic.
9. Per-type counts (521 pub types, 59 `compile_fail`) are re-measured by G0gr.
10. Claude-side Rust throughput is unmeasured (no Rust record in this repo); hours for new-seam Rust are 0.8-1.4x and re-baselined at TW-1.

## 17. Review history

| Pass | What it did | What it changed |
|---|---|---|
| v1-A, v1-B, v1-C | thin thread, deployable and operable, risks and parallelism | tiers, packages, lanes, AWS, risks |
| v2 synthesis | merged them | `doubles[]`, S-MAP spike, Claude-owned seams |
| Reviews 1-4 | code reality, teams and process, real-ness, efficiency and backward pass | re-spec of K2/K3/PG, `seams/` workspace, git rule for E0, author separation, package-derived totals, strangler order |
| v3 | single document, 112 WPs, 26 lanes | partition, E0-ENV, tripwires |
| v3 reviews A, B, C | consistency (8 HIGH), backward pass (1 BLOCKER, 7 HIGH), feasibility (7 HIGH) | all dispositioned in the appendix |
| v4 author, coordinator directives | independence rule, DEMO-0 organizing principle, roleplay-rung decision with treated payloads | 214 WPs, 29 lanes, demo_path column, Claude-only gates, swap-ins, scanner, rung-up schedule, checker extended to independence and demo path |

## Appendix: Findings disposition (id -> fixed / rejected / why)

Review A (consistency). H1 fixed: K3 no longer depends on compile work (K3fx fixture; stand-ins CMP, GSI; section 6). H2 fixed: K2 touches no `crates/core`; CT1 is a Codex WP under `[CONTRACT-CHANGE]`; consent clause optional. H3 fixed: Claude wrappers are new files; Codex gate scripts X-FACADE (9.1). H4 fixed: total path map with 0 unowned of 1683, `durable_jobs.rs` X-CONF, `bridge-contract` and `core-bridge` L-BRIDGE, ranges per lane, new paths marked. H5 fixed: U-14 default measures only; GT0 has no ENV ancestor. H6 fixed: CF0, FRZ0, TW0 are WPs with edges; Codex side of TW-0 only if U-1. H7 fixed: `first_red` and `acceptance` columns, checker rejects empty cells. H8 fixed: rule covers all developer agents; step 2 -> 3 hand-off defined; honesty test 2 covers original-treated and treated payloads (2.2). M1 fixed: chain recomputed (ENV0 > K3 62.0 h; GT1B depth 118.5 h; floors rebuilt). M2 fixed: sessions = max(capacity bound, floor). M3 fixed: no stale list; minimum cuts computed. M4 fixed: K0 is T0.5; tier and wave monotonicity checked. M5 fixed: G0d feeds the gates through the PR receipt rule and ENV6; CRV1 gates GT05; RG numbering aligned (RG-1 GT05, RG-2/3 GT1A, RG-4 GT1B). M6 fixed: ADR blocks sized for 17 and 12 lanes. M7 fixed: contracts table says provisional versus frozen. M8 fixed: compose fragments owned by their lane. M9 fixed: Q3c split, M5b in L-CLIENT, `stages/` in L-MODEL, X-REV defined read-only. M10 fixed: review classes complete incl. L-E2E, X-CONF, X-REV; loops are WPs; one churn number. M11 fixed: per-tier and per-wave shares printed; Codex lanes pulled early. M12 fixed: capacity B lists its conditional ENV items; no unmet dependency. M13 fixed: staffing per capacity (9.6). M14 fixed: U-2 is optional with a defined default. M15 fixed: DVREC owns recompute, STP1 wraps. M16 fixed: G0gp and G0gr split. M17 fixed: citations are to two-team plan 16.6 and 17.1; annexes named. L1 fixed: rungs, RC1-RC3 and R1-R17 are distinct. L2 fixed: table ids used everywhere. L3 fixed: secondary labels row. L4 fixed: ask order stated. L5 fixed: `pulso-engine` CLI is E2 and STP1. L6 fixed: "to create" marks. L7 fixed: TA0 is W1. L8 fixed: GT1B says demoted; deletion in Q2. L9 fixed: lanes counted by WPs per wave. L10 fixed: `wave` column. L11 fixed: checker extended. L12 fixed: numeric acceptance cells.

Review B (backward). B1 fixed: stream B (BK0, BKN, BKNL, BKF/BKT/BKD/BKA/BKC/BKJ, BKE, BKX by Codex; BKFL, BKTL, BKDL, BKAL, BKCL, BKJL, BKOL, BKEL live by Claude); gates list kinds proven; denied-kind negatives at T1a. B2 fixed: E2 and K3 in Q1 deps. B3 fixed: P1 in E7 deps. B4 fixed: P2py in Q1r deps. B5 modified: the user decided DEMO-0 on roleplay; SMOKE and M4 are DEMO-1a rung-up (M4 deps M2a and M3, not M2f). B6 modified: DORIGm is Codex breadth (not gating); E0 detection is real in DEMO-0 via existing sensors and ED0; the local model as E0 responder is superseded by the treated-payload decision. B7 fixed: PX0, DPLAT at T1a with PL-C acceptance, DPL1, DPL2. B8 fixed: L-BRIDGE lane. B9 fixed: K0 T0.5; DMAPC digest from dry-run (`hash=core-authoritative`), K4 at T2. B10 fixed: DEVAL at T1a (Codex swap-in) and EVE (Claude stand-in). B11 fixed: U-15, H1n, `JEV_API_KEY` in ask 6. B12 fixed: BLOB1 and blob-store wording; stage names kept (user directive) with disambiguation. B13 fixed: ratchet records `host` per step; CRV1 gates GT05. B14 fixed: wording of 158 h versus depth (section 6). B15 fixed: gateway `release.yml` and `GATEWAY_CONSUMERS`, agent-core Dockerfile, counts re-measured by G0gr. B16 fixed: E7 acceptance has stall metric and restart policy. B17 fixed with M5. Coverage gaps: U05 PGQ; U26 SB2; U28 LAB28; U34 RC1-RC3; U36 SB1 and SBL; U32 panels CON2; U10 M6; CAP-13..15, 17..20, 22 BKC and BKCL; CAP-23 BKN; CAP-48 BOOT; CAP-56 BKCL; CAP-64 Q3c and QKG; spec-22 families FX22a, FX22b, FX22p; PL-02..04 DPL1 and E4R; PL-06..10 DPL2; PL-C6 DDOC1; blob store BLOB1.

Review C (feasibility). HIGH-1 fixed: path map generated from `git ls-files`, "to create" marked. HIGH-2 fixed: XSTUB stubs and single integrator. HIGH-3 fixed: C-1, C-7, C-11 exist; C-8 and C-10 are new schemas; C-4, C-5 draft until CF1. HIGH-4 fixed: machine model corrected (one 10 GB VM, 1.7 GB free); ENV8 no longer stops or resizes. HIGH-5 fixed: ENV0 measures both accounts; ENV1, ENV3, ENV5, ENV11, ENV12 conditional; no unsourced numbers; seams crates do not depend on `crates/core`. HIGH-6 fixed: Codex lanes consume only the FRZ0 pack; the 22% is no longer headline; shares by tier printed; the first-20-sessions Codex share is 27-30% through T1b because breadth lanes are early. HIGH-7 fixed: ENVADR plus ask 3. MEDIUM-1 fixed (L-ENV paths). MEDIUM-2 fixed: no `exclude`, edition and rust-version in K0, seams leg in the gate. MEDIUM-3 fixed: journal NNNN convention and amendments precedent. MEDIUM-4 fixed: MIG0 RED compares to the union of existing test setups; PGJ is a delta on `pulso_jobs` (16-24 h). MEDIUM-5 fixed (K2/CT1). MEDIUM-6 fixed: 58 worktrees, train size, restack. MEDIUM-7 modified: reviewer capacity is explicit WPs and pools; the +8-12% appears as U-12 default. MEDIUM-8 fixed: sessions labelled a model; only DEMO-0 dated. LOW-1 fixed: counts (45 integration test files, 60,541 lines, 189 packages, `tokio` already in the lock closure). Asks: instant sentences first, U-14 default measure-only, U-8 never merges by default, added U-17 and download approval.

Rejected or modified with evidence: (1) B5 and B6(b) are superseded by the user's DEMO-0 decision (roleplay rung, treated payloads), not rejected on merit. (2) B12 rename of S3a/S3b is rejected because the user asked to keep the stage names; the collision is removed by calling the object store "blob store". (3) C HIGH-6 "pull DORACLE/DREPLAY/DEVAL earlier bound to a consumer gate" is modified: with the independence rule they have no Claude consumer, so they stay Codex breadth with swap-ins, while Claude owns EVE, ORC1 and RPL1. (4) A M5 "G0d as ancestor of GT0" is rejected for the demo path (it would push a non-demo script ahead of DEMO-0; the local gate scripts already exist), G0d lands in W1 and feeds every PR receipt. Earlier reviews 1-4 left open only items already covered above (single spend owner, resume design, git rule for E0, objective tripwires).
