# 6. Why the system is built this way

Pulso's **Improvement Engine** is a service around a separate customer-service platform. It is not a second banking assistant and does not reimplement the software that handles customer conversations. Its job is to turn evidence about service behavior into proposals that can be checked, tested and governed.

## Why this product is not just a chatbot or a dashboard

A customer-facing assistant helps with the conversation happening now. A dashboard can summarize many past conversations. Neither alone repeatedly discovers an unrequested problem, checks competing explanations, changes the service capability, tests the change and carries evidence forward. Pulso's intended **learning loop** is: service evidence → explanation to test → versioned proposed change → comparison with today's behavior → governed next step. The loop creates value only when each step is connected and evidenced; the current implementation has separate pieces and local proofs, not one joined autonomous path.

The architecture is deliberately hybrid. Deterministic code owns arithmetic, data lineage, permissions, resource limits, versions and workflow state because those decisions must be reproducible. **Agent Core** is the separate service platform that defines and runs customer-service building blocks. Its **Jev** component makes structured decisions for a bounded question; a generative language model can explore open-ended explanations and candidate designs. A model may suggest; typed contracts and tests decide whether its output is acceptable. This allows flexible reasoning without making a model the privacy boundary, calculator, identity system or release authority.

## Architecture in plain language

```text
Supplied bank snapshot / generated enriched interaction history / platform events
                       ↓
          Rust improvement-engine core
     validate → analyze → record evidence → evaluate
                       ↓
       versioned change proposal in Agent Core's format
                       ↓
       separate service platform / human review
```

Rust is used for the engine's control and data boundaries: source validation, typed contracts, aggregation logic, immutable records, and explicit state transitions. This makes the safety-relevant parts easier to inspect and test. It does not mean every part of the product is already complete or written in Rust.

Agent Core is the separate platform that defines and runs service building blocks: decision Flows, Jev decision models, response Templates, AI Agents, Tools and related configuration. Pulso should propose changes in formats this platform understands. A file that passes a format check is not proof that the platform actually ran it. A Python bridge connects the Rust engine to this external platform; it is integration code, not a second Agent Core.

## Deliberate trade-offs

These choices follow from exploratory data analysis (EDA)—the initial investigation of the supplied synthetic banking tables—not from a preference for architectural ceremony. The data had millions of records and broad coverage, but often lacked links needed to establish cause or measure outcomes. The engine therefore needs broad analytical freedom, strict claim boundaries and a precise path from a finding to a proposed service change.

| Decision | Benefit | Cost or current limit |
|---|---|---|
| One Rust engine with explicit module boundaries | Easier to build, run and debug as one product while keeping responsibilities separate in code; current evidence does not justify many independently operated services | Some future scale boundaries may need separation; cross-language integration still needs end-to-end proof |
| Read-only input snapshots plus additive engine records | Preserves original data and makes analyses reproducible | A snapshot can be incomplete or stale and is not a live service feed |
| Bounded in-memory SQLite for the current query boundary; per-run DuckDB sandbox is the V3 target | A temporary query database avoids a shared mutable analysis service in the current local path; V3 gives each investigation its own richer SQL workspace | SQLite does not itself prove host/container isolation; V3 isolation, query budgets and concurrent throughput still require implementation and measurement |
| Immutable, versioned evidence and memory | Preserves why a finding or proposal existed and allows later correction/revocation without erasing history | More storage and lifecycle rules; retention and compaction still need operational design |
| Deterministic controls around flexible reasoning | Models can help interpret a pattern, while validators enforce provenance, shape, privacy and release boundaries | A valid control flow can still produce a weak hypothesis; model judgment must be evaluated separately |
| Real external runtime where available; clearly labelled stand-ins elsewhere | Tests the intended integration rather than inventing another service platform | Stand-ins cannot prove compatibility with a live runtime; some local paths are still unconnected |
| Separate Terraform repository from engine source | Infrastructure-as-code (Terraform files that declare cloud resources) can evolve without turning the product repository into an infrastructure monolith | Cross-repository configuration and deployment still need a verified operational path |

