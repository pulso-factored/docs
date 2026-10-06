# 3. What the data can—and cannot—tell us

The engine must not treat every row as equally trustworthy evidence. Alongside the organizer-provided synthetic bank tables, the project received a second **generated interaction-history sample**, called “E0” in engineering notes. It adds detail around possible customer journeys but is not a production event log. A third source family is generated service-platform activity used to test platform monitoring. Keeping these origins separate is essential: one describes the supplied banking snapshot, one enriches it synthetically, and one simulates how an AI service behaves.

| Evidence family | Plain-language meaning | What it can support | What it cannot prove |
|---|---|---|---|
| Original bank snapshot | The organizer-provided, synthetic banking dataset, kept read-only | Descriptive patterns in its supplied tables and fields | A claim about actual customers, current operations, or a causal explanation |
| Generated interaction-history sample (internal label: E0) | Artificially enriched events intended to add detail around the original synthetic data | Testing whether the engine can use richer event sequences, connect a possible journey, and form a candidate explanation | That the generated contact, error, or outcome actually happened at the bank |
| Platform-event cells | Synthetic events about agent/flow behavior, such as rejected drafts, edits, retries, or escalation | Testing aggregate monitoring and whether repeated system behavior can raise a signal | A live feed from the service platform or proof that a particular event caused a customer outcome |

The source dataset is not modified. Engine-owned records are additive: they can refer to source identifiers where permitted, but they do not rewrite the supplied tables. A link between records is only as reliable as the key, match rate, duplicate handling, and null/orphan checks behind it.

## EDA starting point: the facts that motivated the engine

Exploratory data analysis (EDA) of the [contact and experience report](references/eda/factored_contacto_experiencia_eda.pdf) and [integral bank report](references/eda/factored_banco_eda_integral.pdf) is the analytical starting point for Pulso. The summarized figures come from the supplied synthetic CSV files. The reports link to the scripts and aggregate tables used to calculate them; these are reproducible analysis materials, not inputs to the running engine. Regeneration still requires those local files and their analysis environment. The values describe the hackathon snapshot, not a real bank. Useful audit points are the contact-table joins (p. 2), service and experience (pp. 3–4), complaints (p. 5), temporal comparisons (p. 7), delinquency/product activity (p. 8), and advisor mix (p. 9). The most consequential lesson was the gap between visible friction and evidence that could explain it:

| Evidence from the EDA | Evidence grade | System requirement it motivated |
|---|---|---|
| Complaint contacts had `was_resolved=True` less often than transactional contacts (43.6% vs 91.5%) and took longer at the median (7.2 vs 3.4 minutes). | Descriptive by reason; the contact-row flag is not an event history or eventual case closure. | Compare peer groups and service mechanisms; do not equate a contact flag with the life of a case. |
| Customer requests, complaints and claims (PQRs; Spanish *peticiones, quejas o reclamos*) showed 74.9% in the grouped active-status numerator and a 20.1% supplied service-level-agreement (SLA) breach flag (the recorded service target was missed), but `origin_interaction_id`—the field intended to identify the contact that started the PQR—was empty in the audited local extract. | Exact snapshot counts; no direct PQR-to-origin-contact linkage. | Carry source coverage and join quality with every finding; keep the complaint→contact cause unresolved. |
| Same-customer temporal checks for preceding digital errors or declined transactions showed near-identical rates for target contact reasons and control populations. | Exploratory temporal association; weak/no lift in these checks. | Require a comparator and falsification, not just a plausible story or nearby timestamp. |
| In the later contact EDA, 12,402 customers met the corrected active-credit + 30+-days-past-due + positive-current-balance definition; 90.8% had an approved transaction in the prior 90 days and 74.7% used another product. | Cross-table snapshot behavior; no missed-payment cause or collections outcome. The earlier integral EDA used a different arrears cut and reports 13,242 active 30+ products; do not combine the two counts. | Model delinquency separately from inactivity; do not invent a causal or collection policy from status alone. |
| Campaign sends included conversion flags but no experimental control. | Conversion label, not incrementality. | Require an explicit causal comparator before calling a campaign or service change incremental revenue. |

