# Plan B: the deployable, operable, durable real system (lens: work backward from a system that runs continuously)

Author: Planner B (Claude). Date: 2026-10-04. Status: proposal for the orchestrator to debate and merge with the other lenses. Nothing here edits the spec, code or infra.
Evidence base: estado-spec 00-03, spec V3 (4.1, 8-10, 19, 23, 26, 29.9, 31.11, 31.12, 32), plan V3 (2, 12, 13, 14), infra `origin/main` (`agent-core-overlap-and-engine-plan.md`, `deployment-status.md`, `OPEN_GAPS.md`, runbook), `AGENT_CORE_RELAY_FOR_USER.md`, `LLM_GATEWAY_ADOPTION_CLAUDE.md`, `PLATFORM_DATA_MODEL_IMPACT_CLAUDE.md`, journal CX-0165..0182 / CL-0036/37, and the llm-gateway repo read through `gh api` (README, `docs/consuming.md`, `docs/decisions-for-review.md`, `.env.example`, `release.yml`; `gh release list` is empty, so no tag and no digest exist).
Labels used below: VERIFIED (read in a source), INFERRED (my reading), ESTIMATE (my number, not measured), DEFAULT (what we do if nobody answers).

## 0. Thesis in ten lines

1. The system the user wants is not the demo script. It is a handful of long-running processes (control-api, worker, scheduler loop, exporters, Core runtime, gateway) over PG and S3, that survive restarts, spend within a budget, can be paused, and can be rolled back. Today none of the Rust ones exists (VERIFIED: one local-sim CLI, no tokio/axum/reqwest/AWS crates, in-memory job store).
2. The nominal critical path in the status docs (Rust Core client, E0 mapping, U27, run-once, stand-in swap, 18-24 h) targets a labelled one-day cut. For a durable system it is the smaller half. The larger half is the service shell (control-api, durable worker, S3/PG adapters, image, alarms) and the AWS first-apply, which the one-day cut deliberately skips.
3. Key insight: the earliest thing that can be deployed and left running for real needs NO Core and NO model. A platform-shaped event stream (exporter, then control-api ingest, then durable job, then platform sensor, then insight with evidence, then console) uses code that mostly exists (U29, U30, exporter, platform-sim, console seam). It is also exactly what the Product team's Phase 1 supports (findings stop at insight, no proposals). So Tier 1 is deployable first and flushes out every AWS surprise while the Core loop (Tier 2) is built locally in parallel.
4. Every stage of the autonomous loop is written once as a `JobHandler` against ports (decision D3). "Run-once" is the same handler executed by a worker over an in-memory store. This removes the usual rework of the durable worker after the demo path.
5. E0 and the original bank dataset may NOT leave the local host (VERIFIED, spec 28.6: no OpenRouter, hosted Jev/LLM or other external endpoint; local Podman/LocalStack/MinIO only). Consequence nobody has stated plainly: the continuous AWS system cannot run E0 discovery, and real models on E0 means a LOCAL model behind the gateway. Hosted models are allowed only on synthetic-authorized fixtures and on platform data that Product authorizes. This splits the world into three data tiers (section 8) and is the most important planning constraint of this lens.
6. Model cost control cannot live in the gateway (VERIFIED: any authenticated consumer chooses model, price up to 1,000,000 USD/Mtok, max_tokens up to 1,000,000; no rate limit; 120 parallel calls all passed; no Idempotency-Key; no tokens or cost in logs). Our spend ledger and stage policy in `pulso-core-runtime` plus a hard cap on the provider key are the real control. This is a work package (M-2), not a question.
7. Nothing has ever been applied to AWS. Mock-provider tests do not catch IAM, endpoint, KMS-policy or quota failures. The first real `terraform plan/apply` is a discovery event; I budget 18-34 h for it explicitly (D-3, D-5) rather than pretending the declarations are 90 % done.
8. Deploy without GitHub Actions budget: a local, reproducible release script that builds by digest, runs the same gates as CI, emits the signed manifest the infra validators already understand, and leaves `apply` to a human with a saved plan. This also matches the spec (no auto-apply).
9. Codex is frozen, has no GitHub and no Podman. The plan therefore assigns the new Rust service crates (shell, PG/S3 adapters, Core client) to Claude in NEW crates, keeps the domain crates and the semantic hard problems (mapping, compiler, U27, rollout domain) with Codex, and makes the hand-off cheap (bundles plus a Claude-run verify script). Needs user approval (decision D1).
10. Honest total: about 380-590 focused agent-hours of implementation across 7 streams, plus 15-25 % for adversarial review loops. With 4 concurrent Claude lanes and 1-2 Codex lanes that is roughly 28-42 working sessions to a deployed, operable Tier 3, with Tier 1 running locally in 8-12 sessions. Confidence is low-to-medium (section 9).

## 1. Target definition: tiers of "real system"

Rule: each tier ends with something demonstrable, a machine-readable `doubles[]` / `labels` report, and an explicit list of what is still simulated. "Real" never means "wired to a fixture".

| Tier | Name | What exists | Observable acceptance (all by public interface, real deps) | Still scripted or simulated (must be printed) |
|---|---|---|---|---|
| T0 | Unblocked | Codex published or declared its local slices dead; one aggregate local verification command; hand-off protocol; workspace skeleton for new crates | `scripts/verify-all.ps1` runs Rust, Python suites, console, Terraform tests and emits a receipt (head, tool versions, per-suite result); Codex bundle round trip works once | Hosted CI stays red or off; local receipts are the evidence |
| T1 | Durable shell, real source shape (local, then AWS) | Rust `control-api` and `worker` (+scheduler) on real PG16 and S3 emulation; engine image; platform-exporter feeding ingest; detection job on platform observations to insight; console reads live API; metrics, alarms with firing/resolved | `dev.ps1 up`: platform-sim emits traffic with late events, a gap and an unknown event type; exporter delivers; ingest dedupes by batch; scheduler creates a job; platform sensor produces an insight with numerator/denominator and as-of; console shows it over SSE. `kill -9` the worker mid-job: lease expires, job resumes, zero duplicate effects. Stalled-progress alarm fires and resolves. Two workers, one job: one release. | Platform data comes from `platform-sim`; no Core, no model, findings stop at insight (by design, Phase 1) |
| T1-AWS | T1 deployed on staging | Same stack on AWS staging via manifest, ECS, RDS, S3, Secrets, CloudWatch; reached by SSM port-forward | Saved plan applied by a human; smoke passes against `target=real_aws`; alarm delivered to a confirmed mailbox and recovered; restart-all test; kill switch drill; cost report | Source is platform-sim running as a task, or Product's real DB when P-3 succeeds (label which) |
| T2 | Closed loop on real Core (local) | Rust-driven: detect (E0 or platform) -> investigate through Core tasks -> concrete Core candidate -> real native evaluation + Pulso gate -> bounded revision -> human step-up approval -> publish to staging alias -> exporter -> release correlation -> memory use or contradiction -> successor job | `E2E-REAL-01` driven by the Rust stack on the real Core image (no Python stand-in), then `E2E-DEMO-AUTO-01` partial: two separate namespaces (original, E0), at least one backed positive path or an honest `unlinked`/`not_evaluable`, negatives (stale hash, bot approve, lost response, quota). Graded model path: T2a scripted provider behind the REAL gateway (cost and budget exercised), T2b local model for E0, T2c hosted model on synthetic-authorized fixtures only. | Human approval uses the local sandbox issuer (CAP-43; remote IdP is CAP-44, blocked); lab broker and bank backends are what the plan names; trigger may be `manual_command` until T1 scheduler is joined (labelled) |
| T3 | Operable on AWS | T1-AWS + Core runtime + exporters + gateway deployed; model budgets and kill switch; proposal rollout and rollback; incident runbooks; restore and rollback drills; 72 h soak | A proposal moves candidate -> evaluated -> approved -> staging -> observed -> (operator) promote or revoke on AWS; restore drill meets a MEASURED RPO/RTO; digest-pair rollback restores service; soak report; spend report below caps; alarms for the 8 risks of spec 26.3 each proven firing and resolved on the real destination | Jev only if agent-core PR #28 landed; E0 runs stay on the local host (data tier rule); public demo surface is replay only |
| T4 | Real product | Product Phase 2 data lights up more detector families through the capability profile; proposals target the registry the Product runtime actually resolves; real approver identity | A detector that was `unsupported` at Phase 1 runs with no code change when the superset profile (0.5.1 shape) is served; a proposal is published to the product-resolved alias with a named human approver | Contingent on Product and agent-core answers (section 7) |
| T5 | Spec breadth | 13 families, U31, fork, U28 AWS lab, load/chaos, a11y, retention GC at scale | Per spec 30.6 gates | Cut from the first push (section 6) |

Honesty notes: T1 is real operation of a real mechanism on simulated source events; it is not discovery on the bank dataset. T2 on E0 is real discovery, real Core, local only. T3 is the first tier that a third party could call "running".

