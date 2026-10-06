#!/usr/bin/env python3
"""Apply the two edits PLATCHECK needed (denied to the agent by the auto-mode classifier; the USER authorized them and runs this script himself).

What it changes, in the infra worktree D:\\.codex\\factored\\worktrees\\infra-claude-platcheck (branch claude/infra-platform-contract):

1. terraform/envs/hackathon/main.tf, module "compute_platform": adds `extra_service_envs = ["migrate"]`.
   Effect: the platform host renders a separate `migrate.env` (keys MIGRATE__*) used ONLY by the one-shot
   `support-platform-migrate` service. The owner DSN (MIGRATE__CC_DATABASE_URL) therefore stays out of `support.env`
   (the API container), which is the least-exposure layout. No other module or host is touched.
2. docs/secrets-wiring.md: replaces three platform rows (DSN driver, migrate DSN name, CC_ENV staging) so the
   documentation matches the contract and the inventory test passes.

Safe by construction: idempotent (running twice changes nothing), local files only, no network, no AWS, no secrets,
no git commands that change history. It refuses to run if an anchor line is not found exactly once. Run `git diff`
in the worktree afterwards to review. Usage:  python apply_platcheck_edits.py [--worktree PATH] [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_WORKTREE = Path(r"D:\.codex\factored\worktrees\infra-claude-platcheck")

MAIN_TF = "terraform/envs/hackathon/main.tf"
SECRETS_DOC = "docs/secrets-wiring.md"

TF_ANCHOR = "  extra_bundle_files      = local.platform_agent_files\n"
TF_LINE = '  extra_service_envs      = ["migrate"]\n'

DOC_ROWS = [
    (
        "| `CC_DATABASE_URL` |",
        "| `CC_DATABASE_URL` | D | `postgresql://platform_app...@core.<zone>:5432/platform?sslmode=<mode>` (psycopg 3: no `+asyncpg` scheme, no `?ssl=` query); needs `platform_database_enabled` |\n",
    ),
    (
        "| `CC_MIGRATE_DATABASE_URL` |",
        "| `MIGRATE__CC_DATABASE_URL` | D | `platform_owner` DSN rendered ONLY into `migrate.env` for the one-shot `support-platform-migrate` service (`cc-migrate` reads `CC_DATABASE_URL`); never into `support.env`, so the API never sees the owner DSN |\n",
    ),
    (
        "| `CC_ENV`, `CC_SEED_DEMO_DATA`,",
        "| `CC_ENV`, `CC_TRUSTED_PROXIES`, `CC_MIGRATE_ON_START`, `CC_AGENT_CORE_TIMEOUT_SECONDS`, `CC_SEED_DEMO_DATA`, `CC_DEV_MAILBOX`, demo-seed variables | C | set in `deploy/hackathon/platform/compose.yaml`: `CC_ENV=staging` enforces the platform runtime contract and still allows the demo accounts (`demo1234`), the dev MFA code `000000` and the dev mailbox (`CC_ENV=prod` refuses all three); decided: the AWS deployment runs the demo accounts and seeds |\n",
    ),
]


def fail(msg: str) -> "None":
    print(f"STOP: {msg}", file=sys.stderr)
    sys.exit(2)


def edit_main_tf(path: Path, dry: bool) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.find('module "compute_platform" {')
    if start < 0:
        fail('module "compute_platform" not found in main.tf')
    end = text.find("\n}\n", start)
    block = text[start : end + 3]
    if "extra_service_envs" in block:
        return "main.tf: already has extra_service_envs in compute_platform (no change)"
    if block.count(TF_ANCHOR) != 1:
        fail("anchor `extra_bundle_files = local.platform_agent_files` not found exactly once inside compute_platform")
    new_block = block.replace(TF_ANCHOR, TF_ANCHOR + TF_LINE)
    if not dry:
        path.write_text(text[:start] + new_block + text[end + 3 :], encoding="utf-8", newline="")
    return "main.tf: added extra_service_envs = [\"migrate\"] to compute_platform"


def edit_doc(path: Path, dry: bool) -> list[str]:
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    lines = raw.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    for prefix, new_row in DOC_ROWS:
        idx = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
        done = [i for i, ln in enumerate(lines) if ln == new_row.rstrip("\n")]
        if done and not idx:
            out.append(f"doc: row already updated ({prefix[:28]}...)")
            continue
        if len(idx) != 1:
            fail(f"expected exactly one doc row starting with {prefix!r}, found {len(idx)}")
        lines[idx[0]] = new_row.rstrip("\n")
        out.append(f"doc: replaced row {prefix[:28]}...")
    if not dry:
        text = "\n".join(lines)
        if crlf:
            text = text.replace("\n", "\r\n")
        path.write_bytes(text.encode("utf-8"))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--worktree", type=Path, default=DEFAULT_WORKTREE)
    ap.add_argument("--dry-run", action="store_true", help="check anchors and report, write nothing")
    args = ap.parse_args()
    wt: Path = args.worktree
    tf, doc = wt / MAIN_TF, wt / SECRETS_DOC
    for p in (tf, doc):
        if not p.is_file():
            fail(f"file not found: {p}")
    head = (wt / ".git")
    if not head.exists():
        fail(f"{wt} is not a git worktree")
    print(edit_main_tf(tf, args.dry_run))
    for line in edit_doc(doc, args.dry_run):
        print(line)
    print("dry run only, nothing written" if args.dry_run else f"done. Review with: git -C \"{wt}\" diff --stat")


if __name__ == "__main__":
    main()
