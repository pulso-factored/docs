# State of the code versus spec V3: synthesis (2026-10-04)

Prepared by Team Claude from three independent read-only assessments (files 01, 02 and 03 in this folder). Code state = GitHub `main` of `improvement-engine` at `41492cb` (verified with `gh api`) and infra at `dab52ab`. Codex's unpublished local work is counted separately and is NOT progress on main. No tests were run for this assessment: every "done" is a claim from a PR body or a reading of code; hosted CI is red on the last 6 runs (Actions budget), so all evidence is local.

## 1. Where we are

| View (denominator) | Result |
|---|---|
| Spec families §30.3 (22 families) | **39.5 %** (about 43 % if unpublished Codex work counted half); zero families DONE |
| Engine units U01-U36 (47 rows) | **36 %** (1 DONE, 30 PARTIAL, 5 STANDIN, 1 LOCAL, 10 TODO) |
| Integration units + 64 CAP + platform §32 + §26/§4.1/§10 (115 items) | **46 %** (CAP-01..64: 16 DONE, 28 PARTIAL, 11 STANDIN, 9 TODO = 50 %) |
| Use cases S0-S8 | **37 %** |
| Demo steps (10) | **26 %** (2 PARTIAL, 8 STANDIN, 0 real end to end) |
| **Whole spec, honest single number** | **about 40 %** (range 36-46 % depending on denominator; the two unit-level sets overlap on 4 units, so do not average them blindly) |

Per phase (family view, headline) with the other two views as range:

| Phase | Families | Engine units | Integration units |
|---|---|---|---|
| P0 foundations | 50 % | 67 % | n/a |
| P1 durable jobs, bridge, models | 43 % | 42 % | 49 % |
| P2 detection and investigation | 43 % | 50 % | n/a |
| P3 proposal, evaluation, registry | 35 % | 34 % | 44 % |
| P4 second run, memory, continuous | 35 % | 20 % | 30 % |
| P5 release, learning, breadth | 33 % | 12 % | 30 % |

Reading the numbers: breadth exists everywhere (almost everything is PARTIAL), depth exists nowhere (almost nothing is DONE). Most "PARTIAL" is a crate-private boundary or a Python half without its Rust half.

## 2. Who has built what

- **Team Claude (Python/boundary):** the bridge runtime with Core integration (alias, dry-run, writer, evaluation admissions, arms, exporter, key delivery), the contract packs (`bridge-contract`, `platform-contract`), simulators, the platform exporter, local human issuer, real-image E2E (44 live tests on PG16 and a real locally built Core image), the console data seam and infra modules (declared, never applied). Merged: improvement-engine #74-#91, infra #17-#29.
- **Team Codex (Rust engine):** libraries (`core`, `source-adapters`) and one local-simulation CLI. Strong on contracts, reducers, admissions, scenario/value kernels, privacy policies. Merged through #90. About three real slices are only local and unpublished (temporal-successor outbox migration 0005, the U27 paired-scenario seed, the platform source policy), plus dirty edits in 5-7 worktrees. Codex is in a user-requested scope freeze (CX-0180) and cannot reach GitHub or Podman from its environment.

## 3. Why the real, non-mocked end-to-end demo has not happened

It is a single missing chain, not many small gaps. The Rust engine cannot yet drive anything:

