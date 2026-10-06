# Magic round 1A: what the spec offers that makes support operations visibly better

Date 2026-10-04. Read-only research. Sources read: TECH_SPEC V3 (sections 1-29, 31.4/31.6/31.7, 32, plus the 30.8 unit catalogue), PLAN_HACIA_SISTEMA_REAL v5, PLAN_PROPOSER_AND_ATTACH v2. Status checked against improvement-engine main `2a9682de` (== origin/main) by reading crates `seams/crates/{steps,reasoning,eval,core-client,control-api,maturity,memory,authority}` and `crates/core`. Not read line by line: 30.1-30.7, 31.1-31.3, 31.5, 31.8-31.12 (integration plumbing, no product magic).
Legend. Magic H/M/L. Status: IMPL (on main), PART, NONE, DEF (deferred by decision or blocked upstream). Effort S (<1 day agent), M (1-3), L (>3). Codex = could Codex do it without Claude's lane (offline, pure, behind a frozen contract).

## 1. Capability table

### Detection

| # | Spec | Capability | Magic (why) | Status on main | Integration (agent-core / SPA) | Eff | Codex |
|---|---|---|---|---|---|---|---|
| D1 | 14, 18 | Declarative MetricSpec sensors over many families (contact, PQR/SLA, transactions, digital, products, marketing, survey, platform); each cell vs the rest of its channel | H: finds recurring problems nobody asked about | PART: `cells` sensor (M1-M6 bank aggregator) and `rust-events` sensor; Codex flow/platform sensors merged (#95) but offline | Signal feeds Scout; SPA shows it as an insight card on Supervision | S per family | Yes (DFAM1-3) |
| D2 | 14, F2 | Rigor that makes findings credible: discovery/confirmation windows, BH or Bonferroni over ALL explored cells, bootstrap by customer, named discards, `refuted` is kept | M: "we also tested 140 cells and discarded 126" is a persuasive line | IMPL (cells: pooled z, BH, holdout replication, discards; bootstrap not) | Rendered in dossier "method" block | S | Yes |
| D3 | 16, 18 | Association vs cause: `link_grade` (same_outcome_linked / mechanism_proxy / unlinked / not_evaluable) validated by code, never by the LLM | H: prevents the false claim, builds trust with ops leads | PART: `mapping.rs` (finding -> allowed artifact row, else `unlinked`); Codex `workflow_bridge.rs` unwired | Grade is shown on the card; gates the "will reduce X" wording | S (collapse to 2 grades) | Yes |
| D4 | 3, 14 | Cross-source join of contacts, PQR, surveys, digital with exact vs `temporal_candidate` confidence | H: "complaints are 17% of contacts but 41% of unresolved" | PART: bank aggregator has M1-M6; `complaints.origin_interaction_id` is empty so no exact join | Where-signal from bank, mechanism from E0/platform | M | Yes (Python aggregator) |
| D5 | 32.3, 31.6 | Segment/cohort cells: language x channel starvation, reassignment, recontact chains, first-response delay, queue wait, load imbalance | H: tangible ("ES queue waits 4x PT") | PART: events sensor covers reassignment, recurrence, delays per language/channel | Platform event_log; insight card in SPA | S | Yes |
| D6 | 24, 31.6 | Detection from agent-core runs: escalations by flow/node, `agent_step.failed`, tool errors, handoff by layer, cost known/unknown | H when real traffic exists: system sees its own failure modes | NONE (exporter and LayerMapping spec'd; platform has no tool-use or draft events) | Needs exporter role on Core DB or outbound events; SPA unchanged | L | Partly (mapping, fixtures) |
| D7 | 26 of F2, 29.6.8 | Learned detectors `candidate -> shadow -> active`, self-evolution of the engine's own agents (U31) | L for the goal | NONE | none | L | Yes, but skip |

### Proposals

| # | Spec | Capability | Magic | Status | Integration | Eff | Codex |
|---|---|---|---|---|---|---|---|
| P1 | 31.4.4, 29.5 | Artifact kinds: prompt replace, template, policy, flow (add/replace), decision_model (no recalibration), eval_suite, agent field replace; tool/model_profile/release_settings denied | H: real edits to real artifacts | PART: prompt replace + new specialist agent by closure copy of donor `consultas` (anchored patch, byte exact); flow/template/policy only offline (Codex); live BKFL/BKTL not started | Registry proposal `origin=auto_detect`, builder principal, never approve; SPA lists it once tracked | M-L per kind | Offline compilers yes (BKF/BKT/BKD) |
| P2 | plan 16b | NEW AGENT as proposal (user priority 1): full closure born at staging, human adds interrupt + injection ruleset before prod | H: biggest "wow" | PART: closure-copy compile exists; live write/eval of an agent not shown | Proposal API with 26-entity closure; admin promote | M | No (needs live Core) |
| P3 | 31.4.3, 29.5 | Link existing tools: `tools_allowed` + a flow node; new tool = `dependency_blocked(tool_without_executor)` | M-H: "advisors repeat the same query -> tool" | NONE live (new tools paused by decision) | tool-service catalog; flow change | M | Partly |
| P4 | 31.4.3-5, BKC | Multi-change bundle with cascade (`expected_derived` = `auto_bumped`), <=50 changes, base precondition digest | M: needed the moment a flow changes (agent bump) | NONE live (compile stand-in is 2 ops) | Dry-run of the bridge | M | Offline yes (BKA, BKC) |
| P5 | 16 | Alternatives incl. `do_nothing`, falsifiable predictions, expected direction checked against the finding | M-H: honest "not worth changing" is part of the story | IMPL (`do_nothing`, expected-direction deny in reasoning) | Card shows alternatives | S | n/a |
| P6 | 16 | ValueModel: burden x eligible fraction x effect x adoption (-> USD), marginal value across portfolio | M-H if kept simple (a range of cases/month); the 7-factor USD form is fragile | PART: Codex `value_model.rs`, unwired | "Expected effect" line on the card; no USD | S (lite) | Yes (DSCEN2) |

### Pre-release evaluation

| # | Spec | Capability | Magic | Status | Integration | Eff | Codex |
|---|---|---|---|---|---|---|---|
| E1 | 31.7, F4 | Base vs candidate arms through Core `evaluate` on an `eval_suite`; six outcomes (pass, fail with 409 body, failed_infra, quota, changed, timeout) captured | H: evidence before approval | PART: `eval` + `core-client` real-narrow; suite handwritten; gate is a structural stand-in (`quality_claims: forbidden`) | Core owns state; SPA shows verdict | M | No |
| E2 | 18, 31.4.11 | Engine-generated eval cases from the signal's evidence cells: ES/PT, oracle (`Expect`, `actions_verified`), dev/validation/final_locked split, sealed before candidate | H: "it also wrote the tests" | NONE live; Codex `scenario_factory.rs` offline | `eval_suite` draft rides in the same PUT; legible to builders so no final cases | M-L | Partly (factory offline) |
| E3 | 31.7.2 | CombinedGate: Core pass + Pulso improvement gate; four `platform_*` guardrails at 0; `approve_with_loosening` listing 9 yardstick-change types | M-H: tells the approver "pass is not improvement" | PART (structural stand-in, author-is-not-judge) | Decision card option | S-M | Yes |
| E4 | 28.4 | Frozen/prequential replay of history through versions | M for E0 claims, L for ops people | PART (Codex offline) | none | L | Yes |
| E5 | 18, 29.6 | Shadow/canary of candidates | n/a: spec itself says unsupported upstream; only detector shadow is internal | DEF (blocked) | needs platform exposure API | - | - |
| E6 | 31.4.11 | `Agent.metrics` / MetricDef gates (ADR 0020) so a proposal carries its own metric thresholds | M | NONE | Core native gate | M | Partly |

### Human surface, loop, learning

| # | Spec | Capability | Magic | Status | Integration | Eff | Codex |
|---|---|---|---|---|---|---|---|
| H1 | 20.1, 31.7.2 | Decision card / dossier: problem, population, support and counter-evidence, alternatives, diff, base-vs-candidate, both gates, `candidate_hash`, step-up approve/publish/promote | H: the moment the human believes it | PART: authority stand-in, debug-console panels, rationale-in-`docs` plan | Engine endpoint (`/api/v1/evolution`-like) + `docs.rationale` (<=4000 chars) on the proposal; SPA screen is the Product team's | S-M | No (owns live format) |
| H2 | 20, 24.1 | Expert feedback (support/challenge/knowledge) re-verifies, never edits the finding | L-M | NONE | SPA button | M | Yes |
| L1 | 21, F6 | Memory: free wiki, publish by diff + CAS, revocation, restore | M. Spec version is overbuilt | PART: thin notes (confirm/contradict, evidence refs, PII scan), in-memory, not durable | 2nd run reads/contradicts a note | S (thin), L (spec) | Yes |
| L2 | 31.6.4, F5 | Outcome loop: `release.published/promoted/revoked` -> ReleaseCorrelation (`rel-`+hash[:16]), `exposed` only after a run uses the release, before/after window excluding runs that cross the promotion, revoke reopens | H: "did it work" | PART: control-api P2R correlation + one successor run; observation window simulated | Pull from `/v1/export` or registry events with exporter role | M | No |
| L3 | plan 10 (user designs, not in spec) | Case-type maturity: copilot answers -> repeated question -> tool -> drafts accepted -> agent proposed | H: the reference UX | PART: `maturity` crate + console replica; stage 1->2 from E0, rest simulated | Needs draft-disposition and tool-use events from the platform | M | Pure model yes |
| T1 | F1, plan 5 | Triggers: explicit, scheduled, coalesced ingest batch, outcome (release events) | M | PART: explicit and scheduled, pull poller (TR1), successor on release | Poll Core export with overlap, dedupe by `event_id` | S | No |

## 2. Top 12 by magic / effort

1. **H1 decision dossier** with plain-language "what we saw, what we change, what we tested, what we expect" (S-M, H). All the facts already exist; it is assembly.
2. **D1+D2+D5 breadth on the cells/events sensors**: more families and segment cells with the honest discard list already built (S, H).
3. **P1+P2 live Builder-in-Core proposal**, prompt patch and new specialist agent, written as an `auto_detect` proposal with evidence in `docs.rationale` (M, H). Closure-copy compile is already on main.
4. **E2 engine-written eval cases** from the evidence cells (ES/PT, oracle) shipped as the `eval_suite` in the same draft (M-L, H). Without it no proposal is approvable.
5. **P6 ValueModel-lite + P5**: "affects about N cases/month, direction down, `do_nothing` considered" with no USD (S, M-H). Ready code in `value_model.rs`.
6. **L2 outcome loop**: release event -> before/after on the same cell -> verdict card -> memory note (M, H).
7. **L1 thin memory wired into run 2**: "last time we rejected X, skipped" (S, M-H).
8. **D4+D3 cross-source finding with link grade**: bank says WHERE, E0/platform says WHY, the grade says how far the claim goes (M, H).
9. **P3 existing-tool link** ("same query repeated -> link the tool"), reusing L3 maturity stage 2 (M, M-H).
10. **L3 maturity -> "propose an agent" trigger** from real platform events once draft dispositions exist (M, H).
11. **E3 combined gate + `approve_with_loosening` in the card** (S-M, M-H).
12. **D6 detection from agent-core run events** (L, H, but gated by exporter role and live traffic, so last).

Next tier: P1 flow/template/policy live (L each), P4 bundles, E1 replacing the structural stand-in with Core's verdict.

## 3. What is overengineered for the goal (cut or shrink)

- Ten-table schema, job leases, SKIP LOCKED, quotas windows, RFC8785 hashing of everything, N/N-1 upcasters (sections 5, 8, 15, 19): robustness, invisible to a support lead.
- Documentation machinery, ADR/journal gates, 46-unit DAG, 229-WP plan (26, 30): the process weighs more than the product.
- Wiki memory with diff publish, CAS, revocation, restore drills (21): thin notes give the visible effect.
- Four link grades and 7-factor USD ValueModel (16): use linked/unlinked plus a case-count range.
- Detector self-evolution and shadow detectors (U31), 13 signal families as a goal: five good families beat thirteen thin ones.
- Stateful bank sandbox, KBA identity oracle, adversarial client agents (U26, U36, 18): large, and Core's native eval is customer-principal scripted only.
- SQL sandbox with cumulative-disclosure budgets, AWS S3 mailbox sessions, step-up continuity states (19, 20.2): needed for real bank data, not for the demo.
- Prequential replay protocol (28.4): research-grade, not operational.
- Human-visible honesty vocabulary with eight statuses and eight honesty tests (plan 1.1): keep `real/simulated/blocked` and print `doubles[]`.

## 4. Caveats

- E0 is a generated sample; "discovery" there is relative to the generator. Say so on the card.
- Core native `pass` has noise margin 0.05 and no base yardstick on first proposal; it does not prove improvement. The card must not claim it.
- Proposals appear in the SPA only after the platform tracks them (builder lists only its own DB index).
- Magic items D6, L2, L3 depend on events the platform does not emit yet (case type, draft disposition, tool use).
