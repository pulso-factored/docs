# Pulso local cleanup inventory

**Initial audit:** 2026-10-04 02:47 UTC  
**Scope:** `D:\.codex\factored`, `improvement-engine`, and registered Git worktrees.  
**Status:** initial inventory was followed by three verified cleanup passes; historical tables below describe the pre-cleanup state. See the latest addendum for current decisions.

**Current snapshot (2026-10-04 04:24 UTC):** PR #93 remains the last verified engine `origin/main` at `853b029f6f3843df2f3599963ab6e8565dfff700`; a live refresh was not available in this cleanup pass. There are now 4 engine and 4 infra worktrees, including each primary checkout. Root `target/`, source datasets, shared caches and Podman were not removed. Receipts and E2E outputs from removed engine trees were preserved in the root outbox/archive.

## Executive summary at initial audit

- Direct GitHub/local fetch verification confirms current `improvement-engine/main` is `41492cb7f2b20fc2d033643798659436dffb861a` (PR #90); PRs #88 and #90 are merged and the open-PR query returned none at audit time.
- Integration worktree `improvement-engine-post-merge-consolidation` was created from the exact fetched `origin/main` SHA above. Its full Rust workspace tests pass; complete local CI preflight and independent adversarial reviews are pending in this update.
- Earlier inventory found 67 registered worktrees. The current fresh `git worktree list --porcelain` count is **70**; it includes the new integration worktree and two existing Claude worktrees not listed in the earlier inventory. The initial set included 14 dirty trees; this integration worktree is now dirty with selected consolidation. “Clean” still does not mean “safe to remove”: many point at divergent feature commits.
- Podman inventory could not be read: the VM socket returned Access Denied. No container is marked as a cleanup candidate.
- This is a candidate list only. Retain all data, receipts, venvs, and reports until an explicit cleanup pass verifies ownership and reproducibility.

## Dirty worktrees: changes to review before integration

| Worktree | Branch / HEAD | Delta observed | Disposition |
|---|---|---|---|
| `improvement-engine-p1-platform-observability` | `feat/p1-scout-platform-signal` / `fbd71c8` | Uncommitted explanation read model/tests/journal | **Do not port:** current `main` already has this explanation contract, and this old worktree's final tree drops the verifier module and 11 newer tests versus `main`. The delta is superseded, not additive. |
| `improvement-engine-p2-platform-verifier` | `feat/pl-c4-platform-privacy-guard` / `2674a07` | `lib.rs` registration plus untracked privacy policy module, tests, architecture note, journal | Potentially valuable privacy boundary; source and tests are untracked. Not safe to publish before reviewing contract/tests. Preserve. |
| `improvement-engine-p2-proposal-assembly` | `feat/e0-core-draft-binding` / `ac037f6` | 13-line bitacora append only | Documentation receipt, not a product delta. The E0 assembly/binding modules are already in current main; this branch's only source differences remove newer platform explanation and runner builder-preparation behavior. Do not republish. |
| `improvement-engine-restore-main` | `feat/codex-e0-p4-consolidated` / `a496d30` | Runner builder-readiness/status/journal edits (61 lines) | **Do not port:** builder-preparation behavior is already in current main; this branch's runner drops current progress/assembly behavior. Historical consolidated branch, not a forward delta. |
| `improvement-engine-u12-u13-runner-compose` | `feat/p2-u12-u13-e0-runner-compose` / `b5850c8` | 15 files, ~1.3k uncommitted lines across authenticated U12-E evidence, U13 E0 composition, adapters, CLI and tests | **Selected for consolidation** by applying only its uncommitted patch over live main (not stale branch history). Source and consolidated-base workspace suites pass; complete preflight/review pending. Original-projection base behavior is already in main. |
| `improvement-engine-u13a-verified-candidate-admission` | `feat/u13a-verified-candidate-admission` / `014fdf7` | Scout admission code/tests plus journal; generated `target-u13a-admission/` | **Do not port:** its additions duplicate current-main `VerifiedScoutCandidate`/`ScoutCandidateAdmissionAuthority` APIs and fail to compile when naively combined (duplicate definitions). The 14 focused tests pass only against its stale base; current main's admission tests already cover the behavior. |
| `improvement-engine-u14` | `feat/u14-independent-verifier` / `7865e14` | One untracked “preparation” journal | No implementation delta visible. Journal is not evidence of a shippable feature. |
| `improvement-engine-u26-r2` | `feat/u26-stateful-sandbox-r2` / `b5c1762` | Untracked paired-scenario module/tests plus status/journal edits | **Selected for consolidation:** its 11 focused tests pass on live main. Contract explicitly says fixture-only/unverified and makes no lift claim. |

### Dirty worktrees containing only generated artifacts

| Worktree | Untracked item | Candidate action after confirming no process is using it |
|---|---|---|
| `improvement-engine` | `.nexus-outbox/` | Preserve until Nexus receipts are acknowledged/imported; not a generic temp directory. |
| `improvement-engine-e0-holdout-e2e-integration` | `.target-p4-memory/` | Build/test cache; reproducible, but retain until relevant worktree is closed. |
| `improvement-engine-e0-holdout-validation` | `.target-p3-route-red-5aa8e58/` | RED-phase test cache; keep with its work until code review is complete. |
| `improvement-engine-p4-temporal-successor` | `.target-p4-temporal-red/`, `.target-p4-temporal-red2/` | RED-phase test caches; keep with the work until review is complete. |
| `improvement-engine-u12-u13-runner-compose` | `.target-u12-u13/` | Build/test cache; preserve during feature review. |
| `improvement-engine-u13` | `target-u13/` | Build/test cache; preserve during feature review. |
| `improvement-engine-u14-report-store` | `.nexus-outbox/` | Preserve receipts; inspect receipt state before any later cleanup. |

## Branch and remote audit

The API confirms that GitHub has branches for a number of these workstreams; local `git branch -vv` reports many as having no configured upstream. Those are different facts: absence of a local tracking ref is not proof that a GitHub branch does not exist. The GitHub branch listing is paginated, so each candidate branch must be checked by exact name and commit before removal or porting.

| Branch / ref | Direct remote evidence | Assessment |
|---|---|---|
| `feat/original-descriptive-proposal-e2e` | Exists remotely; compare against live `main`: 3 commits ahead, 220 behind, diverged; 13 paths in its old merge-base diff | **Superseded:** live main already has `original_contact_projection`, snapshot descriptive envelope, runner support, tests, and journals. Its older tree omits newer runner and privacy/coverage hardening; do not PR the stale head. |
| `feat/codex-e0-p1-current-main` | Branch exists remotely (per current branch listing); its short SHA from local listing is stale/unverifiable by API | Do not use the old PR branch as the PR base; inspect exact live head before any reuse. |
| `feat/u13-autonomous-scout` | Exists remotely; its shared commit `014fdf7` compares as 0 ahead / 368 behind current `main` | Historical Scout implementation is already superseded/contained in main; the dirty U13a delta duplicates current-main admission types and is excluded. |
| `feat/e0-frozen-memory-cycle`, `feat/p4-two-run-memory-composition` | PR #71 merge is on the historical branch; live main has U23-E/U33-E code and the P4 composition journal | **Superseded for this purpose:** current main already includes the governed temporal-memory implementation; do not republish the stale branch. |
| `feat/otel-local-stack`, `feat/p2-value-model` | Their work was merged via #88 and #90 respectively | Obsolete as independent PR candidates; do not republish. |
| Other local feature refs | Multiple are detached from any local upstream and based on historical ancestors | Not classified as obsolete solely from age or local ahead/behind. Check their diff against live main before cleanup. |

## Registered worktree paths (70 at initial audit)

The list below records paths returned by the fresh `git worktree list --porcelain` audit. Clean worktrees remain protected until their branch deltas have been compared to live GitHub `main`.

```text
D:\.codex\factored\improvement-engine
D:\.codex\factored\worktrees\improvement-engine-ci-dispatch
D:\.codex\factored\worktrees\improvement-engine-claude-f
D:\.codex\factored\worktrees\improvement-engine-design-alignment
D:\.codex\factored\worktrees\improvement-engine-docs-u02-u19
D:\.codex\factored\worktrees\improvement-engine-e0-frozen-memory-cycle
D:\.codex\factored\worktrees\improvement-engine-e0-holdout-e2e-integration
D:\.codex\factored\worktrees\improvement-engine-e0-holdout-validation
D:\.codex\factored\worktrees\improvement-engine-e0-package-validation
D:\.codex\factored\worktrees\improvement-engine-e0-portfolio-cli-summary
D:\.codex\factored\worktrees\improvement-engine-e0-portfolio-e2e
D:\.codex\factored\worktrees\improvement-engine-e0-review-proposal-persistence
D:\.codex\factored\worktrees\improvement-engine-e2e-executable
D:\.codex\factored\worktrees\improvement-engine-e2e-spec
D:\.codex\factored\worktrees\improvement-engine-local-ci-preflight
D:\.codex\factored\worktrees\improvement-engine-local-e2e-script
D:\.codex\factored\worktrees\improvement-engine-main-ro
D:\.codex\factored\worktrees\improvement-engine-original-contact-snapshot-projection
D:\.codex\factored\worktrees\improvement-engine-original-descriptive-proposal-e2e
D:\.codex\factored\worktrees\improvement-engine-original-descriptive-source
D:\.codex\factored\worktrees\improvement-engine-original-e2e-runner
D:\.codex\factored\worktrees\improvement-engine-original-projector
D:\.codex\factored\worktrees\improvement-engine-original-snapshot-signal
D:\.codex\factored\worktrees\improvement-engine-original-stage-progress
D:\.codex\factored\worktrees\improvement-engine-p1-explanation-mainline
D:\.codex\factored\worktrees\improvement-engine-p1-platform-observability
D:\.codex\factored\worktrees\improvement-engine-p2-e0-investigation-plan
D:\.codex\factored\worktrees\improvement-engine-p2-e0-multi-signal-proposals
D:\.codex\factored\worktrees\improvement-engine-p2-platform-verifier
D:\.codex\factored\worktrees\improvement-engine-p2-proposal-assembly
D:\.codex\factored\worktrees\improvement-engine-p2-signal-portfolio
D:\.codex\factored\worktrees\improvement-engine-p4-temporal-successor
D:\.codex\factored\worktrees\improvement-engine-p4-two-run-composition
D:\.codex\factored\worktrees\improvement-engine-restore-main
D:\.codex\factored\worktrees\improvement-engine-runner-live-progress
D:\.codex\factored\worktrees\improvement-engine-source-adapters
D:\.codex\factored\worktrees\improvement-engine-u04b
D:\.codex\factored\worktrees\improvement-engine-u08-e0
D:\.codex\factored\worktrees\improvement-engine-u12-e0
D:\.codex\factored\worktrees\improvement-engine-u12-u13-runner-compose
D:\.codex\factored\worktrees\improvement-engine-u13
D:\.codex\factored\worktrees\improvement-engine-u13-a
D:\.codex\factored\worktrees\improvement-engine-u13a-verified-candidate-admission
D:\.codex\factored\worktrees\improvement-engine-u13e
D:\.codex\factored\worktrees\improvement-engine-u14
D:\.codex\factored\worktrees\improvement-engine-u14-report-store
D:\.codex\factored\worktrees\improvement-engine-u14-cumulative
D:\.codex\factored\worktrees\improvement-engine-u14e
D:\.codex\factored\worktrees\improvement-engine-u14eq
D:\.codex\factored\worktrees\improvement-engine-u15eq
D:\.codex\factored\worktrees\improvement-engine-u16
D:\.codex\factored\worktrees\improvement-engine-u17
D:\.codex\factored\worktrees\improvement-engine-u18
D:\.codex\factored\worktrees\improvement-engine-u19
D:\.codex\factored\worktrees\improvement-engine-u20
D:\.codex\factored\worktrees\improvement-engine-u20e
D:\.codex\factored\worktrees\improvement-engine-u22
D:\.codex\factored\worktrees\improvement-engine-u23
D:\.codex\factored\worktrees\improvement-engine-u23-port
D:\.codex\factored\worktrees\improvement-engine-u24
D:\.codex\factored\worktrees\improvement-engine-u24-v2-sequence-debug
D:\.codex\factored\worktrees\improvement-engine-u26-r2
D:\.codex\factored\worktrees\improvement-engine-u30
D:\.codex\factored\worktrees\improvement-engine-u33-r2
D:\.codex\factored\worktrees\improvement-engine-u33e
D:\.codex\factored\worktrees\improvement-engine-u34f
D:\.codex\factored\worktrees\improvement-engine-u35
D:\.codex\factored\worktrees\improvement-engine-u36
D:\.codex\factored\worktrees\improvement-engine-workflow-compiler
D:\.codex\factored\improvement-engine\worktrees\improvement-engine-post-merge-consolidation
```

> This list reflects the 70-entry registry at the initial audit, including `improvement-engine-post-merge-consolidation` and two Claude worktrees. It is a historical path inventory, not the current registry or a deletion recommendation.

## Other local data and cleanup candidates at initial audit

| Path / resource | Candidate status | Safety note |
|---|---|---|
| `improvement-engine/target/` | Build cache candidate | Re-creatable, but only after all test processes stop and workspace disk is needed. |
| Worktree-local `target*` / `.target-*` directories | Build cache candidates (see dirty table) | Do not remove while their worktrees are active or before the corresponding test evidence is recorded. |
| `tmp/`, `tmp-u23-port-doctest/`, `.scratch/` | Inspect contents first | Names imply temporary use, but age/name alone is insufficient to delete. |
| `output/` | Preserve pending content review | May contain E2E evidence/output needed for the demo or audit trail. |
| `.nexus-outbox/` (root and worktrees) | Preserve | Receipts are not disposable scratch; check receipt status before any future cleanup. |
| `.venvs/`, `data/`, `pulso_muestra_e0/`, `references/`, `demo-site/`, `design/` | Preserve | Environment, source data, project references, or demo assets; not cleanup candidates without a separate purpose check. |
| Podman machine / containers | **Unknown; not inventoried** | `podman ps --all` could not connect because access to the machine identity/socket was denied. No stop/remove action was taken. |

## Cleanup decision rules

1. A worktree is removable only after its branch is proven merged, fully superseded, or safely archived elsewhere; a clean status is not enough.
2. A local branch is removable only after its unique commits are compared against current GitHub `main` and any useful delta is published or intentionally rejected.
3. Remove build caches only after associated tests/evidence are no longer needed and no process uses them.
4. Never remove source datasets, receipts, or demo evidence as part of generic workspace cleanup.

## Verified cleanup addendum — 2026-10-04 03:20 UTC

- Verified live `origin/main` at merge commit `853b029f6f3843df2f3599963ab6e8565dfff700`; PR #93 is merged. Removed 12 obsolete/merged Codex worktrees and their worktree-local generated caches/artifacts: `improvement-engine-post-merge-consolidation`, `improvement-engine-e0-holdout-e2e-integration`, `improvement-engine-local-ci-preflight`, `improvement-engine-original-projector`, `improvement-engine-u13`, `improvement-engine-u14`, `improvement-engine-p1-platform-observability` (superseded), `improvement-engine-p2-platform-verifier` (merged in #93), `improvement-engine-u12-u13-runner-compose` (merged in #93), `improvement-engine-u13a-verified-candidate-admission` (duplicate/superseded), `improvement-engine-u26-r2` (merged in #93), and `improvement-engine-workflow-compiler` (already in main).
- Pruned stale Git worktree registrations left by those removals. Kept all branch refs; no branch deletion, reset, remote prune, or merge was performed.
- Fresh `git worktree list --porcelain` reports **58 registered worktrees**, including the main checkout and preserved Claude worktrees. Remaining worktrees were not assumed disposable: non-merged/divergent work and trees with `.nexus` receipts, E2E `output/`, `.env` or `.secrets` were left untouched.
- Preserved root `improvement-engine/target/` and `.nexus-outbox/` as requested. No shared/root cache, source data, demo artifacts, or files outside the removed worktrees were deleted.
- Podman machine and containers were **not changed**. Podman inventory remains unavailable because this environment returned access denied for the machine/socket; container deletion could not be safely scoped without an inventory.
- Windows process inventory was access-denied, and deleting a worktree-local Rust cache showed concurrent file disappearance. The explicitly authorized cleanup list completed, but do not treat unrelated caches as unused; retain them until active processes/owners can be verified.
- The old registered-worktree list and pre-cleanup counts above describe the initial snapshot only; each subsequent addendum records the count at that time.

## Second-pass cleanup addendum — 2026-10-04 03:51 UTC

- The live GitHub fetch was attempted and failed because this session could not connect to `github.com:443`. Decisions below use the last verified local refs (`improvement-engine/origin/main` `853b029f6f3843df2f3599963ab6e8565dfff700`; `infra/origin/main` `dab52ab9d7f06c42715fcfb1ed78a4ccc55b81c1`) and state this freshness limit.
- Removed the clean, merged infra checkout `infra-aws-foundation-mainline` (`ebbb7bb`, ancestor of last verified `origin/main`). It contained only source already integrated plus ignored Terraform provider/module caches and Python `__pycache__`; no state, `.tfvars`, environment file, or secret file was found. Its local branch ref was removed after verification.
- Removed four obsolete U09 Rust target-cache directories (`tmp/u09-target`, `tmp/u09-target-2`, `tmp/u09-target-final`, `tmp/u09-postrebase`); no U09 worktree remained, each directory had Cargo target-cache markers/layout, and no Cargo/Rust compiler process was visible.
- Removed duplicate generated visual-QA renders `tmp/pulso_spec_visual_qa/` and `tmp/pulso_spec_visual_qa_final/`; both manifests pointed to the canonical `output/pdf/Pulso_spec_visual.pdf`. Kept the canonical PDF and latest `tmp/pulso_spec_visual_verified/` render set.
- Removed the one-off `.scratch/restore-main-pr.md`, its now-empty directory, and `.npm_c.log` (149-byte npm log).
- Removed 31 engine and 7 infra **local branch refs only** after confirming each ref's commit is an ancestor of the last verified `origin/main` and that no worktree had it checked out. Remote branches were not changed. Unmerged branches and every branch checked out in a retained worktree remain.
- Preserved `tmp-u23-port-doctest/` because the corresponding `improvement-engine-u23-port` worktree is still retained; preserved `tmp/e0_audit_deps/` because `docs/validation/Audit-E0.py` explicitly imports it; preserved Postgres `tmp/pg-*` data because container/mount ownership cannot be checked; preserved reports, EDA outputs, demo archives, original/E0 data, `.venvs`, main read-only snapshot, all receipts, and remaining worktrees.
- Rechecked Podman; `podman ps --all` still fails with access denied opening the machine identity, and `podman machine list` fails while creating `$env:USERPROFILE\.config`. No container or Podman machine was changed. Windows process inventory remains restricted; do not remove ambiguous caches or volumes based only on their names.

## Third-pass cleanup addendum — 2026-10-04 04:24 UTC

- Rechecked live GitHub access before cleanup; refresh was unavailable, so this pass uses only the last locally verified engine `origin/main` SHA `853b029f6f3843df2f3599963ab6e8565dfff700`. No remote branches, PRs, or GitHub state were modified.
- Removed 54 obsolete, merged, superseded, or explicitly non-portable Codex engine worktrees. This takes the registered engine inventory from 58 to **4**: the primary checkout, Claude-owned `improvement-engine-claude-f`, detached read-only `improvement-engine-main-ro`, and the unique unpublished `improvement-engine-p4-temporal-successor`. The latter remains because its temporal successor outbox is unique and not consolidated. Two dirty trees (`restore-main`, `p2-proposal-assembly`) were removed only because the prior audit documents their implementation as superseded/non-portable; their local output, Nexus receipts and relevant local `.env` file were preserved in the output archive or root `.nexus-outbox`. The old branch refs remain locally for recovery; no remote refs were deleted.
- Removed engine paths (all under `D:\.codex\factored\worktrees\`, prefix `improvement-engine-`): `ci-dispatch`, `design-alignment`, `docs-u02-u19`, `e0-frozen-memory-cycle`, `e0-holdout-validation`, `e0-package-validation`, `e0-portfolio-cli-summary`, `e0-portfolio-e2e`, `e0-review-proposal-persistence`, `e2e-executable`, `e2e-spec`, `local-e2e-script`, `original-contact-snapshot-projection`, `original-descriptive-proposal-e2e`, `original-descriptive-source`, `original-e2e-runner`, `original-snapshot-signal`, `original-stage-progress`, `p1-explanation-mainline`, `p2-e0-investigation-plan`, `p2-e0-multi-signal-proposals`, `p2-signal-portfolio`, `p4-two-run-composition`, `runner-live-progress`, `source-adapters`, `u04b`, `u08-e0`, `u12-e0`, `u13-a`, `u13e`, `u14-cumulative`, `u14-report-store`, `u14e`, `u14eq`, `u15eq`, `u16`, `u17`, `u18`, `u19`, `u20`, `u20e`, `u22`, `u23`, `u23-port`, `u24`, `u24-v2-sequence-debug`, `u30`, `u33-r2`, `u33e`, `u34f`, `u35`, `u36`, `restore-main`, and `p2-proposal-assembly`.
- E2E output folders from removed trees were moved—not deleted—to `improvement-engine/output/worktree-archive-2026-10-04/`. Receipts from removed worktrees were copied into the root `improvement-engine/.nexus-outbox/`; the Claude worktree and its receipts were not touched. Archived `restore-main` environment config is retained as `.../improvement-engine-restore-main/private-local-config/restore-main.env` and is not loaded as active configuration.
- Removed two task-specific Rust build caches (`worktrees/improvement-engine-p4-temporal-successor/.target-p4-temporal-red` and `tmp-u23-port-doctest`) after confirming no Cargo/Rust compiler process was visible. Kept the P4 source worktree and the primary root `target/` cache.
- Removed the duplicate clean infra checkout `infra-shared-foundation-audit`, whose HEAD exactly matched `infra-aws-foundation` (`c40f4cf547fa70308139696918ad888898a4c560`). Kept its local branch ref and all distinct infra worktrees. Infra registry is now **4** including its primary checkout.
- Final verified local worktree counts: improvement-engine **4**, infra **4**. Podman machine/containers remain untouched because inventory is still inaccessible. Source datasets, shared Postgres temp dirs, venvs, canonical demo artifacts, and root/shared caches remain preserved.

## Historical outcome before cleanup

No pre-existing cleanup performed. One integration worktree was added from exact live `41492cb` main, then synced with PR #92's later main commit. The consolidated worktree contains only U12-E→U13 local evidence composition, platform-source privacy policy primitives, and fixture-only paired-scenario comparison; superseded features above are excluded. The complete local preflight passed (Rust fmt/Clippy/unit/integration/doc tests, Python contracts/fixtures, and Pester). PostgreSQL destructive tests remain opt-in and were not run. Independent reviewers' concerns are addressed/documented; platform policy remains primitives only, not live-source enforcement. Consolidated PR [#93](https://github.com/pulso-factored/improvement-engine/pull/93) is open and GitHub reports `mergeable=true`; hosted status API currently has no entries. No merge or pre-existing cleanup performed.
