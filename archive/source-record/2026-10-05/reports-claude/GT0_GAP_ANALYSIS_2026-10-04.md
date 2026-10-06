# GT0 gap analysis (independent, findings only), 2026-10-04

Scope: branch `claude/w0-train` (worktree improvement-engine-claude-w0-train, HEAD 58b9904) vs DEMO-0/GT0 in
PLAN_HACIA_SISTEMA_REAL_CLAUDE_2026-10-04.md and wp_table.csv (GT0, Q1r, INT0, SMAP, M2a, DC0, TPS, ED0, ED0L, RPP, CRV0, TRN0, G1, G0p).
Evidence: files read in the worktree; I re-ran `contracts/engine-run/tests scripts/dc/tests scripts/gov/tests` (45 passed, no cargo, no containers).
I did NOT re-run e2e-core, core-bridge, roleplay-llm or live tests (need venv/Podman); those rows rely on THREAD01.md / W0_STATUS.md claims and are marked "claimed".

## 0. Verdict
GT0 is NOT reachable today. The ten-step thread, G1 contract, scanner, shim, DC0, ED0/ED0L/SMAP stand-ins exist and live real-Core steps 5/6/8/9 are real-narrow. But the GT0 gate package is absent: no gate script, no CRV0 reviews, no TRN0 train script, no W0 receipts, no DEMO-0 `demo/run.ps1` (demo/ is still the planted judge), spend guard unwired, C-2/C-12 not frozen; on real E0 the thread ends unlinked (steps 5-10 not_exercised) and the live gate fails honestly (needs a labelled override). Remaining to GT0: roughly 45-70 lane-hours (about 4-6 sessions at LVL-A), mostly review, wiring and evidence, little new semantics.

Fact check on the "PR #94" premise: PR #94 is MERGED (main 707c5b4) but origin/main lacks `contracts/engine-run/engine_run.py`, `roleplay-llm/README.md`, `claude_standin/thread01.py`, `core_hooks.py`, `ed0_feed.py`. Branch `claude/w0-train` equals origin/claude/w0-train and is 83 commits ahead of main (222 files, +14.5k lines): G1, Q1r, INT0 hooks and the E0 window are UNMERGED and need a new train PR (w0-train2 is already an ancestor). Hosted CI on #94 was red (rust-ci), so merge evidence = G0p receipt, and none exists.

## 1. GT0 acceptance items (wp_table GT0 acceptance + DEMO-0 definition)

