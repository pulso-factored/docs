# Pulso Worktree and Temporary-Artifact Inventory

**Checked:** 2026-10-04 (UTC)  
**Scope:** local Pulso `improvement-engine` worktrees, shared Git stashes, and nearby generated artifacts. This is an inventory, not a cleanup authorization for Claude-owned work or ambiguous user data.

## Decision summary

- `git worktree list --porcelain` reports **47 registered engine worktrees**: one clean `main` checkout, 45 Claude-owned checkouts, and the active Codex PR #95 successor checkout.
- All 47 registered paths exist. `git worktree prune --dry-run --verbose` found no stale registrations. **No worktree is confirmed safe to delete.**
- The Codex checkout is actively used to finish the existing PR #95 increment and is dirty in exactly four tracked files. Preserve it until publication and user review.
- Preserve all Claude-owned checkouts, whether clean or dirty. Six Claude checkouts have uncommitted/untracked content (listed below); the remaining 39 Claude checkouts and the detached `claude-demo-run` checkout are clean, but ownership still belongs to Claude.
- There are **six shared Git stashes**. All contain recoverable, potentially useful work; preserve all until individually reconciled with their owners and current `main`.
- No Podman containers or machines were inspected or modified in this audit.

## Engine worktree inventory

| Owner / checkout | Branch | Status | Disposition |
|---|---|---|---|
| Main checkout: `D:\.codex\factored\improvement-engine` | `main` | Clean | Preserve |
| Codex: `D:\.codex\factored\worktrees\improvement-engine-p4-temporal-successor` | `codex/w2-independent-slices` | Four modified tracked files; no staged or untracked files | Preserve until PR #95 update is published and reviewed |
| Claude: `D:\.codex\factored\worktrees\improvement-engine-claude-demo-run` | detached | Clean | Preserve; Claude-owned |
| Claude: `D:\.codex\factored\worktrees\improvement-engine-claude-w2a-mig0` | `claude/w2a-mig0` | Untracked `seams/target/` build output | Preserve; owner confirmation required before any cleanup |
| Claude: `D:\.codex\factored\worktrees\improvement-engine-claude-w2b-k2` | `claude/w2b-k2` | Untracked `rfc8785-0.1.4-py3-none-any.whl` | Preserve; owner confirmation required |
| Claude: `D:\.codex\factored\worktrees\improvement-engine-claude-w4c-p1` | `claude/w4c-p1` | Three modified generated egg-info files | Preserve; owner confirmation required |
| Claude: `D:\.codex\factored\worktrees\improvement-engine-claude-w4f-q1` | `claude/w4f-q1` | Untracked `seams/stand-in` | Preserve; owner confirmation required |
| Claude: `D:\.codex\factored\worktrees\improvement-engine-claude-w7-auto` | `claude/w7-auto` | Untracked `debug-console/fixtures/automation/` and `debug-console/tests/component/AutomationView.test.tsx` | Preserve; likely active feature work |
| Claude: `D:\.codex\factored\worktrees\improvement-engine-claude-w7-wire` | `claude/w7-wire` | Modified `seams/crates/pulso/tests/run_tasks.rs` | Preserve; owner confirmation required |

The other **38 Claude-owned worktrees** were clean at inspection and remain preserved because their ownership is explicit. Branch/path suffixes were: `w0-train`, `w1i-gt05`, `w2a-e1`, `w2a-k1`, `w2b-boot`, `w2c-e2`, `w2c-k2h`, `w2d-aus`, `w2d-e5l`, `w3a-bk0`, `w3b-pgjs`, `w3b-reg`, `w3c-e4r`, `w3c-v1`, `w4a-live`, `w4b-cpg`, `w4b-v3r`, `w4c-k5a`, `w4d-bknl`, `w4d-p2r`, `w4e-in0`, `w4e-mem1`, `w5a-dbg`, `w6-demo`, `w6-integ`, `w6-pglive`, `w6-r1e`, `w6-r1e-review`, `w6-r1g`, `w6-r1g-review`, `w6-r1m-review`, `w6-r1r`, `w6-r1r-review`, `w6-r1s`, `w6-r1v`, `w6-r1v-review`, `w7-attach`, and `w7-contracts`. The listed set is preserved even where its branch has already been merged, because a clean checkout is not proof that its owner has finished with the environment.

## Shared stashes

