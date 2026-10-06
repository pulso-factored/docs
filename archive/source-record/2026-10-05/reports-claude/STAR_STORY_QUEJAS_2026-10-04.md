# Star story "quejas" (complaints): findings, design, data (2026-10-04)

Read-only research. Aggregates only. No raw rows copied. Numbers come from existing aggregate outputs (D:\.codex\factored\output\*.json) and reports; none were recomputed from raw CSV.
Re-scope applied (binding): the star is case-type MATURITY detection -> proposed agent for "Cobro indebido" shown in the platform's Automatizacion screens (section 5), not only our console.

## 1. Extracted facts (citations)

### 1a. Complaint analyses and numbers (bank dataset, 2023-06..2026-06, snapshot 2026-06-18)
- Contacts 686,296; Queja 117,021 (17.1%): resolved 43.6%, unresolved 66,000 (56.4%), follow-up 63.0%, CSAT 2.43/4 (lowest), NPS -85; Transaccional unresolved 8.5% (20,385/240,056). Queja = 41% of all unresolved contacts (66,000 of 160,266). output/eda_contact_journey.json; output/eda_service_detail.json; data-lab reports/demand/FINDINGS.md H2 (scratchpad data-lab).
- Flat elsewhere: escalation 9.8-10.1% everywhere, wait ~2.0 min everywhere, resolution equal across countries +-0.3pp, recontact 7d ~2.9% everywhere; reason is the only differentiating dimension (FINDINGS L1). Queja unresolved is the same ~56% on every channel (Phone 43.6% resolved, App 44.1, Email 42.7).
- Spec first measured profile, window 2026-04-18..06-17: Phone/Queja 5,339 contacts, was_resolved=False ~56.3%; Phone/Transaccional 11,167, ~8.1%; wait ~119 s both, so no queja-specific wait thesis. TECH_SPEC_V3:489.
- Complaints (PQR) 67,095 (spec says 80,000 documented; -16%): categories 5 evenly (~13.4k each), SLA breached 13,495 (20.1%, flat 19.8-20.4% per category), 74.9% Open/In Process/Escalated at cutoff (50,269), median age of open ~545 d, 33,475 open older than 365 d; first_response_date known only 40,853 (60.9%), resolution_date 15,349 (22.9%); median response 38 h, median resolution 16 d (known only). Cargo no reconocido + Cobro indebido = 24,491 = 36.5% (the dispute core). output/eda_contact_journey.json; eda_aggregates.json; FINDINGS H3.
- Concentration: 54,145 customers with a PQR; top 10% customers hold 41.7% of PQR; repeat flag 10,086 (15%). output/eda_customer_link.json.
- Mora (days_past_due) cohort: contact rate 31.9% vs 31.4% other credit; PQR rate 3.59% vs 3.64%: no predictive signal. output/eda_mora_contact_predict.json. (Snapshot mora cannot be used as 2023 history, spec:106.)
- Marketing: conversions 0.55-0.57% per send, flat by country, consent True vs False 4,830 vs 4,969 conversions (no consent effect). output/eda_links_aggregates.json; economic_assumptions.md.
- Value scenarios: PQR capacity base case MX ~USD 11.9k/yr at 10% avoided, 45 min, 50% capture. Capacity equivalents, not cash; PQR avoided causally is an assumption. output/scenario_value.json.

### 1b. Relationships (spec 94-110, FINDINGS F6, C5)
- complaints.origin_interaction_id 100% null (67,095). Proximity link fails: 0.4% of PQR have a same-customer call within 24 h, 2.9% within 7 d = normal recontact rate. Calls and complaints were generated independently. Hence no contact->PQR causal chain, grade at most mechanism_proxy.
- surveys <-> interactions: exact join 212,759/212,759 (but only responders; CSAT scale truncated 1-4, NPS 2-7). transcripts <-> interactions: exact but only 171,321 (25%); 42 template texts, all say balance inquiry even under Queja; intent single value. Text gives no semantic prevalence (spec 108).
- E0 = 2,000 real disputes sampled from complaints (Jan 2025+), enriched with generated process data (SAMPLE.md): 200 boot + 1,800 replay; channels 56/18/15/10 phone/email/web/app; repeat customer 16%; SLA breach 22%; R4 amount policy forces human on 30% (median charge US$344 vs R4 cut ~US$250); 6% language-uncovered; Portuguese and hard cases are stress tests.

