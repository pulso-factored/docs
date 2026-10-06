# Review v3-B: BACKWARD PASS of v3-plan.md (reviewer B)

Target: `D:\.codex\factored\docs\plan-real\v3-plan.md` (baseline claimed 853b029; the read-only worktree is now at 853b029, so facts below were checked against it). Method: user clauses and the ten demo steps traced backward through sections 2, 5, 6, 8, 9; WP table parsed and re-computed with a script (112 rows, ancestors, longest chains, tier inversions, orphan WPs); spec 17, 22, 31.1, 31.4.4, 32 and estado-spec 00-03 read; dependency-ladder facts spot-checked in the code and in the llm-gateway (gh api, then the rate limit was hit, so agent-core was checked in the c814c2b checkout). Nothing under D:\Nexus touched.

## 1. Verdict (5 lines)

1. The plan is structurally strong on honesty, ownership and the Python-first strangler, and the table arithmetic is reproducible (419-627 T0-T1b, 78.7/21.3 split, GT0 66-96 h, GT05 133-197 h: all re-derived exactly).
2. BUT it quietly shrinks the user's central clause: "artifact kinds: tools, flows, compiled trees, agents, Jev decision models, any combination". Only `Replace Prompt` + `Add EvalSuite` has a WP in any tier (T0..T5). Flow/tree, template, policy, decision_model, agent, tool, cascade, multi-kind bundles, and the honest negatives for denied kinds have NO WP (finding B1).
3. The gates do not require what they claim: E2 (executor) is not an ancestor of GT1A; P1 (exporter to ingest) is not an ancestor of GT1B; P2py is not an ancestor of GT0, yet step 10 is labelled for S1 (B2-B4).
4. "Real models" and "initial dataset" arrive late by construction: first real/measured model evidence is T2 (M4 hangs off M2f, which hangs off GT1B); the original CSV dataset is T2 (DORIG), and E0 downstream stages run on a synthetic twin until U-13 (B5, B6).
5. Of 12 ladder facts spot-checked, 9 are exactly true, 3 are stale or partly wrong (gateway release workflow and consumer auth exist; serde/compile_fail counts differ). Spec-item coverage has about 26 items with no WP or an unreasoned deferral (section 5).

## 2. Findings by severity

### BLOCKER

**B1. Artifact-kind coverage is a single narrow slice; the user's "tools, flows, trees, agents, Jev models, any combination" has no WP.**
- Plan claim: sec 5 row 5 ("Flow add and ToolDef later"), DEBATE-5 ("Flow add second"), DMAPC (12-18 h: "Replace Prompt plus Add EvalSuite, multi-operation"), M5 ("Jev ... Core-side stays blocked"), sec 9.7 (cuts CAP-07, blocks CAP-41/44).
- Evidence: grep of the plan for `cascade`, `auto_bumped`, `expected_derived`, `CAP-13/15/18/19/20/21/22/23`, `U46`, `U48`, `policy`, `template`, `decision_model`, `tools_allowed`, `release_settings`: zero or one hits, none inside a WP name. Spec 31.4.4 (D-10) marks flow, template, policy, prompt, decision_model, eval_suite, agent (replace of authorized fields) as producible in the first cut; the estado (02, CAP-14) says the Rust compiler enum has 6 kinds but evidences none beyond flow. `change_compiler.rs` supports one minimal Flow vertical only (line 797/1141: `UnsupportedEntityKind`/`UnsupportedOperation`).
- Coverage by kind (propose / validate-dry-run / evaluate / publish):

