# Task for Codex: OPBENCH-lite, an independent benchmark of real findings on the bank dataset and E0

Version 2 (reduced scope, 8-12 agent-hours). Written by Claude (orchestrator) for the user to hand to Codex. Date: 2026-10-04.
Reply channel: the shared journal `docs/pulso_implementation_shared-_bitacora.md` (UTC timestamp + team name `CODEX`). Nothing here asks Codex to depend on, edit or wait for anything of Claude's.
Status: nice-to-have, independent, REAL data and REAL computation. No mocks, no stubs, no models, no agent-core, no network, no AWS.

## 1. Why

Our engine must find real recurring problems and improvement opportunities in the real data. We are adding a dataset-mode sensor (a Python aggregator + a Rust statistical sensor over treated cell tables).
We need an INDEPENDENT second implementation on the same raw data so that (a) two implementations disagreeing exposes a bug in one of them, (b) we have reviewed, real numbers for the demo, (c) we can score our engine: recall (does it find the real findings), precision (does it avoid reporting non-findings), ranking.

## 2. Scope (Codex lane only; in Codex-owned paths: `crates/**`, `docs/data/**`, scripts of your lanes, one new pack directory such as `docs/data/opbench/**`; add the glob to OWNERS per your rules)

Inputs (local only, never copied to the repo):
- Bank dataset: `D:\.codex\factored\data\<table>\year=YYYY\month=MM\...`. FOCUS ONLY on `call_center_interactions`, `complaints`, `satisfaction_surveys` (small tables). Do NOT process `transactions` or `digital_events` in this task.
- E0: `D:\.codex\factored\pulso_muestra_e0\datos` (operational tables only; evaluator tables `labels`/`timeline` are never used).
- Reuse what you already have: the original-source contact/complaints projections (`docs/data/original-contact-projection.md`), `crates/source-adapters`, the runner CLI, DPL2 provenance/exclusion rules. Spec reference: `docs/TECH_SPEC_PULSO_AUTOMEJORA_V3.md` F2 (families atención/contactos and PQR/SLA only for this task).
Hard constraints: deterministic code only; aggregates only; every emitted count is >= 10 or suppressed; no identifiers, no free text, no row-level output; raw/intermediate row data never committed; no secrets.

## 3. Deliverables

### D1. Pre-registration `discovery_v1` (committed BEFORE any result file in the branch history)
Fix, before looking at results: the metric list below with exact definitions, the replication design, the statistical method (state it: two-proportion test with a stated multiplicity correction over ALL explored cells, minimum support, minimum effect size), the k rule (k = 10), the status vocabulary (`candidate`, `candidate_descriptive`, `corroborated`, `corroborated_descriptive`, `uncertain`, `refuted`).
Replication design: if the interaction/complaint timestamps cannot be compared safely over time (your docs say the supplied timestamps are naive, without timezone), do NOT force a temporal split: use cross-sectional replication (a deterministic split by hashed customer key into discovery and replication halves, and/or by branch or channel) and say so. If dates are reliable at month granularity, you may add a temporal replication on top. State the limits.

### D2. Metrics (compute for every cell of reason_category x channel, per the closed normalized vocabulary you already use; plus overall)
- M1 `contact_unresolved_rate`: unresolved / contacts with a known resolution flag, by reason and channel.
- M2 `complaint_share_of_contacts`: complaint-type contacts / all contacts, by channel.
- M3 `complaint_unresolved_share_of_unresolved`: share of all unresolved contacts that are complaints (the earlier read-only analysis suggests ~41%: recompute).
- M4 `pqr_open_rate`: open PQR / all PQR, by category (earlier ~74.9%: recompute).
- M5 `pqr_sla_breach_rate`: breached / PQR with an SLA, by category (earlier ~20.1% and FLAT across categories: report it as `refuted/no differential` if so).
- M6 `survey_low_score_rate`: low satisfaction / surveys, by channel and reason where linkable (state linkability and coverage).
- E1 (E0): `copilot_repeat_rate`: cases where the same leading query signature repeats / cases (earlier 154 of 200, replicated ~93%: recompute from the E0 operational tables, aggregates only).
Register ALL cells explored, including the ones that fail. One command regenerates everything.

### D3. Catalog `opbench-lite.json` (+ JSON Schema)
6 to 8 entries: the positive findings among M1-M6/E1 plus AT LEAST 3 explicit non-findings (refuted/uncertain, e.g. SLA flat). Per entry: `id`, `family`, `title`, `population`, `metric_id` (from D2), `cell` (map of normalized dimensions), `numerator`, `denominator`, `effect` (size + interval vs baseline), `replicated` (bool + figures under the chosen design), `cells_explored`, `multiple_testing` (method + adjusted q), `k_min_ok`, `status`, `type` (`problem` | `inefficiency` | `risk` | `descriptive_only`), `mechanism_class` (hypothesis class only, never causal), `improvement_tags` (agent-core artifact kinds that could address it: `prompt`, `template`, `policy`, `flow`, `decision_model`, `agent`, `tool_link`; NOT new tools), `adequate_proposal_notes` (2-3 lines: what a good proposal must change and what would be a bad one), `caveats`.
Spec acceptance to prove with tests: the same code finds or refutes the anomaly when the evidence is permuted without renaming the `Queja` category; the coarse category is never turned into a cause.

### D4. Cross-check protocol `CROSSCHECK.md` + `scoring.json` example
Matching key (`metric_id` + normalized `cell` + direction), tolerances on effect size, how recall, precision and ranking agreement are scored, and what counts as an acceptable disagreement. Publish your normalized dimension vocabulary (reason_category, channel) so we can adopt exactly the same one. Do not run our code.

### D5 (optional, only if quick, under 2 hours). E0 operational validation blocker
`turn.evidence_ids -> identity_check.check_id` is a relation the supplied contract does not declare, so E0 validation fails closed. Add an explicit, versioned overlay (declared assumption + evidence that the relation holds) WITHOUT editing the external contract, so E0 loads completely.

### D6. Journal entry
UTC + `CODEX`: what was delivered, the exact regeneration command, counts (findings, non-findings, cells explored), data used (names only), what was NOT done.

## 4. Acceptance criteria
1. The pre-registration is committed before the first results file in the history of the branch.
2. `scripts/verify-local-ci.ps1` passes with `CARGO_BUILD_JOBS=1`.
3. Two runs give byte-identical output (sorted keys, stable ordering).
4. Every count in the pack is >= 10 or suppressed; a test scans for violations and for identifier-like or free-text fields.
5. At least 3 non-findings are present; every entry states `cells_explored` and the multiplicity method.
6. The permutation test (spec F2) exists and passes.
7. No dependency on Claude's `seams/**`; none of Claude's files edited; no network; no model calls.

## 5. Delivery
One new consolidated PR from a new branch; do not wait for any merge of ours; update the journal at start (plan), after the pre-registration commit, and at the end.

## 6. What we do with it
We run our aggregator + Rust cells sensor over the same data and score it against `opbench-lite.json` with your protocol; we show the real numbers in the dataset-mode demo; we use `improvement_tags` and `adequate_proposal_notes` as part of the rubric that judges our proposals. Nothing in this task commits Codex to our integration work.
