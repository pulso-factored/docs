# 7. What exists today—and what the product still needs

**Code snapshot checked:** GitHub's `main` branch on 5 October 2026, commit `fc56b598b1be483a6b1eb7ee6fac0d9809c3b646` (commit #125). “On main” means present in that shared code snapshot. A **local run** is an exercise recorded from a particular setup; it may have used another code branch, Agent Core version or generated test data. A test, a demo record and a production capability are different evidence.

**V3** is the current product and technical specification: it describes what the Improvement Engine is intended to do, not everything already present on `main`. “E0” is an internal engineering label for the separate generated interaction-history sample; it is not a product feature or real bank history.

## The honest answer in three sentences

Pulso has important building blocks for a governed improvement engine: Rust code for validating data and preserving evidence, a separate Python connector to Agent Core, tests of event-based measurements, evaluation and memory components, and an internal debug-console foundation. Recorded local exercises include a narrow path from aggregated bank data to a tested response-template draft and a separate, human-approved new-agent lifecycle in a sandbox (an isolated test setup). The offline runner for the original bank tables and generated enriched-history sample remains separate from those Agent Core paths. Pulso does **not** yet demonstrate one continuously autonomous, fully connected, production-ready cycle that discovers an unprompted issue from those sources, proves customer impact and releases a change to the live service.

That is not a reason to dilute the idea. It is the status boundary a judge needs in order to understand what has been built versus what V3 specifies next.

## Capability map: present, connected, and still missing

| Product capability | Present in the checked snapshot | What is not yet proven |
|---|---|---|
| Protect source data and preserve its history | Rust checks validate source files and record which snapshot and fields were used; foundations for immutable (unchangeable) evidence records | Continuous live data intake, durable feed and complete production policy enforcement |
| Explore data for patterns | A restricted typed query path backed by temporary in-memory SQLite; a separate deterministic runner for the original bank tables and generated history | V3's flexible per-investigation DuckDB workspace with enforced isolation; broad model-assisted investigation connected to the source runner |
| Detect service problems | Seven families of aggregate measurements over generated service-platform events, with detector tests | Connection from these sensors into a scheduled/on-demand engine run; verified event meanings, a real event feed and historical backfill |
| Form and evaluate a change | Python connector and versioned contracts for Agent Core; narrow local checks and a documented synthetic draft run | Finding from the source runner → supported Agent Core change in one full path; independent evaluation beyond the same generated source |
| Learn across runs | Temporary working memory, immutable published revisions and records that mark revisions withdrawn | Proven durable, autonomous reuse, contradiction and forgetting across fully connected runs |
| Show what the engine is doing | An organization-scoped endpoint for reading run activity and foundations for an internal Node/TypeScript console | Live connection between the Rust engine API and console; some views still use example/test data |
| Operate reliably | Rust checks, isolated PostgreSQL database-change checks, and local container/AWS-service test configuration | Verified Windows container-stack run, all-language checks in a clean environment, deployed private access/secrets/alarms, recovery and load tests |

The proposal row needs an important nuance: the latest checked documentation records **narrow successes**, not only blockers. A recorded mapping run grouped the supplied bank data into aggregate cells and produced response-template drafts for complaint-related findings (*Queja* means “complaint”) across five channels. A separate synthetic, human-approved new-agent exercise moved a draft through approval and a local staging/test-active lifecycle; its internal test alias was named `prod`, but it did not affect a production system. These paths used separate setups and are not joined to the deterministic runner for the original bank tables and generated enriched history. The new-agent exercise also exposed an unresolved mismatch: a technical-support finding was mapped to an incorrect-charge test case.

## A demo narrative that matches the evidence

1. **Show the source runner:** original banking tables and a separately generated sample with richer interaction histories (called “E0” in engineering files) are processed offline with repeatable rules. Describe the output as counts and repeated patterns—not as a model-driven proposal.
2. **Show the bank-aggregate iteration, not a flattened success/failure:** start with the first four-finding attempt and its permission, artifact-mapping and model-availability blockers. Then show how a later run associated groups defined by complaint reason with an existing response template and used a test where the old wording failed but the proposed wording passed to produce five local drafts. The finding remains an association; no customer outcome was measured.
3. **Show the proposal-mechanics exercise separately:** 350 generated summaries contain a deliberately inserted difference in complaint-status rates. A model-assisted response-template candidate passes a narrow test and is read back from a local Agent Core registry as a draft. It demonstrates response to a known test pattern, not discovery from customer records.
4. **Show the human-gated new-agent lifecycle:** the synthetic test setup demonstrates a person reviewing and approving a draft, then moving it through local test staging to an active test alias. Pause on the mismatch: a technical-support finding was associated only with a seeded incorrect-charge case type, so the exercise did not prove correct routing or a useful customer reply. No bank production environment was changed.
5. **Show the restraint case and source runner:** all eight aggregate views of the generated enriched-history sample were withheld by disclosure controls; the offline runner processes both source datasets deterministically but makes no model or Agent Core calls. Neither “withheld” nor “runner completed” means a problem is absent or solved.
6. **Close with V3:** connect broad discovery across bank and service-platform evidence, investigation, native Agent Core change proposals, reproducible comparison with the current version, human-authorized release and later outcome/memory feedback. That complete self-improvement loop remains the build target.

