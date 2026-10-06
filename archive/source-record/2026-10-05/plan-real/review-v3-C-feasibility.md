# Review v3-C: feasibility, ownership realism, methodology (reviewer C)

Target: `plan-real/v3-plan.md`. Evidence: read-only worktree `improvement-engine-main-ro` (853b029), shared journal, host measurements taken 2026-10-04 (read-only: PowerShell, `podman machine inspect/ssh`, a throwaway `cargo metadata --offline` in the scratchpad).

## 1. Verdict
- The partition is mostly creatable on the real layout, and a nested `seams/` workspace works (tested), but 6 of the Codex path claims and 3 of the "existing struct" contract claims name files and types that do not exist.
- The ENV stream rests on a wrong machine model (WSL2 shares one VM and one 10 GB cap) and on a build cost that is mostly Codex's `crates/core` gate, which the Linux builder cannot serve because Codex has no Podman. Capacity B/C are unfounded; the 1.7 GB free host RAM measured today contradicts "5.3 GB free".
- Codex can absorb about 22% over the full horizon, but not in the window the plan schedules it (T1a has only 6-9 Codex hours), and most of its work is unconsumed until T2. The 22% is real only if U-1 is granted.
- Methodology: ENV1 breaks a written repo rule (AGENTS.md "do not move development to WSL"), the 58 existing worktrees are ignored, one PR per wave is a 50-100 hour diff, and `docs/journal` numbering conflicts.
- Asks list is well ordered with safe defaults; two defaults are not safe/consistent (U-14, U-8) and one latency item is missing.

## 2. Findings (severity order)

### HIGH-1: Codex path map names files that do not exist (9.1, X-GATE, X-FACADE, X-SENS, X-LEARN, X-CONF)
- Evidence: `ls crates/core/src` has no `improvement_evidence.rs`, `policy_oracle.rs`, `pipeline.rs`, `authority.rs`, `detectors/`, `replay/`, and `crates/core/tests/conformance/` and `contracts/pipeline/` do not exist. Real near-equivalents: `final_eligibility.rs`, `evaluation_plan.rs`, `e0_safety_oracle.rs`, `durable_jobs.rs`, `governed_registry.rs`, `memory_temporal_protocol.rs`, `run_fork.rs`, `local_lab.rs`. Real unlisted files: `jev_decision.rs`, `model_provider.rs`, `independent_verifier.rs`, `autonomous_scout.rs`, `quota_grant.rs`, `sandbox.rs`, `wiki_scratch.rs`, `run_*`, `e0_*` (14 more), 45 files in `crates/core/tests/`.
- Why it matters: `OWNERS.md` has a test that fails on any unowned or doubly-owned tracked path. Today about 35 of 52 `crates/core/src` files and all `crates/core/tests/*.rs` (except conformance) are unowned by the map; test files of every Codex lane live there.
- Fix: G0g generates the map from `ls`, not from memory. Replace owned-path lists by lane with real globs: X-GATE `final_eligibility|evaluation_plan|paired_scenario|native_evaluation|e0_safety_oracle|improvement_*(new)`, X-FACADE `lib.rs|durable_jobs.rs|jev_decision.rs` plus NEW `pipeline.rs|authority.rs` (mark "new file"), X-LEARN `memory_*|governed_*|memory_temporal_protocol|e0_frozen_*|run_fork`, X-SENS `*sensor*|signal_portfolio|e0_*investigation|e0_opportunity*`; add `crates/core/tests/<same stem>*.rs` to each lane; mark `detectors/`, `replay/`, `tests/conformance/`, `contracts/pipeline/` as "to be created".

### HIGH-2: lib.rs single-writer rule serialises every Codex lane (9.4 row "lib.rs", 9.1 X-FACADE)
- Evidence: `crates/core/src/lib.rs` holds the flat `pub mod` list (52 modules). Any new module or directory (`detectors/**`, `replay/**`, `platform_*`) needs a `mod` line there; the plan lets only X-FACADE edit it, via `[ASK]`.
- Why: Codex has 1-2 agents; 9 lanes each wait on an `[ASK]` round trip over a journal. Also `crates/core/Cargo.toml` (`[[test]]` entries with `required-features`, feature list) and root Cargo.lock have no owner in the map.
- Fix: pre-allocate in wave 0 a single Codex commit that adds empty `mod` stubs for every planned module (`mod detectors; mod replay;` with `mod.rs`) and `[[test]]` entries; after that, lanes own only their files. State that `crates/core/Cargo.toml` is X-FACADE-owned.