### Wider EDA map: what each business area contributed

The EDA covered the bank beyond contact-center metrics. This map is intentionally about **questions raised and evidence limits**, not a claim that every area has already been connected to Pulso's autonomous detector.

| Business area | What the reports observed | Why it matters to the engine / what remains unknown |
|---|---|---|
| Customers and products | 150,000 customers and about 400,000 products; 38,937 products had no recent transaction, but 270,062 product last-transaction fields were stale relative to observed transactions | A product status or last-use field can misclassify an active person. Reconcile against time-valid transactions before suggesting activation or churn treatment. |
| Delinquency and collections | The integral EDA counted 13,242 active credit products more than 30 days past due under its product-level rule; the later contact analysis used a corrected customer-level cohort of 12,402 active credit customers over 30 days past due with a positive balance | Keep the definitions separate. Recent transaction activity means overdue customers are not necessarily inactive; neither snapshot proves missed-payment cause, recovery probability or intervention lift. |
| Payments and digital journeys | 4,425,008 transactions, including 221,234 declines; 15,620,994 digital events, including 358,723 error events. The session view found 46,828 sessions containing both Error and Purchase, but did not establish event ordering | Counts identify candidates for a funnel/sequence analysis. A decline may later succeed; an error can occur in a session that completes a task. Do not count either as lost revenue without an outcome link. |
| Contact and PQR service | 686,296 contact records, 160,266 marked unresolved on the contact record, 67,095 customer requests/complaints/claims (PQRs); complaint contacts contributed 41.2% of unresolved-contact records | Strong operational prioritization signal, but a contact flag is not a full case history and the audited PQR-origin key was empty. |
| Surveys and customer experience | Contact report contained 212,759 survey rows; response coverage and linked samples varied by metric. Complaint CSAT (customer-satisfaction rating) was 2.43/5 and NPS (promoters minus detractors) -85.3 among respondents | A serious warning signal, not a census of all customers. These are respondent measures and are vulnerable to who chose to answer. |
| Advisors and branches | 1,090 advisors were observed; reason-mix-adjusted resolution gaps were much narrower than raw reason differences. Only 28.6% of PQRs had a linked branch, and branch counts lacked a comparable customer/transaction denominator | Avoid blaming individual advisors or branches from raw rankings. Case mix, selection and missing exposure denominators can explain apparent extremes. |
| Campaigns and growth | 1,746,801 sends and 9,799 tagged conversions (about 0.56%) | A tagged conversion may have happened without the campaign. Without a control group, this is not incremental sales or profit. |
| Exchange rates and source QA | The observed extract contained 13,164 exchange-rate rows versus about 3,000 in the organizer summary | Investigate grain/refresh semantics before translating monetary values; a row-count mismatch is a data contract question, not permission to discard rows. |

This broad scan is why Pulso's opportunity portfolio must include **service operations and business outcomes**, plus data-quality evidence. It should not confuse “a field exists in the CSV” with “the field is trustworthy enough to guide an action.”

This is why evidence in the product is carried as a ladder: **fact → pattern → explanation to test → candidate mechanism → evaluated outcome**. A later stage does not inherit certainty from the prior stage. For example, observing many declined payments is a fact; seeing a higher decline rate in one well-defined group is a pattern; believing a missing service step caused it is an explanation still to test. The [technical detection chapter](technical/04-detection-and-evidence.md) describes how these lessons become detectors, data contracts and intervention selection.

## Four strengths of a statement

1. **Observed fact:** a count, value, or event present in a named input, with its denominator and source version.
2. **Pattern:** a difference or association found in those observations. It answers “what tends to appear together?”—not “what caused what?”
3. **Explanation to test:** a plausible business mechanism, such as repeated edits suggesting that an agent's answer is not useful enough. This is a hypothesis until it survives a discriminating test.
4. **Impact:** a change in safe resolution, customer experience, cost, or revenue. This needs valid outcome data and a comparison; an offline pattern or simulated evaluation is not impact evidence.

