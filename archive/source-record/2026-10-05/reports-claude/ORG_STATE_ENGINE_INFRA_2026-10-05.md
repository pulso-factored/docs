# State of improvement-engine and infra (survey, 2026-10-05)

Read-only survey. Method: `git fetch origin` in the existing checkouts (refs only, no branch change), then `git show origin/main:<path>`. Nothing was built, run, applied or modified. Marks: [V] read in code or docs on origin/main, [D] stated in a doc or journal and not re-run by me, [U] unverified.

Heads read: improvement-engine origin/main `879cd4a5` (2026-10-05 10:56 -0500, merge of PR #110 DET1 full-period cells; PR #109 Codex R3-2/R3-3 just before it). infra origin/main `7251d8f` (2026-10-05 08:32, merge of PR #37 "shared Core is agent-core serve").

Executive truth: the engine is a working local loop (real models, real agent-core registry on a local stack, real bank aggregates) that stops at "a person decides". Infra is a complete, mock-tested Terraform design for a single hackathon environment, with NOTHING applied by evidence.

## 1. What exists

### 1.1 Engine pipeline (detect -> propose -> prove -> announce -> outcome)

| Stage | What it is | State | Evidence |
|---|---|---|---|
| Sensor (bank cells) | Rust `steps::cells` (`steps_cli cells`): contrast cell vs rest-of-channel, BH multiplicity, discovery/holdout halves, R2 windows, k>=10 suppression. DET1 (PR #110, merged): `period: ALL`/`W1`/`W2` cells, pooled support floor, `replication_underpowered`, `depends_on` (M6/M10 -> M1), M1 reason-only family. `cells_exploratory` tier (BH q 0.10, 3 pp, ratio 1.15, support 200) emits `candidate_exploratory`, never `corroborated` | Built, tested on real bank aggregates; label `claude-standin` for the sensor semantics | [V] docs/data/bank-cells-metrics.md; [D] bitacora CL-0076 |
| Sensor (other sources) | E0 local sensors (recurring copilot query, tool retry, technical errors, holdout), platform-events sensor `rust-events` (offline on simulator), agent-run aggregator `AG_*` (synthetic only), scheduled probes/battery | E0 and platform paths run locally on frozen/simulated data; agent runs and live platform feed not connected | [V] docs/IMPLEMENTATION_STATUS.md; docs/data/agent-runs/README.md; scripts/battery |
| Reasoning roles | `seams/crates/reasoning`: Scout (mimo flash), independent Verifier (mimo pro), Builder (flash default, pro recommended), mapping table (hypothesis of where to intervene), rubric R1-R12, dossier ES/PT | Live on gateway; Builder variance with flash (2 of 3 synthetic runs refused by proof) | [V] docs/dev/DEMO_LOOP.md, MAPPING.md |
| Mapping | `mapping_table.json`: finding cell -> candidate artifacts (max 2 tried). Queja M1 -> `template:t/estado_pqr`, then `p/resumen_radicado`; Tecnico/Comercial/Retencion -> NEW agent | Works; new-agent path ends `not_announced:infra_failed` (no admin credential for release settings) | [V] MAPPING.md; DEMO_LOOP.md |
| Registry-writer / compiler | `seams/crates/registry-writer`: put_draft, validate, freeze, evaluate as `builder` principal, Idempotency-Key = finding key; closure, guard, announce | Real against a local agent-core; engine never approves/publishes | [V] DEMO_LOOP.md |
| Proof (evaluate before announce) | Regression suite built from the failing cell must FAIL on base, PASS on candidate, plus wording probe; only proven proposals are announced; deterministic judge, `uncalibrated` | Real execution on local stack; proves the suite discriminates, not customer benefit | [V] DEMO_LOOP.md, W11 doc |
| Dossier | ES (and PT) decision dossier with evidence, same-channel baseline, diff, verdict story, risks | Built; 3 golden dossiers spec (Codex T4) | [V] docs/data/dossier/DOSSIER_SPEC.md, docs/dev/DOSSIER_EXAMPLES.md |
| Announce | POST to support-platform `/internal/builder/proposals/announce` (service token), one notification per supervisor | Verified only against a platform DOUBLE (`scripts/ann1/platform_double.py`); real PR 17 backend exercised once in ANN1 journal 0657 [D]. Without `PULSO_PLATFORM_*` it prints the body | [V] DEMO_LOOP.md |
| Outcome step | `release.published/promoted/revoked` trigger -> before/after on the treated cell vs sibling controls via estimator subprocess (`pulso.outcome.v1`) -> card `improved / no_detectable_change / worsened / inconclusive` | Code and 16 offline tests; NOT exercised after a real release (nothing is published); expected mostly `inconclusive` on stationary data | [V] docs/dev/OUTCOME_STEP.md |
| Maturity | `seams/crates/maturity` with `platform_aligned` profile (S21 thresholds) | Built and tested | [V] docs/dev/MATURITY_ALIGNMENT.md |
| Debug console | internal observability of our own engine (backoffice), `pulso serve`/`pulso run` | Runs on fixtures and live engine events | [V] debug-console/, seams/crates/debug-api |

### 1.2 Artifact kinds (proposal targets)

| Kind | Propose | Validate / evaluate / publish | Evidence |
|---|---|---|---|
| prompt (op replace) | supported, real Core live | supported live | [V] contracts/artifact-kinds/README.md (BK0 matrix) |
| eval_suite (draft-only, op add) | supported | supported live | same |
| template (`t/estado_pqr`) | Used by the MAP1/loop in real runs (patch of a template placeholder) | proven live on local stack; but the frozen BK0 matrix still lists `template` as `denied(kind_not_supported)` for propose: the matrix lags the code [U, reconcile] | [V] DEMO_LOOP.md vs matrix.json |
| new agent | compiled, evaluated; announce blocked by `forbidden_role` 403 (needs admin credential) | blocked | [V] DEMO_LOOP.md |
| flow, policy, tool link | feasible in registry (no Core change), not built in engine; ART2 (tighten-only policy, read-only tool link) pushed on `claude/art2-policy-toollink`, not merged | `not_exercised` | [V] ARTIFACT_KINDS_FEASIBILITY_2026-10-05.md; [D] plan 18-ter |
| agent, decision_model, language_detection, injection_ruleset, model_profile, knowledge_snapshot, tool (executor) | denied by engine compile step | blocked/not_exercised; tool blocked on executor registration; decision_model jev blocked | [V] matrix.json |
| release_settings | denied by bridge | - | [V] matrix.json |

### 1.3 Detection coverage

| Item | Number / state | Source |
|---|---|---|
| Metrics | M1 contact_unresolved_rate, M2-M5 (PQR, open rate, etc.), M6 survey low score (+M6R/M6U/M6L variants), M7 digital error rate (descriptive), M8 consent level_risk (threshold 0.10, min excess 0.05; separate Bonferroni family), M9 declines (refuted/negative control), M10 handle-time share (depends on M1); E1 copilot-capability control | [V] docs/data/bank-cells-metrics.md; plan 18 W1-4 |
| Real aggregates | 7,995 treated cells (M1-M10) in the demo cache; 3,657-row snapshot for scoring (outside Git) | [V] DEMO_LOOP.md; [D] bitacora |
| Measured recall/precision (before DET1) | Against Codex OPBENCH v2 catalog: recall 0.4545 (10 of 22 positives; 12 missed all M1 reason x non-phone channel), precision 0.769, 1 reported non-finding (M6 technical x mobile_app), 2 unmatched M10 | [D] bitacora CX-R3-032/033; DETECTION_GAP_ANALYSIS |
| After DET1 (PR #110) | Corroborated 19 -> 37 cell signals; 11 of the 12 previously missed cells now corroborated, Technico x Web only exploratory. Real recall/precision against v2 catalog NOT yet computed (catalog was not found by the DET1 lane; Codex asked to rescore) | [D] CL-0076 (bitacora). Treat any new recall number as [U] until rescored |
| Exploratory profile | `candidate_exploratory` tier scored separately, never counted in recall/precision | [V] scripts/scoring/README.md |
| Known gaps | Reasoning/value loop does not yet consume `candidate_exploratory` (Finding::from_report takes corroborated only); sensor does not suppress discard counts < k; language x channel cells impossible on bank data (no language column); free text, transcripts, surveys comments never read | [D] CL-0076; [V] bank-cells-metrics.md |

### 1.4 Data sources

| Source | Status |
|---|---|
| Bank dataset (call center, PQR/complaints, digital events 15.6M, transactions, marketing, surveys; snapshot 2026-06-18) | Real, aggregate-only, k>=10; one real structure only (contact reason, M1) |
| E0 (dispute cases, copilot queries, tool calls, close) | Frozen package; only `complaint_id` joins to bank; copilot queries and `case_close` are generated enrichment, not production telemetry |
| Platform events (57 types, contract 1.2/1.3) | Offline simulator and ANN1 double; live feed not connected; 32 event types missing in contract 1.3.0; payload shapes unconfirmed |
| Agent runs (agent-core run exports) | Aggregator exists (synthetic); needs contract 1.4 export and live traffic |
| Probes/battery | Synthetic scenarios against own battery core, never customers |

### 1.5 Observability (Langfuse)

| Item | State | Evidence |
|---|---|---|
| Langfuse Cloud US closure | Live proof recorded: 2 story traces with engine + gateway + agent-core spans under one trace id, 2 agent-run traces, 4 scores per story, 3 priced models, 32 spans forwarded, 0 failed | [D] plan 18-ter; [V] docs/dev/LANGFUSE_CLOSURE.md (one-command `scripts/o11y/langfuse_closure.ps1 -All`, ~10-20 min first time, ~6 min after) |
| Components | local OTLP forwarder (holds key), run-trace bridge, deterministic trace id from finding key + run id, `traceparent` engine -> gateway/agent-core | [V] docs/dev/O11Y.md |
| Upstream PRs | llm-gateway #4 (merged by user), agent-core #48 (merged); engine PR #107 forwarder/bridge/closure: main now includes it [V by file list: scripts/o11y/* present on origin/main] | [V] tree listing |
| Full content to Langfuse | authorized; platform does NOT use Langfuse | [D] plan 18 W1-3 |
| Review risks (Codex R3-1) | gateway #4: caller-controlled baggage/user.id in spans; raw prompt capture is process-wide env | [D] CX-R3-061/062 |

### 1.6 Codex deliverables

| Deliverable | State | Evidence |
|---|---|---|
| T1 outcome estimator (`scripts/aggregate/outcome/`) | Merged; partial: aggregate dependent placebo windows and absent release/customer-cluster history cannot establish calibrated FPR/power/MDE | [D] CX-R3 (bitacora ~l.2678); [V] files present |
| T2 eval bank (`agent-core-assets/eval-suites/codex-bank`: disputas, consultas, copiloto-asesor, recepcion; 104 cases) | Merged; 69 of 104 are prompt-only with no explicit expect/assertion; exact 104-case native evaluation unverified; no paid/provider call | [D] CX-R3-043 |
| T3 run-trace source / agent_runs aggregation | Merged under scripts/aggregate/agent_runs | [V] file list |
| T4 dossier spec + acceptance harness | 3 bilingual goldens, 29/29 harness tests; full black-box acceptance non-green by design (`not_exercised`) | [D] CX-R3-043 |
| T5 OPBENCH v2 (95-cell family) | Generator, schema, tests merged; real aggregate catalog and audit live OUTSIDE Git (SHA-256 recorded) | [V] docs/data/opbench; [D] CX-R3-044 |
| R3-2 golden/judge exercise | 40-item synthetic corpus, two label passes (pass 1 unblinded; pass 2 separately contextualized): exact 79.6%, within-one 96.7%, kappa 0.67, pairwise direction 19/20. This is NOT blind human reliability and NOT judge calibration: no judge/model call made; existing judge calibration output is aggregate-only so judge-vs-labeler kappa is NOT measured. Merged in PR #108 with a provenance label bug fixed in PR #109 | [D] CX-R3-065/066/067/068; [V] docs/data/opbench-lite/r3-2 |
| R3-3 source-derived Agent Core scenarios | 3 suites x 6 synthetic scenarios, schema and agent-binding validated against pin `c814c2b` (13/13); no live execution; Copilot suite `not_evaluable` | [D] CX-R3-068 |
| R3-4 linked-complaint E0 aggregate analysis | Preregistered and frozen; TDD red; no results yet | [D] CX-R3-069/070 |
| Codex environment limits | `gh`/git network blocked for Codex, local Podman stack inaccessible, hosted CI blocked by account billing/spend gate | [D] CX-R3-055/058 |

### 1.7 Test maturity

| Layer | Status |
|---|---|
| Rust workspaces (`seams`, `crates`, core-bridge), Python suites (scoring, aggregate, o11y, regression, dev-stack), Pester (demo-loop, o11y closure, demo-magic/platform) | Large offline suites; local full CI script `verify-local-ci.ps1` / `core-bridge/scripts/ci.ps1` |
| Hosted CI | Actions quota exhausted; hosted ci.yml does not run Python/console/bridge-contract/Terraform suites; local green is not hosted green ([V] OPEN_GAPS) |
| Live | Opt-in live tests (llm, agent-core stack, Langfuse); EV1 minimal suites disputas-min 20/20, consultas-min 11/11 pass on local stack (baselines, not regression proof) [D] |
| Real-wire parity vs a real `agent-core serve` | Not run (open gap) |
| Mock divergences (bridge/registry mocks) | Listed in `bridge-contract/conformance/known_different.py` |

### 1.8 Open PRs (gh not authenticated here, so [U])

Last known from plan 18-ter and bitacora: engine #108 and #109 now merged; engine #107 merged (forwarder files present). Possibly open: agent-core #53, support-platform #27 and #17, llm-gateway (#4 reported merged by plan, but Codex saw it open earlier; later state [U]). Codex R3-4 work is a local branch `codex/r3-4-e0-linked-aggregates`, no PR. Run `gh pr list -R pulso-factored/<repo>` with a valid token to confirm.

### 1.9 Infra: what exists

| Area | Content | Evidence |
|---|---|---|
| Environment described | ONE hackathon/prod environment, us-east-1, brand-new AWS account on the Free Plan, 3 EC2 hosts (core, platform, engine) with Docker Compose; CloudFront single public edge (`/pulso/*` -> engine, everything else -> platform); private Route 53 zone; SSM Session Manager only; one Secrets Manager secret + SSM params. Legacy `staging`/`prod` Fargate roots (engine_platform, bridge_services, flags default false) still in the tree, not the chosen path | [V] ADR 0007/0008, terraform/envs/hackathon, docs/architecture/deployment-status.md |
| Profile `free_plan` (default) | core `m7i-flex.large` runs core-runtime, exporter, migrate, llm-gateway, agent-core serve, tool-service AND Postgres 16 container; platform and engine `t3.small`; no NAT (public subnets, SG-restricted); no RDS, no WAF; CodeBuild small with host-builder fallback | [V] ADR 0008, costs.md |
| Terraform modules (28) | network, hackathon_network/iam/edge/data/compute, observability, storage, secrets, security, identity, workload(_iam), compute, database, rds_proxy, scheduled_task, core_*, data_lake, data_pipeline, ecr, image_builder, buildbox, ci_roles, deployer_policies, auxiliary_roles, engine_platform/task, bridge_services | [V] tree |
| Roots | `bootstrap` (state bucket `pulso-prod-tfstate-<account>` + ECR repos + OIDC/ECR), `envs/hackathon`, `envs/buildbox` (own state key), legacy `envs/staging`, `envs/prod` | [V] tree |
| Services in the design | Shared Core = agent-core `agentcore serve` :8001 + tool-service (flag `agent_services_enabled`); llm-gateway :8080 (private); core-runtime (engine core-bridge, not the shared Core); support-platform API/web/proxy; engine `pulso` :8080 + console; Postgres (container or RDS); S3 lake prefixes; secrets/keys generated by Terraform (gateway bearers, 4 Ed25519 keys, HMAC, origin-verify header) | [V] ADR 0009, docs/agent-services.md, docs/secrets-keys.md |
| ADRs | 0001-0009 (0003 Core workload, 0004 gateway, 0005 Core scale phase 0-1, 0006 data pipeline, 0007 single host, 0008 free plan, 0009 shared Core = serve) | [V] |
| CI/CD | Credential-free fmt/validate, Terraform tests with mock providers, Python contract tests, Pester; `release/validate_manifest.py` offline deploy-manifest check; OIDC plan/apply is a future manual-approved slice; no auto-deploy; `*.tftest.hcl` at env roots not yet in the workflow | [V] deployment-status.md |
| Tooling | `scripts/aws-prod.ps1` (check, bootstrap, images, plan, apply with typed `APPLY`, set-secret, seed-secret-keys merge-only reseed, status, upload), `scripts/buildbox.ps1`, `scripts/release-engine.ps1`, `scripts/aws_plan_review.py` | [V] |
| Cost estimate | prod profile about USD 120/month with WAF (112 without); free_plan removes NAT (~37), RDS (~15), WAF (~8) and adds ~11 for public IPv4 + ~3 volume; total free_plan not stated as a single number (my sum, [U]: roughly 60-75 USD/month before credits). Every number "an estimate until the first Cost Explorer week"; no budget alarm by decision | [V] docs/costs.md |
| Applied? | Docs on main repeatedly say "Nothing is applied" (README, ADR 0002/0007/0009, agent-services.md, OPEN_GAPS "Nothing applied to AWS"). The quickstart says "skip bootstrap if already applied: a plan shows no changes", which hints a bootstrap may have been applied on the human's account, but there is no evidence either way in the repo [U] | [V] docs |

## 2. What can be demoed now (exact steps, local only)

Preconditions common to all: Windows, Podman machine `pulso-dev` running, `uv`, Python 3.11+, built `pulso.exe` (cargo is NOT built by the scripts), `D:\.codex\factored\agent-core.env` and `llm-gateway.env` (values never printed). Free RAM about 3 GB; only one stack at a time. I did not run any of these; commands are from the repo docs [V].

| Demo | What it shows | Steps | Real vs not |
|---|---|---|---|
| A. Value loop (best demo) | real bank cells -> sensor -> Scout -> Verifier -> Builder -> real artifact compile -> regression proof (fails on base, passes on candidate) -> dossier ES -> announce | From an updated engine checkout (current main, not the stale local `main`): `powershell -File scripts/demo-loop/run.ps1 -Up` (about 80 s); then `-Cells -Loop -Show` (cells cached, loop about 3.5 min, ~USD 0.0025). For a guaranteed announced proposal: `-Cells -Loop -Show -Announce -Synthetic -BuilderModel xiaomi/mimo-v2.6-pro` (~70 s, labelled synthetic-planted). `-Down` to free memory. Spanish talk track: docs/dev/DEMO_LOOP.es.md | Real models, local agent-core registry, real aggregates. Real bank run announces Queja patches of `t/estado_pqr`; new-agent findings end `not_announced:infra_failed`; announce goes to a platform double unless `PULSO_PLATFORM_URL`/token set. Nothing is approved or published |
| B. Probes | scheduled agent battery and probe findings, candidate -> corroborated on second run | add `-Probes` (twice) | Synthetic scenarios on own battery core |
| C. Live internal console | DEMO-0 ten-step thread streamed into debug-console | `scripts/demo-magic.ps1` (builds `pulso`, serves console, runs `pulso demo`) | Offline Core double, simulated human, doubles[] printed first |
| D. Platform-event sensor | simulated platform stream -> Rust sensor -> proposal and ledger verdict in console | `scripts/demo-platform.ps1 -Scenario escalation_rise` | Sensor and pipeline real; data, scout/verifier, Core simulated |
| E. Observability | the same stories visible as traces, content and scores in Langfuse Cloud US | `scripts/o11y/langfuse_closure.ps1 -All` (needs `langfuse.env`, built engine under `D:\cargo-targets\claude-lfc\debug`, scratch agent-core branch; `-Mock` for a dry run against a local fake Langfuse) | Real Langfuse; synthetic input; a few cents of model cost |
| F. Eval baseline on a real agent | `disputas-min` 20 / `consultas-min` 11 pass on local stack | `python scripts/dev-stack/stack.py up --reset-db`, then `attach_eval_suite.py --suite <suite.yaml> --create` (see docs/dev/EVAL_SUITES.md) | Real engine, doubles for calibration/classifier |
| G. Scoring harness | recall/precision/ranking against OPBENCH v2 | `scripts/scoring/score_findings.py --catalog <v2 catalog> --signals <steps_cli cells output>` | Needs catalog and `steps_cli` outside Git; the DET1 rescore is still pending |
| H. Infra (nothing live) | design review: Terraform tests with mock providers, `aws_plan_review.py`, cost table, ADRs | `terraform test` in module/env dirs, `python -m unittest discover -s tests`, Pester `scripts/tests` (offline). Do NOT run plan/apply | Static only |

What cannot be demoed: outcome verdict after a real release (nothing is published), a new-agent announcement, flow/policy/tool-link proposals, anything on AWS, agent-core run export live into the sensor, the real support-platform SPA screen fed by the engine (platform double only).

## 3. Missing to run all of it in a production-like environment

| # | Gap | Owner | Type |
|---|---|---|---|
| 1 | Apply the infra: AWS account/profile, bootstrap state, ECR images with digests (agent-core pinned `c814c2b`, llm-gateway, support-api/web, pulso, caddy, tool-service), then plan/apply `envs/hackathon` in stages (Free Plan may refuse services at apply time). Needs user authorization per apply | user + infra | action |
| 2 | Terraform state key migration / existing-secret reseed: the existing Secrets Manager secret lacks the 13 Terraform-generated keys; Core starts with empty key files and fails closed until `aws-prod.ps1 seed-secret-keys` (merge-only) is run. A separate "state key migration" (bootstrap local state -> remote `bootstrap/terraform.tfstate`; buildbox has its own key) is documented in runbook-new-account.md; whether it is a pending blocker for this account is [U] | infra + user | blocker |
| 3 | Secret VALUES: provider keys (`GATEWAY__OPENROUTER_API_KEY` etc.), DB DSNs/runtime role, JEV key, Langfuse keys, platform tokens: set out of band by a human; never in Git/Terraform | user | blocker |
| 4 | Trust grant (ADR 0009): engine key in agent-core `staff-keys` can mint human/`aprobador`/step_up credentials and approve/publish; single secret readable by all three host roles; Terraform state holds seeds in clear. Needs owner sign-off, or per-host secrets, or an agent-core per-kid role ceiling | user + agent-core | decision |
| 5 | Admin credential (or agent-core change) so the `builder` can `put_draft` release settings; otherwise every new-agent proposal fails | user + agent-core | blocker for new agents |
| 6 | Engine <-> Core real wire: Rust client vs real `agent-core serve`; E0 finding -> ChangeSpec mapping; real-wire parity suite never run; tool definitions drift between engine fixtures and tool-service (every tool link refused until aligned) | engine + agent-core | engineering |
| 7 | Engine runtime on AWS: DB runtime secret binding, `pulso_runtime` role, controlled egress to model provider, private debug ingress (internal ALB + identity proxy), operational alarm contract | engine + infra + security | engineering |
| 8 | Platform side: announce route merged and deployed (support-platform #17/#27 [U]), contract 1.3.0 (32 missing event types), `release` in events, `cases.case_type` in exporter allow-list; platform payload shapes unconfirmed; exporter state-loss backfill gap | Product/platform | external |
| 9 | Detection: rescore after DET1 with the v2 catalog; wire `candidate_exploratory` into the Verifier; level-risk finding into reasoning; agent-run and platform-event sources live | engine (Claude/Codex) | engineering |
| 10 | Artifact kinds beyond prompt/template: flow, policy (tighten-only), tool link; reconcile BK0 matrix with code (template) | engine | engineering |
| 11 | Outcome loop live: a real release in the local stack end to end; calibrated estimator needs release/customer-cluster history | engine + Codex | engineering |
| 12 | Hosted CI: restore Actions budget and add Python/console/bridge-contract/Terraform suites to the workflows | repo owner | blocker |
| 13 | Calibrated judge: only 40 synthetic pairs, partial-blind; 30 human-labelled proposal pairs requested from the user; judge-vs-labeler kappa not measured | user | external |
| 14 | Review items from Codex R3-1 to address before any deploy: llm-gateway baggage/raw content capture, support-platform #17 DB recreation (no upgrade path) and narrow PII filter, infra secret reseed stale-write race | Claude lanes | engineering |
| 15 | Cost: budget alarm intentionally absent; free_plan total only as my [U] estimate | user | decision |

## 4. Evidence (paths)

Engine (read via `git show origin/main:<path>` in `D:\.codex\factored\improvement-engine`):
- docs/IMPLEMENTATION_STATUS.md, docs/gaps/OPEN_GAPS.md
- docs/dev/DEMO_LOOP.md, DEMO_LOOP.es.md, LOCAL_STACK.md, MAPPING.md, OUTCOME_STEP.md, EVAL_SUITES.md, MATURITY_ALIGNMENT.md, O11Y.md, LANGFUSE_CLOSURE.md
- docs/data/bank-cells-metrics.md, docs/data/opbench/{CROSSCHECK.md,discovery_v2.md}, docs/data/opbench-lite/r3-2, r3-3
- contracts/artifact-kinds/{README.md,matrix.json}
- scripts/demo-loop/run.ps1, scripts/demo-magic.ps1, scripts/demo-platform.ps1, scripts/dev-stack/stack.py, scripts/o11y/langfuse_closure.ps1, scripts/scoring/README.md
- seams/crates/{reasoning,registry-writer,eval,maturity,steps}

Infra (in `D:\.codex\factored\infra`, origin/main):
- docs/adr/0007, 0008, 0009; docs/architecture/deployment-status.md; docs/gaps/OPEN_GAPS.md; docs/costs.md; docs/agent-services.md; docs/hackathon-deploy.md; docs/aws-prod-quickstart.md; docs/aws-asks.md; docs/runbook-new-account.md; docs/journal/0021-shared-core-credentials.md
- terraform/envs/hackathon, terraform/modules/*, scripts/aws-prod.ps1, deploy/hackathon/*

Org docs (`D:\.codex\factored\docs`):
- TECH_SPEC_PULSO_AUTOMEJORA_V3.md (not re-read in full for this survey [U])
- reports-claude/PLAN_PROPOSER_AND_ATTACH_2026-10-04.md sections 18, 18-bis, 18-ter
- reports-claude/DETECTION_GAP_ANALYSIS_2026-10-05.md, ARTIFACT_KINDS_FEASIBILITY_2026-10-05.md, INFRA_PR37_REVIEW_2026-10-05.md, E2E_RIG_AND_RELAXATIONS_2026-10-05.md
- pulso_implementation_shared-_bitacora.md (CX-R3-043..070, CL-0076)

Caveats: `git fetch` for infra and engine succeeded; `gh pr list` returned nothing (unauthenticated or blocked), so open-PR lists are from documents. The local engine `main` checkout is 207 commits behind origin/main; use a fresh worktree from origin/main for any demo.