### HIGH-3: "Narrow waist" contracts C-8 and C-10 are not real; C-4/C-5 cannot be frozen at CF-0 (9.3)
- Evidence: grep in `crates/core/src` finds no `ChangeSpec` (only `UntrustedChangeSpec`, `AuthorizedChangeSpec`, deliberately non-deserialisable), no `ScenarioCase`, no `ImprovementEvidence`. `JobHandler` and `CoreClient` do not exist anywhere. Real and frozen today: C-1 (`bridge-contract/`: 11 OpenAPI operations in `openapi/bridge-internal-v1.yaml`, `schemas/` incl. `Fact_pulso_change_spec`, `conformance/`, `examples/`), C-7 trait (`durable_jobs.rs:111 DurableJobRepository`; also `JevDecisionPort` at `jev_decision.rs:265`), C-11 (`platform-contract/` event-catalog + schemas). `contracts/control-api/` does not exist and "existing e2e-fixtures double" is actually `e2e-core/src/codex_standin/{engine,bridge,human_port,jwtsvc,...}.py`.
- Why: C-8/C-10 "generated from existing Rust structs" cannot be generated; C-3 step schemas depend on the G0g serde audit (171/459 types). C-4 (ABI outcomes, event vocabulary) and C-5 (CoreClient + FakeCore) are designed by the same lanes that implement K1/K2/E1 in sessions 3-6; freezing before the implementation teaches anything makes CF-0 a rewrite point and R6 (drift) a certainty.
- Fix: relabel C-1, C-7, C-11 as "exists, frozen now" with the real paths above; C-2, C-12, C-13 frozen at CF-0 (Claude-only, pure documents); C-3, C-4, C-5, C-6, C-8, C-9, C-10 as "draft v0 at CF-0, frozen at the first gate that exercises them (TW-1 for C-4/C-5, GT05 for C-3/C-8/C-10)". C-8/C-10: replace with "new serde DTO crate or module to be authored by X-MAP/X-GATE", not generated.

### HIGH-4: ENV8 and capacity B/C assume a machine model that does not exist (7, 9.2)
- Evidence: `~/.wslconfig`: `memory=10GB processors=8`; `wsl -l -v` shows `podman-pulso-dev` and `podman-pulso-codex` both Running as distros of one WSL2 VM; inside it `free -m` shows 9948 MB total, `nproc` 8. `podman machine inspect pulso-dev`: Memory 4096 is a label (rootful wsl type). Host today: 15.7 GB total, **1.7 GB free** (plan says 5.3 GB); VM inside has 8.9 GB free.
- Why: "stop `pulso-codex` (frees up to 6 GiB)", "resize `pulso-dev` to 6-8 GiB" and "second machine `pulso-build` = more RAM" change nothing; stopping a distro frees almost nothing, and a third distro shares the same 10 GB. The real lever is `.wslconfig` (global, needs `wsl --shutdown`) and host RAM. Capacity B (8-9 agents, 2 cargo slots, 1 stack) needs about 8 agent processes (0.5-1 GB each) + 2 rustc peaks + Core/PG/gateway stack on a host with 1.7 GB free: not credible.
- Fix: rewrite ENV8 as "set `.wslconfig` memory/processors and measure host headroom (user action, U-14)"; delete "stop pulso-codex" and "resize pulso-dev"; ENV1 becomes "a Linux build container inside the existing VM" (no new machine, no new RAM). Cut capacity B to "same agents, replay gate, 1.3x" until a RAM number is measured; mark C as hardware-dependent and undated. Recompute section 13.3 for B (the 16/20 session figures shrink by about 20%).