| # | Item | Status | Evidence / what is missing | Est. h | Ask |
|---|---|---|---|---|---|
| 1 | Replay green, 0 digest misses | partial (claimed) | `e2e-core/tests/unit/test_e2e_thread_01.py`, `test_e2e_thread_01_live_replay.py`, drift test, fixtures `thread01_queue`, `thread01_live_queue`. Not re-run by me. Needs rerun with the sensor exe (`ED0_RUNNER_EXE`; step 2 is `blocked(sensor-exe)` without it) | 1-2 | none |
| 2 | One live roleplay run | done (synthetic), partial (E0) | Window 1 synthetic: 6 calls, 4.14 min, G1 clean. Window 2 real local E0: 5 calls, 2.46 min, ends `unlinked`, steps 5-10 not_exercised. | 0 for wording; 6-10 if a candidate on E0 is wanted | ASK-1 satisfied in practice but no recorded user answer in repo: confirm |
| 3 | All 8 honesty tests green | done in code | `contracts/engine-run/tests/test_honesty.py` test_1..test_8 pass (re-run). Gap: green on unit inputs, not asserted against the actual GT0 report | 3-4 | none |
| 4 | C-2 and C-12 frozen by digest | missing | `contracts/engine-steps/DIGEST.json` covers only the FRZ0 pack; no digest for the engine-run schema (C-2) or the roleplay queue/scanner/ledger (C-12) | 2-3 | none |
| 5 | Lane-hours/session re-baselined (sessions 1-12) | missing | no capacity data | 1-2 | none |
| 6 | `doubles[]` lists model, jev, issuer, product, host, gate, data_origin | partial | `generate_doubles` + tests, override entry exists. Not asserted that a real report carries the exact plan labels (`jev=not_exercised(blocked: agent-core PR 28 not on main)`, `product=simulated`, `compile=claude-standin(python)`, `base_world=seeded`, `gateway=stand-in`) | 1-2 | none |
| 7 | Scanner passed every payload | partial | TPS 0 rejections in both live windows, E0 leak scan 0 (claimed). Open risks: opaque ids shaped like allowed tokens pass; ED0L had no complementary suppression (commit c46f04c suppresses small numerator/complement cells, verify) | 3-5 | none |
| 8 | E0 ingested locally, detection by existing Rust sensor | partial | `ed0_detect.py`, `ed0_feed.py`; real-E0 window admitted `e0_recurring_copilot_query_cases` support 154/200, holdout replicated, 2 discards; rename/permute test green. Missing: first-Windows-build receipt of the exe (D:/cargo-targets/claude-ed0) not in repo; E0 path only via env var | 2-3 | none |
| 9 | Scout/verifier on E0-backed lab with recompute | partial | ED0L (`ed0_lab.py`, k=10, salted keys); verifier recompute accepted. "5 fixtures bit for bit, tampered numerator fails" not shown for E0 mode (real shape: 3 groups, one outcome) | 2-3 | none |
| 10 | Builder via SMAP, target from catalogue | partial (honest) | `smap.py` + corpus; E0 mapping exact-or-unlinked. On real E0 no category maps to a catalogue entry, so no change is ever proposed. Needs a ruling: accept `unlinked` as the DEMO-0 E0 ending, or author a catalogue entry for the recurrence flow | 0 or 8-12 | user ruling (not numbered in plan) |
| 11 | Generic compile (CMPpy) + seeded world (WRLD0) | done (stand-in) | `compile_step.py`, `agent-core-assets/worlds/seeded-base.world.yaml`, `tools/worldcheck.py`, `test_world_seeded_base.py`. Not exercised on E0 path | 0 | none |
| 12 | Real Core dry-run and arms | done real-narrow | `tests/live/test_08*`, `test_09*` (3 windows, PG16, Core pin c814c2b, 6 arm runs/window, native evaluation pass). attention-task world avoids PR 28 | 0 | none |
| 13 | Structural stand-in gate verdict | done, fails honestly | GSIpy reports `fail: no_structural_improvement` every window (Core arms expose only status/cost). Steps 8/9 run only under a labelled `human_override`. The plan did not anticipate this; GT0 must state it in the verdict line | 0 (accept) or 8-14 (observable that moves, circularity risk) | user ruling |
| 14 | Simulated issuer + JWS verified by Core | done real-narrow | test_08/09; tampered hash and replay refused | 0 | none |
| 15 | Publish to local staging, alias read | done real-narrow | step 9 release `rel-253b...`, prod unchanged; one window per fresh stack (immutability) | 0 | none |
| 16 | Observation (step 10) | partial | platform-sim P2py; `release.published/rolled_back` classify unknown until Codex event-catalog 1.1.0 (stand-in mapping possible) | 1-2 | ASK-2 only if the Codex swap-in is wanted |
| 17 | `demo/run.ps1` DEMO-0 entry point | missing | `demo/` still the planted judge (README: mechanism_proxy reads planted columns); only `e2e-core/run.ps1` exists. Q1r says planted wiring of demo/ is replaced | 4-6 | none |
| 18 | Gate evidence script (first RED: fails on missing receipt) | missing | no GT0 gate script (grep for GT0 hits only OWNERS.md) | 3-4 | none |
| 19 | Journal entry | unknown | CL-0041..43 cited in W0_STATUS; shared journal not in repo | 0.5 | none |
| 20 | DEMO-0 report (replay plus one live) | missing | `demo/out/demo-report.json` is the old report | 2-3 | none |

## 2. Per WP status (GT0 dependencies)