| Stash | Branch / message | Contents (summary) | Disposition |
|---|---|---|---|
| `stash@{0}` `48cd43b` | `codex/w2-independent-slices` / `CX0243-dpl2-red-baseline` | 524 added lines in `crates/core/src/platform_sensor.rs`; temporary DPL2 baseline | Preserve until the PR increment and its RED evidence are fully recorded; reassess after publication |
| `stash@{1}` `7c69ada` | `feat/p4-proposal-activity-timeline` | 81 test lines in `crates/runner/tests/e0_proposal_output.rs` | Preserve; reconcile later |
| `stash@{2}` `5d4c500` | `feat/u33-frozen-e0-memory-publication` | Frozen-memory publication, governed-memory/lib, and status documentation changes (259 insertions) | Preserve; reconcile later |
| `stash@{3}` `cbcdf5b` | `feat/original-contact-snapshot-projection` | 850 lines across source adapters, local simulation, runner, tests, and docs | Preserve; reconcile later |
| `stash@{4}` `138345b` | `feat/u13-a-verified-admission` | 859 lines in autonomous scout and library registration | Preserve; reconcile later |
| `stash@{5}` `4bb1e62` | `feat/u29-observability` | CI and library registration changes | Preserve; reconcile later |

## Nearby non-worktree artifacts

| Path / artifact | Evidence | Disposition |
|---|---|---|
| `D:\.codex\factored\worktrees\.nexus-outbox` | Durable local Nexus receipts/outbox | Preserve |
| `D:\.codex\factored\worktrees\.pytest_cache` | Regenerable cache, but mtime is current and active use/diagnostic value was not established | Do not delete yet |
| `D:\.codex\factored\worktrees\{bs-test.log,eng-test.log,init.log,w4f-build.log,w7auto-npm.log}` | Small logs with current mtimes; some correspond to Claude work | Preserve pending owner confirmation |
| Engine `target/` and ignored `output/` | Generated, but active local validation/E2E output | Preserve through final PR verification |
| `seams/target/` in Claude W2a | Untracked build output under an active Claude checkout | Do not touch |
| `D:\.codex\factored\buildbox\` Terraform files, plans, backend state, and logs | Separate infra/buildbox state, potentially sensitive | Out of scope; preserve |
| `D:\.codex\factored\tmp\`, root output, EDA/data, virtual environments, E0 sample, docs/references/demo/design | Ownership or continuing value not proven | Preserve |
| Physical infra worktrees under `worktrees/` | Not engine registrations; include AWS foundation/design/runtime and Claude infra work | Out of scope; preserve |

## Branch reconciliation notes

- Live GitHub showed only PR #95 (Codex) and PR #97 (Claude) open at inventory time; PR #19 is closed unmerged. Earlier PRs #69, #75, #78, #87, and #88 are merged.
- Several stale local branch tips contain code that is already in current `main` or PR #95, so their ancestry-only commit counts are not proof of missing changes. Do not merge old branch histories wholesale.
- `fix/ci-manual-dispatch` is one optional workflow-dispatch commit from closed-unmerged PR #19; it is stale/operational unless explicitly re-requested.
- `fix/u23-temporal-memory-hardening` removes expiry/fencing behavior relative to current `main` and must not be revived wholesale.
- `feat/p4-proposal-activity-timeline` contains a distinct runner-observability delta, and an older `feat/e0-holdout-validation` head has an alternate implementation. Both require a separately scoped future review; neither is part of the current PR #95 closing increment.

## Safe cleanup conclusion

There is no confirmed stale worktree, stash, or file to remove now. In particular, do not run recursive deletion over `worktrees/`, do not prune live worktrees, and do not remove Claude-owned or infrastructure paths. Re-evaluate only after PR #95 is published and the relevant owners confirm their work is complete.

## Closing update — 2026-10-04T22:20Z

- PR #95's Codex increment is committed and pushed as `765d99b68318bca14acece6dd24e1f2db9d1e6d5` on `codex/p4-temporal-xstub-consolidated`. The Codex worktree registration became stale after its checkout metadata disappeared; `git worktree prune --verbose` removed that stale registration. The current `git worktree list` reports 47 entries and no longer lists `improvement-engine-p4-temporal-successor`.
- The former checkout directory still contains `target/`, `target-local-e2e/`, and `tests/`. Rust build processes were present during cleanup, so `target/` was preserved rather than deleted while potentially in use. `target-local-e2e/` contains E0/original snapshots and run outputs, and `tests/` contains test assets; both are preserved. No Claude-owned worktree, stash, Podman resource, dataset, or E2E artifact was deleted or modified.
- The previous inventory rows describing the Codex checkout as dirty and its temporary stash as pending are historical as-of-audit observations; implementation is published and the exact temporary baseline stash was dropped after verification. All other shared stashes remain untouched.
- GitHub Actions had no status entries in the last connector read. The GitHub CLI live read was blocked by host network policy; prior connector verification reported PR #95 open, mergeable, not merged, at the published head above. No remote CI pass is claimed.
