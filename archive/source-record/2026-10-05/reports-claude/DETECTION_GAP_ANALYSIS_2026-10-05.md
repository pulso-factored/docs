# Detection gap analysis (2026-10-05)

Read-only research. Evidence: TECH_SPEC V3 (F2 families, section 32.3), BANK_DATA_AUDIT_2026-10-04, MAGIC_ROUND1A/D, `cells.rs`, `bank_cells.py`, Codex OPBENCH v2 (discovery_v2.md, CROSSCHECK.md) and journal CX-R3-032/033. Aggregates only. I did NOT run `score_findings.py`: the v2 catalog and the 3,657-row snapshot are outside Git and `steps_cli.exe` is not built in this worktree. The counterfactual below uses the older cached aggregator output (`tmp/l1-cells/bank_cells.ndjson`, 4,510 rows, same code path); treat numbers as diagnostic, to be confirmed by a rescore.

## 1. Headline

The sensor is not too strict; it is **blind by construction in the aggregator**, and that explains all 12 misses and probably the single reported non-finding. The bank only supports one real structure (contact reason, M1), so "detecting more" means detecting that one structure in more cells, plus opening sources that carry a mechanism (E0, agent runs, platform events), not adding bank metrics.

## 2. Why recall is 0.4545: the 12 misses reconstructed

Codex's 12 misses are all M1 (unresolved rate), reason x non-phone channel, plus Queja x web:

| Missed cell (direction up) | Codex effect | Cause |
|---|---|---|
| complaint x web | 0.389 | A |
| technical x email / mobile_app / whatsapp / web_chat / web | 0.070 / 0.084 / 0.086 / 0.078 / 0.101 | A (bias), B, C |
| commercial x whatsapp / web_chat | 0.108 / 0.131 | B (n), A |
| retention x email / mobile_app / whatsapp / web_chat | 0.142 / 0.195 / 0.195 / 0.233 | A (cells deleted) |

Causes, in order of weight:

- **A. k-suppression at the monthly grain deletes mass and biases the baseline (aggregator, `bank_cells.py`).** Cells carry a `period` (month) and `k_ok` requires numerator, complement and denominator each 0 or >= 10 per (metric, dims, half, month). Non-phone channels are 15% of contacts split over 5 channels x 35 months x 2 halves, so low-rate cells (Transaccional, Producto: numerator < 10) and all of Retencion and Web vanish, while high-rate cells survive. The sensor then sums the survivors. Evidence from the cache: App total 17.7k of about 26k real contacts (-30%); Retencion has a single non-phone cell (Email, n = 22); Web has 416 contacts, 0 Queja/Retencion/Comercial cells (Codex sees 588 Queja on web). Baselines are inflated (App rest-of-channel 26.4% vs 22.2% true) and effects attenuated: Tecnico App +3.6 pp (Codex +8.4), Tecnico Email +2.4, WebChat -1.6, WhatsApp -1.5, all under the 5 pp floor. Phone is unaffected (+7.9 pp, matched). So it is not the same-channel baseline or the 5 pp floor per se; those only bite because A shrinks the effect.
- **B. `min_support` = 500 is applied to the discovery HALF (`c.den < cfg.min_support`, cells.rs ~l.499).** The audit specifies n >= 500 over the full period. Commercial x WhatsApp/Web Chat have about 800 total contacts, about 400 in discovery, so they are discarded as `below_min_support` even if A were fixed. Technical x Web (about 500 real contacts) is an honest `insufficient_support` either way.
- **C. Definition difference, minor.** Codex compares to "all other reasons in the same channel", identical to ours (`stratum()` drops only `reason_category`). Not a cause once A is fixed.

Other scoring items:
- **1 reported non-finding (M6 technical x mobile_app, +0.076):** survey low-score is a function of `was_resolved` (audit F04). Our `depends_on M1` flag fires only if M1 has a finding on the same cell; because of A it has none, so the M6 cell is reported as an independent positive. Expected to disappear with A fixed (hypothesis).
- **2 unmatched M10:** handle-time share is a re-expression of M1, absent from the v2 catalog. It is already flagged `depends_on M1`; the penalty is a scoring-convention gap (dependent signals count as positives).
- **6 ignored descriptive:** M7/M8/M9-type cells (digital error, consent level, declines) that the catalog treats as context. Convention, not a sensor gap.
- Of the 22 positives, 10 matched (consistent with phone cells for all reasons plus Queja in 5 of 6 channels); Codex did not publish which, so this split is inferred.