| Kind (agent-core c814c2b `EntityKind`) | Spec first cut | Propose | Validate | Evaluate | Publish | Verdict |
|---|---|---|---|---|---|---|
| prompt | yes | DMAPV/SMAP | K3 dry-run (K2) | V1/V2 | H1 | covered, narrow (existing `model_profile` only) |
| eval_suite | yes (CAP-21) | handwritten asset only; generator DEVAL T2 | K3 | V1 | H1 | covered only as handwritten asset until T2 |
| flow (tree) | yes add/replace | none | none | none | none | UNCOVERED in all tiers (compile mapping check->rule, ask->collect... absent) |
| template, policy | yes | none | none | none | none | UNCOVERED |
| decision_model (classifier/llm_structured/rule providers) | yes, calibration unchanged | none | none | none | none | UNCOVERED (M5 covers only the Jev gateway pass-through and Rust port) |
| decision_model provider jev | blocked (PR #28) | none | none | none | none | no WP produces the honest `blocked(jev)` ending as a tested negative |
| agent (replace tools_allowed etc.; new agent out of first cut) | partial | none | none | none | none | UNCOVERED |
| tool | NOT first cut (`dependency_blocked(tool_without_executor)`) | none | none | none | none | no WP for the negative, nor for registering an executor in the Pulso-owned runtime factories that would make a tool real |
| model_profile, language_detection, injection_ruleset, knowledge_snapshot | no (`unsupported_capability`) | - | - | - | - | no negative tests named |
| release_settings (reserved draft in c814c2b `registry/candidate.py`, N-07; CAP-23 `dependency_blocked(release_level_change)`) | denied | - | - | - | - | CAP-23 not mentioned anywhere in the plan; no negative test |
| combinations (multi-kind bundle, cascade `auto_bumped == expected_derived`, 50-changes limit, closure, base precondition digest) | CAP-13/15/17/19/20 | none beyond "multi-operation" | partly K3 | - | - | UNCOVERED |
- Why it matters: this is the second half of the user's request (proposal loop producing "any combination" of agent-core artifacts). The plan's honesty vocabulary labels what runs, but nothing is scheduled to extend it, so the system ends at T5 able to improve one prompt. Spec 17 table "Intencion de mejora" lists four compile rows (tree, Jev/decision, LLM-agent, combination); none has a WP.
- Exact fix: add a stream `B` (artifact breadth) after GT05, with one WP per row and the same four verbs (propose, validate/dry-run, evaluate, publish) in each acceptance test:
  - B1 `Flow compile` (X-MAP semantics for ChangeSpec->Flow, DMAPC extension for add/replace, K3 writer for 2+ entities, V1 suite with queue-order); deps DMAPC, K3; tier T2; 14-22 h.
  - B2 `Template+Policy+Prompt+DecisionModel(non-Jev) compile`; deps B1; 10-16 h.
  - B3 `Agent replace (tools_allowed) + cascade prediction (expected_derived vs auto_bumped) + 50-changes/quota budget (CAP-15/19/20)`; deps B1; 10-14 h.
  - B4 `Denied-kind negatives`: tool (`tool_without_executor`), model_profile/ruleset/knowledge (`unsupported_capability`), release_settings (`dependency_blocked(release_level_change)`), Jev (`blocked(jev)`), with the label asserted by the engine; deps DMAPC; tier T1a (cheap, 4-6 h, it protects honesty).
  - B5 `Tool executor registration in pulso-core-runtime factories (sandbox executor + ToolDef) so a read/compute tool can be proposed, dry-run and evaluated in the Pulso-owned world; the bank stays blocked (CAP-41)`; deps B4, DEVAL; tier T3; 12-18 h.
  - B6 `Combination bundle E2E` (flow + prompt + eval_suite + agent field) with cascade; deps B1-B3; tier T3.
  Owner: CL for transport/writer, CX for ChangeSpec semantics (X-MAP/X-GATE), L-COMPILE under U-2. Add a row for each in section 8 and a column "kinds proven" to every gate (GT05: prompt+eval_suite; T2 gate: +flow/template/policy/decision_model/agent; T3 gate: +tool and combinations).

### HIGH

**B2. GT1A does not require the executor (E2) it certifies.** Evidence (script): ancestors of GT1A contain E3b, E5R, K5a, E4R but NOT E2 (14-20 h); E2 is reachable only through E6w (GT1B). Q1 deps = MEM1,V3r,K5a,IN0,Q1r. GT1A text: "Rust executor shell (run-once...), all ten steps hosted by the Rust shell". Fix: add `E2` to Q1 deps (and to the critical-path list; it adds an E1->E2->Q1 chain of about 34 h that is parallel to the K2->K3 spine, so no new critical-path length, but the critical flag of E2 must be recomputed and RG-2 cannot be verified without it). Also add `K3` explicitly to Q1.

**B3. GT1B does not require the ingest hop the "continuous" label depends on.** Evidence: P1 (retarget platform-exporter to the real ingest contract, 4-6 h) has no dependents; GT1B ancestors exclude P1. GT1B acceptance: "ingest batch starts a run with nobody issuing a command". The exporter-to-control-api E2E is spec PL-L6 and step 10 and step 1. Fix: add `P1` to E7 deps (E7 is "triggers: ingest batch"), and add acceptance "exporter batch from platform-sim reaches `/internal/v1/platform/observations`, ACK/quarantine/gap tests (PL-02/03/04)" to E7 or E8s.

**B4. Step 10 at S1/GT0 is not gated by the simulator work that produces it.** Evidence: P2py (release events, fast-forward clock, author-separated effect) has dependents only P2R (T1a); GT0 deps Q1r,SMAP,M2a,DC0,ENV6; section 5 row 10 says S1 `simulated (our simulator emits release.* and effects)`. Fix: add `P2py` to Q1r deps (or GT0 deps). Without it V0 ends at step 9 and the ratchet cannot be green for "all ten steps".

**B5. "Real models" are not demonstrated until after the durable gate.** Evidence: M4 (hosted smoke) deps M2f; M2f deps GT1B; SMOKE tier T2, ENV9 "not on the critical path"; ladder rule (b) says climb when the real service answers the same contract file, the data class allows it and the ledger exists, and M2a (T0) already provides the ledger. So until about session 25 every model is `agent_roleplay`/`recorded`. The user's clause is "executes them for real with real models". Fix: M4 deps -> `M2a,M3` (not M2f) and tier T0.5; keep M2f for per-day/tenant governance; promote ENV9 and SMOKE to T0.5 with SMOKE deps `ENV9,M3,M1` (local model on the RTX 3060 via the same gateway needs a dummy `api_key_env`: gateway `LoadEndpoints` rejects an endpoint without `api_key_env`; state this in M1/ENV9 acceptance). Acceptance: at GT05 at least one stage (scout) runs on `local-model` or capped hosted synthetic and reports a measured schema-valid rate.

**B6. The initial (original) dataset and the E0 path are not end-to-end real before T2/T3.** Evidence: DORIG (T2, deps DWIRE) is the only original-dataset WP; section 2.3 T0 row "E0 steps on a synthetic twin until U-13"; section 5 steps 1-4 label synthetic twin; ENV9 optional. Consequence: through GT1B, E0 exists only as local-sim sensor output; the roleplay scout/verifier/builder see synthetic data. The spec's step 1 ("original snapshot, E0 or a batch wakes the engine") and spec 22 (CSV original selects by sealed ranking, no hardcoded `Queja`) are not met by GT1B. Fix: (a) promote the minimal DORIG slice (two families, namespaces, `unsupported_source` negative; 8-10 h of the 14-20) to T0.5 as `DORIG-min` feeding GT05 (Codex lane, float exists); (b) make the local model (B5 fix) the E0 responder so E0 never needs U-13; (c) add acceptance "E0 run with `data=E0`, no third-party provider in any receipt, honesty test 2 green" to GT1A.

**B7. No WP gives the user "interaction with the product platform" a concrete meaning, and the real inbound path lands last.** Evidence: platform live read is DPLAT (T2) then P3 (T3); outbound is `blocked(product-phase-2)`; steps 9 and 10 `simulated` through T5 ("no real Product source before T5"); EXT-2 asks "which registry and alias the Product runtime resolves" but no WP uses the answer. Spec 32.2/32.3/PL-10 only promise inbound insight that stops at `insufficient_*`. Fix: add `PX0 Product-consumption contract` (L-PLAT, 4-6 h, T0.5): a spec amendment defining interaction as (i) the Product runtime resolving the registry alias of the released agent and (ii) emission of `release.*`/exposure events; conformance tests in `platform-sim` that read the alias and emit events from the real Core alias; label `simulated(product-consumer)` until EXT-2. Move DPLAT (PL-C1/C2/C4/C5, 5-9 h) to T1a (deps G0g only, off critical path) so a read-only `platform_live` insight run (PL-10) exists at GT1A, and add PL-06..PL-10 first REDs to DPLAT acceptance.

**B8. Ownership map leaves live code unowned and double-owns one file.** Evidence: section 9.1 L-ENV owns `scripts/verify-local-*.ps1`; 9.4 says `scripts/verify-local-ci.ps1` is Codex-owned (the file exists on main). No lane owns `core-bridge/**` (except `llm/`), `bridge-contract/**`, `local/core/**`, `scripts/core/**`, `agent-core-assets/**` (except worlds/corpus/eval-suites), `tests/`, `contracts/` (except engine-run/steps/control-api). G0f's own test ("fails when a tracked path has no owner") would fail on day 1; K2/K3 and G2 pin bumps must change `core-bridge`/`bridge-contract` (e.g. CAP-07 entities-by-release route, mock gaps) with no owner. Fix: add lane `L-BRIDGE` (CL) owning `core-bridge/**`, `bridge-contract/**`, `local/core/**`, `scripts/core/**`, `agent-core-assets/**` (other), assign G2, SNET follow-ups and any bridge route change request from K2/K3 to it; change L-ENV glob to `scripts/verify-local-all.ps1`, `scripts/verify-local-fast.ps1` (new files) and mark `verify-local-ci.ps1` Codex.

### MEDIUM

**B9. Tier inversion and an unscheduled hash prerequisite.** (a) WDF (T0.5) depends on K0 (T1a); K0 is on the T1a critical path, so GT05 silently needs the seams workspace. Fix: tier K0 as T0.5. (b) DMAPC (T0.5, builds `precondition_digest` = Core `content_hash`, CAP-12/20) precedes K4 (JCS parity, T2). Fix: either DMAPC takes the digest from the bridge dry-run (state it, label `hash=core-authoritative`) or K4 moves to deps of K3 (parity vectors exist in `core-bridge/wire/agent_core@c814c2b`, 6-9 h).

**B10. M4/SMOKE aside, T2 holds items the demo's honesty already needs.** DEVAL (CAP-21 eval_suite from `ScenarioCase`, 8-12 h, deps only DMAPV) is T2; until then every candidate is evaluated against a handwritten suite (`assets_handwritten`), so no proposal outside the shipped world can be evaluated. Fix: move DEVAL to T1a with deps `DMAPV,DGATE`; it is Codex-owned with float.

**B11. Humans and asks missing from the plan.**
- Step 8 `real-narrow` "once the user performs one recorded CLI approval": no ask (U-15), no scheduling. Add `U-15: approver session (15 min) at GT1A`.
- The durable engine has no notification channel to a human awaiting approval (the CLI decision card only; TA6 covers alarm destinations). Add `H1n` (L-AUTH, 4-6 h, T1b): outbound notification adapter (webhook/email file sink first) for `waiting_human`, with SLA timer.
- JEV key: gateway `/v1/jev` needs `JEV_API_KEY` (config.go `JevKeyEnv`); none of U-4/EXT-3 asks for a JEV key or base URL (default `api.typesafe.ai`). The user's "Jev decision models" cannot be exercised even in gateway-only form without it. Add to U-4: "JEV key and cap, synthetic payloads only".

**B12. S3/blob store and several spec units have no WP.** The spec persistence is PG + S3; no Rust code uses S3 (estado 01), and the plan never states PG-only CAS as an amendment. "S3a/S3b" stage names also collide with S3 (object store) and hide the gap. Fix: add `ART-S3` (L-PG, 6-10 h, T1b) or an explicit amendment "artifacts are PG-CAS in v1; S3 deferred to TA with reason", and rename stages `T1a/T1b` only.

**B13. Gate tripwire/measurement gaps.** TW-3 (6 of 10 ratchet steps on Rust shell at session 15) cannot be evaluated because the ratchet statuses are `stand-in` vs `real-narrow`, not "hosted by Rust"; add `host` per step to the ratchet (G1 already has `host` per report, extend to per step). Add `REV1` to GT05 deps (REV2/REV3 are gate deps; REV1 is not, so S1/S2 PRs can ship unreviewed by Codex).

**B14. Critical-path narrative inconsistency.** Section 6 says "19 packages, 158 midpoint hours" and "GT1B serial 122 h". The script gives the longest chain to GT1B = 121.5 h over 15 WPs (ENV0, ENV1, ENV2, K0, E1, E5L, K3, V1, V2, H1, P2R, MEM1, Q1, GT1A, GT1B); 158 is a sum over a set that includes parallel branches (ENV4, G0g, G0g...). Say "158 is the sum of the 19 zero-float WPs, serial depth 122". With B2 fixed (E2) the chain to GT1B is unchanged but E2 becomes critical.

### LOW

**B15. Ladder facts (section 3.2) that are stale or partly wrong.** See section 4. Edits: gateway row "no release tag or GHCR digest" -> "`.github/workflows/release.yml` (tag-triggered image release, PR #3) exists, no tag pushed; EXT-3 = push a tag"; "no policy allowlist" -> "per-consumer bearer auth via `GATEWAY_CONSUMERS` exists; no per-consumer alias/model allowlist"; agent-core row: c814c2b ships a `Dockerfile` and `docs/plan-e2e-produccion.md` (spec 31.1 H3 said no Dockerfile at 86a7674); TA5 should first check whether agent-core's image/runbook replaces our build. Serde/compile_fail counts (171/459, 54) do not match the tree (521 pub types, 59 `compile_fail` references, 210 derive lines; counts shift with the baseline): present them as "G0g re-measures".

**B16. Continuous-run safety nets are T2.** At GT1B the engine is durable but there is no stalled-work alarm (Q3 is T2). Add to E7 acceptance a heartbeat/stall self-check metric and a Compose restart policy, so "continuous" is not claimed without a visible liveness signal.

**B17. G0d (verify-local-all) is not an ancestor of any gate** although the methodology and every PR body depend on it. Add G0d to GT0 deps.

## 3. Backward traces

### 3.1 Clause by clause (user request)

| Clause | Produced by (WP, wave, lane/team) | Acceptance and label per stage | Defect |
|---|---|---|---|
| Real system integrating with real product platform | P1, P2R (T1a, W2, L-PLAT CL), DPLAT (T2, X-SRC CX), P3/P4 (T3) | S1 simulator only; S3a simulator + inbound read; real inbound T3; outbound `blocked(product-phase-2)` | B7 (no concrete interaction WP; real inbound last) |
| ... agent-core capabilities and execution | K0-K3, K5a, E5L/R, V1/V2, H1 (W1-W2, L-CLIENT/L-EVAL/L-AUTH CL) | `real-narrow` for Prompt+EvalSuite; Jev `blocked` | B1 (breadth), B9 (hash) |
| ... real infra | ENV1/ENV12 (machine), IN0, TA0-TA6 (L-INFRA) | `real` only at TA4/TA5; before that Podman stand-in | TA4 needs U-5 (NO unlimited default); TA chain after IN0 is 28-46 h serial; ask U-5 in session 1 |
| ... llm-gateway | M1, M0RP, M3, M2a/M2f, M4, DC0 (L-MODEL) | R1 roleplay behind the real gateway (T0), local/hosted T2 | B5, B11 (JEV key) |
| initial and augmented datasets | DWIRE (T0.5), DORIG (T2), DSRC/DBRD (T3), local-sim for E0 | E0 on local sensors; downstream synthetic twin until U-13 | B6 |
| durable continuous engine | E1, E2, PGJ, E6w, E7, E8s, H1b (W2-W3) | GT1B `scheduled-ingest`; "continuous" = DREPLAY T2 | B2, B3, B16 |
| signals -> problems/opportunities | DWIRE, E3a, DMAPV, DBRD | S1 local-sim one family; 13 families T3 | fine, labelled |
| proposal loop -> agent-core artifacts any kind/combination | SMAP, DMAPV, DMAPC, K3 | Prompt+EvalSuite only | B1 BLOCKER |
| through agent-core -> real execution -> product | K2/K3, V1, H1, P2R | alias read confirms staging; product effect simulated | B7 |
| magic demo ten steps | section 5 | see 3.2 | B2-B4, B11 |
| everything missing per spec and not in spec | sections 8, 12 | section 5 matrix below | 26 gaps; non-spec adds in section 4 |

### 3.2 Ten demo steps, backward

| # | Prerequisite chain (WP -> gate) | Missing, implicit or unscheduled |
|---|---|---|
| 1 wake | S1: `local-sim` build + Q1r manual; S3b: E7 <- E6w <- PGJ <- MIG0,E1; E4R <- E5L; ingest source P1 | P1 not an ancestor of GT1B (B3); E0 snapshot registration in Rust has no named adapter WP (add to E7 acceptance) |
| 2 signals | DWIRE (X-SENS) T0.5, E3a | candidate discard display only in C1 (T2); label ok |
| 3 scout/verifier | M0RP + Core stages; E5L/E5R broker (T1a); verifier recompute E3a | wiki mount WIKI T3; DuckDB T3; sqlite lab labelled; responder slot capacity ok |
| 4 opportunity | SMAP -> DMAPV (X-MAP) | `do_nothing` required in acceptance (present in 11); mechanism catalogue labelled |
| 5 change | DMAPC, WDF/E3b, K3 | only Prompt+EvalSuite (B1); hash parity (B9a/b); cascade absent |
| 6 gates | DGATE (X-GATE), V1/V2 | suite generator DEVAL T2 (B10) |
| 7 revision | V3r (T1a) rule-driven | LLM-driven T2 (labelled) |
| 8 human | H1 <- V2,E1; DAUTH not gating | approver session ask missing; notification missing (B11) |
| 9 staging alias | K2 alias read, H1 publish | promote/rollback H2 T2 (labelled); revoke needs admin + step_up issuer, not scheduled in L-AUTH issuer tests (add to H2 acceptance) |
| 10 observe/learn | P2py (T0), P2R, MEM1 | P2py not gating GT0 (B4); P1 not gating GT1B (B3) |
| Continuous durable | E7, E8s, H1b, GT1B | liveness/stall signal T2 (B16) |

Honesty labels S1/S2/S3a/S3b in section 5 are internally consistent; the only mislabel risk is step 10 and step 9 claiming S1 `real-narrow/simulated` without the simulator or alias WP in the GT0 ancestry (B4).

## 4. Dependency-ladder spot checks (section 3.2), 12 facts

| # | Fact in plan | Evidence | Result |
|---|---|---|---|
| 1 | gateway main 63155b6 | gh api commits/main | TRUE |
| 2 | `/v1/jev` merged on gateway (PR #2) | PR list: #2 "feat(jev): POST /v1/jev" | TRUE |
| 3 | `api_key_env` mandatory; alias via `LLM_ENDPOINTS` | `config.go LoadEndpoints` requires base_url and api_key_env | TRUE |
| 4 | 1 MiB body, no retry, schema subset, `structured: prompted` | `MaxBodyBytes 1<<20`; openapi + docs/consuming.md ("never retries") | TRUE |
| 5 | "no release tag or GHCR digest" | tags/releases empty, BUT `release.yml` tag-triggered exists (PR #3) | PARTLY (add the trigger) |
| 6 | "no policy allowlist" | `GATEWAY_CONSUMERS` bearer consumers exist | PARTLY |
| 7 | engine main 853b029 / PR #93 | worktree HEAD 853b029 "Merge pull request #93" | TRUE |
| 8 | migrations stop at 0004, three files numbered 0002 | `ls migrations`: 0001, 0002_model_attempt_ledger, 0002_pulso_memory_control, 0002_pulso_platform_observations, 0003, 0004 | TRUE |
| 9 | `core_task.rs` pinned 0.5.0, digest-only | `SUPPORTED_CONTRACT_VERSION = "0.5.0"`, SHA 53e729d | TRUE |
| 10 | 587 tests; ~40 integration binaries; crates/core 58k lines | `#[test]` count 587; 45 files in `crates/core/tests`; 60,541 lines in `crates/core` | TRUE (approx) |
| 11 | Core quotas 10 proposals/24 h, 20 evals/proposal; VERSION 1.3.0 | `registry/quotas.py` (10, 20, 24 h); `contracts/VERSION` 1.3.0 | TRUE |
| 12 | 171 of 459 pub types derive serde; 54 `compile_fail` | tree: 521 pub types, 210 derive lines, 59 compile_fail refs | STALE (re-measure in G0g) |
Unverified (gh rate limit, no clone): PRs #23/#24/#28 absent on agent-core main; "gateway never run against a real provider"; 5 pin bumps in 21 h; Podman VM sizes. Each rung has a trigger in the table except the "Codex engine" row (trigger "RG-1..RG-4" is a retirement gate, not a rung climb) and "GitHub Actions" (U-6 only).

## 5. Coverage matrix: spec item -> WP (gaps in bold)

Families (spec 30.3): P0-A snapshot/S3 **partial: no S3/PG snapshot-publication WP (B12)**; P0-B ENV/IN0; P0-C fixtures **the 22 wire fixture families of spec 22 (`source_snapshot_valid`..`read_model_*`) and `contracts/product/` have no WP; CONTR/G1 cover only engine-run and engine-steps**; P1-A PGJ/E6w/E8s **(U05 PG quota/grant window unscheduled)**; P1-B K*, M*; P1-C E5R, DUCK; P1-D C1, E5L; P2-A DWIRE, DORIG, DBRD; P2-B E3a, MEM1; P2-C MEM1, WIKI, DMEM; P2-D **C1 only (U32-M/V/W model/eval/memory panels have no explicit WP)**; P3-A narrow (B1); P3-B DGATE, DEVAL, DORACLE, DSCEN; P3-C **U26 stateful bank, U36 sandbox identity: no WP**; P3-D C1; P4-A..D PGJ/H*/DREPLAY/DMEM/C1; P5-A TA*; P5-B T5a, O1a (**fairness tests absent**); P5-C O1a, T5c.

Units U01-U36 (+E variants): covered by existing code or a WP except: **U05 PG window, U10 (Rust model transport, "no Rust model call in T0-T2" but no later WP), U11 (M5 partial, Core-side blocked: ok), U26/U36 (sandbox bank/identity), U28 (AWS lab session, no WP; add to TA5 or defer with reason), U31 only inside DBRD (30-50 h block, unspecified), U32 diagnosis SQL same, U34 run control (pause/cancel) and U34-F/FE fork: no WP, U23-A continuous activation: only via E7 label**.

Units U37-U55: U37/U38 K1+H1; U39 K4 (T2, see B9); U40 exists; U41 G2; U42 exists; U43 E5R; U44 **`pulso-bootstrap core` CLI and `bootstrap-report.json` (CAP-48): no WP**; U45 K2 **(entities-by-release route, CAP-07: "cut" in 9.7 with no spec amendment)**; U46 **cascade, DraftPlan, expected_derived: no WP (B1)**; U47 DEVAL (T2); U48 K5f/V1; U49 P1; U50 P2R; U51 exists; U52 IN0; U53 Q1/Q1r **(`known_gaps.json` by SHA, CAP-64: no WP; Q3 covers traceparent only)**; U54/U55 exist.

CAP-01..64 with no WP or deferral without reason: **CAP-13/14/15/17/18/19/20/21(T2 only)/22 (compile breadth, B1), CAP-23 (not named), CAP-48 (bootstrap CLI), CAP-56 (forced limits +-1: only R15 mention), CAP-64 (known_gaps)**; CAP-07 cut by 9.7 (needs amendment), CAP-41/44/62 blocked with labels (acceptable, add negative tests).

Spec 32: PL-L1/L2/L3 exist (P1 retarget), PL-L4 C1, PL-L5 TA5 (implicit), PL-L6 P1 **(must be gated, B3)**; PL-C1/C2/C4/C5 DPLAT; **PL-C6 (spec text) DDOC mentions "amendments" without PL-C6**; PL-C3 deferred (ok); PL-01..10: **PL-02..04 gating and PL-06..10 detector REDs not listed in any acceptance**.

Estado-spec gap lists: all seven key findings of 02 map to WPs except finding 6 (docs vs code: CAP-58/61 "implemented" overstated; add a status-correction DDOC task) and finding 5 (Python/console/Terraform suites not in any workflow: G0d is the answer but no gate requires it, B17). 01 findings 3/4 (U21, U27, U31, U34-FE, U23-A, U32) map to DAUTH/DGATE/DBRD/E7 except U34-FE and U32 panels.

Not in spec, not in plan: human notification channel (B11); approver session; JEV key; gateway-image/tag action; incident comms for Product team; Core/gateway version-skew test between our pin and agent-core's own Dockerfile image; PG backup/restore RPO/RTO exists only as T5b drills.

## 6. Three changes that most raise feasibility

1. Add stream B (artifact breadth) plus B4 negatives at T1a; make every gate list "kinds proven". This is the only change that restores the user's scope, and B4 is cheap (4-6 h).
2. Repair gate ancestry: E2 -> Q1, P2py -> Q1r, P1 -> E7, G0d -> GT0, REV1 -> GT05, K0 tier T0.5, DEVAL -> T1a. All are one-line dep edits that keep the checker passing and make every gate certify what it says.
3. Pull real-model and real-data evidence forward: M4 deps `M2a,M3`; ENV9/SMOKE to T0.5; DORIG-min and DPLAT to T0.5/T1a. Costs 24-38 h of off-critical-path lane time (Codex float) and turns the first T2-era "real" labels into GT05 ones.