These choices are engineering judgments constrained by the product goal—not measured claims that Rust is faster, SQLite is safer, or this layout is cheaper in production. One modular engine avoids operating a separate service for every stage before workload evidence exists. Python remains at the Agent Core boundary because that external runtime is Python-based; this improves integration fidelity but requires a cross-language contract. Reusing Agent Core means proposals target the system expected to execute them, and also means Pulso can be blocked by its permissions, changing data formats, runtime availability or version drift—as the local bank-aggregate run illustrates.

### Why we did not choose the tempting shortcuts

- **“Use a language model to decide if the signal is true.”** Rejected as the sole gate: a confident explanation cannot establish a denominator, a valid link between records, event ordering or permission to use a source. Models can explore and challenge; deterministic validators and independent evidence decide whether a claim is admissible.
- **“Let the model write directly to the live service registry.”** Rejected: a draft, a validated candidate, an evaluation, a human approval and a release are different states with different authority. The exact reviewed content is identified by a cryptographic fingerprint (hash) throughout the process.
- **“Build a fixed tool for every analysis question.”** Rejected as the only analysis interface: it can limit exploration to questions anticipated in advance. V3 gives an investigator flexible, read-only SQL over a temporary copy that has been filtered and de-identified for that run, while code enforces data and resource boundaries.
- **“Turn every stage into a microservice.”** Deferred until scale evidence justifies its operational cost. A modular engine plus an explicit Python Agent Core bridge makes current lineage and control simpler to reason about.
- **“Treat generated histories as operating statistics.”** Rejected: they are excellent fixtures for testing detections and evaluation contracts, but their planted prevalence cannot estimate a real bank rate.

These decisions are not dogma. V3's thresholds and operating profiles are configurable and versioned. Deployment can change when measured workload, security review or external platform contracts require it. The invariant is evidence, authority and traceable lineage—not allegiance to a particular model or number of services.

## Which steps use code, models, and stand-ins today?

| Stage | What is evidenced now | What must not be inferred |
|---|---|---|
| Validate data and aggregate the platform-event test source | Deterministic Rust checks and configured aggregation over generated event histories | A live operations feed or a pattern discovered by a reasoning model |
| Local bank snapshot runner | Deterministic, repeatable descriptive execution over the original bank tables and generated enriched-history sample (called E0 in engineering files); no model-provider calls | Real service-agent behavior or a live Agent Core proposal |
| Documented synthetic complaint value-loop run | A local model and Agent Core runtime are described in the runbook; the artifact remains draft | A fresh reproducible run against today's full integration, or real-customer lift |
| Narrow Agent Core evaluation smoke | The run record says the Agent Core Jev classification component was real; the additional classifier used a keyword stand-in and proposals were manually originated | Autonomous problem discovery or a fully automated proposal/evaluation loop |

Where the implementation record does not identify a model call or execution by the external platform, this guide does not assume one. A **stand-in** is a simplified substitute for a real dependency; it must stay visibly labelled in tests and demonstrations.

## Memory is not just chat history

Pulso's improvement memory is a versioned record of findings, evidence, useful proposals, failed tests and reasons confidence changed. The current code includes temporary working notes and append-only published revisions, with receipts and revocation markers. These structures preserve revision history and record when a revision is withdrawn; by themselves, they do not prove that records survive storage loss or that an autonomous learning system reliably decides what to remember, forget or re-check. That requires explicit source tracking, confidence, review/expiry rules, durable storage guarantees and tests against reinforcing a mistaken claim.

## Observability serves two purposes

Operational logs, measurements and traces should help engineers see where an engine run stopped, what evidence it inspected and why it did or did not produce a proposal. Properly aggregated events from the separate service platform may also become evidence—for example, repeated service-agent retries or transfers to a person. In the current code, aggregate event sensors exist, but the engine has not yet been shown consuming a live event stream; the optional local telemetry backend has not been verified as a complete trace from start to finish.

The internal debug console is therefore a backoffice for operating and diagnosing the Improvement Engine. It is not the customer-support interface and not a replacement for the service platform's own dashboard. Current local evidence does not establish response time, work completed per unit of time under concurrent load, failure recovery or end-to-end telemetry; report these as unmeasured.
