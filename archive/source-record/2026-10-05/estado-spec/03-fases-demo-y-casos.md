# Estado vs spec V3: fases P0-P5, demo magica y casos de uso (vista top-down)

Assessor: top-down view. Ground truth: GitHub `main` of pulso-factored/improvement-engine at `41492cb` (verified with `gh api`), read-only worktree `worktrees/improvement-engine-main-ro`; infra `origin/main` `dab52ab`. Codex local work is counted separately (LOCAL = 0). Hosted CI on main is red for all six latest runs (`gh run list`: failure on f7ec6fd, 41492cb, 869232e, eea264a, c7544bc, b77f3c3; job logs return 404; Actions budget exhausted per CL-0036 / OPEN_GAPS), so every "tests pass" below is local evidence from PR bodies/journals, not a hosted check. The files `01-motor-codex.md` and `02-integracion-plataforma-infra.md` did not exist when this was written; this file relies only on my own evidence from main (unit-level counts live in those files).

Status codes: DONE / PARTIAL / STANDIN / LOCAL / TODO (weights 1 / 0.5 / 0.2 / 0 / 0; "incl. local" counts LOCAL as 0.5).

## 1. Definitions extracted

### 1.1 Phases (spec section 30.3 + 30.9, plan section 3 and 12)

P0-P5 are defined as such (spec 30.1/30.3; plan section 3 table adds the "closing work" per phase). P4 and P5 exist; the plan's section 12 lists the post-demo remainder ("H5 spec completo") per family.

| Phase | Families (30.3) | Units (30.9) | Gate / exit criterion |
|---|---|---|---|
| P0 Base | P0-A artifact/ref/head + first queryable snapshot; P0-B Compose PG/S3, doctor, minimal CI; P0-C initial fixtures, Core pin, glossary/owners | U01, U02, first cut U03 | Clean clone -> `doctor` -> create/read readonly snapshot and durable evidence |
| P1 Tracer | P1-A trigger/job/event/quota/claim; P1-B Core task bootstrap/pin + external models + Jev; P1-C DuckDB extract, sessions, QueryResult; P1-D list/timeline by API | U03, U05-U11, U07/U24 minimal, first U04 | snapshot -> automatic trigger -> Core task -> adaptive query -> receipt -> timeline, with permissions and budget |
| P2 Hallazgo explicable | P2-A multi-family sensors original/E0; P2-B scout/verifier; P2-C wiki, CAS publish, revocation; P2-D expediente UI | U12-U16, U15/U33, U29/U30, U08-E/U12-E | altered input changes support; finding/refutation and memory traceable; no hardcoded `Queja` |
| P3 Cambio evaluable | P3-A alternatives/bridge/compiler + registry writer; P3-B ScenarioFactory/oracle/baseline/pairs/harness; P3-C local simulator/broker isolation; P3-D diff + two gates UI | U16-U20, U26/U27/U35, U32-V, U36/U20-E | eligible opportunity -> authorized draft -> frozen candidate -> native + ImprovementEvidence, including fail/unsafe/infra |
| P4 Automejora E2E | P4-A scheduler/registry/human/simulator integration; P4-B frozen/continuous temporal; P4-C learn/refute + evolution candidate; P4-D full-cycle UI + debug controls | U21-U23, U31/U33/U34, U32*, U22-E/U23-A | autonomous detection -> proposal -> evaluation -> human wait -> staging publish/ack -> new event -> second iteration with memory, nobody forces the finding |
| P5 Entrega robusta | P5-A Terraform/CD/staging/rollback; P5-B load/security/fairness/retention; P5-C runbooks/a11y/onboarding | U25/U28, U32*, U34/U34-F/FE, load/chaos/restore/a11y | third party reproduces stack; chaos/load measured; AWS plan/smoke only if authorized; docs match |

