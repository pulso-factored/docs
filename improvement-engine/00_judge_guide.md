# Pulso Improvement Engine: how the system learns to improve service

## The idea in one sentence

Pulso’s Improvement Engine looks across service evidence to find problems nobody explicitly asked it to look for, checks whether the evidence supports a useful explanation, and prepares a small, testable change to the system that serves customers.

It does not answer a customer’s chat. It improves the system that answers chats, handles calls, follows decision paths and routes work. Its promise is not “add more AI”; it is **turn repeated service experience into governed, testable improvement—continuously, with people involved where judgment or authority matters.**

This guide is for judges and technical readers who are new to Pulso. It starts with the product reason, then explains the evidence, the engine’s intended behavior, its implementation choices, what can be demonstrated today, and what is still a target. The technical reference linked at the end contains detailed contracts and module-level material.

## First, what do these words mean?

- **Improvement Engine:** the Pulso service that detects patterns across many service interactions and proposes improvements. It is not the customer-facing support agent.
- **Signal:** a measured pattern that deserves investigation. A signal is not a proven cause.
- **Opportunity:** a signal plus a plausible change the service can make and a way to test it.
- **Agent Core:** a separate platform that stores, validates and runs service building blocks. Pulso’s job is to discover and propose improvements using those building blocks—not to rebuild that platform.
- **Langfuse:** an optional observability service for following the technical steps of model and agent runs. It helps debug what the system did; it does not establish that a customer problem was solved or that a proposed change improved business outcomes.
- **Original bank dataset:** the synthetic banking tables supplied for the hackathon. “Original” means the supplied base dataset, not live bank production data.
- **Enriched interaction sample:** a second, generated sample with more detailed interaction histories. The project calls it **E0** in code and engineering notes; that is only an internal dataset label, not a product concept. It complements the original tables but is not a record of real bank operations.
- **V3:** our canonical product and technical specification. When a section says “V3 target,” it describes intended behavior, not proof that the behavior is already implemented.
- **Current main:** the code on the project’s GitHub `main` branch. The implementation snapshot used in this guide was checked against `main` at commit [`fc56b598`](https://github.com/pulso-factored/improvement-engine/commit/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646) on 5 October 2026. Run records are separately dated and may come from local test configurations; they are not automatically evidence from that GitHub commit.

> **How to read claims:** “Implemented” means code exists; “local proof” means a specific behavior was exercised in a local environment; “V3 target” means intended future behavior. These are different levels of evidence. All hackathon banking and enriched-history data described here are synthetic.

## Why build this instead of another chatbot or dashboard?

A support agent can resolve one person’s question. A dashboard can show that many people contact the bank about the same thing. Neither, by itself, closes the loop: *notice the recurring issue → check why it may be happening → change the right service capability → test the change → learn from what happens next.*

That missing loop matters because service automation does not automatically improve itself. A fixed decision tree may never cover a new situation. An AI agent may keep escalating a class of cases that another layer could handle. A useful support answer may exist in human practice but never become a tested, reusable capability. The Improvement Engine is designed to find those gaps in the combined evidence and turn them into proposals the service platform can evaluate and govern.

The intended beneficiaries are customers, who could encounter fewer repeated failures and clearer resolutions; operations teams, who could spend less capacity on repeatable friction; and product/service owners, who gain a traceable way to decide what to improve. Those are intended benefits, **not measured customer lift from the current demo**. To make the potential tangible without presenting it as a result, the worked EDA scenario estimates about **USD 7,032/year in service capacity value** under assumed handling-time and wage inputs; it is not cash savings or observed lift ([assumptions and competing scenarios](13_a_finding_becomes_a_testable_opportunity.md)).

## Where the product idea came from: the bank analysis

We began with exploratory data analysis (EDA)—an initial investigation of the supplied banking tables, not with a preselected “complaints bot” idea. The analysis covered synthetic customers, products, transactions, digital activity, service contacts, complaints, surveys and campaigns. It surfaced several possible business problems and, just as importantly, showed where the data could not prove why they happened.

One example stood out: the contact table contains **117,021 complaint-related rows**. **43.6%** have `was_resolved=True`, compared with **91.5%** of transaction-related contact rows. This is a concerning descriptive difference, but that field describes a contact row—not whether an entire complaint case was ultimately resolved or whether the customer had to contact the bank again.

The missing link matters. In the audited copy, the complaint table’s `origin_interaction_id` was empty for all **67,095** complaint records. So we cannot reliably connect a complaint to the interaction that caused it. Nearby digital errors and declined transactions also did not show higher contact rates in the conservative comparisons we ran. Campaign outcomes had no untreated comparison group. The dataset can show where to investigate; it cannot, by itself, establish those causal stories or the impact of a proposed fix.

That changed our product question. Instead of hard-coding “solve complaints,” we asked: **Can a system search across service domains, discover a problem without us naming it, challenge its own explanation, and propose only changes that can actually be tested?** This is the core of Pulso.

The PQR status example later in this guide demonstrates that reasoning discipline; it is not a claim that unclear complaint status was the root cause or the highest-value problem. PQR means *petición, queja o reclamo*—a customer request, complaint or claim.

## The engine’s core loop

### V3 target: discover, challenge, propose, test, learn

The following is the intended autonomous cycle. It begins from authorized data or a service-system signal, not from an operator telling Pulso which topic to investigate.

```mermaid
flowchart LR
  A[Authorized bank and service evidence] --> B[Automatic scan finds candidate patterns]
  B --> C[Check counts, data quality and comparison]
  C --> D[Investigate plausible explanations]
  D --> E[Independent challenge: try to disprove]
  E -->|Weak, unsafe or untestable| F[Record why; defer or stop]
  E -->|Evidence supports a bounded claim| G[Choose smallest useful service change]
  G --> H[Build a versioned Agent Core draft]
  H --> I[Test old behavior against candidate]
  I --> J[Show evidence, uncertainty and decision to operator]
  J --> K[Governed release decision]
  K --> L[Later evidence can update memory (V3 target)]
  L --> A
```

1. **Scan without preselecting the answer.** A schedule, approved new data snapshot, or approved platform observation may trigger a run. Deterministic measurements search authorized sources and compare meaningful groups. Each rate must carry its denominator, period, coverage and source version.
2. **Investigate with room to reason.** If a pattern is worth exploring, a bounded investigation can ask new read-only questions of an isolated, privacy-treated copy of the data. The goal is to find explanations and alternatives, not to let a model write to bank systems.
3. **Try to disprove the explanation.** A separate verification step checks join quality (whether records can be reliably linked), comparison groups, timing, missing fields, counterexamples and reasonable alternate assumptions. It can conclude “not enough evidence.” That is a successful safety outcome, not a failure to produce an answer.
4. **Choose a service mechanism, not a fashionable model.** If there is a controllable problem and a meaningful test, Pulso proposes the smallest suitable change. It may be a decision flow, a structured decision model, a response template, an agent, or a combination. Sometimes the right result is “no supported change yet.”
5. **Compare old and proposed behavior.** The same fixed test cases exercise the existing capability and the candidate. Tests can show that wording or routing behaves as specified; they do not automatically prove improved customer outcomes.
6. **Keep people informed and accountable.** Operators can see what the engine is doing, why it reached a conclusion, what it could not establish, and exactly what decision is requested. A consequential release is bound to the exact version reviewed; AI does not silently publish a change to customers.
7. **Learn without pretending every result is permanent truth.** V3 keeps saved, uneditable memory revisions and records which run used each one. Later authorized evidence may strengthen or contradict a finding; revocation prevents future runs from retrieving it, while its history remains auditable. This full autonomous learn/revoke loop is not yet verified in the current implementation.

### What is deterministic, and what uses AI?

This split is a central design decision. Code performs counting, data validation, permission checks, versioning, test execution and release gates so those controls are reproducible. Reasoning models help generate questions, compare explanations and draft candidate changes where open-ended reasoning is useful. Jev—Agent Core’s structured decision capability—is intended for bounded classification/decision tasks; a general language model is for broader investigation or synthesis. Neither is allowed to turn missing data into facts, bypass a gate, or authorize a release.

In V3, Pulso’s proposals use Agent Core’s own artifact formats and runtime rather than inventing a second agent platform. The output can be a Flow (a deterministic service decision path), a Jev decision model, a Template (reusable response content), an Agent, or a composition of these. Supporting skills, tools and knowledge may be part of the proposed artifact set when needed. Current local proofs cover only narrow portions of this path; see the evidence table below.

## How the evidence changes the design

The EDA pushed us toward four concrete product choices:

| What we learned from the data | Design response | Trade-off we accept |
|---|---|---|
| Many patterns are visible, but not every table can be joined reliably. | Keep where the data came from, its coverage, missing values and join confidence with each finding; allow “unknown” and “unlinked.” | Fewer dramatic causal claims, but a judge or operator can trace why a claim is limited. |
| A large count can be low value or outside the service’s control. | Gate on evidence, controllability and testability before ranking potential value, effort and risk. | The engine may defer a very large issue that it cannot safely change or evaluate. |
| A changed answer is not proof that customers benefited. | Use the same fixed test cases to compare existing and proposed service behavior, then keep outcome claims separate. | A passing test is reported as a bounded technical proof, not an ROI or NPS lift. |
| Service improvements can require different capabilities. | Reuse Agent Core artifacts and choose the smallest suitable one; do not make every improvement a new agent. | More coordination with the platform’s contracts, but no duplicate agent runtime. |

Pulso keeps three evidence classes distinct because they answer different questions:

- **Business events** describe what happened in the banking/service domain: a complaint was opened, a payment declined, or a customer contacted support.
- **Execution traces** describe what the software did while handling work: which decision path ran, which AI layer escalated, which tool was called, or where execution failed. They help engineers debug and may become an approved detector source when linked and governed, but are not outcomes by themselves.
- **Customer outcomes** describe whether the customer’s task was completed, the issue recurred, or the customer rated the service. They need a trustworthy outcome source; a contact-row status or successful tool call is not automatically proof of resolution.

This distinction shapes the internal debug console. Engineers should be able to inspect run stages, evidence and source coverage, model/Agent Core calls, blockers, errors and traces. It is a backoffice tool for the Improvement Engine, not a bank-customer feature. A console foundation exists today, but some views use fixture/sample data; the full live view connected to all runtime stages remains a target.

## One worked example—and exactly what it proves

The observed complaint-contact difference and the local template-drafting proof came from separate runs; the latter did **not** emerge from the former. Together they provide a useful walk-through of a synthetic-data signal, a missing join, and a later, independently configured test mechanic.

1. The scan sees that complaint-related contact rows have a lower row-level resolved flag than transaction contacts.
2. It considers possible explanations: unclear complaint status, digital errors, declined payments and differences in contact mix.
3. The audit finds the complaint-to-contact key empty. The available evidence therefore does not establish which interaction caused each complaint or whether status uncertainty drove repeat contacts.
4. Separately, a local bank-cell run used a **preconfigured hypothesis** to map five complaint-reason/channel groups to an existing complaint-status response template. It did not discover the template mapping from the missing join.
5. A targeted local regression proof checked that the proposed wording rendered the seeded status in those five channel targets. The output remained a draft.

This is a **local proof of a narrow template-testing mechanic**, not proof that Pulso autonomously discovered the status problem, not evidence that the status caused the complaints, and not a measurement of fewer calls, better complaint resolution or higher customer satisfaction. Those distinctions are part of the product: the engine should preserve a useful test hypothesis without upgrading it into a fact.

For the full numerical trail, scenario assumptions, competing hypotheses and source references, see [the worked EDA-to-draft example](13_a_finding_becomes_a_testable_opportunity.md). It also compares complaint service-capacity scenarios with activation and collections scenarios without treating unlike value types as directly comparable returns.

## What exists in code today, and what remains a target?

The current GitHub `main` snapshot demonstrates useful pieces. They are **separate runs and proofs**, not one complete journey through the engine.

| Evidence area | What is demonstrated | What it does not demonstrate |
|---|---|---|
| Original bank data + enriched interaction sample | An offline local runner reads/validates both datasets and produces descriptive or structured preparation outputs. | No model call or Agent Core execution in this runner; it does not autonomously produce and evaluate a bank change. |
| Generated service-system event histories | Sensor tests identify planted patterns in generated histories. | No live service-platform event feed, and no spontaneous real-operation finding. |
| Bank aggregate groups → response-template draft | A separate local route scanned aggregate bank cells, used a deterministic discovery/holdout split within the same synthetic extract, and produced five targeted template drafts. | Not independently confirmed by a second data source, not connected to the offline runner, not proof of root cause or customer impact. |
| Planted proposal demonstration | A separate synthetic scenario exercised model-assisted drafting and local Agent Core readback. | No bank-wide prevalence; its planted pattern is not independent detection. |
| Human-gated artifact lifecycle rig | A separate synthetic rig exercised a person evaluating and approving a draft through local staging and switching a test-only label for the active version. | No actual bank deployment or customer exposure; its seeded case did not prove the intended customer reply. |
| Memory, debug console and runtime foundations | Versioned-memory, run-state, activity and console capabilities exist at different contract or module boundaries. | No verified autonomous publish → later reuse → contradiction/forget cycle, nor one fully connected live debug view of all runtime stages. |

**The gap that matters most:** connect source ingestion, unforced discovery, evidence challenge, value/effort/risk choice, Agent Core artifact creation, meaningful evaluation, human decision and later outcome-based learning into one repeatable run. V3 describes that complete product. The current separate proofs do not yet establish it end to end.

Two different kinds of held-back checks appear in the evidence and should not be confused. A **detector holdout** checks whether a measured pattern repeats in a reserved part of the same source extract; here it is a repeatability check, not independent confirmation. A **candidate evaluation set** checks whether the changed artifact behaves as expected versus the existing artifact on declared scenarios. Neither, by itself, proves real-world customer impact.

## What has actually been built?

At a high level, the current code is divided by responsibility rather than presented as one magical black box:

| Component | Responsibility | Evidence boundary |
|---|---|---|
| Rust engine | Reads and validates source snapshots, applies bounded projections, stores versioned engine state, runs supported scans and exposes control/read foundations. | Code and contract foundations exist; the original/enriched-data runner and several detector/proposal experiments are separate paths. |
| Agent Core bridge | Adapts Pulso proposal/evaluation work to the external Agent Core runtime and its native artifacts. | Local composition and narrow draft/readback runs exist; this is not yet joined to the original/enriched-data runner as one autonomous path. |
| Evaluation components | Run named cases against a baseline and candidate and retain pass/fail evidence. | Specific local template and planted-case proofs exist; no test result establishes bank-wide customer lift. |
| Internal debug console | Lets engineers inspect run state, evidence, calls, failures and blocked stages. | Backoffice foundation exists with some fixture/sample views; full live runtime integration is open. |
| V3 autonomous loop | Connects discovery, challenge, opportunity selection, native artifact creation, evaluation, human governance and later memory/outcomes. | Specification target; not yet demonstrated as one end-to-end run. |

The detailed module-to-code map and open dependencies are in the [implementation reference](technical/09-implementation-map.md). This guide intentionally gives the judge the system shape without requiring familiarity with crate names, run IDs or internal ticket labels.

## Why these engineering choices?

- **Preserve the source data.** The bank dataset is read, validated and projected; Pulso does not rewrite its tables. New product records are stored separately and retain a trace of which source snapshot and transformations informed them.
- **Measure with deterministic code; reason with models.** This keeps arithmetic and authority predictable while leaving room for useful investigation. A model’s explanation is a hypothesis until checked.
- **Use an isolated working copy for analysis.** In V3, each investigation gets a disposable workspace with only approved fields and pseudonymized identifiers where possible. This reduces cross-run data exposure and makes concurrent investigations easier to bound. This is target architecture; the present code has narrower local query foundations.
- **Use the Agent Core runtime.** Pulso focuses on finding and improving service behavior. Agent Core owns how service artifacts are represented, validated and executed. We avoid duplicating that platform.
- **Version rather than overwrite.** Evidence, configurations, proposals, decisions and memory keep immutable revisions (saved versions that are not edited in place) and provenance (a trace of where information came from and what changed it). Memory-use records show which knowledge informed a run; revocation blocks future retrieval without erasing audit history. This makes it possible to explain what changed, reproduce a prior result and withdraw a claim without pretending old evidence never existed.
- **Make the autonomous system visible.** The operator experience is low-touch, not opaque. A business-facing opportunity view explains findings and decisions; an internal debug console is for engineers to inspect runs, traces and failures. The latter is backoffice support for the Improvement Engine, not a customer product surface.
- **Keep local engineering and cloud infrastructure distinct.** The service code and local Podman/LocalStack development stack belong to `improvement-engine`; deployable AWS infrastructure is maintained separately in `infra`. V3 describes staging and production foundations, but a design document alone does not prove a deployed service.

The detailed rationale, data model, security boundary, evaluation strategy and implementation evidence are in the [product and architecture chapter](02_product_rationale_and_architecture.md), [trade-off chapter](06_engineering_choices_and_tradeoffs.md), and [technical reference](technical/README.md).

## What would make the demo feel like the product?

The key moment is not simply a chart lighting up or an AI typing a confident explanation. It is a traceable progression:

**No one names the complaint issue → the engine detects a pattern across its allowed search → the evidence review exposes what is and is not linkable → the system proposes a narrowly scoped service artifact → a test distinguishes it from existing behavior → the operator sees the evidence and exact requested decision.**

Today, that progression is split across local demonstrations, so the demo should show each boundary honestly. The product becomes truly magical when this discovery-to-proposal-to-evaluation path runs autonomously as one connected system and later evidence shows whether the improvement helped. We do not claim that the current dataset or tests have already proved customer lift.

## Further reading

**Product-and-engine story:**

1. [Why the engine exists and how it is designed](02_product_rationale_and_architecture.md)
2. [What the bank evidence says—and cannot say](03_data_provenance_and_evidence.md)
3. [One worked example, from signal to bounded draft proof](13_a_finding_becomes_a_testable_opportunity.md)
4. [How Pulso chooses what to investigate and improve](12_how_pulso_chooses_what_to_improve.md)
5. [What is implemented, what is demonstrated, and what remains open](07_current_status_and_pitch.md)
6. [How memory learns, changes and forgets](technical/07-memory-lifecycle.md)

**Technical reference:** [architecture](technical/01-system-architecture.md), [data and persistence](technical/02-data-and-persistence.md), [run lifecycle](technical/03-run-lifecycle.md), [detection and evidence](technical/04-detection-and-evidence.md), [Agent Core integration](technical/05-agent-core-integration.md), [evaluation](technical/06-evaluation-and-sandbox.md), [security and operations](technical/08-security-and-operations.md), and [implementation map](technical/09-implementation-map.md).

**Infrastructure and observability:** [how the separate Terraform repository supports the engine, where Langfuse fits, and what remains unverified](../infra/guide/infrastructure-and-observability.md). Langfuse is an optional model-execution trace view—not business-outcome evidence—and the guide deliberately does not claim successful real-cloud ingestion.

**Primary sources:** [canonical V3 specification](../archive/source-record/2026-10-05/TECH_SPEC_PULSO_AUTOMEJORA_V3.md), [integral synthetic-bank EDA](references/eda/factored_banco_eda_integral.pdf), [contact and experience EDA](references/eda/factored_contacto_experiencia_eda.pdf), [earlier EDA storytelling report](references/eda/factored_eda_storytelling.pdf), and the [pinned current-main implementation map](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/IMPLEMENTATION_STATUS.md).