1. **No runnable engine service.** `main` has libraries and one local-sim CLI. No worker, no scheduler, no HTTP/SSE control-api, no tokio/axum/reqwest/AWS dependencies. The job store is in memory. Nothing produces a trigger.
2. **The Rust half of the Core integration does not exist** (38 of the 64 CAPs have a Rust half; none is DONE on main): HTTP client and error classifier (U37), wire/JCS hashing (U39), state reader (U45), compiler with cascade (U46), eval package and capture (U47/U48), service-JWT signer, human authorization port (U38/U21). `core_task.rs` still pins the old Core contract 0.5.0.
3. **The E0 finding has no exact mapping to a Core artifact**: the route is `unlinked / no_exact_supported_flow_mapping` (CX-0093). Without it there is no candidate to evaluate.
4. **Models are never real**: no model transport; Jev needs agent-core PR #28 which is not on agent-core main; no authorized LLM key; the LLM was always scripted in every test.
5. **The human loop is missing**: publish with step-up (U21) is TODO; U27 (combined gate) has no code in any crate.
6. **Everything the demo shows today is a Python stand-in driving the real Core stack** (`e2e-core`, `demo/`): the data has the mechanism planted, the improvement judge and the human are stand-ins. Only the Core registry receipts (step 5) and the staging alias read (step 9) are real, and the stand-in drives them.
7. **Compounding factors**: Codex's work is not on GitHub (its environment cannot reach it) and it was frozen at the user's request; hosted CI is red (budget); nothing has ever been applied to AWS (infra is declaration-only).

Real dependencies actually exercised so far: PG16, a real Core image at the current pin, 44 live bridge E2E tests. Never exercised: real LLM/Jev, lab broker, bank, control-api, S3, `real-wire`, any AWS call.

## 4. If it had to be finished tomorrow

Realistic scope: **a Rust-driven run on the real Core stack, honestly labelled**, 18-24 focused hours of work, so it is a stretch for one day and depends on two user actions first (unfreeze Codex; get its unpublished work onto GitHub).

Critical path, in order:

| # | Item | Owner | Effort | Parallel? |
|---|---|---|---|---|
| 0 | Unfreeze Codex; publish its 7 dirty worktrees / 3 local slices on top of current main | user + Codex | 1-2 h | blocks everything Rust |
| 1 | Rust Core HTTP client at the current pin (dry-run, invoke, writer, arms, evaluation admission) using `bridge-contract/` goldens and ADR 0011/0012, service-JWT signer, error classifier | Codex | 6-8 h | with 2 and 4 |
| 2 | E0 finding to ChangeSpec/flow mapping with a seeded catalogue (not keyed to the winning category) | Codex (+ Claude assets) | 5-7 h | with 1 |
| 3 | Swap the Python stand-in for the Rust binary in `e2e-core`/`demo` (same Core `real_local` stack) | Claude | 4-6 h | after 1 |
| 4 | Minimal control-api binding: ingest endpoint for the exporter, bridge callbacks, SSE feed for the console | Codex | in the stretch list | after 1 |
| 5 | One real model call through the llm-gateway (needs an authorized key) | Codex + user | 2-3 h | optional |
| stretch | U27 combined gate (4-5 h), single-process run-once orchestrator (3-4 h), NDJSON/world sink for the console (3 h) | Codex / Claude | 10-12 h | partly |

Not realistic in a day: durable PG worker/scheduler, real Jev, AWS deployment, hosted CI green, breadth across all 13 families.

What would make the demo dishonest: showing stand-in output as engine output; a planted-column judge or scripted LLM presented as discovery; a mapping keyed to the winning category; a scripted approval shown as a human. Keep scripted parts labelled, as the current demo already does.

## 5. Findings worth acting on regardless of the demo

- Hosted CI covers Rust only. Python, console and Terraform suites are not in any workflow; every DONE is a local claim. Cause of the red CI is unverified (logs return 404).
- CAP-37 (release correlation) and CAP-64 (traceparent) are not implemented, and the earlier Claude status doc did not flag them. Its CAP-58/61 "implemented" means a standalone Core stack with a stand-in-driven E2E, not a joint run with the Rust engine.
- Journal "integrated" for Codex means a crate-private boundary, not a product flow; its durable adapters U33-E and U23-E are marked `DependencyUnavailable` in its own status file.

## 6. Open uncertainties

No test was re-run; counts come from PR bodies and code reading. Unpublished Codex work could not be verified. The percentages depend on the rubric (DONE 1.0, PARTIAL 0.5, STANDIN 0.2, LOCAL 0) and on counting spec items, not effort or risk; they measure breadth of coverage, not remaining hours. Per-item evidence is in files 01, 02 and 03.