### HIGH-5: ENV ROI aims at the wrong build, and Codex cannot use it (7, 8.1)
- Evidence: the 33-min gate and the 58k-line `crates/core` cost belong to Codex's root `--workspace` gate (`scripts/verify-local-ci.ps1`: fmt, clippy `--workspace --all-targets`, test `--workspace` twice). Plan 7 says Claude runs that gate rarely. Claude's code is `seams/` (new small crates) and Python. Codex has no Podman (journal CX-0003, plan 3.2), so ENV1/ENV2/ENV3/ENV5/ENV12 (about 17-28 lane-hours) never reach it. `crates/core` has 45 integration test binaries, `rusqlite` bundled (C build), `postgres` 0.19; no `sccache`, `mold`, `lld`, `nextest`, `ollama` exist on host, and the VM has no `cargo`, `cc`, `gcc`, `clang`, `uv`. Any Linux build starts with an image pull plus a compiler install (downloads need approval).
- Also: `seams/crates/engine` wraps pure steps from `crates/core` (plan 10.1), so engine, eval, authority, memory, pg all depend on `crates/core` and rebuild it (bundled sqlite and all) in the seams target dir; the claim "core-client has no dependency on crates/core" holds only for abi and core-client. The vendor estimate (25-35 new packages) omits that these crates inherit the core closure.
- On Windows `rust-lld` ships with the toolchain; ENV2 for the host needs no install and is a 1-hour test, which can speed Codex too.
- Fix: ENV0 first measures **both** accounts (cold/warm `cargo test -p improvement-engine-core --no-run`, link time share). Keep ENV0, ENV2 (host lld + `debug=line-tables-only` via per-account config), ENV4, ENV6, ENV8-corrected. Demote ENV1, ENV3, ENV5, ENV11, ENV12 to "only if ENV0 shows Claude's seams builds exceed 6 min warm". Remove "40-70 hours saved" and "25% of Rust lane time" (unsourced; the journal cites Codex only). State in K0 which seams crates depend on `crates/core` (a DAG test: abi, core-client none; engine, eval, pg yes).

### HIGH-6: Codex 22% is real in total, not in the window, and mostly unconsumed (8.1, 9.5, 3.2)
- Evidence: Codex pace measured at about 370 LOC and 4-5 tests per agent-hour (review-1 line 51). The plan's own per-tier Codex hours: T0 1-2, T0.5 27-42, T1a 6-9, T1b 20-34, T2 55-82, T3 71-117. At 1-2 Codex agents (about 8-12 lane-hours per session) T0.5 fits sessions 3-8, then T1a (sessions 9-20) has 6-9 hours: Codex idles ten sessions or pulls T2 forward. Pulling forward is possible (DORIG, DREPLAY, DORACLE, DPLAT, DEVAL have deps only on DWIRE/DMAPV: 49-69 hours) but none of their outputs is consumed by a Claude lane before T2, so semantics are built against offline goldens with no real arm reports or Core evidence.
- Secret couplings: DPGc "backend-generic conformance" needs a PG backend, which Codex cannot run (only the in-memory reference), so it validates nothing about PG until Claude runs it; DEVAL needs six-outcome captures from real Core arm reports that only Claude's `e2e-core` produces; DPIPE depends on E2 and DAUTH on E1 (Claude shell); DMAPV depends on SMAP corpus (Claude, 6-9 h); WDX/DGATE/DWIRE start from G0g/CONTR (Claude, 4-6 and 3-4 h), so Codex's first package waits on Claude's session 1-2. Every Codex lane needs the root Windows cargo slot, which the machine shares with Claude's builds.
- Fix: (a) add to each Codex WP a "needs from Claude" column and a "consumer lane" column; (b) pull DORACLE/DREPLAY/DEVAL earlier and bind each to a named consumer gate (DEVAL to V1, DREPLAY to a T2 replay demo) or defer them; (c) Claude exports 3 real arm-report and 3 PG-claim traces as goldens by session 4 so DEVAL and DPGc have non-synthetic inputs; (d) change the headline "Codex 22%" to "22% of listed hours; first 20 sessions about 8% (T0..T1a) unless Codex lanes are pulled forward".

### HIGH-7: ENV1 contradicts a written repo rule (AGENTS.md; 7, 9.2)
- Evidence: `AGENTS.md`: "Windows/PowerShell first; do not move development to WSL without documented incompatibilities and a decision." ENV1 makes a WSL ext4 builder the inner loop; the plan never produces the ADR.
- Fix: add WP `ENV-ADR` (1 h, L-GOV): ADR 0100 listing the documented incompatibility (NTFS+Defender link time, ext4 needed) and the decision; user ack in U-14 text. Until then ENV1 runs as an experiment, root gate stays Windows (already stated).

