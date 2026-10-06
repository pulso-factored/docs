# 1. The product problem and Pulso’s value

## A service can be automated—and still need to keep improving

A bank can launch a digital support flow and still leave people repeating the same checks, getting an unclear answer, or handing a customer between teams. A dashboard may show that a metric moved, but it usually does not produce a safe, testable change to the service. A customer-facing AI agent can handle an individual interaction, but it does not by itself learn which recurring service problems are worth fixing across many interactions.

Pulso’s Improvement Engine is intended to close that loop. It studies what happened, distinguishes a real pattern from an attractive anecdote, proposes a change to the service system, checks that change, and explains what evidence supports it. Its value proposition is **continuous improvement of the service**, not simply faster generation of customer replies.

## The boundary: three different jobs

```text
Customer asks for help
          │
          ▼
Customer-service platform ── (intended) handles the case, checks identity, calls permitted tools,
          │                    verifies the result or hands the case to a person
          │ (intended) emits minimized operational events
          ▼
Pulso Improvement Engine ──── detects patterns, investigates, proposes a change,
          │                    evaluates it and shows evidence / review decisions
          ▼
Agent Core platform ───────── stores, validates, evaluates and runs service capabilities
                               that Pulso proposes (separate system; not reimplemented here)
```

This diagram describes the intended boundary, not a currently connected production data flow. The customer-service platform owns the conversation with a person and operational actions. Pulso owns the improvement loop and its internal debugging/oversight view. Agent Core is a separate platform that stores, checks and runs the service configurations Pulso proposes. A versioned configuration in Agent Core is called an **artifact**. A report, a proposal, or a passing format check is not the same thing as a live customer-service result.

## What the engine can improve: the four service layers

The neighboring customer-service platform may resolve an incoming request through four increasingly flexible layers. These are **platform capabilities that Pulso may help improve; Pulso does not run the customer-facing conversation**:

1. **Decision flow:** a predefined tree checks known facts and performs approved deterministic steps. This is a good fit when the correct path is stable and can be expressed as rules.
2. **Structured decision model (Jev):** Agent Core's versioned capability for a bounded classification or decision. It is not a general-purpose conversational agent; it is one of the service building blocks Pulso may propose changing.
3. **Generative AI agent:** reasons over context and approved capabilities for cases that cannot be safely captured by a fixed tree or bounded classifier.
4. **Human specialist:** receives work when authority, risk, ambiguity, or system limitations require a person.

The engine's opportunity is to notice a repeated failure in one of these layers, identify what mechanism may be changeable, and propose the matching Agent Core artifact. A repeated decision-tree miss may call for a Flow change; inconsistent classification may call for a Jev model revision; unclear customer wording may call for a response-template or AI-instruction (prompt) adjustment; an uncovered complex case may call for an agent. A measured pattern alone does not choose among these—the investigation must link evidence to a service component Pulso can actually help change.

### One service issue, four possible interventions

Suppose a customer asks whether a complaint is still open. The system should not jump straight from “many open complaints” to “build another chatbot.” It asks where the friction occurs:

| Evidence points to… | Smallest plausible intervention | What must be tested |
|---|---|---|
| A known status check is missing from a deterministic branch | Add or reorder a **Flow** node that retrieves and explains the verified status | Correct branch selection, safe identity gate, correct status and no false “resolved” message |
| Requests are being assigned to the wrong category | Revise the **Jev model definition** used for bounded classification | Compare category assignments and critical mistakes on a fixed set of cases kept out of development |
| The right status is available but the response is unclear | Revise a **response template or prompt** with explicit status wording | Correct status insertion, supported languages, no invented status, and regression checks on other complaint cases |
| A case needs flexible reasoning across several approved capabilities | Improve an **Agent** or its skill/context | Task completion, tool-use correctness, refusal/escalation and safety suite |

These are intervention examples, not findings from the supplied data. In Agent Core's technical schema, the versioned definition of a Jev model is called `DecisionModelDef`; it is not an agent. A **Flow** is a versioned decision path made of explicit steps and branches. A **response template** is reusable wording with named fields that must be filled from verified data. These terms describe the service components Pulso may change; Agent Core owns their storage and runtime. The Improvement Engine decides whether the evidence supports proposing a change. A person still controls any customer-serving release.

## How that could create value

```text
Repeated service friction
        ↓ hypothesis about mechanism
Change to a controllable capability
        ↓ tested against the current version
Operational proxy (repeat contacts, safe resolution, handoff, handling time)
        ↓ only with valid outcome links and comparison
Business outcome (effort/cost, satisfaction, retention, or revenue)
```

This is the value chain we intend to measure, not a result already achieved. For example, fewer repeated contacts might reduce handling effort; that does not automatically prove lower cost unless the eligible population, saved handling time and cost assumption are measured. **NPS (Net Promoter Score)** summarizes promoters minus detractors; **CSAT (customer satisfaction)** is a rating of a specific interaction. No current run establishes financial savings, NPS/CSAT lift or production impact.