| WP | Status | Gap |
|---|---|---|
| G1 | done; tests green | rule H5 requires `candidate_created_at` even when step 5 is not_exercised; fix proposed, not made (1 h) |
| DC0 | done (scripts/dc tests green, push scan, gateway profiles in local/core/gateway) | gateway profile never run in a container |
| TPS | done, 2 known risks | opaque-id registry; complementary suppression (3-5 h) |
| RPP | done (RUNBOOK, protocol, live evidence of distinct responders) | step caps (scout 5, verifier 5, builder 7) evidenced only through live windows; builder hit the 55 s hold twice |
| M2a | built, NOT wired | `SpendGuard` exists in `core-bridge/.../llm/guard.py` with `test_spend_guard.py`; `main.py` builds only `SpendMeteringGateway`. WP acceptance (run stops at ceiling; ledger equals gateway sum within 1 token) not shown through the runtime. 3-4 h |
| ED0 / ED0L / SMAP | partial | see items 8-10 |
| Q1r | partial | ratchet and replay exist; not yet a clean DEMO-0 entry; label audit per step with data class |
| INT0 | partial | 3 live windows logged with seconds per call (done); "every drift diff explained" and first full Podman run not evidenced |
| CRV0 | MISSING | no `docs/reviews/claude/` in any worktree, no closure script (6-10 h) |
| TRN0 | MISSING | no train script (scripts/gov has only pre-pr-gate.ps1), no W0 receipts, no `exchange/` dir (3-4 h) |
| G0p | partial | `scripts/gov/pre-pr-gate.ps1` (legs ci, pytest, ratchet; receipt `pre-pr-gate/v1`) exists and is tested; no receipt ever produced for a PR |

## 3. Receipts required by the W0 gate
- G0p: one `pre-pr-gate/v1` JSON per W0 PR (verify-local-ci, pytest of touched packages, replay-ratchet; a missing leg fails). Script present; receipts absent for #94 and for the 83-commit delta.
- TRN0: W0 receipt on each train PR; merges in dependency order; restack in one fast gate; PR per 25-35 lane-hours; bundle in `exchange/` at the PR cap. Missing.
- CRV0: review log per reviewed WP, reviewer differs from author, closure script exits 0. Missing.
- GT0 own: manifest of receipts the gate script checks (G0p, TRN0, CRV0 closure, honesty run, scanner ids, C-2/C-12 digests, replay run id, live window log). Missing.
- `.nexus-outbox` receipts were committed then untracked (6b900e1); confirm history does not conflict with DC0.

## 4. The 8 honesty tests (test_honesty.py, all pass now)
1 real vs non-real provider: green. 2 third-party needs scanner id: green (unit). 3 mapping mutation: green (unit; ED0/SMAP mutation tests claimed). 4 ports and template fallback: green. 5 author fields and sealing: green. 6 python-host cap: green. 7 distinct actors/models: green (unit). 8 E0 receipt body via DC0 scanner: green (unit).
Skeptical note: all eight are green on unit inputs; none is yet asserted against the final GT0 report in a gate script. Plan said tests 2,3,7,8 start as red skeletons; here all are real, which is ahead of plan.

## 5. GT0 gate report: required content and proposed outline
Path: `docs/reports/gates/GT0_DEMO0_<date>.md` plus `GT0_receipts.json` read by the gate script (exit 1 on any missing item).
1. Verdict and scope (DEMO-0, host=python, quality_claims forbidden).
2. Doubles table from `generate_doubles`: model=agent_roleplay, jev=not_exercised(blocked: agent-core PR 28 not on main), issuer=simulated, product=simulated, host=python, compile=claude-standin(python), gate=claude-authored(structural), base_world=seeded, gateway=stand-in, data_origin=generated_sample.
3. Ten-step table: status, data class, label, evidence path/test per step; steps 5/6/8/9 real-narrow with Core digest/release id; steps 8-9 shown as human_override with reason.
4. Replay: 0 misses, run id, fixtures digest.
5. Live: 3 Core windows (seconds per call), synthetic roleplay window, E0 roleplay window (counts only), responders, minutes, scanner rejections.
6. Honesty tests 1-8 against the GT0 report, plus G1 H rules.
7. Data-class evidence: DC0 push scan, leak scan, E0 never committed.
8. Receipts: G0p per PR, TRN0, CRV0 closure, spend-guard ceiling through the runtime.
9. Frozen contracts: C-2, C-12 digests; contract_revision, sha, target per step.
10. Open risks: TPS opaque ids, gateway never run in container, SNET container measurements blocked, E0 ends unlinked, gate fails honestly.
11. Capacity re-baseline (sessions 1-12), journal entry id, GT05 preconditions.