Denominator used for the phase table: the 22 assignable families P*-* of 30.3 (3+4+4+4+4+3), one row each, status judged against that family's gate. Unit-level (U01-U55 + 10 variants) and CAP-01..64 counts belong to the other two assessors. Not counted here: the C01-C14 technical scenarios (they are reflected inside the family rows).

### 1.2 Success criterion, DoD, gates

- Spec 1 success: undirected detection and investigation, compatible `EntityDraft[]`, proposal `origin=auto_detect`, validate/freeze, candidate vs base with `EvalSuite` and Pulso improvement gate, autonomous iteration to `evaluated` or justified stop, human step-up approval bound to `candidate_hash`, mock/real registry confirms release and staging, second run uses or contradicts memory. A proves undirected finding; B proves sandbox effect (grade `same_outcome_linked|mechanism_proxy|unlinked|not_evaluable`), not causality on the CSV SLA.
- Spec 12 DoD of the demo engine: a third party clones engine+infra, mounts dataset, runs `doctor`, reproduces non-hardcoded detection **with real Jev/LLM**, inspects expediente/wiki/feed and technical console **without shell**, sees proposal and baseline/candidate evaluation, release/rollback confirmed by the simulator, second iteration. DoD per cut: observable story, RED->GREEN via public interface, unit/contract/integration/E2E, docs, journal, ADR, receipts, recovery, adversarial review.
- 26.3 operational acceptance per cut: structured logs + trace propagation (span links API->queue->worker->Core), bounded-label metrics; alarm table (API errors/p95, stalled autonomous work, model budget/circuit breaker, persistence/sandbox, evidence gaps), each alarm with name, query, window, threshold, owner, runbook, firing/resolved proven locally; crash/restart, collector loss, backup/restore tests per cut. "Do not call monitored a dashboard without tested alarms".
- Plan 11.2/11.3 H4: E2E-REAL-01 (compatibility fixture, does **not** prove finding or improvement) and E2E-DEMO-AUTO-01 (original and E0 in separate namespaces, undirected discovery -> real-model investigation -> proposal -> eval -> decision -> release -> observation -> memory -> successor; at least one backed positive path; negatives/faults; browser E2E on real services). Plan 14: no deadline/capacity known; H0-H4 = demo gate, H5 = full spec.
- 27.2 builder sequence (create proposal, PUT full draft list, validate, freeze, evaluate, two gates, approve with hash, publish with Idempotency-Key, promote separate) and 22 reference journey (11 steps with owner and "failure not disguised") are contract tests, not a script.

### 1.3 Use cases (spec 11)

S0 data/backend/docs (13-source snapshot, bytes untouched); S1 scheduler (two triggers -> one run, 2 workers SKIP LOCKED/fencing, PG restart, lost NOTIFY); S2 investigator (SQL/wiki, real Jev/LLM via Core, QueryReceipt); S3 multi-front finding or refutation (n/denominator/CI, no `Queja` hardcode); S4 opportunity -> alternatives incl. `do_nothing` -> compatible bundle; S5 evaluator candidate vs baseline in simulator; S6 platform observations by layer + API/feed + technical console; S7 memory/registry (evaluated -> human wait -> approve/publish staging -> events -> wiki -> new run); S8 third-party local reproduce + Terraform plan/apply + rollback. C01-C14 are the technical scenarios.

## 2. The 10-step "demo magica": what is real today

Source: `demo/README.md`, `demo/out/demo-report.json` (steps and `doubles[]`), `e2e-core/` (engine stand-in `codex_standin/engine.py`, 155 lines), PR #76/#79 bodies, CL-0023, OPEN_GAPS. Key fact: **no step is driven by the Rust engine.** The demo's engine is a Python stand-in (`e2e-core/src/codex_standin`, `demo/src/pulso_demo/driver.py`) that calls the real Core `real_local` stack (Podman PG16 + `pulso-core-runtime` image on pinned agent-core `c814c2b`), with a **scripted LLM gateway**, an `e2e-fixtures` double for control-api/lab-broker/bank/ingest, a synthetic planted dataset and a mechanism_proxy judge written for the demo.

