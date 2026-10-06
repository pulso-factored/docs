# Review v3-A: mechanical and internal consistency of v3-plan.md

Reviewer A. Method: independent script (`scratchpad/chk.py`, `x.py`) over the section 8 table (112 rows parsed), grep of every id/section reference, and read-only checks of the worktree at 853b029 for path ownership. Line numbers refer to v3-plan.md. No plan file was edited.

## 1. Verdict

Arithmetic is clean: every total, tier sum, lane sum, ratio, critical set and the checker itself reproduce. The defects are structural: (a) the critical chain depends on Codex and `crates/core` work that the plan's own safe defaults leave blocked; (b) the path-ownership map is incomplete and has one hard collision, so the promised OWNERS test would fail on day one; (c) CF-0/TW-0 at session 3 have no WPs behind them; (d) a few prose derivations (80-85 h spine, 55 h chain, capacity C sessions, the 47-79 h list) do not follow from the table. Counts: BLOCKER 0, HIGH 8, MEDIUM 17, LOW 12.

## 2. Mechanical recomputation (all PASS unless marked)

| Check | Plan says | Recomputed | Result |
|---|---|---|---|
| WP count, unique ids | 112 | 112, 0 duplicates | PASS |
| Dangling deps / cycles | none | none / none | PASS |
| One owner per lane; lane count; split | 26 lanes, 16 CL / 10 CX | 26, 16 CL (incl. L-COMPILE), 10 CX, 0 lanes with two owners | PASS |
| Total hours | 847-1290 | 847-1290 | PASS |
| Claude / Codex hours | 667-1004 / 180-286 | same | PASS |
| Share | 78.7% / 77.8% (mid 78.2%) | 78.75% / 77.83% / 78.19% | PASS (inside 70-80 at both bounds) |
| Per tier (total; Codex) | T0 104-159 (1-2); T0.5 65-98 (27-42); T1a 180-261 (6-9); T1b 70-109 (20-34); T2 161-237 (55-82); T3 119-191 (71-117); TA 88-145; T5 60-90 | identical | PASS (but see M4: tier label of K0) |
| Per-lane hours in 9.1 (26 rows) | listed | all 26 identical | PASS |
| E0-ENV sum | 34-56; keep-set (ENV2,4,6,8) 7-11 | 34-56; 7-11 | PASS |
| Critical flags | 19 WPs, 158 mid h, float <= 4 h | computed set equals the 19 `Y` rows exactly, 158.0 h, all CL | PASS |
| Serial midpoint depth | GT0 28, GT05 47, GT1A 120, GT1B 122 | 28.0, 46.5, 120.0, 121.5 | PASS |
| Longest path over lows / highs | not stated | lows GT0 23, GT05 37, GT1A 97, GT1B 98; highs 33, 56, 143, 145; same chain ENV0,ENV1,ENV2,K0,E1,E5L,K3,V1,V2,H1,P2R,MEM1,Q1,GT1A,GT1B in all three | informational (add to section 6) |
| Ancestor hours (13.2) | GT0 66-96; GT05 133-197 (CL 110-161); GT1A 298-437 (269-392); GT1B 372-548 (333-487) | identical | PASS |
| Churn-adjusted central | 575 / 220 / 170 / 128 / 83 / 1175 | 575 / 219 / 170.5 / 128 / 82.5 / 1175 | PASS |
| Scenario (a) Codex share | 22.7-23.6% | 22.67-23.57% | PASS |
| Scenario (b) | +36-57 h; T2/T3 Codex 126-199 | 0.2 x (180..286) = 36-57; 55+71 = 126, 82+117 = 199 | PASS |
| Wave widths | 12 / 21 / 10 / 7 / 12 / 13 | counted lane lists: 12, 21, 10, 7, 12, 13 | PASS |
| Section refs (3, 4, 7, 8, 9.x, 11, 13, 15, 16, 17, 18) | exist | all exist | PASS (see M17 for mis-scoped cites) |
| Chain "ENV0 -> K3 about 55 h" (393) | 55 | ENV0+ENV1+ENV2 = 9.0, K0..K3 = 54.5, total 63.5 | FAIL (M1) |
| "80-85 h spine" (393, 448) | 55 + 25-30 | 63.5 + 25-30 = 88-93 | FAIL (M1) |
| Sessions at A (CL-mid ancestor hours with 10%: 89 / 149 / 364 / 451 over 16-20 h) | 4-6 (5); 7-10 (8); 17-23 (20); 22-28 (25) | 4.5-5.6 (5.0); 7.5-9.3 (8.3); 18.2-22.7 (20.2); 22.6-28.2 (25.1) | PASS |
| Sessions at B (22-26, mid 24) | 3-5 (4); 5-8 (6-7); 13-18 (16); 17-23 (20) | 3.4-4.0 (3.7); 5.7-6.8 (6.2); 14.0-16.5 (15.1); 17.3-20.5 (18.8) | PASS (GT1A and GT1B centrals rounded up by 1 session, acceptable) |
| Sessions at C (40-50, mid 45) vs spine floors 4 / 6 / 11-12 / 13-14 | 3 / 5 / 12 / 15 | by capacity: 2.0, 3.3, 8.1, 10.0; floors bind | FAIL for GT0 (3 < 4) and GT05 (5 < 6) (M2) |
| Line 23 vs table 13.3 at C | "3, 4-5, 11-12, 14-16" | table: 3-4 (3); 4-6 (5); 11-13 (12); 14-16 (15) | minor mismatch (M2) |

