# 6. Evaluation and sandbox

## 6.1 Evaluation is a set of distinct proofs

There is no single “passed” bit that establishes an improvement. The system must keep separate:

| Layer | Question answered | Does not establish |
|---|---|---|
| Source/contract validation | Are these bytes and fields admissible under this source contract? | Correct business meaning or complete source coverage |
| Artifact compilation/schema check | Is the candidate structurally valid for the pinned Core contract? | Runtime behavior |
| Unit/contract tests | Does a deterministic component meet its local contract? | Integration with actual dependencies |
| Core EvalSuite | Does this candidate satisfy its pinned task/oracle suite? | Customer/business lift or representativeness |
| Pulso comparative gate | Did candidate beat baseline on paired, relevant, held-out cases under declared thresholds? | Causal impact in production |
| Operational outcome measurement | Did a released version change linked operational outcomes? | Generalization outside measured population or causal effect without suitable design |

Every evaluation record must identify the candidate and baseline hashes, scenario set and split, random seeds, oracle/metric version, runtime/Core/model/tool versions, execution mode, environment and result receipts. If an oracle or required dependency is missing, record `not_evaluable` or `dependency_blocked`; never treat “not run” as a pass.

## 6.2 Scenario construction and leakage controls

V3 separates discovery from confirmation. Cases used to find an opportunity cannot silently become the only cases used to prove the candidate. For each candidate, freeze a scenario-set revision and split before comparing baseline and candidate. Holdout membership, source availability time and exclusion policy must be reproducible. Baseline and candidate should receive equivalent case content, seeds and simulator state; paired execution reduces noise.

Observed historical records can define scenarios only after minimization, provenance validation and treatment of sensitive data. Generated/augmented cases are tagged as generated and cannot estimate real-world prevalence. Adversarial cases probe failure boundaries but are not prevalence-weighted evidence. Evaluator prompts and scoring rubrics are versioned, blind where feasible, and must not share authority with the proposal generator in a way that lets the candidate optimize its own judge.

## 6.3 What has actually been exercised

The pinned snapshot documents several non-interchangeable pieces of evidence:

1. **Original/E0 snapshot and local-simulation paths:** the offline runner deterministically reads and projects both source populations without calling an external model provider or Agent Core.

   - **Independent E0 data audit:** 2,000 generated dispute cases were reviewed. A read-only Copilot lookup for transactions in the last 30 days (merchant, amount, city and date) appeared in 154/200 cases in one partition and 1,433/1,800 in its remainder. The data audit explicitly says it cannot derive a 1,539-case denominator from the audited source population.
   - **Later engine run record:** reports 1,433/1,539 in its selected holdout, marked descriptive-only. That is a separate run product with an unresolved denominator/provenance discrepancy; do not compare it as if it were the audit's 1,433/1,800 rate. The visible runner summary intentionally withholds replay-population counts. In both records, this is a lookup recurring across cases—not repeated queries within a case, agent success or customer outcome.
   - **Opt-in E0 `local-sim`:** deterministic detection passes supported evidence to a local candidate-exploration step (internally called Scout) and verifier simulation, then can persist a candidate-bound, non-executable investigation/proposal plan. The latest recorded sample used 200 cases in the initial Arranque input partition, found the lookup in 154/200, and returned an unlinked mapping result with the formal `do_nothing` route (make no change). It made no external provider or Agent Core call and established no cause, lift, release or business outcome.

   The original-bank branch remains a limited descriptive finding; its builder input is dependency-blocked. A proposal seed or investigation plan is not an Agent Core Proposal. See the separate [data audit](../../archive/source-record/2026-10-05/reports-claude/BANK_DATA_AUDIT_2026-10-04.md) and [runner record](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/local-e0-e2e-runner.md) for their different scopes.