| # | Step (plan 2) | Label in `demo-report.json` | What actually runs | Stand-in / simulated part | Blocking dependency chain (code evidence on main) |
|---|---|---|---|---|---|
| 1 | Snapshot/E0/observations wake the engine, nobody picks category | stand-in | Rust `improvement-engine local-sim` CLI (crates/runner, 1120 lines in main.rs) can read E0/original and compute signals; run by hand on the sample (200 discovery cases, 154/200 recurring-query, holdout 1433/1539, CX-0171/0172) | Demo uses a synthetic dataset analysed in Python (`analysis.py`); trigger is a CLI invocation | No trigger producer: no scheduler/worker/control-api binary (only bin = `improvement-engine` CLI; `DurableJobStore` is in-memory, `durable_jobs.rs`); exporter -> Rust ingest endpoint does not exist (exporter targets `ingest_fixture`); PL-C1 `platform_live` adapter not on main |
| 2 | Signal families measured, discarded candidates, investigation | stand-in | Rust: `signal_portfolio`, `e0_deterministic_sensor`, `platform_sensor`, `value_model` kernel (pure) all tested | Demo: `analysis.scout` over sqlite dataset | Sensors are libraries behind the CLI; not connected to jobs/receipts/timeline over HTTP; only 3 E0 metrics + platform sensor, not the 13 source families |
| 3 | Adaptive scout SQL/wiki; separate verifier | stand-in | Core verifier agent run on real Core; Rust `autonomous_scout.rs`/`independent_verifier.rs` with ports | LLM scripted (answers built from analysis), `lab_query` rows fixed in double; Rust lab is SQLite (no DuckDB anywhere in crates) | Rust has no Core client: `crates/core/Cargo.toml` has no HTTP dependency; `core_task.rs` only `CoreTaskSimulator` and `SUPPORTED_CONTRACT_VERSION = "0.5.0"` vs V3 1.3.0; `model_provider.rs` builds an OpenAI-compatible request but has no transport; real Jev needs agent-core PR #28 (not on agent-core main, relay file) and an llm-gateway tagged image/key (OPEN questions Q1-Q15) |
| 4 | Opportunity with population, mechanism, uncertainty, alternatives incl. `do_nothing` | stand-in | Rust `workflow_bridge.rs` (U16), `e0_investigation_plan`, `e0_mechanism_resolution`; builder_design stage on real Core | Alternatives come from `builder_design` scripted output | E0 route resolves **unlinked / `no_exact_supported_flow_mapping`** against an empty ephemeral catalogue (`e0_mechanism_resolution.rs:571`, CX-0093, CX-0151, journal 2026-10-03T21:12Z "critical-path gap"); Codex builder lane is design-only, `provider_invoked=false`, non-executable; U20/U20-E blockers explicit in CX-0171/0172 runs |
| 5 | Concrete change: Core entities, versions, diff | real (receipts), change spec stand-in | Real: writer create/PUT/freeze receipts in the real Core registry, dry-run/alias routes, hashes (Claude `core-bridge`) | The ChangeSpec/draft plan is produced by the Python stand-in | Rust `change_compiler.rs` is Add+Flow oriented (plan 3), `governed_registry.rs` writer is `pub(crate)` in-memory; no Rust client against `bridge-contract/` (OPEN_GAPS "E0 -> Core flow mapping"); no DraftPlan/JCS/cascade/`replace` in Rust (U46/U39 families) |
| 6 | Scenarios on base and candidate; two distinct gates | stand-in | Real: Core native evaluation (admission, arms, isolated eval DB, harness) on real_local | Pulso improvement gate = demo's mechanism_proxy judge reading planted columns; bank/scenarios from fixture double | U27 `ImprovementEvidence`/`CombinedGate` does not exist in any crate (grep empty); `native_evaluation.rs` only admits, never executes; U26 sandbox is in-memory |
| 7 | Failure -> bounded automatic revision | stand-in | none in Rust | Demo reviser: two rule-based moves steered by a structured guard breach (tested, mutation-tested) | No Rust iteration loop/revision budget over real eval reports; no builder re-invocation path |
| 8 | Human only for authority; approve fixes operation/hash | simulated (scripted) or manual | Real: Core approve/publish verified JWS from Claude's local-identity sandbox issuer; manual mode via `pulso_demo.decide` | Scripted = simulated supervisor; issuer is an IdP double | No control-api decision endpoint, no `waiting_human_approval` job state in a worker (U21); CAP-44 remote IdP is dependency_blocked by spec |
| 9 | Staging confirmed; exposure needs alias receipt | real | Real alias READ confirms staging; prod untouched unless `--promote` | Driven by the stand-in | Same as 5/8 (engine side absent) |
| 10 | New observations -> memory published/contradicted -> new investigation | stand-in | Real: Core run -> real exporter -> ingest fixture + chain verification | Second batch scripted; memory re-measure and successor started by the stand-in | Rust ingest endpoint absent; U50 release correlation absent; U22/U33 memory are in-memory (journal: "not production-durability proof"); no successor trigger/scheduler |