Not stated in the plan, so not checkable: per-wave hour sums (there is no WP-to-wave column; see L10).

## 3. Defects

Format: ID, severity, location, evidence, exact fix.

### HIGH

**H1. K3 (critical) hard-depends on a Codex-frozen chain; contradicts the stated fallbacks and section 16.**
Location: table row K3 (line 240, deps `K2,DMAPC,E5L`), DMAPC (line 222, deps `SMAP,WDX`), WDX is CX; line 156 ("Codex packages are off the critical path ... DMAPC and WDX gate K3"); 8.1 scenario (b) (line 315); section 16 "F3, F4" (line 642: "K3 depends on fixtures not on the S-MAP verdict").
Evidence: K3 <- DMAPC <- {SMAP, WDX}; WDX has 17 h float, DMAPC 9 h, SMAP 9 h to GT1B (computed), so K3 cannot start until a Codex package and the S-MAP outcome land. DMAPC is Claude-owned (line 156 wrongly groups it with Codex packages). With U-1 defaulting to "Codex lanes stay blocked" and U-2 defaulting to "crates/core untouched; DMAPC goes to Codex", neither WDX nor DMAPC can be produced, yet scenario (b) says the plan "keeps its shape" and K3 is the heart of T1a.
Fix: (1) change K3 deps to `K2,E5L,K3fx` where `K3fx` is a new 2-3 h Claude WP in L-CLIENT (dep K2) that builds a fixture compiled ChangeSpec for Replace Prompt + Add EvalSuite; keep DMAPC as a dependency of Q1 and GT05 only; or delete the sentence in section 16 F3/F4 and say K3 needs DMAPC. (2) Rewrite line 156: "DMAPC is Claude's (L-COMPILE) with 9 h float; WDX (Codex) has 17 h float and gates K3 transitively through DMAPC". (3) State in 8.1(b) the hours added when the fixture path is used.

