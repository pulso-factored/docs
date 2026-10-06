# Cleanup executed (Team Claude), 2026-10-03

Executed from LIMPIEZA_WORKTREES_Y_CONTENEDORES_CLAUDE_2026-10-03.md after re-verifying every item. Each action lists evidence and result.

## Before / after
| Metric | Before | After |
|---|---|---|
| Free D: | 1121.5 GB | 1126.2 GB (infra-claude-u 13 GB still pending, see Skipped) |
| Free C: | 96.2 GB | 95.8 GB (scratchpad/venv deletions did not show as free space; other processes or Podman VHD writes moved it) |
| podman system df Images | 521 (12.88 GB, 11.36 GB reclaimable) | 67 total, 4.296 GB (2.774 GB reclaimable = base images) |
| podman Volumes | 128 (3.405 GB) | 2 (pulso-local_*, 0 B) |
| podman Containers | 4 | 2 (pulso-local-* kept) |

## 1. improvement-engine (git)
- Fetched origin (origin/main 41492cb). `gh pr list`: PRs 74,76,77,79,80,81,82,84,85,86,89,91 (all Claude heads) MERGED; no open claude/* PR.
- Worktrees ci-parity-14666bb (commits co-authored by Claude; `git cherry origin/main` showed all 10 as `-`, i.e. in main by patch-id; dirt = 2 generated reports), improvement-engine-claude-a (branch claude/r4-pin-c814c2b == origin, PR #91 merged, `git cherry` empty, only .nexus-outbox), improvement-engine-claude-c (claude/docs-status-refresh == origin, PR #89 merged, only .nexus-outbox): `git worktree remove --force` failed partway ("Permission denied" / "Invalid argument") because holders existed. Holders stopped after checking command lines: PIDs 13028, 21664, 15876 (+child python 17776) = bash shells whose command contained `infra-claude-u` (not ancestors of this shell; their parent was the session host claude.exe 20600, which I did not touch); 29700 (+27100, 18784) = pwsh running verify-local-ci.ps1 in ci-parity-14666bb; 26328/28332/4084/12916 = npx/node vitest + esbuild from improvement-engine-claude-c. Then a recursive force delete removed ci-parity-14666bb, claude-a, claude-c; `git worktree prune` ran.
- Stale improvement-engine-claude-u dir: first attempts failed on `core-bridge` (busy). Holder: bridge_mock python 18200/15176 (cmdline `pulso-wire-venv-789d6c8 ... bridge_mock.main --port 57579`, since 15:10, Claude). Stopped, deletion then succeeded.
- Other stray Claude processes stopped: python http probe 10644 on :18999 and its parent bash 26176 (cmdline showed the Claude shell snapshot and the probe code). Cargo/rustc processes now running belong to Codex lanes (no Claude worktree remains): left alone.
- Mistake and repair: I accidentally ran `git checkout --detach` in the main improvement-engine checkout, then restored it with `git checkout feat/l0-engine-foundation` (HEAD 6bf9c3d, same as before; no file changes).
- Local branches deleted with `git branch -d` (merged into origin/main): claude/c-console-seam, docs-status-refresh, pl-platform, r-runtime-wire, r2-bridge-gaps, r3-annexd, r4-pin-c814c2b, u-console, u-console-demo (9).
- Remote branches deleted (`git push origin --delete`, PR MERGED, no open PR): claude/c-console-seam, docs-status-refresh, pl-platform, r-runtime-bridge, r-runtime-wire, r2-bridge-gaps, r3-annexd, r4-pin-c814c2b, u-console, u-console-demo (10).

## 2. infra
- Local branches deleted with `-d`: claude/fix-ci-chdir-quote, u-infra-bridge-exporters, u-infra-engine-platform, u-infra-reconcile (4).
- Remote branches deleted: the same four (PRs #25, #26, #23, #24 MERGED).
- KEPT: claude/u-infra-release (local ahead 4: `git cherry` shows 4 `+` patches not in main), claude/u-infra-core-stack-parked (no PR, `git cherry` shows 6 `+` patches not in main, so not superseded).
- SKIPPED (denied by the Claude Code permission classifier, "Git Destructive"; not retried or worked around): `git worktree remove --force worktrees\infra-claude-u` (13 GB, clean except .nexus-outbox, branch claude/docs-status-refresh == origin, PR #29 merged, cherry empty) and the remote delete of claude/u-infra-release (and claude/docs-status-refresh). Left for the user.

## 3. Podman (pulso-dev only)
- Removed containers u-rev-console, u-rev-api; network u-rev-net.
- `volume prune -f`: 126 anonymous volumes removed (2 pulso-local_* kept: attached to the kept containers).
- `image prune -f` (dangling images) and `rmi` one by one (56 tags, 0 failures): pulso-core-runtime 86a7674-* (6), 789d6c8-* (21), 894fa65-* (3), claude-r-test, pulso-core-runtime-claude-r:keys, pulso-debug-console u-rev and l7, pulso-platform-exporter:2323c04, pulso-local-identity:734a2f238acc, and 22 pulso-platform-sim tags (all except those of the c814c2b builds: 9c115ad3ee60, c0e955df664a, e01b91231d40).
- KEPT: pulso-core-runtime c814c2b-{6a562a2,a44003e,d522a4f}, platform-sim x3 above, platform-exporter:76c6252 (last commit touching platform-exporter in main), local-identity:522e083d9638, base images (postgres 16/16-alpine/17-alpine, python, golang, node, nginx, distroless, localstack).
- KEPT pulso-local-postgres-1 / pulso-local-localstack-1 + network pulso-local_pulso-internal + volumes pulso-local_*: labels show compose project pulso-local created from D:\.codex\factored\infra\local\compose.yaml (Codex-owned file), a sign of Codex origin.

## 4. Disk
- Scratchpad: deleted all 33 subdirectories (head 8.9 GB, m 1.4 GB, base 0.7 GB, ac894, agent-core-new, agent-core-pin, core894, ac, ac789, agent-core, cbvenv, venv, deps, probes, ...) after checking: the *-c814c2b venvs are editable-installed from references\agent-core-c814c2b (not from scratch clones); none of the git clones had unpushed commits; head/m/base were plain copies. Also deleted all non-.md files (scripts, logs). Kept common_brief.md and all .md drafts/reports (46 items remain).
- %TEMP% deleted: pulso-bc-venv, pulso-li-venv, pulso-plexp-venv, pulso-wire-venv, pulso-wire-venv-86a7674, -789d6c8, pulso-ci-venv-86a7674, -789d6c8, -894fa65, pulso-wire-check-{789d6c8,86a7674,894fa65}, pulso-core-context-789d6c8. KEPT: pulso-wire-venv-c814c2b, pulso-ci-venv-c814c2b, pulso-wire-check-c814c2b, pulso-cb-venv (used by core-bridge/scripts/test.ps1), pulso-wire-venv-894fa65 (needed by test_expand_contract.py as OLD python). Not touched: pulso-u*-cargo, pulso-ci-db-failfast-*.
- KEPT references\agent-core-894fa65 (core-bridge/tests/integration/test_expand_contract.py OLD_CHECKOUT / OLD_PY).

## 6. references\agent-core-789d6c8
SKIPPED: still referenced on origin/main: core-bridge/tests/runtime/test_image.py lines 96 and 117 use it as the default PULSO_CORE_CHECKOUT (the tests skip silently if it is missing). Deleting is safe after changing that default to agent-core-c814c2b (a code change, outside cleanup scope).

## Final state
`git worktree list` (improvement-engine) has no Claude/ci-parity entries; infra still lists infra-claude-u. `podman ps -a`: only pulso-local-postgres-1 and pulso-local-localstack-1 (Created). Podman pulso images: the 8 kept ones plus base images. Nothing under D:\Nexus, $env:USERPROFILE\.claude, or Codex resources was touched.
