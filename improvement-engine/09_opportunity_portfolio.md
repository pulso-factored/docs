# 9. From bank evidence to a portfolio of improvement bets

## Do not optimize the biggest number

Exploratory data analysis (EDA) did not reveal one unquestionable “80/20 fix.” It revealed different possible opportunities, each with different evidence, business mechanism, effort and risk. In the contact analysis, complaint contacts (*Queja*) and technical-support contacts (*Técnico*) together accounted for **60.5% of contact rows marked unresolved in that analysis**. The two leading PQR subcategories—PQR means *petición, queja o reclamo* (request, complaint or claim)—represented **20.2% of PQR records**. A useful Pareto lens means *prioritize concentrations where they exist*; it does not mean forcing every table into a 20/80 story.

The whole-bank analysis and the contact deep dive also asked different questions. One compared illustrative annual value scenarios and implementation difficulty; the other prioritized visible service pain and a feasible prototype path. These are not contradictory rankings: they optimize different things. A good Improvement Engine should preserve both views, state which objective it is ranking, and show why each candidate lands where it does.

## The value calculation

Use a consistent scenario equation, with every assumption visible:

```text
Net scenario value
  = eligible cases × assumed mechanism success × value per successful case
    − variable delivery cost − fixed implementation/operation cost
```

This is a **scenario calculation**, not a measured outcome or forecast. “Eligible cases” are only cases the proposed change could plausibly affect; “mechanism success” is an assumed chance that it changes the intended behavior; and “value per successful case” is an assumed economic value. For service-capacity opportunities, report freed minutes or staff capacity separately from cash savings. For growth, count only incremental contribution above a credible comparison—not conversions merely tagged to a campaign. For collections, distinguish balance exposed to delinquency from expected loss and incremental recovery. Do not add value from overlapping customer journeys as if they were separate populations.

## Candidate portfolio from the supplied analysis

| Candidate | What was observed | Plausible first intervention | Potential value mechanism | Effort / risk | What could falsify or block it |
|---|---|---|---|---|---|
| **Improve complaint follow-up** | 117,021 complaint-contact records (*Queja*); 43.6% were marked resolved on the contact row, while about 66,000 rows were marked unresolved—41.2% of all unresolved contact rows. PQR records had status and service-level-agreement (SLA: the expected service-time commitment) fields but no populated direct origin-contact key in the audited extract. | Clarify verified status in an existing response Template or improve a supported triage Flow (a structured decision path). The separate bank-aggregate run demonstrates a narrow local Template-draft path. | Fewer status-check contacts or faster safe resolution could reduce handling effort; the value of an avoided repeat contact is not measured here. | A small, reversible candidate if the service exposes an authoritative status; customer impact remains uncertain. | No link from a PQR to its originating contact; no repeat-contact outcome; a clearer message cannot close an open complaint. |
| **Improve technical support** | 102,899 technical-support contacts (*Técnico* in the source); 30,940 marked unresolved. Digital errors were visible, but the same-customer temporal comparison was about 0.16% before technical contacts versus 0.15% overall. | Investigate a bounded Jev decision model or technical-support Flow; choose a flexible AI Agent only if the task needs open-ended reasoning. | Reduce avoidable handoffs or shorten resolution if an actionable technical failure is identified. | Moderate: event sequence, action authority and safe escalation matter. | An error may happen without blocking the task; observed temporal rates were nearly level; no proven causal link. |
| **Streamline transaction/dispute intake** | 240,056 transaction-related contact records; 91.5% marked resolved and a 3.4-minute median duration. The source also had 221,234 declined transaction attempts. | A deterministic Flow can collect a reference and retrieve an authorized transaction; Jev can route a bounded dispute category. | Lower rework or faster intake; transaction lookup may reduce service-agent effort. | A focused prototype is plausible, but account identity, transaction eligibility and refusal rules matter. | A decline is not necessarily a lost payment; the customer may retry; no exact link between transaction and contact or measured effort avoided. |
| **Reduce digital-task friction** | 15.62M event rows, including 358,723 `Error` events. In the session view, 17.4% had an Error and 46,828 contained both Error and Purchase; the aggregate did not establish event order. | Repair a known service-platform handoff, or adjust a decision path/tool configuration only when evidence shows that the platform capability owns the problem. | More completed tasks or fewer support contacts if an error blocks a task. | Potentially broad reach, but event meaning, ownership and timing need validation. | A session can contain an error and still complete a purchase; without the ordered task outcome, the apparent friction may be harmless. |
| **Activate an eligible product** | 35,010 unused accounts/cards, of which 14,911 belonged to active customers with commercial authorization—13,257 unique people. The modeled opportunity counts at most one activation per person, not one per unused product. | A targeted explanation of eligibility and benefits through a response Template, Flow or bounded decision, depending on the service gap. | Additional product contribution, minus message, service and fixed costs. | Potentially low effort when eligibility and permission to contact are already valid; avoid indiscriminate marketing. | A campaign conversion label is not proof of incremental sales. The scenario depends on assumed activation rate, contribution and cost. |
| **Improve early-stage collections support** | The integral report estimated USD 26.6M exposed balance in Mexico's active 30–89-day-past-due group under its definition; later reports use a different customer-level arrears cut. Many delinquent customers still used other products. | First test a bounded servicing/eligibility Flow and a safe explanation/handoff, not an autonomous repayment or credit policy. | Incremental recovery if an eligible intervention changes payment compared with no intervention. | High gross potential but higher execution difficulty, policy/customer-harm risk and uncertain recoverability. | Balance is not loss; there is no repayment/recovery outcome or causal intervention estimate; cohort definitions differ. |
| **Improve campaign incrementality** | 1,746,801 sends and 9,799 tagged conversions (about 0.56%). There was no untreated comparison group. | A service-side eligibility or product-explanation change only if the platform gives a controllable contact path. | Incremental margin above the conversion rate that would occur anyway. | Media cost and attribution risk; campaign spend control is outside the engine unless explicitly exposed. | Without a comparison group the observed conversion cannot establish campaign-caused sales. |