Projected effect of fixing A+B: M1 recall about 0.85-0.95 (Technical x Web remains unreachable), precision rises (M6 cell and M10 become `depends_on`). To be confirmed by Codex rescore.

## 3. What we do not read today, and what it could give

| Source | Signals possible | Why not captured | Artifact it can lead to | Verdict |
|---|---|---|---|---|
| E0 copilot (copilot_query, tool_call, approval, routing_step, case_close) | F14 repeated lookup (79.4%), tool timeout 0.47%, abono over-limit rejection 25% (low power), routing abstained 3.5%, CSAT mean 2.15 | Not in bank aggregator; separate Codex E0 sensor. Stance conflict: our audit says prompt/flow change (`p/copiloto`), Codex v2 labels it `covered_existing_capability` | prompt, flow, existing-tool link | Highest mechanism value; decide stance |
| Digital events (15.6M) | Error concentration on transactional actions (6.0% vs 4.5%) | M7 exists, descriptive: no error-to-contact link (2.66% vs 3.01%), `Error` not a validated taxonomy | at most a `soporte-app` agent | Keep descriptive |
| Transactions | Declines flat (5.0%) | Non-finding, kept as negative control (M9) | none | Do not chase |
| Marketing consent | 50% sends to non-consenting | M8 level_risk exists; no agent target | policy outside platform | Keep as risk card |
| Call transcripts | none | 100% es, one intent, topics = reason | none | Do not chase |
| Free text (PQR `description`, survey comments, transcript text) | Possible sub-reasons inside Queja/Tecnico (the WHY the audit says is missing) | Never read (PII, not asked); unknown whether generator text varies | routing card, prompt, new agent | Cheap probe, see item 5 |
| Surveys | CSAT mediated by resolution | Dependent on M1 | none | Dependent control |
| Agent run events (TEL1) | tool error runs, retries, terminal outcome, handoff by agent/locale | `AG_*` aggregator exists (synthetic only); needs contract 1.4 export and live traffic; k=10 whole-vector suppression | prompt, flow, tool link on our own agents | High value, gated |
| Platform events (57 types, 1.2/1.3) | copilot.suggestion_* (draft acceptance), escalation motives, handoffs, language x channel starvation | suggestion_* quarantined; events sensor (R1G) works offline on `event_log`, no live feed | maturity stage, prompt, routing | High value, gated |
| Proposal decisions (FDBK1) | Which finding types humans reject; meta-precision | In progress; no read contract for lifecycle history | detector calibration, not agent-core | Medium, later |
| Sondas | not assessed (no data seen) | - | - | Defer |

## 4. Detection types we lack

| Type | Gap | Why not captured | Take | Value / effort / FP risk |
|---|---|---|---|---|
| Full-period cells, all channels | Items A/B above | aggregator + support rule | aggregator emits `period=ALL` cells with k at full period (keep monthly rows only where k holds for R2/month counts), pool support on discovery+holdout | High / S / low (k preserved, same BH family) |
| Reason-only cells (channel pooled) | none registered | M1 only reason x channel | add reason-only M1 cell (sensor already supports it: dims.len()==1) | M / S / low; gives the agent-level "uncovered reason" claim with max power |
| Prioritisation by excess volume | ranks by p, not by contacts affected | engine ranking | rank by n x diff (value model, not new test) | M / S / none |
| Cross-metric (M1 x M6, M1 x M10) | all dependent | design | already `depends_on`; fix scoring convention | none / S |
| Cohorts (country, segment, agent hash) | flat in the audit (agent chi2/df 0.97) | nothing to find | keep as negative-control cells | none; k + customer-hash only |
| Trend / drift / onset | stationary (trend p > 0.4), calendar clocks uncertain | no signal in bank | needed on live platform data (outcome loop, L2) | build only with live data |
| Seasonality / hour / weekday | uniform hours, flat months | no signal | - | do not chase |
| Sequence / journey / recontact | recontact 2.88% = random; PQR link 100% null | data | events sensor on platform `previous_case_id` | live only |
| Continuous distributions (AHT, response hours) | only Welch-type test in events sensor; bank handle time is reason-driven | method + low independence | Welch z on duration by reason | L-M / M / medium (derived of M1) |
| Tool-usage concentration | TEL1 | no data | AG_* aggregates | high when live |

