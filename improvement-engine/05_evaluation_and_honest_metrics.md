# 5. How we decide whether an improvement is real

Pulso has two different things to test: first, whether the **Improvement Engine** found a repeatable pattern in its evidence; second, whether a proposed change to the service behaves better than the existing version. Neither test alone proves that customers benefited. Here, **baseline** means the current service capability, **candidate** means the proposed version, and a **holdout** is a set of cases kept aside from designing the change. A **service artifact** is the platform-native building block being changed, such as a decision Flow or response Template.

Testing a detector and testing a proposed service change answer different questions. Even a candidate that passes every programmed check has not yet shown that customers were helped. This chapter explains the evidence ladder in plain language and summarizes what is actually recorded.

## The evidence ladder

| Level | Plain-language question | Example evidence | What it cannot establish alone |
|---|---|---|---|
| Data validation | Did we read the intended source and fields? | Field-structure checks, source fingerprint, row and coverage report | Correct business interpretation or complete data |
| Signal test | Can a sensor find a known pattern and avoid specified false alarms? | Generated positive/negative cases with counts | That the pattern exists in actual service operations |
| Candidate regression | Did the changed service capability preserve required behavior and address target cases? | Same named cases against baseline and candidate | Generalization to new cases or customer benefit |
| Held-back evaluation | Did the candidate succeed on examples not used to design it? | Frozen split and reproducible baseline/candidate results | Causal impact in production |
| Operational impact | Did authorized use change outcomes safely and economically? | Linked, representative outcomes plus a comparison design | Effects outside the measured population without further evidence |

The target product must report which level each result reaches. “Passed” without a named test and population is not an interpretable result.

## What the planted candidate test tells us

The clearest controlled candidate example is a **deliberately planted synthetic pattern**—a difference intentionally inserted into generated test data—described in the [demo-loop record](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/DEMO_LOOP.md). Its intended signal was inserted into invented monthly aggregate counts before the detector ran, in both the discovery split and a generated replication split. For the group labeled “improper charge,” the open-complaint share was 4,095/6,610 = **62.0%**, compared with 8,663/26,460 = **32.7%** across the other categories. In the replication split, it was 4,034/6,508 = **62.0%**, versus 8,699/26,351 = **33.0%**. Reproduction here means that the same pattern appeared again in generated summaries—not that it generalizes to real service cases. These are synthetic counts, not customer records.

The candidate changed an existing response template so a PQR-status reply—about a *petición, queja o reclamo* (request, complaint or claim)—would include the current status in Spanish and Portuguese. The runbook defines eight targeted cases intended to need that status and three guard cases that protect other behavior. It says the original wording failed all eight targeted wording checks; the candidate's status placeholder rendered against seeded test state and passed the configured regression proof. The pinned summary does not let us safely attribute a separate baseline-suite score to that exact candidate run, so we do not borrow the 11-scenario result from another Agent Core smoke test. The runbook also reports 15/15 Agent Core gate items, but the summary does not enumerate them, so that count is not a stand-alone quality score. The local Agent Core registry read the candidate back as a draft. It was never approved, published, promoted or used with customers. No customer resolution, complaints avoided, NPS (Net Promoter Score), CSAT (Customer Satisfaction score), revenue or cost savings were measured.

Why isn't this a real discovery result? Because the program intentionally planted the higher rate in the test input. The check shows the detector and proposal path can respond to a known pattern and reproduce it in held-back generated counts. It does not show how often open complaints occur in the underlying bank data, that the change itself reduces open complaints, or that the status wording is the cause of complaint friction. “62% versus 33%” is a descriptive gap between generated groups, not a 29-point improvement.

## What the bank-cell run tells us

The bank-cell story has more than one iteration. Here, a **bank cell** is an aggregate group of records from the supplied synthetic bank snapshot, not an individual customer. The first capped attempt over **7,995 aggregate rows** did not announce a proposal: proposed new agents hit a local Agent Core permission boundary, one finding lacked a supported mapping to a service capability, and one was blocked when a model was unavailable. Later mapping runs ([run record](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/MAPPING.md)) searched the same portfolio of aggregate groups. Nineteen patterns passed a repeatability check on a deterministic holdout drawn from that same synthetic extract; ten concerned patterns in the share of contacts marked unresolved. The runs also produced draft `t/estado_pqr` response templates for complaint findings across five channels. This is narrow evidence that a model-authored change to an existing artifact can pass a configured regression check and be read back from a local Agent Core registry as a draft. It does not prove that the contact/PQR relationship is causal or that the draft improves customer outcomes. Some other candidate types remain blocked; model attempts also varied between proved, refused and unavailable outcomes. See [chapter 2](02_product_rationale_and_architecture.md) for the full distinction.