### MEDIUM-1: L-ENV glob captures a Codex-owned file (9.1 vs 9.4)
- Evidence: L-ENV owns `scripts/verify-local-*.ps1`, which matches Codex's `scripts/verify-local-ci.ps1`; 9.4 says Claude never touches it. `tests/run-local-ci.Tests.ps1` (Pester) asserts that script's step list, so adding a seams leg there breaks Pester. `scripts/dev.ps1` does not exist (creatable). `local/compose.yaml` exists (66 lines) and `tests/test_local_compose_contract.py` regex-asserts its structure; `include` of `compose.d/` must keep those tests green.
- Fix: L-ENV owns `scripts/verify-local-all.ps1` and `scripts/env/**` only; verify-local-ci.ps1 and the two Pester/compose tests are "Codex-owned, read-only"; G0d runs them as a leg.

### MEDIUM-2: Nested workspace answered; plan's uncertainty and exclude wording can close (17.1, 9.4)
- Evidence: scratch test: root `[workspace] members=[crates/a]` plus `seams/Cargo.toml` with its own `[workspace]` gives `cargo metadata --offline` success in both directories; a nested package WITHOUT its own `[workspace]` fails with "believes it's in a workspace when it's not". Root `rust-toolchain.toml` (1.98.1) is inherited by `seams/`. Hosted `ci.yml` and Codex's gate run `--workspace` at root, so they never see seams; seams has no hosted or Codex coverage at all, and its `Cargo.lock` is separate (hosted `--locked` is not applied).
- Fix: close falsifier 17.1: `exclude` is NOT needed provided `seams/Cargo.toml` has `[workspace]`; K0 test asserts this. Add that seams crates declare `edition = "2024"`, `rust-version = "1.85"` to match core. Add that `verify-local-all` runs `cargo fmt/clippy/test --manifest-path seams/Cargo.toml --locked` and Pester asserts it.

### MEDIUM-3: Journal and ADR allocation collides with repo convention (9.4, C-13)
- Evidence: `docs/journal/` holds NNNN-slug files up to 0067 (with duplicates 0004/0005/0006); `docs/adr/` holds 0001-0005 only plus README. The plan uses `docs/journal/<team>-<lane>.md`, which breaks the numbered convention and AGENTS.md's "every slice updates its journal". ADR ranges 0100+/0200+ are fine (max is 0005). The shared BITACORA is outside the repo (`D:\.codex\factored\docs\pulso_implementation_shared-_bitacora.md`, not a git repo), as is the spec; `docs/spec-amendments/<team>/` lives in the engine repo and does not exist yet. Existing precedent for amendments: `V3_SUCCESSOR_AMENDMENTS_CLAUDE.md` in the shared docs folder.
- Fix: journal files `docs/journal/<NNNN>-<team>-<lane>-<slug>.md` with numbers allocated in blocks (Claude 0100-0399, Codex 0400-0699); amendments kept in shared docs as `docs/<TEAM>_AMENDMENTS_<LANE>.md` (existing pattern) and mirrored once per train.

### MEDIUM-4: Migration allocation is feasible; two details missing (9.4)
- Evidence: `migrations/` has 0001, three independent 0002 files (disjoint tables; no cross-FK), 0003 (creates `pulso_jobs` and `pulso_run_events`), 0004. Tests `include_str!` specific filenames (e.g. `model_attempt_repository.rs` applies 0001 plus `0002_model_attempt_ledger` only). So MIG0 can define "all 0002_* lexical, then 0003" safely; but a runner that applies everything must not change what existing tests apply. `pulso_jobs` already exists, so PGJ "tables" is a claim-next/lease/fencing delta, not new tables (also affects the 20-30 h estimate; re-read).
- Fix: MIG0 RED = "runner applied to empty PG produces the same schema as the union of the existing test setups"; gaps in numbering (0005-0049 unused) must be tolerated. Keep ranges.