### 1c. What the spec EXPECTS (lo que se esperaba)
- Success case: engine detects undirected (no hardcoded "quejas"), builds EntityDraft[], proposal origin=auto_detect, evaluates with EvalSuite + Pulso gate, human approves bound to candidate_hash; claim A (undirected finding) + claim B (sandbox effect on affected capability), NOT causality on CSV resolution/SLA. TECH_SPEC_V3:46.
- Explicit warning: first run on original CSV "may choose another front"; fixture injects a generic non-resolution rise in a renameable category. Spec:737.
- Prohibited example: contact_unresolved on Queja + PQR SLA + a pqr_status_lookup tree = two facts, not a chain. Allowed as mechanism_proxy only. Spec:487.
- Metrics (spec 453): contact_unresolved@1 = COUNT(DISTINCT interaction_id) with was_resolved=False / contacts with known flag, by (contact_reason, channel) vs rest of same channel; pqr_sla@1 = sla_breached=True / known flag, by (category, subcategory, reception_channel) vs rest of same category/channel. Thresholds (spec 455): discovery [T-60d,T-30d), confirmation [T-30d,T); <=3 cells per family; flag coverage >=80%; n_known>=500 per cell and reference in both periods; bootstrap 2,000 by customer; lower bound of difference >0 at alpha=0.05/K Bonferroni; result corroborated_descriptive = no cause, no saving. E0 profile: >=20 distinct cases per pattern, coverage >=80%, candidate_descriptive.
- Link grades: same_outcome_linked | mechanism_proxy | unlinked | not_evaluable (spec 480-485). ValueModel gross = volume x eligible x effect x adoption x unit value (spec 491).
- Change types intended (spec 1412-1426, 29.5): recurring advisor query -> ToolDef + Flow + Agent tools_allowed; stable action sequence -> Flow/Agent; next-step suggestion -> DecisionModel/Policy/Template; uncovered reason -> Agent+Prompt+ModelProfile. Output is ImprovementPackage of EntityDraft[] + eval_suite.
- E0 rules: signal.parquet, labels, timeline-evaluator are NOT inputs; SIG-001/002 not hardcoded; "no_supported_signal" is a legal outcome (spec 1187, 1283). E0 reference signals (SAMPLE.md): SIG-001 repeated_query 154 cases/121 analysts/77% (proposes tool), SIG-002 sequence block-card then create-dispute 23 cases/88%, SIG-003 5 cases (<20, not proposed).
- Maturity/stage model: NOT in TECH_SPEC_V3 (grep madurez/etapa/borrador/Automatizacion/agente propuesto: no hits; Automatizacion only appears in the platform's removed roles). It is a product concept from the platform design boards; only analogues exist: E0 SIG-001 (repeated query, threshold 20 cases = MIN_SUPPORT in platform_sample.py:39), copilot suggestion outcome/edit_ratio fields in platform_history 0.5.1 `suggestion` entity.

### 1d. What E0 supports / not
- Supports (9 operational tables, aggregates): case (2,000; origin, topic, complaint_id, priority, sla_due_at), turn (24,049 generated text), identity_check (845), routing_step (2,000, tier human only), copilot_query (2,201, query_signature opaque), tool_call (2,577), approval (286: decisions true 27/false 5 in boot), case_close (resolved, resolution_code, csat), signal (evaluator reference, excluded). Rust sensor result on the 200 boot cases: recurring copilot query 154/200 (77%, cov 100%), holdout replicated 1,433/1,539 = 93.1% of reproduction cases, status replicated, descriptive only; technical_error_rate 0/187 (13 missing) = no signal (output/e0-run-pr58-.../result.json).
- Cannot support: suggestion table has 0 rows, so NO draft acceptance (tal cual / cambios menores / descartado), no component rows; no queue wait for chat (assumed); no other topics than disputes; frequencies are generator-encoded, not bank prevalence; Portuguese generated; final outcomes only in labels (evaluator-only).
- Platform head eeb73a8 / contract 1.2.0 (branch claude/w7-contracts) admitted events: case.opened|queued|assigned|first_responded|read|viewed|status_changed|closed|priority_changed|rated|assistant_started|assistant_released, assistant.session_started|input_queued|turn_answered|step_up_verified|step_up_rejected|ended, copilot.query_asked|answered. Missing: tool-use events for human advisors, draft sent/edited/discarded, case type (topic) and complaint_id (absent vs E0). Free text only in case.rated.comment and assistant.input_queued.answer (never read).

## 2. Maturity model for the Automatizacion screens (re-scoped story)

Case type = E0 `case.topic` (dataset mode) / future platform `topic` (absent at eeb73a8: gap, ask product). Seeded types on the boards: Cobro indebido, Cargo no reconocido, Problema con app, Calidad de servicio, Atencion en sucursal, Tarjeta virtual (first five = bank complaints.subcategory; E0 only covers the two dispute subcategories: topic fill 36%).

Engine measures per case type over a rolling window, all thresholds config (`MaturityConfig@1`, team-editable, versioned, defaults from the screens):

| Measure | Definition | E0 source | Platform 1.2.0 source |
|---|---|---|---|
| repeat_q | max over query_signature of COUNT(DISTINCT case_id) with that signature, per type, window N | copilot_query | copilot.query_asked (needs a signature in payload: ask) |
| tool_use_rate | cases with a proposed tool used by advisor / cases where it was applicable | tool_call (applicability = pattern cases) | no event (gap) |
| draft_accept_100 | last 100 drafts: sent as is, minor edit (edit_ratio <= 0.2 default), discarded | suggestion: 0 rows, UNSUPPORTED | none (suggestions denylisted): UNSUPPORTED |
| agent_resolved_of | agent-run closes resolved / handled, handed to humans | not in E0 | assistant.turn_answered, case.assistant_released, case.closed (partial) |
| stage 0..3, "Con agente" | 1 copilot answers; 2 tools proposed when repeat_q >= 20 cases (default); 3 draft replies proposed when tool_use_rate >= 0.70; agent proposed when draft_accept_100 >= 0.80 over 100 consecutive | stage 1->2 computable; 2->3 partial; 3->agent NOT computable | only copilot.* counts |

Honest consequence: on E0 the engine can reach "stage 1->2 crossed" (repeat_q = 154 of 200 >> 20) and can compute tool use partially; "El sistema propone un agente para Cobro indebido" (3->agent) cannot be derived from E0 or from platform 1.2.0 because draft outcomes are not recorded. Options: label the banner `simulated` with a seeded draft stream (platform-sim extension) or restrict the demo claim to "propone herramienta" (stage 2).

## 3. Read model / API for the platform front

`GET /internal/v1/automation/case-types` (read-only, scope evolution:read):
`{as_of, data_origin, doubles[], case_types:[{type_id, label, stage:0|1|2|3|"agent", measure_text_key, measure:{numerator,denominator,window}, cases_today, banner:{proposal_id|null}, thresholds:{stage1_to_2:{metric,min},stage2_to_3,stage3_to_agent}}]}`;
`GET .../case-types/{id}` drawer: `{history:[{stage,since}], drafts_last_100:{as_is,minor,discarded,coverage}, thresholds, proposal:{engine_proposal_id, core_proposal_id, candidate_hash, state, link_grade, approval_url}}`;
`PUT .../config` team thresholds (writes MaturityConfig revision). Text is composed by the front from enums and counts (no free text, "84 de cada 100" = numerator/denominator). Every payload carries data_origin and doubles[].

Renderer options:
- A: hand over a feature branch/patch vs eeb73a8 (Automatizacion list + drawer + banner using its design system, backend proxy to our API). 25-40 h incl. restoring the removed role, tests; needs product team consent (screens "not built anywhere"; ENGINEERING_BRIEF line 58, slice-4 line 23) and a contract for case type.
- B: standalone replica served by pulso (debug-console style, same visual) 8-14 h, fully ours, labelled replica.
Recommend B for the demo (hours, no cross-team dependency), shipping the API shape of A so the patch is later mechanical; offer A as a PR proposal after the demo.

## 4. From stage to agent-core proposal
Engine finding (stage crossed + WorkflowBridge) -> ChangeSpec -> our compiler -> Core draft (only `prompt replace` + `eval_suite`, matrix.json) -> Core validate (dry run, real) -> evaluate -> Platform Agent Builder (S16, `POST /builder/proposals/track`) -> human approval with TOTP step-up -> publish to staging alias. Real: validate, publish staging, alias read (L1). Simulated: approval issuer, release/observation events (EXT-2), draft stream, the stage-3 data. Not possible with today's compiler: new tools/flows/agents (denied/blocked), so "agent proposed" is a change DESCRIPTION plus a prompt replace on the nearest real artifact (p/resumen_radicado of `disputas`, or p/copiloto of `copiloto-asesor`) and marks the rest `not_evaluable`.

## 5. Story, metrics, proposal, evaluation (one page)

Problem (plain words): quejas are 17% of contacts but 41% of the unresolved ones; 3 in 4 formal complaints are still open, 1 in 5 broke its SLA; advisors answer the same lookup (recent charges) for most disputes. Honest limit: bank data cannot link complaint to call, indicators are flat except by reason, E0 shows mechanics only.

Sensor signals (exact definitions):
1. Dataset, bank: contact_unresolved@1 on (Queja, channel) = 66,000/117,021 = 56.4% vs rest 16.6%; display only cells with n_known >= 500 and k >= 10; corroboration per spec 455 (descriptive, no cause).
2. Dataset, bank: pqr_sla@1 = 13,495/67,095 = 20.1%; flat per category => the sensor should report NOT a differential (honest "no cell stands out"), plus open_aging = open at cutoff / created = 74.9%.
3. Dataset, E0: e0_recurring_copilot_query_cases = distinct cases with the leading query_signature / cases in window = 154/200 (min support 20), holdout 1,433/1,539.
4. Platform-shaped (rust-events sensor, branch w6-integ/w7-wire, not in w6-demo): per (language/channel) cell: reassignment_rate (cases with >=2 case.assigned / opened), recurrence_rate (previous_case_id set / opened), first_response_delay, resolution_delay (case.closed - case.opened, mean ratio >= 1.25), one-sided z vs rest, Bonferroni, discovery 60% / holdout 40% by event sequence, min_cell_cases 30, min_support 5, k_anon 10, alpha 0.05, min effect 0.05, history gate 14 d and 200 cases. NOTE: payload (close_reason) is never read, so close_reason-based metrics are impossible; the monitor on w6-demo only counts events (stand-in).

Problem/opportunity statement: "Advisors repeat the same recent-charges lookup in 77% of dispute cases (replicated 93% in later cases); a copilot that gathers charges, PQR history and handoff in one answer for dispute requests could remove the repeats; effect is mechanism_proxy (no same-outcome oracle)."

Proposed change: prompt replace p/copiloto@1.0.0 -> 1.1.0 (for dispute/PQR requests, read movements and PQR and handoff first, answer with all three sources in one reply, never invent) + new eval_suite `copiloto-quejas-suite@1.0.0` (agent copiloto-asesor, repetitions 3, scripted scenarios: dispute with candidate charge, cross-customer request must abstain, tool failure, PT locale; assertions: tool events for movements and PQR both appear; thresholds noise_margin/floor per metric). Alternative customer-facing: p/resumen_radicado. No sensitive text drafted here.
Evaluation: Core native eval of candidate vs base on those scripted scenarios (synthetic sandbox data only; dataset scenarios disabled in Core). Viable = suite valid + native verdict pass + Pulso gate (paired candidate vs base, same seeds, improvement of coverage-of-context metric >= min effect with CI lower bound > 0, guardrails unchanged: safety/cross-customer abstentions 100%). Caveat: platform agents use `understand` (Jev, PR #28 not merged): evaluation `not_exercised(jev)` or recorded; real evaluate only on attention-task world (L1). Claim limit: sandbox effect, no bank savings.

Numbers the console shows: 56.4% vs 16.6%, n 117,021; PQR 20.1% SLA, 74.9% open; E0 154/200, holdout 93.1%; stage banner "repeat_q 154 >= 20"; thresholds; link_grade mechanism_proxy; doubles[] list; data_origin.

## 6. Five-act script (doubles[] vocabulary)
1. Detect (real-narrow: Rust sensor on E0 and bank aggregates; platform-sim stream `simulated`): signals with n/denominator/coverage.
2. Investigate (scout/opportunity scripted `stand-in`, or `agent_roleplay` on treated data; verifier real-narrow recompute): bridge grade mechanism_proxy.
3. Build (compiler `claude-standin` -> Core draft validate real): prompt replace + eval_suite.
4. Evaluate + approve (L1 Core native on attention-task real; platform agents `not_exercised(jev)`/recorded; gate GSIpy `stand-in`; approval issuer `simulated`, optionally platform Builder TOTP at L4).
5. Publish + observe (staging publish real; platform alias read real; observation `simulated`) and the Automatizacion screen (replica B, `simulated` draft stream) updating stage.

## 7. New platform-sim scenario mirroring quejas
`resolution_delay_rise` (target cell es/app_chat, not pt/web_chat, to avoid clash): from onset (30%) mean case.opened -> case.closed time x3 in the target cell, constant arrival rate (volume drift would turn it into drift_only), present in discovery and holdout; optional coupled `recurrence` 6%->20% (off by default). Manifest `planted`: effect resolution_delay_rise, cell, onset_sequence, metric "mean (case.closed - case.opened) per cell", baseline_s, elevated_s, multiplier 3, present_in both, plus `mirror_of`: {dataset_metric: contact_unresolved, cell: Queja, bank_rate: 0.564, rest: 0.166} and `stand_in_note`: platform has no topic/complaint_id column. Sensor must admit resolution_delay.es.app_chat and none on null.
Second source in dataset mode (aggregate, treated, k>=10): gold_analytics.contact_reasons_monthly (month x country x channel x reason: contacts, resolved, escalated, followup) from the data-pipeline, suppress cells with contacts < 10, and the E0 recurring-query signal (E0 via dataset-pg).

## 8. Data and execution
- Bank CSV: D:\.codex\factored\data\<table>\year=YYYY\month=MM\*.csv (13 tables, ~1,097 daily files each), customers.csv, products.csv etc. at top. Restricted: laptop only, aggregates only. Existing aggregate outputs: D:\.codex\factored\output\*.json (safe to ship as fixtures).
- E0: D:\.codex\factored\pulso_muestra_e0\datos\*.parquet (9 operational: case, identity_check, turn, routing_step, copilot_query, tool_call, approval, case_close, signal(excluded); labels and timeline are evaluator-only, never mounted), contratos\platform_history.json 0.5.1 and evaluation.json 0.2.0. Needs pyarrow/Rust parquet reader (pyarrow not installed on this laptop). E0 never to hosted models.
- Platform-sim: `python -m product_stream --sqlite out/product.sqlite --backfill 20000 --seed 7 --scenario <name>` (stdlib only), SQLite + manifest.
- Laptop: sensor on E0/bank/sim, compiler, Core real image (L1), console/replica B, demo-magic. AWS: Postgres + ECS engine (R1 design), Core with real model keys, gateway; not needed for the demo (L6).

## 9. Open questions for the user
1. Banner honesty: show "agent proposed" on a seeded draft stream (simulated) or stop the claim at "tool proposed" (stage 2, the only computable one)?
2. Choose A (patch to support-platform, product-team consent) or B (replica) for the Automatizacion screens?
3. Platform needs `topic`/case type, copilot query signature and draft outcome events: request from product team?
4. Target artifact: p/copiloto (advisor) or p/resumen_radicado (customer) given compiler limits and Jev block?
5. Can the user confirm the stage thresholds (20 cases, 70%, 80% of 100) as defaults and who edits them?
6. Is a Rust per-cell sensor (w6-integ/w7-wire) to be merged into the demo branch?