Other evidence also stays separate:

- The seven-family platform-event sensor—a set of measurements over service software's recorded events—was tested against generated histories; all 13 findings that repeated in its documented test run were deliberately planted. It does not prove a live feed or spontaneous discovery.
- The offline runner for the original bank tables and the separately generated enriched interaction history (called “E0” in engineering files) is deterministic and makes no model-provider or Agent Core call. It produces descriptive/recurrence outputs, not an executable service change.
- A separate local support-layer smoke test exercised Agent Core's Jev structured decision model on dispute and general-inquiry cases. Its proposals were supplied by a person, and its query-classification stage used a keyword-based stand-in (a simplified substitute for a real classifier). This is not evidence that the Improvement Engine discovered those cases autonomously.
- A separate [human-gated synthetic new-agent lifecycle](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/AGT1_NEW_AGENT_PATH.md) tested a planted technical-support/phone case: the existing version failed six targeted cases, the candidate was proposed, and a person approved and moved it through local staging to a test-only active-version alias whose internal name was `prod`. This did not deploy to bank production. The only seeded platform case type was incorrect-charge, so the run proves a human-gated lifecycle—not correct routing or a valid customer reply.
- In the enriched-history retrospective, all eight aggregate breakdowns were suppressed under disclosure controls. “Not publishable from this view” does not mean the issue is absent.
- A separate synthetic proposal-rubric exercise compared two labeling passes over 40 proposals. They agreed on many ratings, but one pass was not blind, the other was an independent model context rather than a human, and actual judge-versus-labeler agreement remains unmeasured. Detailed statistics and limits are in the [technical evaluation appendix](technical/06-evaluation-and-sandbox.md).

## Why the distinctions matter

The discovery detector is judged on its ability to identify a pattern under a declared data definition. The proposed service change is judged on whether a concrete artifact handles relevant test cases better than the current version. Business impact is judged only after an authorized release operates on suitable cases and outcomes are measured. Mixing these stages would let a planted test pattern masquerade as customer impact.

For any comparison, preserve the metric definition, numerator and denominator, comparison population, data split, source digest, candidate/current-version identifiers, evaluator version, failures and uncertainty. A percentage without its population can hide a small or biased sample. Searching many groups also increases the chance of finding a coincidental difference; V3 separates initial discovery from confirmation and requires the search process to be considered when evaluating evidence.

### How a candidate can fail—and what the failure means

| Failure/status | Interpretation | Safe system response |
|---|---|---|
| Base and candidate both pass target cases | The suite cannot discriminate this change from existing behavior | Do not claim the candidate fixes the target; improve the test or reject the proposal |
| Candidate fails a guard case | The proposed change regresses a protected behavior | Stop and retain the failed test/evidence; never announce as proven |
| Candidate text compiles but fails a semantic/wording probe | Valid format did not produce the intended behavior | Return the failure to the Builder or stop; syntax is not quality |
| Agent Core denies a write (permission denied) | The current service identity lacks authority for this artifact/action | Keep it blocked; do not borrow human/admin credentials or silently substitute another artifact |
| External model provider is unavailable or times out | The attempt has no quality verdict | Record dependency failure; retry only under bounded policy, otherwise stop this finding without calling it disproven |
| Finding has no supported artifact or test generator | The engine cannot show a controllable change and measure it yet | Keep the finding as an investigation/human-owned item, not a fake proposal |
| An aggregate group is withheld or a data link is absent | Available evidence is insufficient to safely describe or connect the pattern | Report withheld/unlinked/unknown, not zero and not “no problem” |

An evaluation system earns trust by distinguishing “the idea failed,” “the test cannot tell,” and “the dependency never produced a verdict.” These statuses have different next actions and must not collapse into one red/green score.

## What the complete product must eventually measure

Once a change is approved and operated through the external service platform, measure its intended mechanism and—where valid links exist—downstream outcomes: safe resolution, repeat contact for the same issue, human escalation, handling time, complaint status/SLA, satisfaction among survey respondents, and operating cost. Report eligibility, coverage, numerator/denominator, uncertainty, safety regressions and segment limits. **NPS** (Net Promoter Score) and **CSAT** (Customer Satisfaction score) are survey measures from respondents; neither automatically represents every interaction.

At present, no recorded result establishes causal lift, production savings, improved NPS/CSAT, or a real customer rollout. Those remain future product outcomes, not missing decorations on a current chart.

## Further technical detail

See [Evaluation and sandbox](technical/06-evaluation-and-sandbox.md) for frozen test cases, decision gates, statistical controls, failure cases and evidence grades; see the [implementation map](technical/09-implementation-map.md) for gaps preventing the full V3 loop.
