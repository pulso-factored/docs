# 01 - Rust engine core (Team Codex) vs spec V3 (main @ 41492cb)

## Method
Read worktree improvement-engine-main-ro (41492cb, verified with `gh api` = main head): crates/, migrations/, local/, scripts/, .github/workflows/ci.yml, docs/IMPLEMENTATION_STATUS.md, docs/gaps/OPEN_GAPS.md. No cargo run. Test count = grep `#[test]`: 562 in crates/** (6 PG tests are `#[ignore]`, run only in CI job "postgres-artifact-migration"). Local Codex worktrees (66) compared by blob against main (three-dot diff + blob equality) and `git status`. Denominator: spec 30.8 U01-U36 (U09 split A/B) + E variants (U08-E, U12-E, U20-E, U22-E, U23-A, U32-M/V/W, U34-F/FE) = 47 rows; U37-U55 listed separately. CI caveat: hosted `rust-ci` is `failure` on the last 6 runs including main 41492cb (job logs 404; OPEN_GAPS says Actions quota exhausted; cause unverified), so only U02 is scored DONE (complete unit with an ephemeral-PG test); everything else is PARTIAL or lower.

## Structural facts (answers to the brief)
- Crates: `core` (lib), `source-adapters` (lib), `runner` (single binary `improvement-engine`, a local-simulation CLI; the only `fn main` is crates/runner/src/main.rs). Deps: sync `postgres` 0.19, `rusqlite`, csv/parquet. No tokio/axum/hyper/reqwest/aws-sdk anywhere (grep). So on main there is NO worker, NO scheduler, NO control-api HTTP/SSE, NO S3 client, NO Agent Core HTTP client, NO real model transport (OpenAiCompatibleTransport has only scripted/timeout test impls).
- Real PG on main: only 6 `#[ignore]` integration tests (artifact CAS/immutability/tombstones, model-attempt ledger, platform observations RLS, run events, V2 timeline, temporal memory receipts), run in the CI PG17 service. Everything else is in-memory ports (`InMemory*` registries/writers/cursor registry/fork lifecycle/memory registry). S3/MinIO appears only in local/compose.yaml; no Rust code uses it.
- End-to-end: NOTHING on main runs detection -> proposal -> evaluation against real PG/S3/Agent Core. Closest: `improvement-engine local-sim` reading local E0/original files and writing result.json/NDJSON; the proposal is "simulated, unverified, non-executable", evaluation is "structural-only", no Core calls (docs/IMPLEMENTATION_STATUS.md). Core-side E2E exists only as the Claude-owned `e2e-core/` stand-in (OPEN_GAPS: "Codex control-api not published" and "E0 -> Core flow mapping", both open, owner Codex).
- Journal vs code: CX-0182 reports PRs #88/#90 merged and local CI green; GitHub shows rust-ci red on both (consistent with "local green is not hosted green"). IMPLEMENTATION_STATUS itself says durable adapters (U33-E, U23-E) are `DependencyUnavailable`. No hard contradiction found, but journal "integrated" means a crate-private boundary, not a product flow.

## Table (U01-U36 + E variants). D=DONE P=PARTIAL S=STANDIN L=LOCAL T=TODO
| ID | Item | Phase | St | Evidence / missing |
|---|---|---|---|---|
| U01 | Entorno minimo | P0 | P | local/compose.yaml (PG+S3), local/core doctor.core.ps1, ci.yml; backend smoke blocked ("Access is denied", OPEN_GAPS); hosted CI red |
| U02 | Revisiones durables | P0 | D | migrations/0001; tests/artifact_repository.rs (8) + ignored PG test `migration_enforces_cas_immutability...` in CI job |
| U03 | Snapshot original | P0 | P | source-adapters/src/lib.rs, tests/source_adapters.rs; local files only, no S3 persistence/durable publish |
| U04 | Adapter E0 | P1 | P | enriched_history.rs, source-adapters e0_package_validation; U04-B clock; in-memory |
| U05 | Cuota y grant | P1 | P | quota_grant.rs (7 tests); in-memory, no PG window |
| U06 | Trabajo durable | P1 | P | durable_jobs.rs (18 tests) reducer/lease/fence; in-memory; pulso_jobs table (0003) not wired to admission |
| U07 | Actividad por API | P1 | P | 0003 + durable_run_events + run_activity.rs (13); PG ledger only; no HTTP/SSE endpoint |
| U08 | Lab local adaptativo | P1 | P | local_lab.rs (rusqlite), e0_query_lab.rs; no real session isolation/AWS |
| U09-A | Core task invocation/facts | P1 | S | core_task.rs `CoreTaskPort` trait + test doubles (4 tests); no HTTP client |
| U09-B | Pin/binding/reconcile | P1 | S | same; no pin/binding/429/crash-unknown against real Core |
| U10 | Modelos externos | P1 | P | model_provider.rs, PG model-attempt ledger (0002); transport only scripted, no real provider/Core path |
| U11 | Decision Jev | P1 | S | jev_decision.rs `JevDecisionPort` (4 tests); doubles |
| U12 | Sensor determinista | P2 | P | deterministic_sensor.rs, e0_deterministic_sensor.rs; in-memory evidence |
| U13 | Scout | P2 | P | autonomous_scout.rs (+U13-A/E admission); Core/model receipts are doubles; no real model |
| U14 | Verificador independiente | P2 | P | independent_verifier.rs, e0_frozen_verifier.rs; no persistence, no Jev wiring |
| U15 | Wiki montada | P2 | P | wiki_scratch.rs; in-memory |
| U16 | Mecanismo/alternativas | P2 | P | workflow_bridge.rs; provisional only |
| U17 | Compiler | P3 | P | change_compiler.rs; no Core JCS hash parity, replace/policy/eval_suite kinds not evidenced (U39/U46 absent) |
| U18 | Writer registry | P3 | S | governed_registry.rs `InMemoryGovernedRegistryWriter`; no registry PUT |
| U19 | Evaluacion nativa | P3 | S | native_evaluation.rs + tests/native_evaluation_admission.rs admission boundary only; no EvalRun (self-declared) |
| U20 | Plan sellado | P3 | P | evaluation_plan.rs (926 loc); in-memory |
| U21 | Autoridad/publicacion | P4 | T | no module (no human gate, step-up, publish) |
| U22 | Segunda iteracion | P4 | P | governed_memory_use.rs; in-memory commit port |
| U23 | Replay E0 | P4 | P | memory_temporal_protocol.rs + PG temporal-receipt test (CI); no durable use/campaign |
| U24 | Consola lectura | P1/P4 | P | debug_console.rs, run_timeline_v2.rs (+ignored PG test); read boundary only, no HTTP |
| U25 | Despliegue manifest | P5 | T | infra repo scope; nothing in engine |
| U26 | Banco stateful | P3 | P | sandbox.rs (960 loc, 8 tests) in-memory |
| U27 | Comparacion Pulso | P3 | L | main has only value_model.rs (scenario kernel, not ImprovementEvidence/CombinedGate); `paired_scenario.rs` 655 loc UNTRACKED in worktree improvement-engine-u26-r2 |
| U28 | Sesion AWS | P5 | T | nothing |
| U29 | Observaciones plataforma | P2 | P | platform_observations.rs + 0002 + PG RLS test; no endpoint/exporter ingest (exporter is Claude/Python) |
| U30 | Sensor plataforma | P2 | P | platform_sensor.rs |
| U31 | Evolucion detector | P4 | T | nothing |
| U32 | Diagnostico SQL | P4 | T | nothing |
| U33 | Memoria publicada | P2 | P | memory_store.rs in-memory + PG temporal receipts; successor outbox is LOCAL (below) |
| U34 | Control de run | P4 | P | durable run-control receipts, in-memory per IMPLEMENTATION_STATUS, no API |
| U35 | Elegibilidad final | P3 | P | final_eligibility.rs (pure) |
| U36 | Identidad sandbox | P3 | P | sandbox.rs extension; fixture only |
| U08-E | Lab E0 | P2 | P | e0_query_lab.rs |
| U12-E | Sensor E0 | P2 | P | e0_deterministic_sensor.rs |
| U20-E | Oracle E0 | P3 | P | e0_safety_oracle.rs (tests/e0_safety_oracle.rs) |
| U22-E | Iteracion E0 | P4 | P | e0_frozen_memory_cycle/publication crate-private, not wired to CLI/durable runtime |
| U23-A | Continuous activacion | P4 | T | nothing |
| U32-M/V/W | Paneles detalle | P4 | T | nothing in engine (Claude console separate) |
| U34-F | Fork original | P5 | P | run_fork.rs in-memory |
| U34-FE | Fork E0 | P5 | T | nothing |

Engine-side U37-U55 (Codex-owned parts, none on main in Rust): U37 HTTP client/classifier T; U39 wire/hash in Rust T (Python lives in core-bridge, Claude); U43 lab ToolDefs T; U45 Core state reader T; U46 Core compiler/cascade T; U47 CoreEvalPackage T; U48 evaluate result capture T; U49 Rust ingest endpoint T (exporter is Python); U50 release correlation T; U52 local Core env/doctor P (local/core, backend blocked); U53 E2E-REAL-01 T; U54 builder executor T; U55 harness T. U38/U40/U41/U42/U44/U51 belong to Team Claude.

## Per-phase summary (D=1, P=.5, S=.2, L=0, T=0; groupings per spec 30.9, each unit counted once)
| Phase | Units | D/P/S/L/T | Weighted % | % if local published (L=.5) |
|---|---|---|---|---|
| P0 | U01,U02,U03 (3) | 1/2/0/0/0 | 67% (2.0/3) | 67% |
| P1 | U04-U08, U09-A/B, U10, U11, U24 (11) | 0/8/3/0/0 | 42% (4.6/11) | 42% |
| P2 | U12-U16, U29, U30, U33, U08-E, U12-E (10) | 0/10/0/0/0 | 50% | 50% |
| P3 | U17-U20, U26, U27, U35, U36, U20-E, U32-V (10) | 0/6/2/1/1 | 34% (3.4/10) | 39% |
| P4 | U21-U23, U31, U32, U32-M/W, U34, U22-E, U23-A (10) | 0/4/0/0/6 | 20% | 20% |
| P5 | U25, U28, U34-F, U34-FE (4) | 0/1/0/0/3 | 12% | 12% |
| Total (47 rows) | U01-U36 + E variants | 1/30/5/1/10 | 36% (17.0/47) | 37% |

U37-U55 engine-side (13 items, only U52 PARTIAL) would add roughly 4% for that block if included; not in the totals.

## Local unpublished (Codex worktrees; unverified, labeled LOCAL)
Of 66 improvement-engine-* worktrees, almost all branches are squash-merged into main (blobs equal or main newer). Genuinely local content: (1) improvement-engine-p4-temporal-successor, commit 75a613f (no PR): migrations/0005_p4_temporal_successor_outbox.sql (233 loc), memory_temporal_protocol.rs +712, +465 lines of PG test = durable successor outbox for U33/U23 (deepens a PARTIAL, not a new unit); (2) improvement-engine-u26-r2: untracked paired_scenario.rs + tests (U27 seed); (3) improvement-engine-p2-platform-verifier: untracked platform_source_policy.rs (603 loc) + test + doc (platform privacy); (4) uncommitted edits in p1-platform-observability, restore-main (runner main.rs), u12-u13-runner-compose (16 files), p2-proposal-assembly, u13a worktrees. CX-0182 itself lists 7 such worktrees. The remaining ~50 worktrees hold only already-merged work.

## Top findings
1. The engine on main is a library plus a local file-based CLI; no service process of any kind (no worker/scheduler/HTTP/SSE) and no async runtime or HTTP/S3/Core client dependency.
2. No end-to-end flow on real PG/S3/Agent Core exists. Real PG is exercised only by 6 ignored persistence-seam tests; every orchestration port (jobs, quota, Core task, Jev, registry writer, memory, fork, sandbox) is in-memory or a trait with doubles.
3. The Codex-owned bridge to Core is entirely absent: HTTP client (U37), wire/hash (U39), state reader (U45), Core compiler (U46), eval package (U47), evaluate capture (U48). U18/U19 stop at an in-memory writer and an admission boundary. Primary blocker to a non-mocked demo.
4. Missing decision/human loop: U21 (publish with step-up), U31, U23-A, U34-FE, U32 panels; U27 is not on main.
5. Discovery (U12-U16, E0 sensor/verifier/qualification) is the most mature, but chained only inside crate-private compositions and the local-sim CLI; proposals are labeled simulated/non-executable.
6. Hosted CI is red on main and the last 6 runs (Actions quota; logs unavailable); Python/console/bridge suites are not in ci.yml. No unit is CI-verified except via local runs reported in journals.
7. Little genuinely unpublished value (about 3 slices); the gap is unbuilt integration, not unpublished work.

## Open uncertainties
- Reason for hosted rust-ci failures not verified; local-green only per journals.
- #[test] counts include crate-private tests; pass counts not re-run (rule: no cargo).
- U34 durability type (in-memory vs PG) inferred from IMPLEMENTATION_STATUS wording; U17 absence of replace/policy kinds inferred from spec dependencies on absent U39/U46, not exhaustively read.
- Dirty worktrees may overlap one another; not diffed against each other.