## 2. Backward chaining

### 2.1 From the ten demo steps

For each step: what must exist (smallest prerequisite increments), the work packages that deliver them, and the tier where the step first becomes honest. Package ids are in section 3.

| # | Step (plan 2) | Smallest prerequisites, backward | Packages | First honest at |
|---|---|---|---|---|
| 1 | Snapshot/E0/observations wake the engine, nobody picks the category | trigger producer (scheduler tick + ingest event) <- durable job claimed by a worker <- job store on PG <- handler ABI; ingest endpoint <- exporter (exists) <- control-api contract | R-1, R-2, R-3, R-4, R-5, R-7 | T1 |
| 2 | Families measured, discarded candidates, investigation in progress | handler runs sensors over an adapter output <- U29/U30/U12 libs (exist) <- adapter reading S3 snapshot or PG observations <- S3 adapter; run events visible via SSE | R-6, R-7, R-5, P-2 | T1 (platform), T2 (E0) |
| 3 | Scout and verifier use SQL/wiki, separate verifier | Rust Core client invokes stage tasks <- service JWT, pin, binding callbacks served by control-api <- real model path through gateway <- spend ledger and stage policy | C-1, C-5, R-5, M-1, M-2, M-3 | T2 |
| 4 | Opportunity with population, mechanism, alternatives incl. do_nothing | mapping of finding to a catalogued Core capability by declared mechanism metadata <- seeded world with target plus decoys <- compiler DraftPlan | C-4, C-3 | T2 |
| 5 | Concrete change: entities, versions, diff | JCS hash parity <- DraftPlan <- dry-run via bridge route; writer executor client | C-2, C-3, C-1 | T2 |
| 6 | Scenarios on base and candidate, two distinct gates | CoreEvalPackage emitter from ScenarioCase <- result capture of the six evaluate outcomes <- U27 CombinedGate over a sealed U20 plan | C-6 | T2 |
| 7 | Failure leads to bounded revision | revision loop over real eval reports with a budget; builder re-invocation | C-8 | T2 |
| 8 | Human only for authority, approval fixes operation/hash | `waiting_human_approval` job state <- decision endpoint with step-up <- local human issuer (exists) <- console decision panel | C-7, R-5, R-10 | T2 (local issuer), T4 (real IdP) |
| 9 | Staging confirmed, exposure needs alias receipt | alias read via bridge (exists) <- publish receipt persisted before advance; promote is a separate human act with its own receipt | C-7, O-7 | T2 |
| 10 | New observations; memory published or contradicted; new investigation | exporter -> ingest (T1) <- release correlation U50 <- memory commit port durable (0004/0005) <- successor trigger in scheduler | C-9, R-4 | T2 |

### 2.2 From the deployed steady state

Steady state S* = on AWS staging, continuously: platform events arrive, jobs run, stages call Core, models are used within budget, a human approves, a release lands on staging, observations return, memory updates, alarms watch it, an operator can pause, restore or roll back. Each condition and what it needs:

| Steady-state condition | Needs (backward) | Packages | Who must act |
|---|---|---|---|
| Services stay up and restart safely | images pinned by digest in ECR <- release script <- engine image with 3 roles <- binaries; `/readyz` separate from `/healthz`; ECS health check declared (Podman ignores HEALTHCHECK) | R-8, D-1, R-5 | Claude |
| Runtime DB reachable by least privilege | `pulso_runtime` app secret, non-master (OPEN_GAPS: human bootstrap), KMS key policy, S3 and Secrets Manager endpoints or controlled egress | D-2, D-3, D-5 | user and DB/security owner |
| Secrets exist and rotate | secret containers (declared), values loaded by a human, key ceremony, rotation drill with overlapping `kid` | O-5, D-5 | user |
| Work arrives continuously | platform-exporter read-only credential to the Product DB or a read path; network path; or platform-sim task | P-3, D-5 | user and Product |
| Model spend bounded | provider-key hard cap, runtime stage policy (alias, model, price allowlist), reservation, circuit breaker, daily cap in RunConfig, AWS Budgets, kill switch | M-2, O-1, D-7 | user (key and caps), Claude |
| Stalls and spend are noticed | metric contract engine->infra, alarms (8 risks), SNS email confirmed, firing/resolved evidence | R-9, D-4, D-7 | Claude, user (confirm email) |
| A bad publish can be undone | ProposalRollout states, revoke path through Core, post-release monitoring through release correlation, receipts | O-7, C-9 | Codex (domain), Claude (Core ops) |
| Data can be restored | RDS snapshots, S3 versioning, tombstone reconciliation, measured drill | D-8 | Claude, user (approve) |
| Humans can operate it | SSM/ECS Exec path to console, runbooks, severity and on-call, evidence capture | D-4, O-2 | Claude, user (operator) |
| Core and gateway exist on AWS | agent-core workload slice (RDS PG16, secrets, sweep), gateway image digest and ECR, Cloud Map namespace | D-6 (external) | agent-core team via user |
| No data leaves its tier | data classification, egress profile, redaction tests, PL-C4 allow-list in the deployed path | O-3, P-2 | Claude, Codex |

### 2.3 Dependency graph and the real critical path

```
G-1 user/Codex unblock ----------------------------------------------+
G-2 verify-all   G-3 relay   G-4 crate skeleton                       |
        \            |           /                                    |
         +-----------+----------+                                     |
                     |                                                |
   R-1 control-api contract v0     R-2 JobHandler ABI + run-once      |
        |                  \        |                                 |
   R-5 control-api -----+   R-3 PG adapters -- R-4 worker+scheduler    |
        |   |           |        |                  |                 |
   R-10 console   R-6 S3 adapter +-- R-7 detect handler (platform) -- T1 local
        |                                           |
   R-8 image+compose -- R-9 metrics/alarms ---------+
        |                      |
   D-1 release script    D-4 infra deltas   D-2 AWS bootstrap (user)
        \___________ D-3 real plan (fix cycle) ____/
                          |
                     D-5 apply T1 on staging -- D-7 alarms/budget -- D-8 drills -- D-9 soak
   --------------------------------------------------------------------------------
   C-1 core-client -- C-2 hash parity -- C-3 compiler/writer ----+
        |                                    C-4 mapping (long pole of uncertainty)
   C-5 stage handlers (needs R-2, R-5 or fixtures) -- C-6 eval + U27 -- C-8 revision
        |                                                             |
   M-1 gateway local -- M-2 ledger/policy -- M-3 local model   C-7 human loop (needs R-5)
                                                                      |
                                                    C-9 correlation + successor -- C-10 integration = T2
   P-2 platform_live (Codex), P-3 real Product DB, O-* ops, D-6 Core+gateway on AWS = T3
```

Real critical paths (hours are focused effort of the serial chain, not totals):

| Target | Serial chain | Chain hours (ESTIMATE) | Why it is longer than the nominal path |
|---|---|---|---|
| T1 local | R-2 -> R-3 -> R-4 -> R-7 -> R-9 acceptance | 45-70 | The nominal one-day plan cuts the durable worker; for continuity it cannot be cut. Two-worker, kill -9 and PG-restart tests are slow to get right. |
| T2 local | G-1 -> C-1 -> C-5 -> C-6 -> C-7 -> C-9 -> C-10, with C-3/C-4 joining before C-6 | 70-110 | C-4 (mapping) is an intellectual risk, not volume; C-5 needs callbacks from R-5 (use the e2e-fixtures double first, swap later) |
| T1-AWS | D-2 (user, elapsed days) -> D-3 -> D-5 | 25-45 plus user latency | Mock-provider tests do not prove IAM, endpoints, KMS or quotas; first apply always produces a fix cycle |
| T3 | max(T2, T1-AWS) -> D-6 (external) -> O-7 -> D-8 -> D-9 | +40-70 | D-6 depends on the agent-core team's workload slice, which is not merged and is owned by someone we cannot reach directly |

The nominal "tomorrow" estimate of 18-24 h for a Rust-driven labelled run is plausible only for items C-1, C-4 (best case), C-10 on in-memory orchestration. It is not a path to a durable system and I do not count it as T1 or T3 progress.

## 3. Work packages

