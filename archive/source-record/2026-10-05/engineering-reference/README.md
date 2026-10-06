# Pulso Improvement Engine — engineering reference

**Audience:** engineers, data scientists, platform integrators, and operators who need to understand the engine's implementation and its boundaries. This reference is independent of the judge-facing packet in `final_docs/`.

**Purpose:** describe how the product is implemented, how a run moves through it, how to verify claims, and where implementation still differs from the canonical design. This is explanatory documentation, not a replacement for the V3 specification or the source repository's contracts.

**Publication state:** this first edition is a review draft under the shared workspace `docs/engineering-reference/`. It has not yet been synchronized to or published in `improvement-engine/docs/`; that promotion must be based on a fresh, verified repository default branch and must not be done from the stale local `main` checkout.

## Authority and evidence order

When sources disagree, use this order and make the disagreement visible:

1. The canonical target contract: [`../TECH_SPEC_PULSO_AUTOMEJORA_V3.md`](../TECH_SPEC_PULSO_AUTOMEJORA_V3.md).
2. The current `pulso-factored/improvement-engine` default branch and its executable code, schemas, tests, migrations, and module documentation.
3. Reproducible local run records, each limited to the exact command, data population, dependency profile, and commit they identify.
4. This handbook's prose and diagrams.

The source snapshot used for the current-state statements in this first edition is GitHub `main` commit `2e9ccd926e43294326e2dac8e7a9af2c47da3006` (verified 2026-10-05 19:45 UTC in the preceding repository audit). A live GitHub refresh was attempted for this revision but the sandbox denied the network connection. **Before relying on a current-state statement after this snapshot, refresh the remote default branch and revalidate its source links.** Do not treat the stale local `main` checkout as the source of truth.

## State vocabulary

Every capability claim must use one of these meanings:

| State | Meaning |
|---|---|
| `implemented` | Source code exists in the cited snapshot. State the exact component and behavior; this does not imply the complete product path is connected. |
| `locally verified` | A named command/test/run completed against named dependencies and data at a specific revision. Record its result and limits. |
| `partial` | Some required modules or boundaries exist, but the target flow or operational guarantee is not connected. Name both the working part and the missing edge. |
| `target` | Required by V3 but not established in the cited implementation evidence. |
| `external` | Owned by Agent Core, the customer-service platform, or the separately managed Terraform repository. |
| `unknown` | Evidence is insufficient. Never silently convert unknown to false, zero, or complete. |

`implemented`, `locally verified`, and `target` are not interchangeable. Every numbered flow should label the edges that are currently real versus specified, simulated, or blocked.

## Handbook slices

Each slice is independently reviewable, but the cross-links form one implementation manual. The planned sequence is an editorial dependency order, not an implementation priority.

| Slice | Subject | Required engineering questions | Status |
|---|---|---|---|
| 01 | Product boundary and repository/runtime map | Which process owns each responsibility? What runs together? What is external? Which source path implements each boundary? | First edition drafted below. |
| 02 | Inputs, data classes, lineage, and persistence | How do original data, E0, platform events, derived extracts, PostgreSQL, and object storage differ? What is immutable? | Planned |
| 03 | Run lifecycle and asynchronous control | What triggers work? How are jobs admitted, leased, retried, deduplicated, resumed, and stopped? Which guarantees are implemented versus target? | Planned |
| 04 | Detection, investigation, and evidence | Which computations are deterministic? Where may a model reason? How are hypotheses falsified and evidence linked? | Planned |
| 05 | Proposal artifacts and Agent Core boundary | Which native Core primitives can be emitted? How do bridge contracts, pins, receipts, and external authority work? | Planned |
| 06 | Candidate evaluation and sandbox | How are cases/splits/baselines built, candidates executed, and gates interpreted? What does a passing test not establish? | Planned |
| 07 | Memory lifecycle | What is scratch state versus published memory? How are use, supersession, invalidation, and forgetting represented? | Planned |
| 08 | API, debug console, observability, and security | How can an operator reconstruct a run? What is in logs/metrics/traces/events? Which controls protect data and commands? | Planned |
| 09 | Local development, testing, CI, and deployment | How does an engineer reproduce checks on Windows/Podman? Which CI gates exist? What does Terraform declare and what is not deployed? | Planned |
| 10 | Implementation traceability and known gaps | Which V3 requirement maps to which code, test, runbook, and open gap? What evidence is required to close each gap? | Planned |

## Documentation contract for every slice

Each slice must include:

1. **Scope and non-goals.** Identify the service boundary and any external owner.
2. **Current behavior.** Cite repository-relative paths, named symbols/schema/table/test where practical, pinned to a revision for moving sources.
3. **End-to-end flow.** Show producers, consumers, durable state, asynchronous boundaries, errors, retries, and observable output. Mermaid is welcome when it clarifies a real sequence or ownership boundary.
4. **Target versus present.** Map V3 requirements to `implemented`, `locally verified`, `partial`, `target`, `external`, or `unknown`.
5. **Verification.** Give exact commands only when checked at the cited revision; distinguish unit, integration, E2E, and environment-dependent tests.
6. **Failure and security semantics.** Include denial, timeout, duplicate delivery, crash/restart, stale version, tenant boundary, data minimization, or unknown outcome as relevant.
7. **Open gaps and decision links.** Point to canonical spec sections, repository ADRs, gaps, and dated runbooks; do not restate them as new authority.

Do not copy raw bank/E0 records, credentials, customer identifiers, model prompts, or unredacted telemetry into this reference. Prefer schemas, synthetic examples, digests, and reviewed aggregate evidence.

## Maintenance rules

- Write the handbook in English to align with the repository's technical documentation convention.
- Update the affected slice in the same change as code/contracts; record verification facts and limitations in the engineering journal.
- Review source links against the current GitHub default branch before any broad update. A pinned source link is evidence for a snapshot, not a promise that it is still current.
- When implementation changes, update the prior claim in place and retain historical run records only where they explain a still-relevant decision.
- A missing measurement or failed infrastructure gate is recorded as unknown/blocked, not papered over with a mock result.

## Reading path

Start with [01 — Product boundary and runtime map](01-product-boundary-and-runtime-map.md), then follow the table above. For detailed normative behavior, read V3 alongside the relevant slice. For the earlier judge-oriented narrative, use `final_docs/README.md`; it is intentionally not the entry point for engineering work.