Demo score (demo steps as 10 items, real-but-stand-in-driven = PARTIAL, stand-in/simulated = STANDIN): 2 PARTIAL (5, 9) + 8 STANDIN (1-4, 6, 7, 8, 10) = (2x0.5 + 8x0.2)/10 = **26%**. Steps fully real with the Rust engine driving them: **0 of 10**.

### 2.1 The blocker chain, end to end (trigger -> approval)

1. **Trigger producer**: nothing on main. No worker/scheduler binary, no control-api HTTP service (`OPEN_GAPS: "Codex control-api not published"`), no ingest endpoint for Claude's exporter. `DurableJobStore` is in-memory; only run events (`0003_pulso_run_events.sql`), artifacts, model attempts, platform observations and temporal receipts have PG adapters.
2. **Detect**: exists as library + manual `local-sim` CLI (real on the E0 sample); not wired to jobs, not undirected across 13 families.
3. **Investigate**: needs the Rust Core client (U37/U09-A/U09-B on the Rust side) to invoke scout/verifier tasks, plus real model/Jev; neither exists in Rust. Core side is ready (Annex D, `bridge-contract/`, ADR 0011/0012). Codex has stated no network to GitHub (CX-0174..CX-0181), so even its local client work could not be published.
4. **Candidate**: E0 finding -> Core artifact mapping missing (unlinked); compiler/draft plan and writer client in Rust missing/in-memory; Core pin in Rust still 0.5.0.
5. **Calls the Core registry**: only Python (core-bridge `authoring/`, `registry_service.py`) does, under the stand-in.
6. **Evaluate**: Core native eval real; Pulso gate (U27) missing; Plan/oracle sealed in Rust (U20/U20-E) but bridged to no executed arms.
7. **Approve**: Core side real; engine-side decision/command surface (control-api) missing.
8. **Observe/learn**: exporter real; ingest, correlation, scheduler-driven successor missing.

Concentrated: **Rust-side Core HTTP client + E0->flow mapping + control-api/ingest + worker + U27** are the missing seams; everything on the Claude side exists as local-green but is exercised only through the stand-in.

### 2.2 What Codex is doing now (last journal entries)