2. **Bank-cell mapping and planted template proof are separate paths:** the bank-cell scan (internal record label MAP1) reported 19 corroborated aggregate findings and initially attempted only four. Two new-agent proposals were blocked at `put_draft` by the local registry role, one finding had no supported artifact mapping, and one was blocked by model availability. Later runs over the same 7,995 treated aggregate rows mapped complaint cells to the existing PQR-status response template (`t/estado_pqr` in Core) and recorded proven drafts for five channels. The regression proof requires the baseline to fail target cases and the candidate to pass; the deterministic wording judge is explicitly uncalibrated and model attempts varied. This supports a narrow bank-cell → mapped template → tested local Core draft path, not contact-to-complaint causality or impact. Separately, the planted mode used 350 invented monthly group summaries and a known petitions/complaints/claims (PQR) status difference; it tests response to an intentionally planted pattern, not independent discovery. Its fixture has eight target and three guard cases; the runbook reports the baseline failing eight target wording checks, seeded status rendering on the candidate, and 15/15 Core `GateItem` records (supplemental gate metadata, not a standalone quality or outcome score). The draft was not approved, published or promoted in that synthetic run, and platform notification used a test double. See chapter 2 for the full source/runtime distinctions.
3. **Platform sensor generator:** as described in chapter 4, planted sensor cases validate detector behavior on generated event histories. They do not validate a real platform feed or independent findings.
4. **Human-gated new-agent lifecycle (internal record label AGT1):** a distinct planted synthetic technical-support/phone scenario produced a new-agent draft and regression proof; a person evaluated, approved, published into the rig's local staging state and activated the agent in that rig's local test alias named `prod` (not AWS production). The run's only seeded platform case type was incorrect-charge, not technical support. It demonstrates draft/governance interactions, not correct routing, a real production deployment or a customer answer. The demo is also not proof that autonomous Pulso operated the human steps.
5. **Core smoke suites:** the pinned evaluation note reports 20 dispute-handling and 11 general-inquiry scenarios passing against a local Core setup using Jev, Agent Core's structured decision-model primitive. An additional classifier in that setup is a keyword-based double, and the proposals were started manually. This is a narrow Core smoke, not Pulso autonomous discovery.
6. **Optional proposal-rubric research note:** a separate synthetic exercise rated 40 proposals against 12 written criteria (480 ordinal ratings). Two labeling passes agreed exactly on 79.58% and within one rating point on 96.67%; the descriptive pooled kappa was 0.672. The first pass was not blind to proposal strata; the second was an independent model-agent context, not a human or different provider. This does **not** measure judge accuracy or demonstrate the Improvement Engine's detection/evaluation loop; actual row-level judge-versus-label agreement was not measured. It is included only as a calibration caveat, not a headline result.
7. **Enriched-history exact-link retrospective (internal test label R3-4):** repeated local executions were deterministic, but all eight aggregate result tables were suppressed under the k=10 and complementary disclosure policy. It produced zero publishable “why” statements. Suppression prevents reporting a cell; it does not show that a hypothesis is false.

The offline snapshot runner and demo loop are separate paths: the former makes no model/Core/network calls; the latter records a narrow local Core execution path and configured model path. The full joined engine-to-Core flow and the complete local container stack are not verified in the gap register. Treat the runbook records as pinned documentation evidence, not as a fresh run performed by this guide's author. The engine README and gap register are the authority for whether a run is still current.

## 6.4 Candidate gate and decision

The target gate is deterministic over versioned criteria: minimum support, evidence grade, privacy/disclosure policy, baseline-relative score, regressions, critical safety cases, resource/cost ceiling and required Core checks. Model-based grading can contribute a typed observation, but cannot override a deterministic hard gate. A proposal may be retained for revision even when it fails; only the specific candidate hash evaluated can proceed to approval.

Required failure tests include: missing source partitions; changed source digest; no-op candidate; regression on critical cases; evaluator unavailable; nondeterministic result beyond tolerance; low-support/suppressed cohorts; stale holdout; tenant/config mismatch; tool timeout; Core contract drift; cancellation mid-run; duplicate delivery; and uncertain publish response. Each should produce a typed state and a durable/replayable explanation.

## Source references

- V3 §§18, 23, 28, 31
- [Local original/E0 snapshot runner](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/local-e0-e2e-runner.md)
- [Demo loop record and limitations](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/DEMO_LOOP.md)
- [Bank-cell MAP1 mapping and proposal proofs](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/MAPPING.md)
- [AGT1 human-gated lifecycle and routing caveat](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/AGT1_NEW_AGENT_PATH.md)
- [Core evaluation notes](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/EVAL_SUITES.md)
- [R3-4 E0 linked analysis](https://github.com/pulso-factored/improvement-engine/tree/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/data/opbench-lite/r3-4)
- [R3-2 proposal-rubric cross-check and limits](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/data/opbench-lite/r3-2/README.md)
