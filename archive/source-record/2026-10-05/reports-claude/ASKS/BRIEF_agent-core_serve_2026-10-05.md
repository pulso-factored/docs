# Brief for the agent-core team: make `agentcore serve` the production Core

From: Pulso improvement-engine team (Claude). Date: 2026-10-05. Delivery: ready PRs in github.com/pulso-factored/agent-core (small, additive, tested), one report. We consolidate, deploy and test in the real environment; you implement.

## 1. Context (why this is urgent)
Infra ADR 0009 makes `agentcore serve` the ONE shared Core for: the support-platform assistant (customers) and copilot (advisors), our improvement engine (registry writes, evaluate, lineage, run export), evals, and the registry approvals done by supervisors in the platform. It will run as a container on an EC2 host (single environment, us-east-1) next to Postgres, llm-gateway and tool-service. Our engine was proven only on a local stack in which parts of agent-core are test doubles. A survey of main (2ad5d08, 2026-10-05) found: the transfer demo does not work over `serve`; several `serve` pieces are doubles; audit replay of real runs diverges; no fixture agent has an `eval_suite`; GitHub CI has been down since 10-03 (so local gates are authoritative). We need to know exactly what is real, and to close the gaps that block a production-like run.

Already merged and in use (do not redo): PRs 48 (traceparent and Langfuse attributes), 50 (candidate prompts evaluated), 51 (`inherit_from`), 52 (approval review inherited values), 53 (reject `reason_code`), 54 (scenario principal type and subject), 55 (policy `locked` and `guardrail_changes`), 56 (`tool_source`). Open: 57 and 58 (yours).

## 1.1 Boundaries: who owns what (read this before starting; avoids overlap)
- YOU (agent-core): everything inside the agent-core repo: `serve` internals, its health/readiness, migrations, its image, its env contract, its fixtures and ToolDefs, key-loading semantics, eval suites that live in agent-core fixtures.
- US (engine team): the engine side (admitting event types in our exporter contract, resolving evidence links, our own copies of tool fixtures and the drift check script in the engine repo, our eval suites that are finding-specific, built by `scripts/regression/`), the OTLP forwarder and Langfuse closure (done, PR 107), the dev stack scripts.
- INFRA (us, github.com/pulso-factored/infra): Terraform, EC2 compose/systemd/user_data, who generates secrets and tokens (Terraform), S3, IAM, security groups, one shared Postgres instance and its databases and roles, CloudFront. You document what `serve` needs; we wire it. Do not edit infra.
- Platform team: platform repo only. Do not edit support-platform.
- CODEX (independent team): already authored baseline eval suites for the four agents (see A2.4) and scenario packs. Reuse, do not rewrite.
If a task seems to belong to someone else, reply in the PR or to us instead of doing it.

## 2. What we need (work items, in priority order)

### A1. Honest inventory of `serve` (P0, first deliverable, 0.5 day)
Document, with file:line, for each component whether `serve` uses the REAL implementation or a double/stub/in-memory substitute: calibration, classifier, JEV and judges, tool-service client, transcript store, authz (TableAuthz vs staff keys), registry store (Postgres vs memory), run store, telemetry exporter, secrets and key loading, scheduler/background tasks, outbound events. Output: `docs/serve-readiness.md` with a table (component, real/double/broken, evidence, effort to make real). This tells everyone what to trust.

### A2. Close the functional gaps found by the survey (P0)
1. The transfer flow must work over `serve` (dispute and transfer fixtures), same result as `replay --mode fixture`.
2. Audit replay of real runs must not diverge (or document precisely why and what is excluded).
3. Replace doubles that the platform or the engine depend on (calibration, classifier, judge) with real implementations in serve mode, or make the double explicit: serve must REFUSE to start in "production mode" if a double is active unless an explicit `AGENTCORE_ALLOW_DOUBLES=1` is set, and log the active mode at startup.
4. Baseline `eval_suite`s for the four fixture agents (recepcion, disputas, consultas, copiloto-asesor): DO NOT author them from scratch. They already exist: Codex's bank is on our engine main under `agent-core-assets/eval-suites/codex-bank/` (`recepcion@1.0.0.yaml`, `disputas@1.0.0.yaml`, `consultas@1.0.0.yaml`, `copiloto-asesor@1.0.0.yaml`, 104 cases, 69 prompt-only, validated by its own script), and our engine has two minimal live-proven suites (disputas-min 20 cases, consultas-min 11) in the engine repo. Your job: take them as the source, make them load as agent-core fixtures (schema, `agent_id`, thresholds, guard vs gate metrics, hashes), run them natively on `serve`, fix anything the schema or evaluator rejects, and report which cases fail on the current agents (real defects). Copilot cases need the scenario principal type `advisor` (already merged, PR 54). We still attach finding-specific suites ourselves; these are baselines.