### MEDIUM-5: K2 edits a file owned by another lane (8, 9.1)
- Evidence: K2 includes "core_task contract change" (0.5.0 to 1.3.0) while `crates/core/src/core_task.rs` is exclusively L-COMPILE (DMAPC), and DMAPC depends on WDX (Codex). K2 is critical; DMAPC is not a dependency of K2.
- Fix: split `K2a` (typed client, no core change) and `CT1` (core_task 1.3.0 contract change, L-COMPILE, 3-5 h, deps G0g only) as a separate WP before K3; K3 deps K2a, CT1, DMAPC, E5L.

### MEDIUM-6: Worktree rule vs reality and PR size (9.6, 11)
- Evidence: `git worktree list` shows **58** registered worktrees (cleanup inventory: 67 to 70 earlier). The plan's cap "8 live for Claude, 4 for Codex" does not mention the existing 58 or a retirement rule. W1 spans sessions 3-9 (about 100+ lane-hours per team) with trains `w1a/w1b`: each PR bundles several lanes and 3 loops of R1 review do not happen at wave level (R3 is one loop).
- Fix: (a) ENV0/G0e inventory and caps total including legacy; no new worktree while count above 60 without removing merged ones (use the CX-0185 inventory); (b) one train PR per about 25-35 lane-hours, not per wave; R1 content gets loop 2 and 3 on the train diff by an independent reviewer; (c) add a restack rule: if the base PR changes, the stacked train rebases and re-runs only the fast gate (document who does it).

### MEDIUM-7: Claude 16 lanes at 70-80% needs 1 orchestrator and about 5 agents; the review pool is 1 agent at A (9.2, 9.8, 11)
- Evidence: capacity A: orchestrator + 3 implementers + 1 reviewer; R1 packages (K1, K2, K3, E5L, PGJ, E6w, H1, DMAPC, M2a, M2f) need 3 loops, R2 2 loops. At about 60 R1/R2 packages over 25 sessions that is about 2.4 review loops per session per reviewer-slot, each loop 1-3 h on a diff the same orchestrator integrates; roleplay responder takes a slot during live windows. Hours "one review loop included" understate R1 by the stated 10-20% only if the pool is not the bottleneck.
- Fix: state "reviewer time per session" in 9.2 (A 4-6 review-hours) and make live roleplay windows lower priority than R1 loop 2; keep +8-12% default (already in U-12) as the baseline instead of an optional upside.

### MEDIUM-8: Capacity and gate arithmetic are not anchored to a measured session (13.3)
- Evidence: "8 wall hours" and 16-20 lane-hours rest on 4 agents (50-60% efficiency); no measured Claude throughput exists for Rust (17.13 admits no Rust record). The 78% total is arithmetic of the table, fine; the sessions are not.
- Fix: label 13.3 as "model, not data" and make TW-1 re-baseline (already stated) the only dated promise; give GT0 only a date (about 5 sessions), others as ranges conditional on U-1/U-2.

### LOW-1: Hours and counts to correct
- `crates/core`: 60,541 lines including tests (src plus tests), 52 src files, 45 integration test files plus unit tests; 587 `#[test]`; "about 40 integration test binaries" is 45 here. Cargo.lock: 189 packages; `ureq`, `tiny_http`, `ed25519-dalek`, `uuid`, `rustls`, `reqwest`, `hyper` absent (agrees with plan); `tokio` present (via postgres) so "no async runtime" is already false for the lock closure.
- 3.2 "Codex main 853b029... 587 tests; `core_task.rs` pinned 0.5.0" consistent with the tree. RTX 3060 12 GB confirmed (1.4 GB in use).
- Host host: i5-12400, 6 cores/12 threads, D: NTFS 1.28 TB free, Defender real-time on (exclusions not readable without admin) — add Defender exclusion for target dirs to ENV2 (a likely larger gain than mold on NTFS).

## 3. Methodology audit (rule by rule)