## 6. Known facts, assessed
- Steps 5/6/8/9 real-narrow on a real Core (attention-task world, 3 windows): consistent with THREAD01.md (claimed). Caveat: arms use a scripted llm-gateway double and our own judge, so "real" means Core mechanics only.
- Stand-in gate fails honestly; publication needs a labelled simulated-human override: enforced by G1 rules; GT0 verdict must disclose it.
- E0 windows end unlinked: honest and allowed by SMAP, but the demo story rests on the synthetic window.
- M2a not wired: real gap against WP acceptance.
- SNET container-side measurements blocked: SNET is on the 2.4 demo-path list; record as partial/blocked in the gate.
- Gateway container never run (contract double): label `gateway=stand-in` (ASK-4 default); not blocking if labelled.
- Machine load high (about 4 GB free), one cargo slot.

## 7. Minimal next work packages, ordered (lane-hours)

Group A (parallel, independent files):
- A1 GT0-gate: gate evidence script, receipts manifest, report generator, `docs/reports/gates/**` (5-7 h). New worktree `claude/w0k-gt0`.
- A2 M2a-wire: wire SpendGuard through `main.py`/factories plus ceiling test (3-4 h). `claude/w0-model` or new `w0k-m2a`.
- A3 TRN0-script: train integrator in `scripts/gov/**` with dependency-order check (3-4 h). `claude/w0-gov`.
- A4 FRZ-C2C12: digest-pin C-2 and C-12 (2-3 h). `claude/w0b-g1` / `w0-facts`.
- A5 TPS-ids: opaque-id registry, complementary suppression check in ED0L (3-5 h). `claude/w0-model`, `claude/w0d-edl`.

Group B (after A merges into one base; parallel among themselves):
- B1 Q1r-demo: replace planted `demo/` wiring, `demo/run.ps1` (4-6 h). `claude/w0e-q1r`.
- B2 G1-H5: accept null `candidate_created_at` when step 5 not_exercised (1 h). `claude/w0b-g1`.
- B3 INT0-tail: clean replay, drift diffs explained, honesty tests asserted on the real report (4-6 h). `claude/w0f-int0`.
- B4 E0-ending: keep `unlinked` (0 h, documented) or add catalogue entry (8-12 h, only if the user rules). `claude/w0j-e0`.

Group C (serial, last):
- C1 CRV0: fresh-context reviews (RC1 on TPS, DC0, G1, M2a, M0RP, E0 data path; RC2 on the rest), closure script, `docs/reviews/claude/**` (6-10 h, reviewers differ from authors).
- C2 Train PR: G0p receipt for the 83-commit delta, open the train PR (2-3 h plus user merge under ASK-3 default).
- C3 GT0: run gate script, report, journal entry, capacity re-baseline (1-2 h).

Total 32-48 h plus fix loops, so 45-70 h. Critical serial chain: A1/A2/A4 -> B3 -> C1 -> C2 -> C3.

## 8. User needs
- ASK-1: confirm treated-payload-only condition (E0 window already ran).
- ASK-3: default is user merges the train PR; hosted CI is red, so local receipts are the only evidence.
- Not numbered in plan, user rulings needed: (a) GT0 acceptable with an `unlinked` E0 ending; (b) GT0 acceptable with the failed structural gate published under a simulated-human override.
- ASK-2 and ASK-4 are not needed for GT0 at their defaults.

## 9. Skeptical notes
- A passing G1 `check()` proves label consistency, not that the demo works.
- Live evidence is destructive per window (immutable registry): reruns need a fresh stack.
- Hosted CI red; no local receipt has ever been produced.
