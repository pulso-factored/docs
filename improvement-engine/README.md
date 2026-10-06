# Pulso Improvement Engine

> **Documentation snapshot note (5 October 2026).** The story and technical chapters below preserve their own source/commit pins, which may predate the current repository `main`. For current code, configuration and runnable commands, follow [`pulso-factored/improvement-engine`](https://github.com/pulso-factored/improvement-engine) and its README; the raw V3 specification and working record are retained in the [source archive](../archive/README.md). Do not treat an older chapter's “current main” label as a live status assertion.

> **New to Pulso? Start with the [judge guide](00_judge_guide.md).** It explains the Improvement Engine from the beginning—what problem it solves, where the idea came from, how the system is meant to work, what is implemented today, and what remains a V3 target. This README and the chapters below are the evidence index and supporting detail; they are not prerequisites for understanding the product.

## What is this?

**Pulso Improvement Engine is the part of Pulso designed to help a bank's service improve over time.** It looks across records of many interactions—not just one conversation—to find recurring friction, investigate whether a pattern is credible, and prepare a testable change to the support system. It does not itself answer customers or operate their accounts.

This is different from a chatbot. A chatbot answers one customer. The Improvement Engine asks: *Across many interactions, where is service failing or taking unnecessary effort—and what safe change could prevent the same problem next time?*

This guide is written for judges who have never seen Pulso, its service platform, or its code. It combines the product case with the engineering explanation: why the problem matters, how the engine is meant to work, why we chose this design, what is implemented, what has been tested, and what remains open. Internal labels are translated before they are used.

The engine is only one part of the deliverable story. The separate [infrastructure and observability chapter](../infra/guide/infrastructure-and-observability.md) explains how the `infra` repository is intended to host it, where Langfuse fits, and what is—and is not—verified about cloud deployment and trace export.

**Evidence snapshot:** implementation claims below are checked against GitHub `main` at commit `fc56b598b1be483a6b1eb7ee6fac0d9809c3b646` (5 October 2026). Individual run records can come from a different code branch, local Agent Core revision or test stack; each is labelled separately. The bank data is synthetic hackathon data, not production records. V3 is the product/technical target, not a list of delivered features.

## The story in one minute

1. Support teams automate recurring tasks, but customers can still face repeated contacts, unclear answers, rework and handoffs. A chatbot helps one person; an analytics dashboard can describe many cases. Neither alone turns a verified pattern into a governed service change.
2. Pulso's engine is designed to close that gap: measure a pattern, investigate explanations, test a change to the service capability, and keep evidence and human authority attached to the change.
3. It proposes configuration for a separate platform called **Agent Core**—the system that stores and runs service components such as decision flows and agent behaviors. Pulso does not rebuild that runtime.
4. Code enforces data boundaries, arithmetic, versioning and approval rules; AI helps explore evidence and draft candidate changes. Neither AI output nor a high metric automatically becomes truth or a release.
5. Every result is labelled by what actually ran. Today, an offline runner over the original tables and a second, generated/enriched interaction-history sample (internal label **E0**) is separate from generated platform-event tests, a narrow bank-cell-to-Agent-Core draft loop, a planted-data integration demo and a human-gated lifecycle rig. These are distinct proofs, not one joined end-to-end run. V3 describes the complete self-improvement loop; that general loop is not yet proven end to end.

The ambition is the V3 design. This guide describes the implementation and evidence present in the current repository snapshot, and separates it from local test records, synthetic demonstrations and work that remains.

## Where Pulso began: the bank EDA

Pulso did not start as an abstract agent framework. It began with a broad exploratory analysis of the hackathon bank snapshot: thirteen synthetic tables, 150,000 customers, three countries and roughly three years of activity. The largest named tables alone contain 15,620,994 digital events and 4,425,008 transactions; we avoid quoting one grand row total because the reports and source extracts use different grain and count conventions. The analysts asked ordinary banking questions across payments, products, collections, service, complaints, digital journeys and campaigns, then tested whether those facts could be connected into explanations and plausible business choices.

That work revealed both opportunity and a harder product problem. Complaint-related contacts (*Queja* in the source data) were a conspicuous service pain (117,021 rows; 43.6% carried the contact-level `was_resolved=True` flag), but the data did not reliably join a PQR—a *petición, queja o reclamo* (customer petition, complaint or claim)—to the interaction that caused it. Digital errors and declined payments were visible, yet conservative checks comparing the same customer around nearby dates did not show a higher contact rate than the comparison. Campaign conversions were recorded without an untreated comparison group. Collections had scale, but a snapshot could not explain why a customer missed a payment or how much debt an intervention would recover. The tempting charts were not enough to justify a causal fix or a bank-wide return-on-investment claim.

### Three lessons that became product requirements

| What the analysts learned | Product consequence |
|---|---|
| **Service friction can be measured.** Contact reasons, handling times, complaint status, survey responses and digital/transaction events provide useful leads. | Detect across domains and rank by evidence, scale, potential value and effort—not by whichever chart looks largest. |
| **A plausible story can fail its first check.** Missing complaint-to-contact identifiers, low survey response, flat time-window comparisons and campaigns without a control leave important explanations unresolved. | Preserve denominators and data coverage; test competing explanations; distinguish association from cause; return “unknown” or “unlinked” when the source cannot answer. |
| **An insight is not yet an improvement.** Even a credible pattern does not tell us which service capability to change or whether it works. | Turn only supported opportunities into a small, versioned platform change; test it against the existing behavior; leave release authority with a human. |

The PQR-status example later in this guide is deliberately a **mechanics example**, not the EDA's declared business winner: it lets us show the path from a bank pattern to a concrete, reversible response-template draft and a discriminating test. The original EDA did not prove that unclear status caused repeat contact, nor that this intervention outranks other opportunities by expected value.

This gap shaped the product: instead of hard-coding “solve complaints” or shipping a dashboard that stops at description, Pulso is intended to repeatedly discover candidate friction across the service, investigate and challenge the explanation, and prepare the smallest testable change to the service system. It must also say “unknown,” “unlinked,” “suppressed” or “blocked” when evidence does not support a stronger claim. The EDA supplied the questions and limits; the Improvement Engine is our proposed mechanism for turning future evidence—including what the service agents and flows themselves do—into governed iteration.

The source reports are available for readers who want the full analytical trail: [integral bank EDA (25 pages)](references/eda/factored_banco_eda_integral.pdf), [contact and experience deep dive (13 pages)](references/eda/factored_contacto_experiencia_eda.pdf), and [earlier storytelling report (10 pages)](references/eda/factored_eda_storytelling.pdf). For example, the contact report's join map (p. 2), contact/CSAT/PQR views (pp. 3–5), temporal tests (p. 7) and arrears analysis (p. 8) show how the findings and caveats were built. Their figures describe the synthetic hackathon files and scenario assumptions, not real bank performance. The data-provenance chapter below explains which relationships were exact, merely temporal, or unavailable.

## The product loop we are building

**V3 target — illustrative storyboard, not one completed run.** The engine is meant to keep looking for service problems without an operator preselecting the answer. AI helps investigate and design; deterministic controls keep the evidence, permissions and release boundary explicit.

| Moment | What the engine does | What makes it trustworthy / visible |
|---|---|---|
| 1 · Notice | A schedule, new source snapshot or approved platform-event batch can start a run; the operator does not have to say “find complaint problems.” | The trigger, tenant, purpose, source versions and configuration are pinned to the run. |
| 2 · Measure | Deterministic sensors compare rates, counts and coverage across eligible groups. | Numerator, denominator, comparison group, missingness and uncertainty travel with every signal. |
| 3 · Explore | A reasoning task can ask new questions of a treated, bounded data workspace to understand a signal. | It sees only the authorized projection; queries and factual claims retain receipts and source references. |
| 4 · Challenge | A separate verifier looks for broken joins, selection bias, time leakage, counterexamples and alternative explanations. | A weak or contradictory result is rejected, deferred or marked unknown—not promoted by confidence language. |
| 5 · Design | A builder proposes the smallest relevant service-capability change: perhaps a decision flow, a structured decision model, a response template, or an agent. | The output is a versioned Agent Core-native draft tied to the evidence; “new agent” is not the default answer. |
| 6 · Test | The same frozen cases are run against the existing capability and the candidate. | Safety regressions, missing oracles, low support and unavailable dependencies stop the candidate with a reason. |
| 7 · Govern | The backoffice shows evidence, uncertainty, change diff, tests and the exact decision requested. | A human's approval is bound to the exact candidate version; the model cannot publish or promote it. |
| 8 · Learn | Later operational evidence can support, contradict, expire or revoke stored knowledge and start another cycle. | Memory is versioned; new evidence does not silently overwrite or strengthen an old claim. |

For a concrete nine-step walkthrough—from the automatic trigger and evidence checks to a candidate draft, evaluation, human decision and later memory—see [the full PQR-status example in chapter 2](02_product_rationale_and_architecture.md#v3-target-example-how-one-signal-becomes-a-governed-change). It is explicitly separated from the current planted demo.

**Current evidence is split across separate proofs, not one joined loop:** an offline original/enriched-history runner, generated platform-event sensor tests, an early bank-snapshot attempt that stopped at integration blockers, later bank-cell mapping and template drafts, a separate planted synthetic proposal, and a human-gated new-agent lifecycle rig. The evidence card below keeps their inputs and claims separate. The autonomous V3 loop remains the goal, not the current product status.

## Start here: the story for a judge

This folder is the **judge-facing guide**: it explains the product story and the evidence in accessible language. For engineers who need implementation boundaries, data contracts, state machines, failure semantics, test scope and current integration gaps, use the separate [technical reference](technical/README.md). The two documents intentionally have different audiences and levels of detail.

- [1. The product problem and Pulso’s value](01_hackathon_criteria_map.md)
- [2. How one improvement should move through the system](02_product_rationale_and_architecture.md)
- [3. The data, the findings and what they can prove](03_data_provenance_and_evidence.md)
- [4. Trust, privacy and limits on automation](04_security_and_controlled_automation.md)
- [5. How we test whether a proposal is better](05_evaluation_and_honest_metrics.md)
- [6. Engineering decisions and their trade-offs](06_engineering_choices_and_tradeoffs.md)
- [7. What is implemented, demonstrated and still open](07_current_status_and_pitch.md)
- [8. How the team built it and how to present it](08_development_process_and_priorities.md)
- [9. The EDA opportunity portfolio, value scenarios and prioritization](09_opportunity_portfolio.md)
- [10. How service-operation evidence can feed the improvement engine](10_learning_from_service_operations.md)
- [11. Human partnership and the operator experience](11_human_partnership_and_operator_experience.md)
- [12. How Pulso chooses what to improve](12_how_pulso_chooses_what_to_improve.md)
- [13. A worked discovery-to-proposal reasoning trace](13_a_finding_becomes_a_testable_opportunity.md)

The chapters above build the product story. If you want implementation depth, the [technical reference](technical/README.md) continues with architecture, data/persistence, run lifecycle, detector contracts, Agent Core integration, evaluation, memory, operations, and a code-to-gap map. It is part of this packet, not a separate product story.

**Suggested path for a first-time judge:** start with the opening/EDA origin, then [the product loop](02_product_rationale_and_architecture.md), [what is implemented versus still a goal](07_current_status_and_pitch.md), [the worked evidence-to-draft example](13_a_finding_becomes_a_testable_opportunity.md), and [how the engine chooses its next investigation](12_how_pulso_chooses_what_to_improve.md). Chapters 10–11 add the future operational-evidence source and low-touch operator experience. The technical reference is the implementation companion; V3 remains the source for exact contracts and acceptance criteria.

## Evidence snapshot in one minute

| What we can show | What the record says | What it does **not** prove |
|---|---|---|
| Offline original-data + enriched-sample runner | Repeatable local descriptive path; no model provider, Agent Core or network call | Autonomous candidate generation or business impact |
| Bank-cell improvement loop | A recorded mapping run scanned 7,995 aggregate rows; 19 findings passed the strict sensor's discovery/holdout replication gate. The aggregator assigns customers deterministically to discovery (A) and holdout (B), so this is a repeatability check inside the same synthetic extract—not independent-source confirmation, human verification or causal proof. Five complaint-reason/channel cells had a local response-template draft pass a targeted regression proof; each output stayed a draft. | That a complaint caused a contact, every flagged pattern can be acted on, or a draft reduces repeat contacts or improves bank outcomes |
| Earlier bank-cell attempt | Its first capped run tried four findings and stopped at permission, mapping and model-availability blockers | That later mapping/proof iterations never happened; this is iteration history, not the latest bank-cell result |
| Separate planted proposal demonstration | 350 invented monthly aggregate rows exercise a known PQR-status pattern; a model-assisted candidate passed a narrow regression proof and was read back as a local Agent Core draft | Independent discovery or real-bank prevalence/outcomes; this is separate from the later bank-cell mapping runs |
| Human-gated new-agent lifecycle rig | A planted synthetic technical-support finding produced a new-agent draft; a person evaluated, approved, published in local staging and activated the rig's `prod` alias | Correct case routing or reply—the seeded type was an incorrect-charge case—or any real bank deployment/customer result |
| Seven-family platform-event sensor tests | Generated event histories; 13 findings passed the programmed repeat-pattern check, all planted | A connected live event feed or spontaneous finding from operations |
| Enriched-history retrospective | Eight breakdowns suppressed under disclosure rules | That there is no issue, or that suppression measures statistical significance |

The [original/enriched-history snapshot runner](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/local-e0-e2e-runner.md) is another separate proof: it reads both data sources offline and deterministically. Original-bank output is descriptive and partial; the enriched sample can produce structured records that prepare a future investigation, but no model or Agent Core is executed and no candidate is released. The evidence card makes unlike demonstrations impossible to mistake for one successful live run.

> **The magical moment to watch:** the bank-cell route notices a repeated pattern inside its configured search, tests it on a customer-hash holdout half from the same synthetic extract, maps supported cells to an existing service template, and writes a local draft only after the base fails and the candidate passes its targeted regression check. The same record shows the boundary: this is not independent-source or causal confirmation, not yet connected to the original/enriched-history offline runner, and not proof of better customer outcomes. The demo is compelling because the engine can both act and explain why it must stop—not because we call separate proofs one end-to-end run.

## Small vocabulary for a new reader

| Term | Plain-language meaning |
|---|---|
| **Improvement Engine** | Pulso’s analysis and change-proposal service. It is not the customer-facing support agent. |
| **Signal** | A measured pattern worth investigating, such as a higher rate of an undesirable outcome in one comparable group. It is not proof of cause. |
| **Opportunity** | A signal plus a plausible, testable way to improve an outcome, with the evidence and missing links stated. |
| **Proposal / candidate** | A versioned draft change prepared for evaluation. It cannot affect customers just by existing. |
| **Agent Core** | A separate registry and runtime that validates and runs service-capability artifacts. Pulso proposes changes in its formats; Pulso does not reimplement it. |
| **Platform artifact** | A versioned service building block understood by Agent Core, such as a decision flow, agent configuration, tool definition, skill or knowledge package. It is a proposed configuration, not a customer record. |
| **Original bank snapshot** | The structured, synthetic banking tables supplied for the hackathon. “Original” means the base dataset, not live production data. |
| **Enriched interaction sample (internal name: E0)** | A second hackathon dataset with more detailed, generated interaction/event histories. It complements the original tables but is not an observed record of bank operations. |
| **Platform events** | Records of what the support software did—for example, a suggestion was shown, edited, discarded or followed. Current demo histories for these events are synthetic. |
| **Held-out cases** | Test examples kept out of candidate design, used to check whether results repeat on cases the builder did not tune against. |
| **Suppressed result** | A result hidden because it does not meet disclosure rules. Suppressed does not mean zero or “no problem.” |
| **PQR** | *Petición, queja o reclamo*: a customer request, complaint or claim recorded in the supplied data. |
| **Local run** | Software executed in a developer's test environment. It is not a production deployment, and “real Core locally” does not mean real customer service or bank systems. |
| **Aggregate cell** | One measured group in a metric table—for example, all eligible PQR records in one category and split. It is a group count/rate, not one customer. |
| **Baseline** | The existing version or comparison group used to understand how a candidate behaves differently. It must be named; it is not automatically a randomized control group. |
| **Percentage points** | The subtraction between two percentages: 62% versus 33% is a 29-point difference, not a 29% improvement caused by a change. |
| **Gate** | A versioned rule that must pass before a proposal can move to the next governed state. Passing a gate is not the same as getting business approval. |
| **V3** | The current canonical technical specification for the intended product. It describes target behavior and architecture; it does not prove implementation. |

The engineering appendix also uses repository/spec identifiers such as `U02` or `U15`. These are traceability labels for implementation slices, not product terms judges need to memorize.

## Evidence labels used throughout

- **Implemented code:** the named behavior exists in the current repository; this alone does not prove that a full product workflow ran.
- **Local run recorded:** a specific document records a local test or run. Read its setup and limitations; this is not a production result.
- **Synthetic:** generated or deliberately planted data. Useful for testing behavior, not a claim about real bank prevalence.
- **Designed in V3:** target architecture or behavior written in the canonical specification; not proof of implementation.
- **Open gap:** current evidence says the behavior is incomplete, blocked or unverified.

The status chapter gives the date of the evidence snapshot. Local run records are dated and described with their setup and limits; a repository entry alone is not proof that a demo has just been rerun.

## Infrastructure and observability

For the separate Terraform repository, reliability boundaries, and Langfuse’s role, see [Infrastructure, reliability and Langfuse](../infra/guide/infrastructure-and-observability.md). That chapter is pinned to a verified `infra` main snapshot and distinguishes versioned configuration from a deployed environment. Langfuse is an optional trace destination, not the business system of record; real cloud ingestion is not claimed as verified.
