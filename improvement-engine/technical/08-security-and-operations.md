# 8. Security, configuration and operations

## 8.1 Trust boundaries

| Boundary | Security purpose | Current status caveat |
|---|---|---|
| Source snapshot → treated projection | Preserve read-only original, minimize fields, bind schema/digest/cutoff | Validation/projection modules exist; end-to-end source governance still depends on deployment and tested adapters |
| Tenant → query workspace | Prevent cross-tenant reads and host escape | Current embedded SQLite query AST is bounded; V3 containerized DuckDB sandbox is target, not current capability |
| Rust engine → Python Core bridge | Authenticate service identity, tenant/purpose/audience, validate DTOs and idempotency | Contract and local auth code exist; real deployment identity/secret binding is not established |
| Model provider / JEV | Prevent unapproved data egress and constrain spend | Model permissions and data-class policy must be explicit; no provider capability implies source authorization |
| Engine → Agent Core registry | Separate draft/evaluation from privileged publish/promotion | Bridge has effect semantics; live production integration and approval binding remain incomplete |
| Debug console → engine state | Read-only or narrowly authorized operator controls; redact sensitive traces | Console contains fixtures/stand-ins; Rust control API not published in the pinned snapshot |

V3 requests per-run disposable data workspaces and strong egress isolation. The current SQLite AST interface is not equivalent to OS/container isolation. Never mount the host source root, Podman socket, credentials, unrelated tenants or other run directories into an analysis container. If a model provider receives any source-derived content, only fields and evidence classes explicitly allowed by the active versioned run config may be sent.

## 8.2 Configuration and change control

Limits and settings—support thresholds, windows, detector versions, budgets, concurrency, timeouts, model profiles, data-egress policy, retention, evaluation gates and trigger cadence—must be configuration revisions, not hidden constants. Each run pins the exact revision/digest. Config updates are immutable and auditable; rollback means selecting an older approved revision or creating a new revision, not mutating historical configuration.

Secrets are supplied by the runtime secret manager, never committed in source, fixtures, artifacts, prompts or logs. Local `.env` files are development-only and must be excluded from version control. A local identity issuer is test-only; it is not a production identity provider.

**Concrete data-egress rule:** if an investigation needs to ask a model why one group has an unusual rate, the model should receive the authorized, treated aggregate dossier and the question—not raw customer identifiers, a full transcript dump, secrets, or a tool that can mutate a bank record. The run configuration pins which evidence classes may leave the workspace. If the required explanation needs disallowed fields, the correct result is `blocked`/`not_evaluable` with the missing-evidence reason, not an unapproved export. A provider's ability to process text is not permission to receive it.

## 8.3 Observability as system input

The engine should use logs, metrics and traces both to explain its own work and to detect failures in the four service layers. Observability events have two different meanings:

1. **Engine execution telemetry:** stage duration, queue wait, lease attempts, retries, query resource use, evidence counts, model/Core latency and result class. These support reliability and debugging.
2. **Service behavior observations:** classified, minimized events from the customer-service platform describing what its classifier, decision flow, AI1, AI2, tools and human handoff did. These can support detection only after event semantics, ordering, completeness and source contract are verified.

Do not feed arbitrary debug logs or trace baggage directly into detectors. Normalize approved event schemas, remove identifiers/free text unless strictly needed and authorized, attach provenance and availability times, and aggregate before broad access. Current platform sensor tests use generated histories; source payload semantics/backfill are unresolved. Current README says the Rust engine is not yet wired to emit OpenTelemetry (OTel, a common format for logs/metrics/traces). Do not represent optional Grafana/LGTM services as a working telemetry path.

