# Codex brief, round 2: independent work that adds value to the integration and the "magic" flow

Author: Claude (orchestrator), for the user to hand to Codex. Date: 2026-10-04.
Reply channel: the shared journal `docs/pulso_implementation_shared-_bitacora.md` (UTC timestamp + team name `CODEX`). Detail goes to `BITACORA_PULSO.md` and your own docs.
This replaces and expands `CODEX_TASKS_V2_VALUE_2026-10-04.md` (same five tasks, more detail, explicit Definitions of Done).

## 1. Context: what we are building and where it stands

Pulso is an autonomous detection and self-improvement engine. The product is the support platform (`support-platform`), with agent-core integrated into it (agents `copiloto-asesor`, `recepcion`, `disputas`, `consultas`, `constructor-chat`, plus a registry that holds prompts, flows, tools, policies, eval suites). Our engine runs underneath and does six things:

1. DETECT recurring problems in real data (deterministic sensor, statistics with multiplicity control and replication).
2. REASON with three agents called from our service: Scout (what is going on), Verifier (independent: does the evidence hold), Builder (what to change).
3. PROPOSE: send the proposed change to agent-core as a draft proposal (`origin=auto_detect`) against REAL artifacts: priority order is (1) new agents, (2) prompt changes, (3) links to existing tools, (4) new tools (paused: tool-service cannot create tools), (5) policies, (6) trees/flows, (7) rules/classifiers.
4. agent-core does ALL management: evaluation, showing in the SPA, human approval, release. The engine never approves, publishes or promotes. We build no platform screens (only "asks").
5. After a release the engine OBSERVES whether the problem moved and says so honestly.
6. Everything is labelled honestly (real, real-narrow, local-model, recorded, stand-in, simulated, not_exercised, blocked); no causal claims, only associations.

Status on `main` (merged): sensor over bank tables with statistics and replication (`seams/crates/steps/src/cells.rs`, `scripts/aggregate/bank_cells.py`), reasoning roles and a real llm-gateway client (`seams/crates/reasoning`, `engine/src/models/llm_gateway.rs`), a local real stack (`docs/dev/LOCAL_STACK.md`: Postgres, llm-gateway, agent-core, agent `pulso-builder`), scoring harness (`scripts/scoring/`), a pull trigger poller (`scripts/triggers/`), and your OPBENCH-lite (`docs/data/opbench/`). In flight on our side: registry writer (delivers proposals to agent-core), trigger endpoint, and the wiring plus the first live end-to-end pass.

Models used by our agents (you only need them if a task says so; keys are set by the user, never in the repo): generation `xiaomi/mimo-v2.6-flash`; Verifier and reasoning-heavy validators `xiaomi/mimo-v2.6-pro`; judges/reviewers that must be a different family `z-ai/glm-5.3-flash`.

First real result of our sensor against YOUR catalog: recall 1.0 (3/3), non-findings reported 0/5, ranking agreement 1.0, precision 0.18. The low precision is only because the catalog has 3 positive cells while the data supports more. The audit that supports that is `docs/reports-claude/BANK_DATA_AUDIT_2026-10-04.md` (read it: it also lists what the data cannot support).

## 2. Ground rules (all tasks)

- Independence: no dependency on Claude's `seams/**`, no edits to Claude's files, nothing waits for a Claude merge. If you need something from us, write it in the journal as an ask and continue with a clearly labelled stand-in.
- Data: REAL data only where a task uses data (bank dataset under `D:\.codex\factored\data\<table>\year=YYYY\month=MM\...`; E0 under `D:\.codex\factored\pulso_muestra_e0\datos`, operational tables only, never `labels`/`timeline`). Aggregates only, every emitted count k>=10 or suppressed, binary measures published as (valid, pos) and masked when either is 1-9, no margins that allow differencing (we found and fixed that leak in our own aggregator), no identifiers, no free text, nothing row-level committed, no secrets. Authored artifacts (T2, T4) are SYNTHETIC.
- Statistics: pre-register before looking at results (committed before any results file), state the multiplicity method over ALL explored cells, register failed cells too, include non-findings, status vocabulary `candidate`, `candidate_descriptive`, `corroborated`, `corroborated_descriptive`, `uncertain`, `refuted`. Associations only, never causes.
- Determinism: one command regenerates everything; two runs are byte-identical (sorted keys, stable ordering).
- Policy fact: since 2026-10-04 (H1) the assistant serves Portuguese; only handoffs go to people. Do not write content claiming Portuguese always escalates.
- Validation: if you touch Rust, `scripts/verify-local-ci.ps1` passes with `CARGO_BUILD_JOBS=1`. The machine is RAM-constrained: one heavy process at a time. GitHub Actions has no quota, so local validation is authoritative.
- Delivery: small PRs from new branches, one consolidated PR is fine if you prefer; add OWNERS globs for new directories (your lanes); never touch `D:\Nexus`; docs in English; journal entry at start (plan), after each task (exact regeneration command, counts, data used by name only, what was NOT done).
- Priority order: T1, T2, T3, T4, T5. If you can only do one, do T1.

