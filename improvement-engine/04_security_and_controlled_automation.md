# 4. How Pulso keeps improvement proposals under control

Pulso is designed to investigate and suggest changes; it must not silently change how a bank serves customers. The V3 design separates four permissions: **read approved evidence**, **draft a change**, **test it**, and **authorize a release**. The current local code demonstrates only parts of this boundary; the production identity and release path are not complete.

```text
Read approved snapshot
        ↓
Analyze within bounded, read-only workspace
        ↓
Create a versioned draft artifact
        ↓
Run checks and compare with a baseline
        ↓
Human/platform approval is still required for release
```

## Controls represented in the current code

- **The supplied bank tables stay read-only.** Analysis reads an approved snapshot and does not write back to the organizer's source data.
- **Data exploration is constrained in code.** The current investigation workspace accepts only a defined set of read-only query shapes over an isolated, in-memory SQLite copy; callers cannot submit arbitrary SQL or write to the source tables. Its query interface offers no network-request operation. This limits what the application interface can do; it is not proof that the host process is isolated from the network.
- **Changes and evidence are versioned.** Source definitions and proposed service artifacts have immutable-version foundations. Memory changes are appended as revisions rather than overwriting history. A revocation record (“tombstone”) can make a revision unavailable to future runs while preserving an audit trace.
- **Working memory cannot release a change.** The investigation's scratch workspace exposes only typed operations over authorized content; through that interface it cannot publish memory, alter source data, request arbitrary host files or make network calls. This is an application boundary, not proof of operating-system or container isolation.
- **A draft is not a release.** Candidate artifacts and test results do not authorize the customer-service platform to use the change.
- **A debugging console is an internal engineering view.** It is for understanding engine runs, failures, evidence and state—not a customer-facing support interface.

These are boundaries implemented in specific modules and tests on the pinned code snapshot. They are not a claim that a deployed bank system has passed a complete security audit.

## What a safe action would require in a complete product

The hackathon brief expects the customer-service platform to use trusted identity, permission checks for each record, limited action tools, verification of the returned result, safe refusal when evidence is insufficient, and escalation to a person. A customer/account number typed into a message is not proof of identity; a model's words are not an authorization check. Any future customer-serving action must go through the platform's approved tool and be checked against an authoritative result before the system reports success. These requirements belong to the customer-service platform; Pulso detects and proposes improvements to that platform, it does not perform the banking action.

The current Improvement Engine is not the banking action executor. It does not move money, approve credit, change real customer records, or release a customer-facing candidate. Where the full platform is absent, a contract-shaped stand-in must be visibly identified as a stand-in.

### The last mile is a separate authority decision

| What the engine has done | What is still required before customers can be affected |
|---|---|
| It drafted a versioned candidate | Agent Core validates the exact native artifact (the platform's own format) and stores it as a draft |
| The candidate passed a named local test suite | An authorized reviewer sees what changed, the evidence, uncertainty, safety cases and rollback path |
| A reviewer approved a specific candidate fingerprint (content hash) | A trusted release command publishes that exact fingerprint for the correct customer organization and environment |
| A release is active | The serving platform emits measurable, privacy-approved outcome events; Pulso evaluates them before claiming impact |

If a request times out after an external change may have happened, the engine must check the operation's status before retrying, to avoid applying it twice. If an HTTP request receives “accepted, still in progress” (`202 Accepted`), the console reports that state—not “released.” If identity, permission, or exact-candidate checks fail, the engine stops. This lets Pulso prepare improvements proactively without giving a model authority to release them.

## Material limitations today

The current code does not establish production identity and permissions, one complete path from bank/enriched sample through the Rust engine into Agent Core, gradual exposure to real customers, or end-to-end operational telemetry. It does include narrow local Agent Core calls, bank-data-to-draft proofs, and a human-approved lifecycle simulation: a technical-support finding was tested against a rig prepared only for incorrect-charge cases. The simulation exercised approval and version-state mechanics but did not prove correct routing. Its local environment included a label called `prod`; this was a test alias, not a production deployment. The documented full container smoke has not been verified on Windows. Public/cloud entry, runtime secret binding, network-egress enforcement, and operational alarms remain incomplete. A local test must not be read as evidence that live customer data or bank credentials were used.

## What to demonstrate

Use a generated test case to show the difference between a proposal and an authorized action: the engine creates a draft, runs checks, and leaves it pending rather than applying it. A useful adversarial case is one with insufficient evidence or an unsafe requested change; the expected behavior is to refuse, suppress, or request authorized review. Report the number of cases tested and their source. Passing a small fixture suite is evidence about those fixtures, not proof of zero risk.