| Rule | Verdict | Defect and fix |
|---|---|---|
| Strict TDD | Honoured; spikes SMAP/SNET/E9s rewritten test-first | Default for U-12 silent (no spike exemption) is right; keep |
| Independent adversarial reviews, 1-3 loops by focus | Mostly | R1 3 loops with named focus ok; R2 "semantics, edge cases" is two foci, R3 one loop without focus. Name a focus per loop in the WP (correctness, adversarial, verification) |
| Consolidated worktrees and PRs, limited worktrees | Partly | MEDIUM-6: 58 legacy worktrees, wave-size PRs, no restack rule |
| Local CI before PR | Honoured | verify-local-all must call Codex's gate unchanged plus seams leg (MEDIUM-1/2) |
| Real deps via Podman, machine per team | Weak | Both machines are distros of one 10 GB VM; plan plans to stop Codex's; Codex has none usable. Say so; do not stop `pulso-codex` without user ack and justify by measured RAM, not "6 GiB freed" |
| Never block on a merge (branch from PR-to-merge) | Honoured | Add restack rule |
| Journal UTC + team every ~15 min | Honoured | Per-lane files plus consolidated entry; fix filename convention (MEDIUM-3) |
| Spec as source of truth, additive amendments | Honoured in intent | Spec lives outside the engine repo; put amendments where precedent exists |
| Docs in English | Honoured | none |
| Never touch D:\Nexus | Honoured | none |
| Do not stop on failures | Honoured | none |
| Careful with other team's work | Weak in map | HIGH-1/2, MEDIUM-1/5: path claims are wrong and one glob and one WP cross ownership |
| Repo AGENTS.md ("no WSL dev", "no paid calls without scoped authorization") | Violated by ENV1; ok for calls | HIGH-7 |

Implied worktrees per wave: W0 up to 12 lanes, W1 up to 21 lanes against a cap of 8+1 Claude and 4 Codex; therefore at most 13 of 21 W1 lanes are worktree-backed at once and the rest queue; list the first 8 Claude lanes explicitly (L-MODEL, L-E2E, L-CLIENT, L-ENGINE, L-CAPI, L-PG, L-GOV/L-ENV, L-COMPILE) so the queue order is not invented later.

## 4. User-ask list (section 15)
- Realistic and mostly safe. Ordered by latency, the slow ones are EXT-1/2/3 (days, relay), U-5 (account), U-6, then U-14 hardware; session-1 asks that are instant are U-1, U-2, U-12, U-13, U-9, U-14 (ENV0-ENV8 subset), U-4. The plan orders externals first, the user's sentences second; a user reading it wants the opposite: put the 7 "one sentence" asks first (U-1, U-2, U-12, U-13, U-9, U-14a, U-8), relays after.
- Fixes: (1) U-14 default "ENV0-ENV8 inside current RAM" includes stopping `pulso-codex` and resizing, which are actions on shared resources, not defaults; the default should be "measure only; no machine stopped or created". (2) U-8 "PRs wait for the user" is safe but U-8 delegation to merge needs a green hosted check or the user's explicit sentence; restate that the default never merges. (3) Add the missing relay: "Codex's sandbox: can it be given read access to the vendor dir and permission for `cargo build --offline` (ENV10)?" and "may a Linux compiler toolchain image be downloaded (name, source, size)". (4) U-1 default (Codex blocked) makes 22% unreachable; state the combined default share (100% Claude) in 15 next to U-1. (5) U-5, U-6 defaults are consistent with "silence is never approval".

## 5. Three changes that most improve feasibility
1. Regenerate the Codex path map and contracts table from `ls` and `grep` (HIGH-1, HIGH-3, MEDIUM-1), pre-create the lib.rs/Cargo `mod` stubs (HIGH-2), and add real traces as goldens for DEVAL/DPGc (HIGH-6).
2. Replace the ENV stream by "measure both accounts, fix `.wslconfig` and Defender/lld, keep the rest conditional" (HIGH-4, HIGH-5, HIGH-7); recompute capacity B/C and section 13.3 from that.
3. Split K2 (K2a plus CT1), schedule trains by 25-35 lane-hours with restack rules, and count the legacy 58 worktrees (MEDIUM-5, MEDIUM-6).

## 6. Falsifiers closed or opened
- 17.1: closed (no `exclude` needed; nested `[workspace]` suffices; tested).
- 17.2: open; ENV10 stays; vendor must also be readable by the Codex account (ACL claim not checked here).
- 17.7: partly answered: no sccache/mold/nextest/ollama on host, no compiler in VM; gains unmeasured.
- 17.8: answered negatively for RAM on current host (1.7 GB free).
- New: does `seams/*` depend on `crates/core` (yes for engine/eval/pg), thus re-compiling it and inheriting its lockfile closure; the plan's vendor count must include it.
