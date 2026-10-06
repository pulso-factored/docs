# Codex brief, round 3: independent follow-ups (start when round 2 is done, or in parallel if a lane is idle)

Author: Claude (orchestrator). Date: 2026-10-05. Channel: the shared journal (UTC + `CODEX`). Same ground rules as round 2 (`CODEX_BRIEF_ROUND2_2026-10-04.md` section 2): real data only for statistics, aggregates only with k>=10, authored artifacts synthetic, no secrets, pre-registration first for anything statistical, local validation is authoritative, one heavy process at a time, new directories need X-DOC (or your lane) OWNERS globs added in YOUR OWN PR (Claude cannot merge right now: do not wait for any Claude merge; stack on your own branches).

Where we are (so you can judge value): the loop DETECT -> PROPOSE -> EVALUATE BEFORE TANGIBLE -> HUMAN DECISION -> RELEASE -> OBSERVE exists in pieces. Claude has: cells sensor with level_risk findings, reasoning roles (mimo flash / mimo pro / glm judge), registry writer, regression-suite generator that must FAIL on base and PASS on candidate (proven live on a template and a prompt), agent battery (amount probes + attacker pack, live: base 34/37), a gateway judge (live agreement 0.909 exact against a synthetic golden set), decision dossier (in progress), Langfuse observability (in progress), and PRs in agent-core, support-platform, llm-gateway and infra. Real defects already found in the demo agents: `consultas` radicado slot accepts any text; es->pt switch not honoured; recepcion routes a card-number lure to the fraud interrupt; policy 500 vs 250 USD.

Priority order R3-1 > R3-2 > R3-3 > R3-4 > R3-5. Each is independent.

## R3-1. Independent adversarial review of Claude's open PRs (X-REV lane)

Why: an independent second pair of eyes finds what authors miss (our own reviews found request-line smuggling, margin differencing and 3 infra blockers). Value: merge confidence for the user, who will merge when back.
What: review, read-only on GitHub with the connector or `gh` if your token works: improvement-engine PR 102 (https://github.com/pulso-factored/improvement-engine/pull/102), infra PR 37 (https://github.com/pulso-factored/infra/pull/37), support-platform PR 17 (https://github.com/pulso-factored/support-platform/pull/17), llm-gateway PR 4 (https://github.com/pulso-factored/llm-gateway/pull/4), and later the agent-core PRs we open. Classify BLOCKER vs NON-BLOCKER strictly (security, correctness vs the spec `docs/TECH_SPEC_PULSO_AUTOMEJORA_V3.md`, privacy, honesty of labels, tests that really test). Do not push to our branches: write findings to the journal and `docs/reviews/codex/**` (your path).
DoD: one review note per PR in `docs/reviews/codex/`, each finding with file:line and a failing-test sketch; the journal entry summarizes blockers; re-review after Claude fixes.

## R3-2. Independent golden set for the proposal judge (calibration without human labels)

Why: our LLM judge (z-ai/glm-5.3-flash) agrees 0.909 exact with a golden set derived from the rubric anchors by us, which says only that it is consistent with our own reading. An independent labelling by a different party, blind to the judge's outputs, is the closest thing to calibration until the user labels pairs.
What: read `docs/reports-claude/ARTIFACT_ANATOMY_AND_RUBRIC_2026-10-04.md` (rubric R1-R12, 0/1/2, hard gates, adequate >=19 with no zero) and `scripts/scoring/` (score_proposal.py, judge_calibration.py, golden/synthetic_golden_12.json) on main/PR 102. Author 40 SYNTHETIC proposals (patch/template/new-agent; Spanish and Portuguese; against real artifact ids from `scripts/reasoning/fixtures/base_artifacts.json`) spanning clearly good, borderline and clearly bad (violating protected clauses, wrong language policy, PII tokens, claims beyond evidence, etc.), and score each criterion 0/1/2 BLIND (do not run our judge first). Pair them (good vs bad for the same finding) for pairwise tests. Deliver as JSON in our golden format (`golden/…json`) under your path (e.g. `docs/data/golden/**`), plus a README on your labelling protocol and an agreement script that takes the judge outputs file and reports exact / within-1 / hard-gate agreement and Cohen's kappa.
DoD: 40 labelled proposals + 20 pairs; two independent labellers or one labeller twice with a gap (report intra-rater agreement); the script runs on our existing judge output example; no real data.

## R3-3. Real-cell scenario pack (pseudo-replay) in agent-core scenario format

Why: agent-core only evaluates scripted scenarios. Scenarios built from the real recurring problems we detect (Queja/Phone unresolved, Tecnico/Phone uncovered topic, E0 recurrent transactions lookup) make evaluation reflect real operations instead of generic cases.
What: from the audited cells (`docs/reports-claude/BANK_DATA_AUDIT_2026-10-04.md`, your OPBENCH catalog) build 5-8 scenarios per problem, 3 repetitions defined, with templated utterances (no copied text, no PII; digit runs <6, no emails), fake slots, seeded tool replies, confirm/auth steps, and deterministic expectations (outcome/escalated/actions_verified). IMPORTANT lessons from our verification of T2 (journal CL-0068, `docs/reports-claude/VERIFY_CODEX_R2_2026-10-05.md`): seed tools, add confirm/auth steps, amounts as digits, no turns after the run closes. Provenance by cell hash (never a row id). Use our `scripts/dev-stack/attach_eval_suite.py` (PR 102) pattern to run them live on a local stack if you have one; otherwise offline schema validation with the pinned agent-core pydantic model (install rfc8785 in a venv, not globally).
DoD: scenario pack validated by the pinned schema; a protocol for how many repetitions detect a 30-point fix; each scenario tagged with the cell and the behaviour it targets; README.

## R3-4. Cross-source evidence: E0 + bank "why" for the top findings

Why: the bank says WHERE problems are (Queja, phone); E0 can say WHY (advisor copilot behaviour). Spec idea (Wave 3) with real value for proposals.
What: with the one safe link (`complaint_id`, 2000 of 2000) produce pre-registered aggregate tables: for E0 cases linked to complaints by category, copilot query patterns, repeats and handling outcomes; k>=10, aggregates only, no ids/free text. Provide an evidence-grade vocabulary (`link_grade`: linked/indirect/none) and findings with status vocabulary; state clearly what cannot be concluded (no causality).
DoD: pre-registration committed first; deterministic regeneration; tables + README + tests; 3-5 candidate "why" statements each with numbers and limits.

## R3-5. Adversarial corpus v2 (multi-turn, es/pt) for the attacker pack

Why: our fixed attacker pack has 21 scripted scenarios; a larger, independently authored corpus finds more defects (real ones found so far: radicado slot accepts any text, es->pt not honoured, card-number lure to fraud interrupt).
What: multi-turn attack scripts (injection, PII elicitation, fraud pretext, third-party impersonation, language switching, emotional pressure, amount-boundary probing, instruction hierarchy attacks, tool-argument injection) in Spanish and Portuguese, for disputas, consultas, recepcion and copiloto-asesor, in agent-core scenario format with deterministic expectations; mark which defects they would reveal in the current demo agents. Independent of our pack (do not copy it).
DoD: >=60 scripted scenarios, validated by the pinned schema, a coverage matrix (attack family x agent x language), README.

## Delivery and reporting
Journal entry at start and after each task (exact regeneration command, counts, data used by name only, what was NOT done). If a task is impossible or not valuable, say so with evidence and move on. Nothing here asks you to wait for Claude.
