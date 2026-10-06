# Final review 3 of v4-plan.md: feasibility, ownership, methodology, environment (reviewer R3)

Evidence base: v4-plan.md (764 lines, 132 KB); the checker of 8.2 extracted and re-run read-only against the RO worktree (it prints: 214 WPs, 1337-2024 h, Claude 72.8/72.5%, 0 Claude->Codex hard edges, 0 Codex->Claude edges to non-frozen, 31 to frozen, 39 swap-in edges, 1683 tracked paths with 0 unowned or tied: the numbers in 8.1 reproduce); RO worktree at 853b029; shared journal CX-0180/0184-0187 and CL-0038; live read-only measurements on this host on 2026-10-03/04.

## 1. Verdicts

| Area | Verdict | One line |
|---|---|---|
| (1) Methodology | FAIL (fixable, 2 HIGH) | W0 has no review/train/receipt WPs; the "max 3 open PRs" plus "never merged by default" stalls after 3 PRs; worktree retirement is scheduled after the work it is meant to precede |
| (2) Ownership realism | FAIL (fixable, 1 HIGH) | Codex paths are real, but Codex is idle in W0 and W5, its start is gated on spare-slot Claude work, one hidden Codex->Claude edge in an acceptance cell, and no Codex capacity/cargo-slot statement |
| (3) Environment | PASS with 3 edits | All asserted facts re-measured true; one fact has drifted (free RAM) and 3 facts are missing (host total 16 GB, swap 8 GB, disk) |
| (4) User asks | FAIL (fixable, 1 HIGH) | Ask 1 is right and first; but asks 6, 13, 14 are compound, no ask carries "needed by", and ask 14 (merge delegation) is needed in week 1 but listed 14th |
| (5) Readable as ONE plan | FAIL (2 HIGH) | No executive summary, no "first sessions" page, 215-row table, a 90-line script, and review history inside the body; jargon undefined at first use |

## 2. Findings (severity, plan claim, evidence, fix)

### Methodology