These six views must be presented as separate records unless a new run record proves they were part of the same run. In particular, tests of seven service-event measurement families are not the same as the bank-aggregate pattern test and are not yet connected to the autonomous reasoning path.

### What the internal console should make obvious

Pulso's operator surface is a **backoffice for the engine**, not the customer-support chat and not the service platform's agent-management screen. A useful demo should let someone open a run and answer: What triggered it? Which source/configuration versions did it pin? What did the detector measure? What did the verifier challenge? Why was a proposal made, withheld or blocked? Which exact artifact and test suite were involved? What needs a human decision? What is still unknown?

The intended visual is a live run timeline with evidence panels and a candidate diff, plus resource/trace detail for engineers. That is the “magic”: an autonomous system doing the work while leaving a legible trail. The current console has useful foundations but is partly fixture-backed and not fully connected to the Rust execution API; do not present it as a live view of the entire system until the joined path is verified.

#### One finding, as an operator would inspect it

| Timeline card | What should be visible without opening raw customer data | Example state / meaning |
|---|---|---|
| Run accepted | What started the run, which organization/source/configuration version it uses, time cutoff and run identifier | “Accepted” means queued, not completed |
| Signal measured | Metric name in plain language, population, numerator/denominator, period, comparison and source class | A candidate pattern to investigate, not “root cause found” |
| Evidence challenged | How many records could be linked, missing fields, alternative explanations and whether a separate subset repeated the pattern | “Unlinked” means the source cannot connect records; it does not mean the relationship is false |
| Change selected | Why a decision Flow, Jev model, response Template, AI Agent or no change fits; alternatives rejected; exact diff and version fingerprint | A dependency block means the engine could not test due to a missing service, permission or supported mapping |
| Candidate evaluated | Named test suite, target cases, safety-check cases, current-version result and proposed-version result | “Not evaluable” means no verdict; it is neither a pass nor proof that the idea failed |
| Human decision | One precise requested action, reviewer, exact proposed-version fingerprint, environment and rollback reference | Draft approval is distinct from publishing and activation |
| Outcome/memory | Later linked observation, coverage, comparison design and which memory revision informed the run | No outcome record means “impact not measured,” not zero impact |

The product experience should require little routine operator work but never hide what the engine is doing: people are interrupted for a consequential decision or missing expertise. Engineers can inspect every stage, model or Agent Core attempt, retry, cost, event receipt and failure reason. The existing Node/TypeScript console and run-activity view provide foundations; until connected to the live engine API, any example or stand-in data must be labelled visibly.

## Why this is valuable before it is fully autonomous

The differentiator is not “AI writes a better reply.” The target value is an engineering system that can find repeated operational friction, explain what evidence supports it, create a change in the platform's own format, test that change before release, and preserve what it learns. A useful engine must also know when to stop because evidence, permissions, runtime availability or evaluation are missing.

The current implementation demonstrates meaningful safety and integration foundations—versioned evidence, bounded analysis, explicit blockers, tested candidate drafts and a locally exercised human-gated lifecycle. The value hypothesis remains plausible, but no present record measures fewer complaints, higher satisfaction, shorter handling time, savings or revenue. The EDA’s scenario values are assumptions used to compare possible mechanisms, not realized results; see [the origin and economics discussion](02_product_rationale_and_architecture.md#the-origin-story-what-the-eda-taught-us).

## Highest-value remaining integration steps

1. Compose the original and enriched-history source runs with the Rust detector, evidence dossier, independent verifier and non-hardcoded opportunity selection.
2. Connect candidate generation through the actual Core bridge, including typed errors, contract version pinning and an exact candidate-hash lineage.
3. Freeze discovery/confirmation scenarios, execute both baseline and candidate, and make evaluation results/reasons visible through the debug console.
4. Connect a verified platform event feed while keeping its operational events separate from the engine's own logs/traces.
5. Complete durable job and memory lifecycle behavior, restart/concurrency tests, local stack/CI, and deployment/alert runbooks before claiming operational readiness.

## The pitch

**Pulso is building the improvement engine behind a banking service: it turns repeatable service evidence into governed, testable changes to the service's own capabilities—and makes both its reasoning and its limits visible.** Today we can show the foundations and separate local proofs; the fully joined autonomous loop is the goal we are working toward, not an impact claim we pretend has already happened.

## Primary evidence

- [Pinned implementation inventory](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/README.md)
- [Pinned implementation status](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/IMPLEMENTATION_STATUS.md)
- [Pinned open-gap ledger](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/gaps/OPEN_GAPS.md)
- [Local original/E0 snapshot runner](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/local-e0-e2e-runner.md)
- [Bank-cell mapping and draft record](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/MAPPING.md)
- [Synthetic/local demo-loop record](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/DEMO_LOOP.md)
- [Synthetic human-gated new-agent lifecycle record](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/dev/AGT1_NEW_AGENT_PATH.md)
- [V3 target spec](../archive/source-record/2026-10-05/TECH_SPEC_PULSO_AUTOMEJORA_V3.md)