## T1. Outcome estimator validated by placebo (closes "did it work?")

Why: after a release changes an agent, the engine must say whether the problem rate moved, honestly. Today we have nothing that tells "improved" from noise. This is the piece that makes the demo's last beat credible.

What: a deterministic estimator and its validation on the REAL bank cell tables (37 months, `call_center_interactions`, `complaints`, `satisfaction_surveys`).
- Design: pre/post on a treated cell (e.g. reason x channel) against same-period control cells (same channel, other reasons; second control by customer-hash half). Difference-in-differences on proportions with an interval, a minimum support, a minimum observation-window rule, and a pre-registered decision vocabulary: `improved`, `no_detectable_change`, `worsened`, `inconclusive` (including `inconclusive: underpowered`). Never "caused".
- Input/Output: a pure function over cell tables. Read `scripts/aggregate/bank_cells.py` on `main` and adopt its ndjson cell-table schema EXACTLY (so our engine can call it unchanged). Output a small JSON verdict per treated cell with effect, interval, n pre/post, controls used, power note and vocabulary status.
- Validation without a real release: (a) placebo: random fake release dates over the 37 months; the estimator must report no change at the pre-registered false-positive rate (state the bound, e.g. <=5%); (b) power: inject known absolute reductions (2, 5, 10 pp) into the post period of the real aggregates; report detection rate and the minimum detectable effect per cell size. Publish which cells are too small to ever detect an effect (earlier audit: only Phone cells reach n>=500 per 30 days) and make the estimator return `inconclusive: underpowered` for them instead of claiming success.
Definition of Done:
1. Pre-registration (`discovery`-style document) committed before results.
2. Estimator + README + tests; byte-identical reruns; a k>=10 scan test; a test that adopts the exact `bank_cells.ndjson` schema.
3. Placebo report with the measured false-positive rate below the stated bound.
4. Power table by cell size and the list of underpowered cells.
5. Journal entry with the regeneration command and counts.

## T2. Evaluation case bank for the real agent-core agents

Why: agent-core evaluates a proposal against an `eval_suite`, and today no agent has one, so our proposals cannot be meaningfully evaluated by agent-core (our rubric scores that criterion 1 of 2). A real suite turns agent-core's own evaluation step into something that can accept or reject a change.