### How we compare value without pretending it was measured

The bank EDA and its scenario appendix let us reason about order of magnitude, not book a result. The integral EDA modeled, for example, about **USD 7,032 of complaint-handling capacity** in a 12-month three-country scenario versus about **USD 7,954 of gross contribution** in a selected activation scenario before messaging/fixed costs. The former is staff capacity under assumed time and wage values—not automatic cash savings. The latter depends on assumed activation, contribution and capture—not incremental sales proven by a control group. These estimates are from different mechanisms and do not establish which change wins.

| Value step | Evidence or input | What the number can answer | What it cannot answer yet |
|---|---|---|---|
| Size the observed opportunity | Eligible contact rows, complaint flags, response/service-level-agreement (SLA) fields, customer/product groups | “How much activity is visible under this definition?” | “How much can an intervention prevent?” |
| Estimate reachable cases | Share with a controllable, testable service path | “How many cases could this particular artifact affect?” | “Will the artifact be used correctly?” |
| Convert to proximal benefit | Avoided repeat handling, shorter handling time, safe resolution, supported activation | A scenario range using named assumptions and country-specific costs | Causal lift without candidate-vs-baseline operational evidence |
| Subtract effort and risk | Build/change cost, model/runtime cost, messaging, safety/routing risk, reversibility | “Is this a plausible next test relative to effort?” | A realized effect on the bank's profit or loss |

For a priority decision, compare **expected value range × evidence strength × controllability** against **implementation effort × risk**. PQR is the Spanish abbreviation for a *petición, queja o reclamo*—a customer request, complaint or claim. Avoid adding overlapping pools: one person can generate a contact, a PQR, a digital event and a survey response, so summing their row counts can count the same journey more than once. The [EDA origin chapter](02_product_rationale_and_architecture.md#the-origin-story-what-the-eda-taught-us) explains the assumptions and the attribution gaps behind those example numbers.

For an actual value estimate, the engine would carry each link as a separate quantity: affected cases × share eligible for the change × expected mechanism success × value per successful case − implementation/operation cost. Until outcome linkage and a credible effect estimate exist, the result is a scenario range with named assumptions, not booked savings. “The flow test passed” and “the bank saved money” are different claims.

## What a person would see

**V3 target experience:** an operator or product owner opens the Improvement Engine's internal control panel and sees an automatic run unfold as a timeline: approved data snapshot selected → signals ranked → investigation and counter-evidence → proposed-change comparison → baseline/candidate tests → blocked, revise, or approval requested. They can inspect why a finding exists, correct governed context, pause unsafe work, or approve the exact tested version when authorized. The aim is few human interruptions with high visibility—not a silent autonomous system.

**Current evidence:** code contains a debugging-panel foundation and a read interface that scopes each run's activity to the bank/customer organization it belongs to (a tenant). The complete live connection from the Rust engine through its API to that panel is not yet proven; some views use sample or simulated records. Do not mistake the target experience for a fully implemented user journey.

## Where our work fits in the hackathon

The hackathon brief calls for a focused banking customer-service system supported by data, safe handling of ambiguity and a credible evaluation. This packet documents our team's scope: the **Improvement Engine**, a subsystem behind that service.

The neighboring customer-service platform owns conversations and account-affecting actions. Pulso's engine is designed to learn from evidence across many cases and propose tested changes to that platform. This is not a claim that the engine alone replaces or fulfills the entire customer-facing hackathon workflow; it explains the improvement mechanism that makes the wider service capable of evolving.

## The product hypothesis

If the service collects reliable, privacy-minimized evidence about repeated work and outcomes, an engine can help the bank prioritize an improvement that humans might otherwise miss or implement slowly. The hypothesis is that this can reduce repeat effort and improve safe resolution. That is a plausible value mechanism—not yet a measured financial or customer outcome for Pulso.

The system is valuable even when it says “not enough evidence.” A reliable stop prevents the bank from spending effort on a false pattern or deploying a plausible but ineffective change.

## Sources and where to verify

- Hackathon kickoff, pp. 10–15, 18, 20: focused end-to-end workflow, required behaviors, evaluation rigor, disciplines, operation and submission requirements.
- Problem Statement, pp. 1–6: safe service behavior, held-out evaluation, privacy boundaries, permitted architecture choices, and honest metrics.
- Canonical design: [`TECH_SPEC_PULSO_AUTOMEJORA_V3.md`](../archive/source-record/2026-10-05/TECH_SPEC_PULSO_AUTOMEJORA_V3.md), especially §§1, 7, 16–18 and 22–25.

The briefs are evaluation requirements; they are not evidence that Pulso has implemented a particular feature. Implementation status is consolidated in [chapter 7](07_current_status_and_pitch.md).
