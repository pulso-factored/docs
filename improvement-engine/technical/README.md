# Pulso Improvement Engine — technical reference

This is the engineering deep-dive that follows the product narrative in the [main guide](../README.md). It is for judges who want implementation detail, as well as engineers, data scientists, product engineers and operators who need to understand boundaries, contracts, runtime behavior, evidence and integration state.

If you are new to Pulso, first read the main guide's [PQR-status walkthrough](../02_product_rationale_and_architecture.md#v3-target-example-how-one-signal-becomes-a-governed-change) and [evidence card](../02_product_rationale_and_architecture.md#evidence-card-distinct-proofs-distinct-claims). Then return here to see how those moments map to source contracts, run state, detectors, Agent Core artifacts, evaluation, memory and operations. Worked examples in this appendix are marked as recorded local evidence, fake teaching values, or V3 target behavior; those labels are not interchangeable.

The chapters are written in English as technical reference material. They are not a replacement for the canonical V3 spec, the source repository's module documentation, or runbooks. The verified implementation baseline in this edition is a **documentation snapshot**, not a claim that the repository or deployed system has not changed since verification.

It describes two things side by side:

- **V3 target:** the intended end-to-end product contract, defined by [`docs/TECH_SPEC_PULSO_AUTOMEJORA_V3.md`](../../archive/source-record/2026-10-05/TECH_SPEC_PULSO_AUTOMEJORA_V3.md).
- **Current implementation:** code and recorded documentation on `pulso-factored/improvement-engine` `main` at `fc56b598b1be483a6b1eb7ee6fac0d9809c3b646` (commit #125), verified 5 October 2026. This is the reference snapshot for source links below. Historical run records identify their own branch/runtime provenance; they are not silently attributed to this code commit.

“Present in code” does not mean “connected and demonstrated end to end.” Each chapter uses these states explicitly:

| Label | Meaning |
|---|---|
| **V3 contract** | Required target behavior or architecture; may not be implemented. |
| **In code** | A module, schema, adapter, test, or infrastructure definition exists in the pinned snapshot. |
| **Locally demonstrated** | A run record reports execution in a local environment; its target, data class, doubles and limitations still apply. |
| **Not connected / not verified** | Components exist separately, but no evidence proves the complete path or runtime guarantee. |
| **External responsibility** | Owned by Agent Core, the customer-service platform, identity/security, or infrastructure rather than by the improvement engine. |

## Plain-language translator

| Engineering term | Read it as |
|---|---|
| **Signal** | A measured pattern that deserves checking; not yet an explanation. |
| **Opportunity** | A signal plus a plausible service mechanism that this system can actually change and test. |
| **Source / evidence class** | Which versioned dataset or event population supports the statement, and whether it is supplied, generated, assumed or operationally observed. |
| **E0** | Internal label for the additional generated/enriched interaction sample; it is not a real production event log. |
| **Flow** | A deterministic decision path made of explicit branches/nodes. |
| **Jev / `DecisionModelDef`** | Agent Core's structured model for a bounded classification/decision, not a general conversational agent. |
| **Template / Agent** | A reusable response shape / a more flexible reasoning component in the service platform. |
| **Baseline / candidate** | Existing behavior / proposed behavior, run against comparable cases. |
| **Holdout / confirmation split** | Cases deliberately kept out of proposal design, used to see if the result repeats. It is not automatically a real-world experiment. |
| **Draft / announce / publish / promote** | Stored proposal / notification boundary / registry publication / activation in a named environment. Each is a different step. |
| **`k=10` support floor** | At least ten contributing cases before an aggregate cell may be shown under that policy; it is not a statistical-significance or privacy guarantee. |
| **OpenTelemetry** | Standardized application logs/metrics/traces. Defined infrastructure or a configured dashboard does not prove the engine is emitting or monitored. |
| **Langfuse** | A destination for model/agent execution traces. It helps inspect what happened in a run; it is not the authoritative business-evidence store or proof of customer impact. |

When a term is used with a stronger meaning in the code, follow the linked module/contract definition. This short translation exists so readers can follow the architecture before opening those definitions.

## Reading path

1. [System architecture and ownership](01-system-architecture.md) — what belongs to the engine, its neighboring platform, Agent Core and infrastructure.
2. [Data, lineage and persistence](02-data-and-persistence.md) — source classes, E0, platform observations, artifact model and PostgreSQL records.
3. [Run lifecycle and asynchronous control](03-run-lifecycle.md) — triggers, jobs, leases, quotas, idempotency and recovery.
4. [Detection and evidence pipeline](04-detection-and-evidence.md) — deterministic metrics, exploratory reasoning, corroboration and opportunity links.
5. [Proposal and Agent Core integration](05-agent-core-integration.md) — output artifacts, Python bridge, registry/evaluation lifecycle and authority boundaries.
6. [Evaluation and sandbox](06-evaluation-and-sandbox.md) — scenario sources, baselines, gates, recorded results and what they do not prove.
7. [Memory lifecycle](07-memory-lifecycle.md) — ephemeral working memory, published revisions, use and revocation/forgetting.
8. [Security, configuration and operations](08-security-and-operations.md) — trust boundaries, resource limits, telemetry, local stack and delivery checks.
9. [Implementation map and open gaps](09-implementation-map.md) — component-to-contract map and current missing connections.
10. [Infrastructure, reliability and Langfuse](../../infra/guide/infrastructure-and-observability.md) — separate Terraform ownership, deployment-state caveats, trace egress, privacy boundaries and cloud-verification status.

## Ground rules for reading the implementation

1. The customer-service platform handles customer conversations, identity, tools that affect bank state, the four service layers, and live routing. The improvement engine observes approved evidence and proposes improvements; it is not a second customer-service runtime.
2. Agent Core is an external runtime and registry. The engine must emit native, versioned Core artifacts; an internal proposal format is not a replacement runtime.
3. The supplied bank tables are treated as read-only source data. Engine-owned state is additive and references source snapshots rather than changing the source schema.
4. Original bank data, generated/enriched E0 history, synthetic platform events, and outputs from a local simulator are different evidence populations. Never merge their rates or claims without preserving `evidence_kind` and source lineage.
5. A candidate artifact, a passing schema check, a passing sandbox gate, a human decision, a release, and a measured operational outcome are distinct states.
6. The database schema and queueing model in V3 are normative target design. They must not be inferred from a test double or the current in-memory reference reducers.

## Pinned source references

These links are pinned to the implementation snapshot above, not to a moving branch:

- [Engine README](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/README.md)
- [Open integration gaps](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/gaps/OPEN_GAPS.md)
- [Windows snapshot runner](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/local-e0-e2e-runner.md)
- [Bank-cell MAP1 run and candidate mapping](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/MAPPING.md)
- [Human-gated AGT1 new-agent lifecycle](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/AGT1_NEW_AGENT_PATH.md)
- [V3 specification in this workspace](../../archive/source-record/2026-10-05/TECH_SPEC_PULSO_AUTOMEJORA_V3.md)

This reference is a technical explanation, not an alternative specification. If an implementation detail appears to conflict with V3, the chapter should say so and identify whether the code is an interim slice, a deliberate simplification, or a gap; do not silently redefine V3.