A proposed configuration is an intervention idea, not a fifth kind of evidence. It should retain the evidence and hypothesis that motivated it, and its test result should remain separate from the proposed benefit.

## A concrete example: the platform monitor

The pinned code contains seven ways to group service-platform events: rejected drafts, heavily edited suggestions, missing suggestions, failed suggestions, tool-use mix, case-type reassignment, and escalations. Tests exercise them on generated event histories with patterns deliberately planted by the test. The [implementation note](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/data/platform-event-cells.md) shows that the sensor can aggregate and detect a programmed pattern; it does not show that the pattern exists in a live bank service. This sensor is not yet connected to the engine's main automated reasoning run. Do not read “sensor exists” as “the engine continuously finds live platform problems.”

When the engine combines records, it distinguishes an exact identifier match from a nearby event in time and from two counts that merely rise together. Temporal proximity and co-occurrence can prioritize investigation, but neither establishes that one event caused another.

### How to read a finding without skipping steps

Take the open-PQR-rate example from the separate planted test. The **fact** is a count of records matching a named status rule divided by all included PQR records. The **pattern** is a difference between one category and a comparison group, repeated in a reserved portion of the generated test data. The **hypothesis** is that a customer may need clearer status information. The **intervention** is a wording change in one local response-template draft. The **outcome**—whether fewer customers contact support again—is unknown because the test did not measure it. Each sentence gets one evidence label; evidence at an earlier step does not automatically validate the next one.

This ladder is useful beyond PQRs. A digital error near a contact may be a lead to investigate; it is not yet “the customer called because the app failed.” A high escalation rate may be a service-quality signal; it is not yet an agent-caused delay. If the exact linkage or outcome is missing, the correct statement is unlinked/unknown and the improvement remains a testable hypothesis.

## What the current bank-data analysis concluded

One documented analysis of the generated interaction-history sample attempted eight group-level summaries. All eight were withheld by a disclosure rule: groups with fewer than 10 records were suppressed, as were some larger groups when their values could be inferred by subtracting other published totals. This tells us the breakdowns could not safely be published; it does not tell us whether a pattern is common, rare, or absent. The analysis produced **no publishable breakdown or root-cause explanation from those eight views**. The right conclusion is “not publishable from this analysis,” not “there is no issue.”

That result is not the only evidence from the bank snapshot. A separate scan summarized it into 7,995 group-level metric rows and marked 19 patterns as “corroborated.” In this run, that label has a narrow meaning: a deterministic customer split reproduced the pattern in a reserved portion of the same synthetic extract. It does not mean an independent source, human verification or causal confirmation. Later local attempts produced tested response-template drafts for five complaint-reason × channel groups. This is evidence of a narrow pattern-to-draft route—not a re-analysis of the eight withheld views, not a causal complaint journey, and not measured service improvement. Keep the two findings distinct: **one analysis could not publish its breakdowns; a separate detector/proposal route produced drafts for a subset of aggregate groups.**

This is an important product behavior, not a failed chart: the engine should be able to stop itself from turning thin or generated evidence into a confident-sounding root cause.

## Privacy and evidence labels

For a judge-facing report, show aggregates, denominators, source type, analysis version, and any suppression or coverage warning. Do not show raw customer rows or transcripts. Mark a result as **synthetic**, **generated/enriched**, **descriptive**, **hypothesis**, **tested candidate**, or **operationally measured** as appropriate. A minimum-group threshold of 10 reduces one small-group disclosure risk; it does **not** anonymize the dataset or provide a formal mathematical privacy guarantee such as differential privacy. Outside knowledge, other dimensions, or repeated queries can create additional inference risks. Suppression controls therefore also need complementary-group protection (withhold another value if publishing it would let a reader calculate the suppressed value by subtraction). If a small group is suppressed, say so explicitly; never display a blank as if it were zero.

**Business reading:** the current data package is useful for exercising the discovery machinery and its safeguards. It is not a substitute for production customer outcomes. Any later claim of cost saved, complaints avoided, or satisfaction improved must be measured independently from the discovery signal.
