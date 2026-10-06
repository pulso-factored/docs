# PR 32 overlap review (pulso-factored/infra), 2026-10-04

Read-only. Method: git fetch, `gh pr list`, `git merge-tree --write-tree`, `git archive` of origin/main and PR 32 into a scratch dir, then `python -m unittest discover -s tests` on each. No terraform, no AWS, no repo or branch modified.

## Headline

1. PR 32 is the only open PR. Every other remote branch is either an ancestor of main or belongs to a PR already MERGED/CLOSED (#12, #13, #14, #18, #19, #20, #2). Those branches look "ahead of main" only because they were stacked or merged through other commits; their content is already in main in reworked form (`image_registry` became `terraform/modules/ecr` via PR 24; `agent-core-aws-fase0-1` was closed and redone as PR 22).
2. `git merge-tree origin/main origin/claude/hackathon-foundations`: CLEAN, zero textual conflicts (152 files, +14,291/-8).
3. main is currently RED: `tests/test_aws_plan_review.py::CurrentTree::test_no_failures_in_current_terraform_tree` fails on origin/main (a65a26c) because `modules/data_pipeline/variables.tf:104 default = "us-east-2"` trips `hardcoded-region`. PR 32 fixes it (allowlist includes `dataset_region = us-east-2`). On PR 32 the full `unittest discover` is OK (1 skipped locally: caddy binary missing). Merging PR 32 turns main green.

## (1)+(2) Other branches and PRs

| Branch / PR | Author | Date | State | Adds | Overlap with PR 32 | Class | Consequence if both land |
|---|---|---|---|---|---|---|---|
| #31 claude/ta0-aws-asks | Andres Galvis (aleuse) | 10-04 | MERGED | aws-asks doc, plan-review checklist, `scripts/aws_plan_review.py`, its test | PR 32 edits the same checker and test | Complementary (on main) | PR 32 extends it: exact-default allowlist (`region`/`aws_region`/`cloudfront_waf_region`=us-east-1, `dataset_region`=us-east-2), scans `terraform/bootstrap`. Strict elsewhere. Safe. |
| #30, #28, #27 data pipeline/lake, ADR 0006 | Zapata | 10-04 | MERGED | `data_pipeline`, `data_lake`, ADR 0006 | Source of the us-east-2 default that reddens main; ADR number | Safe | PR 32 fixes the test; ADR 0006 is taken, PR 32 uses 0007 (next free). |
| #26, #24, #23, #17 bridge/engine platform/ecr/release validators | Andres Galvis | 10-03 | MERGED | `bridge_services`, `engine_platform`, `workload_iam`, `ecr`, `core_data`, manifest/plan validators | `tests/test_release_manifest.py` log-group owner list | Complementary | PR 32 appends `engine_task`, `hackathon_network`, `image_builder` to the asserted owner list. Any later PR adding a log-group owner conflicts on that one line. No resource overlap: PR 32 creates nothing in `envs/prod|staging`. |
| #22, #21, #16, #15, #11 (ADRs 0003, 0004, 0005, Agent Core scale) | Zapata | 10-02/03 | MERGED | Fargate/NAT/Secrets Manager/RDS Proxy design | ADR 0007 deviates from 0003/0004/0005 | Conflicting decision (documented) | ADR 0007 is "Proposed" and says so; needs Zapata's sign-off since it overrides his ADRs. No code conflict. |
| #19 feat/agent-core-image-registry (`image_registry`: ECR + optional OIDC publisher) | Zapata | 10-03 | MERGED, module not on main | ECR + OIDC publisher, `tests/test_agent_core_image_registry.py` | PR 32 `bootstrap/oidc_ecr.tf` (GitHub OIDC provider, deploy role, ECR push policy) and `image_builder` | Same purpose, superseded by `modules/ecr` + `ci_roles` | Stale branch must not be merged (duplicate ECR/OIDC). Main/PR 32 are complementary but share one account-level constraint: only ONE GitHub OIDC provider per account; `ci_roles` expects an external one, `bootstrap` creates one. A second create fails EntityAlreadyExists. `oidc_enabled` is off unless github_org and github_repo are set. |
| #18 docs/agent-core-delivery-contract | Zapata | 10-03 | MERGED | delivery contract doc + the #19 commit | as above | Duplicate/superseded | Stale branch conflicts with PR 32 only in `envs/{prod,staging}/variables.tf` because it is stale. Ignore. |
| #20 feat/agent-core-aws-fase0-1 | Zapata | 10-03 | CLOSED | first attempt of ADR 0005 | none | Dead | Ignore. |
| #13 docs/infra-engine-design-alignment, #12, #14 (feat/aws-foundation) | "Alexis Galvis" commits = Andres Galvis (aleuse) | 10-01/02 | MERGED | `security`/`storage` modules, `tests/test_aws_foundation_contract.py`, ownership docs | `test_aws_foundation_contract.py` (PR 32 edits); `security`/`storage` vs `hackathon_iam`/`hackathon_data` | Complementary | Stale branches (51 files vs merge-base) conflict with PR 32 in `modules/storage/*`, `test_aws_foundation_contract.py`, `test_terraform_first_baseline.py`; content is already on main reworked. Same owner as PR 32. Do not merge. |
| feat/U01-config-and-tool-probes | same owner | 10-01 | not an open PR (#2 merged); 1 orphan commit (Podman readiness, `scripts/doctor.py`) | none | Safe | n/a |

"Alexis Galvis" is the git author name of the same GitHub account (aleuse) that opened PR 32. Cross-person overlap is only with Zapata (ADRs 0003 to 0006, `data_pipeline`, ECR/OIDC).

## (3) Merge-tree results

- main + PR 32: clean.
- PR 32 + docs/infra-engine-design-alignment: conflicts (`modules/storage/main.tf` add/add, `storage/outputs.tf`, `test_aws_foundation_contract.py`, `test_terraform_first_baseline.py`).
- PR 32 + docs/agent-core-delivery-contract and feat/agent-core-aws-fase0-1: conflicts in `terraform/envs/{prod,staging}/{main,variables}.tf` and `tests/test_agent_core_aws_scale_contract.py`.
All are stale branches already superseded on main; none should land.

## (4) Repo-level checks and PR 32 impact

- `python -m unittest discover -s tests` (CI matrix windows and ubuntu; PR 32 raises timeout 5 to 10 min). On main today: 1 FAIL (plan review, us-east-2). On PR 32: pass.
- Edited tests:
  - `test_environment_promotion_contract.py`: allowed env set `{staging, prod}` becomes `{staging, prod, hackathon, buildbox}`. Test name still says "only staging and production"; `buildbox` is temporary, so this assertion must be edited again when it goes. Stray trailing blank line.
  - `test_aws_foundation_contract.py`: excludes `hackathon_data` from the no-secret-values scan and asserts `ignore_changes = [secret_string]`. Real exception (random RDS master password lands in state); documented in ADR 0007 but needs owner acceptance.
  - `test_release_manifest.py`: owner list; the added comment contains a literal backslash-n (cosmetic).
  - `test_aws_plan_review.py` + `aws_plan_review.py`: allowlist and `scan_extra_roots`. `ENVS = ("staging","prod")` unchanged, so `check_env` switch rules do not cover `envs/hackathon`/`envs/buildbox` (they only get `scan_tf_dir`). Gap, not a break.
- New tests: `test_deploy_stack_script`, `test_docs_consistency` (also run as its own CI step), `test_free_plan_contract`, `test_hackathon_deploy_contract`, `test_service_deployment_doc`; Pester 3.4 on Windows (`scripts/tests`); terraform init/validate/test for 9 new roots plus `hackathon_edge`. Only `.github/workflows/ci.yml` changes (no new workflow). Terraform CI steps not run by me (need provider downloads). New CI dependency: Pester 3.4.0 installed from PowerShell Gallery at run time.

## (5) Recommendations

Must change in PR 32 before merge:
1. ADR numbering: AGENTS.md says decisions live in `docs/adr/`. The free_plan "record 0008" lives only in `docs/decisions.md`. Create `docs/adr/0008-hackathon-free-plan-profile.md` (keep `decisions.md` as pointer) or drop the "0008" label; fix link in `docs/architecture.md:91`. ADR 0007 is free on main today (last is 0006); re-check right before merge.
2. Journal: AGENTS.md requires a `docs/journal` entry per slice with exact commands/results; PR 32 adds none. Add `docs/journal/0018-hackathon-foundations.md` (main's last is 0017; main already has duplicate 0002 and 0009, so verify at merge time). Mention the red-main fix.
3. Rename the test in `test_environment_promotion_contract.py` and note the `buildbox` removal condition.
4. Fix the literal `\n` comment in `tests/test_release_manifest.py`.
5. State explicitly (bootstrap README/ADR) that `bootstrap/oidc_ecr.tf` and `modules/ci_roles` are alternatives per account; keep `oidc_enabled` default off.
6. Consider adding hackathon/buildbox to `ENVS` in `aws_plan_review.py`, or document why not.
7. Obtain Zapata's explicit approval: ADR 0007 overrides ADR 0003/0004/0005 and the allowlist edit touches a checker he relies on.
8. Do not merge or revive the stale branches; ask owners to delete them.

Draft message for owners (forward as-is):

"Heads-up from Andres on infra PR 32 (hackathon single prod, free_plan profile): it is the only open PR and merges cleanly on main. It also fixes the red test_aws_plan_review on main (data_pipeline dataset_region us-east-2 is now an allowlisted default next to the us-east-1 region variables). It adds ADR 0007 plus a free_plan decision record that deviate from ADR 0003/0004/0005 for a short-lived hackathon account only, nothing applied and staging/prod untouched; please review ADR 0007 and the allowlist. Zapata: feat/agent-core-image-registry, docs/agent-core-delivery-contract and feat/agent-core-aws-fase0-1 are already superseded on main (modules/ecr, PR 22) and conflict with PR 32 only because they are stale, so please delete them; bootstrap's optional GitHub OIDC provider is an alternative to ci_roles and must never be applied in an account that already has one. If you add an ADR, take 0009 or higher after PR 32 merges, or tell me so I can renumber."