**Langfuse is a separate, optional trace view—not the Improvement Engine's source of business truth.** In the pinned engine snapshot, trace construction/export helpers and bridge scripts exist, and local traffic has been exercised against a mock receiver. The separate `infra` repository describes one loopback forwarder sidecar per producer (LLM gateway, Agent Core and engine) and defaults both forwarder enablement and prompt/response capture off. Its forwarder is not built or run in that snapshot, Terraform is not applied, and real Langfuse Cloud ingestion/readback remains unverified. The sidecar holds export credentials; producers do not. JSON gets a limited known-secret-pattern scrub, but protobuf is passed through byte-for-byte, so emitters must prevent sensitive content before export. These traces explain execution steps and model/tool behavior; they do not establish that a service problem was solved or that a candidate improved outcomes. See [infrastructure, reliability and Langfuse](../../infra/guide/infrastructure-and-observability.md) for the topology, evidence pins and privacy caveats.

### Example: what an operator should see when a run cannot explain a signal

Imagine the investigator sees a high service-event failure rate but cannot join those events to customer contacts because the platform feed lacks a supported interaction key. The internal backoffice should show, in order: **signal measured** (metric, window, numerator/denominator, coverage and source kind); **join checked** (key and match coverage, with suppressed details withheld); **claim limited** (`unlinked`, no causal wording); **proposal stopped** (reason and missing dependency); and **next safe action** (inspect feed contract or keep the result descriptive). The operator should also see run ID, stage durations, retries, model/Core calls, budget use and trace links. It should not expose raw transcript text or make “blocked” look like a service failure that has already affected a customer.

That is the product's “low interaction, high visibility” principle: the engine does the routine investigation, but leaves an auditable timeline for an engineer or service owner to understand exactly why it proceeded, stopped or asked for approval. This exact live console experience is a V3 target; current console pages include fixture/stand-in data until the Rust control API is connected.

Minimum target indicators include accepted/rejected jobs, queue age, active/expired leases, stage latency, retries and terminal states; source freshness/schema failures; query rows/bytes/time/truncation; model/Core calls, cost/budget and error classes; candidate gate outcomes; external-command reconciliation backlog; memory publication/revocation; and suppression/coverage counts. Alert on stuck jobs, growing queue age, repeated source drift, budget exhaustion, uncertain external effects, bridge auth/contract failures and stale ingestion. Alerts require owner, severity, runbook and tested notification path.

## 8.4 Local versus deployed stack

| Local development/test | Deployed target |
|---|---|
| Windows/PowerShell first; Podman Compose for dependencies; LocalStack only for AWS APIs actually needed by engine tests | Terraform in the separate `infra` repository declares AWS foundations and service resources |
| Disposable PostgreSQL, S3-compatible object storage and optional observability stack | Managed PostgreSQL, object storage, IAM, compute, secrets, network and monitoring according to the infra plan |
| Fixtures/synthetic event generator and external Agent Core local stack where available | Approved platform feeds, deployed Agent Core/identity and secret bindings |
| Explicit offline snapshot runner and separate model/Core demo profile | Controlled private ingress, outbound allowlists, data retention and operational alarms |

The complete local Compose smoke was not verified on the documented Windows environment. AWS Terraform definitions are not an applied deployment. The pinned open-gap register lists private debug ingress, runtime DB secret binding, controlled egress, alarm contract, exporter/control API integration and full joint run as incomplete. The current hosted workflow covers Rust checks and PostgreSQL migration tests, not every Python/console/bridge/Terraform package; the implementation record therefore requires relevant local checks for each package before claiming full validation.

## 8.5 Reliability and recovery

Use explicit deadlines and bounded retry with jitter only for safe/idempotent work. Place limits on source bytes, rows, query time/memory, model tokens/cost, artifact size and run duration. A runaway run must be cancellable and leave a terminal reason plus partial-artifact policy. For external mutations, reconcile by operation identity before retry. For ingestion, cursor advancement must be atomic with accepted observations or recoverable by deterministic replay; current event-source recovery/backfill is unresolved.

## Source references

- V3 §§6, 8–10, 19–20, 25–27, 30
- [Deployment boundary and gaps](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/architecture/deployment-boundary.md)
- [Current open gaps](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/docs/gaps/OPEN_GAPS.md)
- [Current CI workflow](https://github.com/pulso-factored/improvement-engine/blob/fc56b598b1be483a6b1eb7ee6fac0d9809c3b646/.github/workflows/ci.yml)