**H2. K2 contains a `crates/core/src/core_task.rs` change but lives in L-CLIENT, and the U-2 default forbids it.**
Location: K2 name (line 232, "...plus core_task contract change"), 9.1 L-CLIENT paths (line 355), L-COMPILE paths (line 356, WP list DMAPC only), section 16 F-1 (line 621), U-2 default (line 598).
Evidence: `core_task.rs` is owned by L-COMPILE (the exception) whose only WP is DMAPC. K2 (critical, 14-20 h) therefore edits a file outside its lane; under the U-2 default ("leaves crates/core untouched") K2 cannot complete as specified.
Fix: split K2 into `K2` (typed client, `seams/crates/core-client/**` only) and `K2c` (core_task.rs 0.5.0 -> 1.3.0, lane L-COMPILE, owner CL under U-2, dep K0, 3-5 h taken out of K2's 14-20). Give K2 a path when U-2 is silent (core-client carries its own 1.3.0 DTOs, adapter in `seams/`), and list K2c in the U-2 ask.

**H3. Hard path collision: `scripts/verify-local-*.ps1` (L-ENV) vs Codex-owned `scripts/verify-local-ci.ps1`; three sections disagree on `scripts/**`.**
Location: 9.1 L-ENV row (line 350), 9.4 rows at lines 422 and 425, 10.1 (line 483: "Claude owns ... `scripts/**`").
Evidence: the repo has `scripts/verify-local-ci.ps1` and `tests/run-local-ci.Tests.ps1`; the glob `scripts/verify-local-*.ps1` captures the Codex file. Line 422 says Claude must not touch it; line 425 says only L-ENV edits gate scripts; line 483 says Claude owns all of `scripts/**`. G0d and ENV6 call the Codex gate (line 182), so the right rule is wrapper, not edit.
Fix: L-ENV paths become `scripts/env/**`, `scripts/verify-local-all.ps1`, `scripts/verify-local-fast.ps1`, `scripts/dev.ps1`. Add "`scripts/verify-local-ci.ps1`, `scripts/run-local-*.ps1`, `tests/run-local-*.Tests.ps1` are Codex (Codex orchestrator)". In 10.1 replace "`scripts/**`" by "`scripts/env/**` and the listed wrappers". Line 425 becomes "gate wrappers: only L-ENV; Codex gate scripts: Codex".

**H4. The path-ownership map is not total, although the plan promises a test that fails on unowned paths (lines 346, 432).**
Evidence (read-only worktree at 853b029):
- `crates/core/src` has 52 modules; the map names about 20. Unowned: `durable_jobs.rs`, `durable_run_events.rs`, `autonomous_scout.rs`, `deterministic_sensor.rs`, `independent_verifier.rs`, `evaluation_plan.rs`, `final_eligibility.rs`, `governed_registry.rs`, `jev_decision.rs`, `model_provider.rs`, `quota_grant.rs`, `sandbox.rs`, `source_validation.rs`, `wiki_scratch.rs`, `workflow_bridge.rs`, `local_lab.rs`, `local_simulation.rs`, `run_*.rs`, `e0_core_draft_binding.rs`, `e0_frozen_*.rs`, `e0_investigation_plan.rs`, `e0_opportunity_qualification.rs`, `e0_proposal_assembly.rs`, `e0_query_lab.rs`, `e0_safety_oracle.rs`, `enriched_history.rs`, `memory_temporal_protocol.rs` (X-LEARN pattern `temporal_*.rs` does not match it). Consequence: `durable_jobs.rs` holds `DurableJobRepository` and C-7 (claim-next addition, "X-CONF with L-PG") must edit it, but no lane owns it (X-CONF owns `tests/conformance/**` only).
- Patterns that match nothing today: `scenario_*.rs` (X-SCEN; only `value_model.rs` exists), `crates/core/src/detectors/**`, `crates/core/src/replay/**`.
- Top-level paths absent from every lane: `bridge-contract/` (yet C-1 is "published by L-CLIENT", line 401), `core-bridge/**` except `src/pulso_core_runtime/llm/**` (stages, invoke, reconcile, evaluation, exporter, wire, tests), `tests/**`, `contracts/*.schema.json`, `contracts/sources`, `contracts/fixtures`, `agent-core-assets/{manifest.yaml,layer_mappings,tools,tests,ci}`, `local/core/**` outside `gateway/`, `scripts/core/**`, `scripts/run-local-*.ps1`, `docs/adr/**`, `docs/journal/**` (except `codex-rev.md`), `docs/lanes/**`, `docs/spec-amendments/claude/**`, root `Cargo.toml/.lock`, `.github/**`, `seams/Cargo.lock`.
- 9.4 allocates migration ranges to L-PLAT 0070-74, L-MEM 75-79, L-AUTH 80-84, L-CAPI 85-89, L-EVAL 90-94, but those lanes' 9.1 path cells do not list them; X-SENS, X-SCEN, X-MAP, X-CONF have no range although DBRD mentions diagnosis SQL (U32).
Fix: add to 9.1 a final block "Unlaned paths and owner" covering every item above. Assign `durable_jobs.rs` to X-CONF for the C-7 change (X-FACADE reviews). Assign `bridge-contract/` and `core-bridge/wire/**` to L-CLIENT, `core-bridge/src/pulso_core_runtime/{stages,invoke,reconcile,evaluation,exporter}/**` to L-MODEL (M3, SMAP) or a named Python-host lane. Add migration ranges to each lane's path cell (and a reserve for X-SENS). Rewrite X-LEARN to `temporal_*.rs` plus `memory_temporal_protocol.rs`; X-SCEN to `value_model.rs` plus new `scenario_*.rs` marked "new".

**H5. The U-14 default violates the plan's own "no silent default" rule, and the V0 demo gate is hidden behind it.**
Location: U-14 (line 601), ENV1/ENV8 user-action columns (lines 167, 174), GT0 deps (line 218: `Q1r,SMAP,M2a,DC0,ENV6`), S1 "no cargo, no seam crates" (line 107).
Evidence: U-14's default is "proceed with ENV0-ENV8 inside current RAM", but ENV1 needs "approve machine creation and RAM" and ENV8 "stop VM, resize (U-14)": actions on the user's machine that the plan itself treats as approvals. ENV6 <- ENV5 <- ENV1, so GT0 (the Python/Podman V0 demo) has ancestors ENV0, ENV1, ENV5, ENV6 (computed). The first demo therefore waits on an approval the plan then defaults.
Fix: (1) U-14 default: "ENV0, ENV2, ENV4, ENV6 on the existing machine only; ENV1, ENV8, ENV9, ENV12 stay undone until the sentence" and mark ENV1/ENV8 NO DEFAULT. (2) Replace ENV6 by G0d in GT0 deps so the V0 gate needs no builder machine. (3) State in 9.2 that capacity A requires no approval.

**H6. CF-0 / TW-0 (end of session 3) have no WPs, hours or dependency edges behind them, and under U-1's default they cannot happen.**
Location: 9.3 table (lines 399-413), W0 row (line 441), TW-0 (line 479), CONTR (3-4 h, tier T0.5), K0.
Evidence: contracts frozen at CF-0 are produced by WPs scheduled later or elsewhere: C-4 ABI crate -> E1 (11-18 h, T1a); C-5 `CoreClient` + `FakeCore` -> K1/K2 (T1a; TW-1 only at session 6); C-6 openapi -> E5L (14-20 h, deps E1, MIG0); C-7 -> DPGc (T1b); C-8 -> DMAPV (dep SMAP, which cannot finish by session 3 as it depends on M0RP and DC0); C-10 -> DGATE; C-3 -> CONTR ("L-GOV with X-FACADE" but no X-FACADE WP). Only CONTR, G0f and K0 are W0 packages. No row carries a CF-0 dependency, so the first integration point is not in the graph. TW-0 also requires "seams/ builds offline in BOTH accounts" and Codex-published contracts, while U-1's default is Codex blocked (ENV10 has no successor).
Fix: add WP `CF0` (L-GOV, CL, 4-6 h, deps CONTR, K0, G0g) that publishes digest plus fake stubs (signatures and goldens only) for C-4, C-5, C-6, C-7, C-8, C-10, C-12; make K0 (stub part), E1, E5L, DWIRE, DGATE, WDX depend on CF0. Split TW-0 into (a) CL side, mandatory, and (b) CX side, only if U-1 is granted, else journalled `[BLOCKED]` and TW-0 passes on (a). Retag CONTR as T0.

**H7. "Every WP names a first RED" is false: the table has no first-RED, real-dependency or acceptance column.**
Location: section 11 row 1 (line 494), section 8 header (line 186), brief item 3.
Evidence: the 10 columns are id, name, stream, lane, owner, hours_low, hours_high, deps, tier, critical. No row has a RED or acceptance test; about 35 rows (T3, TA, T5 and many T2) are only a noun phrase (DBRD 30-50 h, DSRC "remaining sources", CAMP, WIKI, DMEM, DSCEN, P4, H2, T5a-c, O1b, SMAP "10 recorded outputs", M3 "Stage hardening").
Fix: add columns `first_red` and `accept` (one testable sentence each: count, threshold or file name) and extend the checker to fail on empty cells for tiers T0-T2 and warn for T3/TA/T5. Until then change line 494 to "R1 WPs name their first RED in the lane brief written at lane start".

**H8. The data-class rule binds Claude subagents only; Codex agents and the E0 -> roleplay hand-off are unaddressed.**
Location: 2.2 nuance (line 54), U-13 (line 600), section 5 steps 2-3 (lines 138-139), Codex WPs DORIG, DBRD, DWIRE, DMAPV.
Evidence: line 54 treats a role-playing subagent and Claude developer agents as hosted third-party models that may not see E0 text. Codex is also a hosted third-party model and DORIG, DBRD, DWIRE ("canary REDs"), DMAPV consume E0-shaped data; nothing says Codex agents work from schemas and digests, or that Codex tests commit no E0 text (GitHub is third party, line 51). Step 2 runs E0 sensors for real via `local-sim` (allowed, local), step 3 gives their output to the `agent_roleplay` scout; line 60 says "E0 steps on a synthetic twin until U-13", but step 3's row does not say what data the roleplay scout reads, so E0-derived signals could reach a third party at the 2 -> 3 seam. Honesty test (2) (line 43) covers class E0/CSV only, not `original-treated` (line 52: roleplay only after U-13), so that rule is untested.
Fix: (1) extend line 54 to "all developer agents, Claude or Codex", and copy it into the G0f Codex onboarding brief and U-13. (2) Add to section 5: at GT0 steps 3-4 read the synthetic twin's signals; E0 sensor output stops at step 2. (3) Change test (2) to "class E0, CSV or original-treated".

### MEDIUM

**M1. The 80-85 h "spine" and the 55 h chain do not follow from the table.**
Location: 9.2 (line 393), 9.5 (line 448), 13.3 floors (line 553), `critical` column.
Evidence: ENV0->ENV1->ENV2 is 9.0 h and K0..K3 54.5 h, so the chain is 63.5 h, not 55; with the stated 25-30 that is 88-93, not 80-85. More basically the 80-85 figure assumes V1/V2/H1/MEM1/E1/E5L run against `FakeCore` before K3, but the table keeps V1 <- K3, H1 <- V2, MEM1 <- P2R, Q1 <- MEM1 (post-K3 chain alone 54 h), so the `critical` flags describe the 120 h chain that 9.5 says is not the real one. The floors (4, 6, 11-12, 13-14) rest on the undocumented 80-85.
Fix: either express the fake-based decoupling in the table (V1, H1, E5L deps on CF0 plus a K3 integration edge on Q1) and recompute flags, or write "about 64 h" in line 393 and "about 88-93 h" in 9.5, with floors rebuilt (88-93 / 7.5 gives 12-12.5 sessions to GT1A). Print the recomputed longest-path numbers (lows 23/37/97/98, highs 33/56/143/145) in section 6.

**M2. Capacity C sessions sit below the plan's own spine floors; line 23 differs from table 13.3.**
Evidence: floors are 4 and 6 sessions for GT0 and GT05 (line 553; line 156: 28 h and 46.5 h serial at 7-8 h per session); table C gives GT0 3-4 (central 3) and GT05 4-6 (central 5). Line 23 gives C as "3, 4-5, 11-12, 14-16" vs table "3-4/3; 4-6/5; 11-13/12; 14-16/15".
Fix: set C to GT0 4 and GT05 6 (floors bind), keep 12 and 15, make line 23 use the table's ranges, and add to 13.3 the rule "sessions = max(capacity bound, spine floor)".

**M3. 13.2 "outside the GT1B ancestors" names the wrong set; the number is right.**
Location: line 549.
Evidence: prose lists ENV3, ENV7, ENV9, ENV11, ENV12, G2, P1 and "E9 follow-ons" (no such WPs; E9s is a GT1B ancestor via E5L); those sum to 26-43 h. The computed set of T0-T1b WPs outside the GT1B ancestors is ENV3, ENV7, ENV8, ENV9, ENV10, ENV11, ENV12, G0e, G0d, G2, REV1, P1, DPIPE, DAUTH = 47-79 h (the quoted number). G0d and REV1 in that set are themselves defects (M5).
Fix: replace the list by these 14 ids and delete "E9 follow-ons".

**M4. Tier inversion: WDF (T0.5) depends on K0 (T1a); K0 is scheduled in W0 and TW-0.**
Evidence: computed `tier inversion WDF T0.5 dep K0 T1a`, so GT05's ancestors include a T1a WP. Row "T0 (R half)" in 2.3 (line 61) places `core-client K1/K2` in T0 while the table tags them T1a; TW-1 appears in the "Gate WP" column of 2.3 but is not a WP.
Fix: retag K0 to T0.5 (T0.5 becomes 68-102 h, T1a 177-257 h; totals unchanged); rename the 2.3 row "R half of W0/W1 (tripwires TW-0, TW-1)" and drop "Gate WP"; add the rule "a WP's tier >= every dependency's tier" to the checker.

**M5. Gate dependencies miss mandatory work.**
Evidence: no WP depends on G0d (`verify-local-all` receipt, required in every PR by section 11 line 497), G0e, G2, REV1, DPIPE (computed "no successors" list). GT05 does not depend on REV1 although line 485 makes Codex review mandatory before any `real` label and GT05 flips steps to `real-narrow`. GT1A's name lists "RG-1 to RG-3" (line 252) but 4.3 assigns RG-1 to GT05 (line 119) and the GT05 row (line 229) never mentions RG-1.
Fix: add G0d to GT0 deps (replacing ENV6, see H5), REV1 to GT05 deps, put "RG-1" in the GT05 name and make GT1A "RG-2, RG-3".

**M6. ADR numbering cannot hold 16 Claude lanes.**
Location: 9.4 ADR row (line 429): Claude 0100-0199 "in blocks of 10 per lane".
Evidence: 16 Claude lanes x 10 = 160 > 100 numbers; Codex 10 x 10 = 100 fits with no reserve.
Fix: Claude 0100-0259 (blocks of 10, reserve at the end), Codex 0300-0399; record the map in C-13.

**M7. Contract table vs wave 0.**
Evidence: the W0 row (line 441) says C-1..C-13 are published in W0, but C-9 is frozen at CF-1 (end of W1, line 409). 9.3 says contracts are published "before any lane that consumes them starts" while W0 starts producers and consumers together (12 lanes). C-1's publisher is L-CLIENT but `bridge-contract/` is in no lane (H4). C-8 is "published by X-MAP" but DMAPV depends on SMAP, so it cannot exist at CF-0.
Fix: W0 row "C-1..C-8, C-10..C-13", C-9 explicitly CF-1. 9.3 intro: "consumers start against the published digest or a stub marked `provisional`". C-8 published by L-MODEL (schemas from existing structs, 2-3 h inside SMAP), X-MAP reviews.

**M8. `compose.d` fragments have two owners.**
Evidence: 9.4 (line 424) says each lane owns `local/compose.d/<lane>.yaml`; 9.1 gives L-ENV exclusive `local/compose.d/**`.
Fix: L-ENV owns `local/compose.yaml` only; each `local/compose.d/<lane>.yaml` belongs to its lane; edit the L-ENV path cell.

**M9. Several WPs write outside their lane's path set.**
Evidence (location of the work vs the lane's paths): Q3 (traceparent, line 472) needs code in control-api and core-client, but L-OPS owns only docs and `local/observability/**`; M5 (Rust `JevDecisionPort` test) is L-MODEL, which has no `seams/` path; M3 "stage hardening" and SMAP touch `core-bridge/.../stages/**` (L-MODEL has only `llm/**`); G1 and G2 deliver code (doubles[] generator, pin-watch) but L-GOV paths are contracts and docs; E6w (worker binary) has no crate in L-PG (`seams/crates/pg/**` only); DWIRE "sensor handlers" (line 224) is a handler, which 10.1 places in `seams/crates/engine` (L-ENGINE) while X-SENS owns only crates/core and crates/runner; ENV10 is in lane X-REV, "read-only", yet runs cargo builds.
Fix: split Q3 (`Q3c` code slice in L-CAPI/L-CLIENT via `[ASK]`); move M5's Rust test to L-CLIENT or add `seams/crates/jev-test/**` to L-MODEL; add `core-bridge/src/pulso_core_runtime/stages/**` to L-MODEL; add `scripts/gov/**` to L-GOV; declare crate names in K0 (abi, core-client, engine, control-api, pg, worker, eval, authority, memory); rename DWIRE "Pure sensor entry points over input views"; define X-REV as "read-only on others' files; owns `docs/journal/codex-rev.md` and its own target dir".

**M10. Review-class assignment is incomplete and its extra cost is missing from the totals.**
Evidence: line 495 classes lanes R1/R2/R3 but omits L-E2E, X-CONF, X-REV, DUCK, X-FACADE non-authority code (WDX, DPIPE) and non-auth parts of L-CAPI. Section 8 header says second and third loops add 10-20% on R1 packages; section 16 F5-F9 says +30-40% for R1 loops; the U-12 default says +8-12%. Totals in 13.1 add only 10% "churn" (pin bumps, environment, re-records). R1 lane hours are about 200-290, so omitted loops are about +20-58 h.
Fix: classify the omitted lanes; keep one number (for example +15% on the listed R1 WPs) and add it as its own line in 13.1 (central 575 -> about 600-620), or state that the 10% churn also covers extra loops.

**M11. The Claude/Codex ratio holds globally but not in the near term.**
Evidence: T0-T1b Codex hours are 54-87 of 419-627 (12.9-13.9%); Codex T2+T3 is 126-199 of its 180-286 (about 70%). Until GT1B Claude carries about 87% of the work; 8.1 hides this.
Fix: add a per-tier ratio column to 8.1 and the sentence "Claude share is 86-87% through T1b, 70-75% after". Decide whether to pull DORIG, DREPLAY, DORACLE (deps DWIRE only) forward; 9.5 W1 already lists X-SRC and X-LEARN in W1 while their tiers say T2.

**M12. Capacity B claims what only ENV12 provides; the E0-ENV fallback set has dangling deps.**
Evidence: 9.2 column B gives "cargo slots 2 (build containers on `pulso-build`...)" with prerequisites "ENV0..ENV8, ENV11" and not ENV12, but ENV12 is the "one build container per Rust lane" item (line 177). Line 182: if the gain is below 1.3x only ENV2, ENV4, ENV6, ENV8 stay, but ENV2 depends on ENV1 and ENV6 on ENV5 (both dropped).
Fix: add "ENV12-lite (one extra container)" to B's prerequisites or set B cargo slots to 1. In line 182 name the dependency rewrites (ENV2 on the host, ENV6 without nextest) and recompute the hours of the surviving set.

**M13. Per-lane staffing (9.8) is incompatible with the agent caps.**
Evidence: line 477 gives each active lane an implementer plus a test author (R1 lanes) plus a reviewer; W2 has 10 concurrent lanes (about 25 agents) vs caps 5 / 8-9 / 12-15 (line 385). Column C counts "about 9 implementers" while the worktree cap is 8 for Claude plus 4 for Codex.
Fix: state staffing per capacity: at A one implementer per lane, and pooled test authors and reviewers without worktrees (as line 391 already says); define "lane concurrency = min(width, implementers available)".

**M14. U-2 and U-1 wording: "NO DEFAULT" with a default column; scenario (a) needs U-1.**
Evidence: U-2 says "NO DEFAULT for the ownership change" yet its third column gives a default (Claude builds only under seams/, DMAPC goes to Codex). The section 15 preface defines NO DEFAULT as "stays undone". Scenario (a) moves DMAPC to Codex, which requires U-1; under U-1's default scenario (a) collapses into (b).
Fix: U-2's third column becomes "Not applicable: ownership change stays undone; consequences: ..."; add to 8.1(a) "only if U-1 is granted; otherwise see (b) and H1".

**M15. DWIRE / E3a / DMAPV overlap in S2.**
Evidence: E3a (L-ENGINE) "evidence-side steps (sensors, verifier recompute, intent validation)", DWIRE (X-SENS, "sensor handlers over input views") and DMAPV (X-MAP, "design-intent validation") name the same functions. 9.7 resolves roles for sensors and mapping but not for verifier recompute: no Codex WP owns the pure recompute function.
Fix: add a 9.7 row "Verifier recompute: pure function in X-GATE (or X-MAP), wrapper in E3a" and reword E3a to "wrappers for sensors, recompute, validation".

**M16. G0g gates the no-cargo V0 path and sits on the critical path for Rust-only reasons.**
Evidence: M1 (gateway in the local stack) depends on G0g (pub-surface audit, PR 93 review: Rust-facing, 4-6 h, flag Y), so a Python/Podman demo inherits a Rust audit delay.
Fix: split G0g into `G0g-py` (facts refresh, pin check; blocks M1) and `G0g-rs` (pub-surface audit, PR 93 review; blocks K0, WDX, DGATE, DPGc, DPLAT).

**M17. Mis-scoped cites.**
Evidence: line 598 "silence is NEVER approval (spec section 5)": spec section 5 is "Modelo persistente minimo: diez tablas nuevas" and has no such rule; the two-team plan section 5 is "Ownership" and line 631 cites "plan V3 section 5" for the same rule; "section 5" in this plan is a third thing (demo steps). Lines 406 and 469 cite "Annex D.3 / D.2": those annexes are in PLAN_DOS_EQUIPOS_CODEX_CLAUDE_V3.md, not in the spec.
Fix: cite "PLAN_DOS_EQUIPOS section/paragraph" after confirming the paragraph by grep, and prefix annex cites "two-team plan Annex D.x".

### LOW

L1. Notation collision: `R0..R3` is the ladder rungs (line 76), `R1..R3` the review classes (line 495), `R1..R19` the risk ids (line 568). Rename the ladder to `L0..L3` or the review classes to `RC1..RC3`.
L2. Mixed names for WPs: `D-REPLAY` (lines 65, 70, 114), `D-EVAL` (135), `D-ORACLE`, `D-PG` (110) vs table `DREPLAY`, `DEVAL`, `DORACLE`, `DPGc`; `S-MAP` vs `SMAP`. Normalize to table ids.
L3. Labels outside the 2.1 vocabulary: `assets_handwritten`, `sandbox_double`, `mechanism_proxy/seeded_target`, `base_world=seeded`, `gate=claude-authored`, `scheduled-ingest`, `unsupported_source`; `scripted` (test 1) is a ladder rung, not a status. Add a "secondary labels" row to 2.1 and map rungs to statuses.
L4. Section 15 order: the preface says "external relays first, then the user's explicit sentences" but user asks run U-1, U-2, U-12, U-13, U-14, U-4, U-9, U-5, U-6, U-7, U-8 (undocumented order). Order by need (U-1, U-2, U-14 before session 1; U-13 before E0 steps; U-5 before TA0) and say so.
L5. `pulso-engine doctor` and `once` (line 61) have no WP (closest: IN0 and E1). Name the owner WP.
L6. `scenario_*.rs`, `detectors/**`, `replay/**` match nothing at 853b029 (see H4); mark them "new".
L7. TA0 is "early" (line 263) but L-INFRA appears in no wave before W4 (line 445). Add L-INFRA (TA0, offline) to W0 or W1.
L8. GT1B's name says "Python host retired (RG-4)" but 4.3 moves it to `legacy_host` and deletes it two sessions later; no WP covers the move or deletion. Rename "Python host demoted" and add the deletion to Q2.
L9. W1 lists X-SCEN although its only WP DSCEN depends on DEVAL (T2), and X-SRC/X-LEARN with T2 WPs; the width 21 overstates executable width. Add a "ready WPs in wave" count.
L10. No WP-to-wave mapping, so per-wave hour sums cannot be audited. Add a `wave` column (W0..W5).
L11. The checker (lines 319-337) covers ids, deps, cycles, one owner per lane and the ratio; it does not check path containment, tier monotonicity (M4), `critical` flags, per-tier sums, lane totals vs 9.1, or empty first_red/accept (H7). Add those assertions (all reproduced in `chk.py`).
L12. Vague or untestable wording: "honest labels" (GT0), "removes memory stalls" (ENV8), "families x kinds matrix with evidence" (T3), "thin memory note, confirm/contradict" (MEM1), "Stage hardening" (M3), "10 recorded outputs" (SMAP, no pass criterion), "remaining original sources" (DSRC), "Families and detector breadth" (DBRD), "DoD pack" (T5c), "alarm firing and resolved" without a latency number. Replace each by a count, threshold, file or negative test. Good examples already present: RG-2 (identical ordered sequence and `candidate_hash` on 3 runs), TW-0..TW-3, the ENV keep rule (1.3x or 5 minutes).

## 4. Cross-reference check summary

Defined and used consistently: all 112 WP ids named in prose exist; lane ids (26) resolve; C-1..C-13 each defined once in 9.3 (C-8, C-9, C-12 never reused elsewhere, C-13 only in W0); TW-0..TW-3 defined once in 9.8; RG-1..RG-4 defined in 4.3 (see M5); EXT-1..3 and U-1, U-2, U-4..U-9, U-12..U-14 defined once in section 15 (U-3, U-10, U-11 only as dropped, line 609); CF-0 and CF-1; DEBATE-1..6 once each in 16; R1..R19 once each in 14. Migration ranges 0005-0049 (Codex) and 0050-0099 (Claude) do not overlap, and existing migrations stop at 0004 with three files numbered 0002 (confirmed in the worktree). ADR range arithmetic fails (M6). All "section N" references resolve (M17 notes the mis-scoped ones).

## 5. Recommended order of fixes

1. H1, H2, H6 (graph and fallbacks), then H3 and H4 (path map), then H5, H7, H8.
2. Re-run the extended checker after the M4, M5, M1 edits; update the 8.1 tier lines (M4 shifts 3-4 h from T1a to T0.5) and table 13.3 (M2).