### A3. Operability contract (P0)
- `GET /healthz` (liveness: process up, event loop responsive, no dependency checks) and `GET /readyz` (readiness: Postgres reachable and schema at the expected version, migrations applied, signing keys loaded, llm-gateway reachable; tool-service reachability reported but configurable as required or optional). Both unauthenticated, fast (<200 ms), JSON with per-dependency status and no secrets.
- Postgres schema bootstrap and migrations run automatically at start, idempotent, guarded by an advisory lock so two instances do not race.
- Configuration only through environment variables (document the full list: names, required or optional, defaults, which are secrets) in `docs/serve-env.md`; fail fast with a clear message when a required one is missing; never log values.
- Graceful shutdown (finish or checkpoint in-flight turns on SIGTERM), safe restart in the middle of a run (a run resumes or closes with a defined outcome, never a corrupted state).
- Structured JSON logs with trace id; request and run concurrency limits configurable.

### A4. Container image (P0)
(Interface with infra: you deliver the Dockerfile, the compose reference and the documented env contract; infra wires them into EC2 and Terraform and builds the final tagged image with digests. Do not edit infra.) `Dockerfile` for `agentcore serve`: multi-stage, non-root user, pinned base by digest, linux/amd64 AND linux/arm64 (the EC2 type may be Graviton), `HEALTHCHECK` using `/healthz`, entrypoint `agentcore serve`, no dev dependencies, size reported. A `docker compose` example (serve, Postgres, llm-gateway, tool-service) that is the reference for infra. Build must work locally with Podman (we have no hosted CI).

### A5. Auth and keys for the engine (P1)
Key GENERATION and injection belong to infra (Terraform generates the tokens and Ed25519 keys; infra PR 37 is merged). What we need from you is only the consuming side in agent-core:
- A dedicated `builder` principal (accepted risk: key in staff-keys) with an explicit allow-list: registry write, freeze, evaluate, read; approve, publish and promote denied (already the engine's contract; add a test in `serve` mode).
- Document the exact key and staff-keys file formats `serve` reads (names, shapes, where they are mounted, how reloaded) so infra can generate and mount them; loading must be idempotent and never print key material.
- Key rotation: confirm and test that rotating the engine key does not need restarting other services (or document what is needed).

### A6. Tool-service alignment (P1)
- Tool definitions in agent-core fixtures drift from tool-service (e.g. `leer_productos` source `productos` vs `customer_products`; `leer_pqr_cliente` `pqr` vs `customer_cases`; `obtener_pqr` and `buscar_transacciones` have no source). Align the agent-core fixtures and add a test in agent-core that compares fixture ToolDefs with tool-service's contract and fails on drift. Our side (already in progress, do not duplicate): the engine's own copy of the fixtures and a drift-check script in the engine repo, and the ask text `ASK_tool-alignment.md`. Coordinate on the final `source` values by replying to that ask.
- Confirm the tool grant model for read-only tool links (what authorizes an agent to call a tool: field classifier, field grants, tool-service), documented in one page; the engine proposes links based on it.

### A7. Observability (P2)
Langfuse itself is DONE (your PR 48 plus our forwarder, proven live on Langfuse Cloud); do not rebuild it. Only verify that `AGENTCORE_TRACE_CONTENT` and `AGENTCORE_TRACE_LANGFUSE` still work in `serve` mode inside the container image, and document the OTLP env names.

## 3. How to test (required)
1. Unit and contract: new tests per item, RED first; `ruff`, `mypy`, `lint-imports`, `agentcore contracts --check`, the touched pytest suites and `tests/registry`, `tests/contracts`, `tests/outbound`.
2. Live end to end on a local compose (Podman is fine): Postgres 16, llm-gateway (OpenRouter models xiaomi/mimo-v2.6-flash for agents, xiaomi/mimo-v2.6-pro for judges), tool-service on the data pipeline fixtures, `serve` image built by A4. Run: start and finish runs for the four agents (es and pt), the transfer flow, freeze and evaluate with an `eval_suite`, approve and publish through the approval routes, run export, lineage. Do not leave anything `not_exercised` for missing environment; if a key is needed, say exactly which and we provide it as a process environment variable.
3. Chaos: restart Postgres while serving; restart `serve` mid-run; start `serve` with a missing required variable; start with the DB down and confirm `/readyz` is 503 while `/healthz` is 200.
4. Concurrency: 20 simultaneous runs, no errors, bounded latency (report p50 and p95).
5. Image: build, run non-root, health check passes, size and arch reported; the compose example comes up with one command.

## 4. Definition of done
- `docs/serve-readiness.md` and `docs/serve-env.md` merged; the table has no "unknown".
- Every item above has a PR (or an explicit "not doing, because" with evidence); each PR has tests and passes local gates.
- The local compose runs the full loop above with `serve` as the Core, with the doubles removed or explicitly flagged; the chaos and concurrency results are in the report.
- Image reproducible with one command on amd64 and arm64.
- Report to us: PR list, test counts, the live-run transcript summary (counts only, no secrets), remaining gaps with owner and effort.

## 5. Constraints
No secrets in code, tests, logs or PR text. Additive and backward compatible where possible (published hashes unchanged). Keep the engine contract: the engine never approves, publishes or promotes. Ask us if any value or credential is missing; do not invent.
