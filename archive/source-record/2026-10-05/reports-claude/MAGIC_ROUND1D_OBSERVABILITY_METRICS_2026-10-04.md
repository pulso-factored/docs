# MAGIC round 1D: observability and metrics (2026-10-04)

Read-only research. Legend: [V] verified in code/docs, [I] inferred, [?] unknown. Nothing under D:\Nexus touched.

## 1. LLM observability (Langfuse)

**What already exists [V].** llm-gateway (Go) emits OTLP spans per call when `OTEL_EXPORTER_OTLP_ENDPOINT` is set: `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.input_tokens/output_tokens`, finish reasons, `llmgateway.consumer`, error kind (`llm-gateway/internal/gateway/telemetry.go:42-80`; infra ADR 0004 line 74). It also has `internal/cost/cost.go`. agent-core has `agent_telemetry` (OTLP/HTTP batch exporter, explicit endpoint+headers, `setup.py`), and its docs already point to Phoenix as the optional viewer. So both producers speak OTLP/HTTP; the only missing piece is a backend and our own engine spans.

**Langfuse fit [V from langfuse docs].** Accepts OTLP/HTTP at `/api/public/otel/v1/traces` with Basic auth (project keys). Span = observation; `langfuse.observation.type` = span|generation|event; model/usage/cost, input/output, metadata (`langfuse.trace.metadata.<k>`) and prompt links map from attributes. Standard `gen_ai.*` attributes are accepted [I: docs list property mapping; verify with one test span]. Scores, datasets, experiments, prompts are first-class entities (API/UI).

