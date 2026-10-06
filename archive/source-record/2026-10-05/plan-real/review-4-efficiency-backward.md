# Review 4 of plan v2: efficiency, parallelism, estimates, backward pass

Critic 4. Target: `D:\.codex\factored\docs\plan-real\v2-synthesis.md` (cited "v2 section"). Evidence: v2 tables re-summed with python; improvement-engine PRs #60-#93 via `gh api`; shared journal (CL-0010..0037, CX-0014..0184); read-only worktree at main 41492cb; `gh api` for agent-core and llm-gateway; machine probe (12 logical CPUs, 15.7 GB RAM with 5.3 GB free now, RTX 3060, no Ollama installed). Units: "p-h" = v2 focused hours. Nothing in the repo was edited or built.

## 1. Verdict

1. v2 is directionally right (thin thread first, honest labels, Claude owns the seams), but its schedule is not supported by its own work-package table: the packages for T0-T1b sum to 282-422 p-h, the tier table says 185-260, the minimum viable cut says 70-100 while its kept packages sum to 157-230 (findings F1, F2).
2. On v2's own hour ranges the real critical path to T1a is 65-100 serial p-h (not 55-75) and runs through Codex's D-PIPE and D-AUTH while Codex is frozen; at v2's own 7 serial h/session that is S9-S14, not S7. S1-S6 carry 2-3x their stated capacity (F2, section 8).
3. Parallelism is nominal: about 70% of p-h are Rust behind one cargo slot on a 15.7 GB machine, lane L3 carries about 85-126 p-h alone, and the 5-agent cap is below the lane table's concurrent peak (F3). The critical path can be cut 20-25% and Codex taken off it (F4).
4. Several inherited facts are stale or wrong: main has moved (853b029, PR #93 merged, containing the "valuable Codex slices"), Codex reached GitHub at 02:52Z, the Rust crate already has a model-budget port and a durable-job reference model, and the agent-core pin changed four times in 21 hours with no budget for it in the plan (F5, F6).
5. Recommended: reorder as a strangler (real model through the existing Python stand-in first, Rust semantics via `pulso-engine step` second, Rust-hosted durable shell third), re-baseline hours by package type (section 4), and apply the review ritual by risk class (section 6).

## 2. Findings by severity

### F1 (BLOCKER) The headline hour totals do not equal the package sums
- Claim: v2 section 8.2: T0-T1b 185-260 h; section 0 item 10; section 8.3 MVC "about 70% of T1a (70-100 h)". Section 3 header says review adds 15-25% on top; section 8.2 says the ranges "include one review loop". Both cannot hold.
- Evidence (python re-sum of v2 section 3 ranges): G 17-28; T0 packages (M1, K0-K2, E0, E1, half of D-WIRE) 42-62; T1a listed packages (K3, E2, E4, E5, V1-V3, H1, P1, P2, MEM1, Q1, D-PIPE, D-GATE, D-MAP, D-AUTH, D-WIRE rest) 154-226; packages that T1a needs but section 8.2 does not list (M3 10-16, S-MAP 6-8, M2 ceiling 4-6, E3 4-6, IN0 6-10, D-PLAT 8-14) 38-60; T1b (D-PG, E6, E7, E8 subset) 37-57. Total 288-433 raw, 330-540 with the 15-25% that section 3 says is extra. The tier table (T1a 100-140) is 35-40% below the sum of the packages it names.
- Consequence: the "A says 190-250, consistent" reconciliation (section 8.1) is coincidence: v2 adopted A's number, then added G, S-MAP, M3, IN0, E4 HTTP server, MEM1 and a Rust human port that A did not carry.
- Edit: replace 8.2 by the package-derived table of section 4 below; state once whether hours include review (recommend: hours = implementation + own tests + one review loop; second and third loops are a 10-20% add-on on trust-boundary packages only); make 8.3 sum its kept packages (section 5 below: 150-210 p-h for v2's own kept list).

### F2 (BLOCKER) The session schedule overshoots v2's own capacity model, and T0 at S2 is not reachable
- Claim: section 4.2 (about 18 focused h/session, about 7 serial h/session), section 4.3 (T0 at S2, 70%; T1a at S7, 55%), section 2.3 (T1a serial chain 55-75, T0 22-32).
- Evidence: critical path computed from v2's own dependency columns: G0a>G0c>D-PIPE>D-AUTH>H1>P2>MEM1>Q1 = 65-100 p-h (T1a); G0a>G0b>K0>K1>K2 = 22-33 p-h (T0 wire). 55-75 serial hours at 7 serial h/session is 8-11 sessions; 65-100 is 9-14. T0 chain 22-33 is 3-5 sessions at one serial lane, so a gate at S2 needs K1 and K2 on different agents, which K2 depends on K1 forbids.
- Load per session (section 8 below): S1 about 40-60 p-h of content vs capacity 18; S2 37-58; S3 40-60. Sum S1-S6 for Claude's lanes plus Codex-fallen packages is 229-340 p-h against 6 x 18 = 108 (band 72-144): a ratio of 1.6-4.7, central 2.6.
- Edit: state the gate sessions as S3-S4 for T0-Rust and S8-S10 for T1a with the unchanged structure, or (recommended) restructure per F4/F7 so T0 (real model on real Core, Python-hosted) lands S2 and Rust-hosted T1a S7-S9. Add the arithmetic (content p-h / capacity) to each session gate so slippage is visible.

### F3 (HIGH) Parallelism is nominal in four places
- One cargo slot: Rust packages (K0-K6, E1-E9, V1-V3, H1-H2, MEM1 and all D-*) are about 70% of T0-T1b p-h; only M1/M3/S-MAP/E0/G1/P1/P2/Q1-harness/IN0/O1/TA are Python, TS, PowerShell or Terraform. Journal evidence that cargo is the real throttle: CX-0035 (first full preflight stalled over 20 min compiling and linking, "D: operations unusually slow", passed only with `CARGO_BUILD_JOBS=2`), CX-0067 ("P4 tests own Cargo"), CX-0079 ("Cargo is now free"). crates/core is 58,149 lines plus bundled sqlite (`rusqlite` bundled) and `postgres`, so any crate that links it pays the relink. v2 K2 "implements the existing ports CoreTaskPort ..." in `core-client`, i.e. depends on `crates/core`.
- Agent cap: section 5.2 table peaks at 2-3 (L1) + 2-3 (L2) + 1-2 (L3) + 1-2 (L4) + 2-3 (X1) = 8-13 concurrent, against the stated cap of 5. With Codex unfrozen, Claude gets about 3 slots including reviewers.
- Lane L3 owns M1-M5, P1-P3, Q1-Q3, IN0: about 85-126 p-h, the longest lane by 2x (L1 is 44-63, L2 is about 90-130 but split in two agents). It is a serial queue behind one Podman VM.
- Shared reviewer: 4-5 lanes each needing 1-3 loops through one reviewer on one critical path; at 15-25% of about 20 lane-h/session it is 3-5 reviewer-hours per session with serial latency on each package.
- Edits: (a) make `core-client` independent of `crates/core` (own serde DTOs against `bridge-contract` goldens; `engine` crate adapts to the Codex ports). Its inner loop then never relinks the 58k-line crate and K1/K2/K3/K5 can use a private `CARGO_TARGET_DIR` and run in parallel with Codex builds. (b) Move target dirs to the fastest local disk, use `cargo check` and `cargo test -p <crate>` in the inner loop, full workspace only in `verify-local-all` once per wave; add `sccache` if the spike shows relinking dominates. (c) Cap at 3 implementers + 1 reviewer + orchestrator, and say which lanes they are (section 7). (d) Split L3 into L3a stack and model (M1, M3, S-MAP, IN0, M2) and L3b platform and e2e (P1, P2, Q1-Q3), and rotate two reviewers.

### F4 (HIGH) The critical path can be shortened about 20-25% and Codex taken off it
Applying only dependency edits that v2's own text justifies (python recomputation on v2's ranges):
1. G0c intake is no longer needed (F5): remove 4-8 h from the root.
2. K3 depends on "S-MAP verdict" (v2 3.3) but K3 compiles a DraftPlan; the existing Python writer flow already pushes hand-authored drafts (CL-0023: steps 5 and 9 already real). K3 needs fixtures, not the verdict. Likewise V1 needs "D-MAP" only for suite relevance; v2 itself uses an assets hand-written suite in T1 (`suite_source=assets_handwritten`), so V1 depends on K2 and K3 only.
3. H1 depends on D-AUTH (Codex, after D-PIPE) but the ABI already has `waiting_human` and the T1 requirement is "approve fixes op and hash"; give H1 a minimal inline binding check and move D-AUTH to T1b/T2 (full U21). This removes D-PIPE (10-16) and D-AUTH (6-10) from the T1a path and makes v2's own fallback ("minimal linear driver behind the same ABI") the T1a default; D-PIPE becomes a T1b swap behind the frozen `JobHandler` ABI.
4. Split E2 (14-20, the largest node): E2a linear driver over the fake bridge needs only E1 (8-12 p-h, starts beside K1); E2b live wiring needs K2 (6-8).
5. Q1 (14-20) as a terminal big-bang becomes a ratchet: create `E2E-THREAD-01` in S2 asserting all ten steps with their current labels, and flip a step from `stand-in` to `real` as each package lands; residual Q1 is 5-8 p-h.
6. P2's Python half (simulator emits `release.*`, fast-forward clock) depends only on E4 for correlation, not on H1.
7. K1 (10-14) is then the single chokepoint with four successors (K2, K3, E4, E5): split it across two agents (JWT sign/verify and profile/version probe; HTTP transport, classifier and idempotency/digest).
Result: T1a critical path 51-75 p-h (was 65-100), now entirely on Claude-owned seams, K1 > K3 > V1 > V2 > V3 (45-64) and K1 > E4 > P2 > MEM1 > Q1 (46-67).

### F5 (HIGH) Inherited facts that are stale or false
- Main moved. `gh api` shows main at 853b029 (2026-10-04T03:01Z), not 41492cb: PR #92 merged and Codex consolidation PR #93 merged. #93 contains `crates/core/src/paired_scenario.rs` (663 lines + 311 test lines) and `platform_source_policy.rs` (603 + 277), `source-adapters` additions (477), and `local_simulation.rs`. CX-0183 states the temporal-successor memory work is "superseded" and was excluded. Consequences: G0c (4-8 h, "intake of Codex WIP") becomes about 0.5-1 h of verification; D-GATE (10-14) starts from landed seed code (revise to 7-10); D-PLAT starts from landed policy primitives (revise to 6-10); risk R11 (lost Codex work) is retired for those slices; v2's pre-flight (f) can be closed now. The other dirty Codex worktrees were audited and judged superseded (CX-0183), which also shows the cost of 70 worktrees (an audit of 70 paths was itself a task).
- Codex GitHub access. v2 section 5.5 and U-3 assume GitHub is unreachable from Codex. CX-0181 ("direct GitHub verification"), CX-0183 ("Live GitHub/main fetch confirmed") and CX-0184 ("Published PR #93 ... pushed updated head") show it worked from Codex at 02:5xZ. Podman is still inaccessible to Codex (CX-0182). Edit: G0a mirror (1-2 h) and G0b offline-vendoring spike become a 15-minute S1 check ("can Codex `git fetch` and `cargo fetch`?"), with the mirror kept only as fallback.
- Rust already has budget and model seams. `crates/core/src/model_provider.rs` (1,753 lines) defines `ModelPort`, `ModelBudgetPort` (reserve/release by attempt identity), `ModelAttemptRepository` with a `PostgresModelAttemptRepository`, `OpenAiCompatibleTransport` and cost-micros caps; migration `0002_model_attempt_ledger.sql` exists. v2 M2 builds the budget ledger "in our runtime (Python)" and never mentions these, and plan V3 line 5 says the engine does not call models. Edit: M2 must state one owner for the ledger (Python runtime for Core-originated calls, Rust `ModelBudgetPort` for any engine-originated call, or declare `OpenAiCompatibleTransport` unused and say why) so the same money is not metered twice or zero times.
- Durable jobs. `durable_jobs.rs` (1,170 lines) already defines `DurableJobRepository` (`admit_atomically`, `acquire_job_lease(job_id, ...)`, fencing, `recover_job_after_restart`, `reconcile_unknown_job`) with an in-memory reference; no PG implementation exists and, importantly, no "claim next ready job" operation (acquire takes a known `job_id`). v2 D-PG (14-24 p-h) is plausibly sized but should name the missing claim primitive (SKIP LOCKED) as an additive trait method, owned by Codex, so E6 does not invent it.
- Plan V3 main/pin: `AGENT_CORE` pin c814c2b held at gh-time (agent-core main c814c2b at 21:03Z); llm-gateway main is 63155b6 with `POST /v1/jev` already merged (d11c261, PR #2). v2 section 9.3 item 2 ("Jev also needs a gateway change not on main") should be rechecked: the gateway side exists; the blocker recorded in the plan is agent-core PR #28 on the Core side.

### F6 (HIGH) No budget for pin churn and environment tax, both observed
- Evidence: the Core pin moved 86a7674 > b32b1e9 > 789d6c8 > 894fa65 > c814c2b between CL-0010 (04:44Z) and CL-0036/37 (01:22-01:45Z next day): four bumps in 21 wall hours. Bump-driven Claude PRs: #82 (23.7k lines, 758 files, with dry-run and alias routes), #86 (Annex D alignment), #91 (c814c2b, ADR 0012); CL-0019 documents a full impact analysis per bump (14 mock-parity failures at one bump). Environment: crun "pids controller unavailable" requiring `--cgroups=disabled` (CL-0011/0016), Windows ephemeral-port exhaustion in #79's evidence, a stalled first Rust preflight (CX-0035). v2 R9, R12 and R5 name these but no WP carries hours, and K1's first act is to "retire 0.5.0/53e729d" (an already stale pin).
- Edit: add package G2 "pin-watch and bump lane" (reuse `scripts/core/pin-watch/pin-watch.ps1`; 2-4 p-h per bump, expected 2-3 bumps before T1a = 6-12 p-h) and a standing 10% environment/churn allowance per Claude lane in the estimates. Contract-version gating must stay on SHA plus manifest digest (CL-0019: `VERSION` stayed 1.3.0 across bumps), and K1's pin constant must be one generated file, not scattered.

### F7 (HIGH) Order of the strangler: de-risk the real model before the Rust shell, not after
- Claim: v2 section 4.3 puts the tripwire at the end of S4 and keeps Python-hosted shell (F-PY) as a fallback that "dilutes the spec" and costs 25-35 h of rework.
- Evidence: the thread already exists in Python on the real Core with a scripted LLM (CL-0023: steps 1-4, 6, 7, 10 `stand-in`, 5 and 9 real, 8 simulated or manual; estado 00). M1/M3/S-MAP are Python and Podman work and need no cargo. The three unknowns that can sink the plan (local model schema compliance, E0 finding-to-artifact mapping, container networking) are all measurable without any Rust.
- Proposal: invert the order (details in section 3): V0 = real gateway + local model driving the existing stand-in, with `doubles[]` generated by the engine-run schema, landing about S2 and giving the user a first real-model demo; V1 = Rust semantics (`pulso-engine step`: sensors, compile, gate) called by the Python host; V2 = Rust-hosted durable shell. The tripwire then has nothing to trip: F-PY is the first deliverable, Rust is a strangler replacing step hosts one at a time, and each replacement is a contract-identical swap proven by the same `E2E-THREAD-01` ratchet. This also removes the user's S4 go/no-go (U-11) from the critical path. It costs E3 (4-6 p-h) earlier and adapters; it saves the F-PY rework.

### F8 (MEDIUM) Claude has never shipped Rust in this repo
Every Claude PR (#74-#91) is Python, TypeScript, PowerShell or Terraform; all 68.7k lines of Rust (core 58.1k, runner 4.5k, source-adapters 6.1k) are Codex-authored. Moving K1-K6, E1-E9, V1-V3, H1-H2 to Claude is the largest change of v2, and U-2 is justified, but the estimate must carry (i) a context-load tax of 1-2 h per new subagent session reading ports and conventions (Edition 2024, `rust-version 1.85`, strict Clippy warnings-denied gate), (ii) first-time Windows link and lock behavior, (iii) an explicit acceptance of Codex as reviewer on every Claude Rust PR (v2 has this as D-REV, 3-5 h per wave; keep it). Mitigation: first Rust package is the mapping-agnostic `core-client` against goldens (F3a), with Codex conventions written into `OWNERS.md`.

### F9 (MEDIUM) Estimate bias differs by package type
See section 4. Short form: pure domain slices against frozen contracts are over-estimated (history 20-90 min wall per slice), live-integration and concurrency packages are under-estimated, and the unit itself (agent-hour versus wall hour) is undefined in v2.

### F10 (MEDIUM) The methodology ritual is priced uniformly (15-25%) but its real cost varies 15% to 85%
See section 6 for the quantification and the risk-class proposal.

### F11 (MEDIUM) Acceptance tests are not all cheap or automatable
See section 9. Key points: the `E2E-THREAD-01` full stack (PG16 + Core + gateway + local model + sim + exporter + engine) is a 10-25 min, multi-GB run; a deterministic replay mode (recorded responses, v2 M3) must be the pre-PR gate and the live local-model mode a per-wave gate. T2 "third party reproduces from a clean clone", T5 72 h soak and TA acceptance are not cheap; compressed-clock substitutes are proposed.

### F12 (MEDIUM) Decision-latency ordering
See section 10. v2 lists 11 asks with defaults but does not order them by lead time or note that one (model/Ollama download) needs the user's explicit permission for a multi-GB download before M1 can start.

### F13 (MEDIUM) Implicit prerequisites in the backward pass
See section 8. Notable: container-to-host reachability for the Rust broker callback, host-VM clock skew (JWT exp, leases), a simulator fast-forward clock for step 10, a restart supervisor for "continuous", local-model inference capacity next to Podman and cargo, and who renders the step-5 diff before C1.

### F14 (LOW) Worktree and journal overhead
70 registered worktrees (CX-0183) and 187 CX plus 37 CL journal entries in 22 wall hours. Cap live worktrees at about 8 (one per lane plus one integration) and replace per-slice journal entries by the single 10-row state table v2 section 5.4 already proposes; enforce it, because the history shows the opposite habit.

## 3. Better lane and session schedule (contract-first, strangler, spikes early)

Machine reality (measured now): 12 logical CPUs, 15.7 GB RAM with the Podman VM resident, 5.3 GB free, RTX 3060 (4 GB reported by WMI, check true VRAM), no local model runtime. A 7-8B quantized model plus PG16 plus Core image plus cargo does not fit alongside a second Podman E2E; heavy-gate mutex (v2 G0e) is correct and must also cover the model server.

Agents (cap 5): orchestrator; R1 (Rust, `core-client` and its own target dir); R2 (Rust, `engine` and `control-api`); P (Python/Podman/PowerShell: stack, model, sim, e2e); one reviewer. A Codex slot (domain, offline) replaces R2 or the reviewer when unfrozen; never six.

| Session | Zero-cargo work (P, orchestrator) | Rust work (R1, R2, Codex) | Spikes and asks | Gate (observable) |
|---|---|---|---|---|
| S1 | M1 (gateway image from pinned SHA, local model alias, smoke), G0e/f, `OWNERS.md`, engine-run schema (G1 part), E0 contracts (openapi, broker confirmation) as `[CONTRACT-PUBLISHED]` | R1: K0, K1 (JWT/profile/version probe first, DTOs from goldens). R2: E1 ABI draft. Codex: D-GATE remainder on landed seed (offline) | S-NET (1 h: Core container to host-listener reachability; host/VM clock skew); S-MAP start on Python builder with M1; G0b 15 min check; send all asks (section 10) | local model returns schema-valid scout JSON 3 of 3 or the fallback is chosen; reachability and clock verdict |
| S2 | M3 (hardening, record 10 real responses with provenance), S-MAP verdict, V0 run: stand-in + real gateway + local model with engine-generated `doubles[]`; Q1 ratchet file created | R1: K1 done, K2 against the real image (same key twice, one run). R2: E1 frozen, E2a linear driver over fake bridge. Codex: D-PIPE transcripts rev1 | pin-watch run (G2) | V0 demo green (steps 1-10 on real Core and real model, honest labels); K2 live |
| S3 | P1 exporter retarget; M2 ceiling; simulator realism (P2 Python half, fast-forward clock) | R1: K3 on fixtures (draft+dry-run) and writer+readback. R2: E4 binding + ingest vs the same black-box tests as the double, E5 broker | pin-watch | T0-Rust: `pulso-engine doctor` and `once` with real scout; steps 1-3 through the Rust executor |
| S4 | IN0 compose (one up), negatives for steps 1-5 | R1: K3 complete. R2: E2b live wiring, V1 on fixtures; Codex: D-MAP validation on S-MAP corpus, D-WIRE adapt | D-REV review wave | steps 1-5 live in Rust, candidate frozen (no go/no-go: fallback already shipped) |
| S5 | Q1 ratchet advances; P2 correlation | R1: K5 (reconcile, faults). R2: V1 live, V2, V3 rule, H1 minimal inline authority | | steps 6-9 real |
| S6 | MEM1 note artifact, step 10 with simulator effect | R2: MEM1, successor job; Codex: D-PIPE reducer swap behind ABI | wave PR W-T1a | `E2E-THREAD-01` green in replay mode, live once |
| S7-S9 | O1 minimal runbooks, soak harness (compressed clock) | E6, E7, E8 subset, D-PG on Codex, claim primitive | D-PG fallback decision at S6 end (move earlier than v2's S5) | T1b: kill -9, new batch starts a run |

This yields a first honest real-model demo at S2 (v2: nothing real before S2 and a full thread at S7), Rust T0 at S3, and moves the only remaining go/no-go (D-PG ownership) earlier. Rust hours do not shrink; what changes is that nothing real waits for them.

## 4. Estimates: v1 versus v2 versus history, and recalibration

### 4.1 Comparison of the four estimates
| Source | Scope | Range (p-h) | Bias note |
|---|---|---|---|
| v1-A | T0+T1 incl. minimal PG queue, ingest, broker | 190-250 | no G, no MEM1 PG, no S-MAP; plausible for a labelled thin thread, not for the sum in v2 |
| v1-C | T1 run-once 110-150; T2 140-200; T3 80-120; T4 50-80 | 380-550 | T1 excludes durable queue; its 110-150 is near v2's T0+T1a headline but v2's packages are larger |
| v1-B | T0-T3 on AWS | 450-700 | broadest scope; only source pricing O1 and TA |
| v2 headline | T0-T1b 185-260; through T3+TA 480-740 | | adopts A's range |
| v2 packages re-summed | T0-T1b | 288-433 raw (330-540 with review per section 3 header) | headline 35-45% low |

### 4.2 What this project's history says
- Unit problem. v2 never defines p-h; section 4.2 implies 18 p-h per 8 wall-hour session. Observed wall: Claude orchestrated 4-9 concurrent lanes from 04:44Z to 01:45Z next day (about 21 h) and merged 12 PRs; Codex ran 5-7 concurrent worktrees (187 CX entries) and merged 7 consolidated PRs, about 19.9k added lines (#75, 78, 83, 87, 88, 90, 93), about 0.9k lines per wall hour across all its lanes including tests and docs. PR #76 (126k lines, 1,055 files) is mostly generated or vendored wire and is not a throughput figure. Open-to-merge latency is user-bound and small in session (5 min to 2.6 h; #79 1 min, #76 89 min, #82 77 min).
- Greenfield, contract-shaped, fixture-first code is very fast: console L7 (7.6k lines, 10 Playwright + 5 unit) was delivered locally about 40 min after dispatch (CL-0010 04:44Z to CL-0011 05:23Z, with four other lanes in parallel).
- Pure domain Rust slices with an author who has context: 22 min (P3, RED 18:31Z, closed 18:53Z), 30 min with three review loops (E0 route binding, CX-0095 to CX-0106: forged-binding blocker found in loop 3), 1.1 h with three wording loops (P1 explanation, CX-0145..0149), but 1.5 h+ when semantics are subtle (P4 expiry, CX-0128..0134 then CX-0153..0160).
- Live-integration against the real stack was slow and had tails: L2/L3a/L3b/L5/L6/L8 "runtime integrated" took 9.5 wall hours (CL-0011 05:23Z to CL-0016 15:00Z) with 2-5 lanes, then pin churn (F6) consumed about a quarter of the day (judgment from the PR sequence and CL-0018/19/20/36).
- Full local Rust CI: 6-16 min when cargo is free (CX-0076 to 0077, CX-0092 to 0093), but 20+ min stalls and re-runs after upstream merges (CX-0035, CX-0184 reran the whole gate after merging main).

### 4.3 Recalibration by package type (multiplier on the v2 range; lane-hours including one review loop and local gates)
| Class | Packages | v2 p-h (sum) | Multiplier | Recalibrated | Reason |
|---|---|---|---|---|---|
| A contracts, scripts, harness, compose | G0*, G1, E0, IN0 | 26-39 | 0.7-1.0 | 18-39 | wire generator, contract pack, compose fragments already built fast |
| B pure domain Rust, authored by Codex against landed seeds | D-PIPE, D-GATE, D-MAP, D-AUTH, D-WIRE, D-PLAT | 49-80 (with D-GATE revised) | 0.4-0.8 | 20-64 | 22-90 min per slice observed; only valid if Codex is unfrozen and has context |
| C new seam Rust by a Claude subagent | K0-K1, E1-E3, M2 ceiling, V2-V3 | 48-70 | 0.8-1.4 | 38-98 | no Claude Rust history; context load; first Windows link |
| D live integration with the real image, PG or model | M1, K2, K3, E4, E5, V1, H1, P1, P2, MEM1, Q1 | 106-152 | 1.3-2.0 | 138-304 | 9.5 h integration, port exhaustion, cgroups, pin churn; E4 and Q1 black-box against two targets |
| E concurrency and durability | D-PG, E6, E7, E8 subset | 37-57 | 1.5-2.5 | 56-142 | v2's own R-3/R-4 and B's warning; PG and Core on one VM |
| F real-model behavior | M3, S-MAP | 16-24 | 1.0-2.5 | 16-60 | unknown schema compliance of a 7-8B local model; timebox and fallback bound it |
| Total T0-T1b | | 282-422 | | 285-710 | central about 430-480 (with 10% churn and env allowance: about 470-520) |

At 16-20 lane-h per session (not 18-24: one cargo slot, one Podman VM, reviewer queue) the central T0-T1b is 22-30 sessions of full-strength lanes for the plan as drawn. That is the honest number if nothing is cut; it is why the minimum viable cut matters. If Codex stays frozen, class B moves to Claude at 0.8-1.4 (add 25-60 lane-h).

### 4.4 Per-class bias summary
- Optimistic: live integration (D), concurrency (E), first-apply AWS (TA3 10-18 is low if the agent-core slice is not stable: 1.5-2x plus user latency), the Q1 big-bang, and every "S-MAP verdict" timebox (6-8 h includes a model-quality unknown).
- Pessimistic: Codex pure-domain slices on landed seeds (B), contract and schema writing (A), G0c (obsolete, F5).
- Not priced at all: pin churn (6-12 p-h), model/ledger ownership reconciliation, G2, S-NET and clock spikes (2 p-h), unpacking the `JobHandler` ABI for both stores, worktree hygiene.

## 5. Minimum viable cut (honestly labelled, end-to-end real thread)

v2 section 8.3 keeps K1-K3, E1-E2, E4-E5, M1+M2, D-PIPE min, D-GATE min, D-MAP, V1, V2, H1, P2 min, Q1, G1 and says 70-100 p-h. The kept packages sum to 150-210 p-h at v2's own ranges (K1 10-14, K2 8-12, K3 12-16, E1 5-8, E2 14-20, E4 12-16, E5 8-12, M1 8-12, M2a 4-6, D-PIPE min 6-10, D-GATE 7-10, D-MAP 12-20, V1 10-14, V2 4-6, H1 10-14, P2 min 8-12, Q1 14-20, G1 5-7). The MVC is not minimal and not cheap.

Proposed staged cut (each stage is shippable and labelled; later stages never invalidate earlier ones):

| Stage | Contents | p-h | Sessions (16-20 lane-h) | What is real, what is labelled |
|---|---|---|---|---|
| MVC-0 "real model through the stand-in" | M1, M3, S-MAP (timeboxed), M2a ceiling, G1 honesty harness, Q1 ratchet (replay + live), S-NET, G2, simulator realism | 45-70 (central 55) | 3-4 | real Core, real llm-gateway, local model on E0 for steps 3, 4, 7; engine = Python stand-in (`stand-in`); human `simulated`; no Rust |
| MVC-1 "Rust semantics, Python host" | K0-K3 (core-client, own DTOs), E3 `step` CLI, D-GATE remainder, D-WIRE, minimal D-MAP validation (or `unlinked` ending), V1-V3 on the Rust side via step calls | 75-105 | 5-7 | Rust does sensing, compile, dry-run, gate against the real Core; host is Python; label "Python-hosted shell, Rust semantics" |
| MVC-2 "Rust shell, run-once" | E1-E2, E4-E5 (binding, ingest, broker), H1 minimal, P1-P2, MEM1 thin | 70-100 | 5-7 | all ten steps through a Rust process, jobs in memory, step 10 labelled if the simulator is the actor |
| MVC-3 "durable" | D-PG, E6, E7, E8 subset, D-PIPE swap, D-AUTH | 50-80 | 4-6 | kill -9 survival, auto-trigger (step 1 `real`) |

Cumulative to a Rust-hosted run-once real thread: about 190-275 p-h, 13-18 sessions; to durable: 240-355 p-h, 17-24 sessions. The user-visible milestones arrive at session 3-4, 8-11, 13-18, 17-24 respectively, and the first two require neither Codex nor AWS. Never cut (v2 9.2 list stays): independent verifier actor, `do_nothing`, honest `unlinked`, human gate, bounded revision, negatives, `doubles[]`, budget ceiling.

## 6. Overhead of the methodology and where a lighter loop is safe

Measured from the journal (not estimated): 187 CX entries and 37 CL entries in about 22 wall hours; 80 lines mentioning blocker/blocking, 77 mentioning adversarial review, 83 clear/accepted lines. Examples: P3 22 min total of which review-driven rework (cross-tenant finding CX-0086 to fix CX-0087 to privacy hardening) about 8 min (35%); E0 plan runner 30 min total, review-driven about 14 min (45%), with the decisive blocker (forged cross-packet route, CX-0104) found only in loop 2-3; P4 expiry 2 h, over 80% review and correction loops (CX-0129..0134, 0153..0160); P1 explanation 1.1 h, 3 wording loops with no code defect. Console and docs slices: review share about 15-25%. Local CI parity: 6-16 min per full run, 2-3 runs per consolidated PR (CX-0184 reran after merging upstream main). Publication and consolidation: 7 dirty worktrees with partial or superseded work (CX-0182/0183) cost an audit plus selective cherry-pick.

| Risk class | Packages | Ritual share of wall time (history) | Loop to apply (within the user's rules) |
|---|---|---|---|
| R1 authority and trust boundary | K1 JWT and classifier, E4 auth and replay, E5 grants and redaction, H1, D-AUTH, M2 budget, E6/D-PG fencing, K5 reconcile | 35-85% | strict TDD, independent reviewer (different agent, adversarial brief), 2-3 loops, mutation or forgery regression named in the first RED, focused gates per slice |
| R2 semantics against goldens | D-GATE, D-MAP, V1-V3, K2, K3, E2, D-PIPE | 30-45% | strict TDD, 1-2 loops, review of the slice diff, focused gates per slice |
| R3 mechanical and contract-driven | DTOs from goldens, openapi, schemas, scripts, compose, console fixture views, runbooks, doc updates | 15-25% | TDD still (a failing golden, conformance or script test first); ONE review loop at wave level over the consolidated diff against a checklist; no per-package full suite |
| Spike | S-MAP, S-NET, E9 SSE, G0b | n/a | timeboxed throwaway; the deliverable is a written finding and a corpus, code is discarded and rewritten test-first (this needs the user's explicit nod because the rule is strict TDD; proposed as ask U-12) |

What stays unchanged (it does not break any stated rule): RED first for every production slice, independent adversarial reviews on every package that touches R1/R2, local CI parity before each PR (run the full `verify-local-all` once per wave, not per slice), consolidated worktrees and PRs (one per wave per repo), no dependence on a merge to continue. What changes: loops scale with risk instead of a flat 15-25%; the per-slice journal entries are replaced by the state table; no more than about 8 live worktrees. Expected effect: about 8-12% fewer lane-hours overall and, more importantly, R3 reviews stop being serial gates on the critical path.

## 7. Parallelism: the true DAG and where it is nominal

Nodes and edges are v2 section 3 "Deps" columns; hours are v2 ranges; my recomputation is in the python used for this review.

```
G0a,G0f,G0e -> G0b -> K0 -> K1 -> { K2, K3, E4, E5(E0,E1) }
M1 -> { M3, S-MAP }          E0 -> { E4, E5, P1 }          K0 -> E1 -> { E2, H1, D-WIRE }
G0c -> D-PIPE -> { D-AUTH, D-MAP(+S-MAP) }   G0c -> { D-GATE, D-PG }
K2,K3,D-MAP -> V1 -> V2(+D-GATE) -> V3       K2,E1,D-AUTH -> H1 -> P2(+E4) -> MEM1(+E5) -> Q1(all)
T1b: D-PG,E2 -> E6 -> E7(+E4) -> E8/Q2
```

Critical paths on v2's own numbers: T0 wire 22-33 (G0a>G0b>K0>K1>K2); T1a 65-100 (G0a>G0c>D-PIPE>D-AUTH>H1>P2>MEM1>Q1); T1b chain G0a>...>K2>E2>E6>E7>Q2 64-93 plus the T1a tail. After the F4 edits: T1a 51-75, with K1 as the shared chokepoint and Codex off the path.

Where parallelism is nominal:
| Resource | Evidence | Effect on the schedule |
|---|---|---|
| One cargo slot | CX-0035, 0067, 0079; core crate 58k lines + bundled sqlite | at most 1.2-1.5 productive Rust implementers unless `core-client` is decoupled (F3a) |
| One Podman VM (`pulso-dev`, Claude's only; Codex has none) | CL-0010, CX-0182 | all live PG/Core/gateway/model tests serialize; Q1 live and K2 live compete with P lane work |
| Machine RAM: 15.7 GB, 5.3 GB free now | probe | a 7-8B model, PG16, Core, gateway and a cargo link do not coexist; the heavy-gate mutex must include the model server |
| 5-agent cap | v2 5.2 | 8-13 nominal concurrent agents in the lane table; real implementers 3 |
| Reviewer queue | v2 5.2 shared reviewer | serial latency per package on R1/R2 |
| User as sole merger and relay | CL-0036, CX-0184 | not a throughput limit in session (merge latency 5 min to 2.6 h) but a hard gate overnight and for AWS, agent-core, Product |

Python-side work that can proceed with no cargo and no Codex (P lane): M1, M3, S-MAP, S-NET, P1, P2 Python half, simulator clock, IN0, G1 schema and generator, E0 contracts, G0d, O1 runbooks, TA plan-only Terraform, console fixture work. This is about 30% of p-h but 100% of the early risk.

Contract-first, stubs and goldens that unblock the other team: publish in S1 (a) `contracts/control-api/openapi.yaml` and the broker confirmation, (b) `contracts/engine-run/` schema, (c) the frozen port list with file and digest, (d) Claude's strawman pipeline command list; Codex can write D-PIPE against (d) offline from day one and D-GATE against landed `paired_scenario.rs`. `ChangeSpec` and `ScenarioCase` JSON schemas from existing Rust structs (v2 5.3 item 5) should move from "session 2, Codex" to "S1 if unfrozen, else Claude generates them from the structs": K3 and V1 need them first.

## 8. Backward pass: demo steps and the durable engine, and session feasibility S1-S6

### 8.1 Each demo step to prerequisites, owner, slot
| # | Prerequisites found | Present in v2 with owner and slot? | Implicit or missing |
|---|---|---|---|
| 1 data wakes engine | ingest endpoint E4 (CL, S3), exporter retarget P1 (CL, S3), trigger E7 (CL, T1b S8-S10), snapshot registration, E0 input_view | yes; step is `manual_command` until T1b | registration of an E0 snapshot as an engine input (who writes it, where the digest lives) is only inside E7; the E0 `input_view` size must fit a 7-8B local context (M3 acceptance should assert token count) |
| 2 families and discards | D-WIRE (CX/CL S2), existing sensors | yes | discard persistence is a file snapshot in T1a; say so in the label |
| 3 adaptive SQL/wiki, separate verifier | K2, M3, E5 broker with grants, distinct verifier actor | yes (S3 gate) | the Core runtime (container) must call the Rust broker on the host: container-to-host reachability on Podman for Windows is not in any package; the lab SQL engine capacity on E0 size (sqlite lab, DuckDB deferred) not measured |
| 4 opportunity, alternatives incl. `do_nothing` | builder_design on a model (M3), S-MAP/D-MAP | yes | quality floor of the local model (DEBATE-4) has no owner for the decision before S2 gate; assign to orchestrator with a numeric rule (3 of 3 valid) |
| 5 concrete change, diff, consumer, cascade | K3, dry-run, console diff | partial: cascade and consumer prediction cut (dry-run authoritative); `diff rendered` without C1 | who renders the diff in T1a: name the NDJSON-to-world-feed path that the existing console `stand-in` provider reads (CL: console seam #85); add an acceptance line |
| 6 base vs candidate, two gates | K2 arms/evaluate, V1 suite, V2 gate, D-GATE | yes | bank double for stateful arms (CAP-41 blocked) is labelled; evaluation quotas (20 evals per proposal) need fresh Core DB per run: only in R13 |
| 7 bounded revision | V3 rule-driven | yes | nothing missing; LLM-driven revision is T2 |
| 8 human only for authority | H1, issuer (exists, #79), D-AUTH | yes | with F4 the inline binding check is T1a; D-AUTH T2; say who is the human in the live demo (user) and the reachability of the issuer key volume |
| 9 staging confirmed by alias | publish + alias read in H1/K3, exists in Python (CL-0023) | yes | no separate "publish and alias-read" client WP; it hides in H1 (10-14); name it |
| 10 new observations, memory, new run | P2, MEM1, E7 auto-start | partial | a simulator fast-forward or injected clock so post-release effects appear inside the demo is not a WP; the "automatically" part is T1b E7 only; temporal-memory work landed differently than v2 assumes (CX-0183) |
| Continuous durable engine | D-PG, E6, E7, E8 | yes (T1b) | restart supervisor (Podman restart policy or `dev.ps1`), readiness semantics, graceful shutdown, clock skew between host and Podman VM after host sleep (JWT `exp`/`jti`, leases), NDJSON and event-log growth, a compressed-clock unattended soak of 2-4 h at T1b (v2 has 72 h only in T5) |

### 8.2 Session-by-session feasibility (S1-S6 as written in v2 section 4.3)
Capacity per session: 18 p-h (v2) and 7 serial h. Content figures use v2's ranges (Claude lanes plus packages that fall to Claude while Codex is frozen).
| Session | Content in p-h | Feasibility | Specific problems |
|---|---|---|---|
| S1 | G0a/b/d/e/f 17-28, K0 2-3, K1 start about 6, E0+G1 11-15, M1 8-12, S-MAP start 3-4: 47-68 | 2.6-3.8x over capacity | M1 needs an approved multi-GB download (Ollama, model weights, Go build of the gateway); Codex intake is moot (F5); G0d (4-6) and G1 (5-7) can wait for S2 |
| S2 | K1 rest 4-8, K2 8-12, E1 5-8, D-WIRE 6-10, M3 10-16, S-MAP rest 3-4: 36-58 | 2-3x over | "T0 70% at S2" fails on the K1 > K2 chain (22-33 serial) and on M3 needing M1 first |
| S3 | E4 12-16, E5 8-12, K3 half 6-8, E2 14-20, P1 4-6, M2a 4-6, P2 part 6: 54-74 (Claude) plus 26-44 Codex | 3-4x over | steps 1-3 real through the executor need E2+E4+E5+K2+M3 together |
| S4 | K3 rest 6-8, V1 start 5-7, E3 4-6, IN0 6-10, negatives 6-8, E2 swap: 30-45 | 1.7-2.5x over | tripwire "steps 1-5 live with candidate frozen" needs S-MAP, D-MAP, K3 and a builder_design answer from the local model: P(no) is high, which commits F-PY (25-35 h) |
| S5 | V1 rest 5-7, V2 4-6, V3 5-7, H1 10-14 (D-AUTH blocks), K5 8-10, D-PG 14-24: 46-68 | 2.5-3.8x over | H1 depends on D-AUTH which depends on D-PIPE: Codex frozen |
| S6 | MEM1 8-12, P2 12-18, E6 start 5, Q1 14-20: 39-55 | 2.2-3x over | Q1 as a big-bang; D-PG PG tests need Claude's Podman |
Sum S1-S6: 252-368 against 108 (band 72-144). The structure is sound, the quantity is not; with section 3's order S1-S4 become feasible (they contain the P-lane risk work and K1-K3) and the rest slides to S7-S9.

## 9. Acceptance tests: automatable and cheap?
| Tier | Acceptance | Cost | Automatable | Proposal |
|---|---|---|---|---|
| T0 | `doctor` green; `once` ends with receipt, tokens, cost | 3-10 min on local model | yes | add token and latency budget so a 120 s call is flagged; run in replay mode in CI |
| T1a | `E2E-THREAD-01` with negatives | 10-25 min live, 4-6 GB | yes, heavy | two modes: `--model=replay` (recorded real responses with provenance, under 5 min, pre-PR gate) and `--model=live` (per wave, needs RAM window U-7); the honesty tests (scripted provider labelled real) are unit-cheap and run always |
| T1b | kill -9, two triggers one run, lost NOTIFY | 2-4 min, PG only | yes, cheap | keep PG-only (no Core, no model); add a 2-4 h compressed-clock soak |
| T2 | chaos C01-C09, third-party reproduction from a clean clone, spend report equals gateway sums | 40-90 min plus human time | partly | split into a nightly-style local aggregator and a one-off reproduction by an agent in a clean worktree |
| T3 | `E2E-DEMO-AUTO-01` two namespaces | heavy | partly | defined only when D-ORIG has a cheap fixture |
| TA | staging run, alarm firing and resolved, rollback drill | user-gated | no (needs user's AWS) | keep plan-only validation local |
| T5 | 72 h soak, load | hours | no | compressed-clock only |

## 10. Decision latency and ordering of asks

Observed: merge latency is small in session (5 min to 2.6 h, median under 90 min); the long latencies are people outside the loop (AWS account and SSO, agent-core, Product, gateway owners) and a download approval. Nothing in the plan is hard-blocked by a user answer because every ask carries a default, but three asks change what S1 should contain.

Send ONE message at T-0 ordered by lead time:
1. External relays first (longest lead, never block local work): EXT-AC, EXT-PR, EXT-GW, U-5 AWS and the alarm mailbox confirmation click (needs days).
2. Model download (U-4a): explicit permission with filename, source and size for the local-model runtime and weights (several GB) plus whether the RTX 3060 may be used; without it S1 M1 cannot start and the V0 milestone slips one-for-one. Hosted key (U-4b) is optional and later.
3. Quick yes/no set: U-1 (unfreeze scope), U-2 (ownership), U-3 (mostly moot, F5), U-10 (debates), U-12 (spike exemption from strict TDD, new).
4. At end of S2: U-8 merge of W1/W2; at S6: D-PG ownership; U-7 RAM windows announced per live E2E; U-11 disappears under the strangler order.
Idle-time rules: Codex-blocked work uses defaults the same day; Claude never waits on a merge; the user is the human actor only for the step-8 live demo.

## 11. If everything slips 50%

Smallest valuable thing: MVC-0 plus a reduced MVC-1.
1. Keep: real gateway and local model driving the existing stand-in on the real Core with honest engine-generated `doubles[]`, the budget ceiling and kill switch, the negatives, the replay mode, and a Rust `pulso-engine doctor` and `once` proving `core-client` against the real image (T0). This is about 60-90 p-h at the slipped rate (5-6 sessions) and already replaces the scripted LLM, the part of the demo a skeptic rejects first.
2. Add only if time remains: Rust compile (K3) and D-GATE as `pulso-engine step` called by the Python host.
3. Drop first, in order: AWS (TA), T2 and T3, console live (C1), H2, durable memory, K4-K5 beyond lost-response, O1 beyond three runbooks (stalled work, budget breach, bad publish and rollback), the PG queue (labelled `jobs=in-memory`).
4. Never drop: verifier actor, `do_nothing`, honest `unlinked`, human gate, bounded revision, doubles generated by the engine.
Value retained: a repeatable, honestly labelled run of the ten-step thread with a real model through the real gateway and real Core, plus a Rust process that talks to the real Core. Codex's libraries remain consumed via `step` and are not wasted.

## 12. Resolution of the debates that touch efficiency

- DEBATE-6 (tripwire timing and AWS). Remove the tripwire: with MVC-0 first the Python-hosted thread is the default carrier and F-PY is not a fallback but stage 1 of a strangler (F7). AWS: run only the questions (day 0) and plan-only Terraform; do not spend a P lane on TA3/TA4 before MVC-1, because first-apply fix cycles (10-18 p-h, central about 20 with latency) exceed the value of deploying a T1 slice that has no Core, no model and no data. Decisive evidence: nothing has ever been applied (estado 02), the agent-core workload slice is unconfirmed (CL-0013, EXT-AC), and Core, gateway and exporter are the parts the user named as real.
- DEBATE-2 (who writes D-PG). Codex writes the PG adapter and the additive "claim next ready job" primitive offline only if unfrozen by S5; otherwise Claude takes it at the end of S6 as a minimal adapter (v2 says end of S5, one session too early given F4 moves it later). Decisive evidence: the trait and in-memory reference already exist (`durable_jobs.rs`), the claim primitive does not, and Codex has no Podman (CX-0182) so its PG tests are Claude-run anyway.
- DEBATE-1 (sync `tiny_http` versus async). Efficiency view: sync wins on build time and cognitive load with a hard switch rule: the E9 SSE spike (2 h) runs in S1-S2, before E4 starts, not after; if SSE with resume (`id=sequence`, 410, 202) needs more than two threads per connection or breaks on Windows, switch the control-api crate only to axum/tokio and keep `core-client` sync. Evidence: only `tokio-postgres` brings tokio transitively today (Cargo.lock), so adding an async runtime to one crate is a contained change.
- DEBATE-4 (local model floor). Fix the numeric rule in advance (3 of 3 schema-valid on scout and verifier, 2 of 3 on builder_design with at most one bounded regeneration), decided at the S2 gate by the orchestrator; fallback (a) recorded replay plus synthetic hosted twin, labelled.
- DEBATE-3 and DEBATE-5 are product and spec judgments outside efficiency; note only that DEBATE-5's spike (S-MAP) is mapping-agnostic for K3/V1 under F4, so its verdict no longer sits on the critical path to T1a.

## 13. Missing from v2 (including items not in the spec)

1. G2 pin-watch and bump lane with hours (F6); a single generated pin constants file.
2. S-NET spike: container to host reachability for broker callbacks and host/VM clock skew check as a `doctor` line.
3. Decision on the existing Rust `ModelBudgetPort`/`OpenAiCompatibleTransport` and the 0002 ledger migration (F5).
4. Named WP for publish plus alias-read client; named WP for the NDJSON-to-world-feed adapter the console reads in T1a.
5. Simulator fast-forward clock for step 10 and an injected clock for quota windows (R13 mentions only soak).
6. Restart supervisor and graceful shutdown semantics for "continuous"; compressed-clock soak at T1b.
7. Capacity budget for the local model (VRAM and RAM next to Podman and cargo) and a mutex that includes the model server.
8. A rule for worktree count, journal volume and who deletes superseded worktrees (70 today).
9. Per-session capacity arithmetic in every gate and a velocity re-baseline at MVC-0 completion using wall-clock measured hours per class (section 4.3), not the p-h bands.
10. Reviewer capacity: two rotating reviewers and a risk-class assignment (section 6).
11. Spike exemption for strict TDD requires the user's explicit approval (U-12).

## 14. The three changes that would most improve feasibility and efficiency

1. Reorder as a strangler and make the first deliverable "real model and gateway through the existing Python stand-in" (MVC-0, S1-S3, no cargo, no Codex, no AWS), turning F-PY from a tripwire fallback into stage 1; keep Rust semantics via `pulso-engine step` as stage 2 and the Rust durable shell as stage 3.
2. Re-baseline the plan on its own packages and capacity: replace section 8.2 and 8.3 with package-derived sums (288-433 p-h raw to T1b; MVC kept list 150-210), put the capacity arithmetic in every session gate, and shorten the critical path with the F4 edits (K3 and V1 off S-MAP/D-MAP, H1 off D-AUTH, D-PIPE swap in T1b, E2 split, Q1 ratchet, K1 split), which also takes Codex off the T1a critical path.
3. Remove the machine bottleneck by design: decouple `core-client` from `crates/core`, private target dirs, replay-mode acceptance as the pre-PR gate with live mode per wave, a heavy-gate mutex that includes the model server, three implementers plus one reviewer instead of the 8-13 nominal, and refresh the stale facts (main 853b029, GitHub reachable from Codex, #93 merged, existing model-budget and job-store seams) before S1.

## 15. Addendum (coordinator facts, folded in)

### 15.1 Facts and their effect on sections above
- Main is 853b029 (PR #93 merged). Already used in F5; no estimate moves beyond G0c (about 0.5-1 h), D-GATE (7-10) and D-PLAT (6-10). Totals in 4.3 stay: 285-710 lane-h, central about 430-480.
- Codex publishes through a GitHub connector (#87, #88, #90, #93): G0a mirror and U-3 are fallbacks only; its real constraints are the scope freeze and no Podman or live PG. Section 3 and 10 already treat them that way.
- The E0/CSV local-host restriction is lifted for local tests and our own infra. Effects: (a) the data-class table in v2 1.3 and "E0 never on AWS" (TA) are void for our own infra; (b) the only reason to prefer a local model is now quality or cost, not privacy, so the U-4a hardware ask and the Ollama download become optional; (c) hosted third-party providers still need treated data plus the user's explicit OK, which also applies to any Claude subagent used as a model (see 15.2 risk 1); (d) DEBATE-3 reduces to "which providers", and E0 can be a TA smoke dataset once U-5 exists.

### 15.2 Idea: a real gateway-compatible endpoint backed by role-playing subagents (`agent_roleplay`)
Design: a small OpenAI-compatible shim (Python, 2-4 p-h) behind the real llm-gateway container (alias = `roleplay`, stage policy file unchanged); each request is written to a queue directory with its digest; a responder subagent answers per the stage schema; the shim returns it with `provider=agent_roleplay`. Every transcript is stored keyed by request digest, so the second run of the same request is a deterministic replay (this is exactly v2 M3's recorded corpus, produced as a by-product). The same shim pattern serves `/v1/jev` for the engine-side Jev client and a bank/sandbox stand-in, always labelled.

What it unblocks earlier (measured against the critical paths above):
| Item | Before | With roleplay |
|---|---|---|
| M1 (gateway + model) | 8-12 p-h plus a multi-GB approved download, VRAM and RAM next to Podman | gateway image build plus shim 6-9 p-h; no download, no GPU, frees about 5 GB RAM for cargo and Podman |
| M3 corpus | 10 real responses, 10-16 p-h, small-model retries | 6-10 p-h; corpus produced by roleplay with provenance |
| S-MAP | confounded by 7-8B quality (DEBATE-4) | tests the mapping approach itself with a strong builder; verdict about 1 session earlier |
| V0 (real gateway through the stand-in) | S2 | end of S1 or early S2 |
| Rust T0 (K1-K2) | S3, Rust-bound | unchanged: the chain G0b>K0>K1>K2 is cargo and contract bound, not model bound |
| T1a critical path K1>K3>V1>V2>V3 (45-64) | | unchanged; roleplay removes M1/M3 (19-29 serial, now 12-19) from the near-critical set only |
| Replay-mode CI gate | needs 10 real responses first | available at the end of S2 |
| Jev (blocked by agent-core PR #28 on main) | `blocked(jev)` | the gateway route (d11c261 merged) and our client can be tested with `agent_roleplay`; the Core-side Jev node stays `blocked(jev)` |
Net: V0 moves 0.5-1 session earlier; MVC-0 drops from 45-70 to 38-58 p-h (2.5-3.5 sessions, 3-4 before); no tier after T0 moves earlier because the Rust and live-Core chain dominates (F4). It removes the U-4a gate and the local-model risk from the early path.

Costs and risks (quantified):
1. Per-call latency: a subagent turn is about 20-90 s (startup plus generation); a thread has about 15-30 calls (scout 6-10 with tool loops, verifier 3-5, builder 1-2, revision 2-4, memory/successor 3-6), so a live run is 10-60 min wall versus 3-10 min on a local model. Budget 4-8 live runs per session, everything else replay. Gateway `timeout_s`, Core node and our HTTP timeouts must be raised to 300-600 s for the roleplay alias and the thread test must treat timeouts as `waiting_dependency`, not failure; verify Core agent nodes tolerate multi-minute calls in S1 (add to S-NET).
2. Agent-cap interaction: the responder occupies one of the 5 slots during live runs (3 implementers + reviewer + orchestrator already fill it). Schedule live runs in windows when an implementer is idle, or batch one responder per stage; do not run live roleplay while a Podman E2E and two cargo builds run.
3. Honesty and independence: a Claude subagent is a hosted third-party model processing E0 data: needs the user's explicit OK and treated data (15.1c). Status must be a new vocabulary entry `agent_roleplay` (below `local-model`); honesty tests: a report claiming `real` model with provider `agent_roleplay` fails; no quality, lift or "model can discover" claim is allowed; scout, verifier and builder must be answered by distinct fresh-context subagents that are neither the implementer nor the reviewer of the code under test (author is not judge). Roleplay hides the weak-model failure mode: keep a one-off small local-model smoke (3 of 3 schema-valid) in T2 to convert `agent_roleplay` into measured `local-model` evidence.
4. Determinism: replay keyed by request digest breaks whenever prompts or schemas change; budget a re-record step (2-4 p-h per prompt revision) and a drift test that fails with the digest diff, not a silent live call.
5. Cost: subagent tokens (user's Claude usage), gateway ledger records provider `agent_roleplay` with zero price; the budget ceiling tests must still run against a priced fake alias so the ledger path is exercised.

### 15.3 Updated schedule and minimum viable cut
- S1 (P lane): gateway image + roleplay shim + smoke (`usage_known`, provider label), S-NET (adds timeout tolerance), S-MAP on the Python builder with roleplay; R1 K0/K1; R2 E1 ABI; orchestrator: asks (drop the Ollama ask, keep the roleplay-OK ask). Gate: scout, verifier, builder answered through the real gateway with `agent_roleplay` receipts; reachability, clock and timeout verdicts.
- S2: M3 corpus capture and replay mode, S-MAP verdict, V0 demo (stand-in + real gateway + roleplay, labelled), Q1 ratchet, K2 live. Gate: V0 and replay CI at about 80% (was 75%).
- S3-S9 unchanged from section 3 (Rust-bound). Optional small-model smoke moves to T2.
- MVC-0 (section 5): 38-58 p-h, 2.5-3.5 sessions, labelled "real Core, real gateway, `agent_roleplay` model, Python stand-in engine". MVC-1 to MVC-3 unchanged. In the 50%-slip case (section 11) MVC-0 is about 4-5 sessions and no longer depends on user hardware.
- Ask list changes: remove U-4a hardware download as a gate (keep as optional); add U-13 "may Claude subagents process E0/CSV data as the model behind the gateway, labelled `agent_roleplay`" (needs explicit yes; default: roleplay only on synthetic data); update U-9 (E0 may run on our own AWS once U-5 exists).