CX-0177..CX-0182 (2026-10-04 01:03-01:50Z): P2 ValueModel kernel (merged as #90, pure arithmetic/ranking, no claim of full ValueModel@1, aggregate removed after review); opt-in local OTel LGTM compose (#88 merged; no runner trace emission claimed); scope freeze requested by user (CX-0180: finish active slices, take no new tasks, then stop for status review; runner composition explicitly deferred); CX-0181/0182: PR #87 merge reverified, #88/#90 merged, hosted `rust-ci` failed with 404 logs, seven worktrees with uncommitted partial work preserved and not published. Codex environment: GitHub CLI token invalid / network blocked (CX-0174, CX-0175, CX-0180); it publishes only through the connector with reconstructed commits. Codex is therefore currently **stopped** by user instruction, and the Rust E0 -> Core path is last documented as "disconnected" (journal 2026-10-03T21:12Z gap audit).

## 3. Status per family (denominator: 22 families of 30.3)

| Family | Status | Evidence (main unless noted) |
|---|---|---|
| P0-A artifact/ref/head + snapshot | PARTIAL | `migrations/0001`, `artifact_repository` + `postgres_artifact_migration` (PG, `--ignored` in CI), `source_validation`, `enriched_history`; no S3/MinIO adapter in any crate (localstack only in compose) |
| P0-B Compose + doctor + CI | PARTIAL | `local/compose.yaml` (pg, localstack, otel-lgtm), `local/core/doctor.core.ps1` (Claude, Core checks), `scripts/verify-local-ci.ps1`; OPEN_GAPS: Codex container smoke never run (Podman denied), hosted CI red |
| P0-C fixtures, pin, glossary | PARTIAL | pin c814c2b + ADR 0012, CONTEXT.md, `contracts/` has 5 schemas + 2 fixture families; most of the 22 fixture families of spec 22 (signal/bridge/change_spec/tree/scenario/evaluation/release_ack/memory/read_model) absent; no `contracts/product/` |
| P1-A trigger/job/event/quota/claim | PARTIAL | U05/U06 reducer + fencing tests on in-memory store; PG only for run events; no scheduler, no SKIP LOCKED/2-worker/PG-restart tests |
| P1-B Core task + models + Jev | PARTIAL | Python side real_local (core-bridge 529 passed, e2e-core 44/1 live, local evidence); Rust side simulator only, contract 0.5.0, no HTTP, no live model/Jev, Jev blocked on agent-core #28 |
| P1-C lab/sessions/QueryResult | PARTIAL | `local_lab.rs` SQLite with in-memory grant authority, `e0_query_lab`; spec/plan demand DuckDB and mounted wiki; no adaptive dependent-query session over Core tools in Rust |
| P1-D list/timeline by API | STANDIN | Console (merged #74/#77/#85) runs on fixtures + stand-in `DebugApi` provider; Rust `debug_console.rs`/`run_timeline_v2.rs` are libraries, no HTTP server, no SSE |
| P2-A multi-family sensors | PARTIAL | `e0_deterministic_sensor`, `signal_portfolio`, `original_contact_projection`, `platform_sensor` (E0 sample run: 154/200); 3-4 metrics, not 13 families; not job-driven |
| P2-B scout/verifier/strength | PARTIAL | `autonomous_scout.rs`, `independent_verifier.rs`, `e0_frozen_verifier`; tested with scripted ports, no real model |
| P2-C wiki/CAS/revocation | PARTIAL | `wiki_scratch`, `memory_store`, `governed_memory_use`, expiry (#83), PG temporal receipts; main store in-memory |
| P2-D expediente/evidence UI | STANDIN | Console panels on fixtures; platform explanation read model in Rust (#87) not served |
| P3-A alternatives/bridge/compiler/writer | PARTIAL | `workflow_bridge` (U16) done in lib; compiler Add+Flow only; writer in-memory crate-private; real Core writer is Python under stand-in; E0 route unlinked |
| P3-B scenarios/oracle/baseline/pairs | PARTIAL | `evaluation_plan` (U20), `sandbox`, `e0_safety_oracle`, `value_model` scenario kernel; Core native eval/arms/harness real_local (Claude); Pulso U27 gate absent |
| P3-C simulator/broker isolation | STANDIN | `sandbox.rs` in-memory; broker/bank are `e2e-fixtures` double; CAP-41 stateful bank in native gate is dependency_blocked (D-7) |
| P3-D diff + two gates UI | STANDIN | Console fixture panels (#77) |
| P4-A scheduler/registry/human/simulator | STANDIN | Human issuer + Core approve/publish/alias real (Claude, local-identity) but no scheduler/worker; whole path driven by stand-in |
| P4-B frozen/continuous temporal | PARTIAL | `memory_temporal_protocol` U23 in-memory + PG receipts (0004), E0 frozen cycle `pub(crate)`; no clocked campaign, no resume |
| P4-C learn/refute + evolution | PARTIAL | `governed_memory_use` U22, expiry; U31 evolution absent; two-run composition only in LOCAL branch |
| P4-D full-cycle UI + controls | STANDIN | Console decision/demo panels on fixtures; commands gated, no live backend |
| P5-A Terraform/CD/rollback | PARTIAL | infra main `dab52ab`: modules incl. `engine_platform`, `bridge_services` declared and offline-validated, flags default off; nothing applied; no engine image (no control-api/worker to ship); OIDC/CD manual future |
| P5-B load/security/fairness/retention | TODO | no load/chaos/restore suite; only RLS/privacy unit tests (counted in other rows) |
| P5-C runbooks/a11y/onboarding | PARTIAL | extensive docs/ADR/journals; no runbooks with RPO/RTO, alarms firing/resolved, a11y tests |

## 4. Per-phase and overall percentages

"Incl. local" credits the unpublished Codex worktrees (unverified; many overlap what already merged under other SHAs, so this uplift is small and approximate).

| Phase | Items | DONE | PARTIAL | STANDIN | LOCAL | TODO | Weighted % | % incl. local |
|---|---|---|---|---|---|---|---|---|
| P0 | 3 | 0 | 3 | 0 | 0 | 0 | 1.5/3 = **50%** | 50% |
| P1 | 4 | 0 | 3 | 1 | 0 | 0 | 1.7/4 = **43%** | ~46% (platform scout signal, pl-c4 guard WIP) |
| P2 | 4 | 0 | 3 | 1 | 0 | 0 | 1.7/4 = **43%** | ~46% |
| P3 | 4 | 0 | 2 | 2 | 0 | 0 | 1.4/4 = **35%** | ~38% (u26-r2 stateful sandbox WIP) |
| P4 | 4 | 0 | 2 | 2 | 0 | 0 | 1.4/4 = **35%** | ~40% (p4 two-run, p4 consolidated, temporal successor) |
| P5 | 3 | 0 | 2 | 0 | 0 | 1 | 1.0/3 = **33%** | 33% |
| **Families total** | **22** | **0** | **15** | **6** | **0** | **1** | **8.7/22 = 39.5%** | **~43%** |

Companion tables (same weights):

| Set | Items | Result |
|---|---|---|
| Use cases S0-S8 (S0 PARTIAL, S1 STANDIN, S2 STANDIN, S3 PARTIAL, S4 STANDIN, S5 PARTIAL, S6 PARTIAL, S7 STANDIN, S8 PARTIAL) | 9 (0 DONE, 5 PARTIAL, 4 STANDIN) | 3.3/9 = **37%** |
| Demo steps 1-10 (section 2) | 10 (0 DONE, 2 PARTIAL, 8 STANDIN) | 2.6/10 = **26%** |
| **Overall (my denominator: 22 families + 9 UCs + 10 steps = 41 items)** | 41 | 14.6/41 = **35.6%** |

Read this honestly: zero DONE anywhere because (a) hosted CI is red/unverified, (b) the spec demands real PG/S3/Core where main uses in-memory/SQLite/fixtures, and (c) nothing is exercised end to end by the Rust engine. The percentages are an upper-ish estimate of "capability present in some form"; the **real e2e demo is 0%** in the Rust-engine sense. Overall spec % over the full U/CAP catalogue should be taken from files 01 and 02 and will differ (the unit catalogue weights Claude's packages, which are mostly complete as local-green, more heavily than my family view does).

## 5. Most important findings

1. No step of the demo is driven by the Rust engine; the whole 10-step run is a labelled Python stand-in over a real Core stack, a scripted LLM and a planted synthetic dataset. The demo proves Core-side plumbing and console rendering, not discovery.
2. The Rust workspace has a single binary (`improvement-engine local-sim`) and no HTTP dependency: no control-api, no worker/scheduler, no Core client, no S3, no DuckDB, no model transport, no U27 gate. `core_task.rs` still pins contract 0.5.0 while the Core side is 1.3.0/`c814c2b`.
3. The E0 signal is `unlinked` (`no_exact_supported_flow_mapping`): nothing turns the finding into a Core artifact; the Codex builder lane is design-only and non-executable. This is the actual intellectual gap, not just plumbing (journal 2026-10-03T21:12Z).
4. Claude's side is broad and locally green (core-bridge, assets, platform-sim, exporter, local-identity, console, infra modules; all PRs merged) but only exercised via the stand-in; real-wire parity and joint H4 never ran (OPEN_GAPS).
5. Hosted CI on main is red on all six latest runs with unreadable logs; the only evidence is local. Codex cannot reach GitHub, so publication goes through the user/connector; seven dirty Codex worktrees hold unpublished, unverified partial work (U13 runner compose, U13A admission, U26-r2, platform scout signal, pl-c4 guard, E0 draft binding, P4 consolidated).
6. Codex is under a user scope freeze (CX-0180) and has stopped; runner composition was deferred.
7. Real LLM/Jev is blocked externally: agent-core JEV-through-gateway PR #28 not on agent-core main, no tagged llm-gateway image, no authorized key/budget. DoD of the demo requires real models.
8. P5 operational acceptance (alarms firing/resolved, load/chaos, restore, AWS) is essentially untouched; infra is declarations, not applied.

## 6. Open uncertainties

- Whether the Python bridge can serve as the engine's Core client for a one-day cut (spec says Rust client over HTTP; the plan forbids the Rust engine importing Python).
- Content and state of Codex's seven dirty worktrees is unverified; "incl. local" is approximate.
- Hosted CI red cause unverified (quota vs real failures); Codex local `verify-local-ci` green claims could not be re-run by me (not allowed to run builds).
- Spec 22/31 fixture inventory vs `contracts/` was checked by listing, not by running the validators.
- Product answers (nine questions) still gate trusting `platform_live` payloads.

## 7. Tomorrow plan: minimum critical path to a defensible real e2e

Goal: the Rust engine drives one run, E0 (or original) -> finding -> Core candidate -> real native evaluation -> Pulso gate -> human approval -> staging confirmed -> exporter -> successor, against the existing `real_local` Core stack, with every remaining double listed in `doubles[]`.

Realistic in one day: a **Rust-driven run on the real_local Core stack, honestly labelled**, with recorded or scripted LLM unless a key/gateway is supplied; i.e. an E2E-REAL-01-class result plus a partial E2E-DEMO-AUTO-01. Not realistic in one day: durable PG worker/scheduler with SKIP LOCKED and restart tests, real Jev, AWS deploy, hosted-CI green, full 13-family discovery, browser E2E on real API.

Ordered critical path (hours = focused effort for one agent each; P = parallelizable with the previous item):

| # | Work item | Owner | Effort | Parallel? | Notes |
|---|---|---|---|---|---|
| 0 | User unfreezes Codex and moves its unpublished work to GitHub (or declares the 7 worktrees dead); resolve how Codex reaches Podman/Core (its VM was inaccessible) | User | 1 | start first | Hard precondition; Codex scope freeze CX-0180 and Podman denial block everything |
| 1 | Minimal Rust Core HTTP client (U37 subset): service-JWT signing, Annex D headers (`Idempotency-Key`, `job_id` claim), invoke scout/verifier/builder_design, admission + evaluate-only/arms, dry-run, alias read; bump `core_task.rs` to 1.3.0/pin; coded against `bridge-contract/` goldens | Codex | 6-8 | P with 2, 4 | Needs `ureq`-style crate in Cargo (Codex-owned) |
| 2 | E0 -> Core flow mapping: resolver that links a measured finding to a catalogued Core capability by declared mechanism metadata (not by category name), plus seeded world with the target flow and decoys; compile minimal `DraftPlan` for one `replace/add` Flow change | Codex (compiler) + Claude (assets world) | 5-7 | P with 1 | The real intellectual risk; budget for failure and keep `unlinked` honest |
| 3 | U27 minimal: `ImprovementEvidence`/`CombinedGate` over real native report + sealed U20 plan, mechanism_proxy grade, unknown/unsafe blocks | Codex | 4-5 | after 1 | Reuse `evaluation_plan`/`value_model`; must read real arms, not planted columns |
| 4 | Single-process orchestrator `run-once` (job reducer in-memory, bounded revision loop up to N, waiting_human state, successor trigger from exporter batch) | Codex | 3-4 | after 1,3 | Cut: no durable worker/scheduler; label `trigger=manual_command`, `jobs=in_memory` |
| 5 | Engine output sink for the console: write NDJSON/world via existing translator (`demo/translate.py`) or minimal read-only HTTP for `DebugApi` | Codex (sink) + Claude (adapter) | 3 (sink) / 6-8 (HTTP) | P | Cut allowed: no live control-api; console reads Rust-produced world, labelled fixture API |
| 6 | Swap the stand-in in `demo/`/`e2e-core` for the Rust binary; keep human issuer, exporter, console; update `doubles[]`; fix Annex D mismatches found | Claude | 4-6 | after 1 | Python side already tested; integration bugs are the risk |
| 7 | Integration run on `pulso-dev` (E2E-REAL-01 first, then demo run), negative cases (stale hash, bot approve, lost response), evidence report with `target/sha/doubles[]` | Claude + Codex | 3-4 | last | Rerun locally; hosted CI stays red |
| 8 | Real LLM: gateway key/budget authorization, one live smoke of scout through the gateway | User + Claude | 2-3 | optional | Only if the key and gateway image exist; otherwise recorded/scripted and say so |

Critical path wall-clock: items 0 -> (1 || 2) -> 3 -> 4 -> 6 -> 7 = roughly 18-24 focused hours of Codex work; feasible in one day only with two or three parallel Codex lanes touching disjoint crates and the user transferring code to GitHub early. Treat completion by tomorrow as a stretch; the safe deliverable is items 1+2+6 (Rust client plus mapping plus stand-in swap) with 3-5 as stretch.

What can be cut and still count as "real e2e" under the spec's wording: durable PG scheduler/worker and multi-worker fencing (U06 production adapter; plan H1 mentions restart, so state it as a known gap); live control-api/SSE (spec allows the console to be technical dev console; label fixture/world feed); AWS/Terraform apply (spec: local first, AWS needs authorization); 13-family breadth (>=2 families is the spec's first cut); promote to prod (spec: publish != promote, staging confirmation suffices); hosted CI green (not a demo gate, but say it is red); remote IdP (CAP-44 dependency_blocked by design; sandbox issuer is the spec's own workaround, must be labelled).

What would make it dishonest: any step still driven by the Python stand-in but reported as engine output; a scripted LLM or planted-column judge presented as undirected discovery or improvement; a flow mapping keyed to the winning category (violates "no hardcoded `Queja`"); calling native `pass` an improvement or the mechanism_proxy result a causal SLA effect; scripted approval reported as a human; forcing both original and E0 to success or hiding an `unlinked`/`not_evaluable` result; citing the mock or a2 level as real Core; claiming "autonomous" while the trigger is a manual command without saying so; quoting local-green as hosted CI.