**Mapping to our pipeline.**
- One trace per `proposal_attempt`, trace id = deterministic from `trigger_key` so replays join. Root span `finding` (metadata: signal, cell, k, replication verdict).
- Child spans `scout`, `verifier`, `builder` (each a span; each LLM call a `generation` with model mimo-flash/pro/glm, tokens, USD set explicitly using our price table, so cost does not depend on Langfuse's model list), `compile`, `agentcore.proposal.create/freeze/evaluate` (event + gate verdict), later `outcome` event attached to the same trace days later (same trace id, new span; late spans are fine in OTLP).
- Scores on the trace: `eval_gate_pass` (bool), `rubric_quality` (0-1, LLM-judge or rubric), `human_decision` (accepted/rejected/expired), `outcome_verdict` (improved/no_change/worsened/inconclusive). Scores can be posted later via API, which fits human latency.
- Datasets: frozen "known-problem" cases (the bank Queja-by-reason finding, E0 repeated-copilot-query) as a regression set; Experiments = rerun Scout/Verifier/Builder prompts or model swaps (flash vs pro vs glm) over the set and compare cost/quality. This is the strongest "improvement of the improver" story.
- Prompts: keep our three agent prompts in agent-core registry (source of truth, they are agent-core agents). Langfuse prompt management would duplicate; skip. Link versions via metadata `prompt_version`.

**Where to instrument.** Both, with one trace id propagated: (a) gateway already emits generations; add a request header `traceparent` from the engine so gateway spans become children of our spans (small; engine is the caller so we control it) and set `llmgateway.consumer=pulso-engine` [V consumer attr exists]. Ask gateway owners only for optional `gen_ai.usage.cost` / input-output capture (unknown if present [?]); we do not depend on it. (b) Engine (Rust): `opentelemetry` + `opentelemetry-otlp` (http-proto, reqwest) with a BatchSpanProcessor; ~1-2 days for spans at stage boundaries, no new service. Do not instrument only the gateway: it cannot see finding, verification, proposal, outcome.
agent-core runs (`pulso-builder` via /v1/runs) export spans through `agent_telemetry` if its OTLP endpoint is pointed at Langfuse with the auth header (config only, `OTEL_EXPORTER_OTLP_ENDPOINT` in agent-core.env; headers may need the explicit `headers=` argument since setup does not read `OTEL_*` [V setup.py docstring]; platform/agent-core ask: 1 env/config line).

**Self-hosted vs cloud.** Self-host v3/v4 needs web + worker + Postgres + ClickHouse + Redis + S3 (v4: ClickHouse >= 25.12) [V docs]. Realistic floor about 4 vCPU / 16 GB for comfort; ClickHouse alone wants several GB [I]. That does not fit a Free Plan tiny instance nor a RAM-constrained laptop. Recommendation: **Langfuse Cloud (Hobby free tier or Core) for the demo**, with our own synthetic data only (the gateway scanner blocks raw rows already; generation inputs are treated aggregates). Caveats: free-tier limits on units/retention [?, check current pricing], data leaves our perimeter, so keep `input/output` capture to treated prompts or disable it (metadata + tokens only). Self-host later only if the platform gives a proper host. Fallback with near-zero footprint if cloud is refused: Phoenix single container (already referenced by agent-core runbooks, SQLite) for traces only, no datasets/experiments depth.

**What Langfuse adds that debug-console does not.** Console = our system's state (runs, graph, gates, diff, decision, automation maturity). Langfuse = per-call forensic view (prompt in/out, tokens, latency, cost, retries), cross-run cost/latency analytics with no code, scores/annotation queues for the human rubric, datasets/experiments for model and prompt comparison. Console cannot do model-vs-model experiments or cost drill-down; Langfuse cannot show the engine's graph/decision story. Keep both; deep-link console -> Langfuse trace by trace id (console stores the id; one URL template).

## 2. Metrics (exact definitions, source today, where shown)

Run = one engine run for a trigger; proposal = frozen proposal in agent-core registry; decision window = proposal creation to human approve/reject/expiry.

| # | Metric | Definition | Source today | Shown |
|---|---|---|---|---|
| A1 | Agent resolution rate | runs closed `resolved` / runs closed, per agent and reason | agent-core `/v1/export/runs` (pull, in use) | console panel; SPA card ask |
| A2 | Handoff rate | runs with `handoff.created` / runs | export events [V event catalog] | console |
| A3 | Fallback rate | LLM calls served by a fallback model / calls | gateway spans [I: needs attribute check] | Langfuse |
| A4 | Cost per agent run | sum USD of generations in the run | gateway tokens x price table | Langfuse + console |
| A5 | Latency p50/p95 | run duration; per generation | spans | Langfuse |
| P1 | Proposals made | count of frozen proposals per week | ledger [V viable/not_viable/not_evaluable] | console |
| P2 | Human decision mix | accepted / rejected / expired / pending, share and counts | registry state via pull (`/registry-events`) | console; SPA |
| P3 | Time to decision | decision ts - proposal freeze ts, median and p90 | registry-events | console |
| P4 | Pre-release eval pass rate | proposals whose `evaluate` gate passed at first attempt / evaluated; also attempts-to-pass | Builder calling `evaluate` (not wired yet, round 1B #1) | console + Langfuse score |
| P5 | Proposal quality score | rubric 0-1: evidence cited (k, CI), targets a real artifact, eval cases attached, reversible, no PII; mean of items, judge = Verifier-independent model or deterministic checks | not exist; deterministic part computable from proposal JSON | Langfuse score, console badge |
| P6 | Outcome verdicts | share improved / no_change / worsened / inconclusive per proposal, vs a pre/post window on the monitored metric | `release.*`, `run.closed`, lineage `release_id` (round 1B #4); bank data is stationary so pre/post is weak [V audit] | console; SPA |
| P7 | Automation share | detected problems (replicated, verified) with an accepted proposal / detected problems | ledger + P2 | console headline |
| P8 | Cost per proposal | sum USD of all generations in trace (Scout+Verifier+Builder+retries); USD = tokens_in x p_in + tokens_out x p_out, prices per token flash 1.4e-7/2.8e-7, pro 4.35e-7/8.7e-7, glm 1.5e-7/5e-7 | tokens from gateway/engine; prices table | console + Langfuse |
| V1 | Estimated value (range) | contacts avoided/yr x handling cost; shown as low/base/high, never a point | below | console, flagged ESTIMATE |

**V1 honestly.** Bank audit [V]: unresolved contacts: Queja 56.4% (66,000/117,021) vs 16.6% others; ~686k contacts / 3 yrs ~ 229k/yr; Queja ~39k/yr. Handled time on unresolved contacts is 28.9% (per audit, as the user stated). Formula: avoided contacts = affected_volume x baseline_unresolved_rate x assumed_relative_reduction (scenarios 5% / 15% / 30%, labelled assumptions, not measured) x recontact_share; minutes = avoided x mean handle time on unresolved; USD = minutes x loaded agent cost per minute (unknown input; ask the user/bank for a number, else show minutes only). Show as "up to X hours/year if reduction is r", ranges, and say that the bank data shows no causal chain contact->complaint [V audit sec 0.5] so recontact avoidance is NOT claimed. Verdict-based value counts only proposals with outcome `improved`.

## 3. Ranking (magic / effort), who does it

1. Console "Proposal story" panel: finding -> Scout -> Verifier -> Builder -> proposal -> eval gate -> decision -> outcome as one timeline with cost and Langfuse deep link. Panels already project `investigation_set, alternatives_set, diff_set, gates_set, decision_set` (debug-api `panels.rs`); add `cost_set`, `outcome_set`. Effort S. **Us.**
2. Headline strip (P1, P2, P7, P8): "N problems found, M proposals, K accepted, $0.0X per proposal". Effort S, from ledger. **Us.**
3. Token/USD accounting in the engine (price table, per stage), emitted as events. Effort S. **Us.**
4. Engine OTLP spans + `traceparent` into the gateway, shipped to Langfuse Cloud. Effort M. **Us** (Codex independent can do gateway-side header passthrough/cost attribute check; ask is optional).
5. Pre-release evaluate in Builder with attempt count (P4: "failed first, passed second"). Effort S-M. **Us + agent-core** (capability exists, N).
6. Value card V1 with ranges and assumption sliders in console. Effort S. **Us** (needs a handling-cost input from the user).
7. Scores on traces: gate pass, rubric quality (deterministic checks first), human decision synced from registry events. Effort M. **Us.**
8. Outcome verdict (P6) via release lineage pull. Effort M; depends on a published release existing. **Us + agent-core** (pull works, no new work) / **platform** for approvals.
9. Langfuse dataset + experiment: model comparison flash vs pro vs glm on the Queja case. Effort M. **Codex independent** (runs over frozen cases, no engine coupling).
10. SPA card "improvement impact" (P2/P6/V1 summary) and pointing agent-core `agent_telemetry` at the same Langfuse. Effort S on our side (forwardable ask), M for them. **Platform / agent-core.**

## 4. Build first
Items 1-3 in one increment (no new infra, pure wow in the console), then 4 with Langfuse Cloud for the "click a proposal, see every LLM call and its cost" moment, then 5-6. Caveat: with stationary bank data, outcome verdicts will mostly be `inconclusive`; say so on screen rather than manufacturing improvement.
