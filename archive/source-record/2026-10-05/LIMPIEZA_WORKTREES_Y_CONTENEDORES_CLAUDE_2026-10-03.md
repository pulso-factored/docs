# Cleanup inventory: Claude worktrees, Podman (pulso-dev) and scratch (2026-10-03)

Read-only inventory. Nothing was deleted or modified. All commands below are proposals for the user to run (or approve). State is moving: other agents are active (pin bump in `improvement-engine-claude-a`, docs refresh in `claude-c` and `infra-claude-u`), so re-run the checks marked "verify" right before deleting.

Data sources: `git worktree list` in `improvement-engine` and `infra` after `git fetch --prune`; `gh pr list`; `podman --connection pulso-dev ...`; PowerShell process/size scans. `origin/main` of improvement-engine at inventory time: `f6a2963` (PR #89 merge).

## 0. Top three wins

1. **`worktrees\infra-claude-u` = 13.0 GB** (almost all of it `terraform\modules\*\.terraform` provider caches, git-ignored) plus **`worktrees\ci-parity-14666bb` = 5.4 GB** (detached, all 10 commits already on main under other SHAs). About 18 GB on D:.
2. **Podman pulso-dev: 11.4 GB reclaimable images (88%) and 3.4 GB reclaimable volumes (100%)**, mostly superseded `pulso-core-runtime` / `pulso-platform-sim` tags (pins 86a7674, 789d6c8, 894fa65) and anonymous test-PG volumes.
3. **Scratchpad ~12.3 GB** (`head` 8.9 GB, `m` 1.4 GB, `base` 0.7 GB are infra clones with `.terraform` caches; `ac894`/`agent-core-new`/`agent-core-pin`/venvs ~1 GB) plus **%TEMP% pulso venvs ~2.4 GB**.

## 1. Git worktrees

### 1.1 Claude-owned worktrees (improvement-engine)

| Worktree | Branch | Last commit | Uncommitted | Ahead/behind origin/main | Merged? | Verdict |
|---|---|---|---|---|---|---|
| `improvement-engine-claude-a` | `claude/r4-pin-c814c2b` (local only, no remote, no PR) | 2026-10-03 | 8 modified files (`core-bridge/.reports/exporter-report.json`, `demo/src/pulso_demo/driver.py`, `e2e-core/...` x5) + untracked `e2e-core/tests/unit/test_annexd_dto_first_red.py`, `.nexus-outbox/` | ahead 3 / behind 9 | No | **KEEP. In use by the pin-bump agent** (demo driver and cargo clippy/check processes running from it). |
| `improvement-engine-claude-c` | now `claude/docs-status-refresh` (was `claude/c-console-seam`, switched during this inventory) | 2026-10-03 | untracked `.nexus-outbox/` only | ahead 1 / behind 0 (PR #89 MERGED as merge commit) | Branch merged by PR #89; local tip has 1 extra commit vs origin/main (verify) | **WAIT**: a docs agent is using it; vitest + esbuild processes started from it at 19:03 are still alive (see 4). Removable after that agent finishes. `debug-console/node_modules` is 158 MB. |
| `improvement-engine-claude-u` | not a registered worktree (no `.git`) | 2026-10-03 | n/a | n/a | n/a | Stale directory copy, 497 MB (`target` 391 MB, `debug-console` 137 MB). Leftover from a failed `Remove-Item` (Permission denied). See 1.3. |
| `ci-parity-14666bb` | detached HEAD `14666bb` | 2026-10-03 | 2 modified generated reports (`core-bridge/.reports/exporter-report.json`, `demo/out/demo-report.json`) | ahead 10 / behind 71 | `git branch --contains` is empty, but all three sampled subjects exist on origin/main under different SHAs (`ef7e39a`, `6078cbe`, `cba439e`): rebased/squashed copies | **Safe to remove** (5.4 GB). Optional backup: `git branch backup/ci-parity-14666bb 14666bb` first. |

Commands (run from `D:\.codex\factored\improvement-engine`):

```powershell
# ci-parity: generated reports are the only dirt, safe to discard
git worktree remove --force D:\.codex\factored\worktrees\ci-parity-14666bb
# claude-c: only after the docs agent is done and its commit is pushed/merged
git worktree remove D:\.codex\factored\worktrees\improvement-engine-claude-c
# claude-a: NOT until the pin-bump PR is merged
```

### 1.2 Claude-owned worktree (infra)

| Worktree | Branch | Uncommitted | Ahead/behind | Verdict |
|---|---|---|---|---|
| `infra-claude-u` (13.0 GB) | now `claude/docs-status-refresh` (was `claude/u-infra-bridge-exporters`, PR #26 MERGED) | untracked `.nexus-outbox/` | 0 / 0 vs origin/main at last scan (verify) | Removable once the docs agent is done. Free 13 GB. Do it with `git worktree remove` (it will delete the `.terraform` dirs too). |

```powershell
# from D:\.codex\factored\infra
git worktree remove D:\.codex\factored\worktrees\infra-claude-u
```

### 1.3 The leftover `improvement-engine-claude-u` directory (not a worktree)

- No process has that path in its executable or arguments. Five Claude bash shells have the string `claude-u` in their command line: PIDs **13028, 21664, 15876** (started 20:27:23, child `python.exe` 17776 running `python -`) and **30568, 7436** (20:29:35). These look like a still-running (possibly hung) delete attempt from a previous agent; a shell or child whose current directory is inside the tree would produce exactly "Permission denied". `handle.exe` is not installed, so the exact holder could not be proven read-only. The directory is owned by the current user (no ACL problem).
- Proposed: stop those PIDs only if the user confirms they are dead agent shells, then delete:

```powershell
Stop-Process -Id 15876,21664,13028,30568,7436,17776   # user confirms first
Remove-Item -LiteralPath D:\.codex\factored\worktrees\improvement-engine-claude-u -Recurse -Force
# if long paths fail (node_modules/target): robocopy empty-dir mirror, then Remove-Item
#   mkdir $env:TEMP\empty; robocopy $env:TEMP\empty D:\...\improvement-engine-claude-u /MIR; Remove-Item both
```
- Its branch `claude/u-console` is already merged (PR #74), so nothing is lost. `git worktree prune` is not needed (it was never registered).

### 1.4 Local and remote Claude branches (merged = safe for `-d`)

improvement-engine, local branches, all ancestors of origin/main and none checked out now:

```powershell
git branch -d claude/c-console-seam claude/pl-platform claude/r-runtime-wire claude/r2-bridge-gaps claude/r3-annexd claude/u-console claude/u-console-demo
```

`claude/docs-status-refresh` (PR #89 merged but local tip may be ahead by 1) and `claude/r4-pin-c814c2b` (unmerged, in use): keep for now. Use `-D` for docs-status-refresh only after confirming PR #89 contains it.

infra, local branches merged into origin/main:

```powershell
git branch -d claude/fix-ci-chdir-quote claude/u-infra-bridge-exporters claude/u-infra-engine-platform claude/u-infra-reconcile
```

infra branches NOT to delete without a decision:
- `claude/u-infra-release`: PR #17 merged and `origin/claude/u-infra-release` is merged, but the local branch is **ahead 4** (the L9 `core_stack` commits, same subjects as the parked branch). `-d` will refuse. User decides.
- `claude/u-infra-core-stack-parked` (ahead 6, behind 21, "parked pending PR #20"): keep.
- `claude/docs-status-refresh`: in use.

Remote branches (**user decides**; deleting a merged PR branch is irreversible on the remote side, though the commits stay in main):

```powershell
# improvement-engine (all merged into origin/main, PRs merged)
git push origin --delete claude/c-console-seam claude/pl-platform claude/r-runtime-bridge claude/r-runtime-wire claude/r2-bridge-gaps claude/r3-annexd claude/u-console claude/u-console-demo
# infra (all merged)
git push origin --delete claude/fix-ci-chdir-quote claude/u-infra-bridge-exporters claude/u-infra-engine-platform claude/u-infra-reconcile claude/u-infra-release
```
Alternatively enable "automatically delete head branches" in the GitHub repo settings (not done here).

### 1.5 Codex-owned worktrees (do NOT delete; listed for information)

All other registered worktrees are Codex-owned (no `claude` in the name, not in the CL journal entries). Last commit dates are all 2026-10-01 to 2026-10-03. "Merged" = HEAD is an ancestor of origin/main (squash merges would show N). Dirty column = number of modified/untracked paths.

improvement-engine (main checkout `improvement-engine` is on `feat/l0-engine-foundation`, merged, 1 dirty path):

| Worktree (suffix after `improvement-engine-`) | Branch | Merged | Dirty | Ahead/behind |
|---|---|---|---|---|
| ci-dispatch | fix/ci-manual-dispatch | N | 0 | 1/362 |
| design-alignment | docs/engine-infra-design-alignment | N | 0 | 1/252 |
| docs-u02-u19 | docs/u02-source-snapshot-contract | N | 0 | 2/267 |
| e0-frozen-memory-cycle | feat/p4-durable-memory-use | N | 0 | 1/196 |
| e0-holdout-e2e-integration | feat/p4-governed-memory-recovery | Y | 1 | 0/206 |
| e0-holdout-validation | feat/p3-e0-route-resolution | N | 1 | 8/170 |
| e0-package-validation | feat/e0-package-validation | N | 0 | 2/240 |
| e0-portfolio-cli-summary | feat/e0-portfolio-cli-summary | N | 0 | 3/170 |
| e0-portfolio-e2e | feat/e0-simulation-portfolio-e2e | N | 0 | 2/170 |
| e0-review-proposal-persistence | feat/e0-review-proposal-persistence | N | 0 | 3/33 |
| e2e-executable | feat/e2e-local-executable | Y | 0 | 0/205 |
| e2e-spec | docs/e2e-path-tech-spec | N | 0 | 2/244 |
| local-ci-preflight | chore/local-ci-preflight | Y | 0 | 0/198 |
| local-e2e-script | feat/e0-local-e2e-script | N | 0 | 4/238 |
| original-contact-snapshot-projection | feat/original-contact-snapshot-projection | N | 0 | 2/206 |
| original-descriptive-proposal-e2e | feat/original-descriptive-proposal-e2e | N | 0 | 3/199 |
| original-descriptive-source | feat/original-wall-clock-source-discovery | N | 0 | 1/200 |
| original-e2e-runner | feat/local-original-e2e | Y | 0 | 0/170 |
| original-projector | feat/original-contact-projector | Y | 0 | 0/229 |
| original-snapshot-signal | feat/p2-original-snapshot-signal | N | 0 | 3/199 |
| original-stage-progress | feat/original-stage-progress | N | 0 | 4/170 |
| p1-explanation-mainline | feat/otel-local-stack | N | 0 | 11/10 |
| p1-platform-observability | feat/p1-scout-platform-signal | N | 3 | 1/172 |
| p2-e0-investigation-plan | feat/p2-value-model | N | 5 | 1/10 |
| p2-e0-multi-signal-proposals | feat/p2-e0-retry-error-overlap | Y | 0 | 0/199 |
| p2-platform-verifier | feat/pl-c4-platform-privacy-guard | N | 5 | 2/172 |
| p2-proposal-assembly | feat/e0-core-draft-binding | N | 1 | 18/65 |
| p2-signal-portfolio | feat/p2-signal-portfolio | N | 0 | 1/172 |
| p4-temporal-successor | feat/p4-temporal-memory-successor | N | 2 | 1/172 |
| p4-two-run-composition | feat/p4-two-run-memory-composition | N | 0 | 1/196 |
| restore-main | feat/codex-e0-p4-consolidated | N | 4 | 4/33 |
| runner-live-progress | feat/runner-live-progress | Y | 0 | 0/199 |
| source-adapters | feat/e2e-source-adapters | N | 0 | 2/244 |
| u04b, u08-e0, u12-e0, u12-u13-runner-compose (16 dirty) | feat/u04b-e0-replay-clock, feat/u08-e0-replay-query-adapter, feat/u12-e0-deterministic-sensor, feat/p2-u12-u13-e0-runner-compose | N | 0/0/0/16 | 4/334, 7/279, 3/264, 3/199 |
| u13, u13a-verified-candidate-admission, u14, u14-report-store, u24-v2-sequence-debug, workflow-compiler | feat/u13-autonomous-scout, feat/u13a-..., feat/u14-independent-verifier, feat/u07-durable-run-events, feat/u24-v2-sequence-debug, feat/workflow-compiler-vertical-slice | Y | 1/4/1/1/0/0 | 0 ahead |
| u13-a, u13e, u14-cumulative, u14e, u14eq, u15eq, u16, u17, u18, u19, u20, u20e, u22, u23, u23-port, u24, u26-r2 (5 dirty), u30, u33-r2, u33e, u34f, u35, u36 | feat/u13-a-..., u13e, u14-..., u14e, u14eq, u15eq, u16, u17, u18, u19, u20, u20e, u22, u23, fix/u23-..., u24, u26-..., u30, u33-r2, p4-e0-mechanism-resolution-runner, u34-f, u35, u36 | N | all 0 except u26-r2 | 1-10 ahead, 170-336 behind |

infra (Codex): `infra` (main checkout, `feat/U01-config-and-tool-probes`, 1 dirty, ahead 2/behind 68, not merged), `infra-aws-foundation` (N, 6/57), `infra-aws-foundation-mainline` (Y), `infra-design-alignment` (N, 8/57), `infra-runtime-database-wiring` (N, 7/57), `infra-shared-foundation-audit` (N, 6/57). Note: Git reports "dubious ownership" for the Codex-sandbox-owned worktrees (owner `CodexSandboxOffline`); the figures above were read with a per-command `safe.directory` override, no config changed.

Merged Codex worktrees exist (about 15), but removing them is Codex's decision. A merged HEAD does not imply the lane is finished.

Unknown owner: none among registered worktrees. `.nexus-outbox` under `worktrees\` is a Nexus receipt outbox; do not touch.

## 2. Podman, machine pulso-dev (connection `pulso-dev`)

Totals (`podman system df`): Images 521 (4 active) 12.88 GB, 11.36 GB reclaimable; Containers 4, 0 active; Volumes 128 (2 active) 3.4 GB, all reclaimable. Pods: none. The machine is very dynamic: during this inventory `pulso-claude-r4-pg`, `tender_heyrovsky` (image `pulso-core-runtime:c814c2b-d522a4f`), a `pulso-claude-e2e-1791077284626-*` compose stack (core-postgres, human-issuer, platform-sim, core-runtime...) and `pulso-claude-a-pg` appeared and disappeared. At the last check nothing was running.

### 2.1 Containers

| Name | Image | State | Class | Needed? |
|---|---|---|---|---|
| `pulso-local-postgres-1` | postgres:17-alpine | Created (never started, 2026-10-01) | local stack (compose project `pulso-local`, from Codex's `local/compose.yaml`, created on this machine before the split) | No agent needs it now; user decides |
| `pulso-local-localstack-1` | localstack/localstack:latest | Created (never started) | same | same |
| `u-rev-console` | pulso-debug-console:u-rev | Exited | Claude test leftover (console review) | No |
| `u-rev-api` | node:22.16-alpine | Created | Claude test leftover | No |
| `pulso-claude-r4-pg`, `pulso-claude-a-pg`, `tender_heyrovsky`, `pulso-claude-e2e-*` | postgres:16-alpine / pulso-core-runtime:c814c2b-* | seen running, gone at last check | **In flight: pin-bump agent. Do NOT remove.** | Yes while the pin-bump PR is open |

Networks: `podman` (default, keep), `pulso-local_pulso-internal` (local stack, with the containers above), `u-rev-net` (Claude leftover; empty). Volumes: `pulso-local_pulso-postgres` and `pulso-local_pulso-localstack` belong to the local stack (tiny, attached to the Created containers); the other 126 are anonymous 64-hex volumes from throwaway PG containers (Claude test leftovers; "dangling" count 124).

```powershell
$p = "$env:USERPROFILE\AppData\Local\Programs\Podman\podman.exe"; $c = "--connection","pulso-dev"
# Claude leftovers (safe)
& $p $c rm -f u-rev-console u-rev-api
& $p $c network rm u-rev-net
# local stack (user decides; never started)
& $p $c rm -f pulso-local-postgres-1 pulso-local-localstack-1
& $p $c network rm pulso-local_pulso-internal
& $p $c volume rm pulso-local_pulso-postgres pulso-local_pulso-localstack
# anonymous test volumes: only run when NO agent stack is running (podman ps shows nothing)
& $p $c volume prune -f
```

### 2.2 Images (sizes are per tag; layers are shared, so the true reclaim is the 11.36 GB figure)

Classification by repository:
- `localhost/pulso-core-runtime` (33 tags, 434-465 MB): pins `86a7674-*` (9 tags, 438 MB), `789d6c8-*` (19 tags, 465 MB), `894fa65-*` (3 tags: c096b2f, a7712b0, c3616d4), `claude-r-test`, and `c814c2b-*` (2 tags: **`c814c2b-d522a4f` and `c814c2b-a44003e`: KEEP**, pin-bump in flight).
- `localhost/pulso-platform-sim` (24 tags named by image id, 438-465 MB): same pin generations. KEEP only `c0e955df664a` (c814c2b build) and the sim image the e2e stack currently uses (`af1151a61ea3`, if still tagged; verify).
- `localhost/pulso-core-runtime-claude-r:keys` (465 MB): Claude leftover.
- `localhost/pulso-platform-exporter:76c6252` (186 MB) and `:2323c04` (164 MB): exporter images; `2323c04` is superseded, `76c6252` is the latest (user decides whether the pin bump still needs it).
- `localhost/pulso-local-identity` (2 tags, 176 MB): `522e083d9638` is the one in use by the current e2e stack: KEEP; `734a2f238acc` superseded.
- `localhost/pulso-debug-console` `u-rev` and `l7` (49.9 MB each): Claude test leftovers.
- 19 untagged `<none>` images (49.9 MB to 1.26 GB; one 1.26 GB): build leftovers.
- Base images (keep, cheap to re-pull but needed offline): `postgres` (3 tags: 16-alpine, 17-alpine, +1), `node:22.16-alpine`, `python`, `golang`, `nginxinc/nginx-unprivileged`, `gcr.io/distroless/static-debian12`, `localstack/localstack:latest` (only if the local stack is dropped).

Removal commands (superseded pins; the tag lists must be re-checked right before running):

```powershell
& $p $c image prune -f                                   # 19 dangling images
foreach ($ref in 'localhost/pulso-core-runtime:894fa65-*','localhost/pulso-core-runtime:789d6c8-*','localhost/pulso-core-runtime:86a7674-*',
                 'localhost/pulso-core-runtime:claude-r-test','localhost/pulso-core-runtime-claude-r:keys',
                 'localhost/pulso-debug-console:u-rev','localhost/pulso-debug-console:l7','localhost/pulso-platform-exporter:2323c04') {
  & $p $c rmi --force (& $p $c images --filter "reference=$ref" -q)
}
# platform-sim: list, then remove every tag EXCEPT c0e955df664a (and the one in use by a live e2e stack)
& $p $c images --filter reference=localhost/pulso-platform-sim --format "{{.Tag}}"
# pulso-local-identity superseded tag
& $p $c rmi localhost/pulso-local-identity:734a2f238acc
```

`podman rmi` refuses images used by a container, which is the safe behavior here. Do **not** use `podman system prune -a` or `podman image prune -a` (it would also remove the base images and the c814c2b tags that are momentarily unused).

## 3. Scratch and temp

Scratchpad `$env:USERPROFILE\AppData\Local\Temp\claude\D---codex-factored\18ab5ab6-8b27-4650-818f-7d8bb6599946\scratchpad` ~12.3 GB:

| Item | Size | Note |
|---|---|---|
| `head` | 8.9 GB | infra clone(s) with `.terraform` caches |
| `m` | 1.37 GB | infra clone |
| `base` | 686 MB | infra clone |
| `ac894`, `agent-core-new`, `agent-core-pin` | 270, 269, 233 MB | agent-core clones (894fa65 / newer pins). Keep `ac894`/`core894`/`agent-core-new` until the pin-bump PR is merged (diff references). |
| `cbvenv`, `venv`, `deps` | 152, 145, 77 MB | venvs/deps; safe |
| `ac`, `ac789`, `agent-core`, `core894`, `ie`, `pinwatch_scratch`, `pw-scratch`, others | 5-14 MB each | small; scripts, drafts, logs (about 12 MB total of text files) |

Whole `...\Temp\claude` tree: 16.4 GB (other sessions included).

`%TEMP%` (`$env:USERPROFILE\AppData\Local\Temp`), pulso-named:
- Claude venvs (~2.4 GB): `pulso-wire-venv` 223 MB, `-86a7674` 226, `-789d6c8` 260, `-894fa65` 258, `-c814c2b` 258; `pulso-ci-venv-86a7674` 223, `-789d6c8` 260, `-894fa65` 260, `-c814c2b` 260; `pulso-bc-venv` 192, `pulso-cb-venv` 32, `pulso-li-venv` 90, `pulso-plexp-venv` 46; `pulso-wire-check-*` (1 MB each), `pulso-core-context-789d6c8` 7 MB. **Keep `pulso-wire-venv-c814c2b` and `pulso-ci-venv-c814c2b`** until the pin-bump PR merges; the others are removable. The `-86a7674` venv is the L2 reference venv named in the brief; keep it only if reference runs are still wanted.
- Unknown/Codex-likely (not recommended): `pulso-u17-cargo` 2.97 GB, `pulso-u18-cargo` 2.96 GB, `pulso-u20e-cargo` 3.05 GB, `pulso-u23-cargo` 2.94 GB, `pulso-u23-audit-cargo` 0.63 GB, `pulso-u26-audit-cargo` 0.72 GB (Oct 2; names match Codex u-lane worktrees; ~13.3 GB total), `pulso-terraform-1.10.5` 115 MB, ~110 empty `pulso-ci-db-failfast-*` dirs, `pulso-e0-script-test-*`, `pulso-snapshots-e2e-*`. Ask Codex.

```powershell
$t = $env:TEMP
Remove-Item -Recurse -Force "$t\pulso-wire-venv","$t\pulso-wire-venv-86a7674","$t\pulso-wire-venv-789d6c8","$t\pulso-wire-venv-894fa65","$t\pulso-ci-venv-86a7674","$t\pulso-ci-venv-789d6c8","$t\pulso-ci-venv-894fa65","$t\pulso-bc-venv","$t\pulso-cb-venv","$t\pulso-li-venv","$t\pulso-plexp-venv"
$s = "$env:USERPROFILE\AppData\Local\Temp\claude\D---codex-factored\18ab5ab6-8b27-4650-818f-7d8bb6599946\scratchpad"
Remove-Item -Recurse -Force "$s\head","$s\m","$s\base","$s\cbvenv","$s\venv"
```

### Stray processes (PIDs only; none was stopped)

- Claude, likely stale: `bridge_mock` on port 57579: **18200, 15176** (since 15:10, old 789d6c8 venv); vitest/esbuild from `claude-c`: **28332, 26328, 12916** (since 19:03); loose `python` http server **10644** (10:41; owner unconfirmed); bash shells tied to claude-u: **13028, 21664, 15876, 30568, 7436** plus `python -` **17776**.
- Claude, in flight (do not stop): demo driver **31100, 26940** and cargo clippy/check **17792, 11860** (started 20:38, pin-bump agent in `claude-a`).
- Codex/IDE (not ours): `node.exe` 24140, 24728, 24788, 28996, 11028, 8300, 20472, 10220, 11736, 30784, 3236, 31596 (Codex cua_node), `npx @playwright/mcp` 25440, 25092, 28380, 14080, 22972, 22244, 26220, 25964.

## 4. Recommended order and what to keep

1. Wait until the pin-bump agent finishes and its PR is merged (no PR exists yet for `claude/r4-pin-c814c2b`). Until then keep: worktree `improvement-engine-claude-a`, branch `claude/r4-pin-c814c2b`, tags `pulso-core-runtime:c814c2b-*` and sim `c0e955df664a`, `pulso-local-identity:522e083d9638`, venvs `*-c814c2b`, `ac894`/`core894`/`agent-core-new` in scratch, base images, any running `pulso-claude-*` container.
2. Now (safe, no agent depends on it): `git worktree remove ci-parity-14666bb` (5.4 GB), delete the stale `claude-u` directory after stopping its shells (0.5 GB), remove `u-rev-*` containers/network/images, `image prune -f`, scratch `head`/`m`/`base`, superseded temp venvs.
3. After the docs agents finish: remove `improvement-engine-claude-c` and `infra-claude-u` worktrees (13 GB); `git branch -d` the merged local Claude branches.
4. Then: superseded `pulso-core-runtime` / `pulso-platform-sim` / exporter images, `volume prune` with no stack running.
5. User decides: remote branch deletion, `pulso-local-*` stack removal, `claude/u-infra-release` local branch (4 unpushed-looking commits), `claude/u-infra-core-stack-parked`, anything Codex-owned (section 1.5, the `pulso-u*-cargo` dirs).
6. After the pin-bump PR merges: remove `claude-a` worktree, `claude/r4-pin-c814c2b` branch, `pulso-claude-*` leftovers, c814c2b-d522a4f/a44003e images only if the next pin supersedes them, and the `*-c814c2b` venvs.
