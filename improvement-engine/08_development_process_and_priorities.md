# 8. How the team builds and decides what to trust

These practices exist to protect the Improvement Engine's central promise: a problem must be discovered from evidence, not made to look true by a convincing explanation or demo. A green test is useful evidence for a specific behavior; it is not proof of customer impact or a complete product.

An autonomous improvement system must be tested as carefully as the changes it proposes. A green unit test can validate a small behavior; it cannot establish that the complete product is safe, integrated, or valuable to a bank. The engineering process therefore ties each claim to the level of evidence that actually supports it.

## The working method

```text
Understand the business question
           ↓
Define observable behavior and data contract
           ↓
Write a test that fails for the missing behavior
           ↓
Implement the smallest complete slice
           ↓
Run unit → integration → end-to-end checks locally
           ↓
Independent review of safety, evidence and edge cases
           ↓
Update technical documentation and known limits
```

The test-first loop is often called **red–green–refactor**: first show a new test fails for the expected missing behavior (red), implement until it passes (green), then simplify without changing that behavior (refactor). Independent reviewers try to find where the test or explanation claims more than it proves. Real local dependencies are preferred when practical; generated test data, fixtures and stand-ins (simplified substitutes for external services) must be labelled and never counted as real bank or platform execution.

## Examples of evidence-led engineering

- In the proposal-scoring exercise, adversarial review found language that could make model-assisted ratings sound like blinded human judgments. The team corrected the wording and added a regression check. The resulting agreement figures remain limited to a small generated corpus.
- In the generated interaction-history analysis, an unknown source state caused the pipeline to stop rather than silently classify rows. A conservative, versioned disclosure rule then withheld all output tables that did not meet the privacy threshold. This avoided publishing a root-cause story from insufficient evidence.
- In the generated scenario work, schema, provenance and privacy checks pass, while executions are explicitly marked **not run**. The documentation preserves that distinction instead of calling the scenarios successful agent tests.
- In the local candidate example, the baseline's regression failures and the candidate's gate results are reported separately, and the artifact remains a draft. Passing proposal checks is not confused with improved customer outcomes.

These are not proof that every subsystem is finished. They show the discipline the product needs: fail closed when input meaning is uncertain, preserve provenance, show denominators, and resist converting suggestive patterns into causal claims.

### How to report maturity without hiding the gaps

For every visible demo moment, say which level of proof it reaches:

| Demo claim | Evidence needed | Honest label when that evidence is absent |
|---|---|---|
| “The source was read correctly” | Versioned file list, schema/coverage check, repeatable content fingerprint | Not validated / source mismatch |
| “The system detected a pattern” | Named sensor, metric, support, denominator, comparison and repeatable result | Candidate signal / generated test only |
| “This is why it happened” | Reliable links between records, usable event timing, alternatives challenged and a corroborating mechanism | Hypothesis / unlinked / unresolved |
| “The proposal is better” | Exact Agent Core-compatible change, test cases fixed before evaluation, current/proposed version runs and declared outcome rules | Draft only / not evaluated / dependency blocked |
| “Customers or the bank benefit” | Authorized operation, linked outcomes, credible comparison and uncertainty | Not measured |

This vocabulary makes a demo more convincing, not less: viewers can distinguish an engine that produces polished prose from one that states exactly what it observed, what it tested and why it stopped.

## Priorities that follow from the evidence

1. Make one repeatable local path run from a data snapshot through an automatically detected pattern, investigation, proposed service change and evaluation result.
2. Verify the exact integration with the actual Agent Core runtime; keep every simplified substitute visibly distinct.
3. Run generated cases, including cases where a proposal should fail or be unsafe; compare the same predeclared cases against the current and proposed versions.
4. Connect events from the service platform and operational records from the engine itself, with privacy-preserving links between them.
5. Prove local resource limits, failure recovery and the human approval/release boundary before claiming deployment or customer impact.

This ordering favors a complete, inspectable slice over many disconnected features. The larger technical specification describes the intended full system; the current code and evidence must be presented at their actual maturity.

## Further reading in the repository

- `docs/TECH_SPEC_PULSO_AUTOMEJORA_V3.md` — intended product and technical contract; it describes the target, not a checklist of completed work.
- `docs/README.md` and current root `README.md` — repository orientation and current implementation pointers.
- `docs/gaps/OPEN_GAPS.md` — integration and operating limitations.
- `docs/dev/DEMO_LOOP.md` — documented synthetic local value loop, with the source type and limitations in its run record.
- `docs/data/opbench-lite/` — proposal scoring, generated scenarios and enriched-history exploratory analysis.
- `docs/BITACORA_PULSO.md` — technical implementation log and decisions.

The guide in this folder separates that V3 target from evidence in the checked code snapshot and dated local run records.