Owner key: CL = Claude (main thread or subagent), CX = Codex, U = user, EXT = another team via the user. Hours = focused hours for implementation plus own tests (ESTIMATE; adversarial review is +15-25 % and is not in the ranges). "Fallback" says what happens if the owner is unavailable. Locations are paths in `improvement-engine` unless prefixed `infra:`.
Real dependencies: PG16 and the Core image on `pulso-dev` (Podman, Claude's machine) unless said otherwise.

### 3.1 Stream G: unblock and hygiene (T0)

| ID | Package | Owner | Hours | Depends on | First RED | Location | Hand-off |
|---|---|---|---|---|---|---|---|
| G-1 | Unfreeze Codex with a reduced scope (domain crates + C-3, C-4, C-6, R-7, P-2, O-7 domain); user moves the three genuine local slices (temporal-successor outbox 0005, `paired_scenario.rs`, `platform_source_policy.rs`) and any other wanted worktree to GitHub; declare the other 4 dirty worktrees dead or merged | U + CX | 1-2 (U), 3-5 (CX consolidation) | none | n/a (decision) | journal, GitHub | CX posts one entry listing what was published and what was dropped |
| G-2 | `scripts/verify-all.ps1` plus `infra/scripts/verify-all.ps1`: aggregate Rust (`verify-local-ci`), core-bridge, e2e-core, platform-*, console, bridge-contract, Terraform tests (incl. the ones CI skips: workload, workload_iam, engine_platform, bridge_services, envs), emit `receipt.json` {head, toolchain versions, suites, results, duration}; try once to read why hosted CI is red (`gh run view`), record, then stop | CL | 3-5 | none | script exits non-zero if a suite is missing or red; receipt hash changes with the head | `scripts/`, `infra:scripts/` | PR bodies quote the receipt instead of "local green" |
| G-3 | Codex relay: `handoff/<id>/` folder (git bundle or patch, `verify.ps1`, expected receipts); CL runs Codex's `#[ignore]` PG tests and any Podman test on `pulso-dev` and replies with a receipt in the journal | CL | 2-3 | none | a Codex test that needs PG fails under the relay with a clear "needs-podman" status, passes after CL run | `D:\.codex\factored\handoff\` (outside repos), `scripts/relay.ps1` | one-way bundle, one reply entry |
| G-4 | Workspace skeleton PR: empty crates `control-api`, `worker`, `core-client`, `engine-adapters` (pg, s3), `OWNERS.md` (path -> owner), reserved migration number blocks (CX 0005-0049, CL 0050+), single owner for `Cargo.toml` workspace members and `Cargo.lock` regeneration rule | CL | 2-3 | G-1 decision D1 | workspace builds and clippy `-D warnings` with empty crates; a test fails if a crate is not in `OWNERS.md` | root `Cargo.toml`, `OWNERS.md` | prevents merge conflicts on shared files for every later PR |
| G-5 | Relay the ask list of section 7 to the user in one message | CL | 1 | none | n/a | `docs/plan-real/` | user answers asynchronously, defaults apply meanwhile |

### 3.2 Stream R: runtime shell (T1) and its deployability

| ID | Package | Owner | Hours | Depends on | First RED | Location | Hand-off |
|---|---|---|---|---|---|---|---|
| R-1 | control-api contract v0: OpenAPI + goldens + conformance suite extracted from what Claude already consumes (exporter ingest, bridge callbacks and binding, lab-broker audience routes, console `DebugApi`, decision and step-up routes of 20.1/16.13.6, SSE feed, `/healthz /readyz /internal/v1/version`). Reference implementation = existing `e2e-fixtures` double | CL | 6-9 | G-4 | conformance suite passes against the double and FAILS against an empty server (proves it bites) | `control-api-contract/` (new, mirrors `bridge-contract/`) | CL publishes first; CX reviews domain shapes within one journal round |
| R-2 | `JobHandler` ABI and run-once harness: handler(job, ports) -> outcome {complete, retry_wait, waiting_dependency, waiting_human, failed, unknown}; effects only through ports (artifact repo, run events, Core task port, model port, quota); in-memory store for run-once, PG store for the worker; golden event sequences | CL (CX review) | 5-8 | G-4 | one handler under in-memory and under PG store emits identical event sequence; a handler that writes outside a port is rejected by a lint test | `crates/worker/src/handler.rs` | ABI doc in journal before C-5 and R-7 start |
| R-3 | PG adapters: `DurableJobStore` (U06) on `pulso_jobs`, quota window (U05) with conditional reservation, claim with advisory lock + `SKIP LOCKED`, lease/heartbeat/fence, sweeper, `append_run_event` per-root lock | CL | 14-22 | R-2 | two workers on one job -> one release; late response after lease expiry is fenced; PG restart mid-claim loses nothing | `crates/engine-adapters/pg`, `migrations/0050+` | migrations reviewed by CX (domain reducers stay in `crates/core`) |
| R-4 | worker binary + scheduler: trigger producers (observation batch, snapshot, timer, successor), lane quotas, heartbeat, graceful shutdown, `LISTEN/NOTIFY` as wake-up only with polling recovery, `kill -9` test, `lane` fairness | CL | 10-16 | R-2, R-3 | `kill -9` mid-step: sweeper requeues, zero duplicate effects; lost NOTIFY still processed; 10 runs of one snapshot -> one job | `crates/worker` | feeds C-5, R-7 |
| R-5 | control-api binary: ingest with U29 PG adapter and cursor/ack, service-JWT verification (aud, jti, per-route), bridge callback and binding routes, debug read routes (runs, timeline, evidence), commands returning 202 + job id, SSE from `pulso_run_events` with polling fallback, version/readiness | CL | 14-22 | R-1 | platform-exporter (existing, 51 tests) against the real binary: replayed batch deduped, gap flagged, unknown event type quarantined and acked (PL-02/03) | `crates/control-api` | console and exporter flip from double to real by config only |
| R-6 | S3 artifact adapter: temp blob + CAS head, digest check on read, orphan GC with grace period, upload grants for the exporter and sandbox | CL | 8-12 | G-4 | blob with no PG ref is an orphan; PG ref with bad digest blocks read and raises an alert event | `crates/engine-adapters/s3` | LocalStack S3 now, real S3 in T1-AWS |
| R-7 | Platform detection handler v0: observation batch -> job -> platform sensor (existing U30) -> insight artifact with n/denominator/as-of/provenance; stops at insight (PL-C5); late event triggers window revision | CX (fallback CL) | 8-12 | R-2 | late event after window close reopens the review; a detector needing `tool_call` returns `unsupported` naming the missing capability | `crates/worker/src/handlers/platform.rs` (CX-owned file) | first end-to-end proof of T1 |
| R-8 | Engine image: multi-role entrypoint (`control-api`, `worker`, `migrate`), non-root, read-only rootfs plus writable `/tmp`, health check declared in compose, env names aligned with infra `engine_platform` (`PULSO_DATABASE_DSN`, `PULSO_SERVICE_SIGNING_KEY`, `PULSO_VERIFIER_KEYS`, `PULSO_CORE_BRIDGE_URL`, `PULSO_SANDBOX_TASK`); compose services; `dev.ps1 up` | CL | 6-10 | R-4, R-5 | image refuses to start with a missing secret and prints names only; `AGENTCORE_ALLOW_DEMO`-style demo flags absent | `Dockerfile`, `local/compose.yaml`, `scripts/dev.ps1` | the digest is what D-1 packs |
| R-9 | Observability v1: engine->infra metric contract (namespace, bounded labels, units), OTel tracing with span links API->queue->worker->Core, 8 alarm definitions (stalled progress, queue age, ingest freshness, API 5xx and p95, dead jobs, model budget/breaker, Core readiness, gateway error rate) with owner and runbook link; Grafana alert rules locally; test turns the collector off | CL (CX co-signs metric names) | 10-14 | R-4, R-5 | stalled-progress alarm fires when a worker is paused with queued jobs and resolves when resumed; collector loss does not change durable state | `docs/contracts/metrics.md`, `crates/*/src/telemetry.rs`, `local/` | D-4 turns the contract into CloudWatch alarms |
| R-10 | Console live: `provider=http` against the real control-api, SSE, empty/error/partial states, decision panel stub | CL | 4-6 | R-5 | browser test: console shows the T1 insight from the real API with the server killed and restarted mid-stream | `debug-console/` | n/a |

T1 subtotal: 85-131 h. Parallel lanes: (R-2,R-3,R-4), (R-1,R-5,R-10), (R-6,R-8), (R-7 by CX), (R-9).

### 3.3 Stream C: closed loop on real Core (T2)

| ID | Package | Owner | Hours | Depends on | First RED | Location | Hand-off |
|---|---|---|---|---|---|---|---|
| C-1 | `core-client`: endpoint profile, HTTP client with transport policy, error classifier per Annex D, service-JWT signer (`sub=worker:<id>`, `job_id` binding, `Idempotency-Key`, `evc-` derivation copied exactly from ADR 0011), pin constants moved from 0.5.0/53e729d to 1.3.0/c814c2b, instance probe | CL (fallback CX) | 10-14 | G-4 | replays every golden of `bridge-contract/`; classifier maps every Annex D error; live smoke on the real image on `pulso-dev` | `crates/core-client` | CX consumes the existing `CoreTaskPort` seam; no signature change without a journal entry |
| C-2 | Wire and hash parity: `core_content_bytes`, JCS `content_hash` equal to Core on the 250-file wire vectors; wire-drift check against `core-bridge/wire/agent_core@c814c2b` | CL | 5-7 | C-1 | Rust hash differs from Core on a golden -> test red; unknown wire file -> drift failure | `crates/core-client/src/wire` | n/a |
| C-3 | Compiler: `ChangeSpec` -> `DraftPlan` -> `changes[]`, closure, cascade prediction, dry-run compare with `candidate_hash`, kinds beyond Add+Flow (replace, policy, eval_suite as feasible), writer executor client with base preconditions | CX | 14-20 | C-1, C-2 | dry-run `candidate_hash` equals freeze on the real image; entity outside the supported subset is `unsupported`, not silently dropped | `crates/core/src/change_compiler.rs` | publishes DraftPlan fixtures to CL for the e2e swap |
| C-4 | E0 -> Core mapping: resolver that links a measured finding to a catalogued capability through declared mechanism metadata (not category name); seeded world with the target flow and decoys; honest `unlinked` when nothing fits | CX (resolver) + CL (assets world 3-5 h) | 8-14 (+3-5) | C-2 | rename the winning category: same mapping result (mutation); catalogue containing only decoys: `unlinked`, never forced | `crates/core/src/e0_mechanism_resolution.rs`, `agent-core-assets/worlds/pulso-evolution` | this is the real intellectual risk; budget for a failed first attempt |
| C-5 | Core stage handlers: scout, verifier, builder_design invocations as `JobHandler`s: pin exact release, bind private context before effects, read result and facts (whitelist), reconcile unknown (crash after send), 429 and quota paths; against the `e2e-fixtures` control-api first, real R-5 later | CL + CX | 12-18 | R-2, C-1 | kill after send: job ends `unknown`, reconcile reads the run, no resend; unbound context: invocation refused | `crates/worker/src/handlers/core_stage.rs` | n/a |
| C-6 | Evaluation: U47 CoreEvalPackage emitter from `ScenarioCase`, U48 capture of the six `evaluate` outcomes (incl. `failed_infra`, lost response, 409 body), U27 `ImprovementEvidence` + `CombinedGate` over a sealed U20 plan (seed in unpublished `paired_scenario.rs`) | CX | 14-20 | C-1, C-3, G-1 | native pass without baseline does not pass the combined gate; `mechanism_proxy` never reports a causal claim; unknown blocks | `crates/core/src/{native_evaluation,evaluation_plan,combined_gate}.rs` | CL runs real-image tests via relay (G-3) |
| C-7 | Human loop (U21): `waiting_human_approval`, decision endpoint with step-up, approval fixes operation and hash, publish with `Idempotency-Key`, separate promote, receipts persisted before advance, console decision panel | CL (endpoint, console, issuer) + CX (state machine) | 12-18 | R-5, C-5 | bot approve rejected; approve without step-up rejected; second publish with same key creates no second release; stale staging yields `proposal_stale` | `crates/control-api`, `crates/core/src/authority.rs`, `debug-console/` | n/a |
| C-8 | Bounded revision loop on real eval reports (budget, no hidden retry) | CX | 5-8 | C-6 | a failing candidate triggers at most N revisions then ends `failed_exhausted` visibly | `crates/core/src/revision.rs` | n/a |
| C-9 | Closing the cycle: release correlation U50 / CAP-37 (`release.*` events), traceparent Rust->bridge (CAP-64) and `known_gaps.json` by SHA, successor trigger from new observations, memory use or contradiction durable (needs 0004/0005 temporal receipts + successor outbox from G-1) | CL (correlation, traceparent) + CX (memory) | 10-14 | C-7, G-1 | observations after publish are attributed to the release; contradicted memory starts a successor job; trace id appears in the receipt | `core-bridge/`, `crates/core/src/memory_*.rs` | n/a |
| C-10 | Integration: swap the Python stand-in for the Rust stack in `e2e-core` and `demo`; run E2E-REAL-01 then DEMO-AUTO; negatives; report with `target/sha/doubles[]/labels`; fix Annex D mismatches found | CL | 8-12 | C-1..C-9 | demo run whose report lists any stand-in as engine output fails a report-honesty test | `e2e-core/`, `demo/` | T2 gate |

T2 subtotal: 101-150 h. Parallel lanes: (C-1,C-2) then (C-3, C-4, C-5) then (C-6, C-7) then (C-8, C-9) then C-10.

### 3.4 Stream M: model path (grounded in the llm-gateway repo)

How the path works (VERIFIED): Core's `HttpLLMGateway` calls `POST /v1/generate` with a per-consumer Bearer token; the request carries prompt, inputs, optional closed-subset schema and the profile (alias, model, temperature, max_tokens, timeout_s, structured, price as decimal strings); one provider call, no retries; cost is computed by the gateway from the price WE send; errors are typed (`rate_limited`, `timeout`, `unavailable`, `invalid_output`, `refused`) and `invalid_output`/`refused` carry usage. `POST /v1/jev` is a transport for JEV and needs agent-core PR #28 on main (VERIFIED: not on main). Our `pulso-core-runtime` wraps the Core gateway port in `BindingGuardGateway(SpendMeteringGateway(...))` (VERIFIED in the adoption doc). The gateway has no release tag (VERIFIED) and the AWS workload is not declared (VERIFIED, infra ADR 0004).

| ID | Package | Owner | Hours | Depends on | First RED | Location | Hand-off |
|---|---|---|---|---|---|---|---|
| M-1 | Real gateway in local compose: build from a pinned commit of `pulso-factored/llm-gateway` (no tag exists), `core-egress` network, consumer tokens, alias pointing at a scripted OpenAI-compatible upstream; replace the image overlay and the double that always answers cost 0; readiness uses the authenticated empty-body probe (400 means authenticated); declare the container health check yourself | CL | 4-6 | none | with the real gateway, a call with 1000/500 tokens at the profile price meters `0.000260`; a bad token is a readiness failure, not "unavailable on every call" | `local/core/compose.core.yaml`, `core-bridge/` | T2a |
| M-2 | Spend ledger and policy in our runtime (the gateway will not do it): meter failed calls that carry usage, honor `usage_known`, reserve before dispatch, stage policy as allowlist of (alias, model, max price, max_tokens, timeout) with fail-closed unknown profile, per-run and per-day caps from `RunConfigRevision`, circuit breaker leading to `waiting_dependency`, and a distinct outcome for "gateway down" so an agent node does not become `escalate(low_confidence)` | CL (CX supplies RunConfig fields) | 8-12 | M-1 | a profile with a price 1000x the allowlist is rejected before dispatch; a 502 `invalid_output` with usage is charged; gateway stopped: job `waiting_dependency`, not `low_confidence` | `core-bridge/src/pulso_core_runtime`, `crates/core/src/run_config.rs` | feeds O-1 and the budget alarm |
| M-3 | Local real model for E0: gateway alias to a local OpenAI-compatible server on the host (Ollama or vLLM class, a 7-8B instruct model, `structured: prompted`); measure JSON validity and latency; keep the profile and price (0) versioned | CL + U (hardware) | 3-6 | M-1 | scout stage on E0 treated payload returns schema-valid output through the local alias with zero bytes leaving the host (egress test) | `agent-core-assets` profile, `local/` | the only real-model path allowed on E0 |
| M-4 | Hosted smoke on synthetic-authorized fixtures only (never E0 or bank rows), through the gateway, with a capped key: one scout and one verifier call, receipts show provider, model, tokens, cost | CL + U (key, cap) | 3-4 | M-1, M-2 | call without a key fails closed; run beyond the daily cap is refused before dispatch | `e2e-core/` live-model profile (opt-in) | live suite stays separate from PRs |
| M-5 | Recorded-provider fixtures from M-3/M-4 runs (labelled `recorded`) so CI is deterministic; prompt/profile versioning; drift report when a model changes behavior | CL + CX | 6-10 | M-3 | replay of a recorded run reproduces output digests; changing the profile changes the digest | `agent-core-assets`, `crates/core` | n/a |
| M-6 | Jev through the gateway `/v1/jev` | CL | 4-6 once unblocked | EXT (agent-core PR #28 on main) | typed decision from the real runtime through the gateway; enum invalid and low confidence cases | `core-bridge/` | DEFAULT: skip Jev; use `llm_structured` and `rule` providers |

M subtotal: 28-44 h.

### 3.5 Stream D: deploy pipeline and AWS (T1-AWS, T3)

| ID | Package | Owner | Hours | Depends on | First RED | Location | Hand-off |
|---|---|---|---|---|---|---|---|
| D-1 | Local release tooling `scripts/release.ps1`: build images (engine 3 roles, `pulso-core-runtime` incl. exporters, sandbox-lab) with Podman by pinned base digests, run `verify-all`, `cargo audit`, `pip-audit`, secret scan (gitleaks class), SBOM, record digests, emit `deploy-manifest.json`, run `validate_manifest.py` and `deploy_plan.py --dry-run`, push to ECR with the human's short-lived credentials | CL | 8-12 | R-8, G-2 | manifest builder refuses a tag-only image reference, a mismatched `contracts_version` or `pin_manifest_digest` (existing validators M-01..M-10), and a dirty tree | `scripts/`, `infra:release/` | replaces `release.yml`/`plan.yml`; a self-hosted runner is an option only after the user checks that its pricing does not draw on the exhausted budget (UNVERIFIED) |
| D-2 | AWS bootstrap with the user: account and region (provisional us-east-1), SSO profile, state bucket + lock + KMS (external bootstrap), who owns the shared foundations (are they already applied by the agent-core infra owner?), alarm mailbox, optional OIDC provider and subjects (not needed for a human-applied flow) | U (2-4) + CL (2-3) | 4-7 | none (elapsed days) | `terraform init` against the real backend succeeds with the SSO profile; no local backend is ever used for staging | `infra:terraform/envs/staging/backend.hcl` | blocks D-3 |
| D-3 | First real `terraform plan` of staging with foundations plus `engine_platform` and `bridge_services`, then the fix cycle (IAM, VPC endpoints, KMS key policy, SG references, Cloud Map ownership, secret shapes). Expect it to fail in ways mock providers cannot show | CL | 10-18 | D-2, D-4 | plan is clean and `validate_plan.py --stage infra` passes; a plan that touches a task definition in infra stage is rejected | `infra:terraform/` | each fix lands as a small infra PR |
| D-4 | Infra deltas that are ours: `core-migrate` task, sweep wiring (when the Core slice lands), engine alarm module from R-9 contract, refresh fixtures from pin `894fa65` to `c814c2b` and record the real `pin_manifest_digest` (VERIFIED stale in infra docs), confirm the provisional engine variable names against R-8, ECS Exec/SSM access for the console (no ALB, no public ingress), add `terraform test` for the roots CI skips | CL | 10-16 | R-8, R-9 | alarm module test: each alarm has owner, runbook, window and recovery; a task definition with demo flags is rejected | `infra:terraform/modules`, `infra:release/` | n/a |
| D-5 | Deploy T1 to staging: DB role and application secret bootstrap (human), secrets loaded (human), `engine-migrate`, services at desired count 1, smoke `target=real_aws`, receipt; source = platform-sim as an ECS task or Product DB (label) | CL + U (approver, secrets) | 8-14 | D-1, D-3, R-8, R-9 | smoke fails closed if `doubles` is non-empty or the tenant binding is missing; `result=not_run` is never reported as success | `infra:docs/runbooks`, receipts private | runbook rehearsal first with `--dry-run` |
| D-6 | Core runtime, exporters and gateway on AWS: consume the agent-core workload slice (Core RDS PG16, secrets, namespace, security groups) and a gateway image digest; if absent, DEFAULT is no AWS Core (T2 stays local) | CL + EXT | 10-20 | EXT, M-1, D-5 | readiness gates: engine is not updated before Core `/readyz` and contract match; `manifest_incompatible` blocks | `infra:terraform/envs/*` | single owner of the `pulso-core-runtime` ECS name and Cloud Map name must be agreed (infra open question 8) |
| D-7 | Alarm destinations and cost guard on AWS: confirm SNS mailbox, prove firing and resolved on the real destination, AWS Budgets and billing alarm (ask who owns account-level budgets), kill switch drill (pause all lanes, `PULSO_LLM_MODE=disabled`, desired count 0) | CL + U | 6-10 | D-5, O-1 | a queued job with workers stopped fires the stalled alarm to the mailbox and clears after resume | `infra:terraform/modules/core_alarms`, `docs/runbooks` | n/a |
| D-8 | Restore and rollback drills: RDS snapshot restore into a scratch instance, S3 version restore, tombstone reconciliation before access, digest-pair rollback as a unit, measured RPO/RTO recorded in the DeploymentProfile | CL + U (approve) | 8-12 | D-5 | restore leaves a missing blob as `unavailable`, never serves a revoked artifact; drill exceeding the target fails the gate | `infra:docs/runbooks` | n/a |
| D-9 | Soak 72 h with synthetic traffic plus light chaos (kill a task, throttle the gateway, drop the collector, rotate a key with overlapping `kid`) | CL | 6-10 (+elapsed) | D-7, D-8 | zero lost batches or jobs, zero duplicate releases, lag within the configured budget; report with p50/p95/p99 | `docs/reports/` | n/a |
| D-10 | `prod` (demo) environment created only for a demo window, then scaled to zero | CL + U | 4-8 | D-9 | n/a | `infra:terraform/envs/prod` | needs separate authorization (spec 10) |

D subtotal: 70-119 h (excluding D-10).

### 3.6 Stream O: operations, security, governance not in the spec (or only named there)

| ID | Package | Owner | Hours | Depends on | First RED | Where it belongs |
|---|---|---|---|---|---|---|
| O-1 | Cost and budget governance, five layers: (1) provider-key hard cap, (2) runtime stage policy and reservation (M-2), (3) per-run, per-day, per-tenant caps in `RunConfigRevision`, (4) AWS Budgets plus billing alarm, (5) kill switch `pulso pause [lane]` as a durable command plus `desired_count=0` runbook. Also an on-demand cost report script (tokens, USD, ECS, RDS) | CL (+CX run config) | 6-10 | M-2 | a budget-exhausted job ends `waiting_dependency` with a visible reason; the kill switch stops claims within one poll interval and survives a worker restart | engine (`crates/worker`, `core-bridge`), infra (budgets), runbook |
| O-2 | Incident handling: severity matrix, operator and escalation (single operator today: the user), eight runbooks (stalled work, budget breach, Core unavailable, gateway degraded, exporter gap, bad publish and rollback, secret exposure and rotation, restore), evidence capture checklist, post-incident journal template | CL | 8-12 | R-9 | tabletop test: each alarm links to a runbook that names its first command and its recovery condition | `infra:docs/runbooks/`, `docs/runbooks/` |
| O-3 | Data classification, retention and erasure: table in section 8, S3 lifecycle and CloudWatch retention in Terraform, redaction tests on logs and spans, PL-C4 allow-list enforced in the deployed ingest path, erasure by tombstone for platform-derived data, no prompts or rows in logs or alarms | CL + CX | 6-10 | R-5, P-2 | a canary string placed in turn text, prompt and SQL result never appears in logs, spans, receipts or alarm payloads | engine and infra; legal sign-off belongs to the user |
| O-4 | Threat model and independent security review: control-api (service JWT, replay, callbacks), bridge callbacks, sandbox RunTask, secrets, egress, console access path; plus supply chain (digest pinning, SBOM, dependency audit) | independent reviewer agent + CL | 8-12 | R-5, D-3 | cross-tenant read through a debug route is rejected; a replayed service JWT `jti` is rejected | `docs/security/` |
| O-5 | Secrets lifecycle: generation (CAP-63), human loading ceremony (never in chat or Git), rotation drill with overlapping `kid` (Core has no hot reload, N-09, so restart window), gateway token overlap (gateway has one token per consumer; ask Q6), leak scan in CI | CL + U | 6-10 | D-5 | rotation drill: new key accepted, old key rejected after the window, no downtime beyond the planned restart | infra secrets, runbook |
| O-6 | Tenant model: DEFAULT single tenant per environment (`PULSO_TENANT_ID` required), schema and RLS multi-tenant ready, tenant bootstrap seed, cross-tenant tests on every `pulso_*` table and every route | CX + CL | 6-10 | R-3 | a request with another tenant id reads zero rows and is audited |
| O-7 | Rollout and rollback of published proposals: `ProposalRollout` states (published_staging -> observing for a maturity window -> promote_requested -> promoted -> regressed? -> revoked), post-release monitoring through release correlation, human-gated revoke or alias flip with receipts, automatic action limited to "stop proposing for this agent" (never auto-rollback of authority), compatibility with Core's publish-is-not-promote | CX (domain) + CL (Core ops) | 12-18 | C-7, C-9 | a regression signal on a promoted release opens a revoke request and blocks new proposals for that agent without changing the alias by itself |
| O-8 | Load and capacity per spec 8 (1x, 3x, 10x bursts, concurrent scan), cost per 1,000 model calls and per corroborated opportunity | CL | 8-12 | T3 | burst of 1,000 observations per layer during a scan: zero loss, lag within budget | after T3; hardware declared |

O subtotal (O-1..O-7): 52-82 h.

### 3.7 Stream P: the real product platform

| ID | Package | Owner | Hours | Depends on | First RED | Location | Hand-off |
|---|---|---|---|---|---|---|---|
| P-1 | Relay the Product questions (read path, payload schemas, sequence contiguity, Phase 2 timeline, demo-row marker, retention, which Core registry and alias the Product runtime resolves, human approver identity) | CL -> U | 1 | none | n/a | section 7 | defaults apply |
| P-2 | `platform_live` Rust adapter on `platform-contract` 1.1.0: event catalog with quarantine, gap rules, `available_at=ingested_at`, as-of reconstruction from events, capability profile used by detectors (`unsupported`/`insufficient_*`), privacy allow-list and credential tables denied by construction (local `platform_source_policy.rs` is the seed), stop at insight | CX | 14-20 | G-1 | `login_accounts` read refused before any query; unknown event type counted and the batch still acked | `crates/source-adapters`, `crates/core/src/platform_*.rs` | R-7 consumes it |
| P-3 | Exporter against Product's real DB: read-only credential and network path (PG replica or SQLite snapshot), first real read, schema drift tolerance, demo-row exclusion, no `turns.text` by default | CL + EXT | 6-10 | D-2, EXT answers | exporter refuses to start with a credential that can write; sequence gap on the real source is flagged | `platform-exporter/` | DEFAULT: platform-sim |
| P-4 | Phase 2 readiness: superset-profile contract tests (0.5.1 shape), detector activation by profile only, target registry and alias mapping for Product-owned agents, interim human approver mapping (CAP-44 stays blocked) | CL + CX | 8-14 | P-2 | serving a profile with `tool_call` enables the existing detector with no code change | `platform-contract/`, `crates/core` |

P subtotal: 29-45 h.

### 3.8 Totals

| Stream | Hours (ESTIMATE) |
|---|---|
| G unblock | 11-17 |
| R runtime shell | 85-131 |
| C Core loop | 101-150 |
| M models | 28-44 |
| D deploy and AWS | 70-119 |
| O ops, security, governance | 52-82 |
| P product platform | 29-45 |
| Total implementation | 376-588 |
| Adversarial review loops (1-3 per consolidated PR) | +15-25 % |
| H hardening and breadth (T5), not sized in detail | 120-250 more |

## 4. Parallelization design

### 4.1 Lanes and disjoint file ownership

Repo layout assumption (VERIFIED, main 41492cb): `crates/{core,source-adapters,runner}`, `core-bridge/`, `e2e-core/`, `bridge-contract/`, `platform-{contract,sim}/`, `platform-exporter/`, `local-identity/`, `agent-core-assets/`, `debug-console/`, `demo/`, `local/`, `migrations/`, `scripts/`, `contracts/`. New (G-4): `crates/{control-api,worker,core-client,engine-adapters}`, `control-api-contract/`, `OWNERS.md`.

| Lane | Owner (slots) | Files (exclusive) | Packages | Subagent use inside the lane |
|---|---|---|---|---|
| L0 integrator | Claude main thread | `OWNERS.md`, root `Cargo.toml`, `scripts/verify-all`, journal, `docs/plan-real/*` | G-2..G-5, integration, merges of stacked branches | none; it only reads receipts and decides |
| L1 worker | Claude subagent 1 | `crates/worker`, `crates/engine-adapters/pg`, `migrations/0050+` | R-2, R-3, R-4, C-5, O-1 | one implementer, one adversarial reviewer (concurrency) |
| L2 control-api | Claude subagent 2 | `crates/control-api`, `control-api-contract/`, `debug-console/` | R-1, R-5, R-10, C-7 (endpoint and console) | implementer; second agent for console browser tests |
| L3 Core client and runtime | Claude subagent 3 | `crates/core-client`, `core-bridge/`, `local/core/`, `agent-core-assets/` (assets part), `e2e-core/`, `demo/` | C-1, C-2, M-1..M-5, C-9, C-10 | implementer plus a real-image test runner on `pulso-dev` |
| L4 release and infra | Claude subagent 4 | `infra:*`, `scripts/release*`, `Dockerfile`, `local/compose.yaml` | R-8, R-9, D-1..D-10, O-2, O-4, O-5 | one agent per infra root; independent infra/security reviewer |
| L5 adapters | Claude (shares slot with L1 or L4) | `crates/engine-adapters/s3`, `platform-exporter/` | R-6, P-3 | n/a |
| X1 domain engine | Codex lane 1 | `crates/core/**` (all existing files), `crates/source-adapters` | C-3, C-4, C-6, C-8, P-2, O-7 | Codex's own subagents; independent review by an agent not its author |
| X2 handlers and platform | Codex lane 2 | `crates/worker/src/handlers/**` (CX-owned subtree), `platform-contract` review | R-7, O-6, P-4 | same |

Real concurrency (planning input, not a promise): 4 Claude lanes plus the main thread plus 1-2 Codex lanes. If only 3 slots exist, merge L5 into L1 and drop O-4 to after T2; T1 slips by about 2-3 sessions.

Shared-file rules (cheap and mandatory): (a) workspace `Cargo.toml`, `Cargo.lock`, `OWNERS.md` change only through L0; (b) migrations: CX numbers 0005-0049, CL numbers 0050+, one PR per migration pair with its test; (c) `crates/worker/src/handlers/**` belongs to CX, `crates/worker/src/*.rs` to CL, with the `JobHandler` trait frozen after R-2 (changes need a journal entry); (d) contracts are append-only versions; (e) `docs/IMPLEMENTATION_STATUS.md` is rewritten by one owner per PR to avoid conflicts.

### 4.2 Contract hand-offs: who publishes what first

| Order | Contract | Publisher | Consumer | Gate before the consumer starts |
|---|---|---|---|---|
| 1 | `JobHandler` ABI and golden event sequences (R-2) | CL | CX (R-7, C-3 harness), CL (C-5) | journal entry with the trait and a passing run-once demo |
| 2 | control-api contract v0 with conformance (R-1) | CL | CX (shapes), CL (R-5, R-10, exporters), console | conformance green against the double |
| 3 | `bridge-contract/` and ADR 0011 (exists) | CL | CX and C-1 | already published; C-1 adds a Rust conformance runner |
| 4 | Capability catalogue schema and mechanism metadata (C-4) | CX | CL (assets world) | one schema, two fixtures (target, decoy) |
| 5 | DraftPlan fixtures and `ChangeSpec` examples (C-3) | CX | CL (C-10 swap) | published with their dry-run hashes |
| 6 | Metric and alarm contract (R-9) | CL, co-signed by CX | infra (D-4) | table of metrics, labels, windows, owners |
| 7 | Release manifest extension for engine digests and migrations head | CL | infra validators | `validate_manifest.py` extended and green |
| 8 | Product questions and answers (P-1) | CL via user | CX (P-2), CL (P-3) | answer or DEFAULT recorded in the journal |

### 4.3 Integration points and merge cadence

- Integration branch `integration/real` (local, long-lived, Claude): every lane stacks on it so nobody waits for a merge ("never depend on a merge to keep working"). Consolidated PRs are cut from it, one per milestone, not one per feature.
- PR plan for T1 (6 PRs): P-A skeleton + verify-all (G-2, G-4); P-B contracts and ABI (R-1, R-2); P-C PG adapters and worker (R-3, R-4); P-D control-api and console live (R-5, R-10); P-E S3 adapter, image, compose (R-6, R-8); P-F observability and detection handler (R-7, R-9). T2 (5 PRs): core-client + hash; compiler and mapping; eval and gate; human loop and correlation; e2e swap. T3 (4 PRs in infra, 2 in engine).
- Each PR body carries the `verify-all` receipt (head, suites, results) and `doubles[]`. Merging is done by the user; hosted CI stays informational.
- Rebase rule: when the user merges PR N, the integration branch rebases once; lanes pick it up at their next checkpoint.

### 4.4 What each team does while blocked

| Blocker | Claude does | Codex does |
|---|---|---|
| Codex frozen or no GitHub (now) | R-*, M-*, D-1..D-4, O-* (everything that is not domain semantics); builds the relay | when unfrozen: consolidate, then C-4 first (longest uncertainty) |
| No Podman for Codex | runs Codex's PG and Core tests through the relay and posts receipts | writes pure-Rust domain code and goldens against `bridge-contract/` fixtures |
| No AWS access | local T1/T2, release script, `terraform plan` against mocks plus offline validators | n/a |
| agent-core PR #28 or Core slice absent | local gateway and `llm_structured` providers; no Jev | n/a |
| Product answers absent | platform-sim and capability profiles with the default superset | P-2 against `platform-contract` 1.1.0 |
| Claude's contract not yet published | n/a | domain work against the existing `bridge-contract` and `platform-contract` |

### 4.5 Coordination protocol (cheap)

One journal entry type: `HANDOFF <id> from=<team> to=<team> contract=<path>@<sha> verify=<command> receipt=<path>`; one reply type: `RECEIPT <id> result=<ok|red> head=<sha> suites=<n/n>`. A bundle drop folder for Codex (G-3). No chat coordination. Status board = one table in the journal updated by L0 at each tier gate (ready, in progress, blocked, reviewing; blocked agents are not counted as active lanes). Relay to the agent-core, gateway and Product humans always through the user, in one consolidated message (G-5).

## 5. Prioritization

Scoring: value (V) to the user's stated goal, risk reduction (R), unblocking power (U); 1-5 each.

| Package group | V | R | U | Rule applied | Verdict |
|---|---|---|---|---|---|
| G-1..G-4 | 3 | 5 | 5 | cheapest unblock of everything | first, day one |
| R-1, R-2 | 3 | 4 | 5 | the two contracts that decouple lanes | first week |
| R-3..R-5 (durable shell) | 4 | 5 | 5 | continuity cannot be bolted on after the demo; also the largest uncertainty in volume | start immediately in parallel with C-1 |
| C-1, C-2 | 5 | 4 | 5 | nothing real touches Core from Rust without them | start immediately |
| C-4 (mapping) | 5 | 5 | 4 | biggest intellectual risk; if it fails, T2 degrades to honest `unlinked` | start by day two, time-box 14 h, report failure early |
| D-2 (AWS bootstrap) | 3 | 5 | 4 | has user latency in days; starting it late is the main schedule risk of T1-AWS | ask in the first message |
| D-3/D-5 (first real apply of T1) | 4 | 5 | 3 | surfaces unknown unknowns early, while the stack is small | as soon as R-8 yields an image |
| M-1, M-2 | 4 | 5 | 4 | cost and policy are the defects that hurt later; real gateway also fixes the cost-0 double | with C-5 |
| C-6, C-7 | 5 | 4 | 3 | the demo's gates and human authority | after C-3/C-5 |
| R-7 (detection on platform data) | 4 | 3 | 3 | the first honest running behavior | after R-4 |
| R-9, D-7, O-1, O-2 (alarms, budgets, runbooks) | 3 | 5 | 2 | "not monitored unless alarms fire" (spec 26.3); runaway spend is the worst early failure | before the first unattended run on AWS |
| O-7 rollout/rollback | 4 | 4 | 2 | required to call it operable, but needs C-7 and C-9 | T3 |
| P-2..P-4 | 3 | 3 | 2 | grows with Product answers; P-2 is Codex's best use while Podman is unavailable | parallel, Codex-led |
| M-3 local model | 4 | 3 | 2 | only real-model path on E0 | after M-1 |
| M-4 hosted smoke | 2 | 3 | 1 | cheap proof that the hosted path works on allowed data | one short session |
| M-6 Jev | 2 | 2 | 1 | blocked externally | wait |

Cut or defer explicitly (each with the reason): 13 source families and portfolio optimization (spec allows 2 families for the first cut); U31 detector self-evolution; fork lanes (U34-F/FE); AWS lab sandbox U28 (needs a threat model and escape tests before any bank data; synthetic only until then); CAP-23, CAP-41, CAP-44 (blocked by decisions outside our code); public demo hosting beyond immutable replay; multi-AZ high availability and SQS trigger (spec says a benchmark must justify it); hosted CI green (replaced by receipts; do not spend effort until budget exists); a second AWS environment running continuously (prod is created for a demo window only); promote-to-prod automation (publish to staging plus an operator-gated promote is enough); advanced autoscaling.

Tier order by reasoning: T0 then T1 and T2 in parallel (T2 does not wait for T1 because handlers are ABI-first); T1-AWS starts as soon as an image and user inputs exist because first apply is the largest unknown; T3 after both. If the user wants the demo before durability, T2 can be shown first with run-once and the trigger labelled `manual_command`; the plan does not make T1 a prerequisite of showing it.

## 6. What is not in the spec (or only named) and where it belongs

| Topic | Gap | Decision in this plan | Owner and package | Repo or place |
|---|---|---|---|---|
| Deploy without GitHub Actions budget | spec 26.2 assumes workflows; none exist, hosted CI is red | local release script producing the manifest; human `apply` of a saved plan; later optionally a self-hosted runner after checking pricing | CL, D-1 | `scripts/`, `infra:release/` |
| Accounts, keys, state backend | external bootstrap; nothing exists | ask list; no local backend ever for staging or prod | U, D-2 | external |
| Secret lifecycle | declared containers only | generation, loading ceremony, rotation drill, leak scan | CL, O-5 | infra and runbook |
| Cost and budget governance | gateway has none; no AWS budget | five-layer design (O-1) | CL, O-1 | engine, runtime, infra |
| Monthly AWS spend | unknown | ESTIMATE only: a continuous staging with NAT, private endpoints (interface endpoints cost per AZ), two small RDS instances and about six small Fargate tasks is likely in the low hundreds of USD per month; prod only for a demo window; scale to zero when idle; compute with the AWS calculator in D-3 | U decides ceiling, CL, D-3/D-7 | infra |
| Tenant model | `tenant_id` everywhere, no provisioning story | single tenant per environment, RLS-ready, cross-tenant tests | CX + CL, O-6 | engine |
| Observability for operators | metric contract and alarms undefined (OPEN_GAPS) | R-9 metric contract, D-4 alarm module, firing/resolved on the real destination | CL | engine and infra |
| Data retention and erasure | OPEN_GAPS: no period, no erasure path | proposal in section 8, tombstone erasure, lifecycle rules | U (approve), CL, O-3 | infra |
| Incident handling | none | O-2 severity and runbooks, single operator today | CL, O-2 | runbooks |
| Rollout and rollback of published proposals | publish and promote exist in Core; rollback of an engine proposal undefined | ProposalRollout and revoke with human authority | CX + CL, O-7 | engine |
| Human approval UX at scale | local issuer only | console decision panel; real IdP is CAP-44 (blocked) | CL, C-7 | console |
| Access to the internal console on AWS | no ingress by design | ECS Exec and SSM port-forward, no ALB until the edge contract exists | CL, D-4 | infra |
| Supply chain and image provenance | digest pinning only | SBOM, dependency audit, pinned bases, secret scan in `release.ps1` | CL, D-1, O-4 | scripts |
| Threat model and security review | named, not done | O-4 independent review before any non-synthetic data | reviewer agent | `docs/security/` |
| Disaster recovery | RPO/RTO unmeasured | restore drill and DeploymentProfile values | CL, D-8 | runbooks |
| Load and capacity | benchmark not run | O-8 after T3 | CL | reports |
| Product platform Phase 2 data | roadmap unknown | profile-gated detectors, superset tests, ask Product | CL + CX, P-4 | contracts |
| llm-gateway policy | no allowlist, no limits, no tag | our policy in runtime (M-2) and asks Q1, Q2, Q6, Q7, Q8 | CL | runtime |
| Model data tiers | hosted models forbidden on E0 | local model path M-3 | CL, M-3 | local |
| Pin and fixtures drift | infra docs cite `894fa65`, engine pins `c814c2b` | D-4 refresh and record the real `pin_manifest_digest` | CL | infra |

## 7. Risks, external dependencies and the exact asks

Everyone below is reachable only through the user. One consolidated message (G-5); defaults let work proceed.

| # | Dependency | Exact ask for the user to relay or decide | Default if no answer | What slips if never answered |
|---|---|---|---|---|
| A1 | User | Lift the Codex freeze with a reduced scope (domain crates; list in G-1); move the three genuine local slices to GitHub; confirm that Claude may add new Rust crates `control-api`, `worker`, `core-client`, `engine-adapters` | Claude builds the shell crates; Codex stays frozen; domain packages C-3, C-4, C-6, O-7, P-2 wait and T2 slips by their size (about 60-90 h) | T2 breadth; T1 is unaffected |
| A2 | User and AWS administrators | Which AWS account and region for staging; SSO profile for a human operator; existing state bucket, lock and KMS or permission to bootstrap; are shared foundations already applied and by whom; alarm mailbox (needs confirmation click); is the Product platform in this account or another (VPC peering, PrivateLink or a replica) | no AWS apply; everything runs on `pulso-dev`; D-3 uses `terraform validate` and mock tests only | T1-AWS and T3 (the whole "deployed" claim) |
| A3 | agent-core team (jzapata owns infra) | (a) land PRs #23, #24 and #28 on main (they are in side branches); (b) status and ownership of the Core workload slice (Core RDS PG16, secrets, namespace, security groups, sweep, `core-migrate`); (c) one `pulso-core-runtime` ECS name and Cloud Map name: ours or theirs; (d) who records `pin_manifest_digest`; (e) answers to infra questions 1-9 and relay items 2-9 of `AGENT_CORE_RELAY_FOR_USER.md` | local Core only; no Jev; `llm_structured` providers; bridge services declared but not applied | D-6, M-6, T3 Core on AWS |
| A4 | llm-gateway owner | tag `v0.1.0` and publish a digest, or permission to build from a pinned commit and push the digest to our ECR; asks Q1 (allowlist and caps per consumer), Q2 (rate and concurrency limits), Q6 (two active tokens, authenticated readiness route), Q7 (Idempotency-Key), Q10 (stable error code) | we build from a pinned commit locally; our runtime enforces policy; ledger is ours | gateway on AWS (D-6) |
| A5 | User (model keys and money) | an OpenRouter-class key with a hard spend cap for synthetic-only smoke (suggest a small cap such as 20-50 USD, ESTIMATE); confirmation that hosted models never see E0 or bank rows; host hardware for a local 7-8B model (GPU or enough RAM); daily and per-run caps | scripted provider behind the real gateway (T2a); local model only if hardware allows | M-3, M-4; T2b/T2c are labelled absent |
| A6 | Product team | read path (PG replica, snapshot, API); payload schemas per event type; sequence contiguity and `ingested_at` trust; demo-row marker; Phase 2 roadmap per entity; retention and redaction rules; whether data may reach hosted models; which Core registry and aliases the Product runtime resolves and whether Pulso may write proposals to it; who the human approver is and through what identity provider | platform-sim; capability profile superset; local issuer for approvals | P-3, P-4, T4 |
| A7 | User | monthly AWS ceiling and who owns account-level budgets; named operator and alert destination; approval authority for each apply | propose a soft ceiling and one operator (the user); apply only with explicit approval of a saved plan | D-7 |
| A8 | User and legal/security | data tiers of section 8 confirmed, including that nothing from E0 or the bank CSVs enters AWS; retention proposal approved | all E0 and bank data stays local; AWS only hosts synthetic and Product-authorized data | O-3 sign-off |

Technical risks (with mitigations):

| Risk | Likelihood and impact | Mitigation |
|---|---|---|
| First AWS apply uncovers IAM, endpoint, KMS or quota failures | high, medium cost (18-34 h already budgeted) | do it with T1 while the stack is small; small PRs per fix |
| E0 mapping fails to produce an exact Core artifact | medium-high, high impact on the demo | time-box; ship honest `unlinked` as a positive result for safety; use the seeded decoy world to prove non-forcing |
| Durable worker concurrency bugs (leases, fencing, NOTIFY) | medium, high | ABI-first, property tests, two-worker and kill -9 tests before any handler logic is added |
| Rust async stack mismatch with Codex's sync libs | medium, medium | domain crates stay sync; shell wraps them in blocking tasks; decided in D2 below |
| Model quality on a local 7-8B model is too low for scout/verifier | medium, medium | recorded-fixture path (M-5), label results, never claim discovery quality; use hosted only on synthetic fixtures |
| Gateway has no policy and we trust a caller-supplied price | known, medium | M-2 allowlist in runtime plus provider key cap |
| Core pin moves again (agent-core PR #28, N-items) | high, medium | dual-run suite and `pin-watch` exist; bump is its own PR with expand/contract test |
| Podman is Claude's only and is the single point of integration testing | medium, medium | keep `pulso-dev` stable; relay protocol; do not run Codex tests in parallel with Claude suites on the same machine |
| Cost surprise on AWS or models | medium, high | O-1 layers; desired count 0 when idle; billing alarm before first apply |
| Hosted CI red hides regressions | known, medium | `verify-all` receipts; never quote hosted CI as evidence |

## 8. Data tiers, retention and residency (proposal for approval)

| Tier | Data | Where it may live | Hosted models | Retention default (proposal) |
|---|---|---|---|---|
| D-local | E0 package, original bank CSVs, E0 derived extracts and holdout | the team's host, Podman, LocalStack/MinIO in loopback only | NO (local model only) | until the user deletes; nothing replicated |
| D-synth | `platform-sim` traffic, synthetic scenario fixtures, `agent-core-assets` worlds | local and AWS | YES with a capped key | runs and receipts 180 days; blobs 90 days unless referenced by published memory |
| D-product | Product Phase 1 and 2 platform data (real shape, demo content today) | AWS only after Product confirms authorization; `turns.text`, names and credentials excluded by allow-list | only if Product says so (DEFAULT no) | event batches 180 days; derived insights as D-synth; erasure by tombstone and rebuild |
| D-ops | job rows, run events, audit, model receipts (no prompts, no rows), spend ledger | AWS and local | n/a | audit and receipts kept; CloudWatch logs 30 days on staging; RDS automated backups 7 days; S3 versioning on, noncurrent 30 days |

## 9. Timeline in working sessions

Definition: one session = about 5 focused hours of one lane. "Calendar" is not promised. Ranges include rework but not user latency or the other teams' lead times. Adversarial review is included at +20 %.

| Milestone | Cumulative sessions (wall-clock, assuming 4 Claude lanes plus 1-2 Codex lanes) | Confidence | What drives the range |
|---|---|---|---|
| T0 unblocked | 1-2 | 80 % | user action on G-1; Claude work is small |
| T1 local (durable shell, platform loop, alarms) | 8-12 | 60 % | R-3/R-4 concurrency testing, R-5 breadth |
| T1-AWS (applied, smoke, alarm delivered) | 11-17 | 40 % | user bootstrap latency (days), first-apply fix cycle |
| T2 local, T2a (scripted provider behind the real gateway, Rust-driven E2E-REAL-01) | 14-20 | 50 % | C-1 to C-6 chain; Codex availability |
| T2 with local model and negatives (T2b), partial DEMO-AUTO | 20-28 | 40 % | C-4 mapping outcome; model quality |
| T3 (Core and gateway on AWS, rollout/rollback, drills, 72 h soak) | 30-42 | 30 % | agent-core slice and gateway digest (external), drills, soak elapsed time |
| T4 | not schedulable | n/a | Product Phase 2 data and approver identity; agent-core PR #28 |
| T5 | after T3, 25-50 additional | 20 % | breadth |

If Claude runs alone (Codex frozen): T1 unchanged at 8-12; T1-AWS unchanged; T2 grows to 26-38 because the domain packages (C-3, C-4, C-6, C-8, O-7, P-2) fall to Claude; T3 to 38-54.
If AWS access arrives late: nothing except T1-AWS and T3 moves; the local tiers continue.
If hosted CI were restored: no effect on this plan; receipts remain the evidence.

## 10. Decisions to debate (the ones most likely to be wrong)

| # | Decision | My position | Alternative | Why it matters |
|---|---|---|---|---|
| D1 | Ownership transfer of the new Rust service crates (control-api, worker, adapters, core-client) from Codex's lane to Claude, with the domain crates and hard semantics staying with Codex | Yes, because Codex is frozen, has no Podman or GitHub, and every one of these crates needs real PG and Core images that only Claude can run | keep all Rust with Codex and wait for unfreeze | changes T2 by 30-60 sessions of Codex time and decides whether a durable system exists in weeks or months; needs user approval and Codex's consent |
| D2 | Async stack: axum and tokio for control-api and worker, domain crates stay sync, bridged with blocking tasks; reqwest or ureq (blocking) in `core-client` | Yes; SSE and many concurrent leases need it, domain code is unaffected | single-threaded sync server for control-api (tiny_http) | a wrong choice is expensive to undo after R-5 |
| D3 | All autonomous stages are `JobHandler`s against ports from the start, so "run-once" is just a worker over an in-memory store; durable worker is not deferred past T2 | Yes | build a throwaway run-once orchestrator first (the one-day plan) | avoids rewriting every stage after the demo, at the price of delaying the first run by about 5-8 h (R-2) |
| D4 | Deploy T1 (no Core, no model) to AWS first, before Core and the gateway exist there | Yes, it is the earliest honest steady state and de-risks AWS | wait for the agent-core slice and deploy everything together (CAP-62) | decides whether AWS problems are found in week 3 or week 8 |
| D5 | Data tiers: nothing from E0 or the bank CSVs enters AWS and hosted models are synthetic-only; real models on E0 are local | Yes, it follows spec 28.6 literally | ask for an exception to run discovery in AWS with a hosted model | removes "continuous AWS discovery on the bank dataset" from the target; the continuous AWS system runs on platform-shaped data |
| D6 | Cost control lives in our runtime (allowlist, reservation, caps, kill switch) because the gateway has none, with the provider key cap as the hard stop | Yes | ask the gateway team to implement per-consumer policy first | gateway changes belong to another team and may take long |
| D7 | Deployment is a local script plus human apply of a saved plan; no OIDC auto-deploy | Yes, aligned with the spec and with the exhausted Actions budget | self-hosted runner or a paid budget top-up | determines whether releases are reproducible by a third party without an account on GitHub billing |
| D8 | Single tenant per environment with multi-tenant-ready schema | Yes | build tenant provisioning now | avoids unused machinery; RLS tests keep the door open |

## 11. Immediate next actions (first session)

1. Send the ask list (A1-A8) to the user; start with A1 and A2 because they have latency.
2. L0: G-2, G-3, G-4 in one stacked branch.
3. L2: R-1 (control-api contract) and L1: R-2 (handler ABI); L3: C-1 start; L4: D-1 plus R-8 scaffolding.
4. CX (once unfrozen): consolidate and publish the three slices (G-1), then start C-4 with a time box.
5. Journal: one entry announcing the lanes, the file ownership table and the HANDOFF format, so Codex and Claude read the same rules.
