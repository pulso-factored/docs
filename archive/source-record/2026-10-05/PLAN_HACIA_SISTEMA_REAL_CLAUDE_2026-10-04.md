# Plan to the real Pulso system: final plan (v5), DEMO-0 first

Date 2026-10-04. Final author: Claude (orchestrator of the main thread). One self-contained document: front page, first sessions, glossary, body (sections 1-15), annexes A-F at the end. Baselines read at authoring: improvement-engine main `853b029` (1683 tracked files), agent-core main `c814c2b` (pin, contract 1.3.0), llm-gateway main `63155b6`, infra `origin/main` (177 files). Hours are focused lane-hours (implementation, own tests, first review loop), ranges are about 80% bands. Every number below is printed by the checker of annex B from the table of annex A (output in annex C); the prose is generated from the same values.

## Front page

### Goal (restated faithfully)

Ignore the "24 hours" scenario. Implement incrementally and reach, as early as possible, a REAL system: a durable, continuous detection and self-improvement engine that integrates (1) the real product platform (the Product team's platform: cases, turns, assignments, `event_log`, phases 1-3), (2) the real agent-core and its execution (registry, runs, evaluation, approval, publication), (3) the real infrastructure (AWS, Terraform, deployed services) and (4) the real llm-gateway. It uses the initial dataset and the augmented dataset (E0 = `pulso_muestra_e0`, and the bank CSVs) and really runs: ingests data, searches for signals, analyses problems and opportunities, and loops signals to improvement proposals expressed as agent-core artifacts of any kind (tools, flows, compiled trees, agents, Jev decision models, prompts, eval suites, policies, templates, combinations), through agent-core, executed for real with real models, interacting with the product: the spec's real "magic demo" (ten steps) and beyond. Cover everything still missing per the spec and what the spec does not specify; group, prioritise and organise it for parallel execution by subagents and two teams (Claude holds the main thread, Codex supports); feasible and efficient.

Directives kept: incremental, DEMO-0 as early as it is honest; scope NOT shrunk; Claude 70-80% of the remaining hours and Codex 20-30%; the Claude path independent of Codex (0 hard edges; Codex outputs are optional swap-ins); maximum parallel partition with a total path map and conflict matrix; E0 and the CSVs authorized for local tests and our own infrastructure (the user lifted the earlier ban there) but never for third-party hosted models beyond treated payloads (ASK-1); labelled roleplay doubles accepted for DEMO-0; methodology mapped rule by rule (section 10).

### The answer in 10 bullets

1. **What remains:** 229 work packages (WP = a row of annex A) in 29 lanes (a lane owns disjoint paths): 1419-2157 focused hours (midpoint 1788, about 1967 with 10% churn); Claude 1055-1600, Codex 364-557.
2. **DEMO-0 first:** the first honest end-to-end run of the ten steps, built only by Claude from today's code: 27 WPs, 142-219 h, serial floor 65.5 h, 12.4 (11.0-14.2) sessions at LVL-A (range in brackets; assumed capacity 14-18 lane-hours per session). The v4 headline (76-111 h, 6.4 sessions) was rejected by the final review: five pieces of the thread were in no WP.
3. **Honest by construction:** detection by the existing Rust sensor on E0; a real Core, a real gateway path, role-played models (`agent_roleplay`, treated payloads only); the report prints what is NOT exercised (Jev, revision loop, memory and successor, model quality).
4. **Independence:** Claude to Codex hard edges: 0; Codex depends only on Claude's frozen pack (30 edges); 40 optional swap-in edges; the rule costs Claude 117-172 h of stand-ins and live per-kind WPs. If Codex stays frozen nothing on the Claude path shifts.
5. **Ladder of demos,** each re-running the same thread with fewer doubles: DEMO-0 (Python host) > DEMO-1a (Rust steps) > DEMO-1 (Rust shell) > DEMO-2 (durable worker, `kill -9`) > DEMO-3 (AWS staging) > DEMO-4 and DEMO-5 (hardening, artifact breadth). Gates GT0, GT05, GT1A, GT1B, GT2, GT3 are reachable with every ask unanswered (checker-proved); GT05m and GTA need asks by nature.
6. **Critical path** to GT1B: 20 WPs, 145.5 h, all Claude; GT1B is 39.5 (35.1-45.1) sessions at LVL-A and 30.1 (26.3-35.1) at LVL-B (a model, not data).
7. **Parallel in structure, bounded in practice:** lanes per wave 8 17 21 12 22 14 (W0..W5); live concurrency is the number of implementers (3 per team at LVL-A), not of lanes (section 8).
8. **Environment measured before improved:** host 16 GB with 5.7 GB free at the last sample, `.wslconfig` 10 GB / 8 CPUs / swap 8 GB, C: 112 GB and D: 1.2 TB free; capacity levels LVL-A/B/C are assumptions re-baselined at GT0 and TW-1.
9. **Beyond the spec:** deployment, secrets, cost, tenancy, retention, rollout, approval UX, blob store, observability, incidents all have WPs (section 11).
10. **You decide four things first:** ASK-1 treated payloads, ASK-2 lift the Codex freeze, ASK-3 merge delegation, ASK-4 one image download; each has a needed-by and a safe default (section 14).

### DEMO-0: definition and time to reach it

`demo/run.ps1` (replay) plus one live run: E0 ingested locally; the existing Rust local-sim sensor (not the planted old `demo/` judge) admits one signal family with recorded discards; a role-played scout and a distinct verifier work over an E0-backed treated lab with deterministic recompute; a role-played builder proposes a change chosen from the ReadBase capability catalogue (`unlinked` and `not_evaluable` are valid endings); a generic Python compile turns Replace Prompt plus Add EvalSuite into a draft plan over a seeded base world; the REAL Core validates it by dry-run and runs the evaluation arms; a non-planted stand-in gives a structural gate verdict (`quality_claims: forbidden`); a simulated issuer approves; publish to local staging; alias read; observation. Printed labels: `model=agent_roleplay`, `jev=not_exercised(blocked: agent-core PR 28 not on main)`, `issuer=simulated`, `product=simulated`, `host=python`, `compile=claude-standin(python)`, `base_world=seeded`, `data_origin=generated_sample`.

| Measure | Value (from the checker) |
|---|---|
| Hours, WPs | 142-219 h over 27 WPs (10.0% / 10.2% of all hours); the ancestors of GT0 are exactly the demo path |
| Serial floor | 65.5 h (DC0 > ED0 > SMAP > Q1r > INT0 > GT0) |
| Sessions LVL-A / B / C | 12.4 (11.0-14.2) / 9.6 (9.6-11.0) / 9.6 (9.6-9.6) (the floor binds at B and C) |
| With the Codex enabling pack on the same agents | 14.1 (12.5-16.1) / 10.7 (9.6-12.5) / 9.6 (9.6-9.6) (pack WPs G0gr, CF0, FRZ0, BK0 add 24.5 h, about 1.7 sessions at LVL-A; accepted so Codex starts in session 3; the greedy schedule of the first sessions needs 13) |
| Not in those hours | 2-3 sessions of live responder windows (a role-playing subagent holds one agent slot 10-30 min per live run); plan 13-15 calendar sessions at LVL-A |
| Confidence | medium-low; only DEMO-0 is dated; re-baselined at GT0 and TW-1 |

### Claude and Codex split, and the independence rule

Overall 1419-2157 h: Claude 1055-1600 (74.3% / 74.2%, low / high), Codex 364-557 (25.7% / 25.8%). Through T1b: 750-1134, Claude 550-829 (73.3% / 73.1%), Codex 200-305 (26.7% / 26.9%); per wave and tier the split varies by design. Rule, stated the right way round: **Codex WPs depend only on Claude's frozen artifacts (the W0 pack G0f, G0gr, CONTR, CF0, FRZ0, BK0 plus ENV0 and ENV4); Claude WPs have no hard dependency on any Codex WP.** Where the real system would consume Codex output, Claude owns a labelled stand-in behind the same port and the Codex output is an optional swap-in (`~` edge) that gates nothing. Under silence on ASK-2 the twelve Codex lanes execute 0 hours.

### The first asks (full table with needed-by and defaults in section 14)

- **ASK-1** (before the first live roleplay run on E0-derived input, session 6): confirm the responder gets only treated payloads, never raw E0 or CSV rows. Default: treated payloads only.
- **ASK-2** (before session 2): lift the Codex scope freeze CX-0180 for offline lanes. Default: Codex executes 0 hours.
- **ASK-3** (before the first W0 PR): let Claude merge its own green trains. Default: you merge each train; teams keep working stacked.
- **ASK-4** (before M1, session 1-2): approve one named download, the Go builder image for llm-gateway. Default: the existing contract double, labelled `gateway=stand-in`.

## First sessions (what runs in parallel)

A session is about 8 wall hours; LVL-A = orchestrator + 3 implementers + 1 reviewer, one cargo slot, one stack, about 16 lane-hours of Claude work per session. The schedule below is a greedy simulation of the demo-path WPs plus the Codex enabling pack and WTR1 at that capacity (hand-offs allowed inside a session, priority to the longest remaining chain and, in sessions 1-3, to the pack): it needs 13 sessions, against the formula's 14.1 (12.5-16.1) with the pack. The responder (a role-playing subagent) takes one agent slot only during live windows. Codex runs offline on its own machine.

| Session | Claude: parallel tracks (WP ids) | Codex (needs ASK-2) | You |
|---|---|---|---|
| 0 | none | none | answer ASK-1 to ASK-4 and ASK-15 in five short sentences |
| 1 | G0f OWNERS and Codex brief; CONTR schemas; FRZ0 pack (8 of 11 h); WTR1 worktree inventory | none yet | none |
| 2 | FRZ0 closes; G0gr audit; BK0; CF0: the pack is published (journal CONTRACT-PUBLISHED); DC0 starts | XSTUB stubs and WTR2 (list-only) as soon as ASK-2 is answered | ASK-2 needed now |
| 3 | DC0 closes (data-class gate); SNET spike (reachability, 60 s and 600 s limits, Go image check); G0e target dirs; G0p W0 receipt script; M0RP shim starts | W1 starts from the pack: DMAPV, DVREC, DWIRE, DGATE, CT1 (offline, depth-1 PRs) | merge the first PR (ASK-3) |
| 4 | M0RP closes; ED0 first Windows build of the Rust runner (own target dir) and E0 detection; TPS scanner starts | WDX, DMAPC, DORIGm, FX22a, DPLAT | none |
| 5 | TPS closes; G0gp facts; WRLD0 seeded world; G1 report schema and honesty tests start; M1 real gateway (or the labelled stand-in) | continues; about 3 PRs per wave at depth 1 | announce a free-RAM window (ASK-23) |
| 6-7 | G1 closes; SMAP builder harness (first live roleplay on E0-derived input); ED0L E0-backed lab; CRV0 prepares | DEVAL, BKF, BKT, DPL1 | ASK-1 needed now |
| 8-9 | M3 stage hardening and replay; P2py simulator; CMPpy compile; GSIpy verdict; CLT0 timeout; RPP responder protocol; M2a spend ceiling | DJC, DPGc, FX22b | none |
| 10-11 | Q1r ten-step ratchet in replay, then INT0 first full run on Podman, replay drift, live windows with the responder lane | continues | live windows need a free-RAM window |
| 12-13 | CRV0 loops 1-3 and fixes; TRN0 trains; GT0: receipts, all 8 honesty tests green, `doubles[]` listed, journal entry, DEMO-0 report (replay plus one live run) | continues | watch DEMO-0 |
| 14+ | W1: ENV0 baseline, STP1 CMP GSI E3b (Rust steps), ED0b original CSV, CRV1, then GT05 (DEMO-1a) | W1 and W2 swap-in candidates | ASK-5 to ASK-14 as they come due |

## Glossary (acronyms and id families, in order of first use)

| Term | Meaning |
|---|---|
| Pulso | the product family; "the engine" = the improvement-engine repository (Rust libraries plus one local-sim CLI today) |
| Core, agent-core | the other team's execution platform: registry, runs, evaluation, approval, publication; we consume it through HTTP only |
| llm-gateway | the other team's Go service in front of model endpoints (`POST /v1/generate`, per-consumer bearer, aliases in `LLM_ENDPOINTS`) |
| E0, CSV | `pulso_muestra_e0` (augmented dataset, a generated sample) and the original bank CSVs (initial dataset) |
| WP, lane | WP = work package (a row of annex A: id, owner CL or CX, hours, deps, first RED test, acceptance). Lane = a team-owned set of path globs; `L-*` Claude lanes (17), `X-*` Codex lanes (12) |
| CL, CX | Claude, Codex. Journal ids `CL-nnnn`, `CX-nnnn` in the shared journal |
| Wave W0..W5 | scheduling band: W0 DEMO-0 sprint plus enabling pack, W1 DEMO-1a, W2 DEMO-1, W3 DEMO-2, W4 hardening and breadth, W5 T3, AWS, T5 |
| Tier T0..T5, TA | what exists at each stage: T0 DEMO-0, T0.5 Rust steps, T1a Rust shell, T1b durable, T2 hardening, T3 breadth, TA AWS, T5 load and security |
| GTn, DEMO-n | GT = gate WP (evidence package) that closes a demo: GT0 (DEMO-0), GT05 (DEMO-1a), GT05m (its local-model rung), GT1A (DEMO-1), GT1B (DEMO-2), GTA (DEMO-3), GT2 (DEMO-4), GT3 (DEMO-5) |
| S1, S2, S3a, S3b | strangler stages: Python host, Rust steps called by Python, Rust shell run-once, durable worker; RG-1..RG-5 = retirement gates of the Python host |
| LVL-A/B/C, HW-1..3 | capacity levels (A current, B software-only, C hardware) and the three hardware options of ASK-14; both are assumptions |
| doubles[] | the engine-generated list of every stand-in, simulated or role-played part of a run; status vocabulary in section 1 |
| `agent_roleplay` | a real HTTP path and real gateway whose model answers are written by role-playing subagents; plumbing only, `quality_claims: forbidden` |
| treated payload | what the engine itself sends to a model after the spec's pre-ModelPort treatment (pseudonymised ids, no raw sensitive fields) |
| TPS, RPP, SMAP, ReadBase | treated-payload scanner; responder protocol and runbook; S-MAP-lite (finding to valid artifact) harness; the engine's read model of Core capabilities and catalogue |
| ratchet, E2E-THREAD-01 | one test file with the ten demo steps, red until each step is real; re-run on every host and rung with a `host` column |
| stand-in, swap-in, `~` | stand-in = a Claude implementation of a Codex-owned semantic behind the same port; swap-in = optional adoption of the Codex implementation; `~DEP` marks an optional edge in the table |
| FROZEN, FRZ0 pack | frozen artifacts Codex may depend on: G0f, G0gr, CONTR, CF0, FRZ0, BK0 (W0), ENV0, ENV4 (W1); FRZ0 is the digest-pinned pack of schemas, goldens and traces |
| C-1..C-13 | the 13 contracts of section 7.3; CONTRACT-CHANGE and CONTRACT-PUBLISHED are journal tags |
| ASK-n, EXT-1..3 | a one-sentence decision for you with a needed-by and a safe default; EXT = messages you relay to the agent-core team, the Product team, the gateway owners |
| `needs`, `paths`, `@lane` | table columns: asks a WP cannot run without; path globs the WP edits (`@lane` = anywhere in the lane's own globs) |
| Streams | WP id families by stream: ENV environment, G governance, C contracts, M models, Q integration and E2E, P platform, E engine and control-api, K core-client, V evaluation and memory, H human authority, B artifact breadth, D Codex domain and reviews, I console, observability, ops, A AWS |
| RC1-RC3 | review classes (3, 2 and 1 loops); CRVn Claude independent review WPs, REVn Codex opportunistic reviews, RVCn Claude review of Codex, TRNn and TRXn train integrators (Claude, Codex); SEAM-1 = the Rust seam PRs (JWT, idempotency, hash, egress) |
| TW-n, TWn | TW-n is a tripwire (objective red/green rule), TWn its evidence WP |
| CAP-n, U-n, PL-n | capability, unit and platform-contract item numbers of the spec (V3) |
| Jev | the decision-model service behind `/v1/jev`; Core-side support is agent-core PR 28, not on main |
| trains, stacks, bundles | a train is one consolidated PR per 25-35 lane-hours; a stack is a chain of PRs each based on the previous; a bundle is a `git bundle` in `exchange/` for unpublished work |
| session, lane-hour | a session is about 8 wall hours of the orchestrator; a lane-hour is one focused implementer hour |

## Body

### 1. Definition of "real": vocabulary, data classes, demos

**1.1 Honesty vocabulary.** Every step line of a run report carries one status and one data class. `doubles[]` is generated BY THE ENGINE from observed facts (URL that answered, image digest, Core `/internal/v1/version` and manifest digest, gateway `model` echo, receipt provider, scanner id), never hand-written. Reports (`contracts/engine-run/`, WP G1) carry `target`, `sha`, `contract_revision` and `host` per step.

| Status | Meaning |
|---|---|
| `real` | real dependency, real data path, engine-driven, full coverage promised by the tier |
| `real-narrow` | real dependency and path, one family, kind or path only |
| `local-model` | real small model on our hardware; quality claims bounded by the measured schema-valid rate |
| `agent_roleplay` | real HTTP path and real gateway; answers written by role-playing subagents; plumbing and mapping only, `quality_claims: forbidden` |
| `recorded` | digest-keyed replay of a recorded response, with provenance; never shown as live |
| `stand-in` | real downstream driven by a Python host, fixtures, or a Claude implementation of a Codex-owned semantic |
| `simulated` | synthetic source or scripted actor (platform-sim, local issuer as human) |
| `not_exercised` | the thread did not reach this part (Jev, revision loop, memory and successor in DEMO-0) |
| `blocked(<dep>)` | named external dependency (Jev PR 28, CAP-41 bank, CAP-44 IdP, Product Phase 2) |

Secondary tags: `semantics=claude-standin`, `compile=claude-standin(python)`, `gate=claude-authored`, `suite=assets_handwritten`, `authority=claude-standin`, `hash=core-authoritative`, `base_world=seeded`, `gateway=stand-in`, `data_origin=generated_sample`, `treated=scanner:<id>`, `scheduled-ingest`, `unsupported_source`. Ladder rungs map to statuses: rung 0 `real`, rung 1 `agent_roleplay`, rung 2 `recorded`, rung 3 `stand-in` or `simulated`.

Honesty tests (they bite) and the WP that turns each green: (1) `real` while a receipt provider is `agent_roleplay`, `recorded` or scripted fails (G1); (2) a receipt whose data class is E0, CSV or original-treated and whose provider is third-party (hosted or `agent_roleplay`) fails unless it carries a passing scanner id, and a hosted REAL model also needs `third_party_ok` citing the user's sentence (TPS); (3) a mapping keyed to the winning category fails the rename and permute mutation test (ED0, SMAP); (4) per-port Core double provenance and model price source are listed and a template-fallback stage output fails (G1); (5) world, suite, simulator effect and judge carry `author` fields and the suite is sealed before the candidate exists (G1, WRLD0, GSIpy); (6) a report with `host=python` cannot carry a label above DEMO-1a (G1); (7) scout and verifier use distinct actors and different model identities (RPP); (8) a tracked file with E0 markers or a `data=E0` receipt body fails the push scan (DC0). G1 ships tests 1, 4, 5, 6 green and 2, 3, 7, 8 as red skeletons; all eight are green at GT0.

**1.2 Data classes (binding).**

| Class | Where it may run | Which model may see it |
|---|---|---|
| `synthetic` (independently authored) | anywhere | any model, hosted with a capped key included |
| treated payload | anywhere | roleplay responder and local model, only through the TPS allow-list; a hosted REAL model only after ASK-8 |
| E0 / CSV raw (rows, raw conversation text, derived extracts) | local host and our own infrastructure; never committed (digests and counts only) | local processes only; NEVER a third-party model, hosted or roleplay |
| ops (job rows, run events, receipts, ledger) | anywhere | n/a |

The user lifted the earlier ban on running E0 and the CSVs in local tests and our own infrastructure; the ban on third-party models stays except treated payloads (ASK-1 confirms the condition, you may widen it later). The same rule binds every developer agent, Claude and Codex (both are hosted third parties): they work from schemas, digests and synthetic fixtures, not raw E0 text; the Codex onboarding brief (G0f) says so. The step 2 to 3 hand-off: local sensors run on raw E0 and emit signals; the engine's pre-ModelPort treatment produces the treated payload; the scanner admits it; only then does the roleplay scout see it. E0 is itself a generated sample (`synthetic/platform_sample.py`), so every report says `data_origin=generated_sample`: the engine discovering what the generator encodes is discovery relative to the engine, not evidence about real customers.

**1.3 Demos, tiers and gates (each demo re-runs the same thread with fewer doubles).**

| Demo | Tier | Gate | Stage | What exists and what is observable | Doubles that remain (each has a scheduled rung-up) |
|---|---|---|---|---|---|
| DEMO-0 | T0 | GT0 | S1 | `demo/run.ps1`: section 2; replay green plus one live run; `E2E-THREAD-01` with all ten steps labelled | model `agent_roleplay`; Jev `not_exercised`; issuer `simulated`; product `simulated` with a real Core alias read; host `stand-in(python)`; compile and verdict stand-ins; seeded world |
| DEMO-1a | T0.5 | GT05 | S2 | Rust steps (recompute, validation, compile, gate) called by the Python host; original CSV slice (ED0b) real-narrow; model rung stays roleplay replay | `semantics=claude-standin`; host python |
| DEMO-1a-m | T0.5 | GT05m | S2 | optional rung-up: local GPU model, measured schema-valid rate (needs ASK-7) | `local-model` quality bounded |
| DEMO-1 | T1a | GT1A | S3a | Rust shell run-once, control-api lite, authority state machine, thin memory; approval simulated by default (H1r upgrades to one real recorded CLI approval, ASK-11) | jobs in memory; trigger manual; Codex semantics are stand-ins |
| DEMO-2 | T1b | GT1B | S3b | PG jobs, worker, `kill -9` survives, an ingest batch starts a run unaided; Python host demoted | label `scheduled-ingest` (not "continuous") |
| DEMO-3 | TA | GTA | | same thread on AWS staging, alarm fired and resolved, rollback drill (needs the AWS asks) | prod untouched; Product outbound `blocked(product-phase-2)` |
| DEMO-4, DEMO-5 | T2, T3 | GT2, GT3 | | hardening, then breadth: flow, template, policy, decision model, agent, bundle, tool, Jev (blocked) with evidence | remote IdP, bank, real Product DB, Jev in Core |

"Continuous" in the spec means the prequential replay protocol (spec 28.4 and 28.5); until the replay driver (RPL1 stand-in or DREPLAY swap-in) lands, a scheduler plus queue is called `scheduled-ingest`.

### 2. DEMO-0: the ten steps walked backward, and the re-scope

**2.1 What DEMO-0 really delivers per step** (corrected after final review 2; labels of steps 3, 5, 6, 7, 10 changed).

| # | Step | DEMO-0 status and WPs | Honest limit | Where it becomes real |
|---|---|---|---|---|
| 1 | Data wakes the engine | `manual_command`; the E0 package is ingested by a local process (ED0) | no trigger | `scheduled-ingest` at DEMO-2 (E7) |
| 2 | Signals, discards | `real-narrow`: existing Rust local-sim sensor on raw E0 (a derived recurrence metric with post-selection holdout), one admitted family plus recorded discards (ED0) | one family; E0 is a generated sample | 13 families are Codex breadth (DFAM1-3) |
| 3 | Scout and separate verifier | `agent_roleplay` scout and a distinct verifier on the real Core; tool results come from an E0-backed treated lab of k-anonymous aggregates with deterministic recompute (ED0L, TPS) | lab is a local sqlite lab | Rust recompute STP1, broker E5R; DuckDB DUCK |
| 4 | Opportunity, mechanism, alternatives, do_nothing | `agent_roleplay` builder; target chosen from the ReadBase capability catalogue, never from model prose; `unlinked` and `not_evaluable` are valid endings (SMAP) | no quality claims | local model GT05m, hosted real DEMO-2 |
| 5 | Concrete change, versions, diff | generic Python compile of Replace Prompt plus Add EvalSuite over a seeded base world (CMPpy, WRLD0), `compile=claude-standin(python)`; dry-run and writer receipts are real on Core | two kinds only | Rust compile CMP (DEMO-1a); other kinds stream B |
| 6 | Base vs candidate, two gates | arms `real-narrow` on real Core, suite `assets_handwritten`; verdict is a non-planted stand-in with an author-separated judge (GSIpy), structural only: arm outcomes under a role-played model carry no quality information | `quality_claims: forbidden` | GSI in Rust (DEMO-1a); Codex gate is a swap-in |
| 7 | Failure to bounded revision | `not_exercised` unless the honest gate fails (then a rule-driven stand-in) | not claimed | V3r (DEMO-1), V3L (T2) |
| 8 | Human only for authority | `simulated` local issuer; the JWS is really verified by Core | | real approver H1r (ASK-11) |
| 9 | Staging confirmed by alias read | `real-narrow` on local Core | not AWS | DEMO-3 |
| 10 | Observations, memory, successor | observation only: platform-sim emits `release.*` and effects (P2py, `simulated`); memory and successor `not_exercised` | | MEM1 (DEMO-1), durable memory DEMO-2 |

**2.2 Why v4's 76-111 h was wrong and what changed.** Final review 2 found five pieces of the ten-step thread in no demo-path WP. Added: ED0L (E0-backed treated lab and recompute), CMPpy and WRLD0 (generic compile and seeded base world), GSIpy (stand-in verdict replacing the planted judge of `demo/`), INT0 (integration tail: first full run, replay drift, live windows). Re-sized: Q1r 5-7 to 14-22 (the existing driver, translate and analysis are built on the planted dataset), SMAP 8-12 to 12-20, ED0 5-8 to 8-14 (includes the first Windows build of the runner on a separate target dir), M3 6-9 to 7-11, M0RP 8-12 to 10-14, SNET 2-3 to 3-4, TPS 5-7 to 6-9, FRZ0 8-12 to 9-13. Removed from the GT0 ancestors: M5a (Jev is not exercised by the thread). Added by final review 3: G0p (W0 receipt script), TRN0 (W0 integrator), CRV0 (independent review before GT0), G0e (target dirs, moved to W0), CLT0 (configurable client timeout), plus G0f and CONTR as ancestors. Result: 142-219 h, about 1.9x v4's midpoint; the reviewer's own estimate was 120-175 h before the review, trains and timeout WPs of final review 3.

**2.3 Is detection honest?** Yes. `crates/runner` runs `prepare_e0_package_for_local_simulation`, `run_local_simulation` (metric `e0_recurring_copilot_query_cases`, a derived recurrence over `copilot_query` patterns on Arranque cases) and `evaluate_e0_recurrence_holdout` (post-selection replication on the Reproduccion split); `docs/IMPLEMENTATION_STATUS.md` records an actual local E0 smoke on 200 cases (2026-10-02). The old `demo/` is the planted one (its generator plants OTP retry exhaustion; its judge reads `retry_exhausted`, `extra_needed`, `risky`) and is abandoned for detection and judging; ED0's first RED is the rename and permute mutation test (the winning category must change with the label). The E0 finding has no exact route to a Core artifact in the engine today (`unlinked`, `no_exact_supported_flow_mapping`); SMAP therefore validates the builder's target against a capability catalogue in ReadBase, with a permutation test and a negative that must end `unlinked`.

**2.4 The 27 demo-path WPs:** G0f, G0gp, G0e, G0p, TRN0, CONTR, G1, DC0, SNET, M1, M0RP, M3, TPS, RPP, M2a, WRLD0, CLT0, P2py, ED0, ED0L, SMAP, CMPpy, GSIpy, Q1r, INT0, CRV0, GT0. The checker asserts that this set equals the ancestors of GT0 plus GT0, is Claude-only, has no ENV-stream WP and contains no WP that needs an ask.

### 3. Dependency services, the ladder, and the roleplay path

**3.1 Ladder rule.** Rungs, labelled in `doubles[]`: 0 the real service; 1 real path with an `agent_roleplay` backend; 2 digest-keyed recorded replay; 3 fixtures or stand-ins. Start on the highest rung that is available, permitted by the data class and within budget; climb when the real service passes the same black-box test file as the lower rung; never descend silently (a lower rung is a deliberate run-config choice, auto-relabelled); every rung runs the SAME test file.

**3.2 Services (evidence at authoring).**

| Service | State now | Gaps | Start rung and climb | Owner |
|---|---|---|---|---|
| llm-gateway (main 63155b6) | Go; aliases via `LLM_ENDPOINTS` (`api_key_env` mandatory), per-request `profile` (alias, model, temperature, max_tokens, `timeout_s` default 8 max 300, `structured` native or prompted, price), schema subset, no retry, 1 MiB body, per-consumer bearer via `GATEWAY_CONSUMERS`; `/v1/jev` merged (needs `JEV_API_KEY`); `release.yml` exists but 0 tags and 0 releases; never run against a real provider | no per-consumer alias or model allowlist, rate limit, idempotency, cost log; caller owns price; no GHCR digest; building it needs a Go image (not present in the default Podman connection, ASK-4) | rung 1 now (built from SHA, alias `pulso-evolution-llm` pointing at the shim); rung 2 replay; rung 0 local model or hosted capped key (ASK-7, ASK-9); EXT-3 | CL (M1, M0RP, TPS, M2a) |
| agent-core (main c814c2b, 1.3.0) | real Core image drives scout, verifier, builder, writer, arms; 44 live e2e tests; PRs 23, 24, 28 are merged=true into side branches (`ccr-a4781bdb-dnrn7q`, `feat/registry-contratos`, `feat/http-llm-gateway`), NOT main | ambiguous 409 `idempotency_conflict` (N8-02); Core-side doubles; template fallback when gateway env unset; quotas (10 proposals per 24 h, 20 evals per proposal); pin moved 5 times in about 21 h | rung 0 now; per-port double provenance; Jev `blocked(jev)`; EXT-1 | CL (G2, K1-K3, L-BRIDGE) |
| Product platform | Phase 1: cases, turns, assignments, `event_log`; no AI features; platform-contract 1.1.0, exporter and simulator are ours | read mechanism unknown; no Phase 2 dates | rung 3 simulator with a real Core alias read (PX0); read-only real inbound at T3 (P3); EXT-2 | CL (PX0, P1, P2py, P3) |
| Infra and AWS | Terraform declaration-only; nothing ever applied; shared foundations belong to the agent-core infra owner | no account, state backend, SSO, mailbox | plan-only; local Podman stack as staging stand-in; first apply TA4 after GT1B; paths under shared foundations are edited only through TA0 asks | CL (TA0-TA6) |
| Codex engine (main 853b029) | libraries plus one local-sim CLI; 587 tests; `core_task.rs` pinned 0.5.0 digest-only; compiler takes one Flow shape; `durable_jobs.rs` trait without claim-next; migrations 0001-0004; 521 pub types and 59 `compile_fail` references (G0gr re-measures) | no worker, scheduler, control-api, Core client, PG adapters | consumed as merged code (sensors via the existing binary); new Codex work is an optional swap-in only | CX |
| Podman and capacity | `pulso-dev` and `pulso-codex` are distros of ONE WSL2 VM; Codex has no usable Podman | one stack at a time | measure first (ENV0) | CL |
| GitHub Actions | budget exhausted; hosted CI Rust-only and red | no hosted evidence | `verify-local-all` receipt in every PR body (G0p in W0) | CL |

**3.3 The roleplay path: facts and design (rewritten after final review 2).**

Protocol facts, verified in the code: the Core agent node calls `HttpLLMGateway`, which posts `POST <gateway>/v1/generate` (system prompt verbatim, canonical inputs as RFC 8785 JSON, a closed-subset `schema`, and a `profile`); the real gateway then calls the alias endpoint from `LLM_ENDPOINTS`, an OpenAI-compatible `POST /v1/chat/completions`; that endpoint is our shim (dummy `api_key_env`). The agent runs in `prompted` mode with a flat step schema `{kind: tool_call|final, tool, args, output}`: **tool use is the model's JSON in the message content** (`{"kind":"tool_call","tool":"pulso/lab_query@1.0.0","args":{...}}`), executed by Core's tool loop (execute, append observation, call again); it is NOT OpenAI `tool_calls`. The shim returns `choices[0].message.content` as JSON text plus `usage` (flagged `usage_estimated`). The stage policy (`PULSO_LLM_STAGE_POLICY`) pins alias, model, price and max_tokens per stage and rejects a registry profile that differs (`alias_mismatch`, `model_mismatch`, `price_mismatch`): the registry profile `pulso-evolution-structured@1.0.0` has alias `pulso-evolution-llm`, model `external-reasoning-model`, price 1/4, `timeout_s` 60. Design consequence: the registry stays untouched (a profile change moves release digests); the real gateway's `LLM_ENDPOINTS` entry `pulso-evolution-llm` points at the shim; the shim echoes whatever model string is configured. M0RP's acceptance is a JSON step round trip, not a tool_calls round trip.

Timing limits and the design for them:

| Limit | Value | Consequence |
|---|---|---|
| profile `timeout_s` | 60 s (gateway deadline; core HTTP client waits `timeout_s` + 5) | any responder answer slower than 60 s fails the step |
| Core invoke timeout (`AsgiCoreClient`) | 600 s for the whole stage call; after that the receipt is `unknown` and goes to reconcile | a stage of 15 calls at 20-90 s (5-22 min) can exceed it |
| responder latency | 20-90 s per call (one fresh subagent per call) | exceeds 60 s in the tail |

(1) **Async job pattern with a late-answer cache (M0RP):** a request becomes a job keyed by its normalised key; the responder subagent works the job; the shim holds the connection up to 55 s (TCP keep-alive on) and otherwise returns a typed `504 responder_timeout`; the late answer is persisted and serves the retry instantly (the host-level stage retry, or the next attempt of the same normalised key). (2) **Splitting calls (RPP, M3):** each responder call decides one step only (one tool call or one final) with a short output; scout and verifier are capped at 5 steps and the builder at 7 (the asset `max_steps` 16 is unchanged: the responder finalises early), so a stage is at most 5 x 55 s = 4.6 min worst case. (3) **Configurable client timeout (CLT0, 1-2 h in L-BRIDGE):** 1800 s for live DEMO-0 runs; an expired call becomes `unknown` and the host polls reconcile until terminal, a path that already exists. (4) **Fallback:** only if SNET measures more than 20% of responder calls above 55 s, raise the stage profile `timeout_s` to 120-300; that is a profile bump with a release-digest cascade (2-3 h, recorded as an ADR), not the default. SNET measures all of it before M3 relies on it.

Budget (an estimate, measured by SNET and RPP): one live run is about 20-30 model calls (scout up to 5, verifier up to 5, builder up to 7, evaluation arms about 12 depending on the suite; the writer uses deterministic tools) at 20-55 s, i.e. 10-30 minutes of one responder slot; 4-8 live runs per session; everything else replays.

Replay (rung 2): key = (stage, step index, digest of the canonical inputs with volatile fields normalised: `run_id`, `turn_id`, `session_id`, `labels`, and binding, job and artifact ids replaced by ordinals). Acceptance of M0RP and M3: the same stage replayed 3 times from a fresh Core DB gives 0 misses; a drift test fails with the digest diff instead of going live silently; a prompt revision costs a re-record (2-4 lane-hours). Synthetic and treated corpora are committable; anything derived from raw E0 stays in a git-ignored local directory with a digest manifest.

Treated-payload scanner (TPS): deny-by-default allow-list over the FIXED input dict that `LLMAgentPort.step` builds (keys `goal`, `step`, `tools` catalogue, `output_schema`, `observations`); any other key is rejected. Observations from `lab_query` follow an explicit treated-aggregate spec, because the plan's own data-class table forbids derived extracts for third parties: only `metric_id` and `window_id` (enums), `count` (integer, suppressed to `<k` below k, default k = 10), `rate` (rounded to 2 decimals), group keys as salted truncated HMAC hashes, `evidence_ref` (opaque id pattern); every other string field is rejected. First RED: a lab row with a free-text field is rejected; a k-anonymous aggregate passes. ED0L produces only those aggregates. The responder protocol (RPP): a lane of fresh-context subagents, one per call, each reads only its queue file and writes only its response file; scout, verifier and builder use distinct responders; none is the implementer or reviewer of the code under test; faults (timeout after send, 502 `invalid_output`) come from a scripted side channel, never from a subagent.

Jev: the shim also serves `/v1/jev` to test pass-through and the Python and Rust `JevDecisionPort` (M5a, M5b, in W1 and W4, off the demo path); Core-side Jev is `blocked(jev)` until PR 28 is on main, so DEMO-0 uses `llm_structured` stages and says `jev=not_exercised`. Rung-up schedule: recorded replay for CI (DEMO-0, M3); local GPU model (ENV9, SMOKE, GT05m); hosted real on synthetic data (M4, ASK-9); hosted real on treated E0 payloads (ASK-8, DEMO-2); each swaps the backend only, same test file.

### 4. Strangler order and retirement of the Python host

| Stage | Host | What moves | Feasibility |
|---|---|---|---|
| S1 (DEMO-0) | Python host (`e2e-core/codex_standin`, core-bridge stages) | the model path becomes real (gateway plus roleplay); E0 detection runs through the existing Rust sensor | no cargo seam, no Codex; the one cargo action is building the existing runner binary |
| S2 (DEMO-1a) | Python host calls `pulso-engine step` | semantics as JSON-in/JSON-out Rust steps in `seams/crates/steps`, over the frozen schemas (no sealed Codex type is touched) | sensors wrap the existing binary; recompute, validation, compile and gate are Claude stand-ins |
| S3a (DEMO-1) | Rust shell, jobs in memory | executor, control-api lite, authority state machine stand-in, thin memory | resume-after-kill from CAS-stored inputs |
| S3b (DEMO-2) | Rust worker on PG | durability | PGJ, worker, triggers |

Python host freeze rule: after GT0 it gets glue only (E3b); new semantics enter as Rust steps behind `contracts/engine-steps/`. RG-1 (GT05): every step the ratchet marks `real-narrow` is served by a Rust step. RG-2 and RG-3 (GT1A): the ratchet is green on the Rust shell and for 3 recorded runs both hosts give the same ordered command sequence and `candidate_hash`; all negatives pass including resume-after-kill. RG-4 (GT1B): `demo/run.ps1` defaults to the Rust host; the Python host moves to `e2e-core/legacy_host`, deleted by Q2. RG-5 (GT3): a Claude stand-in is retired only if its swap-in passed the conformance test (SWA, SWP, SWC, SWB, SWL). If TW-1 or TW-2 trips, the Python host stays the carrier with Rust steps, labelled, and the plan is re-based, not abandoned. The object store is always called "blob store" (BLOB1) to avoid the S3 stage-name collision.

### 5. Independence design, dependency graph, critical paths

Rules, enforced by the checker:
1. No Claude WP has a hard dependency on a Codex WP (printed count 0). Gates are computed over Claude-only edges; no gate has a Codex or swap-in ancestor.
2. Codex WPs depend only on the FROZEN artifacts (`FROZEN:` line of annex D): 30 edges, none to a non-frozen Claude WP (0). FRZ0 publishes the digest-pinned pack Codex verifies against: C-7 v1.1 claim-next signature, C-8 ChangeSpec and ScenarioCase schemas, C-9 transcript seed, C-10 gate result shape, a builder-output corpus v0 (10 synthetic outputs), arm-report goldens, bridge dry-run and writer goldens with digests, and PG claim traces recorded from existing tests. No Codex lane needs Podman, live PG or a live Core; no acceptance cell of a Codex WP names a Claude WP (DMAPV now validates the 10 FRZ0 corpus outputs, not SMAP's; DPL1 no longer says "consumed by E4R"; CT1 says "reviewed by a distinct actor").
3. Swap-ins are `~` edges from a Claude WP to a Codex WP (40): SWA (compile, gate, recompute, validation), SWP (pipeline, authority), SWC (conformance on PG), SWB (kind modules and goldens), SWL (replay, oracle, detectors, memory, original families), plus RVC1-3 reviews. They depend on a Claude gate, gate nothing, are never critical, each carries a conformance test, and a stand-in is retired only through GT3 (RG-5).
4. Hand-offs are versioned artifacts (digest-pinned packs, train tags) plus the journal.

Hard-edge graph of the Claude path (computed). GT0: DC0 > ED0 > SMAP > Q1r > INT0 > GT0 (depth 65.5 h; M0RP, TPS, WRLD0, G1, M3, CMPpy, GSIpy and the review and train WPs feed it in parallel). GT05: depth 67.0 h. GT1A: G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A (117.0 h). GT1B: the same plus GT1B (118.5 h). `K0 > K1 > K2 > K3` is the integration spine (the ENV0 chain to K3 is 62.0 h because K0 needs ENV2 and ENV4); K3 does not wait on any compiler (K3fx fixture). Critical path to GT1B (float at most 4 h, midpoint hours): 20 WPs, 145.5 h, all Claude.

| Gate | Ancestors (all Claude or frozen) | Hours incl. gate | Serial depth | Asks required |
|---|---|---|---|---|
| GT0 | 26 | 142-219 | 65.5 h | none |
| GT05 | 40 | 203-310 | 67.0 h | none |
| GT05m | 44 | 213-330 | 68.5 h | ASK-7 |
| GT1A | 67 | 390-582 | 117.0 h | none |
| GT1B | 78 | 460-688 | 118.5 h | none |
| GTA | 88 | 542-825 | 157.0 h | ASK-17..21 |
| GT2 | 95 | 609-904 | 142.0 h | none |
| GT3 | 95 | 580-863 | 161.5 h | none |

Hidden gates (cause most slips): (1) the S-MAP outcome (finding to valid artifact), first read in DEMO-0 with `unlinked` and `not_evaluable` as valid endings; (2) real-model behaviour on stage schemas, measured at GT05m, so every label before it is `agent_roleplay`; (3) the compile writer path is a Core stage with a sealed `RegistryMutationCommitment`, not HTTP routes (K3); (4) cargo slot, Podman and RAM (ENV0); (5) pin churn (G2); (6) responder latency against the 60 s and 600 s limits (SNET).

### 6. Environment and capacity (measured first, improved second)

Facts re-measured 2026-10-03/04 (read-only): host RAM 16 GB total, free 5.7 GB at the last sample (1.7 GB at an earlier one; ENV8 therefore records min and median over a working day, not one sample); `.wslconfig` `memory=10GB`, `processors=8`, `swap=8GB` (D:\WSL\wsl-swap.vhdx), mirrored networking; the VM shows 9948 MB; disk C: 112 GB free, D: 1.2 TB free (cargo target dirs must live on D:, G0e); no sccache, mold, lld, nextest or ollama on the host; no cargo or compiler in the VM; `rust-lld` ships with the toolchain; RTX 3060 12 GB; both Podman machines are distros of one WSL2 VM (a third distro, `Standar-Dev`, is stopped); 58 registered git worktrees; the full 33-minute gate is Codex's Windows root script (fmt, clippy, test `--workspace`, 45 integration test binaries in `crates/core`, bundled sqlite); Codex cannot reach Podman. No speedup number below is sourced: each is "to measure" in ENV0 and kept only if it shows at least 1.3x or 5 minutes saved. The Go builder image for the gateway is not in the default Podman connection (ASK-4).

| Level (assumptions) | Content | Needs | Capacity, lane-hours per session |
|---|---|---|---|
| LVL-A current | Claude: orchestrator + 3 implementers + 1 reviewer (a live responder displaces an implementer); one cargo slot; one stack; replay-mode gate. Codex: 3 implementers + 1 integrator, offline, Windows host only | no approval (Codex needs ASK-2) | Claude 14-18; Codex 12-16 (a ceiling: 0 under silence) |
| LVL-B software-only, decided by ENV0 | host lld and debug profile (ENV2), vendored deps (ENV4), separate target dirs (G0e), fast and full gate tiers (ENV6); conditional: Linux build container in the existing VM with sccache and nextest (ENV1, ENV3, ENV5), pytest sharding (ENV7), local model runtime (ENV9) | ENV1 needs the ADR written by ENVADR citing ENV0 measured incompatibilities (AGENTS.md says no development in WSL without documented incompatibilities and a decision) plus ASK-5 and ASK-6 | 18-24 |
| LVL-C hardware or runners | ENV11 lane scheduler, ENV12 build farm | ASK-14: HW-1 host RAM to 32-48 GB with `.wslconfig` memory 24 GB, about USD 80-200; HW-2 a second Linux box with 64 GB, about USD 800-1500 used; HW-3 an on-demand 16 vCPU 64 GB cloud or self-hosted Actions runner, about USD 0.5-1.0 per hour, USD 100-250 per month (indicative list prices, not quotes). Decision rule: if ENV0 shows RAM as the bottleneck ask HW-1 first (cheapest) | 35-45 |

Default (silence): ENV0, ENV2, ENV4, ENV6, ENV8, G0e only on the existing machines; ENV8 writes recommended `.wslconfig` values as an ask; no machine is stopped, created or resized. The demo path contains no ENV-stream WP; environment WPs run behind DEMO-0 unless ENV0 shows they shorten it. Velocity is re-baselined at GT0 (first measured throughput after about 12 sessions) and again at TW-1, so the level used for planning (ASK-14) follows data.

Codex capacity rules: one heavy build slot per account; both accounts may hold a slot at once only when free host RAM is at least 6 GB (ENV8 lock), otherwise they alternate; the pace assumed is 4-5 tests per agent-hour (journal CX-0178..0184). At that pace 364-557 Codex hours add about 1,600-2,500 tests to the 587 that exist; if the 33-minute gate scales linearly (an assumption) it reaches roughly 100-170 minutes by W4, so Codex runs a fast tier per lane (`cargo test -p improvement-engine-core --test <file>`) and the full root gate once per train (the TRX rule).

`seams/` consequences: a nested `[workspace]` works (tested: root `cargo metadata` and `seams/` both succeed, no `exclude`, the root `rust-toolchain.toml` 1.98.1 is inherited); hosted CI and Codex's root gate do not see `seams/`, which has its own `Cargo.lock`, so the `seams` leg of `verify-local-all` (`cargo fmt/clippy/test --manifest-path seams/Cargo.toml --locked`, asserted by Pester), the receipt in every PR body, and a hosted workflow added by the CI integrator when Actions return (ASK-22) are the mitigation. No `seams` crate depends on `crates/core` (K0 dependency-graph test), so `seams/` never recompiles it; its vendored closure is only the new packages (`ureq` without TLS, `tiny_http`, `ed25519-dalek`, UUIDv7, JCS; about 25-35); adopting Codex code happens in a separate crate `seams/crates/swap` behind a cargo feature, created only at swap-in time.

### 7. Partition for maximum parallelism

Scope is not reduced; it is partitioned. 229 WPs sit in 29 lanes (17 Claude, 12 Codex). Each lane owns disjoint paths and builds against frozen contracts, recorded packs and fakes; Claude lanes never wait on Codex lanes and the reverse.

**7.1 Total path map.** Annex D holds the machine-readable `owners` block (the most specific glob wins; a tie fails), the numbered ranges and the planned-new-paths block. Checker result: 1860 paths (1683 tracked paths of improvement-engine main 853b029 plus 177 paths of infra `origin/main`, prefixed `infra:`) map to exactly one lane, 0 unowned, 0 tied; 59 planned new paths resolve to the intended lane; every WP's `paths` column resolves inside the WP's own lane (229 WPs carry explicit globs). Rules that close the review gaps: (a) migration ranges: Codex X-LEARN 0005-0014, X-SRC 0015-0024, X-GATE 0025-0029, X-FACADE 0030-0039, X-CONF 0040-0042, X-ARTIF 0043-0044, X-SENS 0045-0046, X-SCEN 0047-0049; Claude L-PG 0050-0069, L-PLAT 0070-0074, L-MEM 0075-0079, L-AUTH 0080-0084, L-CAPI 0085-0089, L-EVAL 0090-0094; reserve 0095-0099 owned by L-GOV; (b) ADR blocks (current maximum 0005): Claude blocks of 10 from 0100 in alphabetical lane order, Codex blocks of 8 from 0300; journal files `docs/journal/NNNN-<lane>-<slug>.md` (last existing 0067; L-GOV 0068-0099; Claude blocks of 16 from 0100; Codex from 0400); each block is a glob in the owners block, so a new ADR or journal file never lands in another lane's glob; (c) `local/compose.d/l-<lane>.yaml` per lane, `local/compose.d/**` L-ENV; (d) new Pester tests `tests/verify-local-*.Tests.ps1` L-ENV; (e) paths marked "to create": `crates/core/src/artifact_kind_*.rs` and its tests, `crates/core/src/{policy_oracle,pipeline,authority}.rs`, `crates/core/src/replay_*.rs`, `scenario_*.rs`, `facade_*.rs`, `detectors/`, `tests/conformance/`, `contracts/{pipeline,artifact-kinds,product,engine-*,control-api}`, `roleplay-llm/`, `local/{pg,observability,compose.d}`, `seams/**`, `docs/{reviews,spec-amendments,reports,runbooks,security,lanes}`, `agent-core-assets/{corpus,eval-suites}`, `scripts/{env,gov,dc}` and the only to-create test file `crates/core/tests/policy_oracle.rs`; (f) the infra rule `infra:**` is L-INFRA, but paths under shared foundations (owned by the agent-core infra owner) are edited only through TA0 asks.

**7.2 Single integrators and cross-lane resolutions.** `crates/core/Cargo.toml`, `lib.rs`, the root `Cargo.toml` and `Cargo.lock`, `.github/**` and the Codex gate scripts have ONE integrator, X-FACADE: XSTUB adds empty `mod` stubs and `[[test]]` entries for every planned module in one bootstrap commit (the stub files belong to their lanes afterwards), so other Codex lanes own only their files. `seams/Cargo.toml` and `seams/Cargo.lock` have one integrator, L-CLIENT: K0 creates only those two files and the core-client crate (workspace `members = ["crates/*"]`); every other lane creates its own crate directory with its first commit; a new dependency is a `[DEP-ASK]`. Resolutions of the four crossing WPs: E3b (Python host glue) moved to L-E2E (`e2e-core/**`); Q3c split into Q3ca (control-api, L-CAPI) and Q3cc (core-client, L-CLIENT); K0 as above; WDX edits only `lib.rs` re-exports and its own new `facade_*.rs` files, and a `pub(crate)` to `pub` change in another lane's file is a `[DEP-ASK]` to that lane. Claude gate wrappers are new files (`scripts/verify-local-all.ps1`, `verify-local-fast.ps1`, L-ENV) that call the Codex script unchanged as a leg. L-BRIDGE owns `core-bridge/**` (except `llm/`, `stages/` and their tests, L-MODEL), `bridge-contract/**`, `agent-core-assets/**` (except worlds, corpus, eval-suites), `local/core/**` (except `gateway/`), `scripts/core/**`; K2 and K3 request route or mock changes through BRG1. K2 touches no `crates/core` file (its own 1.3.0 DTOs); the `core_task.rs` 0.5.0 to 1.3.0 change is CT1, executed by Codex under a `[CONTRACT-CHANGE]` stanza; nothing on the Claude path waits for it. Consent clause (ASK-16, optional): only if you want Claude to edit named Codex-owned files while Codex is frozen; default none.

| Lane | Team | WPs | Hours | Review class |
|---|---|---|---|---|
| L-AUTH | CL | 6 | 38-56 | RC1 |
| L-BREADTH | CL | 7 | 50-72 | RC1 |
| L-BRIDGE | CL | 6 | 25-39 | RC2 |
| L-CAPI | CL | 6 | 46-64 | RC1 (auth, replay), RC2 rest |
| L-CLIENT | CL | 11 | 72-103 | RC1 |
| L-CONSOLE | CL | 2 | 24-36 | RC3 |
| L-E2E | CL | 15 | 126-193 | RC2 |
| L-ENGINE | CL | 12 | 93-140 | RC2 (authority and gate stand-ins RC1) |
| L-ENV | CL | 16 | 46-75 | RC3 |
| L-EVAL | CL | 8 | 58-85 | RC2 |
| L-GOV | CL | 39 | 144-220 | RC3 |
| L-INFRA | CL | 8 | 74-125 | RC2 (apply is human-approved) |
| L-MEM | CL | 3 | 24-36 | RC2 |
| L-MODEL | CL | 13 | 72-107 | RC1 (ledger, scanner), RC2 rest |
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

**7.3 Contracts: the 13, reconciled with the code** (digest-pinned, append-only, the same black-box test file against double and real).

| # | Contract | State at 853b029 | Published by | Frozen at |
|---|---|---|---|---|
| C-1 | Core wire: `bridge-contract/` OpenAPI (11 operations), schemas, conformance, examples | exists | L-BRIDGE | now |
| C-2 | run report schema, `doubles[]`, honesty tests | to create (G1) | L-GOV | GT0 |
| C-3 | step JSON in/out (`contracts/engine-steps/`) | to create (CONTR); only 171 types derive serde, so steps use DTOs | L-GOV | CF1 (after GT05) |
| C-4 | job handler ABI crate `seams/crates/abi` | to create (E1) | L-ENGINE | CF1 (after E1 and TW-1) |
| C-5 | `CoreClient` trait and `FakeCore` from C-1 goldens | to create (K2) | L-CLIENT | CF1 |
| C-6 | `contracts/control-api/openapi.yaml`; today's double is `e2e-core/src/codex_standin/*.py` | to create (E5L) | L-CAPI | CF1 (after E5L) |
| C-7 | `DurableJobRepository` (`durable_jobs.rs:111`). Version v1 = the existing trait, frozen at CF0. Version v1.1 adds the claim-next signature, published in FRZ0 and frozen with the FRZ0 digest; DJC only implements it. Any later change is a new versioned file plus `[CONTRACT-CHANGE]` | trait exists, claim-next to add (DJC) | FRZ0, X-CONF | CF0 (v1), FRZ0 (v1.1) |
| C-8 | `ChangeSpec` and `ScenarioCase` schemas (no such Rust types exist) | new schemas (SMAP drafts, FRZ0 publishes) | L-GOV | CF1 |
| C-9 | pipeline transcripts rev1 | seed in FRZ0 | L-GOV, X-FACADE | CF1 |
| C-10 | gate result shape | shape in FRZ0; Codex fills semantics | L-GOV | CF1 |
| C-11 | `platform-contract/` 1.1.0 event catalogue plus `release.*` | exists, `release.*` added by PX0 | L-PLAT | now |
| C-12 | roleplay queue protocol, scanner allow-list, ledger schema | to create (M0RP, TPS, RPP) | L-MODEL | GT0 |
| C-13 | allocation tables (migrations, ADR, journal, OWNERS) | annex D | L-GOV | CF0 |

CF0 freezes C-13 and C-7 v1 and publishes digests of the drafts; C-2 and C-12 are frozen at GT0 because their WPs (G1, M0RP, TPS, RPP) finish there; CF1 freezes C-3, C-4, C-5, C-6, C-8, C-9, C-10 at the first gate that exercises them (its deps include E1 and E5L so nothing freezes before it exists). Draft contracts are `provisional` and consumers start against the published digest. Narrow waists: C-1, C-4, C-3, C-6, C-5, C-2, C-7.

**7.4 Conflict matrix.**

| Shared item | Rule |
|---|---|
| `local/compose.yaml`, `scripts/dev.ps1` | only L-ENV; per-lane fragments `local/compose.d/l-<lane>.yaml` owned by that lane, pulled in with `include`; `tests/test_local_compose_contract.py` stays green |
| Gate and CI scripts | Claude wrappers L-ENV; Codex gate X-FACADE |
| Docs indexes | generated at train time by the integrator from `docs/lanes/<lane>/**` |
| Spec | additive amendments by the owning team, mirrored once per train; precedent file `V3_SUCCESSOR_AMENDMENTS_CLAUDE.md` |
| `OWNERS.md` | generated; a test fails on unowned or doubly-owned paths, including the planned new paths |
| Integration branches | `train/<wave>-<team>` built by the team integrator from `lane/<lane>/<wave>` |
| Vendor dir `D:\.codex\factored\vendor` | read-only (ENV4); Codex read access is ASK-13 |
| Shared journal | one consolidated entry per team about every 15 minutes (ids CL-, CX-); lanes write only their repo journal files |

**7.5 Waves and parallel width.** W0 DEMO-0 sprint plus the enabling pack and W0 hygiene (G0e, G0p, WTR1, WTR2); W1 DEMO-1a plus Codex breadth; W2 DEMO-1; W3 DEMO-2; W4 hardening and breadth; W5 T3, AWS, T5.

| Wave | Hours (Claude share low / high; WPs; lanes) | Claude PRs | Codex PRs | Max open PRs (Claude / Codex) |
|---|---|---|---|---|
| W0 | 167-256 (98.2% / 98.0%; 34 WPs; 8 lanes: 6 CL + 2 CX) | 7 | 1 | 12 / 3 |
| W1 | 174-268 (58.6% / 59.0%; 44 WPs; 17 lanes: 9 CL + 8 CX) | 5 | 4 | 12 / 3 |
| W2 | 310-457 (71.0% / 70.7%; 51 WPs; 21 lanes: 12 CL + 9 CX) | 10 | 4 | 12 / 3 |
| W3 | 172-264 (38.4% / 37.9%; 24 WPs; 12 lanes: 4 CL + 8 CX) | 3 | 5 | 12 / 3 |
| W4 | 326-488 (73.3% / 72.5%; 45 WPs; 22 lanes: 15 CL + 7 CX) | 10 | 4 | 12 / 3 |
| W5 | 270-424 (97.8% / 97.6%; 31 WPs; 14 lanes: 13 CL + 1 CX) | 12 | 1 | 12 / 3 |

Width = lanes with WPs in the wave; the checker also prints the widest dependency level (33 WPs over 19 levels). Live concurrency is bounded by implementers (3 per team at LVL-A) and by the one cargo slot, so lanes beyond that queue in critical-chain order; the plan is parallel in structure and about 3-4 wide in execution at LVL-A. Serial spine inside each wave: W0 DC0 > ED0 > SMAP > Q1r > INT0; W1 CMP > E3b; W2 K1 > K2 > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1; W3 PGJ > E6w > E7; W5 TA4 > TA6.

### 8. Merge policy, PRs, worktrees, reviews, tripwires (one rule block)

1. **Trains.** One consolidated PR per 25-35 lane-hours per team (not per feature, not per wave): PRs per wave W0..W5 are Claude 7 5 10 3 10 12 (47 in all) and Codex 1 4 4 5 4 1 (19), computed as ceil(team midpoint hours of the wave / 30). Lane branches `lane/<lane>/<wave>` merge into `train/<wave>-<team>` in dependency order; fast gate after each merge, full gate once per train. Each PR body carries the gate receipt and `doubles[]`: the W0 receipt of G0p (verify-local-ci, pytest of touched Python packages, replay-mode ratchet) in W0, `verify-local-all` (G0d) from W1.
2. **PR cap.** At most 3 independent stacks open per team. A stack is a chain of PRs each based on the previous PR's head; Claude stacks go up to depth 4 (so at most 12 open Claude PRs); Codex works at depth 1: every Codex train is based on the last user-confirmed main SHA and never stacks on its own unmerged PR (GitHub is unreachable from Codex's environment; it publishes only through its connector), so at most 3 open Codex PRs.
3. **At the cap.** A team neither idles nor exceeds the cap: it keeps working on unpublished stacked branches (Claude) or writes a `git bundle` to `D:\.codex\factored\exchange\` with a `[HANDOFF]` journal entry (Codex, and Claude beyond depth 4) and publishes the next PR when a base merges. Restack: when a base changes, the integrator rebases the stacked train in the same session, re-runs the fast gate and the tests of touched files, the owning lane resolves conflicts, nobody rewrites another lane's branch; Codex restacks only from a bundle based on the last confirmed main.
4. **Merge delegation is ASK-3** (third ask). Default: you merge each train. Cost under the default: 47 + 19 merges over the whole plan; DEMO-0 alone needs the W0 trains (7 Claude PRs).
5. **Worktrees.** Hard ceiling of 40 registered worktrees across both teams at any time (58 registered today; WTR1 runs first in session 1 and its inventory script fails above 40); live implementer worktrees = implementers (3 Claude plus 1 integrator; 3 Codex plus 1 integrator), never lanes; a lane holds a worktree only while one of its WPs is in progress and is torn down at train merge; reviewers and the responder hold none. There are 94 lane-wave branches in all, at most 8 checked out at a time. WTR2 (Codex-side inventory) runs in W0; under silence on ASK-2 it only lists. W2, W4 and W5 have 21, 22 and 14 lanes, but three implementers cannot drive them at once: width above that is a queue, not parallelism.
6. **Independent adversarial reviews, 1-3 loops by class.** RC1 (3 loops: correctness against RED and goldens; adversarial: forgery, replay, egress, fencing, budget; verification of fixes plus mutation tests), RC2 (2 loops: semantics; edge cases and negatives), RC3 (1 loop at train level against a checklist). Loops 2 and 3 are WPs, hours inside the totals: CRV0 (before GT0: TPS, DC0, G1, M2a, M0RP and the E0 data path RC1, the rest RC2; gates GT0), CRV1 (S1 retro-review and S2; gates GT05), CRV2 (SEAM-1: JWT, idempotency, hash, egress; gates GT1A), CRV3 (PG, worker, fencing; gates GT1B), CRV4 (T2; gates GT2), CRV5 (W5 live breadth and transport; gates GT3), CRV6 (AWS slice; gates GTA). Reviewers are distinct fresh-context Claude actors. REV1-5 (Codex) are opportunistic second reviewers and gate nothing; RVC1-3 (Claude reviewing Codex) are optional. The L-GOV overhead is the real tax: 39 WPs, 144-220 h (train, review, tripwire, fact WPs).
7. **Subagents inside a lane.** One implementer per active lane (strict TDD, the WP's first RED); test authors and reviewers are pooled and hold no worktree; work needing no cargo slot (schemas, goldens, fakes, Python, SQL design, runbooks, Terraform plans, TypeScript, docs) runs in parallel with Rust lanes.
8. **Tripwires** (objective; none waits on the user): TW-0 (evidence WP TW0) seams build offline in the Claude account and CF0 published, Codex part only with ASK-2; TW-1 (TW1) K2 live on the real image (same `Idempotency-Key` twice gives one run, scout receipt with tokens and cost), red means stop Rust server work and reduce Track R to steps and conformance; TW-2 (TW2) E5L suite green on the Rust server with a roleplay scout, red means stay on the Python host with Rust steps and re-base; TW-3 (TW3) at least 6 of 10 ratchet steps hosted by the Rust shell, red means re-plan RG gates with you informed.

### 9. Coordination protocol between the teams

1. Hand-offs happen only through versioned artifacts (digest-pinned packs, contract files, train tags) and the journal; no team blocks on the other's branches. Codex depends on Claude's frozen artifacts; Claude depends on no Codex WP (optional swap-ins only).
2. Journal tags `[CONTRACT-PUBLISHED]`, `[CONTRACT-CHANGE]`, `[ASK]`, `[DEP-ASK]`, `[BLOCKED]`, `[DONE]`, `[HANDOFF]`, `[FINDING]`, at most 8 lines each, first line UTC timestamp and team; `[DONE]` carries target, sha, `doubles[]`, agent-hours, tests added, gate minutes (telemetry for recalibration). One 10-row state table at the start of each session. An `[ASK]` carries a default only where the default is safe; silence is never approval.
3. Codex lanes run offline against the FRZ0 pack, goldens and fixtures; no Podman, live PG or live Core. Claude never runs Codex tests for it on the Claude path; PG runs of Codex suites are the optional SWC.
4. Codex onboarding brief at unfreeze (G0f, one page): current main, the G0gr export list, `seams/` is Claude's, lane map, ranges, vendor dir, the data-class rule for developer agents, depth-1 PR rule, bundle rule.
5. Blocked behaviour: nobody idles; a blocked lane records `[BLOCKED]`, takes the documented default and moves on. Humans of agent-core and Product are never contacted directly; you relay one consolidated message (the journal reaches only Codex).
6. Nexus: checkpoint receipts go through `nexus checkpoint --stdin` in the workspace outbox with an allowlisted project id and a stable idempotency key; nobody writes the vault; no WP reads or writes `D:\Nexus`.

### 10. Methodology compliance (every standing rule)

| Rule | How honoured |
|---|---|
| Strict TDD | every WP names a first RED in the table; spikes (SNET, E9s) are rewritten test-first; ASK-15 default is the full ritual |
| Independent adversarial reviews, 1-3 loops | classes RC1-RC3 per lane (7.2 table, section 8.6); CRV0-CRV6 are WPs inside the totals |
| Consolidated worktrees and PRs | section 8: PR per 25-35 lane-hours, 3-stack cap with an at-the-cap rule, 40-worktree ceiling, WTR1 and WTR2 in W0 |
| Local CI before PR | G0p receipt in W0, `verify-local-all` (G0d) from W1, in every PR body |
| Real dependencies via Podman, machine per team | Claude's `pulso-dev` stack; Codex has none usable, so its lanes are offline by design |
| Never depend on a merge | Claude trains stack on the PR head; Codex trains are depth 1 from the last confirmed main plus bundles; independence rule |
| Parallelize with subagents | 7.5, 8.7; the roleplay responder lane (3.3) |
| Two teams coordinate only through the shared journal | section 9 |
| Each team owns its part | annex D path map; consent clause ASK-16 for crossings |
| Spec is the source of truth; additive amendments by the owning team | amendments per team (7.4); the stand-in labels and PX0 are amendments |
| Humans of other teams unreachable | EXT-1..3 relays as paste-ready messages (section 14) |
| Infra: one company, shared foundations, defer to the agent-core infra owner, never duplicate | TA0 asks first; TA5 reuses agent-core's Dockerfile and runbook where they fit; shared-foundation paths only via asks |
| Stay in scope (consume agent-core and llm-gateway, do not build their internals) | the shim is a test double behind their HTTP contract; no Core or gateway edits |
| debug-console is OUR backoffice, not the product UI | CON1, CON2 |
| Docs in English; never touch D:\Nexus | all |
| Do not stop on failures | `[BLOCKED]` plus default plus next WP; red tripwires re-base |
| AGENTS.md (Windows first, no development in WSL without documented incompatibilities and a decision) | ENVADR cites ENV0 measurements; ENV1 depends on ENVADR and needs ASK-5; root gate stays Windows |

### 11. What the spec does not specify, and where it goes

| Topic | Decision | WP | Tier |
|---|---|---|---|
| Machine and build environment | measure first, three levels | ENV0-ENV12, G0e, WTR1, WTR2 | T0-T2 |
| Deployment pipeline | local release script by digest, SBOM, audit, human apply of a saved plan | TA1 | TA |
| Runtime ops, incidents | eight runbooks, single operator today | O1a | T2 |
| Secrets lifecycle, retention, redaction canaries | uncommitted env files locally, loaded by a human on AWS | O1a, TA4 | T2/TA |
| Cost and budget governance | one owner, the Python ledger; ceilings, breaker, kill switch, reconciliation | M2a, M2f, TA6 | T0/T2 |
| Tenant model | single tenant per environment, RLS-ready, cross-tenant tests | Q2 | T2 |
| Product Phase 2 availability | capability profile, superset tests; outbound `blocked(product-phase-2)` | PX0, DPL2, P4 | T0.5-T3 |
| llm-gateway policy gaps | enforced in our runtime; EXT-3 | M2a, TPS | T0 |
| Observability, liveness | traceparent, metrics, alarm firing and resolved, stall metric | Q3, Q3ca, Q3cc, E7 | T1b/T2 |
| Data retention, E0 replacement | data classes, tombstone erasure | O1a, DC0 | T0/T2 |
| Rollout and rollback of published proposals | `ProposalRollout`, human-gated revoke | H2 | T2 |
| Human approval UX and notification | decision card (CLI) then console panel; notification adapter with SLA | H1, H1r, H1n, CON1 | T1a-T2 |
| Blob store (spec says PG plus S3) | PG-CAS first, S3-compatible adapter, AWS S3 at TA4 | E1, BLOB1 | T1a/T2 |
| CAPs 11-12 JCS parity; 13-15, 17-22 compile breadth; 23 release_settings denied; 48 bootstrap CLI; 56 forced limits; 64 known_gaps | each has a WP | K4, BK0-BKCL, BOOT, QKG, Q3ca | T0-T2 |
| U05 PG window, U10 Rust model transport, U26 and U36 sandbox, U28 lab session, U32 panels, U34 run control and fork | each has a WP | PGQ, M6, SB1, SB2, SBL, LAB28, CON2, RUN1-RUN3 | T1b-T3 |
| Spec-22 fixture families, PL-02..04 and PL-06..10, PL-C6 | Codex offline fixtures; Claude's E4R has its own tests | FX22a, FX22b, FX22p, DPL1, DPL2, DDOC1 | T1a |
| Prequential replay and oracle (28.3-28.5) | Claude stand-ins, Codex protocol as swap-in | RPL1, ORC1, DREPLAY, DORACLE | T2 |
| Hosted CI | `verify-local-all` receipts are merge evidence | G0p, G0d | T0-T0.5 |
| Spend of AWS | low hundreds of USD per month for staging, computed in TA3 (estimate) | TA3 | TA |

### 12. Estimates, minimum cut and sessions

Hours: 1419-2157 raw (midpoint 1788, about 1967 with a 10% churn allowance for pin bumps, environment tails and re-records; review loops are explicit WPs). Through T1b: 750-1134 (midpoint 942). By tier (by wave: section 7.5):

| Tier | Total hours (Codex) | Claude share of the lows |
|---|---|---|
| T0 | 167-256 (CX 3-5) | 98.2% |
| T0.5 | 156-241 (CX 56-86) | 64.1% |
| T1a | 277-406 (CX 62-91) | 77.6% |
| T1b | 150-231 (CX 79-123) | 47.3% |
| T2 | 302-450 (CX 81-124) | 73.2% |
| T3 | 207-318 (CX 83-128) | 59.9% |
| TA | 80-135 (CX 0-0) | 100.0% |
| T5 | 80-120 (CX 0-0) | 100.0% |

Waves W1 and W3 are Codex-heavy by design (Codex runs its offline breadth lanes while Claude integrates); W5 is Claude-heavy because AWS and soak are Claude's. Why Claude's share is not lower: stand-ins for Codex semantics and the live per-kind WPs are Claude WPs (57-85 + 60-87 = 117-172 h), the price of the independence rule; Codex lanes grow in breadth (families, scenario kernels, memory breadth, per-kind goldens, conformance, spec text), not in criticality. Claude is the bottleneck: the Claude share is a consequence of the rule, not of Codex's capacity, and the cheapest lever (Codex building the stand-ins) is the one the rule forbids.

Sessions per gate (a session is about 8 wall hours; capacities are assumptions, so this is a model, not data). Rule: sessions = max(capacity bound, serial floor); capacity bound = 1.10 x ancestor midpoint hours / capacity midpoint (LVL-A 16, LVL-B 21, LVL-C 40 lane-hours per session; the range uses the ends 18 and 14, 24 and 18, 45 and 35); floor = 1.10 x serial depth / 7.5 h. The table is printed by the checker.

| Gate (demo) | Serial depth | LVL-A 14-18: central (range) | LVL-B 18-24 | LVL-C 35-45 (floor binds) |
|---|---|---|---|---|
| GT0 (DEMO-0), demo path only | 65.5 h | 12.4 (11.0-14.2) | 9.6 (9.6-11.0) | 9.6 (9.6-9.6) |
| GT0 plus the Codex enabling pack on the same agents | 65.5 h | 14.1 (12.5-16.1) | 10.7 (9.6-12.5) | 9.6 (9.6-9.6) |
| GT05 (DEMO-1a) | 67.0 h | 17.6 (15.7-20.2) | 13.4 (11.8-15.7) | 9.8 (9.8-9.8) |
| GT05m (local-model rung, needs ASK-7) | 68.5 h | 18.7 (16.6-21.3) | 14.2 (12.4-16.6) | 10.0 (10.0-10.0) |
| GT1A (DEMO-1) | 117.0 h | 33.4 (29.7-38.2) | 25.5 (22.3-29.7) | 17.2 (17.2-17.2) |
| GT1B (DEMO-2) | 118.5 h | 39.5 (35.1-45.1) | 30.1 (26.3-35.1) | 17.4 (17.4-18.0) |
| GTA (DEMO-3, needs AWS asks) | 157.0 h | 47.0 (41.8-53.7) | 35.8 (31.3-41.8) | 23.0 (23.0-23.0) |
| GT2 (DEMO-4) | 142.0 h | 52.0 (46.2-59.4) | 39.6 (34.7-46.2) | 20.8 (20.8-23.8) |
| GT3 (DEMO-5) | 161.5 h | 49.6 (44.1-56.7) | 37.8 (33.1-44.1) | 23.7 (23.7-23.7) |

Reading: DEMO-0 is the only near-term promise (about 12.4 (11.0-14.2) sessions at LVL-A, plus 2-3 sessions of responder windows; the floor binds at LVL-B and LVL-C); the Claude path to DEMO-1 and DEMO-2 is long because Claude carries the stand-ins itself; breadth lanes run in parallel and finish earlier than their gates. If Codex is frozen nothing on this table changes. Minimum viable cut: the ancestor set of each gate; never cut: independent verifier actor, `do_nothing`, honest `unlinked`, the human gate, bounded revision, negatives, `doubles[]`, the budget ceiling, the data-class gate, the treated-payload scanner.

### 13. Risks

| # | Risk | P/I | Mitigation |
|---|---|---|---|
| R1 | DEMO-0 builder output cannot become a valid artifact (S-MAP) | medium/high | `unlinked` and `not_evaluable` are valid endings; target from the ReadBase catalogue; permutation test |
| R2 | `agent_roleplay` read as model quality | medium/high | status vocabulary, honesty tests, `quality_claims: forbidden`, GT05m measures |
| R3 | E0 text reaches a third party (responder, developer agent, git) | medium/high | TPS scanner, DC0 push scan, treated-only rule, agents work from schemas |
| R4 | Roleplay latency (10-30 min per live run), the 60 s and 600 s limits, one responder slot | high/medium | async job pattern, step caps, CLT0, replay by digest, live windows |
| R5 | Claude concentration: about 74% of hours and the whole critical path on one team | high/medium | per-lane journals, pooled reviewers, trains, independent Codex lanes, tripwires |
| R6 | Stand-ins diverge from Codex semantics | medium/medium | swap-in conformance tests on FRZ0 cases; RG-5; labels in `doubles[]` |
| R7 | Cargo and RAM contention (5.7 GB free sample, 10 GB VM, two accounts building) | high/medium | ENV0 first, ENV8 lock, replay gate, one stack, caps; HW-1..3 |
| R8 | Contract drift between lanes | high/high | digest pins, FRZ0 pack, same black-box file on double and real |
| R9 | Pin churn (5 bumps in 21 h, `VERSION` constant) | high/medium | G2 gate on SHA plus manifest digest |
| R10 | agent-core PRs 23, 24, 28 never reach main; N8-02 ambiguous 409 | high/medium | no Core-side Jev; reconcile read disambiguates; EXT-1 |
| R11 | Hosted CI red hides regressions | high/medium | local receipts; ASK-22 |
| R12 | Podman instability (cgroups, ports) | medium/high | doctor smoke before any `real` label |
| R13 | First AWS apply fails | high/medium | 10-18 h budgeted (TA3), offline plan early |
| R14 | Python host becomes permanent | medium/high | freeze rule, RG-1..RG-4, deletion in Q2 |
| R15 | Core quotas (10 proposals per 24 h, 20 evals per proposal) throttle live runs | medium/medium | fresh Core DB per run, injected clock |
| R16 | Optimistic "done" claims | medium/medium | every `[DONE]` needs a receipt with `doubles[]` |
| R17 | ENV gains smaller than hoped | medium/medium | ENV0 rule: keep only at least 1.3x or 5 minutes |
| R18 | Codex idle for lack of a merge or an ask (ASK-2, ASK-3 silent) | medium/medium | Codex 0 hours under ASK-2 silence is planned for; depth-1 plus bundles under ASK-3 silence |

### 14. Asks and relays (silence is never approval)

Order: your one-sentence decisions first, then external relays. Every ask has a needed-by and a safe default taken without an answer. The checker proves that gates GT0, GT05, GT1A, GT1B, GT2, GT3 have no ancestor that needs an ask; the asks that stay behind a default only gate GT05m (ASK-7) and GTA (ASK-17..21).

| id | ask (one sentence) | needed by | safe default if unanswered | unlocks |
|---|---|---|---|---|
| ASK-1 | Confirm in one sentence that the roleplay responder may receive only treated payloads (after the spec pre-ModelPort treatment), never raw E0 or CSV rows or raw conversation text; you may lift it later. | session 6 (first live roleplay run on E0-derived input; synthetic smokes and replay need nothing) | treated payloads only | DEMO-0 live run |
| ASK-2 | Lift the Codex scope freeze (CX-0180) for offline lanes only (no Podman, no live PG). | session 2 (pack publication) | Claude path alone; Codex lanes execute 0 hours; swap-ins wait | all Codex lanes (364-557 h) |
| ASK-3 | Delegate to Claude the merge of its own consolidated trains when the local receipt is green (Codex trains still wait for you). | first W0 PR (session 3) | you merge each train; both teams keep working stacked and publish bundles (section 8) | throughput of every wave |
| ASK-4 | Approve one named download: the Go builder image (name and size are quoted by SNET) used to build llm-gateway from the pinned SHA. | session 1-2 (before M1) | existing fixtures_app contract double; doubles[] says gateway=stand-in | real gateway label at DEMO-0 |
| ASK-5 | Acknowledge the ADR (written by ENVADR from ENV0 evidence) that allows a Linux build container inside the existing WSL VM despite AGENTS.md. | W1, before ENV1 | measure only; ENV1 stays undone | ENV1 |
| ASK-6 | Approve named downloads for the build container: toolchain image and optional sccache and nextest. | W1, before ENV1 or ENV3 or ENV5 | none downloaded | ENV1, ENV3, ENV5 |
| ASK-7 | Approve one local model download (name, source, size) for the RTX 3060. | W1, before ENV9 | none; roleplay replay stays the rung | ENV9, SMOKE, GT05m |
| ASK-8 | May treated E0 payloads go to a hosted REAL model (DEMO-2 rung-up)? | W3, before DEMO-2 | NO | hosted real-model run |
| ASK-9 | Provide a hosted model key in an ignored env file with a hard cap (suggested USD 20 through DEMO-1a, 100 through T2, 2 per run, 10 per day), synthetic data only. | W1, before M4 | no hosted calls | M4 |
| ASK-10 | Provide JEV_API_KEY for the real gateway /v1/jev. | W4, before BKJL against the real upstream | Jev only through the shim | real Jev upstream test |
| ASK-11 | Give a 15-minute approver session for one recorded CLI approval. | W2, DEMO-1 | simulated issuer | H1r (step 8 relabel) |
| ASK-12 | Name a notification channel (webhook or mailbox) for waiting_human. | W3, before H1n | file sink | H1n real channel |
| ASK-13 | Give the Codex account read access to the vendor dir and permission for cargo build --offline. | W1, before ENV10 | Codex builds with its own cache | ENV10 |
| ASK-14 | Pick hardware option HW-1, HW-2 or HW-3 (section 6) once ENV0 names the bottleneck. | after ENV0 (W1) | LVL-A or LVL-B only | ENV11, ENV12, LVL-C |
| ASK-15 | Confirm the review-loop classes RC1-RC3 and that spikes are rewritten test-first. | session 1 | full ritual for every WP, no exemption | nothing blocks |
| ASK-16 | Optional: consent for Claude to edit named Codex-owned files while Codex is frozen. | only if you want it | none; stand-ins are used | nothing blocks |
| ASK-17 | Provide the AWS staging account id, region and SSO profile name. | W5, before TA3 | offline plan only | TA3-TA6, LAB28, GTA |
| ASK-18 | Confirm who owns the shared AWS foundations and the Terraform state bucket (default: the agent-core infra owner, via a relay). | W5, before TA3 | defer; plan only | TA3 |
| ASK-19 | Give an alarm mailbox that a human reads. | W5, before TA6 | alarm stays unconfirmed (TA6 red) | TA6 |
| ASK-20 | Set a monthly AWS spend ceiling. | W5, before TA6 | no apply | TA6 |
| ASK-21 | Approve each apply of a saved Terraform plan (one sentence per apply). | W5, per apply | no apply | TA4 and later |
| ASK-22 | Provide GitHub Actions budget or a self-hosted runner. | W2 | local receipts are merge evidence | hosted CI evidence |
| ASK-23 | Announce free-RAM windows for live runs (host free RAM was 5.7 of 16 GB at the last sample). | session 5, before the first live run | live run skipped with insufficient_memory; replay only | live runs |
| ASK-24 | Relay message EXT-1 to the agent-core team (text in section 14). | W2, before DEMO-1 | plan without them; no Core-side Jev; plan-only AWS | pin hygiene, Jev on main |
| ASK-25 | Relay message EXT-2 to the Product team (text in section 14). | W5, before P3 | simulator and capability profile; no outbound action | P3 |
| ASK-26 | Relay message EXT-3 to the llm-gateway owners (text in section 14). | W2, before DEMO-1 | build from SHA 63155b6; client-side ceiling and ledger | gateway tag and caps |

**EXT-1, paste-ready, for the agent-core team** (relay through you; the journal does not reach them):

> Subject: Pulso improvement-engine consuming agent-core (pin c814c2b). We consume agent-core through its HTTP contract only and change nothing in it. Four requests, each with our fallback if you cannot: (1) PRs 23, 24 (registry contract, proposals listing) and 28 (Jev through the gateway) show merged=true into side branches (ccr-a4781bdb-dnrn7q, feat/registry-contratos, feat/http-llm-gateway) but are not on main; will they land on main? Fallback: we treat Jev as blocked and use llm_structured stages. (2) Please return a distinct error code for an idempotent request still in progress; today a 409 idempotency_conflict is ambiguous (N8-02). Fallback: we disambiguate with a reconcile read. (3) Please publish a changelog and a manifest digest per pin bump; we saw 5 bumps in about 21 hours. Fallback: we gate on SHA plus manifest digest. (4) For AWS: can your infra owner confirm the Core workload slice and one pulso-core-runtime name, and whether registry-e2e overlaps our e2e-core? Fallback: plan-only AWS, no duplication of shared foundations.

**EXT-2, paste-ready, for the Product team:**

> Subject: Pulso improvement-engine and the support platform (Phase 1). We read your published data model (cases, turns, assignments, event_log) through our own exporter and simulator and write nothing to your platform. Please tell us, with our fallback if you cannot: (1) how a consumer may read events and the payload per event_type; fallback: our simulator and a capability profile that ends at insufficient_*. (2) whether event_log.sequence is contiguous per tenant. (3) your Phase 2 roadmap for AI features, and a marker that identifies demo rows. (4) retention rules, and whether conversation text may reach hosted models; fallback: it never does. (5) which registry and alias your runtime resolves, and who approves a release on your side; fallback: outbound actions stay blocked(product-phase-2).

**EXT-3, paste-ready, for the llm-gateway owners:**

> Subject: llm-gateway consumption by Pulso (main 63155b6). We build the gateway from the pinned SHA and call POST /v1/generate. Please consider, with our fallback if not: (1) push the first tag (release.yml exists, 0 tags and 0 releases today) and publish a GHCR digest; fallback: build from SHA. (2) a per-consumer allowlist of aliases and models and price caps; rate limit; echo of the provider request id; an Idempotency-Key; a stable error code field; the status of /v1/jev. Fallback: we enforce ceilings, a ledger and a kill switch client-side (M2a, M2f).

### 15. Residual uncertainties (falsifiers, read-only first)

1. Whether Codex's account can read the vendor dir, build offline and reach a loopback PG (ENV10, ASK-13).
2. Whether the spec's pre-ModelPort treatment is already a callable function or must be re-implemented to define the scanner allow-list (TPS reads it first); the value of k.
3. Whether the local-sim E0 output feeds the builder design input without a new adapter (ED0, SMAP).
4. Responder latency tail against the 60 s and 600 s limits, and whether the responder lane runs as stateless background subagents (SNET, RPP).
5. Real gains of ENV items (all "to measure"); Windows versus Linux parity.
6. Whether the agent platform allows the concurrent agents assumed at LVL-B and LVL-C.
7. PG 16 (Core runtime) versus 17 (engine CI) behaviour (G0gr preflight).
8. Whether Core quotas bite the roleplay live runs; the `usage_estimated` metering path of the shim against the reservation logic.
9. Per-type counts (521 pub types, 59 `compile_fail`) are re-measured by G0gr.
10. Claude-side Rust throughput is unmeasured (no Rust record in this repo); hours for new-seam Rust are 0.8-1.4x and re-baselined at GT0 and TW-1.
11. Whether the Go builder image can be pulled at all in the default Podman connection (ASK-4, SNET); if not, DEMO-0 carries `gateway=stand-in`.

## Annex A. Work packages (machine-readable table)

Columns: `id | name | stream | lane | owner | hours_low | hours_high | deps | wave | tier | critical | demo_path | needs | paths | first_red | acceptance`. Owner CL = Claude (orchestrator plus subagents), CX = Codex. A `~` before a dep marks an optional swap-in edge (Claude WP, Codex dep, never gating). `critical` = Y when the WP has at most 4 midpoint hours of float on the longest chain to GT1B (computed). `demo_path` = Y for the WPs that are exactly the ancestors of GT0 plus GT0. `needs` lists the asks (ASK-n, section 14) a WP cannot run without; `-` means none (every Codex WP implicitly needs ASK-2). `paths` lists the globs the WP edits; each must resolve inside the WP's lane in the annex D map (`@lane` = anywhere inside the lane's own globs; only ENV-free bootstrap commits XSTUB and K0 create files of other lanes' crates, and they create only empty stubs or declarations). Hours include implementation, own tests and the first review loop; later loops are the CRV and REV WPs. Gate WPs are 1-2 h evidence packages. External work (EXT, ASK) has no hours. The same table is in `wp_table.csv` next to `check_plan.py`.

| id | name | stream | lane | owner | hours_low | hours_high | deps | wave | tier | critical | demo_path | needs | paths | first_red | acceptance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G0f | OWNERS.md with generated path map and test, journal tags, state table, Team trailer, Codex onboarding brief | G | L-GOV | CL | 2 | 3 | - | W0 | T0 | Y | Y | - | OWNERS.md AGENTS.md docs/agents/** | owners test fails on the 1683 tracked files with no map | 0 unowned and 0 tied tracked paths at 853b029 plus rules for new paths; brief states data-class rule for all developer agents |
| G0gp | Facts refresh: pins, gateway SHA, agent-core main, PR states, DB versions | G | L-GOV | CL | 2 | 3 | - | W0 | T0 | N | Y | - | docs/reports/gates/** | facts.json schema test fails when a SHA is missing | facts.json with SHAs and gh state of agent-core PRs 23, 24, 28 |
| G0gr | Pub-surface audit (pub types, serde derives, compile_fail), post-merge review of PR 93, PG16 and PG17 preflight | G | L-GOV | CL | 4 | 6 | - | W0 | T0 | Y | N | - | docs/reports/gates/** | audit script fails when counts are absent | measured counts replace 521 and 59; export request list for WDX; ADR and journal maxima read |
| G1 | engine-run report schema, doubles[] generator, honesty and author-separation tests | G | L-GOV | CL | 9 | 12 | - | W0 | T0 | N | Y | - | contracts/engine-run/** | honesty test 1 fails: real status with a scripted receipt provider | tests 1,4,5,6 green; tests 2,3,7,8 are red skeletons turned green by TPS (2), ED0 (3), RPP (7), DC0 (8); report carries target, sha, contract_revision and host per step; all 8 green is a GT0 criterion |
| CONTR | contracts/engine-steps JSON in/out schemas and port list (draft v0) | C | L-GOV | CL | 3 | 4 | G0f | W0 | T0 | Y | Y | - | contracts/engine-steps/** | schema validation fails on a sample step | schemas for sensors, recompute, validation, compile, gate; digest published |
| CF0 | Contract freeze 0: freeze C-13 and C-7 v1 (existing trait); digests and stubs of drafts C-2..C-12 | C | L-GOV | CL | 3 | 4 | CONTR,G0f | W0 | T0 | Y | N | - | docs/reports/gates/** | digest pin test fails with no published digest | journal CONTRACT-PUBLISHED entries; C-13 allocation tables and C-7 v1 frozen by digest; digests of drafts C-2..C-12 published as provisional |
| XSTUB | Codex: empty module stubs and [[test]] entries for every planned module in one commit | D | X-FACADE | CX | 2 | 3 | G0f | W0 | T0 | N | N | - | crates/core/Cargo.toml crates/core/src/lib.rs | cargo check fails on a mod line without file | root gate green; no behaviour; single bootstrap commit also creates the empty stub files owned by other Codex lanes; lib.rs and core Cargo.toml untouched afterwards by other lanes |
| DC0 | Data-class gate: gw-e0 and gw-hosted profiles, internal network, content scanner, push scan, split corpora | G | L-MODEL | CL | 5 | 7 | - | W0 | T0 | N | Y | - | scripts/dc/** local/core/gateway/** | scanner fails on a tracked file with an E0 marker | honesty test 8 green; E0 profile has no key and no external route; push scan blocks a tracked file with an E0 marker |
| SNET | Spike: container-to-host reachability, clock skew, multi-minute calls, gateway timeout_s 60 versus invoke 600 s, Go image availability | G | L-E2E | CL | 3 | 4 | - | W0 | T0 | N | Y | - | e2e-core/** demo/** | probe fails when Core cannot reach the host shim | report with: 5-minute call result, behaviour of a 70 s model call (typed timeout), measured seconds per responder call, podman images check for the Go builder image; spike rewritten test-first |
| M1 | Real llm-gateway in the local Core stack from pinned SHA: LLM_ENDPOINTS alias pulso-evolution-llm to the shim, stage policy, smoke | M | L-MODEL | CL | 4 | 6 | G0gp,SNET | W0 | T0 | N | Y | - | local/core/gateway/** | smoke fails: gateway alias returns 404 | real gateway answers a Core stage call through alias pulso-evolution-llm (model external-reasoning-model, price 1/4, registry untouched); if the Go image is absent and ASK-4 is unanswered, the existing fixtures_app contract double answers and doubles[] says gateway=stand-in |
| M0RP | agent_roleplay shim: OpenAI chat-completions upstream of the real gateway, request queue, async job pattern with late-answer cache, normalised replay key, fault channel | M | L-MODEL | CL | 10 | 14 | - | W0 | T0 | N | Y | - | roleplay-llm/** | replay test fails: the same stage re-run with a new run_id misses the recorded digest | JSON step round trip (message content {"kind":"tool_call"} or {"kind":"final"}, no OpenAI tool_calls); same stage replayed 3 times from a fresh Core DB with 0 misses (run_id, turn_id, session_id, binding, job and artifact ids normalised); a call slower than 55 s returns typed 504 and its late answer serves the retry; drift test shows the digest diff |
| M3 | Stage hardening: gateway schema subset, stage policy alignment, timeout plan, synthetic recorded corpus, replay mode | M | L-MODEL | CL | 7 | 11 | M0RP,G1 | W0 | T0 | N | Y | - | core-bridge/src/pulso_core_runtime/stages/** core-bridge/tests/llm/** | stage policy test fails: shim answers with model agent_roleplay and the policy rejects model_mismatch | 4 stages (scout, verifier, builder, writer) pass in replay with 0 schema rejects and 0 alias_mismatch, model_mismatch or price_mismatch; registry profile bytes and release digests unchanged; scout and verifier capped at 5 steps, builder at 7 |
| SMAP | S-MAP-lite harness: finding to builder to dry-run, 10 recorded outputs, design-input producer, C-8 JSON schemas, capability catalogue in ReadBase | M | L-MODEL | CL | 12 | 20 | M0RP,DC0,ED0,WRLD0,TPS | W0 | T0 | N | Y | - | core-bridge/tests/runtime/test_stages_smap.py agent-core-assets/corpus/** | permutation test fails: relabelling the finding category leaves the target unchanged | 10 outputs recorded; counts of valid, unlinked, not_evaluable reported; target chosen from the ReadBase capability catalogue, never from model prose; relabel and permute test changes or nulls the target; one negative ends unlinked |
| ED0L | E0-backed treated lab and deterministic recompute for scout and verifier (sqlite lab of treated aggregates; evidence refs resolvable) | Q | L-E2E | CL | 8 | 14 | DC0,ED0,TPS | W0 | T0 | N | Y | - | e2e-core/** demo/** | verifier test fails: an evidence ref does not resolve in the lab | lab rows are k-anonymous treated aggregates only; verifier recompute equals the scout figure on 5 fixtures bit for bit; a tampered numerator fails; every evidence ref resolves; no raw E0 row crosses the scanner |
| ED0b | Original bank CSV dataset through the same runner (--source original), separate namespace, unsupported_source honoured | Q | L-E2E | CL | 3 | 5 | ED0 | W1 | T0.5 | N | N | - | e2e-core/** demo/** | unsupported_source negative fails: an original-only finding passes as supported | runner --source original runs locally in its own namespace; negative green; labelled real-narrow with data_origin recorded; 0 raw rows leave the local host; no Codex WP needed |
| CMPpy | Generic ChangeSpec to DraftPlan compile in Python for Replace Prompt plus Add EvalSuite over the seeded world, digest from Core dry-run | Q | L-E2E | CL | 5 | 8 | CONTR,WRLD0 | W0 | T0 | N | Y | - | e2e-core/** demo/** | compile test fails on a two-operation spec | compiles the SMAP valid outputs at INT0 (built first against the CONTR C-8 schema fixtures); 4 denied kinds return the named reason; dry-run accepted by real Core; label compile=claude-standin(python) |
| GSIpy | Stand-in gate verdict from arm reports with an author-separated judge (replaces the planted judge of demo/); structural verdict only | Q | L-E2E | CL | 5 | 8 | G1,WRLD0 | W0 | T0 | N | Y | - | e2e-core/** demo/** | gate test fails when one of two gates is skipped | verdict from both gates over 5 arm-report fixtures; judge author differs from suite and world authors; report states quality_claims: forbidden; planted columns not read |
| M2a | Spend ceilings on the single Python ledger, kill switch, reconciliation hook | M | L-MODEL | CL | 3 | 4 | M1 | W0 | T0 | N | Y | - | core-bridge/src/pulso_core_runtime/llm/** | ceiling test fails when a call exceeds the cap | run stops at ceiling; ledger equals gateway sum within 1 token |
| P2py | Simulator release events, fast-forward clock, effect realism with author separation | P | L-PLAT | CL | 6 | 9 | G1 | W0 | T0 | N | Y | - | platform-sim/** platform-contract/** | sim test fails: no release.* event after publish | release events plus effect series authored apart from the judge; observation only: memory and successor are labelled not_exercised |
| Q1r | E2E-THREAD-01 ratchet in replay and live with all ten steps on the Python host; planted judge, effect and revision wiring of demo/ replaced | Q | L-E2E | CL | 14 | 22 | G1,M3,M1,P2py,ED0,ED0L,SMAP,CMPpy,GSIpy,CLT0 | W0 | T0 | N | Y | - | e2e-core/** demo/** | ratchet test file with ten red steps | replay green with 0 digest misses; one live roleplay run; every step labelled with status and data class; step 7 not_exercised unless the gate fails; step 10 observation only; host=python |
| INT0 | DEMO-0 integration tail: first full ten-step run on Podman, replay drift, live windows, fix cycle | Q | L-E2E | CL | 10 | 16 | Q1r | W0 | T0 | N | Y | - | e2e-core/** demo/** | ten-step run fails at the first step that still uses a fixture | one full run of the ten steps green in replay and one live run; 3 live windows logged with seconds per call; every drift diff explained |
| CRV0 | Independent adversarial review before GT0: RC1 loops on TPS, DC0, G1, M2a, M0RP and the E0 data path; RC2 on the rest; distinct fresh-context reviewers | D | L-GOV | CL | 6 | 10 | TPS,DC0,G1,M2a,M0RP,ED0,ED0L,SMAP,M3 | W0 | T0 | N | Y | - | docs/reviews/claude/** | review-closure script exits 1 while any finding is open | findings of loops 1 to 3 closed; reviewer differs from author for every reviewed WP; review log in docs/reviews/claude; CRV1 retro-reviews Q1r, INT0, CMPpy and GSIpy |
| GT0 | Gate DEMO-0 (honest scope): E0 ingested locally, detection by the existing Rust sensor, scout and verifier on an E0-backed lab with recompute, builder via S-MAP, generic compile, stand-in verdict, real Core arms, simulated approval, publish to local staging, alias read, observation | Q | L-GOV | CL | 1 | 2 | Q1r,INT0,SMAP,M2a,DC0,ED0,ED0L,TPS,RPP,CRV0,TRN0 | W0 | T0 | N | Y | - | docs/reports/gates/** | gate evidence script fails on a missing receipt | replay green with 0 misses and one live roleplay run; all 8 honesty tests green; C-2 and C-12 frozen by digest; lane-hours per session re-baselined from sessions 1 to 12; doubles[] lists model=agent_roleplay, jev=not_exercised(blocked: agent-core PR 28 not on main), issuer=simulated, product=simulated, host=python, gate=claude-authored(structural, quality_claims forbidden), data_origin=generated_sample; scanner passed every payload |
| BK0 | Artifact-kind capability matrix as a contract with propose, validate, evaluate, publish verbs and denied-kind list | B | L-GOV | CL | 4 | 6 | CONTR,G0gr | W0 | T0 | N | N | - | contracts/artifact-kinds/** | matrix test fails when a kind has no verb row | contracts/artifact-kinds covers every EntityKind and release_settings; digest published as frozen artifact |
| FRZ0 | Frozen artifact pack for Codex: C-7 v1.1 claim-next signature, C-8 ChangeSpec and ScenarioCase schemas, C-9 transcript seed, C-10 gate result shape, builder-output corpus v0 (10 synthetic outputs), arm-report goldens, bridge dry-run and writer goldens with digests, PG claim traces | C | L-GOV | CL | 9 | 13 | CONTR,G0f | W0 | T0 | N | N | - | contracts/engine-steps/** | pack digest test fails when a golden or the bridge dry-run goldens are missing | pack published with one digest and a manifest of 7 parts; Codex lanes verify only against it (no Core, PG or Podman); journal CONTRACT-PUBLISHED |
| M5a | Roleplay JEV server behind gateway /v1/jev, plus Python JevDecisionPort test (DEMO-0 uses llm_structured stages; Core-side Jev stays blocked(jev) until agent-core PR 28 is on main) | M | L-MODEL | CL | 4 | 6 | M0RP | W1 | T0.5 | N | N | - | roleplay-llm/** | pass-through test fails on header strip | gateway forwards to the roleplay JEV; port handles 200, 4xx, 502; real upstream needs JEV_API_KEY (ASK-10); GT0 labels jev=not_exercised |
| ED0 | E0 ingest and local detection: existing Rust local-sim sensor (first Windows build of the runner, own target dir) on the E0 package, sealed ranking, discards, design-input producer | Q | L-E2E | CL | 8 | 14 | DC0,G0e | W0 | T0 | N | Y | - | e2e-core/** demo/** | rename and permute mutation test: winning category changes with the label | detection output derived from E0 locally by the Rust sensor (one admitted signal family plus recorded discards), no planted column; honesty test 3 green; report carries data_origin=generated_sample; receipts show only local providers |
| G0p | W0 pre-PR gate and receipt script: verify-local-ci.ps1 plus pytest of touched Python packages plus replay-mode ratchet | G | L-GOV | CL | 2 | 3 | - | W0 | T0 | N | Y | - | scripts/gov/** | receipt script exits 1 when the pytest leg or the replay-ratchet leg is missing | receipt JSON (verify-local-ci result, packages touched, ratchet replay result) pasted in each W0 PR body; superseded by verify-local-all at G0d |
| TRN0 | Claude consolidation train integrator for W0: lane merges in dependency order, PR per 25 to 35 lane-hours, restack rule, W0 receipt | G | L-GOV | CL | 3 | 4 | G0p | W0 | T0 | N | Y | - | scripts/gov/** | train script fails when a lane branch is out of order | W0 PRs merged in order, each with the W0 receipt; stacked trains restacked within one fast gate; bundle written to exchange/ when the PR cap is reached |
| WRLD0 | Seeded base world: an attention-demo dispute agent that an E0 dispute finding can plausibly target (Replace Prompt plus Add EvalSuite) | M | L-MODEL | CL | 3 | 4 | G0gp | W0 | T0 | N | Y | - | agent-core-assets/worlds/** | world conformance test fails: no agent with a replaceable prompt exists in the seeded world | seeded world with 1 dispute agent, 1 prompt, 1 eval-suite slot; label base_world=seeded; world author recorded and different from the judge |
| CLT0 | Configurable invoke timeout (default 600 s) in AsgiCoreClient and unknown-to-reconcile polling for live runs | I | L-BRIDGE | CL | 1 | 2 | - | W0 | T0 | N | Y | - | core-bridge/src/pulso_core_runtime/client/** | client test fails: a 700 s stage call is cut at 600 s | timeout read from config (1800 s for live DEMO-0 runs); a call that exceeds it becomes unknown and the host polls reconcile until terminal; 0 duplicate effects in 3 forced cases |
| TPS | Treated-payload scanner at the roleplay shim: deny-by-default allow-list over the fixed LLMAgentPort input dict, treated-aggregate spec for lab-row observations | M | L-MODEL | CL | 6 | 9 | - | W0 | T0 | N | Y | - | roleplay-llm/** | scanner test: a lab row with a free-text field is rejected | 100 treated payloads pass, 20 raw rows and raw conversation texts rejected; a k-anonymous aggregate (count >= k, hashed ids, enum fields, no free text) passes and a row below k is suppressed; honesty test 2 green |
| RPP | Responder protocol and runbook: queue directory, one fresh-context subagent per request or stage batch, distinct responders for scout, verifier, builder, one agent slot, call budget, latency budget | M | L-MODEL | CL | 3 | 4 | M0RP | W0 | T0 | N | Y | - | roleplay-llm/** | protocol test: a responder that sees the repo instead of the queue file is rejected | documented lane of subagents driven by the orchestrator; step caps (scout 5, verifier 5, builder 7) enforced; measured calls and minutes per live run in the report; honesty test 7 green |
| ENV0 | Baseline timings in both accounts (cold and warm core test --no-run, link share, host free RAM, gate minutes, worktree count) and keep/cut table | ENV | L-ENV | CL | 2 | 3 | - | W1 | T0.5 | Y | N | - | scripts/env/** | baseline.ps1 --check fails without baseline.json | baseline.json for both accounts with 6 timings each (cold and warm core test --no-run, link share, gate minutes, host free RAM min and median over a working day, worktree count); keep or cut table; every speedup claim in the plan cites it |
| ENVADR | ADR: Linux build container inside the existing WSL VM versus AGENTS.md rule no development in WSL | G | L-GOV | CL | 1 | 2 | ENV0 | W1 | T0.5 | N | N | - | docs/adr/020[0-9]-* | test asserts AGENTS.md WSL rule cites an ADR | ADR merged from the L-GOV block (0200-0209) citing the incompatibilities measured by ENV0; user ack ASK-5 quoted in journal; root gate stays Windows |
| ENV2 | Host lld, line-tables-only debug profile, Defender exclusion for target dirs, per-account config | ENV | L-ENV | CL | 1 | 2 | ENV0 | W1 | T0.5 | Y | N | - | scripts/env/** | baseline.ps1 --compare exits 1 against the committed baseline before the change | kept only if >=1.3x or >=5 min saved on core test --no-run (compare exits 0), else reverted and recorded |
| ENV4 | cargo vendor into shared read-only dir with per-account source replacement; closure includes crates/core 189 packages | ENV | L-ENV | CL | 2 | 3 | ENV0 | W1 | T0.5 | Y | N | - | scripts/env/** | cargo build --offline --locked fails in clean CARGO_HOME | both accounts build the seams skeleton and root tests --no-run offline (exit 0); the new packages (about 25-35) are listed |
| ENV6 | Fast gate and full gate wrappers: Codex gate unchanged as a leg, seams leg with manifest-path and locked, Pester asserts | ENV | L-ENV | CL | 3 | 4 | ENV0 | W1 | T0.5 | N | N | - | scripts/verify-local-all.ps1 tests/verify-local-*.Tests.ps1 | Pester asserts verify-local-all runs the root script and the seams leg | seams-only change runs no root workspace test; receipt JSON with minutes |
| ENV8 | Memory plan: measure .wslconfig and host headroom, heavy-slot lock file; no machine is stopped, created or resized | ENV | L-ENV | CL | 1 | 2 | ENV0 | W1 | T0.5 | N | N | - | scripts/env/** | two processes contend, only one acquires the lock | lock honoured by both accounts; min and median free host RAM over a working day recorded; recommended .wslconfig values written as a user ask only |
| G0e | Per-lane CARGO_TARGET_DIR on D: and slot protocol (moved to W0) | G | L-ENV | CL | 1 | 2 | - | W0 | T0 | N | Y | - | scripts/env/** | two lanes with equal target dir fail the check | each lane has its own target dir on D: (never C:); two lanes with equal dirs fail the check; documented in the lane brief |
| WTR1 | Worktree inventory and retirement of merged legacy worktrees (Claude side); hard cap of 40 registered worktrees | G | L-ENV | CL | 2 | 3 | - | W0 | T0 | N | N | - | scripts/env/** | inventory script lists unmerged worktrees and exits 1 above 40 registered | registered worktrees at most 40 (58 measured today); merged legacy ones removed; unmerged ones listed for the user; no Codex worktree touched |
| G2 | pin-watch and bump lane (initial; later bumps 2-4 h each) | G | L-BRIDGE | CL | 4 | 6 | - | W1 | T0.5 | N | N | - | scripts/core/** | pin-watch test fails on a pin bump without manifest digest | gate on SHA plus manifest digest; one generated pin-constants file |
| WTR2 | Codex-side worktree inventory and retirement | G | X-REV | CX | 1 | 2 | - | W0 | T0 | N | N | - | docs/reviews/codex/** | inventory script lists unmerged worktrees | default under silence: list-only report to the user; with ASK-2 answered the merged Codex worktrees are removed; combined count reported |
| G0d | verify-local-all receipt script (root gate leg, seams leg, replay mode, E0 scanner hook) | G | L-ENV | CL | 4 | 6 | ENV6,G0f | W1 | T0.5 | N | N | - | scripts/verify-local-all.ps1 tests/verify-local-*.Tests.ps1 | Pester asserts receipt has the seams leg and the scanner | receipt JSON in every PR body |
| ENV10 | Codex-side probe: offline build from the vendor dir, own target dir, timings, loopback PG reachability | ENV | X-REV | CX | 1 | 2 | ENV4 | W1 | T0.5 | N | N | ASK-13 | docs/reviews/codex/** | probe fails when the vendor dir is unreadable | report with minutes of an offline build in the Codex account and whether loopback PG answers (yes or no); exit 0 |
| PX0 | Product consumption contract: registry alias resolution plus release.* exposure events; platform-sim reads the real Core alias | P | L-PLAT | CL | 4 | 6 | G1 | W1 | T0.5 | N | N | - | platform-sim/** platform-contract/** | sim conformance fails: alias read returns nothing | spec amendment; label simulated(product-consumer) until EXT-2 answers |
| M4 | Hosted smoke on synthetic data with capped key | M | L-MODEL | CL | 3 | 4 | M2a,M3 | W1 | T0.5 | N | N | ASK-9 | core-bridge/src/pulso_core_runtime/llm/** | smoke fails without the cap env | scout 3 of 3 schema-valid on a hosted model with the cap env set, receipt provider shown; blocked until ASK-9 is answered |
| ENV9 | Local GPU model runtime on the RTX 3060 (model name, source and size need approval ASK-7) | ENV | L-ENV | CL | 4 | 8 | ENV8 | W1 | T0.5 | N | N | ASK-7 | scripts/env/** | runtime smoke fails: no completion | rung-up to the local model: runtime smoke returns a completion, model digest in the receipt, heavy slot taken; needs the download approval ASK-7 |
| SMOKE | Local-model smoke: scout and verifier 3 of 3 schema-valid, builder 2 of 3 with one regeneration | M | L-MODEL | CL | 4 | 8 | ENV9,M3,M1 | W1 | T0.5 | N | N | ASK-7 | core-bridge/tests/llm/** | smoke asserts schema-valid rate and fails at 0 of 3 | rung-up DEMO: scout and verifier 3 of 3, builder 2 of 3 schema-valid on the local model; status local-model; payload scanner stays on |
| ENV1 | Linux build container inside the existing VM (conditional on ENV0 and ADR) | ENV | L-ENV | CL | 4 | 6 | ENV0,ENVADR | W1 | T0.5 | N | N | ASK-5,ASK-6 | scripts/env/** | container build fails: no toolchain | warm seams build time recorded; kept only if >=1.3x on Claude seams builds; ADR merged and ack ASK-5 quoted before the first container build |
| ENV3 | sccache in the Linux build container (conditional) | ENV | L-ENV | CL | 2 | 3 | ENV1 | W1 | T0.5 | N | N | ASK-6 | scripts/env/** | cache hit-rate check fails at 0 | kept only if ENV0 rule is met |
| ENV5 | cargo-nextest archive and partitioned runs in the container (conditional) | ENV | L-ENV | CL | 2 | 3 | ENV1 | W1 | T0.5 | N | N | ASK-6 | scripts/env/** | partitioned run misses a test | all tests run exactly once across 3 partitions (union equals the full list) |
| ENV7 | pytest sharding with PG schema per shard (conditional on RAM) | ENV | L-ENV | CL | 4 | 6 | ENV8 | W1 | T0.5 | N | N | - | scripts/env/** | shard test fails on a shared schema | core-bridge suite sharded 2-way with identical pass set |
| DMAPV | Evidence-bound design-intent validation, do_nothing, no invented refs | D | X-MAP | CX | 6 | 10 | FRZ0 | W1 | T0.5 | N | N | - | crates/core/src/e0_builder_design.rs crates/core/tests/e0_investigation_plan.rs | validation test rejects an invented evidence ref | the 10 builder outputs of the FRZ0 corpus: valid, unlinked or not_evaluable decided without catalogue, identical to the FRZ0 verdicts |
| CT1 | core_task.rs 0.5.0 to 1.3.0 typed contract change via CONTRACT-CHANGE stanza | D | X-COMPILE | CX | 3 | 5 | G0gr | W1 | T0.5 | N | N | - | crates/core/src/core_task.rs crates/core/tests/core_task.rs | core_task test fails on 1.3.0 fields | digest-only constants replaced; bridge goldens parsed; reviewed by a distinct actor (if Claude is unavailable, recorded as unreviewed and closed by RVC1) |
| WDX | pub exports and DTO facades for composite steps in crates/core | D | X-FACADE | CX | 6 | 8 | G0gr,CF0,XSTUB | W1 | T0.5 | N | N | - | crates/core/src/lib.rs crates/core/src/facade_*.rs crates/core/tests/facade_*.rs | export test fails: facade not nameable outside crate | facade list from G0gr exported; sealed constructors unchanged; compile_fail guards still pass |
| DMAPC | Compiler: Replace Prompt plus Add EvalSuite, multi-operation, authorization chain; digest from bridge dry-run | D | X-COMPILE | CX | 12 | 18 | FRZ0,WDX,CT1 | W1 | T0.5 | N | N | - | crates/core/src/change_compiler.rs crates/core/tests/change_compiler.rs | compile test fails on a two-operation spec | Prompt+EvalSuite spec compiles; precondition digest hash=core-authoritative checked against the FRZ0 bridge dry-run goldens; compile_fail guards intact |
| DGATE | U27 combined gate on the paired_scenario seed | D | X-GATE | CX | 7 | 10 | G0gr,CF0 | W1 | T0.5 | N | N | - | crates/core/src/paired_scenario.rs crates/core/tests/paired_scenario.rs | gate test fails when one of two gates is skipped | both gates required; result shape C-10 draft; offline goldens |
| DVREC | Pure verifier recompute function | D | X-GATE | CX | 3 | 5 | CONTR | W1 | T0.5 | N | N | - | crates/core/src/independent_verifier.rs crates/core/tests/independent_verifier.rs | recompute test fails on a tampered numerator | recompute matches 5 fixtures bit for bit |
| DWIRE | Pure sensor entry points over input views; namespace and canary REDs | D | X-SENS | CX | 4 | 8 | CONTR | W1 | T0.5 | N | N | - | crates/core/src/deterministic_sensor.rs crates/core/tests/deterministic_sensor.rs | namespace canary fails when original and enriched mix | entry points callable through step schema; canaries red then green |
| DORIGm | Original dataset minimum slice: 2 families, separate namespaces, unsupported_source negative | D | X-SRC | CX | 8 | 10 | DWIRE | W1 | T0.5 | N | N | - | crates/core/src/original_contact_projection.rs crates/core/tests/original_contact_projection.rs | negative test fails when original-only passes as supported | 2 families on sealed ranking, no hardcoded category; negative green |
| K0 | seams workspace skeleton declaring every crate, own [workspace], edition 2024, dependency-graph test, vendor build | K | L-CLIENT | CL | 3 | 4 | ENV2,ENV4,G0gr | W1 | T0.5 | Y | N | - | seams/Cargo.toml seams/Cargo.lock seams/crates/core-client/** | graph test fails: abi depends on crates/core | workspace members glob crates/*; each lane creates its own crate directory in its first commit (K0 creates only seams/Cargo.toml, Cargo.lock and the core-client crate); graph test: abi and core-client free of crates/core; vendor build offline |
| TW0 | Tripwire TW-0 evidence: seams builds offline in the Claude account, CF0 published, Codex side only with ASK-2 | G | L-GOV | CL | 1 | 2 | CF0,K0 | W1 | T0.5 | N | N | - | docs/reports/gates/** | tripwire script fails on missing journal entry | TW-0 verdict recorded; Codex part BLOCKED if ASK-2 is unanswered |
| REV1 | Independent review wave (Codex) of S1 and S2 PRs and DTO checks | D | X-REV | CX | 4 | 6 | - | W1 | T0.5 | N | N | - | docs/reviews/codex/** | review-closure script exits 1 while any finding is open | reviews S1 and S2 PR train tag published by Claude in the journal; findings closed; verdict in journal; opportunistic second reviewer, gates nothing |
| GT05 | Gate T0.5: Rust steps called by Python host with semantics=claude-standin; RG-1; original dataset slice real-narrow; kinds proven: prompt, eval_suite | Q | L-GOV | CL | 1 | 2 | E3b,GT0,CRV1,PX0,ED0b | W1 | T0.5 | N | N | - | docs/reports/gates/** | gate script fails when a step is still stand-in | ratchet flips steps 2,3,4,5,6 to real-narrow per step with host column; ED0b original run labelled; model rung stays roleplay replay (local-model rung is GT05m); 0 asks needed |
| GT05m | Gate T0.5m: model rung-up on the local GPU model (optional, needs the download ask) | Q | L-GOV | CL | 1 | 2 | GT05,SMOKE | W1 | T0.5 | N | N | ASK-7 | docs/reports/gates/** | gate script fails when no local-model receipt exists | scout and verifier 3 of 3 and builder 2 of 3 schema-valid on the local model; E0 run with data=E0 and local model only; status local-model; scanner stays on |
| STP1 | Step stand-ins in seams/crates/steps: sensor wrapper over existing local-sim binary, verifier recompute, intent validation (labelled stand-in vs Codex semantics) | E | L-ENGINE | CL | 8 | 12 | CONTR,FRZ0,K0 | W1 | T0.5 | N | N | - | seams/crates/steps/** | recompute test fails on a tampered numerator | 3 steps JSON in and out through the step schema; Python host calls them |
| CMP | Compile stand-in: Replace Prompt plus Add EvalSuite over bridge-contract DTOs, digest from dry-run, denied-kind negatives | E | L-ENGINE | CL | 9 | 13 | CONTR,FRZ0,K0 | W1 | T0.5 | N | N | - | seams/crates/steps/** | compile test fails on a two-operation spec | compiles the FRZ0 corpus; 4 denied kinds return the named reason; label compile=claude-standin |
| GSI | Gate stand-in: two-gate verdict over arm reports, author is not judge (label gate=claude-authored) | E | L-ENGINE | CL | 6 | 9 | CONTR,FRZ0,K0 | W1 | T0.5 | N | N | - | seams/crates/steps/** | gate test fails when one gate is skipped | verdict equals FRZ0 gate goldens on 5 cases |
| E3b | Python host glue (e2e-core): steps called through the step schema, ratchet flips per step with host and semantics columns | E | L-E2E | CL | 5 | 7 | STP1,CMP,GSI | W1 | T0.5 | N | N | - | e2e-core/** demo/** | ratchet steps 2 to 6 still stand-in(python) | steps 2 to 6 flip to real-narrow with semantics=claude-standin in the ratchet (5 flips) |
| CRV1 | Independent Claude review of S1 and S2 PRs by distinct fresh-context reviewers (loops per class) | D | L-GOV | CL | 4 | 6 | E3b | W1 | T0.5 | N | N | - | docs/reviews/claude/** | review-closure script exits 1 while any finding is open | retro-review of S1 PRs (Q1r, INT0, CMPpy, GSIpy) and S2 PRs; findings closed; reviewer differs from author |
| RVC1 | Claude review of Codex W0-W1 train: facades, compiler, gate, validation (optional) | D | L-GOV | CL | 4 | 6 | ~DMAPC,~DGATE,~WDX,~DMAPV | W1 | T0.5 | N | N | - | docs/reviews/claude/** | review script lists unreviewed Codex commits | review script exits 0: every Codex commit of W0-W1 carries a reviewer id different from the author |
| TRN1 | Claude consolidation train integrator for W1: lane merges in dependency order, one PR per 25 to 35 lane-hours, restack rule, local receipt | G | L-GOV | CL | 6 | 9 | - | W1 | T0.5 | N | N | - | scripts/gov/** | train script fails when a lane branch is out of order | trains merged with receipts; stacked trains restacked within one fast gate |
| TRX1 | Codex train integrator for W1: lane merges into one train PR per 25 to 35 lane-hours, restack rule, root gate receipt | G | X-FACADE | CX | 2 | 4 | - | W1 | T0.5 | N | N | - | Cargo.lock .github/** scripts/verify-local-ci.ps1 | train script fails when a lane branch is out of order | trains merged with root gate receipts |
| DPLAT | platform_live adapter PL-C1, C2, C4, C5 | D | X-SRC | CX | 5 | 9 | G0gr | W1 | T1a | N | N | - | crates/core/src/platform_source_policy.rs crates/core/tests/platform_source_policy.rs | adapter test fails on a read-write grant | read-only snapshot adapter; PL-C4 guard test green |
| FX22a | Spec-22 wire fixture families 1 to 11 with goldens | D | X-SRC | CX | 8 | 10 | CF0 | W1 | T1a | N | N | - | contracts/fixtures/** | fixture validator fails on a missing family | 11 families validated by validate_fixtures |
| DJC | claim-next on DurableJobRepository: trait addition, in-memory reference, REDs | D | X-CONF | CX | 3 | 5 | CF0,FRZ0 | W1 | T1b | N | N | - | crates/core/src/durable_jobs.rs crates/core/tests/durable_jobs.rs | claim-next test fails: two claimers get the same job | claim-next implements the C-7 v1.1 signature frozen in FRZ0 (no signature edit here); in-memory reference green; 2 claimers never get the same job |
| TA0 | AWS asks and offline plan review | A | L-INFRA | CL | 2 | 3 | - | W1 | TA | N | N | - | infra:** | plan review checklist fails with no account assumptions | asks drafted; offline terraform validate on current tree; gaps listed |
| K1 | core-client transport: Ed25519 JWT, classifier, idempotency, generated pin constants | K | L-CLIENT | CL | 10 | 14 | K0 | W2 | T1a | Y | N | - | seams/crates/core-client/** | same Idempotency-Key twice makes 2 runs against FakeCore | 1 run on the real image for 2 identical keys; classifier table 100% of bridge-contract errors |
| K2 | core-client typed invoke, arms, admissions, dry-run, alias read (own 1.3.0 DTOs; no crates/core edit) | K | L-CLIENT | CL | 11 | 16 | K1 | W2 | T1a | N | N | - | seams/crates/core-client/** | golden decode fails for run envelope | 11 bridge-contract operations typed; FakeCore generated from goldens |
| K3fx | Fixture compiled ChangeSpec (Replace Prompt plus Add EvalSuite) from bridge-contract goldens so K3 does not wait on the compiler | K | L-CLIENT | CL | 2 | 3 | K0,SMAP | W2 | T1a | N | N | - | seams/crates/core-client/** | fixture fails dry-run against FakeCore | fixture accepted by real dry-run once; used by K3 tests |
| K3 | Draft-plan artifact, commitment sealing, writer-stage invoke, readback, dry-run | K | L-CLIENT | CL | 18 | 26 | K2,E5L,K3fx | W2 | T1a | Y | N | - | seams/crates/core-client/** | writer test fails: commitment mismatch not detected | Prompt+EvalSuite published to staging alias on the real image; readback equals commitment |
| E1 | JobHandler ABI, run-once harness, CAS-persisted inputs, resume-after-kill test | E | L-ENGINE | CL | 11 | 18 | K0,CF0 | W2 | T1a | Y | N | - | seams/crates/abi/** seams/crates/engine/** | kill between handlers loses an input | kill -9 between two handlers resumes with identical event sequence |
| E2 | Executor: linear driver then live wiring | E | L-ENGINE | CL | 14 | 20 | E1,K2 | W2 | T1a | N | N | - | seams/crates/engine/** | executor fails a 3-handler golden sequence | ten steps run on the Rust shell against the real image in one run (exit 0) |
| E9s | Spike: tiny_http SSE and disconnect detection | E | L-CAPI | CL | 2 | 2 | K0 | W2 | T1a | N | N | - | seams/crates/control-api/** contracts/control-api/** | disconnect not detected within 5 s | verdict on tiny_http versus axum with 2 measured numbers (disconnect detection seconds, memory) |
| MIG0 | Migration runner, role bootstrap, widen job status, order the three 0002 files | E | L-PG | CL | 6 | 10 | K0 | W2 | T1a | N | N | - | seams/crates/pg/** migrations/005[0-9]_* | runner schema differs from union of existing test setups | empty PG gains the same schema as the union of existing test setups (diff 0 lines); numbering gaps tolerated |
| E5L | control-api lite: artifacts, authorization-checks, core-task-bindings | E | L-CAPI | CL | 14 | 20 | K1,E1,MIG0,E9s | W2 | T1a | Y | N | - | seams/crates/control-api/** contracts/control-api/** | black-box test file fails against the Rust server | same test file green against double and Rust server; roleplay scout served |
| E4R | control-api rest: ingest ACK and quarantine, health, JWT replay store | E | L-CAPI | CL | 10 | 14 | E5L | W2 | T1a | N | N | - | seams/crates/control-api/** contracts/control-api/** | ingest gap test fails to quarantine | PL-02/03/04 cases green; replay of a JWT rejected |
| E5R | Lab and wiki broker rest: grants, QueryReceipt, wiki read | E | L-CAPI | CL | 8 | 11 | E5L | W2 | T1a | N | N | - | seams/crates/control-api/** contracts/control-api/** | grant test fails: expired grant accepted | QueryReceipt for a sqlite lab query; wiki read |
| V1 | Eval package: assets suite sealed before arms, six evaluate outcomes | V | L-EVAL | CL | 10 | 14 | K3 | W2 | T1a | Y | N | - | seams/crates/eval/** | sealed-suite test fails when suite changes after arms | the six evaluate outcomes each captured from a real arm report (6 of 6) |
| V2 | Gate wiring over real arm reports, author is not judge | V | L-EVAL | CL | 4 | 6 | V1,GSI | W2 | T1a | Y | N | - | seams/crates/eval/** | author-equals-judge test fails | verdict from both gates; fails when authors coincide |
| V3r | Rule-driven bounded revision (max 2 attempts) | V | L-EVAL | CL | 5 | 7 | V2 | W2 | T1a | N | N | - | seams/crates/eval/** | third attempt not refused | failure leads to revision then stop; budget unchanged |
| DEVAL | U47 CoreEvalPackage emitter from ScenarioCase, six-outcome capture | D | X-GATE | CX | 8 | 12 | DMAPV,DGATE | W2 | T1a | N | N | - | crates/core/src/native_evaluation.rs crates/core/tests/native_evaluation_admission.rs | emitter test fails for an unseen scenario shape | eval_suite generated from 3 non-shipped scenarios; goldens from 3 real arm reports |
| H1 | Human authority: DecisionRequest, waiting_human, issuer port, approve then publish, alias read | H | L-AUTH | CL | 10 | 14 | V2,E1,AUS | W2 | T1a | Y | N | - | seams/crates/authority/** | approve without both gates is accepted | default level: simulated issuer approves or rejects with the decision card (diff, gates, hash, alternatives, cost) and publishes; approve without both gates is refused; real recorded approval is the label upgrade H1r |
| H1r | Real approver session: one recorded CLI approval with the decision card (label upgrade of step 8) | H | L-AUTH | CL | 2 | 3 | H1 | W2 | T1a | N | N | ASK-11 | seams/crates/authority/** | recorded-approval check fails: the approval has no real operator identity | one approval by a real operator recorded with decision card digest; step 8 relabelled real-narrow; not an ancestor of any gate |
| P1 | Retarget platform-exporter to the real ingest contract | P | L-PLAT | CL | 4 | 6 | E4R | W2 | T1a | N | N | - | platform-exporter/** | exporter batch rejected by control-api | platform-sim batch reaches /internal/v1/platform/observations |
| P2R | Release correlation in ingest and successor trigger | P | L-PLAT | CL | 6 | 8 | E4R,P2py,H1 | W2 | T1a | Y | N | - | seams/crates/control-api/src/correlation/** | release event creates no successor | a release.* event starts the successor run (1 run created, 0 duplicates) |
| MEM1 | Thin memory: note artifact, wiki read, confirm or contradict | V | L-MEM | CL | 8 | 12 | E5R,P2R | W2 | T1a | Y | N | - | seams/crates/memory/** | note test fails to contradict a prior claim | 1 note confirmed and 1 contradicted, each with evidence refs that resolve |
| K5a | Reconcile: lost response, 429, crash after write | K | L-CLIENT | CL | 5 | 6 | K2 | W2 | T1a | N | N | - | seams/crates/core-client/** | lost-response test creates a duplicate | 3 fault cases yield exactly one effect |
| IN0 | One-command compose project and doctor aggregate | I | L-ENV | CL | 6 | 10 | E5L,M1 | W2 | T1a | N | N | - | local/compose.yaml scripts/dev.ps1 | doctor fails with a stopped service | one command starts the stack; doctor green |
| BOOT | pulso-bootstrap core CLI and bootstrap-report.json (CAP-48) | I | L-BRIDGE | CL | 5 | 8 | G0gp | W2 | T1a | N | N | - | scripts/core/** agent-core-assets/** | bootstrap report schema fails when empty | report lists seeded assets and digests on a fresh Core |
| BRG1 | Bridge route and mock gap requests from K2 and K3; CAP-07 decision recorded as amendment | I | L-BRIDGE | CL | 3 | 5 | K2 | W2 | T1a | N | N | - | bridge-contract/** | bridge contract test fails for a requested route | each request answered or amended; goldens regenerated |
| DPL1 | PL-02, 03, 04 ingest gating fixtures: ACK, quarantine, gap | D | X-SRC | CX | 5 | 7 | DPLAT | W2 | T1a | N | N | - | crates/core/tests/platform_observations.rs contracts/fixtures/** | fixture fails: gap not quarantined | 12 fixtures green offline; gap fixture quarantines; ACK fixture acknowledges |
| DPL2 | PL-06 to PL-10 detector REDs and capability profile ending at insufficient_* | D | X-SENS | CX | 8 | 12 | DPLAT,DWIRE | W2 | T1a | N | N | - | crates/core/src/platform_sensor.rs crates/core/tests/platform_scout.rs | PL-10 fails: detector claims data Phase 1 lacks | 5 cases green; insight stops at insufficient_* |
| DDOC1 | PL-C6 spec text and amendment index | D | X-DOC | CX | 2 | 3 | DPLAT | W2 | T1a | N | N | - | docs/spec-amendments/codex/** | doc link test fails for PL-C6 | PL-C6 amendment merged; the amendment index lists it; link test exits 0 |
| FX22b | Spec-22 families 12 to 22 plus read_model fixtures | D | X-SRC | CX | 8 | 10 | FX22a | W2 | T1a | N | N | - | contracts/fixtures/** | fixture validator fails on a missing family | families 12-22 validated |
| FX22p | contracts/product fixtures for the Product consumer contract | P | L-PLAT | CL | 3 | 5 | PX0 | W2 | T1a | N | N | - | contracts/product/** | product fixture fails validation | contracts/product validated and consumed by platform-sim |
| BKN | Denied-kind negatives: tool_without_executor, unsupported_capability, release_level_change, blocked(jev) | B | X-ARTIF | CX | 4 | 6 | BK0,DMAPC | W2 | T1a | N | N | - | crates/core/src/artifact_kind_*.rs crates/core/tests/artifact_kind_*.rs | negative test accepts a tool proposal | 4 negatives return the named reason offline |
| BKNL | Live denied-kind negatives on real Core dry-run | B | L-E2E | CL | 2 | 3 | CMP,Q1r | W2 | T1a | N | N | - | e2e-core/** demo/** | live negative passes a denied kind | 4 negatives labelled by the engine; no publish |
| BKX | Dispatch in change_compiler to artifact_kind modules | B | X-COMPILE | CX | 4 | 6 | DMAPC,BK0 | W2 | T1a | N | N | - | crates/core/src/change_compiler.rs crates/core/tests/change_compiler.rs | dispatch test fails for an unregistered kind | new kinds register without editing compiler logic |
| Q1 | E2E-THREAD-01 on the Rust shell; Python host becomes regression twin; negatives | Q | L-E2E | CL | 5 | 8 | MEM1,V3r,K5a,IN0,Q1r,E2,K3,E3b | W2 | T1a | Y | N | - | e2e-core/** demo/** | ratchet step 1 stays stand-in | 10 steps with host=rust; negatives green; resume-after-kill |
| REV2 | Independent review wave (Codex) of SEAM-1 seam PRs: JWT, idempotency, hash, egress, loops 2 and 3 | D | X-REV | CX | 8 | 12 | - | W2 | T1a | N | N | - | docs/reviews/codex/** | review-closure script exits 1 while any finding is open | reviews SEAM-1 train tag; findings closed; opportunistic, gates nothing |
| TW1 | Tripwire TW-1: K2 live on the real image | G | L-GOV | CL | 1 | 1 | K2 | W2 | T1a | N | N | - | docs/reports/gates/** | tripwire script fails with no receipt | same key twice gives one run; scout receipt with tokens and cost |
| TW2 | Tripwire TW-2: E5L suite green on Rust server with roleplay scout | G | L-GOV | CL | 1 | 1 | E5L | W2 | T1a | N | N | - | docs/reports/gates/** | tripwire script fails with no receipt | verdict recorded |
| TW3 | Tripwire TW-3: at least 6 of 10 ratchet steps hosted by Rust shell | G | L-GOV | CL | 1 | 1 | E2,V2,H1 | W2 | T1a | N | N | - | docs/reports/gates/** | tripwire script counts host=python steps | verdict recorded |
| CF1 | Contract freeze 1: freeze C-3, C-8, C-9, C-10 (after GT05) and C-4, C-5, C-6 (after TW-1, E1, E5L) | C | L-GOV | CL | 2 | 3 | GT05,TW1,E1,E5L | W2 | T1a | N | N | - | contracts/engine-steps/** docs/reports/gates/** | digest pin test fails for a changed draft | frozen digests of C-3, C-4, C-5, C-6, C-8, C-9, C-10 published; CONTRACT-CHANGE stanza rules active; a changed draft fails the digest pin |
| GT1A | Gate T1a: ratchet on Rust shell; RG-2, RG-3; kinds proven: prompt, eval_suite, denied-kind negatives; approval simulated by default; roleplay replay on E0 | Q | L-GOV | CL | 1 | 2 | Q1,CRV2,GT05,BKNL,CF1 | W2 | T1a | Y | N | - | docs/reports/gates/** | gate script fails on a stand-in step | 3 recorded runs give identical command sequence and candidate_hash; honesty test 2 green; step 8 labelled simulated unless H1r ran; 0 asks needed |
| AUS | U21 authority state-machine stand-in inside seams/crates/authority | H | L-AUTH | CL | 5 | 8 | E1 | W2 | T1a | N | N | - | seams/crates/authority/** | state test allows approve without both gates | all transitions covered; label authority=claude-standin |
| CRV2 | Independent Claude review of SEAM-1 PRs (JWT, idempotency, hash, egress; loops 2 and 3) | D | L-GOV | CL | 8 | 12 | K3 | W2 | T1a | N | N | - | docs/reviews/claude/** | review-closure script exits 1 while any finding is open | findings closed; reviewer differs from author |
| RVC2 | Claude review of Codex T1a-T1b work (optional) | D | L-GOV | CL | 4 | 6 | ~DEVAL,~DPL2,~BKN,~DPIPE,~DAUTH,~DPGc | W2 | T1a | N | N | - | docs/reviews/claude/** | review script lists unreviewed Codex commits | review script exits 0: every Codex commit of T1a-T1b carries a reviewer id different from the author (optional) |
| TRN2 | Claude consolidation train integrator for W2: lane merges in dependency order, one PR per 25 to 35 lane-hours, restack rule, local receipt | G | L-GOV | CL | 8 | 12 | - | W2 | T1a | N | N | - | scripts/gov/** | train script fails when a lane branch is out of order | trains merged with receipts; stacked trains restacked within one fast gate |
| TRX2 | Codex train integrator for W2: lane merges into one train PR per 25 to 35 lane-hours, restack rule, root gate receipt | G | X-FACADE | CX | 2 | 4 | - | W2 | T1a | N | N | - | Cargo.lock .github/** scripts/verify-local-ci.ps1 | train script fails when a lane branch is out of order | trains merged with root gate receipts |
| DPGc | Backend-generic conformance suite over DurableJobRepository | D | X-CONF | CX | 6 | 10 | DJC | W2 | T1b | N | N | - | crates/core/tests/conformance/** | suite fails on a backend that double-claims | suite green on in-memory reference; PG claim traces from FRZ0 replay offline; PG run is SWC |
| BKF | Flow and compiled-tree kind: propose, validate and compile modules plus goldens (offline) | B | X-ARTIF | CX | 10 | 14 | BK0,DMAPV | W2 | T1b | N | N | - | crates/core/src/artifact_kind_*.rs crates/core/tests/artifact_kind_*.rs | flow compile test fails on add-flow of 4 keys | add-Flow and replace-Flow goldens (2) and 3 queue-order cases green offline |
| BKT | Template, policy and prompt-variant kinds: propose, validate, compile (offline) | B | X-ARTIF | CX | 8 | 12 | BK0,DMAPV | W2 | T1b | N | N | - | crates/core/src/artifact_kind_*.rs crates/core/tests/artifact_kind_*.rs | policy compile test fails | goldens for 3 kinds (template, policy, prompt-variant) incl. authorized-field limits, green offline |
| BKD | Decision-model kind (classifier, llm_structured, rule providers): propose, validate, compile (offline) | B | X-ARTIF | CX | 8 | 12 | BK0,DMAPV | W2 | T1b | N | N | - | crates/core/src/artifact_kind_*.rs crates/core/tests/artifact_kind_*.rs | calibration-unchanged test fails | goldens; calibration rule enforced; Jev provider returns blocked(jev) |
| BKA | Agent kind (replace authorized fields) plus cascade prediction expected_derived versus auto_bumped (CAP-19) | B | X-ARTIF | CX | 6 | 9 | BK0,DMAPV | W2 | T1b | N | N | - | crates/core/src/artifact_kind_*.rs crates/core/tests/artifact_kind_*.rs | cascade test: auto_bumped differs from expected_derived | cascade equality asserted on 3 fixtures |
| BKJ | Jev decision-model kind: propose and validate, honest blocked(jev) ending | B | X-ARTIF | CX | 3 | 5 | BK0 | W2 | T1b | N | N | - | crates/core/src/artifact_kind_*.rs crates/core/tests/artifact_kind_*.rs | Jev kind passes as supported | blocked(jev) asserted by the engine in 1 propose and 1 validate case |
| PGC | Conformance suite for the Rust job repository, written by L-PG against the frozen C-7 signature | E | L-PG | CL | 5 | 8 | E1,FRZ0 | W2 | T1b | N | N | - | seams/crates/pg/** | suite fails on a repository that double-claims | suite green on in-memory and PG; claim traces from FRZ0 |
| PGJ | PgJobRepository: claim-next (SKIP LOCKED), lease, fencing delta on existing pulso_jobs, migration 0050+ | E | L-PG | CL | 16 | 24 | MIG0,E1 | W3 | T1b | N | N | - | seams/crates/pg/** migrations/005[0-9]_* | 2 workers claim one job | conformance PGC green; fencing token rejects stale writer; trait is the seams abi trait |
| E6w | Worker loop: lease, heartbeat, fencing, graceful shutdown | E | L-PG | CL | 10 | 14 | PGJ,E2 | W3 | T1b | N | N | - | seams/crates/worker/** | worker keeps a job after lease loss | graceful stop leaves no lease; restart resumes |
| E7 | Triggers: cadence, ingest batch, snapshot registration, coalescing; liveness metric and restart policy | E | L-ENGINE | CL | 8 | 12 | E6w,E4R,P1 | W3 | T1b | N | N | - | seams/crates/engine/** | ingest batch starts no run | an exporter batch starts a run unaided (1 run); stall alarm metric present; compose restart policy set |
| E8s | Durability subset: kill -9, 2 workers, PG restart, lost NOTIFY | E | L-PG | CL | 8 | 12 | E6w,PGC | W3 | T1b | N | N | - | seams/crates/pg/** | kill -9 duplicates an effect | 0 duplicate effects across 4 faults |
| RUN1 | Run control pause and cancel (U34) | E | L-ENGINE | CL | 6 | 9 | E6w | W3 | T1b | N | N | - | seams/crates/engine/** | cancel leaves a running job | pause and cancel each persisted across 1 restart (2 cases) |
| H1b | Durable waiting_human and approval across restart | H | L-AUTH | CL | 3 | 5 | H1,PGJ | W3 | T1b | N | N | - | seams/crates/authority/** | approval lost after restart | approval resumes the run after kill |
| H1n | Human notification adapter (webhook or file sink) for waiting_human with SLA timer | H | L-AUTH | CL | 4 | 6 | H1 | W3 | T1b | N | N | - | seams/crates/authority/** | waiting_human emits no notice | notice emitted within 60 s; SLA breach alarm |
| DPIPE | Pure reducer pipeline swapped in behind the ABI | D | X-FACADE | CX | 6 | 10 | CF0,FRZ0 | W3 | T1b | N | N | - | crates/core/src/pipeline.rs | pipeline transcript differs from linear driver | C-9 transcripts rev1 equal |
| DAUTH | U21 authority state machine (full) | D | X-FACADE | CX | 4 | 8 | CF0,FRZ0 | W3 | T1b | N | N | - | crates/core/src/authority.rs | state test allows approve without gates | all transitions covered; compile_fail guards intact |
| REV3 | Independent review wave (Codex) of PG, worker SQL and fencing | D | X-REV | CX | 5 | 8 | - | W3 | T1b | N | N | - | docs/reviews/codex/** | review-closure script exits 1 while any finding is open | reviews the PG and worker train tag; findings closed; optional, gates nothing |
| GT1B | Gate T1b: kill -9 survives; ingest batch starts a run; Python host demoted (RG-4) | Q | L-GOV | CL | 1 | 2 | E7,E8s,H1b,GT1A,CRV3,H1n,RUN1 | W3 | T1b | Y | N | - | docs/reports/gates/** | gate script fails on a duplicate effect | durable run; label scheduled-ingest; demo/run.ps1 defaults to Rust |
| BKC | Combination bundle: multi-kind, closure, 50-change limit, base precondition digest (CAP-13, 15, 17, 20, 22) | B | X-ARTIF | CX | 8 | 12 | BKF,BKA | W3 | T1b | N | N | - | crates/core/src/artifact_kind_*.rs crates/core/tests/artifact_kind_*.rs | bundle test fails over the 50-change limit | bundle of 3 kinds compiles; limits at 50 and 51 verified |
| BKE | Per-kind evaluation suite emitters and goldens: flow, decision model, agent, policy | B | X-GATE | CX | 10 | 14 | BK0,DEVAL | W3 | T1b | N | N | - | crates/core/src/evaluation_plan.rs crates/core/tests/evaluation_plan.rs | suite emitter fails for a flow queue-order case | one sealed suite per kind (4 kinds) green offline |
| CRV3 | Independent Claude review of PG, worker SQL, fencing, authority | D | L-GOV | CL | 5 | 8 | E8s | W3 | T1b | N | N | - | docs/reviews/claude/** | review-closure script exits 1 while any finding is open | findings closed; reviewer differs from author |
| TRN3 | Claude consolidation train integrator for W3: lane merges in dependency order, one PR per 25 to 35 lane-hours, restack rule, local receipt | G | L-GOV | CL | 5 | 8 | - | W3 | T1b | N | N | - | scripts/gov/** | train script fails when a lane branch is out of order | trains merged with receipts; stacked trains restacked within one fast gate |
| TRX3 | Codex train integrator for W3: lane merges into one train PR per 25 to 35 lane-hours, restack rule, root gate receipt | G | X-FACADE | CX | 2 | 4 | - | W3 | T1b | N | N | - | Cargo.lock .github/** scripts/verify-local-ci.ps1 | train script fails when a lane branch is out of order | trains merged with root gate receipts |
| DORIG | Original dataset path beyond the minimum slice (remaining families, namespaces) | D | X-SRC | CX | 6 | 10 | DORIGm | W3 | T2 | N | N | - | crates/core/src/original_contact_projection.rs crates/core/tests/original_contact_projection.rs | namespace test fails on a mixed query | all remaining original families (the list in the FRZ0 corpus) pass sealed ranking; a mixed-namespace query is rejected in 3 cases |
| DREPLAY | Prequential and frozen replay protocol, replay clock, cohorts (spec 28.4) | D | X-LEARN | CX | 14 | 20 | DWIRE | W3 | T2 | N | N | - | crates/core/src/replay_*.rs crates/core/tests/replay_*.rs | replay test uses data after the cutoff | cohort replay reproducible by digest; goldens from FRZ0 |
| DORACLE | Policy oracle fixtures and security questions, not_evaluable default | D | X-GATE | CX | 8 | 12 | DWIRE | W3 | T2 | N | N | - | crates/core/src/policy_oracle.rs crates/core/tests/policy_oracle.rs | oracle returns pass without fixtures | 12 fixtures and 6 security questions |
| SB1 | U36 sandbox identity semantics | D | X-GATE | CX | 5 | 8 | DGATE | W3 | T2 | N | N | - | crates/core/src/sandbox.rs crates/core/tests/sandbox_identity.rs | identity reuse across runs is accepted | identity per run enforced: reuse across runs rejected in 3 cases; unit tests green |
| RUN2 | Fork semantics over durable_run_events (U34-F, FE) | D | X-LEARN | CX | 8 | 12 | DAUTH | W3 | T2 | N | N | - | crates/core/src/run_fork.rs crates/core/tests/run_fork.rs | fork test shares a parent sequence | fork replays by digest |
| CONF2 | Conformance suites for FakeCore versus bridge goldens and control-api black-box file (offline) | D | X-CONF | CX | 6 | 10 | CF0,FRZ0 | W3 | T2 | N | N | - | crates/core/tests/conformance/** | suite fails when FakeCore drifts from a golden | suite green on goldens; consumed later by swap-in |
| DFAM1 | Signal families 1 to 4: detectors, negatives and discards, fixtures | D | X-SENS | CX | 12 | 18 | DWIRE | W3 | T2 | N | N | - | crates/core/src/detectors/** | family test finds no discard | 4 families each with positive, negative and discard fixtures |
| DFAM2 | Signal families 5 to 8 | D | X-SENS | CX | 12 | 18 | DFAM1 | W3 | T2 | N | N | - | crates/core/src/detectors/** | family test finds no discard | 4 families covered |
| M2f | Full spend governance: per day and tenant, breaker, ledger versus gateway reconciliation | M | L-MODEL | CL | 8 | 10 | GT1B | W4 | T2 | N | N | - | core-bridge/src/pulso_core_runtime/llm/** | breaker test fails to open at the daily cap | ledger equals gateway sum on 3 runs; kill switch under 10 s |
| K4 | JCS content-hash parity and wire drift (CAP-11, CAP-12) | K | L-CLIENT | CL | 6 | 9 | GT1A | W4 | T2 | N | N | - | seams/crates/core-client/** | parity vector fails for a non-ASCII key | all wire vectors of pin c814c2b match |
| K5f | Reconcile full: 409 ambiguity, evaluation_result_lost | K | L-CLIENT | CL | 3 | 4 | K5a | W4 | T2 | N | N | - | seams/crates/core-client/** | 409 idempotency_conflict misclassified | 3 ambiguity cases yield one effect |
| H2 | Authority full flows, rollout and rollback (ProposalRollout), kill-switch race, revoke with step-up issuer | H | L-AUTH | CL | 14 | 20 | AUS,H1b | W4 | T2 | N | N | - | seams/crates/authority/** | rollback test leaves the alias on the candidate | publish, promote, revoke and rollback each leave a receipt; race test green |
| V3L | LLM-driven revision with per-attempt budget | V | L-EVAL | CL | 10 | 14 | V3r,M2f | W4 | T2 | N | N | - | seams/crates/eval/** | third attempt exceeds the budget | 2 attempts within budget; revision cites the failed gate |
| EVE | Eval-suite emitter stand-in from ScenarioCase (U47) in seams/crates/eval | V | L-EVAL | CL | 7 | 10 | V1,FRZ0 | W4 | T2 | N | N | - | seams/crates/eval/** | emitter fails for an unseen scenario shape | suite emitted for 3 non-shipped scenarios; label suite=claude-standin |
| ORC1 | Policy oracle reader with not_evaluable default (stand-in) | V | L-EVAL | CL | 4 | 6 | V2 | W4 | T2 | N | N | - | seams/crates/eval/** | oracle returns pass without fixtures | not_evaluable by default; 5 fixtures |
| RPL1 | Prequential and frozen replay driver with replay clock over cohorts (stand-in for the spec continuous label) | E | L-ENGINE | CL | 9 | 13 | E7 | W4 | T2 | N | N | - | seams/crates/engine/** | replay run uses future data | frozen and prequential runs reproducible by digest |
| SBL | Sandbox identity binding in core-bridge sandbox port (U36 stand-in) | I | L-BRIDGE | CL | 4 | 6 | BRG1 | W4 | T2 | N | N | - | core-bridge/** | sandbox call without identity is accepted | identity bound per run; cross-run use rejected |
| PGQ | PG window for quota and grant (U05) | E | L-PG | CL | 6 | 9 | E6w | W4 | T2 | N | N | - | seams/crates/pg/** | grant window test lets an expired grant pass | quota window enforced across restart |
| BLOB1 | Blob store trait: PG-CAS default plus S3-compatible adapter on MinIO; AWS S3 at TA4 | E | L-PG | CL | 8 | 12 | MIG0 | W4 | T2 | N | N | - | seams/crates/pg/** | blob round trip fails digest check | artifact bodies round trip digest-equal via PG-CAS and MinIO (2 backends) |
| CON1 | Console http provider, SSE with resume, decision panel, debug read routes | I | L-CONSOLE | CL | 16 | 24 | E4R,H1 | W4 | T2 | N | N | - | debug-console/** | console contract test fails on resume | SSE resume after disconnect; decision panel shows gates |
| CON2 | U32 model, eval and memory panels in debug-console | I | L-CONSOLE | CL | 8 | 12 | CON1,E5R | W4 | T2 | N | N | - | debug-console/** | panel test fails with no data | 3 panels (model, eval, memory) render from debug routes with fixture data |
| Q2 | E2E-THREAD-02 chaos matrix, tamper, leakage, tenant tests; delete legacy host | Q | L-E2E | CL | 10 | 14 | GT1B | W4 | T2 | N | N | - | e2e-core/** demo/** | tamper test is accepted | chaos matrix of 8 faults green; legacy host removed |
| Q3 | Observability: metrics contract and alarm table with firing and resolved proof | I | L-OPS | CL | 8 | 12 | E4R | W4 | T2 | N | N | - | docs/contracts/metrics.md local/observability/** | alarm test never fires | alarm fires and resolves within 5 min in the local stack |
| Q3ca | traceparent in control-api (CAP-64) | I | L-CAPI | CL | 2 | 3 | E4R | W4 | T2 | N | N | - | seams/crates/control-api/** contracts/control-api/** | request without traceparent is accepted | traceparent propagated on every control-api hop; request without traceparent refused in 3 routes |
| Q3cc | traceparent in core-client (CAP-64) | I | L-CLIENT | CL | 1 | 2 | E4R,K2 | W4 | T2 | N | N | - | seams/crates/core-client/** | core-client test fails: outbound call without traceparent | traceparent sent on every Core call; 3 calls checked against FakeCore |
| QKG | known_gaps.json by SHA (CAP-64, U53) | Q | L-E2E | CL | 3 | 5 | Q1r | W4 | T2 | N | N | - | e2e-core/** demo/** | report without known_gaps fails | known_gaps listed per SHA in every run report; a report without it fails |
| O1a | Runbooks (8), secrets lifecycle, retention table, redaction canaries | I | L-OPS | CL | 20 | 30 | Q3 | W4 | T2 | N | N | - | docs/runbooks/** docs/security/** | canary secret leaks into a log | 8 runbooks drilled once; canaries clean |
| M5b | Rust JevDecisionPort test against the roleplay JEV server | K | L-CLIENT | CL | 3 | 5 | M5a,K2 | W4 | T2 | N | N | - | seams/crates/model-client/** | port test fails on a 502 | port handles 200, 4xx, 502 |
| RUN3 | Run fork (U34-F and FE) and live fork on durable runs | E | L-ENGINE | CL | 6 | 9 | RUN1 | W4 | T2 | N | N | - | seams/crates/engine/** | fork shares the parent idempotency key | fork run independent of its parent; events linked; 2 forks from one parent differ |
| BKFL | Flow and compiled-tree kind, live: compile, dry-run, evaluate on real arms, approve, publish (own implementation) | B | L-BREADTH | CL | 10 | 14 | BK0,K3,V1 | W4 | T2 | N | N | - | seams/crates/artifacts/** | flow dry-run test fails for add-flow of 4 keys | flow proposal published to staging alias and read back |
| BKTL | Template, policy and prompt-variant kinds, live | B | L-BREADTH | CL | 7 | 10 | BK0,K3,V1 | W4 | T2 | N | N | - | seams/crates/artifacts/** | policy publish test fails | 3 kinds published and read back |
| BKDL | Decision-model kind (non-Jev providers), live, calibration unchanged | B | L-BREADTH | CL | 7 | 10 | BK0,K3,V1 | W4 | T2 | N | N | - | seams/crates/artifacts/** | calibration change is accepted | decision model published; calibration digest unchanged |
| BKAL | Agent kind (authorized fields) with cascade prediction, live | B | L-BREADTH | CL | 7 | 10 | BK0,K3,V1 | W4 | T2 | N | N | - | seams/crates/artifacts/** | cascade mismatch not detected | auto_bumped equals expected_derived on 3 cases |
| BKCL | Combination bundle live: closure, 50-change limit, forced limits at plus and minus 1 (CAP-56) | B | L-BREADTH | CL | 9 | 13 | BKFL,BKAL,BKTL | W4 | T2 | N | N | - | seams/crates/artifacts/** | limit 51 accepted | bundle of 3 kinds published; limits verified at 50 and 51 |
| GT2 | Gate T2: kinds proven: flow, template, policy, decision_model, agent, bundle; chaos, console, spend, replay stand-in | Q | L-GOV | CL | 1 | 2 | BKCL,BKDL,Q2,CON1,H2,M2f,ORC1,RPL1,EVE,CRV4,Q3,O1a | W4 | T2 | N | N | - | docs/reports/gates/** | gate script fails on a missing kind | E2E-THREAD-02 green; third-party reproduction of the GT0 run recorded; kinds-by-families matrix for flow, template, policy, decision_model, agent, bundle complete |
| CRV4 | Independent Claude review of T2 PRs | D | L-GOV | CL | 8 | 12 | Q2 | W4 | T2 | N | N | - | docs/reviews/claude/** | review-closure script exits 1 while any finding is open | findings closed |
| REV4 | Independent review wave (Codex) of T2 PR tags; optional | D | X-REV | CX | 8 | 12 | - | W4 | T2 | N | N | - | docs/reviews/codex/** | review-closure script exits 1 while any finding is open | findings closed |
| ENV11 | Lane scheduler with slot tokens (needs capacity beyond A) | ENV | L-ENV | CL | 4 | 6 | ENV8 | W4 | T2 | N | N | ASK-14 | scripts/env/** | scheduler lets two stacks run | slot tokens: 2 concurrent stacks refused and 1 admitted; test exits 0 |
| ENV12 | Build farm: build container per Rust lane and a second stack (needs hardware, level C) | ENV | L-ENV | CL | 4 | 8 | ENV1,ENV3 | W4 | T2 | N | N | ASK-14 | scripts/env/** | two builds collide on a target dir | 3 concurrent builds with no collision |
| TRN4 | Claude consolidation train integrator for W4: lane merges in dependency order, one PR per 25 to 35 lane-hours, restack rule, local receipt | G | L-GOV | CL | 8 | 12 | - | W4 | T2 | N | N | - | scripts/gov/** | train script fails when a lane branch is out of order | trains merged with receipts; stacked trains restacked within one fast gate |
| TRX4 | Codex train integrator for W4: lane merges into one train PR per 25 to 35 lane-hours, restack rule, root gate receipt | G | X-FACADE | CX | 2 | 4 | - | W4 | T2 | N | N | - | Cargo.lock .github/** scripts/verify-local-ci.ps1 | train script fails when a lane branch is out of order | trains merged with root gate receipts |
| DFAM3 | Signal families 9 to 13 and detector evolution (U31) | D | X-SENS | CX | 14 | 20 | DFAM2 | W4 | T3 | N | N | - | crates/core/src/detectors/** | detector evolution test regresses a metric | 13 families total; evolution gated by sealed holdout |
| DDIAG | Diagnosis SQL (U32 backend) over the sqlite lab | D | X-SENS | CX | 6 | 10 | DFAM1 | W4 | T3 | N | N | - | crates/core/src/local_lab.rs crates/core/tests/local_lab.rs | diagnosis query leaks a row | 5 diagnosis queries with receipts |
| DMEM1 | Learning protocol P4 and P5 temporal rules | D | X-LEARN | CX | 8 | 12 | DREPLAY | W4 | T3 | N | N | - | crates/core/src/memory_temporal_protocol.rs crates/core/tests/memory_temporal_protocol.rs | memory use before publication accepted | 6 temporal rules (P4, P5) each with a red then green test; use before publication rejected |
| DMEM2 | Durable memory and governed use breadth | D | X-LEARN | CX | 9 | 14 | DMEM1 | W4 | T3 | N | N | - | crates/core/src/governed_memory_use.rs crates/core/tests/governed_memory_use.rs | governed use without grant accepted | 10 governed-use cases |
| DSCEN1 | ScenarioFactory and counterfactual proxies | D | X-SCEN | CX | 8 | 12 | DEVAL | W4 | T3 | N | N | - | crates/core/src/scenario_*.rs crates/core/tests/scenario_*.rs | factory output differs by seed | 3 scenario families |
| DSCEN2 | Value kernels (value_model extensions) | D | X-SCEN | CX | 6 | 10 | DSCEN1 | W4 | T3 | N | N | - | crates/core/src/value_model.rs crates/core/tests/value_model.rs | value kernel unit mismatch accepted | 6 value kernels each with 3 unit tests; unit mismatch rejected |
| SB2 | U26 stateful bank sandbox world (real bank stays blocked CAP-41) | D | X-SCEN | CX | 8 | 12 | DSCEN1 | W4 | T3 | N | N | - | crates/core/src/scenario_*.rs crates/core/tests/scenario_*.rs | bank state leaks across runs | stateful world with 6 scenarios |
| DSRC | Additional source adapters (remaining original sources) | D | X-SRC | CX | 8 | 12 | DORIG | W4 | T3 | N | N | - | crates/source-adapters/** | adapter accepts an unsupported source | each remaining source validated on sealed samples |
| DDOC | Spec text, additive amendments, status corrections for CAP-58 and CAP-61 | D | X-DOC | CX | 6 | 10 | DDOC1 | W4 | T3 | N | N | - | docs/IMPLEMENTATION_STATUS.md | status table disagrees with code | status table matches the code at the baseline |
| DSPEC | Spec text for artifact kinds, breadth gates and stand-in swap protocol | D | X-DOC | CX | 4 | 6 | BK0 | W4 | T3 | N | N | - | docs/spec-amendments/codex/** | link test fails for a missing section | 3 amendment files merged (kinds, gates, swap protocol); link test exits 0 |
| TA1 | Local release script by digest, SBOM, audit, deploy manifest | A | L-INFRA | CL | 8 | 12 | IN0 | W4 | TA | N | N | - | infra:** | manifest without digest accepted | release by digest; SBOM and audit in receipt |
| TA2 | Infra deltas: fixtures to pin c814c2b, engine alarms, core-migrate task, ECS Exec | A | L-INFRA | CL | 10 | 16 | Q3,TA1 | W4 | TA | N | N | - | infra:** | infra contract test fails on stale pin | terraform validate and plan -refresh=false exit 0 offline for the 5 deltas (fixtures pin c814c2b, engine alarms, core-migrate task, ECS Exec, release by digest) |
| REV5 | Independent review wave (Codex) of T3 and TA PR tags; optional | D | X-REV | CX | 6 | 10 | - | W5 | T3 | N | N | - | docs/reviews/codex/** | review-closure script exits 1 while any finding is open | findings closed |
| M6 | Rust model transport for the engine (U10): gateway client crate | K | L-CLIENT | CL | 10 | 14 | M2f,K1 | W5 | T3 | N | N | - | seams/crates/model-client/** | transport test fails on a timeout | engine calls the gateway through the Rust client in 1 live run; ledger equals gateway usage within 1 token; timeout returns a typed error |
| BKOL | Tool kind live: executor registration in Pulso-owned runtime factories (bank stays blocked) | B | L-BRIDGE | CL | 8 | 12 | BK0,BKFL | W5 | T3 | N | N | - | core-bridge/** | tool proposal passes with no executor | sandbox tool proposed, dry-run, evaluated, published |
| BKJL | Jev decision-model kind live against the roleplay JEV; real Core side blocked(jev) | B | L-BREADTH | CL | 4 | 6 | BK0,M5a | W5 | T3 | N | N | - | seams/crates/artifacts/** | Jev kind passes as supported | blocked(jev) shown in the report; roleplay JEV path exercised in 1 live case |
| BKEL | Per-kind evaluation suites live (own emitters) for flow, decision model, agent, policy | B | L-EVAL | CL | 8 | 12 | EVE,BKFL,BKDL,BKAL | W5 | T3 | N | N | - | seams/crates/eval/** agent-core-assets/eval-suites/** | suite changed after arms is accepted | 4 sealed per-kind suites (flow, decision model, agent, policy) each run on real arms; mutation after seal rejected |
| CRV5 | Independent Claude review of W5 live breadth and transport: M6, BKOL, BKJL, BKEL, CAMP (RC2, loops 2 and 3) | D | L-GOV | CL | 6 | 9 | M6,BKOL,BKJL,BKEL,CAMP | W5 | T3 | N | N | - | docs/reviews/claude/** | review-closure script exits 1 while any finding is open | findings closed; reviewer differs from author; gates GT3 |
| DUCK | DuckDB lab replacement for sqlite lab | E | L-CAPI | CL | 10 | 14 | E5R | W5 | T3 | N | N | - | seams/crates/control-api/** contracts/control-api/** | query result differs from sqlite | same QueryReceipts on 20 queries |
| CAMP | Campaigns and alternatives portfolio | V | L-EVAL | CL | 10 | 16 | V3L | W5 | T3 | N | N | - | seams/crates/eval/** | campaign shares a budget | campaign of 3 alternatives with do_nothing |
| P3 | Real Product source: read-only snapshot, PL-C4 guard in deployed path | P | L-PLAT | CL | 8 | 12 | P1 | W5 | T3 | N | N | ASK-25 | platform-contract/** | guard test allows a write grant | inbound read-only run on the real source ends at insufficient_* (1 run); a write grant is refused |
| P4 | Phase 2 readiness: superset profile, target registry and alias mapping | P | L-PLAT | CL | 8 | 14 | PX0,P1 | W5 | T3 | N | N | - | platform-contract/** | profile test lights an absent detector | superset profile tests green |
| WIKI | Wiki free exploration and transform | V | L-MEM | CL | 8 | 12 | E5R | W5 | T3 | N | N | - | seams/crates/memory/** | wiki write without grant accepted | 20 exploration queries within grants return receipts; 3 out-of-grant queries rejected |
| DMEMC | Memory breadth live: durable head, confirm and contradict at scale | V | L-MEM | CL | 8 | 12 | MEM1,E7 | W5 | T3 | N | N | - | seams/crates/memory/** | memory head lost after restart | durable head survives kill -9 |
| GT3 | Gate T3: kinds proven add tool, Jev(blocked), bundle with tool; stand-in retirement RG-5 decided per swap-in | Q | L-GOV | CL | 1 | 2 | BKOL,BKJL,BKEL,M6,CAMP,DMEMC,WIKI,CRV5 | W5 | T3 | N | N | - | docs/reports/gates/** | gate script fails on a missing kind | kinds-by-families matrix has 0 empty cells, each cell with a receipt id; Jev row shows blocked(jev); tool row published on a staging alias; RG-5 decided per swap-in |
| SWA | Swap-in: adopt Codex compile, gate, recompute, validation behind the step schema after conformance | E | L-ENGINE | CL | 6 | 9 | GT1A,~DMAPC,~DGATE,~DVREC,~DMAPV,~WDX | W5 | T3 | N | N | - | seams/crates/swap/** | conformance test fails when outputs differ from the stand-in on FRZ0 cases | identical results on 20 cases; stand-in retired only by GT3 decision |
| SWP | Swap-in: adopt Codex pipeline reducer and authority state machine | E | L-ENGINE | CL | 5 | 8 | GT1A,~DPIPE,~DAUTH | W5 | T3 | N | N | - | seams/crates/swap/** | transcript differs from the linear driver | C-9 transcripts equal; authority transitions equal |
| SWC | Swap-in: run Codex conformance suite on PG | E | L-PG | CL | 2 | 3 | GT1B,~DPGc,~CONF2 | W5 | T3 | N | N | - | seams/crates/pg/** | suite fails on PG | Codex conformance suites run on PG; pass counts and PG version recorded in the PR body |
| SWB | Swap-in: adopt Codex per-kind modules and goldens against the live kinds | B | L-BREADTH | CL | 6 | 9 | GT2,~BKF,~BKT,~BKD,~BKA,~BKC,~BKE,~BKJ,~BKN,~BKX | W5 | T3 | N | N | - | seams/crates/artifacts/** | golden differs from the live compile output | all Codex goldens green against live output |
| SWL | Swap-in: adopt Codex replay, oracle, detectors and memory breadth | E | L-ENGINE | CL | 5 | 8 | GT2,~DREPLAY,~DORACLE,~DFAM3,~DMEM2,~DSCEN2,~DORIG | W5 | T3 | N | N | - | seams/crates/swap/** | adoption test differs from stand-in | equal on FRZ0 cohorts |
| RVC3 | Claude review of Codex T2-T3 work (optional) | D | L-GOV | CL | 5 | 8 | ~DREPLAY,~DORACLE,~DFAM3,~DMEM2,~BKF,~BKC | W5 | T3 | N | N | - | docs/reviews/claude/** | review script lists unreviewed Codex commits | review script exits 0: every Codex commit of T2-T3 carries a reviewer id different from the author (optional) |
| TRN5 | Claude consolidation train integrator for W5: lane merges in dependency order, one PR per 25 to 35 lane-hours, restack rule, local receipt | G | L-GOV | CL | 6 | 10 | - | W5 | T3 | N | N | - | scripts/gov/** | train script fails when a lane branch is out of order | trains merged with receipts; stacked trains restacked within one fast gate |
| TA3 | First real terraform plan and fix cycle | A | L-INFRA | CL | 10 | 18 | TA0,TA2 | W5 | TA | N | N | ASK-17,ASK-18 | infra:** | plan fails on IAM or KMS | terraform plan for staging exits 0 with 0 unexpected destroys; saved plan sha recorded |
| TA4 | First slice on staging (control-api, worker, PG) at the T1b gate | A | L-INFRA | CL | 8 | 14 | TA3,GT1B | W5 | TA | N | N | ASK-17,ASK-21 | infra:** | apply of the saved plan fails | slice answers health; human-approved apply |
| TA5 | Core, gateway and exporters on AWS; first check agent-core c814c2b Dockerfile and runbook | A | L-INFRA | CL | 10 | 20 | TA4 | W5 | TA | N | N | ASK-17 | infra:** | thread against staging fails | 10-step thread runs against the 3 staging URLs (control-api, Core, gateway): ratchet exits 0 with target=staging in every step |
| TA6 | Alarm destinations, budgets, kill-switch and restore drills, soak | A | L-INFRA | CL | 20 | 32 | TA4 | W5 | TA | N | N | ASK-19,ASK-20 | infra:** | alarm mailbox unconfirmed | alarm fired and resolved; restore drill |
| CRV6 | Independent Claude review of the AWS slice: IAM, KMS, alarms, apply plan (RC2, loops 2 and 3) | D | L-GOV | CL | 5 | 8 | TA4 | W5 | TA | N | N | ASK-17 | docs/reviews/claude/** | review-closure script exits 1 while any finding is open | findings closed; reviewer differs from author; gates GTA |
| LAB28 | Lab session lifecycle on staging (U28): create, TTL, revoke, tenant isolation | A | L-INFRA | CL | 6 | 10 | TA4 | W5 | TA | N | N | ASK-17 | infra:** | cross-tenant lab session accepted | isolation test green |
| GTA | Gate DEMO-3: the same demo thread against AWS staging URLs; kinds proven as GT1B | Q | L-GOV | CL | 1 | 2 | TA5,TA6,GT1B,CRV6 | W5 | TA | N | N | - | docs/reports/gates/** | gate script fails on a local URL | thread against staging; alarm fired and resolved; rollback drill; prod untouched |
| O1b | Threat model, independent security review, remaining ops | I | L-OPS | CL | 20 | 30 | O1a | W5 | T5 | N | N | - | docs/runbooks/** docs/security/** | threat model has no abuse case | review findings closed |
| T5a | Load, chaos at spec numbers, 72h soak on compressed clock | Q | L-E2E | CL | 30 | 45 | Q2 | W5 | T5 | N | N | - | e2e-core/** demo/** | soak run breaks at hour 1 | 72h compressed soak with 0 duplicate effects |
| T5b | Security review fixes and retention and restore drills | Q | L-OPS | CL | 15 | 25 | O1b | W5 | T5 | N | N | - | docs/runbooks/** docs/security/** | restore drill fails | restore drill within the stated RPO and RTO (2 numbers measured) |
| T5c | Browser and a11y matrix, DoD pack, third-party reproduction | Q | L-E2E | CL | 15 | 20 | Q2 | W5 | T5 | N | N | - | e2e-core/** demo/** | a11y check finds a blocker | spec DoD checklist: every item has an evidence link and the check script exits 0 with 0 blank items; third-party reproduction of GT0 recorded |

## Annex B. The checker (extracted from this file and run on it)

`python check_plan.py PLAN.md [IMPROVEMENT_ENGINE_REPO] [INFRA_REPO]` parses the table above, the `FROZEN:` line, the `owners`, `newpaths` and `numbers` blocks of annex D and the ASK table of section 14, and checks: unique ids; no dangling deps; acyclic; tier and wave monotone along hard edges; one owner per lane; non-empty `first_red` (never a review checklist) and `acceptance` (a number, exit code, named artefact or verdict); every `needs` names an existing ASK; the independence rule (counts printed); gates free of Codex and swap-in ancestors; GT0, GT05, GT1A, GT1B, GT2, GT3 have no ancestor that needs an ask; the `critical` column (float at most 4 h to GT1B); the demo path equals the ancestors of GT0, is Claude-only, has no ENV-stream WP and excludes M5a; Claude 70-80% and Codex 20-30% overall and through T1b; every WP `paths` glob resolves inside its lane; every planned new path resolves to its lane; with the repo arguments every tracked path of improvement-engine at 853b029 and every path of infra `origin/main` has exactly one owner; finally the `numbers` block of this file must equal the computed values (so prose and checker cannot differ).

```python
#!/usr/bin/env python3
"""check_plan.py - machine checker of the Pulso real-system plan (final, v5).

Usage:  python check_plan.py PLAN.md [IMPROVEMENT_ENGINE_REPO] [INFRA_REPO]
        (PLAN.md may also be wp_table.csv-derived; the table, the FROZEN line, the `owners`,
        `newpaths`, `numbers` blocks and the ASK table are read from the plan file itself.)
Exit code 0 = PASS, non-zero = at least one violation (assert message names it).
With the repo arguments it also proves that every tracked path of improvement-engine main
(and every path of infra origin/main) has exactly one lane owner by the most specific glob.
"""
import re, sys, math, collections, subprocess

TIERS = 'T0 T0.5 T1a T1b T2 T3 TA T5'.split()
TI = {t: i for i, t in enumerate(TIERS)}
PACK = 'G0f G0gr CONTR CF0 FRZ0 BK0'.split()          # wave-0 enabling pack (Claude), published for Codex
DEFAULT_GATES = 'GT0 GT05 GT1A GT1B GT2 GT3'.split()    # must be reachable with every ask unanswered
USER_GATED = {'GT05m': 'model rung-up needs a local-model download (ASK-7)',
              'GTA': 'real AWS staging needs the AWS asks (ASK-17..21)'}
STANDIN = 'CMP GSI STP1 AUS PGC EVE ORC1 RPL1 SBL'.split()          # Claude stand-ins of Codex semantics
LIVEKIND = 'BKFL BKTL BKDL BKAL BKCL BKJL BKOL BKEL'.split()        # Claude live per-kind WPs
CAP = {'A': (14, 18), 'B': (18, 24), 'C': (35, 45)}                  # lane-hours per session, ASSUMPTIONS (LVL-A/B/C)
WAVES = ['W0', 'W1', 'W2', 'W3', 'W4', 'W5']


def parse(txt):
    lines = txt.splitlines()
    hi = next(i for i, l in enumerate(lines) if l.startswith('| id | name |'))
    hdr = [c.strip() for c in lines[hi].strip().strip('|').split('|')]
    rows = []
    for l in lines[hi + 2:]:
        if not l.startswith('|'):
            break
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        assert len(c) == len(hdr), ('column count', c[0], len(c), len(hdr))
        rows.append(dict(zip(hdr, c)))
    return rows


FENCE = chr(96) * 3


def block(txt, name):
    m = re.search(FENCE + name + r'\n(.*?)' + FENCE, txt, re.S)
    assert m, 'missing block ' + name
    return m.group(1)


def conv(p):
    o = ''; i = 0; b = 0
    while i < len(p):
        c = p[i]
        if p.startswith('**', i):
            o += '.*'; i += 2; continue
        if c == '*': o += '[^/]*'
        elif c == '{': o += '(?:'; b += 1
        elif c == '}': o += ')'; b -= 1
        elif c == ',' and b: o += '|'
        elif c == '.': o += r'\.'
        else: o += c
        i += 1
    return re.compile('^' + o + '$')


def rep(g):
    """a representative concrete path of a glob (for location-inside-lane checks)"""
    g = g.replace('**', 'x/y')
    g = re.sub(r'\{([^,}]*)[^}]*\}', r'\1', g)
    g = re.sub(r'\(([^|)]*)[^)]*\)', r'\1', g)
    g = re.sub(r'\[(.)[^\]]*\]', r'\1', g)
    return g.replace('*', 'x')


def analyze(txt, repo=None, infra=None, out=print, check_numbers=True, critical_out=None):
    rows = parse(txt)
    by = {r['id']: r for r in rows}
    assert len(by) == len(rows), 'duplicate id'
    F = set(re.search(r'^FROZEN: (.*)$', txt, re.M).group(1).split())
    lo = lambda r: int(r['hours_low']); hi = lambda r: int(r['hours_high']); mid = lambda r: (lo(r) + hi(r)) / 2
    deps = lambda r: [d for d in r['deps'].split(',') if d != '-']
    hard = lambda r: [d for d in deps(r) if d[0] != '~']
    opt = lambda r: [d[1:] for d in deps(r) if d[0] == '~']
    needs = lambda r: [d for d in r['needs'].split(',') if d != '-']
    asks = set(re.findall(r'^\| (ASK-\d+) \|', txt, re.M))
    assert asks, 'no ASK table'
    bare = []
    for r in rows:
        assert lo(r) <= hi(r) and lo(r) > 0, ('hours', r['id'])
        assert r['critical'] in ('Y', 'N') and r['demo_path'] in ('Y', 'N'), r['id']
        assert r['owner'] in ('CL', 'CX') and r['wave'] in WAVES and r['tier'] in TI, r['id']
        assert r['first_red'] and r['acceptance'] and r['paths'], ('empty cell', r['id'])
        assert not r['first_red'].lower().startswith('review checklist'), ('first_red is not a RED', r['id'])
        if not re.search(r'\d|green|exit|reject|equal|match|publish|merged|closed|digest|label|recorded|survive|receipt|pass|fail|refus|enforc|fire|resolv|answer|compil|valid|accepted|read back|resum|stop|replay|hash|signed|identical', r['acceptance'], re.I): bare.append(r['id'])
        for d in hard(r) + opt(r):
            assert d in by, ('dangling dep', r['id'], d)
        for d in hard(r):
            assert TI[by[d]['tier']] <= TI[r['tier']] and by[d]['wave'] <= r['wave'], ('monotone', r['id'], d)
        for n in needs(r):
            assert n in asks, ('unknown ask', r['id'], n)
    assert not bare, ('bare acceptance cells (no number, exit code, named artefact or verdict)', bare)
    # acyclic
    order = []; seen = set()
    def vis(n, p=()):
        assert n not in p, 'cycle ' + n
        if n in seen: return
        for d in hard(by[n]): vis(d, p + (n,))
        seen.add(n); order.append(n)
    for n in by: vis(n)
    lane = collections.defaultdict(set)
    for r in rows: lane[r['lane']].add(r['owner'])
    assert all(len(v) == 1 for v in lane.values()), 'lane with two owners'
    own_of = {l: next(iter(v)) for l, v in lane.items()}
    N = collections.OrderedDict()
    P = lambda *a: out(' '.join(str(x) for x in a))
    # ---- independence
    c2x = [(r['id'], d) for r in rows if r['owner'] == 'CL' for d in hard(r) if by[d]['owner'] == 'CX']
    x2c = [(r['id'], d) for r in rows if r['owner'] == 'CX' for d in hard(r) if by[d]['owner'] == 'CL' and d not in F]
    x2f = [(r['id'], d) for r in rows if r['owner'] == 'CX' for d in hard(r) if by[d]['owner'] == 'CL' and d in F]
    sw = [(r['id'], d) for r in rows for d in opt(r)]
    assert all(by[a]['owner'] == 'CL' and by[d]['owner'] == 'CX' for a, d in sw), 'optional edge must be Claude swap-in <- Codex'
    assert all(by[f]['owner'] == 'CL' for f in F), 'FROZEN must be Claude artifacts'
    assert not c2x and not x2c, ('independence violated', c2x, x2c)
    N['c2x_hard'] = len(c2x); N['x2c_nonfrozen'] = len(x2c); N['x2frozen'] = len(x2f); N['swapin_edges'] = len(sw)
    P('Claude->Codex hard edges:', len(c2x), '| Codex->Claude edges to non-frozen:', len(x2c), '| Codex->frozen:', len(x2f), '| optional swap-in edges:', len(sw))
    def anc(n, a=None):
        a = set() if a is None else a
        for d in hard(by[n]):
            if d not in a: a.add(d); anc(d, a)
        return a
    def cpm(g):
        A = anc(g) | {g}; ES = {}
        for n in [n for n in order if n in A]: ES[n] = max([ES[d] + mid(by[d]) for d in hard(by[n])] + [0])
        end = ES[g] + mid(by[g]); LF = {n: end for n in A}
        for n in reversed([n for n in order if n in A]):
            for d in hard(by[n]): LF[d] = min(LF[d], LF[n] - mid(by[n]))
        return A, ES, end, {n: LF[n] - mid(by[n]) - ES[n] for n in A}
    gates = [r['id'] for r in rows if r['id'].startswith('GT')]
    for g in DEFAULT_GATES + list(USER_GATED): assert g in gates, ('missing gate', g)
    depth = {}; chain = {}
    for g in gates:
        A = anc(g)
        assert not [x for x in A if (by[x]['owner'] == 'CX' and x not in F) or opt(by[x])], ('gate depends on Codex or swap-in', g)
        A2, ES, end, fl = cpm(g)
        n = g; ch = [g]
        while hard(by[n]):
            n = max(hard(by[n]), key=lambda d: ES[d] + mid(by[d])); ch.append(n)
        depth[g] = end; chain[g] = list(reversed(ch))
        P(g, 'serial depth %.1f h' % end, '| gate ancestors', len(A), '(all Claude or frozen) | chain', ' > '.join(chain[g]))
        N['anc_' + g] = len(A)
        N['chain_' + g] = ' > '.join(chain[g])
        N['hours_' + g] = '%d-%d' % (sum(lo(by[x]) for x in A | {g}), sum(hi(by[x]) for x in A | {g}))
        N['depth_' + g] = '%.1f' % end
    # default gates reachable with every ask unanswered
    for g in DEFAULT_GATES:
        bad = [x for x in anc(g) | {g} if needs(by[x])]
        assert not bad, ('gate needs a user ask', g, bad)
    for g, why in USER_GATED.items():
        assert [x for x in anc(g) | {g} if needs(by[x])], ('user-gated gate has no ask', g)
    P('default-reachable gates (no ask in any ancestor):', ' '.join(DEFAULT_GATES), '| user-gated:', ' '.join(USER_GATED))
    # critical column
    A, ES, end, fl = cpm('GT1B')
    crit = {n for n in A if fl[n] <= 4}
    if critical_out is not None:
        critical_out.extend(sorted(crit)); return None
    assert {r['id'] for r in rows if r['critical'] == 'Y'} == crit, 'critical column mismatch'
    ncrit = sum(r['critical'] == 'Y' for r in rows); hcrit = sum(mid(by[n]) for n in A if fl[n] <= 4)
    N['critical_wps'] = ncrit; N['critical_hours_mid'] = '%.1f' % hcrit
    P('critical to GT1B', ncrit, 'WPs, midpoint hours', hcrit)
    # demo path = exact ancestor set of GT0, Claude-only, closed, no ENV stream, no Jev, no ask
    D = {r['id'] for r in rows if r['demo_path'] == 'Y'}
    assert D == anc('GT0') | {'GT0'}, ('demo_path != ancestors of GT0', D ^ (anc('GT0') | {'GT0'}))
    assert all(by[n]['owner'] == 'CL' and not opt(by[n]) and by[n]['stream'] != 'ENV' for n in D), 'demo path must be Claude-only, no ENV stream'
    assert 'M5a' not in D, 'M5a must be out of the GT0 ancestors'
    # ---- sums, splits
    def S(f): return sum(lo(r) for r in rows if f(r)), sum(hi(r) for r in rows if f(r))
    def share(f):
        a = S(f); b = S(lambda r: f(r) and r['owner'] == 'CL')
        return a, b, '%.1f%% / %.1f%%' % (100 * b[0] / a[0], 100 * b[1] / a[1])
    a, b, s = share(lambda r: True)
    for k, f in (('all', lambda r: True), ('t1b', lambda r: TI[r['tier']] <= 3)):
        aa, bb, ss = share(f)
        assert 70 <= 100 * bb[0] / aa[0] <= 80 and 70 <= 100 * bb[1] / aa[1] <= 80, ('Claude share outside 70-80', k, ss)
        assert 20 <= 100 * (aa[0] - bb[0]) / aa[0] <= 30 and 20 <= 100 * (aa[1] - bb[1]) / aa[1] <= 30, ('Codex share outside 20-30', k, ss)
        N[k + '_total'] = '%d-%d' % aa; N[k + '_claude'] = '%d-%d' % bb; N[k + '_codex'] = '%d-%d' % (aa[0] - bb[0], aa[1] - bb[1])
        N[k + '_share_claude'] = ss; N[k + '_mid'] = '%.0f' % ((aa[0] + aa[1]) / 2)
        N[k + '_share_codex'] = '%.1f%% / %.1f%%' % (100 * (aa[0] - bb[0]) / aa[0], 100 * (aa[1] - bb[1]) / aa[1])
        P('split', k, 'total %d-%d | Claude %d-%d | Claude share %s' % (aa + bb + (ss,)))
    N['wps'] = len(rows); N['lanes'] = len(lane); N['lanes_cl'] = sum(v == 'CL' for v in own_of.values()); N['lanes_cx'] = sum(v == 'CX' for v in own_of.values())
    N['churn_total'] = '%.0f' % (1.1 * (a[0] + a[1]) / 2)
    P('WPs', len(rows), 'lanes', len(lane), '(CL %d, CX %d)' % (N['lanes_cl'], N['lanes_cx']), '| all', share(lambda r: True))
    for t in TIERS:
        sh = share(lambda r: r['tier'] == t); N['tier_' + t] = '%d-%d (CX %d-%d)' % (sh[0] + (sh[0][0] - sh[1][0], sh[0][1] - sh[1][1]))
        N['tiershare_' + t] = '%.1f' % (100 * sh[1][0] / sh[0][0]) if sh[0][0] else '-'
        P('tier', t, N['tier_' + t], 'Claude share of lows', N['tiershare_' + t])
    for w in WAVES:
        sh = share(lambda r: r['wave'] == w)
        nw = sum(r['wave'] == w for r in rows); lw = {r['lane'] for r in rows if r['wave'] == w}
        cl = sum(own_of[l] == 'CL' for l in lw)
        N['wave_' + w] = '%d-%d (%s; %d WPs; %d lanes: %d CL + %d CX)' % (sh[0] + (sh[2], nw, len(lw), cl, len(lw) - cl))
        P('wave', w, N['wave_' + w])
    dm = S(lambda r: r['id'] in D); ev = S(lambda r: r['id'] not in D)
    N['demo_wps'] = len(D); N['demo_hours'] = '%d-%d' % dm; N['demo_mid'] = '%.1f' % ((dm[0] + dm[1]) / 2)
    N['demo_pct'] = '%.1f%% / %.1f%%' % (100 * dm[0] / (dm[0] + ev[0]), 100 * dm[1] / (dm[1] + ev[1]))
    N['evolution_hours'] = '%d-%d' % ev
    P('demo path', dm, 'WPs', len(D), 'evolution', ev, N['demo_pct'])
    # independence cost of the rule
    sa = S(lambda r: r['id'] in STANDIN); sb = S(lambda r: r['id'] in LIVEKIND)
    N['indep_cost'] = '%d-%d' % (sa[0] + sb[0], sa[1] + sb[1]); N['indep_cost_standins'] = '%d-%d' % sa; N['indep_cost_livekind'] = '%d-%d' % sb
    P('independence cost (Claude stand-ins + live per-kind WPs)', N['indep_cost'])
    pk = S(lambda r: r['id'] in PACK); N['pack_hours'] = '%d-%d' % pk; N['pack_mid'] = '%.1f' % ((pk[0] + pk[1]) / 2)
    # ---- sessions model
    def sess(h, dep, c):
        cl, ch = CAP[c]; cc = (cl + ch) / 2
        f = 1.10 * dep / 7.5
        return max(1.10 * h / cc, f), max(1.10 * h / ch, f), max(1.10 * h / cl, f)
    def sfmt(h, dep, c):
        x, y, z = sess(h, dep, c); return '%.1f (%.1f-%.1f)' % (x, y, z)
    for g in DEFAULT_GATES + list(USER_GATED):
        AA = anc(g) | {g}; h = sum(mid(by[x]) for x in AA)
        for c in 'ABC': N['sess_%s_%s' % (g, c)] = sfmt(h, depth[g], c)
    AA = anc('GT0') | {'GT0'} | set(PACK); h = sum(mid(by[x]) for x in AA)
    dep = max(depth['GT0'], max(cpm(p)[2] for p in PACK))
    N['demo_pack_mid'] = '%.1f' % h
    for c in 'ABC': N['sess_GT0pack_' + c] = sfmt(h, dep, c)
    for g in DEFAULT_GATES + list(USER_GATED):
        P('sessions', g, 'depth', N['depth_' + g], 'A', N['sess_%s_A' % g], 'B', N['sess_%s_B' % g], 'C', N['sess_%s_C' % g])
    P('sessions GT0+pack', 'A', N['sess_GT0pack_A'], 'B', N['sess_GT0pack_B'], 'C', N['sess_GT0pack_C'])
    # ---- PRs per wave per team (ceil(mid/30)), lanes, ASAP width
    for w in WAVES:
        for t in ('CL', 'CX'):
            m = sum(mid(r) for r in rows if r['wave'] == w and r['owner'] == t)
            N['prs_%s_%s' % (t, w)] = math.ceil(m / 30) if m else 0
    N['prs_CL'] = ' '.join(str(N['prs_CL_' + w]) for w in WAVES); N['prs_CX'] = ' '.join(str(N['prs_CX_' + w]) for w in WAVES)
    N['prs_total_CL'] = sum(N['prs_CL_' + w] for w in WAVES); N['prs_total_CX'] = sum(N['prs_CX_' + w] for w in WAVES)
    P('PRs per wave Claude', N['prs_CL'], '(%d) | Codex' % N['prs_total_CL'], N['prs_CX'], '(%d)' % N['prs_total_CX'])
    lvl = {}
    for n in order: lvl[n] = 1 + max([lvl[d] for d in hard(by[n])] + [0])
    cnt = collections.Counter(lvl.values()); N['asap_width'] = max(cnt.values()); N['asap_levels'] = max(cnt)
    N['lanes_per_wave'] = ' '.join(str(len({r['lane'] for r in rows if r['wave'] == w})) for w in WAVES)
    P('width: lanes per wave', N['lanes_per_wave'], '| ASAP level width', N['asap_width'], 'over', N['asap_levels'], 'levels')
    # ---- lane table
    N['lane_table'] = ';'.join('%s:%d:%d-%d' % (l, sum(r['lane'] == l for r in rows), sum(lo(r) for r in rows if r['lane'] == l), sum(hi(r) for r in rows if r['lane'] == l)) for l in sorted(lane))
    # ---- paths: location inside lane
    own = block(txt, 'owners')
    RU = [(l.split(': ')[0], conv(g), len(g.replace('*', ''))) for l in own.splitlines() if l.strip() for g in l.split(': ', 1)[1].split(' ; ')]
    def owner(f):
        m = sorted([(s, l) for l, r, s in RU if r.match(f)], reverse=True)
        return None if not m or (len(m) > 1 and m[0][0] == m[1][0] and m[0][1] != m[1][1]) else m[0][1]
    assert {l.split(': ')[0] for l in own.splitlines() if l.strip()} >= set(lane), 'lane without path map'
    nexp = 0
    for r in rows:
        if r['paths'] == '@lane': continue
        nexp += 1
        for g in r['paths'].split():
            assert owner(rep(g)) == r['lane'], ('WP path outside its lane', r['id'], r['lane'], g, owner(rep(g)))
    N['wps_explicit_paths'] = nexp
    P('paths: %d WPs with explicit globs all resolve inside their lane; %d use @lane' % (nexp, len(rows) - nexp))
    npb = [l for l in block(txt, 'newpaths').splitlines() if l.strip()]
    for l in npb:
        p, ln = [x.strip() for x in l.split('->')]
        assert owner(p) == ln, ('planned new path has wrong owner', p, ln, owner(p))
    N['newpaths_checked'] = len(npb)
    P('planned new paths checked:', len(npb))
    if repo:
        fs = [f for f in subprocess.check_output(['git', '-C', repo, 'ls-files']).decode().split('\n') if f]
        if infra:
            fs += ['infra:' + f for f in subprocess.check_output(['git', '-C', infra, 'ls-tree', '-r', '--name-only', 'origin/main']).decode().split('\n') if f]
        bad = [f for f in fs if not owner(f)]
        P(len(fs), 'tracked paths (repo + infra origin/main),', len(bad), 'unowned or tied'); assert not bad, bad[:10]
        N['tracked_paths'] = len(fs)
    # ---- numbers block of the document must equal the computed values
    if not check_numbers:
        return N
    nb = {}
    for l in block(txt, 'numbers').splitlines():
        if l.strip():
            k, v = l.split(' = ', 1); nb[k.strip()] = v.strip()
    comp = {k: str(v) for k, v in N.items() if k not in ('tracked_paths',)}
    diff = {k: (nb.get(k), comp.get(k)) for k in set(nb) | set(comp) if nb.get(k) != comp.get(k) and k != 'tracked_paths'}
    assert not diff, ('numbers block differs from computation', diff)
    P('numbers block: %d values equal the computation' % len(nb))
    return N


if __name__ == '__main__':
    txt = open(sys.argv[1], encoding='utf-8').read()
    analyze(txt, sys.argv[2] if len(sys.argv) > 2 else None, sys.argv[3] if len(sys.argv) > 3 else None)
    print('PASS')
```

## Annex C. Checker output on this file

```text
Claude->Codex hard edges: 0 | Codex->Claude edges to non-frozen: 0 | Codex->frozen: 30 | optional swap-in edges: 40
GT0 serial depth 65.5 h | gate ancestors 26 (all Claude or frozen) | chain DC0 > ED0 > SMAP > Q1r > INT0 > GT0
GT05 serial depth 67.0 h | gate ancestors 40 (all Claude or frozen) | chain DC0 > ED0 > SMAP > Q1r > INT0 > GT0 > GT05
GT05m serial depth 68.5 h | gate ancestors 44 (all Claude or frozen) | chain DC0 > ED0 > SMAP > Q1r > INT0 > GT0 > GT05 > GT05m
GT1A serial depth 117.0 h | gate ancestors 67 (all Claude or frozen) | chain G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A
GT1B serial depth 118.5 h | gate ancestors 78 (all Claude or frozen) | chain G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A > GT1B
GT2 serial depth 142.0 h | gate ancestors 95 (all Claude or frozen) | chain G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A > GT1B > Q2 > CRV4 > GT2
GT3 serial depth 161.5 h | gate ancestors 95 (all Claude or frozen) | chain G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A > GT1B > M2f > V3L > CAMP > CRV5 > GT3
GTA serial depth 157.0 h | gate ancestors 88 (all Claude or frozen) | chain G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A > GT1B > TA4 > TA6 > GTA
default-reachable gates (no ask in any ancestor): GT0 GT05 GT1A GT1B GT2 GT3 | user-gated: GT05m GTA
critical to GT1B 20 WPs, midpoint hours 145.5
split all total 1419-2157 | Claude 1055-1600 | Claude share 74.3% / 74.2%
split t1b total 750-1134 | Claude 550-829 | Claude share 73.3% / 73.1%
WPs 229 lanes 29 (CL 17, CX 12) | all ((1419, 2157), (1055, 1600), '74.3% / 74.2%')
tier T0 167-256 (CX 3-5) Claude share of lows 98.2
tier T0.5 156-241 (CX 56-86) Claude share of lows 64.1
tier T1a 277-406 (CX 62-91) Claude share of lows 77.6
tier T1b 150-231 (CX 79-123) Claude share of lows 47.3
tier T2 302-450 (CX 81-124) Claude share of lows 73.2
tier T3 207-318 (CX 83-128) Claude share of lows 59.9
tier TA 80-135 (CX 0-0) Claude share of lows 100.0
tier T5 80-120 (CX 0-0) Claude share of lows 100.0
wave W0 167-256 (98.2% / 98.0%; 34 WPs; 8 lanes: 6 CL + 2 CX)
wave W1 174-268 (58.6% / 59.0%; 44 WPs; 17 lanes: 9 CL + 8 CX)
wave W2 310-457 (71.0% / 70.7%; 51 WPs; 21 lanes: 12 CL + 9 CX)
wave W3 172-264 (38.4% / 37.9%; 24 WPs; 12 lanes: 4 CL + 8 CX)
wave W4 326-488 (73.3% / 72.5%; 45 WPs; 22 lanes: 15 CL + 7 CX)
wave W5 270-424 (97.8% / 97.6%; 31 WPs; 14 lanes: 13 CL + 1 CX)
demo path (142, 219) WPs 27 evolution (1277, 1938) 10.0% / 10.2%
independence cost (Claude stand-ins + live per-kind WPs) 117-172
sessions GT0 depth 65.5 A 12.4 (11.0-14.2) B 9.6 (9.6-11.0) C 9.6 (9.6-9.6)
sessions GT05 depth 67.0 A 17.6 (15.7-20.2) B 13.4 (11.8-15.7) C 9.8 (9.8-9.8)
sessions GT1A depth 117.0 A 33.4 (29.7-38.2) B 25.5 (22.3-29.7) C 17.2 (17.2-17.2)
sessions GT1B depth 118.5 A 39.5 (35.1-45.1) B 30.1 (26.3-35.1) C 17.4 (17.4-18.0)
sessions GT2 depth 142.0 A 52.0 (46.2-59.4) B 39.6 (34.7-46.2) C 20.8 (20.8-23.8)
sessions GT3 depth 161.5 A 49.6 (44.1-56.7) B 37.8 (33.1-44.1) C 23.7 (23.7-23.7)
sessions GT05m depth 68.5 A 18.7 (16.6-21.3) B 14.2 (12.4-16.6) C 10.0 (10.0-10.0)
sessions GTA depth 157.0 A 47.0 (41.8-53.7) B 35.8 (31.3-41.8) C 23.0 (23.0-23.0)
sessions GT0+pack A 14.1 (12.5-16.1) B 10.7 (9.6-12.5) C 9.6 (9.6-9.6)
PRs per wave Claude 7 5 10 3 10 12 (47) | Codex 1 4 4 5 4 1 (19)
width: lanes per wave 8 17 21 12 22 14 | ASAP level width 33 over 19 levels
paths: 229 WPs with explicit globs all resolve inside their lane; 0 use @lane
planned new paths checked: 59
1860 tracked paths (repo + infra origin/main), 0 unowned or tied
numbers block: 137 values equal the computation
PASS
```

## Annex D. Path map, ranges, planned new paths, frozen set, numbers

Frozen artifacts Codex may depend on (W0 pack plus ENV0 and ENV4, which are W1 WPs):

FROZEN: ENV0 ENV4 G0f G0gr CONTR CF0 FRZ0 BK0

Owners block (lane: globs separated by ` ; `; `{a,b}` alternation; `[x-y]` and `(a|b)` pass through as regex; the most specific glob wins):

```owners
X-FACADE: Cargo.toml ; Cargo.lock ; rust-toolchain.toml ; .github/** ; scripts/verify-local-ci.ps1 ; scripts/run-local-*.ps1 ; scripts/init-local-env.ps1 ; tests/run-local-*.Tests.ps1 ; tests/test_postgres_ci_caller_contract.py ; crates/core/Cargo.toml ; crates/core/src/lib.rs ; crates/core/src/{debug_console,durable_run_events,model_provider,quota_grant,run_activity,run_config,run_timeline_v2,workflow_bridge}.rs ; crates/core/src/{pipeline,authority}.rs ; crates/core/tests/{model_provider,artifact_repository,model_attempt_repository,postgres_artifact_migration,postgres_run_events,tracer,quota_grant,run_activity,run_config}.rs ; contracts/pipeline/** ; migrations/0001_* ; migrations/0002_model_attempt_ledger.sql ; migrations/0003_* ; migrations/003[0-9]_* ; crates/core/src/facade_*.rs ; crates/core/tests/facade_*.rs ; docs/adr/033[2-9]-* ; docs/journal/(046[4-9]|047[0-9])-*
X-CONF: crates/core/src/durable_jobs.rs ; crates/core/tests/durable_jobs.rs ; crates/core/tests/conformance/** ; migrations/004[0-2]_* ; docs/adr/(031[6-9]|032[0-3])-* ; docs/journal/(043[2-9]|044[0-7])-*
X-COMPILE: crates/core/src/{change_compiler,core_task}.rs ; crates/core/tests/{change_compiler,core_task}.rs ; docs/adr/(030[8-9]|031[0-5])-* ; docs/journal/(041[6-9]|042[0-9]|043[0-1])-*
X-MAP: crates/core/src/{e0_builder_design,e0_core_draft_binding,e0_investigation_plan,e0_mechanism_resolution,e0_opportunity_qualification,e0_proposal_assembly}.rs ; crates/core/tests/{e0_investigation_plan,e0_mechanism_resolution}.rs ; docs/adr/(035[6-9]|036[0-3])-* ; docs/journal/(051[2-9]|052[0-7])-*
X-ARTIF: crates/core/src/artifact_kind_*.rs ; crates/core/tests/artifact_kind_*.rs ; migrations/004[3-4]_* ; docs/adr/030[0-7]-* ; docs/journal/(040[0-9]|041[0-5])-*
X-GATE: crates/core/src/{evaluation_plan,final_eligibility,paired_scenario,native_evaluation,e0_safety_oracle,independent_verifier,governed_registry,jev_decision,sandbox,policy_oracle}.rs ; crates/core/tests/{sandbox,evaluation_plan,final_eligibility,paired_scenario,native_evaluation_admission,e0_safety_oracle,independent_verifier,governed_registry,jev_decision,sandbox_identity,policy_oracle}.rs ; migrations/002[5-9]_* ; docs/adr/034[0-7]-* ; docs/journal/(048[0-9]|049[0-5])-*
X-SENS: crates/core/src/{autonomous_scout,deterministic_sensor,e0_deterministic_sensor,e0_query_lab,enriched_history,local_lab,local_simulation,platform_sensor,signal_portfolio}.rs ; crates/core/tests/{autonomous_scout,deterministic_sensor,e0_deterministic_sensor,e0_query_lab,enriched_history,local_lab,local_simulation,platform_sensor,platform_scout}.rs ; crates/core/src/detectors/** ; crates/runner/** ; migrations/004[5-6]_* ; docs/adr/038[0-7]-* ; docs/journal/(056[0-9]|057[0-5])-*
X-SRC: crates/core/src/{original_contact_projection,platform_discovery,platform_discovery_verifier,platform_observations,platform_source_policy,source_validation}.rs ; crates/core/tests/{original_contact_projection,platform_observations,platform_source_policy,postgres_platform_observations,source_validation}.rs ; crates/source-adapters/** ; contracts/*.schema.json ; contracts/{README.md,__init__.py,validate_fixtures.py} ; contracts/fixtures/** ; contracts/sources/** ; tests/test_artifact_envelope_contract.py ; tests/test_source_snapshot_partition_inventory.py ; migrations/0002_pulso_platform_observations.sql ; migrations/(001[5-9]|002[0-4])_* ; docs/adr/(038[8-9]|039[0-5])-* ; docs/journal/(057[6-9]|058[0-9]|059[0-1])-*
X-LEARN: crates/core/src/{memory_store,governed_memory_use,memory_temporal_protocol,e0_frozen_memory_cycle,e0_frozen_memory_publication,e0_frozen_summary,e0_frozen_verifier,run_fork,wiki_scratch}.rs ; crates/core/src/replay_*.rs ; crates/core/tests/{governed_memory_use,memory_temporal_protocol,run_fork,wiki_scratch,postgres_memory_temporal_receipts,published_memory}.rs ; crates/core/tests/replay_*.rs ; migrations/0002_pulso_memory_control.sql ; migrations/0004_* ; migrations/(000[5-9]|001[0-4])_* ; docs/adr/(034[8-9]|035[0-5])-* ; docs/journal/(049[6-9]|050[0-9]|051[0-1])-*
X-SCEN: crates/core/src/{value_model}.rs ; crates/core/src/scenario_*.rs ; crates/core/tests/{value_model}.rs ; crates/core/tests/scenario_*.rs ; migrations/004[7-9]_* ; docs/adr/037[2-9]-* ; docs/journal/(054[4-9]|055[0-9])-*
X-DOC: docs/IMPLEMENTATION_STATUS.md ; docs/architecture/** ; docs/data/** ; docs/gaps/** ; docs/platform-observations.md ; docs/local-e0-e2e-runner.md ; docs/spec-amendments/codex/** ; docs/adr/(032[4-9]|033[0-1])-* ; docs/journal/(044[8-9]|045[0-9]|046[0-3])-*
X-REV: docs/reviews/codex/** ; docs/adr/(036[4-9]|037[0-1])-* ; docs/journal/(052[8-9]|053[0-9]|054[0-3])-*
L-GOV: AGENTS.md ; CLAUDE.md ; CONTEXT.md ; README.md ; OWNERS.md ; .gitattributes ; .gitignore ; docs/BITACORA_PULSO.md ; docs/agents/** ; docs/adr/** ; docs/journal/00[0-9][0-9]-* ; docs/spec-amendments/claude/** ; docs/reports/gates/** ; docs/reviews/claude/** ; docs/lanes/** ; contracts/engine-run/** ; contracts/engine-steps/** ; scripts/gov/** ; contracts/artifact-kinds/** ; migrations/009[5-9]_* ; docs/adr/020[0-9]-* ; docs/journal/(026[0-9]|027[0-5])-*
L-ENV: local/compose.yaml ; scripts/env/** ; scripts/verify-local-all.ps1 ; scripts/verify-local-fast.ps1 ; scripts/dev.ps1 ; tests/test_local_compose_contract.py ; seams/xtask/** ; local/.env.example ; local/.secrets/** ; tests/verify-local-*.Tests.ps1 ; local/compose.d/** ; docs/adr/018[0-9]-* ; docs/journal/(022[8-9]|023[0-9]|024[0-3])-*
L-MODEL: roleplay-llm/** ; local/core/gateway/** ; scripts/dc/** ; agent-core-assets/worlds/** ; agent-core-assets/corpus/** ; core-bridge/src/pulso_core_runtime/llm/** ; core-bridge/src/pulso_core_runtime/stages/** ; core-bridge/tests/llm/** ; core-bridge/tests/runtime/test_stages* ; docs/adr/023[0-9]-* ; docs/journal/(030[8-9]|031[0-9]|032[0-3])-* ; local/compose.d/l-model.yaml
L-BRIDGE: core-bridge/** ; bridge-contract/** ; agent-core-assets/** ; local/core/** ; scripts/core/** ; docs/adr/012[0-9]-* ; docs/journal/(013[2-9]|014[0-7])-* ; local/compose.d/l-bridge.yaml
L-E2E: e2e-core/** ; demo/** ; docs/reports/e2e/** ; docs/adr/016[0-9]-* ; docs/journal/(019[6-9]|020[0-9]|021[0-1])-* ; local/compose.d/l-e2e.yaml
L-PLAT: platform-contract/** ; platform-exporter/** ; platform-sim/** ; contracts/product/** ; seams/crates/control-api/src/correlation/** ; migrations/007[0-4]_* ; docs/adr/026[0-9]-* ; docs/journal/(035[6-9]|036[0-9]|037[0-1])-* ; local/compose.d/l-plat.yaml
L-CLIENT: seams/Cargo.toml ; seams/Cargo.lock ; seams/crates/core-client/** ; seams/crates/model-client/** ; docs/adr/014[0-9]-* ; docs/journal/(016[4-9]|017[0-9])-* ; local/compose.d/l-client.yaml
L-ENGINE: seams/crates/abi/** ; seams/crates/engine/** ; contracts/engine-handlers/** ; seams/crates/steps/** ; seams/crates/swap/** ; docs/adr/017[0-9]-* ; docs/journal/(021[2-9]|022[0-7])-* ; local/compose.d/l-engine.yaml
L-CAPI: seams/crates/control-api/** ; contracts/control-api/** ; migrations/008[5-9]_* ; docs/adr/013[0-9]-* ; docs/journal/(014[8-9]|015[0-9]|016[0-3])-* ; local/compose.d/l-capi.yaml
L-PG: seams/crates/pg/** ; seams/crates/worker/** ; local/pg/** ; migrations/00[56][0-9]_* ; docs/adr/025[0-9]-* ; docs/journal/(034[0-9]|035[0-5])-* ; local/compose.d/l-pg.yaml
L-EVAL: seams/crates/eval/** ; agent-core-assets/eval-suites/** ; migrations/009[0-4]_* ; docs/adr/019[0-9]-* ; docs/journal/(024[4-9]|025[0-9])-* ; local/compose.d/l-eval.yaml
L-AUTH: seams/crates/authority/** ; local-identity/** ; migrations/008[0-4]_* ; docs/adr/010[0-9]-* ; docs/journal/(010[0-9]|011[0-5])-* ; local/compose.d/l-auth.yaml
L-MEM: seams/crates/memory/** ; migrations/007[5-9]_* ; docs/adr/022[0-9]-* ; docs/journal/(029[2-9]|030[0-7])-* ; local/compose.d/l-mem.yaml
L-CONSOLE: debug-console/** ; docs/adr/015[0-9]-* ; docs/journal/(018[0-9]|019[0-5])-* ; local/compose.d/l-console.yaml
L-OPS: docs/runbooks/** ; docs/security/** ; docs/contracts/metrics.md ; local/observability/** ; docs/adr/024[0-9]-* ; docs/journal/(032[4-9]|033[0-9])-* ; local/compose.d/l-ops.yaml
L-BREADTH: seams/crates/artifacts/** ; docs/adr/011[0-9]-* ; docs/journal/(011[6-9]|012[0-9]|013[0-1])-* ; local/compose.d/l-breadth.yaml
L-INFRA: infra:** ; docs/adr/021[0-9]-* ; docs/journal/(027[6-9]|028[0-9]|029[0-1])-*
```

Planned new paths and their expected lane (the OWNERS test of G0f extends the map with them):

```newpaths
crates/core/src/artifact_kind_flow.rs -> X-ARTIF
crates/core/tests/artifact_kind_flow.rs -> X-ARTIF
crates/core/src/policy_oracle.rs -> X-GATE
crates/core/tests/policy_oracle.rs -> X-GATE
crates/core/src/pipeline.rs -> X-FACADE
crates/core/src/authority.rs -> X-FACADE
crates/core/src/facade_steps.rs -> X-FACADE
crates/core/tests/facade_steps.rs -> X-FACADE
crates/core/src/replay_clock.rs -> X-LEARN
crates/core/src/scenario_factory.rs -> X-SCEN
crates/core/src/detectors/family_01.rs -> X-SENS
crates/core/tests/conformance/jobs.rs -> X-CONF
contracts/pipeline/transcript.json -> X-FACADE
contracts/artifact-kinds/matrix.json -> L-GOV
contracts/product/fixture.json -> L-PLAT
contracts/engine-steps/pack/manifest.json -> L-GOV
contracts/engine-run/report.schema.json -> L-GOV
contracts/control-api/openapi.yaml -> L-CAPI
contracts/engine-handlers/abi.md -> L-ENGINE
roleplay-llm/server.py -> L-MODEL
roleplay-llm/tests/test_scanner.py -> L-MODEL
local/pg/init.sql -> L-PG
local/observability/alerts.yaml -> L-OPS
local/compose.d/l-pg.yaml -> L-PG
local/compose.d/l-model.yaml -> L-MODEL
local/compose.d/shared.yaml -> L-ENV
seams/Cargo.toml -> L-CLIENT
seams/crates/abi/src/lib.rs -> L-ENGINE
seams/crates/steps/src/lib.rs -> L-ENGINE
seams/crates/swap/src/lib.rs -> L-ENGINE
seams/crates/pg/src/lib.rs -> L-PG
seams/xtask/src/main.rs -> L-ENV
docs/reviews/codex/rev1.md -> X-REV
docs/reviews/claude/crv0.md -> L-GOV
docs/spec-amendments/codex/pl-c6.md -> X-DOC
docs/spec-amendments/claude/px0.md -> L-GOV
docs/reports/gates/gt0.md -> L-GOV
docs/reports/e2e/run-01.md -> L-E2E
docs/runbooks/rb-01.md -> L-OPS
docs/security/threat-model.md -> L-OPS
docs/lanes/l-pg/notes.md -> L-GOV
scripts/env/baseline.ps1 -> L-ENV
scripts/gov/w0-receipt.ps1 -> L-GOV
scripts/dc/scan.py -> L-MODEL
scripts/verify-local-all.ps1 -> L-ENV
tests/verify-local-all.Tests.ps1 -> L-ENV
agent-core-assets/corpus/smap-01.json -> L-MODEL
agent-core-assets/eval-suites/flow.json -> L-EVAL
agent-core-assets/worlds/seed.json -> L-MODEL
migrations/0005_x.sql -> X-LEARN
migrations/0050_x.sql -> L-PG
migrations/0095_x.sql -> L-GOV
docs/adr/0100-x.md -> L-AUTH
docs/adr/0230-x.md -> L-MODEL
docs/adr/0300-x.md -> X-ARTIF
docs/adr/0395-x.md -> X-SRC
docs/journal/0100-l-auth-x.md -> L-AUTH
docs/journal/0405-x-artif-x.md -> X-ARTIF
docs/journal/0591-x-src-x.md -> X-SRC
```

Numbers block (values the checker recomputes; the prose of this document is generated from the same values):

```numbers
c2x_hard = 0
x2c_nonfrozen = 0
x2frozen = 30
swapin_edges = 40
anc_GT0 = 26
chain_GT0 = DC0 > ED0 > SMAP > Q1r > INT0 > GT0
hours_GT0 = 142-219
depth_GT0 = 65.5
anc_GT05 = 40
chain_GT05 = DC0 > ED0 > SMAP > Q1r > INT0 > GT0 > GT05
hours_GT05 = 203-310
depth_GT05 = 67.0
anc_GT05m = 44
chain_GT05m = DC0 > ED0 > SMAP > Q1r > INT0 > GT0 > GT05 > GT05m
hours_GT05m = 213-330
depth_GT05m = 68.5
anc_GT1A = 67
chain_GT1A = G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A
hours_GT1A = 390-582
depth_GT1A = 117.0
anc_GT1B = 78
chain_GT1B = G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A > GT1B
hours_GT1B = 460-688
depth_GT1B = 118.5
anc_GT2 = 95
chain_GT2 = G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A > GT1B > Q2 > CRV4 > GT2
hours_GT2 = 609-904
depth_GT2 = 142.0
anc_GT3 = 95
chain_GT3 = G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A > GT1B > M2f > V3L > CAMP > CRV5 > GT3
hours_GT3 = 580-863
depth_GT3 = 161.5
anc_GTA = 88
chain_GTA = G0f > CONTR > CF0 > E1 > E5L > K3 > V1 > V2 > H1 > P2R > MEM1 > Q1 > GT1A > GT1B > TA4 > TA6 > GTA
hours_GTA = 542-825
depth_GTA = 157.0
critical_wps = 20
critical_hours_mid = 145.5
all_total = 1419-2157
all_claude = 1055-1600
all_codex = 364-557
all_share_claude = 74.3% / 74.2%
all_mid = 1788
all_share_codex = 25.7% / 25.8%
t1b_total = 750-1134
t1b_claude = 550-829
t1b_codex = 200-305
t1b_share_claude = 73.3% / 73.1%
t1b_mid = 942
t1b_share_codex = 26.7% / 26.9%
wps = 229
lanes = 29
lanes_cl = 17
lanes_cx = 12
churn_total = 1967
tier_T0 = 167-256 (CX 3-5)
tiershare_T0 = 98.2
tier_T0.5 = 156-241 (CX 56-86)
tiershare_T0.5 = 64.1
tier_T1a = 277-406 (CX 62-91)
tiershare_T1a = 77.6
tier_T1b = 150-231 (CX 79-123)
tiershare_T1b = 47.3
tier_T2 = 302-450 (CX 81-124)
tiershare_T2 = 73.2
tier_T3 = 207-318 (CX 83-128)
tiershare_T3 = 59.9
tier_TA = 80-135 (CX 0-0)
tiershare_TA = 100.0
tier_T5 = 80-120 (CX 0-0)
tiershare_T5 = 100.0
wave_W0 = 167-256 (98.2% / 98.0%; 34 WPs; 8 lanes: 6 CL + 2 CX)
wave_W1 = 174-268 (58.6% / 59.0%; 44 WPs; 17 lanes: 9 CL + 8 CX)
wave_W2 = 310-457 (71.0% / 70.7%; 51 WPs; 21 lanes: 12 CL + 9 CX)
wave_W3 = 172-264 (38.4% / 37.9%; 24 WPs; 12 lanes: 4 CL + 8 CX)
wave_W4 = 326-488 (73.3% / 72.5%; 45 WPs; 22 lanes: 15 CL + 7 CX)
wave_W5 = 270-424 (97.8% / 97.6%; 31 WPs; 14 lanes: 13 CL + 1 CX)
demo_wps = 27
demo_hours = 142-219
demo_mid = 180.5
demo_pct = 10.0% / 10.2%
evolution_hours = 1277-1938
indep_cost = 117-172
indep_cost_standins = 57-85
indep_cost_livekind = 60-87
pack_hours = 25-36
pack_mid = 30.5
sess_GT0_A = 12.4 (11.0-14.2)
sess_GT0_B = 9.6 (9.6-11.0)
sess_GT0_C = 9.6 (9.6-9.6)
sess_GT05_A = 17.6 (15.7-20.2)
sess_GT05_B = 13.4 (11.8-15.7)
sess_GT05_C = 9.8 (9.8-9.8)
sess_GT1A_A = 33.4 (29.7-38.2)
sess_GT1A_B = 25.5 (22.3-29.7)
sess_GT1A_C = 17.2 (17.2-17.2)
sess_GT1B_A = 39.5 (35.1-45.1)
sess_GT1B_B = 30.1 (26.3-35.1)
sess_GT1B_C = 17.4 (17.4-18.0)
sess_GT2_A = 52.0 (46.2-59.4)
sess_GT2_B = 39.6 (34.7-46.2)
sess_GT2_C = 20.8 (20.8-23.8)
sess_GT3_A = 49.6 (44.1-56.7)
sess_GT3_B = 37.8 (33.1-44.1)
sess_GT3_C = 23.7 (23.7-23.7)
sess_GT05m_A = 18.7 (16.6-21.3)
sess_GT05m_B = 14.2 (12.4-16.6)
sess_GT05m_C = 10.0 (10.0-10.0)
sess_GTA_A = 47.0 (41.8-53.7)
sess_GTA_B = 35.8 (31.3-41.8)
sess_GTA_C = 23.0 (23.0-23.0)
demo_pack_mid = 205.0
sess_GT0pack_A = 14.1 (12.5-16.1)
sess_GT0pack_B = 10.7 (9.6-12.5)
sess_GT0pack_C = 9.6 (9.6-9.6)
prs_CL_W0 = 7
prs_CX_W0 = 1
prs_CL_W1 = 5
prs_CX_W1 = 4
prs_CL_W2 = 10
prs_CX_W2 = 4
prs_CL_W3 = 3
prs_CX_W3 = 5
prs_CL_W4 = 10
prs_CX_W4 = 4
prs_CL_W5 = 12
prs_CX_W5 = 1
prs_CL = 7 5 10 3 10 12
prs_CX = 1 4 4 5 4 1
prs_total_CL = 47
prs_total_CX = 19
asap_width = 33
asap_levels = 19
lanes_per_wave = 8 17 21 12 22 14
lane_table = L-AUTH:6:38-56;L-BREADTH:7:50-72;L-BRIDGE:6:25-39;L-CAPI:6:46-64;L-CLIENT:11:72-103;L-CONSOLE:2:24-36;L-E2E:15:126-193;L-ENGINE:12:93-140;L-ENV:16:46-75;L-EVAL:8:58-85;L-GOV:39:144-220;L-INFRA:8:74-125;L-MEM:3:24-36;L-MODEL:13:72-107;L-OPS:4:63-97;L-PG:8:61-92;L-PLAT:7:39-60;X-ARTIF:7:47-70;X-COMPILE:3:19-29;X-CONF:3:15-25;X-DOC:3:12-19;X-FACADE:8:26-45;X-GATE:6:41-61;X-LEARN:4:39-58;X-MAP:1:6-10;X-REV:7:33-52;X-SCEN:3:22-34;X-SENS:6:56-86;X-SRC:7:48-68
wps_explicit_paths = 229
newpaths_checked = 59
```

## Annex E. Findings dispositions (all review passes)

Disposition vocabulary: fixed (done as proposed), modified (done another way, with the evidence), rejected (not done, with the evidence). In this pass nothing was rejected outright; five items were modified (E.5).

### E.1 Final review 1 (numbers and rules): `review-v4-1-numbers.md`

| Id | Sev | Disposition |
|---|---|---|
| F1 | MED | fixed: the enabling pack is stated (G0f, G0gr, CONTR, CF0, FRZ0, BK0, 30.5 h midpoint); the sessions model (rule, capacities 16 / 21 / 40, floor 7.5 h) is in the checker; section 12 and the front page print its output; the old "5.6%" and "5.7/5.5%" are replaced by the computed 10.0% / 10.2% |
| F2 | HIGH | fixed: GT05 no longer depends on SMOKE or ENV9; GT05m (needs ASK-7) is a separate gate; H1 has a simulated-issuer default and H1r (needs ASK-11) upgrades the label; new `needs` column and a checker rule: GT0, GT05, GT1A, GT1B, GT2, GT3 have no ancestor that needs an ask |
| F3 | MED | fixed: DPL1 no longer says "consumed by E4R"; CONF2 and CT1 reworded; swap-ins stay `~` edges |
| F4 | MED | fixed: CF1 deps GT05, TW1, E1, E5L and names C-3 to C-6 and C-8 to C-10; C-7 v1 frozen at CF0, v1.1 (claim-next) frozen with the FRZ0 digest, DJC implements it |
| F5 | MED | fixed: G1 acceptance lists tests 1, 4, 5, 6 green and 2, 3, 7, 8 as skeletons turned green by TPS, ED0, RPP, DC0; GT0 requires all 8 |
| F6 | MED | fixed: CRV0 before GT0 (the demo path now carries an independent loop), CRV5 for W5 live breadth gating GT3, CRV6 for the AWS slice gating GTA; CRV hours are table rows |
| F7 | MED | fixed: `paths` column plus checker assertion; E3b moved to L-E2E; Q3c split into Q3ca and Q3cc; K0 creates only the workspace files and the core-client crate; WDX edits only re-exports and its own facade files |
| F8 | LOW | fixed: ADR and journal block globs per lane, migration reserve 0095-0099 (L-GOV), `tests/verify-local-*.Tests.ps1` (L-ENV), `local/compose.d/l-<lane>.yaml`; the checker also runs on the planned-new-paths block. Sub-item (iv) `docs/contracts/metrics.md` was already mapped to L-OPS in v4 (evidence: v4 owners line L-OPS), only the compose rule was missing |
| F9 | LOW | fixed: the frozen set is called "W0 pack plus ENV0 and ENV4" everywhere |
| F10 | LOW | modified: PR counts are computed as ceil(team midpoint hours of the wave / 30). The review used the T0.5 tier hours (57-88 h) for Codex W1; the wave W1 Codex hours are about 91.0 h (midpoint), which gives 4 PRs; the count is now a checker output, not typed |
| F11 | LOW | fixed: 26 acceptance cells rewritten with counts, exit codes or named artefacts; 9 review first_red cells replaced by "review-closure script exits 1 while any finding is open"; ENV2 first_red is a real RED (`baseline.ps1 --compare` exits 1); the checker rejects bare cells and review-checklist REDs |
| F12 | LOW | fixed: shared-foundation paths are edited only via TA0 asks; the checker also maps infra `origin/main` (177 paths) |
| N1-N4 | | fixed: WPs RC1-RC3 renamed RUN1-RUN3 (review classes keep RC1-RC3); WP C1 renamed CON1; hardware options HW-1..3, capacity levels LVL-A/B/C; appendix ids prefixed A-, B-, C-; the seam wave is SEAM-1; TW-n versus TWn stated in the glossary |
| N5 | | kept: per-wave and per-tier Codex shares vary by design; the user rule is overall and through T1b |

### E.2 Final review 2 (DEMO-0 reality): `review-v4-2-demo0.md`

| Id | Sev | Disposition |
|---|---|---|
| R1 | HIGH | fixed: section 3.3 and M0RP: tool use is the model's JSON in the content, no OpenAI `tool_calls`; acceptance is a JSON step round trip |
| R2 | HIGH | fixed: alias `pulso-evolution-llm`, model `external-reasoning-model`, price 1/4 kept; registry and digests untouched; the shim echoes the configured model; M3 acceptance names the three policy mismatches |
| R3 | HIGH | modified: the review proposed raising profile `timeout_s` to 120-300 (a profile bump with a digest cascade, which also contradicts R2's "registry untouched"); done instead: async job pattern with late-answer cache, 55 s per-call budget, step caps 5/5/7, CLT0 configurable client timeout (1800 s) with unknown-to-reconcile polling; the profile bump remains the fallback if SNET measures more than 20% of calls above 55 s. Same failure mode removed without moving digests |
| R4 | MED | fixed: call count 20-30 under the caps; live run 10-30 min of one slot |
| R5 | MED | fixed: replay key normalises run_id, turn_id, session_id, labels and ids; 3 replays from a fresh Core DB with 0 misses |
| R6 | MED | fixed: TPS is a deny-by-default allow-list over the fixed `LLMAgentPort` dict with an explicit treated-aggregate spec for lab rows (k-threshold, hashed groups, no free text); first RED is a free-text lab row |
| R7 | LOW | fixed: SNET checks the Go image (not present in the default Podman connection, measured) and ASK-4 asks for the one download, default the existing contract double labelled `gateway=stand-in` |
| F1 | HIGH | modified: ED0L, CMPpy, WRLD0, INT0 added and Q1r, SMAP, ED0, M3 re-sized as proposed; GSIpy depends on G1 and WRLD0 (it reads arm-report fixtures, not CMPpy output) so it runs in parallel; CMPpy is built first against the CONTR C-8 fixtures and run on SMAP outputs at INT0; CMPpy and the seeded world are two WPs because worlds live in L-MODEL paths. Total 142-219 h versus the review's 120-175 h: the difference is the review, train, receipt, timeout and target-dir WPs required by final review 3 |
| F2 | HIGH | fixed (see R1, R2) |
| F3 | HIGH | modified (see R3) |
| F4 | HIGH | fixed (see F2 of review 1): GT05 and GT05m |
| F5 | MED | fixed: `jev=not_exercised(blocked: agent-core PR 28 not on main)`; M5a moved to W1 and out of the GT0 ancestors; step 10 and step 7 labels; `data_origin=generated_sample` |
| F6 | MED | fixed: SMAP target from the ReadBase capability catalogue, permutation test, a negative ending `unlinked` |
| F7 | MED | fixed: ED0b (3-5 h, `--source original`, separate namespace, W1, a GT05 dependency) makes the original CSV reachable without Codex; DORIGm, DORIG, DSRC stay swap-ins |
| F8 | MED | fixed (see R5) |
| F9 | MED | fixed (see R6) |
| F10 | LOW | fixed: hours and sessions exclude live windows; 2-3 sessions of responder windows are stated |
| Sec. 2.3 | | steps 3, 5, 6, 7, 10 relabelled (section 2.1) |
| Sec. 4 | | clause coverage: the dataset clause no longer depends on Codex; DEMO tier per clause is in section 1.3 |
| Sec. 5 | | model-axis defect fixed with F4; ordering AWS before breadth kept |

### E.3 Final review 3 (feasibility and process): `review-v4-3-feasibility.md`

| Id | Sev | Disposition |
|---|---|---|
| M1 | HIGH | fixed: G0p (W0 receipt script), TRN0 (W0 integrator) and CRV0 are GT0 dependencies; the W0 pre-PR gate is stated in section 8.1 |
| M2 | HIGH | fixed: the cap is 3 independent stacks per team, with depth rules and an at-the-cap rule (unpublished stacked branches or bundles); merge delegation is the third ask; PR counts per wave per team are computed |
| M3 | MED | fixed: WTR1 in W0 and first; hard ceiling 40 registered; live worktrees equal implementers; a lane holds one only while a WP runs; WTR2 default is list-only |
| M4 | MED | fixed: live worktrees = implementers; width above is a queue (section 7.5) |
| M5 | MED | fixed: the independence rule is stated the right way round in the front page, 5 and 9 |
| M6 | MED | fixed: Codex trains are depth 1 from the last user-confirmed main plus bundles; Claude depth up to 4 |
| M7 | LOW | pass (compliance confirmed) |
| O1 | HIGH | modified: the enabling pack is priority work in sessions 1-3 (FRZ0 closes in session 2) so Codex starts in session 3; the cost is computed, 1.7 sessions at LVL-A, not the reviewer's 1-1.5 |
| O2 | MED | fixed: DMAPV validates the FRZ0 corpus; bridge dry-run and writer goldens added to FRZ0; CT1 acceptance reworded; REV1-5 labelled opportunistic |
| O3 | PASS | `crates/core/tests/policy_oracle.rs` marked "to create" (section 7.1) |
| O4 | HIGH | fixed: Codex capacity row, per-account slot rule, 4-5 tests per agent-hour, gate-time projection with its assumption, fast tier per lane (section 6) |
| O5 | MED | fixed: stated plainly in section 12 and the front page (Claude is the bottleneck; independence costs 117-172 h) |
| E1 | LOW | fixed: host 16 GB, free 5.7 GB, swap 8 GB, C: 112 GB, D: 1.2 TB, `.wslconfig` 10 GB / 8 CPUs; ENV8 records min and median; target dirs on D: |
| E2 | PASS | levels labelled assumptions; velocity re-baselined at GT0 as well as TW-1 |
| E3 | PASS | G0e moved to W0 (demo path) so W0 runs with per-lane target dirs |
| E4 | PASS | ENVADR cites ENV0 evidence; ENV1 depends on ENVADR and needs ASK-5 and ASK-6 |
| A1 | PASS | ASK-1 is first |
| A2 | HIGH | fixed: 26 single-sentence asks, a needed-by column, order 1 treated payloads, 2 Codex freeze, 3 merge delegation, then downloads and acks, then DEMO-1/2/3 items, then relays; EXT-1..3 are paste-ready |
| R1 | HIGH | modified: restructured as front page (2 pages), first sessions, glossary, body, annexes; the table, checker, owners block and history are annexes inside this single file because you asked for one document, not separate files |

### E.4 Earlier passes (carried from v4, ids prefixed)

These paragraphs keep the ids of their time. Mapping of the old ask ids (U-n) to the current ones: U-1 to ASK-2, U-2 to ASK-16, U-4 to ASK-9 and ASK-10, U-5 to ASK-17..21, U-6 to ASK-22, U-7 to ASK-23, U-8 to ASK-3, U-9 to ASK-8, U-12 to ASK-15, U-13 to ASK-1, U-14a to ASK-5, U-14b to ASK-6 and ASK-7, U-14c to ASK-14, U-15 to ASK-11, U-16 to ASK-12, U-17 to ASK-13. WP RC1-RC3 are now RUN1-RUN3, C1 is CON1, Q3c is Q3ca and Q3cc.

**Review A (v3, consistency).** A-H1 fixed: K3 no longer depends on compile work (K3fx fixture; stand-ins CMP, GSI; section 6). A-H2 fixed: K2 touches no `crates/core`; CT1 is a Codex WP under `[CONTRACT-CHANGE]`; consent clause optional. A-H3 fixed: Claude wrappers are new files; Codex gate scripts X-FACADE (9.1). A-H4 fixed: total path map with 0 unowned of 1683, `durable_jobs.rs` X-CONF, `bridge-contract` and `core-bridge` L-BRIDGE, ranges per lane, new paths marked. A-H5 fixed: U-14 default measures only; GT0 has no ENV ancestor. A-H6 fixed: CF0, FRZ0, TW0 are WPs with edges; Codex side of TW-0 only if U-1. A-H7 fixed: `first_red` and `acceptance` columns, checker rejects empty cells. A-H8 fixed: rule covers all developer agents; step 2 -> 3 hand-off defined; honesty test 2 covers original-treated and treated payloads (2.2). A-M1 fixed: chain recomputed (ENV0 > K3 62.0 h; GT1B depth 118.5 h; floors rebuilt). A-M2 fixed: sessions = max(capacity bound, floor). A-M3 fixed: no stale list; minimum cuts computed. A-M4 fixed: K0 is T0.5; tier and wave monotonicity checked. A-M5 fixed: G0d feeds the gates through the PR receipt rule and ENV6; CRV1 gates GT05; RG numbering aligned (RG-1 GT05, RG-2/3 GT1A, RG-4 GT1B). A-M6 fixed: ADR blocks sized for 17 and 12 lanes. A-M7 fixed: contracts table says provisional versus frozen. A-M8 fixed: compose fragments owned by their lane. A-M9 fixed: Q3c split, M5b in L-CLIENT, `stages/` in L-MODEL, X-REV defined read-only. A-M10 fixed: review classes complete incl. L-E2E, X-CONF, X-REV; loops are WPs; one churn number. A-M11 fixed: per-tier and per-wave shares printed; Codex lanes pulled early. A-M12 fixed: capacity B lists its conditional ENV items; no unmet dependency. A-M13 fixed: staffing per capacity (9.6). A-M14 fixed: U-2 is optional with a defined default. A-M15 fixed: DVREC owns recompute, STP1 wraps. A-M16 fixed: G0gp and G0gr split. A-M17 fixed: citations are to two-team plan 16.6 and 17.1; annexes named. A-L1 fixed: rungs, RC1-RC3 and R1-R17 are distinct. A-L2 fixed: table ids used everywhere. A-L3 fixed: secondary labels row. A-L4 fixed: ask order stated. A-L5 fixed: `pulso-engine` CLI is E2 and STP1. A-L6 fixed: "to create" marks. A-L7 fixed: TA0 is W1. A-L8 fixed: GT1B says demoted; deletion in Q2. A-L9 fixed: lanes counted by WPs per wave. A-L10 fixed: `wave` column. A-L11 fixed: checker extended. A-L12 fixed: numeric acceptance cells.

**Review B (v3, backward).** B-B1 fixed: stream B (BK0, BKN, BKNL, BKF/BKT/BKD/BKA/BKC/BKJ, BKE, BKX by Codex; BKFL, BKTL, BKDL, BKAL, BKCL, BKJL, BKOL, BKEL live by Claude); gates list kinds proven; denied-kind negatives at T1a. B-B2 fixed: E2 and K3 in Q1 deps. B-B3 fixed: P1 in E7 deps. B-B4 fixed: P2py in Q1r deps. B-B5 modified: the user decided DEMO-0 on roleplay; SMOKE and M4 are DEMO-1a rung-up (M4 deps M2a and M3, not M2f). B-B6 modified: DORIGm is Codex breadth (not gating); E0 detection is real in DEMO-0 via existing sensors and ED0; the local model as E0 responder is superseded by the treated-payload decision. B-B7 fixed: PX0, DPLAT at T1a with PL-C acceptance, DPL1, DPL2. B-B8 fixed: L-BRIDGE lane. B-B9 fixed: K0 T0.5; DMAPC digest from dry-run (`hash=core-authoritative`), K4 at T2. B-B10 fixed: DEVAL at T1a (Codex swap-in) and EVE (Claude stand-in). B-B11 fixed: U-15, H1n, `JEV_API_KEY` in ask 6. B-B12 fixed: BLOB1 and blob-store wording; stage names kept (user directive) with disambiguation. B-B13 fixed: ratchet records `host` per step; CRV1 gates GT05. B-B14 fixed: wording of 158 h versus depth (section 6). B-B15 fixed: gateway `release.yml` and `GATEWAY_CONSUMERS`, agent-core Dockerfile, counts re-measured by G0gr. B-B16 fixed: E7 acceptance has stall metric and restart policy. B-B17 fixed with M5. Coverage gaps: U05 PGQ; U26 SB2; U28 LAB28; U34 RC1-RC3; U36 SB1 and SBL; U32 panels CON2; U10 M6; CAP-13..15, 17..20, 22 BKC and BKCL; CAP-23 BKN; CAP-48 BOOT; CAP-56 BKCL; CAP-64 Q3c and QKG; spec-22 families FX22a, FX22b, FX22p; PL-02..04 DPL1 and E4R; PL-06..10 DPL2; PL-C6 DDOC1; blob store BLOB1.

**Review C (v3, feasibility).** C-HIGH-1 fixed: path map generated from `git ls-files`, "to create" marked. C-HIGH-2 fixed: XSTUB stubs and single integrator. C-HIGH-3 fixed: C-1, C-7, C-11 exist; C-8 and C-10 are new schemas; C-4, C-5 draft until CF1. C-HIGH-4 fixed: machine model corrected (one 10 GB VM, 1.7 GB free); ENV8 no longer stops or resizes. C-HIGH-5 fixed: ENV0 measures both accounts; ENV1, ENV3, ENV5, ENV11, ENV12 conditional; no unsourced numbers; seams crates do not depend on `crates/core`. C-HIGH-6 fixed: Codex lanes consume only the FRZ0 pack; the 22% is no longer headline; shares by tier printed; the first-20-sessions Codex share is 27-30% through T1b because breadth lanes are early. C-HIGH-7 fixed: ENVADR plus ask 3. C-MEDIUM-1 fixed (L-ENV paths). C-MEDIUM-2 fixed: no `exclude`, edition and rust-version in K0, seams leg in the gate. C-MEDIUM-3 fixed: journal NNNN convention and amendments precedent. C-MEDIUM-4 fixed: MIG0 RED compares to the union of existing test setups; PGJ is a delta on `pulso_jobs` (16-24 h). C-MEDIUM-5 fixed (K2/CT1). C-MEDIUM-6 fixed: 58 worktrees, train size, restack. C-MEDIUM-7 modified: reviewer capacity is explicit WPs and pools; the +8-12% appears as U-12 default. C-MEDIUM-8 fixed: sessions labelled a model; only DEMO-0 dated. C-LOW-1 fixed: counts (45 integration test files, 60,541 lines, 189 packages, `tokio` already in the lock closure). Asks: instant sentences first, U-14 default measure-only, U-8 never merges by default, added U-17 and download approval.

**Rejected or modified with evidence (v4 pass):** (1) B-B5 and B-B6(b) are superseded by the user's DEMO-0 decision (roleplay rung, treated payloads), not rejected on merit. (2) B-B12 rename of S3a/S3b is rejected because the user asked to keep the stage names; the collision is removed by calling the object store "blob store". (3) C-HIGH-6 "pull DORACLE/DREPLAY/DEVAL earlier bound to a consumer gate" is modified: with the independence rule they have no Claude consumer, so they stay Codex breadth with swap-ins, while Claude owns EVE, ORC1 and RPL1. (4) A-M5 "G0d as ancestor of GT0" is rejected for the demo path (it would push a non-demo script ahead of DEMO-0; the local gate scripts already exist), G0d lands in W1 and feeds every PR receipt. Earlier reviews 1-4 left open only items already covered above (single spend owner, resume design, git rule for E0, objective tripwires).

### E.5 Modified findings, with evidence

1. v4-2 R3 and F3 (profile bump): see E.2; evidence is the registry digest cascade of a profile change and the stage policy that pins alias, model and price.
2. v4-2 F1 (GSIpy dependency and the WP split): evidence is that the existing arm-report fixtures exist without CMPpy, and that `worlds/**` is an L-MODEL path while the compile is L-E2E.
3. v4-3 O1 (1-1.5 sessions of delay): the checker computes 1.7 sessions; the pack is kept because it unlocks 364-557 Codex hours.
4. v4-3 R1 (annex files): the user's single-document instruction takes precedence.
5. v4-1 F10 (Codex W1 PR count): the review mixed tier hours with wave hours; the checker computes the wave figure.

## Annex F. Review history

| Pass | What it did | What it changed |
|---|---|---|
| v1-A, v1-B, v1-C | thin thread; deployable and operable; risks and parallelism | tiers, packages, lanes, AWS, risks |
| v2 synthesis | merged the three | `doubles[]`, S-MAP spike, Claude-owned seams |
| Reviews 1-4 | code reality; teams and process; real-ness gaps; efficiency and backward pass | re-spec of K2, K3 and PG, the `seams/` workspace, git rule for E0, author separation, package-derived totals, strangler order |
| v3 | single document, 112 WPs, 26 lanes | partition, E0-ENV, tripwires |
| v3 reviews A, B, C | consistency (8 HIGH), backward pass (1 BLOCKER, 7 HIGH), feasibility (7 HIGH) | all dispositioned in E.4 |
| v4 author, coordinator directives | independence rule, DEMO-0 organizing principle, roleplay-rung decision with treated payloads | 214 WPs, 29 lanes, `demo_path` column, Claude-only gates, swap-ins, scanner, rung-up schedule, checker extended |
| v4 final reviews 1, 2, 3 | numbers and rules (1 HIGH, 6 MEDIUM, 5 LOW); DEMO-0 reality (7 HIGH-level findings: DEMO-0 FAIL, honesty PASS with fixes, incrementality one defect, clause coverage one clause); feasibility (5 HIGH: methodology, ownership, asks, readability, Codex capacity) | all dispositioned in E.1-E.3 |
| v5 (this document) | final author applied every finding; 214 to 229 WPs; DEMO-0 re-scoped from 76-111 h to 142-219 h; gates GT05, GT05m split; `needs` and `paths` columns; checker extended (asks, paths, newpaths, numbers block, sessions model, demo-path exactness); single file with annexes | this file, `wp_table.csv`, `check_plan.py` |