## What the scenario numbers do—and do not—say

The whole-bank EDA compared illustrative 12-month scenarios in USD:

| Scenario in the EDA | Modeled result | How to interpret it |
|---|---:|---|
| Complaint handling capacity | About **USD 7,032** | Estimated capacity/time value under assumed wage and capture factors; not cash savings or a proven reduction in staffing cost. |
| Selected activation case | About **USD 7,954 gross contribution** before messaging and fixed costs | Assumed activation and contribution; not incremental sales measured against a control. A separate Mexico SMS sensitivity showed that more messaging could make the scenario negative. |
| Early collections in Mexico | At a **0.05%** assumed improvement on USD 26.6M of 30–89 day balance, minus USD 5,000 execution cost, about **USD 8,305 net scenario value** | Sensitivity arithmetic, not a forecast of recoveries. The low 0.01% case was negative; 90+ day debt was treated as harder to recover, not as an equivalent opportunity. |

All scenario amounts are in **USD**. They are not directly comparable without a shared definition of eligible population, time horizon, cost capture and risk. In particular, the collections example looks most attractive only at one assumed success rate, while also being the hardest to execute. The EDA therefore did **not** conclude “collect more at any cost.” It recommended weighing potential value against difficulty; the contact-focused analysis separately selected dispute intake as a feasible prototype to evaluate.

## The engine's prioritization rule

For each candidate, Pulso should expose four independent dimensions:

1. **Evidence strength:** exact join or aggregate association; source coverage; time validity; independent confirmation; counter-evidence.
2. **Controllability:** the specific decision Flow, Jev model, response Template, AI Agent, Tool definition (configuration for a service capability), context or platform owner that can change the mechanism. If none is supported, retain a finding without fabricating a proposal.
3. **Value range:** eligible scale × plausible mechanism effect × value per successful case, with assumptions and overlap caveats.
4. **Delivery difficulty and risk:** effort, runtime/permission dependencies, customer harm, reversibility and monitoring burden.

This makes the decision legible: a small Template patch may be the best *next test* even when a collections opportunity has a larger theoretical ceiling; a high-volume digital error should not outrank a lower-volume failure if most errored sessions still complete. “Do nothing yet” remains a valid candidate when evidence or authority is inadequate.

## Why this portfolio matters to the product story

Pulso is not a complaint-resolution bot, a collections optimizer, or a marketing recommender. It is the engine that repeatedly performs this analysis: scans broadly, notices concentrations without being told which table to favor, checks the business story, identifies the controllable platform surface, selects the smallest testable native artifact, compares alternatives and records why it proceeded or stopped. A future run can elevate a different opportunity if the evidence, value assumptions or available artifact changes—and it must show the change in rationale.

The EDA provided the first candidate portfolio and taught us how easily a large balance, error count, poor survey score or conversion label can be mistaken for value. The Improvement Engine's value is to make the transition from those raw signals to a governed, testable decision repeatable, visible and honest.

## Sources

- [Integral bank EDA](references/eda/factored_banco_eda_integral.pdf), especially the executive decision, customer/product activity, delinquency scenarios and 12-month comparison.
- [Contact and experience EDA](references/eda/factored_contacto_experiencia_eda.pdf), especially the contact reason, PQR, digital, agent, branch and cross-domain analyses.
- [Storytelling EDA](references/eda/factored_eda_storytelling.pdf), especially the data inventory, Pareto test, candidate hypotheses and business interpretation.
- [Data definitions, joins and caveats](03_data_provenance_and_evidence.md).
- [Canonical V3 product and implementation target](../archive/source-record/2026-10-05/TECH_SPEC_PULSO_AUTOMEJORA_V3.md).