What: read the agent-core repo (`github.com/pulso-factored/agent-core`: `agent-core-assets/**` on main, the registry and eval suite schema/docs) and our `docs/reports-claude/ARTIFACT_KINDS_AND_EVALS_PLAN_2026-10-04.md` and `ARTIFACT_ANATOMY_AND_RUBRIC_2026-10-04.md`. Author eval suites in agent-core's own format for `disputas`, `consultas` and `recepcion` (and `copiloto-asesor` if the format allows): 20-30 SYNTHETIC cases each, Spanish and Portuguese, covering happy paths (cargo no reconocido, cobro indebido, estado de PQR, routing), protected behaviours (fraud interrupt, injection ruleset, amount-based escalation policy, no promise of refunds, no PII echo) and negative cases. Expected results must be checkable without a model where possible (routing, closed-vocabulary slots, tool-call presence) and by rubric where not. Validate each suite with agent-core's own validator/CLI offline (clone, `uv`, no network).
Place them in OUR repo as drafts the engine can attach to proposals (a path like `agent-core-assets/eval-suites/<agent>/`), plus a README mapping each case to the behaviour it protects.
Definition of Done:
1. Every suite passes agent-core's schema validation (show the command and its output summary).
2. A test proves each protected behaviour is covered by at least 2 cases per language where applicable.
3. No real data, no PII; digit runs of 6 or more and emails are avoided in case text (agent-core's PII wrapper would tokenise them).
4. README with the case-to-behaviour map; journal entry.

## T3. Agent-behaviour signal source: agent-core runs to cell tables

Why: bank tables show customer-level problems. agent-core's own run exports show where the AGENTS fall short. A second source of real problems makes the engine find inefficiencies in the agents themselves, not only in the customer data.

What: a deterministic aggregator (Python, stdlib) that turns an agent-core run export (`/v1/export/runs`, `/runs/{id}/events`; use recorded fixtures such as `scripts/triggers/fixtures/export_recorded.json` on `main`, the agent-core export docs, and, if the user provides one, an export from the local stack) into the SAME ndjson cell-table schema our sensor consumes: agent x locale x topic x outcome metrics. Define 4-6 metrics with exact definitions (candidates: handoff rate by locale, fallback-template rate, closed-early rate, tool-error rate, low-confidence rate, steps per run) and state honestly which are computable from the export and which are not. k>=10 with the (valid, pos) masking rule, no free text, no ids.
Definition of Done:
1. Output schema-compatible with `bank_cells.ndjson` (a test loads both with one reader).
2. Determinism test and k scan test.
3. README with the metric definitions, their limits and what the fixture does and does not prove (label recorded vs real).
4. Journal entry.

## T4. Proposal dossier spec and black-box acceptance harness

Why: step 3-4 of the experience is a supervisor opening a proposal in the platform. If the proposal reads badly, the magic is lost, however good the statistics. Separately, an independent party (you) verifying our path end to end by HTTP is the strongest check we can get.

What (a): study what agent-core stores for a proposal (origin `auto_detect`, rationale, changes, changelog, evaluation results) and what the support-platform SPA actually renders (`support-platform`, `frontend/`, read-only). Write `docs/data/dossier/DOSSIER_SPEC.md`: which fields the engine must fill so a supervisor understands the proposal in 30 seconds (the problem, the evidence numbers with the baseline, expected effect and HOW it will be measured, risks, what stays unchanged), with 3 golden example dossiers (a prompt patch, a link to an existing tool, a new specialist agent) in Spanish with Portuguese variants, using only the audited aggregates (e.g. Queja 56.4% unresolved vs a 16.6% same-channel baseline). List what the SPA cannot display (those become asks for the platform team, not work for us).
What (b): a black-box acceptance script `scripts/acceptance/` (Python stdlib, HTTP only) that, against a running local stack (`docs/dev/LOCAL_STACK.md`), checks: a proposal exists in the registry with origin `auto_detect`, a valid draft with non-empty changes, the engine never approved, published or promoted anything, rationale fields satisfy DOSSIER_SPEC, no PII tokens in the draft, the 24h proposal quota is respected. It fails clearly when the stack is down.
Definition of Done:
1. DOSSIER_SPEC with 3 golden dossiers and the "SPA cannot display" list.
2. The acceptance script with tests on recorded responses, a README, and no import of our code.
3. Journal entry.

## T5. Extend OPBENCH-lite to every audited finding

Why: makes our precision number credible and finds more real opportunity families.

What: add (with a committed `discovery_v2.md` pre-registration before results): Queja unresolved on every channel (not only Phone); Comercial, Tecnico and Retencion unresolved on Phone; Comercial on Email and App; the digital-events error concentration on transactional actions (descriptive only, no link to contacts); marketing sends to non-consenting customers (a RISK, not a service problem); the E0-to-bank join on `complaint_id` (the only link, 2000 of 2000); agent outliers if real. Correct OPB-04: the earlier 93.1% is not reproducible (the audit gets 79.4% cross-case and 1,433/1,800 in the holdout) and the existing `leer_movimientos` tool already covers that query: mark it `covered`. Keep at least 5 non-findings, `cells_explored` and the multiplicity method on every entry. If quick, also D5 from round 1 (E0 operational validation overlay).
Definition of Done:
1. `opbench-lite` v2 catalog + schema + tests, pre-registration committed first.
2. `python scripts/scoring/score_findings.py --catalog <your v2 catalog> --signals <cells json>` runs (see `scripts/scoring/README.md`); report our sensor's new recall and precision if you can produce signals with `python scripts/aggregate/bank_cells.py` and the `steps_cli cells` binary on `main`; otherwise validate the schema only and say so.
3. Journal entry with counts (findings, non-findings, cells explored).

## What we expect back and what we do with it

- T1 becomes the outcome step of the engine (we call it unchanged). T2 gets attached to proposals so agent-core's evaluation has teeth. T3 feeds our sensor. T4 tells us what to fill in proposals and independently checks the path. T5 is our scoring reference.
- If a task turns out to be impossible or not valuable, say so in the journal with the evidence and move on; do not pad.
