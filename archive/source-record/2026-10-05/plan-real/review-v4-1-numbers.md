# Final review 1 of v4-plan.md: numbers and rules

Reviewer: FINAL REVIEWER 1. Method: own parser and own scripts (scratchpad r1.py, r1b.py, r1c.py; not the plan's checker), read-only worktree `improvement-engine-main-ro` (HEAD 853b029, 1683 tracked files; `improvement-engine-claude-main-ro` does not exist). No plan file was edited.

## Verdict per rule

| Rule | Verdict |
|---|---|
| Table integrity (214 WPs, ids unique, 0 dangling, acyclic incl. `~` edges, tier/wave monotone) | PASS |
| 29 lanes, 17 CL / 12 CX, one owner per lane | PASS |
| Hours 1337-2024; all prose numbers in 8.1 (tiers, waves, lanes, gates, shares, demo path, critical path) | PASS (recomputed, identical) |
| Owner split (70-80 / 20-30) overall, through T1b, per wave, per tier | PASS overall and T1b; per-wave/tier outliers by design (see N5) |
| (a) INDEPENDENCE by graph traversal | PASS on hard edges; 1 textual violation (F3) |
| (b) path map total and one-to-one; WP location inside lane path set | PASS for the map; FAIL for WP location (not checkable, 4 crossings) |
| (c) first_red and acceptance, no bare noun phrases | PARTIAL: none empty; about 15 acceptance cells are bare noun phrases |
| (d) ADR / migration / journal ranges | PASS on collisions; 3 map gaps |
| (e) review-loop hours in totals | PASS (CRV 25-38, REV 31-48, RVC 13-20, TRN 33-51, TRX 8-16 are table rows); coverage gap F6 |
| Cross-references and notation | FAIL (F1, F2, F4, F5, N1-N3) |

## 1. Recomputed numbers (all equal the plan unless stated)

- 214 WPs; sum 1337-2024; CL 973-1467 (72.8 / 72.5 %); CX 364-557. Through T1b: 679-1018 total, CL 479-713 (70.5 / 70.0 %). 
- Tier (total; CX lows-highs): T0 102-149 (2-3), T0.5 152-235 (57-88), T1a 275-403 (62-91), T1b 150-231 (79-123), T2 302-450 (81-124), T3 201-309 (83-128), TA 75-127, T5 80-120. CL shares of lows 98.0, 62.5, 77.5, 47.3, 73.2, 58.7, 100, 100: match.
- Waves: W0 102-149 (23 WPs, 5 lanes), W1 170-262 (44, 16), W2 308-454 (50, 21), W3 172-264 (24, 12), W4 326-488 (44, 22), W5 259-407 (29, 14); CL/CX lanes per wave 4/1, 8/8, 12/9, 4/8, 15/7, 13/1: match. Lane table (29 rows, WPs and hours): match.
- Demo path: 16 WPs, 76-111 h, equals the exact ancestor set of GT0 (closed, Claude-only, no `~`); critical path G1 > M3 > Q1r > GT0 = 25.5 h (P2py ties).
- Gates (Claude-only hard edges): ancestors GT0 15, GT05 33, GT1A 60, GT1B 71, GT2 88, GT3 86, GTA 80; hours incl. gate 76-111, 147-221, 334-493, 404-599, 553-815, 514-759; serial depth mid 25.5 / 39.5 / 117.0 / 118.5 / 142.0 / 154.0 / 157.0; lows-highs GT0 21-30, GT05 32-47, GT1A 95-139, GT1B 96-141, GTA 125-189: match. Chains match section 6 text (GT1B 20 critical WPs, 145.5 h; ENV0 > ... > K3 = 62.0 h verified by hand).
- Sessions (rule: max(1.10 x ancestor mid / capacity, 1.10 x depth / 7.5), capacity midpoints 16 / 21 / 40): all rows of the section 13 table reproduce EXCEPT the "+27 h enabling pack" row (F1).
- Edges: Claude->Codex hard 0; Codex->Claude non-frozen 0; Codex->frozen 31; `~` edges 39, all Claude swap-in <- Codex; no gate ancestor and no critical WP carries `~`. 
- Path map: 149 globs (28 lanes + `infra:**`), 1683 files, 0 unowned, 0 ties, 85 files matched by more than one glob (all resolved by specificity, none tied). All 29 lanes have a map entry and a WP. The infra rule is the single glob `infra:**`; origin/main of infra has 177 files (local checkout lists 18), so "total" there is trivial and not checked.

## 2. Findings (severity, evidence, exact fix)

F1 MEDIUM - Section 13 row "DEMO-0 with the enabling pack (+27 h)" does not reproduce. With +27 h: A 8.3 (7.4-9.5), B 6.3 (5.5-7.4), C 3.74 -> 3.7. The printed 8 (7.2-9.3), 6 (5.4-7.2), 4.0 corresponds to +24.3 h at A/B and an unexplained floor at C (the floor is 1.10 x 25.5 / 7.5 = 3.74). The Claude-only W0 enabling WPs (G0f, G0gr, CONTR, CF0, FRZ0, BK0) sum 29.5 h midpoint. Fix: state which WPs form the pack, use the real sum (29.5 -> 8.5 (7.5-9.7) at A, 6.4 (5.6-7.5) at B, 3.7 at C) or the stated 27, and add the sessions model to the checker so section 13 is computed, not typed (line 3 claims every number is checker-computed; sessions and the 5.6 % in line 11 are not; 8.1 says 5.7/5.5 %).

F2 HIGH - Gates GT05, GT1A, GT1B, GTA hard-depend on user-ask-gated WPs, contradicting "none blocks the demo path" and the default-on-silence rule. GT05 deps SMOKE -> ENV9 (needs U-14b download approval; ask 4 default: nothing downloaded; section 7 default says ENV9 waits). GT1A and GT1B and GTA inherit it. H1 (critical, GT1A ancestor) acceptance "one recorded CLI approval" needs the approver session of U-15 (ask 7; default simulated issuer), and GT1A/RG-2 read "real recorded approval". Fix: make SMOKE a `~`-style optional edge (GT05 acceptance already says "local or hosted") or add a waiver clause "skipped with status blocked(U-14b)", and give H1 two acceptance levels (simulated by default; real recorded approval is the DEMO-1 label upgrade). Otherwise the default path never reaches GT05.

F3 MEDIUM - Hidden Claude->Codex consumption in text. DPL1 (CX) acceptance "consumed by E4R" (E4R is Claude) while section 12 says "Claude's E4R has its own tests" and E4R has no edge to DPL1; CONF2 "consumed later by swap-in" is fine. Fix: delete "consumed by E4R" from DPL1 or turn it into `~DPL1` on E4R-side swap-in WP; same check for any "feeds/consumed by" in CX acceptances.

F4 MEDIUM - Contract freeze bookkeeping. (i) CF1 text freezes C-3, C-8, C-10, C-4, C-5, but the table in 9.2 also gives C-6 and C-9 "Frozen CF1". (ii) CF1 deps are GT05, TW1 only; E1 (publishes C-4) and E5L (publishes C-6) are not ancestors of CF1, so C-4/C-6 would freeze before they exist. (iii) 9.2 says C-7 is frozen at CF0, but the claim-next signature is added by DJC (deps CF0, FRZ0), whose acceptance says "trait signature frozen as C-7". Fix: add E1, E5L (or TW2) to CF1 deps and name C-6, C-9 in its text; say CF0 freezes the C-7 shape without claim-next, claim-next frozen when DJC lands (or move the claim-next signature into FRZ0).

F5 MEDIUM - G1 acceptance "8 honesty tests green" cannot hold at G1 (deps `-`): test 3 needs ED0 (ED0 acceptance says test 3 green), test 8 needs DC0 (DC0 acceptance says test 8 green), tests 2 and 7 need TPS/RPP. Fix: G1 acceptance "tests 1,4,5,6 green; 2,3,7,8 skeleton red, turned green by TPS, ED0, RPP, DC0" and keep GT0 acceptance as the place where all 8 are green.

F6 MEDIUM - Review coverage vs RC classes. CRV1-4 cover S1/S2, R1 seam, PG/worker, T2. No independent loop WP before GT0 (demo path ships with loop 1 only; CRV1 comes after) and none for W5 (TA0-TA6 RC2, M6, BKOL, BKJL, BKEL, CAMP, T5, GT3, GTA) although the lane table assigns RC2. CRV hours 25-38 h against about 300 h of RC1-class lane hours (L-AUTH, L-CLIENT, L-PG, scanner/ledger, X-COMPILE) looks low for two extra loops. Fix: add CRV5 (W5: TA, M6, live breadth, gated into GT3 and GTA) and either state that DEMO-0 is first-loop-reviewed with CRV1 retro-reviewing S1, or add CRV0 before GT0 (4-6 h, would put the demo path at 80-117 h; update 5.6 %).

F7 MEDIUM - WP location vs lane path set is not machine-checkable (no `paths` column) and 4 WPs visibly cross lanes. E3b (L-ENGINE) edits the Python host and ratchet, which live in `e2e-core/**` (L-E2E). Q3c (L-CAPI) covers control-api and core-client (L-CLIENT). K0 (L-CLIENT) creates skeletons of crates owned by L-ENGINE, L-CAPI, L-PG, L-EVAL, L-AUTH, L-MEM, L-BREADTH. WDX (X-FACADE) exports facades of types in X-COMPILE/X-GATE files. Fix: add a `paths` column (globs) per WP and have the checker assert each glob resolves to the WP's lane in the owners map; reassign E3b to L-E2E (or split E3b into a Rust step part and a Python glue part), split Q3c into Q3c-api and Q3c-client, state K0 creates only member declarations (empty crate dirs owned by K0 until the lane's first commit), and state that WDX only edits `lib.rs` re-exports (or give its `pub use` edits to each lane's file via CONTRACT-CHANGE).

F8 LOW - Path-map gaps for new files: (i) lane ADR blocks (0100-0395) and journal blocks (0100+, 0400+) are not in the owners block; `docs/adr/**` is L-GOV only, so Codex ADRs 0300-0395 sit in L-GOV's glob (the prose says the OWNERS test "extends the map", but the checker does not); (ii) migration reserve 0095-0099 unmapped; (iii) new Pester tests for `verify-local-all.ps1` (ENV6, G0d) match no glob (`tests/run-local-*.Tests.ps1` is X-FACADE); (iv) `docs/contracts/metrics.md` and `local/compose.d/**` (per-lane) have no rule although 9.3 says lanes own them. Fix: add `docs/adr/{0100..}` and `docs/journal/{01..}` block globs per lane to the owners block, add `tests/verify-local-*.Tests.ps1` to L-ENV, `local/compose.d/<lane>.yaml` rule, and make the checker also run on a synthetic list of the planned new paths.

F9 LOW - "wave-0 frozen artifacts" (section 1 point 4, section 6 rule 2, section 10.1) is false for ENV0 and ENV4, which are W1/T0.5 members of `FROZEN:`. Fix: say "frozen artifacts (W0 plus ENV0, ENV4)" or drop ENV0/ENV4 from FROZEN and give WTR2/ENV10 a different rule.

F10 LOW - Codex W1 train count: section 9.5 says 4 Codex PRs for W1, 57-88 h at 25-35 h per PR gives 2-3. Fix: 3 (or explain the TRX1 split).

F11 LOW (bare noun phrases, criterion c). Acceptance cells that are not observable or numeric: GT3 "matrix families by kinds with evidence", SWC "receipt in PR body", TA5 "thread against staging URLs", TA3 "clean plan for staging", TA2 "deltas planned offline", WIKI "exploration within grants", DSCEN2 "kernels with unit tests", DSPEC / DDOC1 "amendments merged", M6, BKEL, DORIG, DMEM1, SB1, ENV11, RVC2/RVC3 "all reviewed", T5c "spec DoD checklist signed with evidence", and 9 review/CRV cells with identical first_red "review checklist has an open finding" (a checklist is not a failing test). ENV2 first_red "script reproduces link-time metric before and after" is not a RED. Fix: give each a measurable threshold (count, exit code, named file) and an executable first_red; for reviews use "review-closure script exits 1 while any finding is open".

F12 LOW - Infra: `infra:**` assigns the whole infra repo to L-INFRA (Claude) while the plan also says shared foundations are owned by the agent-core infra owner. Fix: add "paths under shared foundations are edited only via TA0 asks" to the owners note, and have the checker run on `git ls-tree origin/main` of the infra repo.

## 3. Notation collisions (fix by renaming)

N1 `RC1/RC2/RC3` is both the review class (9.1, 9.6, 11) and WPs RC1 (pause/cancel), RC2 (fork semantics, Codex), RC3 (run fork). Rename classes to `RV1/RV2/RV3` or WPs to `RUN1-3`.
N2 `C1` is WP (console), hardware option C1 (section 7, ask 10) and capacity level C; `C-1` is a contract; streams B and C collide with capacity levels B and C. Rename hardware options `HW-1..3` and capacity levels `CAP-A/B/C` (CAP- already means spec capabilities: use `LVL-A/B/C`).
N3 Appendix finding ids H1-H8, M1-M17, B1-B17, L1-L12, R1 (risk) and "R1 seam PRs" (REV2/CRV2) collide with WP ids H1, H2, M1-M6, K, and risk ids R1-R17. Prefix appendix ids `A-H1`, `B-B1`, `C-HIGH-1` and call the seam wave `SEAM-1`.
N4 `TW-0..TW-3` (tripwires) and WPs TW0..TW3 differ only by the hyphen; acceptable but state "TW-n is the tripwire, TWn its evidence WP".
N5 Not a defect: Codex share per wave is 38-98 % Claude (W3 38 %), per tier T1b 47 %; the user rule is overall and through T1b, both inside 70-80 / 20-30. Keep the "by design" sentence; it is accurate.

## 4. Checks that passed (so they need no action)

- (a) no Claude -> Codex edge direct or transitive (no Claude WP has any hard edge to a CX WP; hard-edge closure of every gate is Claude or frozen); Codex -> Claude only to the 8 FROZEN ids; all 39 `~` edges point Claude -> Codex; none in a gate ancestor set or in the critical column.
- (d) Migrations: existing 0001, three 0002, 0003, 0004 are matched by explicit X-FACADE / X-SRC / X-LEARN globs; the new ranges 0005-0049 (CX) and 0050-0094 (CL) are disjoint and equal their globs. ADR blocks 17 x 10 = 0100-0269 and 12 x 8 = 0300-0395 are in alphabetical lane order as stated; existing ADR max 0005. Journal: existing max prefix 0067 (prefixes are not unique in the repo, 97 files), ranges 0068-0099 (L-GOV), 0100-0371 (17 x 16), 0400+ (CX) are disjoint.
- (e) Review hours are rows of the table, so the totals include them.
- Cross-references: every U-n (1, 2, 4-9, 12-17), TW-0..3, RG-1..5, C-1..13, EXT-1..3, R1-R17, ENV0-ENV12, TA0-TA6, CRV1-4, REV1-5, RVC1-3, TRN1-5, TRX1-4 exists once; every WP is in the table and referenced deps exist; 9.2 contract table lists each of the 13 once; 117-172 h of Claude stand-ins in section 8.1 reproduces (lows 57 + 60, highs 85 + 87); worktrees registered 58 (verified with `git worktree list`).

## 5. Exact fix list (priority order)

1. F2: remove SMOKE (and so ENV9) from GT05's hard deps or add a waiver; two-level H1 acceptance.
2. F4: CF1 deps add E1, E5L; name C-6/C-9; C-7 claim-next freeze moment.
3. F7: add `paths` column plus checker assertion; reassign E3b; split Q3c; clarify K0 and WDX.
4. F1: recompute or explain the +27 h row; put the sessions model into the checker; fix 5.6 vs 5.7/5.5 %.
5. F5: restate G1 acceptance; F3: drop "consumed by E4R".
6. F6: add CRV0/CRV5 or document the exemption; F9, F10, F8, F11, F12, N1-N4 as above.