**M1 HIGH. W0 has no independent review, no integrator, no pre-PR gate script.**
Claim: sec 11 "Independent adversarial reviews 1-3 loops", "Local CI before PR: verify-local-all receipt in every PR body (G0d, ENV6)", sec 9.5 "about 5 Claude PRs in W0".
Evidence: table rows: G0d and ENV6 are W1; TRN1, CRV1 are W1; there is no TRN0 and no CRV0. W0 holds 100-146 Claude hours (98% of W0), including the riskiest code (TPS scanner, DC0 data-class gate, G1 honesty tests, M2a spend ceiling) which sec 9.1 itself classes RC1 (3 loops). CRV1 reviews "S1 and S2 PRs" after GT0 and gates only GT05. So DEMO-0, the only dated promise, ships with zero gating independent review and with a receipt script that does not exist yet (appendix says "local gate scripts already exist", but those are Codex's Rust script; nothing covers the Python/roleplay/e2e W0 code).
Fix: add TRN0 (3-4 h, Claude integrator for W0) and CRV0 (6-8 h: RC1 loops on TPS, DC0, G1, M2a by a distinct fresh-context reviewer; RC2 on the rest), make CRV0 a dep of GT0 (adds about 0.5 session; keep it Claude-only). State the W0 pre-PR gate explicitly in sec 11: existing `scripts/verify-local-ci.ps1` + pytest of touched Python packages + replay-mode ratchet; `verify-local-all` replaces it at G0d.

**M2 HIGH. The PR cap and the merge default contradict "never block on a merge".**
Claim: sec 9.5 "at most 3 open per team"; ask 14 default "PRs wait for the user, never merged by default"; sec 11 "Never depend on a merge: trains stack on the PR head".
Evidence: Claude plans 43 PRs, Codex 19 (sum of 9.5: 5+5+9+3+10+11 and 1+4+4+5+4+1; I checked each against the hours/30 band and the counts are consistent). If the user does not merge, a team reaches 3 open stacked PRs after about 3 trains and the plan has no rule for the 4th; either it blocks (violates the rule) or it silently exceeds the cap. W2 alone makes 9 Claude PRs. Also the user must review and merge 62 PRs by hand under the default, which nobody has costed.
Fix: define the cap as "3 open independent stacks", allow stack depth up to 4 with restack, and say what happens at the cap: the team keeps working on unpublished stacked branches (a `git bundle` in `exchange/`), publishes when a base merges, never idles. Move the merge-delegation ask to position 2-3 and phrase it as one sentence with the default "I will ask you to merge each train; work continues stacked meanwhile".

**M3 MEDIUM. Worktree retirement runs after the work it is supposed to precede; the cap is ambiguous; per-lane branches multiply.**
Claim: sec 1.11 "legacy worktrees retired first (WTR1, WTR2)"; 9.5 "target at most 25 registered before W1 starts; afterwards live worktrees are capped (counting legacy ones)".
Evidence: WTR1/WTR2 are rows with wave W1 and dep ENV0 (also W1), so W0 (5 lanes, enabling pack) runs on top of the 58 registered worktrees (re-measured today: `git worktree list` = 58). "Before W1 starts" is circular. The cap text is ambiguous: 25 legacy + 8+1 Claude + 4+1 Codex = 39, or 25 total? Lane branches `lane/<lane>/<wave>`: Claude 4+8+12+4+15+13 = 56 and Codex 1+8+9+8+7+1 = 34, i.e. 90 lane-wave branches, each a candidate worktree; that is per-lane, not consolidated (the consolidation is only at PR level). WTR2 needs Codex unfrozen (ask 2), Claude must not touch Codex worktrees.
Fix: (a) move WTR1 to W0 and first (2-3 h, no ENV0 dep: it is an inventory script); (b) cap = at most 40 registered worktrees across both teams at any time (hard, tested by the inventory script), live implementer worktrees = number of implementers, not lanes; (c) a lane holds a worktree only while a WP of it is in progress and is torn down at train merge; (d) WTR2 default under silence = list-only report to the user.

**M4 MEDIUM. Staffing and worktree numbers disagree.** Sec 7 level A = "1 orchestrator + 3 implementers + 1 reviewer", but sec 9.4 caps "8+1 Claude and 4+1 Codex live worktrees" and W2/W4/W5 have 21/22/14 lanes. Three implementers cannot drive 8 live lanes; the other 5 worktrees would sit idle, contradicting "idle lanes hold none". State: live worktrees = implementers (3 Claude + responder window); width above that is queue, not parallelism. The honest parallelism at A is 3-4, which the capacity numbers already assume.

**M5 MEDIUM. Section 10.1 states the independence rule backwards.** "Claude->Codex edges go only to wave-0 frozen artifacts; Codex->Claude flow is optional swap-ins." In 6.1-6.3 and the checker, a Claude->Codex edge means a Claude WP depending on a Codex WP (0 hard, 39 optional); frozen artifacts are Claude-owned, and swap-ins are Claude depending on Codex. As written, 10.1 says hard Claude->Codex edges exist. Rewrite: "Codex WPs depend only on Claude's wave-0 frozen artifacts (31 edges); Claude WPs have no hard dependency on any Codex WP (0) and only optional swap-in edges (39)." Table verified: no violation (I read every CX row's deps: only G0f, G0gr, CONTR, CF0, FRZ0, BK0, ENV0, ENV4, other CX WPs). Narrative in sec 1.4, 6.1, 8.1 is correct; 10.1 is the only inverted place.

**M6 MEDIUM. Codex restack is not executable as written.** Sec 9.5: "the integrator rebases the stacked train in the same session". Journal CX-0187: Codex cannot fetch GitHub (`github.com:443` fails), `gh` token invalid; it publishes only through the connector, and CX-0173/0184 show that a PR required the user's transfer or a reconstruction "as a child of exact live main via GitHub API". Rebasing on "the head of the PR it stacks on" needs that head locally. Fix: Codex trains are based on the last user-confirmed main SHA, depth 1 (no stacking on its own unmerged PRs); an unmerged base is handled by a bundle from `exchange/`; say so in sec 9.5 and in the Codex onboarding brief. Claude trains may stack deeper (M2).

**M7 LOW (compliant, checked).** Strict TDD: every row has a non-empty first RED; spikes rewritten test-first (ask 11 default = full ritual): PASS. Journal: tags with UTC timestamp and team in the first line, one consolidated entry per team about every 15 min, `[DONE]` telemetry: PASS (but state that the Codex entries are CX-NNNN and the Claude CL-NNNN in the shared file, already said). Spec source of truth with additive amendments by the owning team: PASS (precedent file named). Docs in English, never touch D:\Nexus (sec 10.6 only uses `nexus checkpoint`; no WP touches the vault): PASS. Do not stop on failures: `[BLOCKED]` + default: PASS. Careful with the other team's files: path map total (0 unowned of 1683, re-run), consent clause U-2 default none: PASS. Real dependencies via Podman, one machine per team: PASS (Codex offline by design; consistent with journal "Podman access-denied" CX-0187).

### Ownership realism

**O1 HIGH. Codex idles through W0 and starts only after Claude's spare-slot enabling pack.**
Evidence: from the checker, per wave Codex hours: W0 2-3 (XSTUB only), W1 about 73-112, W2 about 90-134, W3 about 106-164, W4 about 88-134, W5 about 6-10. Every Codex WP except XSTUB depends on FRZ0, CF0, CONTR, G0gr, BK0, ENV0 or ENV4, which sec 8 says "run on spare slots" of the Claude agents (8 sessions to GT0 if they share the agents). Pack hours: G0f 2-3 + G0gr 4-6 + CONTR 3-4 + CF0 3-4 + FRZ0 8-12 + BK0 4-6 = 24-35 h, about 2 sessions at A. So the 27-30% Codex share is only reachable if the pack is not left to spare slots; at spare priority Codex starts around session 5-8, i.e. wastes the whole DEMO-0 window and the plan's own "Codex pulled early" claim fails.
Fix: schedule the enabling pack as sessions 1-2 priority with 2 implementers while the third starts DC0/SNET/M0RP; DEMO-0 slips at most 1-1.5 sessions (6.4 -> about 7.5 of the plan's own 8) but unlocks about 100-150 Codex hours in W1. Make this an explicit orchestrator decision in sec 13 (the two numbers side by side), not an implied "spare".

**O2 MEDIUM. FRZ0 pack contents do not fully cover the Codex lanes that cite them.**
- DMAPV acceptance "10 SMAP outputs: valid, unlinked or not_evaluable" but deps are FRZ0 only; the 10 outputs are produced by SMAP, a Claude W0 WP that is not a dep and not in the pack (the pack has "builder-output corpus v0"). That is a hidden Codex->Claude edge to a non-frozen WP, which the checker cannot see because it only reads the deps column. Fix: either change the acceptance to the FRZ0 corpus, or add a pack addendum FRZ1 ("SMAP outputs, treated-class, committable") published after SMAP and listed in FROZEN.
- DMAPC acceptance "precondition digest hash=core-authoritative ... from bridge dry-run": needs dry-run response goldens with digests. `bridge-contract/` goldens are in the repo, so Codex can read them, but the pack list (C-7 signature, C-8, C-9, C-10, corpus v0, arm-report goldens, PG claim traces) omits them. Add "bridge dry-run and writer goldens (from bridge-contract) with digests" to FRZ0 and to the pack digest.
- CT1 acceptance "Claude review recorded" is an edge on Claude for acceptance. Reword: "review by a distinct actor; if Claude's is unavailable, record 'unreviewed' and let RVC1 close it".
- REV1-5 need Claude-published train tags; they are optional and labelled so: fine, but they make Codex's X-REV lane (33-52 h) conditional on Claude output, so exclude it from the 27-30% "can work without waiting" claim or say it is "opportunistic".
Real offline feasibility otherwise: PASS. Evidence: Codex's own crates (`crates/core`) compile with a bundled sqlite; PG-backed tests are `#[ignore]`d and the journal records full workspace gates green on Windows without PG (CX-0178..0184), 45 integration test files at 853b029; DPGc/DJC against in-memory reference plus recorded claim traces is a legitimate offline design; DPLAT/FX22/DPL1/DPL2 use `platform-contract` 1.1.0 in the repo.

**O3 PASS (paths).** Every existing Codex-owned file named in the path map exists at 853b029: I checked 43 `crates/core/src/*.rs` names and 15 `crates/core/tests/*.rs` names (only `tests/policy_oracle.rs` is absent, correctly a "to create" file; add it to the "to create" list, which names only `policy_oracle.rs`), the 3 crates (`core`, `runner`, `source-adapters`), the 6 migrations (0001, three 0002_*, 0003, 0004) and `AGENTS.md`. `crates/core/src/detectors/` does not exist (listed as to create: correct). Migration/ADR/journal ranges do not collide with existing numbers (last migration 0004, ADR 0005).

**O4 HIGH. No Codex capacity statement and a shared "one cargo slot".**
Claim: sec 7 level A "one cargo slot; ... 4+1 Codex worktrees"; capacity 14-18 lane-hours per session.
Evidence: Codex's root gate is a 33-minute Windows `--workspace` run; Codex builds natively on the Windows host (16 GB total, see E1), Claude's seams build on the same host; the heavy-slot lock of ENV8 is cross-account. If the slot is global, Codex's 4+1 implementers serialize against Claude's builds; if per account, host RAM is oversubscribed (VM 10 GB cap + two cargo links). The capacity table says nothing about Codex; sessions in 13 are computed from Claude-ancestor hours / (14-18), i.e. Claude only. The journal pace the v3 plan used (Codex about 4-5 tests and about 370 LOC per agent-hour; review-1 §51) is dropped from v4. At that pace 364-557 Codex hours add about 1,600-2,500 tests (4.5/h) to a suite that has 587 today; if the 33-minute gate scales with test count (my assumption, linear) it would reach roughly 100-170 minutes by W4, which the one-slot rule makes the Codex bottleneck. Nothing in the plan addresses this.
Fix: add a "Codex capacity" row to sec 7 (agents, slot rule per account, pace 4-5 tests/agent-hour, the gate-time projection, mitigation: ENV6 fast tier for Codex = per-lane `-p improvement-engine-core --test <file>` locally, full root gate once per train, which is already the TRX rule); state that Codex hours are a ceiling subject to ask 2 and that under silence the Codex 12 lanes execute 0 hours.

**O5 MEDIUM. Claude 17 lanes at 70-73% is executable only as a queue.** 973-1467 Claude hours with 3 implementers: W2 has 21 lanes (12 Claude) and W4 22 lanes (15 Claude). Each lane gets about one-fifth of an implementer; context switching and the 12% of Claude hours spent on L-GOV overhead (33 WPs, 120-183 h of train/review/tripwire/facts) are the real tax. The plan's own churn allowance (10%) is below the churn implied by 5 pin bumps in 21 h and one-fifth duty per lane. Say plainly: Claude is the bottleneck, the 70-73% is a consequence of the independence rule, and the cheapest lever is Codex taking the stand-ins (which the rule forbids): so the user should see that independence costs about 117-172 Claude hours (the plan states this; add it to the executive summary).

### Environment (re-measured read-only, 2026-10-03/04)

| Plan assertion | Measured now | Verdict |
|---|---|---|
| `.wslconfig` 10 GB, 8 CPUs | `memory=10GB`, `processors=8`; also `swap=8GB` (D:\WSL\wsl-swap.vhdx), `networkingMode=mirrored`; VM `free -m` total 9948 MB, `nproc` 8, used 734 MB | TRUE; swap not mentioned |
| Host free RAM about 1.7 GB | free 5,746 MB of 16,125 MB total | DRIFT (one volatile sample); plan never states the 16 GB total |
| No sccache, mold, lld, nextest, ollama on host | none on PATH; `ollama.exe` and `~/.ollama` absent (a stale Ollama PATH entry exists) | TRUE |
| No cargo/compiler in VM | `which cargo rustc gcc cc sccache mold ld.lld cargo-nextest` all absent in the pulso-dev distro (no gcc either) | TRUE |
| rust-lld ships with the toolchain | `rust-lld.exe` under the 1.98.1 sysroot `lib/rustlib/x86_64-pc-windows-msvc/bin` | TRUE (not on PATH) |
| Podman: both machines are distros of one VM | connections pulso-dev (+root, default) and pulso-codex (+root) share one machine identity; WSL distros `podman-pulso-dev`, `podman-pulso-codex` running; a third distro `Standar-Dev` is stopped | TRUE; third distro unmentioned (harmless; one VM anyway) |
| GPU RTX 3060 12 GB | RTX 3060, 12288 MiB, 1142 MiB in use | TRUE |
| Disk | C: 111.7 GB free, D: 1,200 GB free | not in plan |

**E1 LOW/MEDIUM.** Add to sec 7: host 16 GB total, swap 8 GB, C: 112 GB / D: 1.2 TB free, and make ENV8 record min/median free RAM over a working day rather than one sample (5.7 vs 1.7 GB in a day shows the single number is not a basis for R7). Expect target dirs per live lane (14 live worktrees) to matter on C: only if cargo dirs default there; G0e must place them on D:.
**E2 PASS.** Capacity levels A/B/C are labelled assumptions ("an assumption re-baselined at TW-1", "model, not data"); C1-C3 prices are "indicative list prices, not quotes"; no unsourced speedup (ENV0 keep rule 1.3x or 5 min). Remaining nit: re-baselining happens at TW-1 (K2, W2, about session 25+); re-baseline velocity at GT0 as well (first measured throughput after about 6 sessions) so level selection (ask 10) uses data early.
**E3 PASS.** ENV on the demo path: the 16 `demo_path=Y` WPs (G0gp, G1, DC0, SNET, M1, M0RP, M3, SMAP, M2a, P2py, Q1r, GT0, M5a, ED0, TPS, RPP) contain no ENV WP; all ENV rows are W1+ and "run behind DEMO-0 unless ENV0 shows they shorten the demo path" is stated in sec 7. One gap: W0 runs 5 lanes plus the pack concurrently without the slot protocol and per-lane target dirs (ENV8, G0e are W1); put G0e (1-2 h) in W0.
**E4 PASS with edit (ENV1 vs AGENTS.md).** AGENTS.md line 7: "do not move development to WSL without documented incompatibilities and a decision". The plan has ENVADR (ADR), ask 3 (ack), default "measure only", and ENV1 depends on ENVADR. Edit: ENVADR's acceptance must cite measured incompatibilities from ENV0 (the AGENTS.md wording asks for incompatibilities, not just an ADR), and ENV1 must list the ack as an explicit dependency, not only inside ENVADR's acceptance text.

### Asks

**A1 PASS.** Ask 1 is the confirmation of the treated-payload condition for the roleplay responder, one sentence, with the safe default "treated payloads only"; silence-never-approval is stated; every ask has a default or "NO DEFAULT".
**A2 HIGH. Compound asks, no deadline column, wrong order for the first week.**
Evidence: ask 6 mixes a hosted key, three cap numbers, and `JEV_API_KEY`; ask 13 (AWS) lists 7 sub-asks; ask 14 mixes Actions budget, RAM windows, and merge delegation. The user cannot answer these in one sentence, contradicting the sec 15 header. Merge delegation (needed from the first W0 PR, see M2) is 14th. Ask 2 (freeze lift) is correctly second, but nothing says it is the single largest lever on the Codex 27% (and, if silent, Codex executes 0 hours). No ask says when its answer is needed.
Fix: split 6, 13, 14 into single-sentence asks; add a "needed by" column (before W0 / before W1 / before DEMO-1 / before DEMO-3); order: 1 treated payloads, 2 Codex freeze lift, 3 merge delegation, then ENV acks (3, 4 of v4), then DEMO-1/2/3 items. Hardware ask 10: add the decision rule ("ENV0 shows X: ask C1 first, cheapest") and keep prices labelled indicative. Relays EXT-1..3 should be shipped as three ready-to-paste messages (the user is the only channel; today they are lists of phrases).

### Readability as ONE plan

**R1 HIGH. Not readable by the user as one plan.**
Evidence: 764 lines / 132 KB (about 33k tokens). Lines 159-374 (45% of the file) are the 214-row WP table; lines 398-484 are a Python script; lines 756-764 are a dense findings-disposition appendix about earlier drafts. There is no executive summary: sec 1 "the plan in sixteen lines" is itself dense and uses IDs undefined at first use (WP in line 11; GT0, G1 > M3 > Q1r, TPS, RPP, SMAP, `ratchet`, `doubles[]`, S1/S2/S3a/S3b, RG-1..5, TW-0..3, RC1-3, CRV/REV/RVC/TRN/TRX, CAP-n, U-n, EXT-n, "lane"). Grep: no "first session" or day-by-day view exists.
Fix (structure): (1) page 1: five-sentence executive summary (goal; DEMO-0 in about 6-8 sessions at medium-low confidence; what is real vs roleplay; what the user must decide now; what independence costs); (2) page 2: "what happens in the first sessions" (below); (3) sec 2-7, 9.5, 10, 14, 15 as the body (about 250 lines); (4) move sec 8 table, 8.2 checker, 9.1 owners block, 17 and the appendix into annex files referenced by name; (5) a 20-term glossary right after the summary; (6) every ID expanded once on first use.
Suggested first-sessions content (derived from the table; all subject to M1/M3/O1 edits above):
- Session 0, user only: answer asks 1 (treated payloads), 2 (Codex freeze lift), 3 (merge delegation).
- Session 1: WTR1 inventory; G0f, G0gr, CONTR (unblocks Codex); DC0, SNET start; first RED tests for TPS and M0RP.
- Session 2: CF0, FRZ0, BK0 (Codex pack published, journal `[CONTRACT-PUBLISHED]`); M1 real gateway smoke; G1 starts.
- Session 3-4: M0RP, TPS, RPP, G1, ED0 (E0 ingest locally, sealed ranking); Codex starts XSTUB, DVREC, DWIRE, DMAPV.
- Session 5-6: M3, SMAP, P2py, M2a, M5a; Q1r ratchet in replay; CRV0.
- Session 6-8: GT0: replay green plus one live roleplay run with `doubles[]` listed; journal entry; user sees the first demo.

## 3. Resolution of the named checks

1. 29 lanes / 6 waves, implied counts: PRs Claude 43 (5/5/9/3/10/11), Codex 19 (1/4/4/5/4/1), total 62; each PR is 25-35 lane-hours and the counts agree with the per-wave hours; consolidated and bounded at PR level; NOT bounded at worktree/branch level (90 lane-wave branches) and no rule for the cap being reached (M2, M3).
2. 58 legacy worktrees: re-measured 58; plan to retire them is correct in intent, wrongly scheduled (M3).
3. Local CI before every PR: PASS from W1, undefined in W0 (M1).
4. Never block on a merge: PASS for Claude trains, FAIL under the default merge policy at the 3-PR cap (M2) and for Codex restack (M6).
5. Claude/Codex independence (new user rule): table 0 hard Claude->Codex edges, re-verified by the checker and by reading the CX rows; narrative correct in sec 1/6/8, inverted in 10.1 (M5); one hidden edge in an acceptance cell (O2).

## 4. The three changes that most improve feasibility

1. Make the enabling pack (G0f, G0gr, CONTR, CF0, FRZ0 with the O2 additions, BK0) the first two sessions and add TRN0/CRV0 for W0: unlocks 100-150 Codex hours for about 1-1.5 sessions of DEMO-0 delay and puts independent review under the only dated promise.
2. Fix the merge/PR/worktree policy as one rule block: stack depth and what happens at the cap, Codex depth 1 plus bundles, hard 40-worktree ceiling with live = implementers, WTR1 in W0, merge-delegation ask third.
3. Split the document: a 2-page front (summary plus first sessions), glossary, asks as single sentences with "needed by", and move the table, checker and history to annexes.

Files: D:\.codex\factored\docs\plan-real\review-v4-3-feasibility.md (this file). I changed nothing else; the checker was run from a copy in the scratchpad.