## 5. Ranking (value / effort)

1. **Full-period aggregation + pooled support (A, B).** S. Recovers about 10 of 12 misses, all in channels where proposals matter (chat/email agents). Lane: Claude (`bank_cells.py`, `cells.rs`). Codex: independent rescore.
2. **Dependency and scoring hygiene** (M6/M10 `depends_on` even without a parent finding on the cell; agree a convention that dependent and context signals are not positives; reason-only M1 cells; excess-volume ranking). S. Codex: update scorer.
3. **Resolve the E0 copilot-repeat stance and add its mapping row** (prompt + flow, existing tools; evaluated with scripted scenarios). S. Only mechanism-level proposal we have. Codex: align catalog `actionability` or document disagreement.
4. **More E0 families** (tool timeouts, over-limit rejections, routing abstention, approval latency). M, candidate_descriptive only (low n, generator-encoded). Codex can do all of it independently (E0 exporter exists).
5. **Free-text feasibility probe** (distinct templates / sub-reasons in PQR description and survey comments, aggregate counts only, no text out). S to probe, L to productise (PII scrub, k). Only route to a WHY; may be null if text is templated.
6. **Wire events sensor to platform `event_log`** (language x channel starvation, reassignment, recurrence). S-M; gated on live feed; H when live. Codex: fixtures.
7. **TEL1 `AG_*` run aggregates into a separate sensor namespace** (tool error, retry, handoff by agent/locale). M; gated on export contract 1.4 and traffic; targets our own agents' prompt/flow/tool link.
8. **Platform events 1.3 (suggestion acceptance, escalation motives)** feeding L3 maturity. M-L; blocked upstream.
9. **FDBK1 meta-detector** (reject rate by finding kind, to retune thresholds). M; no read contract yet.
10. **Continuous metrics (AHT, PQR response by priority).** M; derived of M1, no agent artifact for PQR back-office.

## 6. Roadmap

1. **This week: fix the blind spots (items 1-2).** Aggregator full-period cells + pooled-n support, keep k at full period, rerun, Codex rescores; expect recall >= 0.85. Add reason-only cells and the dependency convention. Success criterion: misses reduced to the honest Technical x Web `insufficient_support`.
2. **Next: mechanism where WHERE is known (items 3-5).** Settle the E0 stance and mapping row; Codex extends the E0 catalog (v3) with timeouts/rejections/abstention; run the free-text probe to see if a WHY exists inside Queja.
3. **Then, as feeds land (items 6-9).** Events sensor and TEL1 on live platform/agent-core traffic, FDBK1 for calibration. No new bank metrics before these.

## 7. Do not chase

- **Transaction declines, SLA breach, recontact, agent outliers, wait/escalation, hour/weekday/seasonality, country/segment effects:** flat or random in 37 months; they are negative controls and must stay refuted. Any "finding" there is a false positive.
- **PQR open backlog:** independent of age (artifact). Report only with `artifact_suspect`.
- **CSAT/handle time as independent problems:** mediated by M1; never a separate burden.
- **Transcripts, intents, language:** 100% es, single intent.
- **Marketing campaign heterogeneity (F09), consent (F08) as agent proposals:** no agent-core artifact; keep as risk or context cards.
- **Digital error by app version:** about 600 versions, noise.
- **Lowering the 5 pp floor or alpha to inflate recall:** the misses are an aggregation defect; loosening thresholds would add false positives on the flat controls.
- **Learned detectors (D7):** low value for the goal.

## 8. Constraints

k >= 10 on every emitted count stays; moving suppression to the full period is safe because published counts are still >= 10 and complementary suppression is kept. Customer-hash halves and BH over all explored cells stay unchanged. Free-text work needs PII scrub and aggregate-only output. Everything stays descriptive (`claim: association`, ceiling `corroborated_descriptive`).
