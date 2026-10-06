# LLM gateway adoption: analysis and design (Team Claude)

Date: 2026-10-03. Scope: analysis and design only (no repo changes other than this file). Evidence is cited as `repo:path:line`.

Sources read:
- `pulso-factored/llm-gateway` main `63155b600d4b108ac871125cfd633c2beb11b0b5` (2026-10-03T16:12:41Z, confirmed with `gh api`), scratch clone, called **GW** below.
- `pulso-factored/agent-core` main `789d6c8` (PR #26 `HttpLLMGateway`, ADR 0024; ADR 0022/0023 are about stable surfaces and AWS scale-out, not the gateway), called **AC**.
- `pulso-factored/infra` `origin/main` `docs/adr/0004-llm-gateway-workload.md`, called **ADR4**.
- Our tree: worktree `improvement-engine-claude-r` (HEAD 8ee031d, pin already 789d6c8 per `core-bridge/docs/adr/0008-agent-core-pin-789d6c8.md`), V3 spec, two-team plan.

Executive summary:
1. The gateway is small and sound, but it is **only** a stateless, one-call, typed-error HTTP adapter. It has **no server-side budget, no rate limit, no model or price allowlist, no idempotency, no streaming, no usage log**. Everything the V3 spec calls "budget", "egress control" and "fail closed" must therefore stay in our `pulso-core-runtime` wrappers and in infra.
2. Our runtime already speaks the gateway protocol: AC `HttpLLMGateway` replaces `OpenAICompatGateway` behind the same `LLMGateway` port, so `BindingGuardGateway(SpendMeteringGateway(ports.gateway))` (`core-bridge/src/pulso_core_runtime/main.py:277`) keeps wrapping the Core port **unchanged**. The work is configuration, readiness, fail-closed classification, metering fixes, local stack and tests.
3. Four defects/gaps in what we have today matter more than the transport: (a) `UnconfiguredLLMGateway` silently turns "no gateway" into "unavailable on every call"; (b) `SpendMeteringGateway` does not meter failed calls that carry usage, drops over-cap spend, ignores `usage_known`, and has no pre-reservation; (c) a gateway outage on a Scout/Verifier/Builder `agent` node surfaces as `escalate(low_confidence)`, indistinguishable from a real "I could not find it"; (d) `compose.core.yaml` and V3 CAP-50/CAP-60/F6 still describe the removed `LLM_ENDPOINTS` + provider keys inside the runtime.
4. The Rust engine never calls an LLM (verified in V3 and in the engine tree). Codex needs only vocabulary and error-mapping notes (section 6).
5. I built the image and ran it on `pulso-dev` against a scripted OpenAI-compatible upstream (section 1.8): all documented behaviours reproduced; two operational findings (HEALTHCHECK ignored in OCI builds; any caller can choose any model and price).

---

## 1. Gateway API contract (verified)

### 1.1 Routes and auth
| Route | Auth | Notes | Evidence |
|---|---|---|---|
| `POST /v1/generate` | Bearer (per consumer) | LLM call | `GW:internal/httpapi/httpapi.go:100` |
| `POST /v1/jev` | Bearer | JEV transport, gateway holds `JEV_API_KEY`, retries 429/529 only | `GW:httpapi.go:103`, `GW:api/openapi.yaml:104-138` |
| `GET /healthz` | none | `{"status":"ok"}`; liveness and (per ADR4) readiness; no dependency check | `GW:httpapi.go:137-144`, `ADR4 contract item 2` |
| `GET /v1/openapi.yaml` | none | contract served by the instance | `GW:httpapi.go:146-153` |
| anything else | n/a | 404 `not_found`; non-POST on generate: 405 | `GW:httpapi.go:106-108,217` |

Auth: `Authorization: Bearer <token>`; the token is SHA-256 hashed and compared to every configured consumer in constant time; the consumer **name** goes to logs and spans, never the token (`GW:httpapi.go:200-215`). Order of checks on `/v1/generate`: method, **auth**, content-type, body size, body decode (`GW:httpapi.go:155-182`). Consequence used below: a valid token with an intentionally empty/invalid body returns 400 (auth passed, no provider call, no cost); an invalid token returns 401. That gives a **free authenticated readiness probe** (observed: unknown field -> 400 with a valid token; bad token -> 401).

### 1.2 Request
`POST /v1/generate` body (closed contract, unknown fields -> 400, so `stream` is rejected: observed):
`prompt` (system message, sent as is), `inputs` (object -> RFC 8785 canonical JSON in the *user* message), optional `schema` (closed subset: `type, enum, properties, required, additionalProperties(bool), items`; anything else -> 400), `profile` {`endpoint_alias, model, temperature(0..100), max_tokens(1..1_000_000), timeout_s(1..300, default 8), structured(native|prompted, default native), price{input_per_mtok, output_per_mtok}` decimal **strings** 0..1_000_000}, optional `labels` (closed keys: `prompt, model_profile, run_id, turn_id, session_id, release, agent`, each <=128 chars). Evidence: `GW:api/openapi.yaml:187-258`, `GW:internal/httpapi/request.go:14-18,123-167`. Body limit 1 MiB (`MAX_BODY_BYTES`).

Upstream call: exactly one `POST {base_url}/chat/completions` with `Authorization: Bearer <key from env>`; body is `model, messages[system,user], temperature, max_tokens` plus `response_format` json_schema strict only in `native` mode; `prompted` appends the Spanish schema instruction to the system prompt (`GW:internal/gateway/call.go:54-60,85-111`, `GW:gateway.go:210`). Redirects are not followed (`GW:gateway.go:133`); response capped at 8 MiB (`GW:call.go:19`).

### 1.3 Response and errors
Success: `{output, model (as reported by provider), tokens_in, tokens_out, cost_usd (string, 6 decimals), usage_known}`. Cost is computed by the gateway from **the price the caller sent**; any provider-reported cost is ignored (observed: provider `cost:99.0` ignored). Without provider usage: tokens 0, cost `"0.000000"`, `usage_known:false` (observed).

Errors: `{"error":{"kind","message","model"?,"tokens_in"?,"tokens_out"?,"cost_usd"?}}`; `message` is generated by the gateway and never echoes inputs or provider text (observed: a 429 whose body contained a marker string did not leak).

| HTTP | kind | observed trigger |
|---|---|---|
| 400 | `bad_request` | unknown field, unsupported schema keyword, `stream` |
| 401 | `unauthorized` | missing/wrong token |
| 413 / 415 | `payload_too_large` / `unsupported_media_type` | 1 MiB+ / non-JSON |
| 429 | `rate_limited` | **provider** 429 only (there is no gateway-side limiter) |
| 502 | `unavailable` | provider 4xx/5xx, upstream down, unknown alias, empty key, undecodable reply, JEV without key |
| 502 | `invalid_output` | not JSON, schema violation, `finish_reason=length`; **carries tokens and cost** |
| 502 | `refused` | `content_filter`/refusal; carries tokens and cost |
| 504 | `timeout` | `timeout_s` elapsed (observed 1.02 s at `timeout_s=1`) |

AC `HttpLLMGateway` maps these kinds 1:1 to `GatewayErrorKind`; `bad_request`, `unauthorized` and unknown kinds become `unavailable` (`AC:agent_core/adapters/llm/http_gateway.py:142-160`).

### 1.4 Streaming, limits, idempotency
- **No streaming** (`GW:docs/specs/2026-10-03-llm-gateway-extraction-design.md:12` lists "stream, cache, retry, keep counters" as non-goals; request with `stream` is 400).
- **No rate or budget limits.** Observed: 120 requests with 30 concurrent all returned 200. No per-consumer quota, no concurrency cap, no max price, no allowed-model list: the caller owns model, parameters and price (`GW:docs/decisions-for-review.md` row 11 only caps absolute numbers: price <= 1,000,000 USD/Mtok, `max_tokens` <= 1,000,000).
- **No idempotency key, no dedupe, no retries** (one provider call per request; JEV is the only retrying path).
- Timeouts: provider deadline = `timeout_s`; server `ReadTimeout 30s`, `WriteTimeout 330s` (`GW:cmd/llm-gateway/main.go:84-85`).

### 1.5 Observability
JSON logs on stdout: `request` line with `request_id, route, status, duration_ms, consumer, kind, model`; `generation failed` with `kind, alias, model, cause` (cause is a gateway-generated reason such as a schema path, no data). **Tokens and cost are not logged** (only on spans). OTLP traces (GenAI attributes) only when `OTEL_EXPORTER_OTLP_ENDPOINT` is set; `traceparent` and `X-Request-Id` are honoured; `labels` are copied to the span. Verified: after ~30 calls with marker strings in prompt/inputs, a 429 body marker, the upstream key and the consumer token, **zero** occurrences in the container logs.
Implication: the **spend ledger must be ours** (the gateway cannot reconstruct spend from logs); gateway spans are optional corroboration.

### 1.6 Configuration and secrets
`GATEWAY_CONSUMERS` JSON `{name:{token_env}}` (required, exit 2 if missing; two consumers with the same token -> exit non-zero) (`GW:internal/config/config.go:94,147,172-181`); one env var per consumer token; `LLM_ENDPOINTS` JSON `{alias:{base_url(http|https), api_key_env}}`; one env var per provider key; `LISTEN_ADDR` (:8080), `MAX_BODY_BYTES`, `JEV_API_KEY, JEV_BASE_URL (https only, http toward localhost), JEV_MAX_RETRIES, JEV_BACKOFF_MS`, standard `OTEL_*`. Missing endpoint key or no endpoints only logs a warning and calls fail `unavailable` (`GW:cmd/llm-gateway/main.go:52,56`): fail-open at startup, fail-closed per call. Keys are read from env per call and never stored. A plain `http://` provider `base_url` is allowed (needed locally; in staging/prod infra must enforce https destinations).

### 1.7 Dockerfile and health
`golang:1.27` build, `CGO_ENABLED=0`, `gcr.io/distroless/static-debian12:nonroot` (uid 65532, no shell), `EXPOSE 8080`, `HEALTHCHECK ... /llm-gateway -healthcheck`, 18.4 MB image (`GW:Dockerfile`). **Finding:** podman builds OCI images and warns "HEALTHCHECK is not supported for OCI image format and will be ignored"; `inspect` shows `Healthcheck: <nil>`. Compose/ECS must declare the health check themselves (`["CMD","/llm-gateway","-healthcheck"]` works: observed rc=0). Release: tag `vX.Y.Z` -> `ghcr.io/pulso-factored/llm-gateway` (private repo, so pull credentials are needed); never run yet (`GW:.github/workflows/release.yml`).

### 1.8 Local build and run evidence (pulso-dev, rootless)
Commands (podman at `$env:USERPROFILE\AppData\Local\Programs\Podman\podman.exe`, always `--connection pulso-dev`):
- `build -t localhost/llm-gateway:claude-scratch .` from the scratch clone: success in ~33 s.
- user-defined network `claude-llmgw-net`; upstream = scripted OpenAI-compatible double (stdlib Python run inside an existing `pulso-core-runtime` image, script injected by base64 env var) at `claude-llmgw-upstream:9000`; gateway container `--cgroups=disabled --pids-limit=0 -p 127.0.0.1:18471:8080`, two consumers, one alias `scripted`.
- Driver (host Python) results: ok/fenced-JSON/text/no-usage/provider-cost-ignored -> 200 with exact cost (1000 in/500 out at 0.10/0.32 = `0.000260`); `badjson, wrongshape, truncated` -> 502 `invalid_output` with usage+cost; `refuse` -> 502 `refused` with usage; provider 429 -> 429; provider 500 -> 502 `unavailable`; slow upstream at `timeout_s=1` -> 504 `timeout`; unknown alias -> 502; upstream stopped -> 502 `unavailable` in 0.09 s; `native` mode sends `response_format` (verified in upstream capture), `prompted` appends the schema to the system prompt; upstream received the **upstream** key, never the consumer token; 401/415/413/400/405 behave as documented; two consumers authenticate independently; `/v1/jev` without key -> 502 `unavailable`; `-healthcheck` rc=0 inside the container; duplicate tokens or missing `GATEWAY_CONSUMERS` -> exits with error.
- **Operational finding (security-relevant):** any authenticated consumer can send `model:"anything"` and `price` up to 1,000,000 USD/Mtok and `max_tokens` up to 1,000,000; observed `cost_usd:"1500.000000"` for a 1000/500 call. Accounting trusts the caller's price. See 2.6 and question Q1.
- Cleanup done: both containers, the network and the image were removed (`ps -a` shows 0 `claude-llmgw-*`). I did not run the gateway's own `go test` (no Go toolchain in this session); its CI runs it.

---

## 2. How our system uses it

### 2.1 Current state in our tree
- `pulso-core-runtime` composes the pinned Core in-process (`core-bridge/src/pulso_core_runtime/main.py`): `resolve_ports(...)` returns `ports.gateway`; the live path wraps it: `gateway=BindingGuardGateway(SpendMeteringGateway(ports.gateway, l3.registry, l3.store), l3.registry)` (`main.py:277`); evaluation composes from the **unguarded** gateway with its own budget meter (`main.py:85-90`, `evaluation/budget.py:80-98`).
- With AC 789d6c8 `ports.gateway` is `HttpLLMGateway(registry, AGENTCORE_LLM_GATEWAY_URL, AGENTCORE_LLM_GATEWAY_TOKEN)` when both vars are set, else `UnconfiguredLLMGateway` (`AC:agent_core/composition/serve_ports.py:191-205,322-323`). Env vars are passed through untouched (`core-bridge/README.md:77`, ADR 0008 item 7).
- `local/core/compose.core.yaml:165-168` still forwards the removed `LLM_ENDPOINTS` and `PULSO_LLM_API_KEY` (and no `AGENTCORE_LLM_GATEWAY_*`); `e2e-core` works around this with an image overlay that bakes the two `AGENTCORE_LLM_GATEWAY_*` env vars and a scripted double that speaks **the gateway protocol** (`e2e-core/src/codex_standin/stack.py:55-86`, `fixtures_app.py:399-413`; declared gap in `report.py:36-43`). That double skips the real gateway and always answers `cost_usd:"0"`, so cost/budget behaviour is not exercised end to end.
- World assets: one profile `pulso-evolution-structured@1.0.0` with `endpoint_alias: pulso-evolution-llm`, `timeout_s: 60`, `structured: prompted`, placeholder price (`agent-core-assets/worlds/pulso-evolution/model_profiles/`); all four agents (scout, verifier, builder-design, writer) share it. Agent nodes route `answered -> done`, `gave_up -> escalate(low_confidence)` (`.../flows/pulso-scout@1.0.0.yaml:89-93`).
- Where AC calls the gateway: `agent` nodes (via `LLMAgentPort`), `respond` nodes with `generate` (M8, falls back to a **template** on any non-`invalid_output` error: `AC:agent_core/response/responder.py:120-122`), and `llm_structured` decision providers. An `agent`-node `GatewayError` is absorbed: usage is charged, `agent_step failed(error_kind)` is emitted, node returns `gave_up` (`AC:agent_core/interpreter/handlers/agent.py:172-178`). Only M8 `respond` has a "template fallback"; our evolution world has no `respond/generate` nodes (the attention demo does).

### 2.2 Target topology and secrets
```
engine (Rust) --> control-api/worker --> pulso-core-runtime --HTTPS/HTTP, Bearer consumer token--> llm-gateway --> provider(s)
                                          (no provider keys, no provider egress)                    (provider keys, only egress)
```
- Runtime env: `AGENTCORE_LLM_GATEWAY_URL` (private DNS name of the gateway) and `AGENTCORE_LLM_GATEWAY_TOKEN` (consumer `pulso-core-runtime`). **Remove** `LLM_ENDPOINTS` and every provider key from runtime and compose; the runtime never holds a provider key.
- Gateway env: `GATEWAY_CONSUMERS={"pulso-core-runtime":{"token_env":"GATEWAY_TOKEN_PULSO_CORE_RUNTIME"}}`, `LLM_ENDPOINTS` with per-stage aliases (2.5), one key variable per alias, optional `JEV_API_KEY`.
- Engine and bridge workloads get **no** gateway token (they do not call models). Only `pulso-core-runtime` is a consumer, so the gateway's `consumer` log field identifies our runtime and a leaked token is attributable.
- Option for later: two consumers in the same runtime (`pulso-core-runtime` for live, `pulso-core-runtime-eval` for evaluation) to separate accounting in gateway logs/spans. It needs a second `HttpLLMGateway` instance built by us (AC `resolve_ports` builds one). Not required for the first adoption.
- Mock/e2e use throw-away tokens (`scripted-not-a-secret` style); nothing real in the repo.

### 2.3 Where our wrappers sit (they still wrap the Core gateway port)
`HttpLLMGateway` implements the same `LLMGateway.generate(prompt, inputs_model_view, locale, schema)` port, so the stack is, outermost first:
1. `BindingGuardGateway`: refuses with `GatewayError.refused` before any network call when the invocation binding is not confirmed (`core-bridge/src/pulso_core_runtime/tools/guard.py:40-52`). Correct position; keep outermost so a refused call costs zero tokens and never leaves the process.
2. `SpendMeteringGateway`: ledger in `pulso_bridge.budget_meter` via `ReceiptStore.meter_spend` (`adapters.py:177-207`, `store/receipts.py:154-176`).
3. `HttpLLMGateway` (AC): sends profile+price from the registry (our pinned world) and `labels` {`prompt, model_profile, run_id, turn_id, session_id, release, agent`}; tenant/job/stage are **not** labels (closed key set), so join through `run_id` against our binding table.

Defects to fix in (2), all verified in code:
- **D1 failed calls are not metered.** `generate` calls the inner gateway first and only meters on return; `GatewayError(invalid_output|refused, tokens, cost)` propagates unmetered (`adapters.py:196-198`), although the provider charged. Meter `exc.cost_usd/tokens` before re-raising.
- **D2 over-cap spend is dropped.** `meter_spend` inserts only if the new total stays <= cap (`receipts.py:166-173`), so the call that crosses the cap is never recorded and the ledger under-counts real spend. Record it (new `meter_spend(..., force=True)` or a second "overrun" column) and then refuse subsequent calls.
- **D3 no pre-reservation.** Concurrent calls can each pass; worst case overshoot = N x (`max_tokens` x output price + estimated input). Reserve `max_tokens x price_out + tokens_est x price_in` (from the profile that will be sent) before the call, settle to actual afterwards, release on `timeout` as **unknown** (V3 `AC` text: "Timeout posterior al envio conserva unknown/reserva hasta readback"; the gateway has no idempotency, a timed-out call may still have billed).
- **D4 `usage_known` is ignored.** `meter_spend` has no such parameter in this path; a `usage_known:false` success must mark the meter row `usage_known=false` and must not release the reservation (V3 line 1109).
- **D5 outcomes are not recorded.** The wrapper sees every `GatewayError.kind` but stores nothing about it, which is why section 2.7 cannot distinguish infra failure from low confidence. Add a small append-only `model_call_ledger` (binding ref, stage, attempt, kind, tokens, cost, usage_known, model-as-reported, gateway `X-Request-Id` if obtainable, no prompt/text).

### 2.4 Budgets: three layers, none of them in the gateway
1. **Core per-run budgets** from the Agent descriptors (`budgets.max_cost_per_run`, `max_model_calls_per_turn`, `max_tokens_per_run`) enforced by Core using `cost_usd` returned by the gateway; correct only if the registry price is right (price and `source/as_of` are our assets).
2. **Our ledger** (`budget_meter`, cap from the sealed invocation `budget.cost_usd_max`) with D1-D5 fixed; also `PULSO_EVAL_BUDGETS`/`evaluation/budget.py` for evaluation arms.
3. **Provider-side limits** on each alias's key (per-key monthly cap, allowed models), because the gateway enforces none. This is the only hard stop against a compromised or buggy runtime and must be treated as a deploy requirement (infra/ops), until upstream adds per-consumer limits (Q1-Q3).
Plus a **registry-asset guard** in our assetcheck/compile path: a ModelProfile price must be present with `source` and `as_of`, `max_tokens` <= a per-stage ceiling, `timeout_s` <= `ALB_idle - 5`.

### 2.5 Aliases and model profiles per stage
Gateway aliases are provider routes (base URL + key); the model name and parameters come from our ModelProfile in the release. Proposed:

| Stage / use | ModelProfile (new, versioned asset) | `endpoint_alias` (gateway) | notes |
|---|---|---|---|
| Scout (`pulso-scout`) | `pulso-scout-llm@1` | `pulso-scout-llm` | exploratory, longest `max_tokens`, `structured: prompted` (agent node requires prompted) |
| Verifier | `pulso-verifier-llm@1` | `pulso-verifier-llm` | prefer a **different model or provider key** than Scout for independence (V3 line 1369: separate run/context/prompt); separate key = separate provider quota and revocation |
| Builder (design) | `pulso-builder-llm@1` | `pulso-builder-llm` | |
| Writer | none required | n/a | writer flow is mostly tools; if it gets an agent node, reuse builder profile |
| Jev | decision model `jev-evolution-route` (not an LLM profile) | n/a | still direct `HttpJevTransport` with `AGENTCORE_JEV_API_KEY` in AC 789d6c8 (`AC:agent_core/composition/serve_ports.py:45`; `jev_http.py:20`). The gateway has `/v1/jev` but **AC has no adapter for it yet**: until it lands the runtime keeps the JEV key and `api.typesafe.ai` egress (documented exception to "no provider keys in the runtime"); Q4 |
| `llm-smoke` / canary | `pulso-canary-llm@1`, tiny `max_tokens`, own alias | `pulso-canary-llm` | used by bootstrap smoke and the data-leak canary tests |

Each alias can map to the same `base_url` with a different key env. Assets: rename the current `pulso-evolution-llm`; update `assetcheck.py` alias collection (`agent-core-assets/tools/assetcheck.py:128`) to also check every alias is declared in a checked-in `gateway-aliases.json` (names and base-URL hosts only, no keys) used by compose generation and by infra notes.

### 2.6 Data-leak and egress controls
1. **No provider egress from runtime/engine/bridge**: networks enforce it (local: section 3; AWS: ADR4 item 4 + SG, "destination control" remains `dependency_blocked` per plan F6).
2. **No provider keys outside the gateway**: assert at startup that the runtime environment contains none of the names `LLM_ENDPOINTS`, `*_API_KEY` except the documented `AGENTCORE_JEV_API_KEY`; add a readiness/doctor check (`llm_keys_not_in_runtime`).
3. **What reaches the provider** is the Core `inputs_model_view` (Core already tokenizes/limits the model view; the gateway does not redact: `GW:docs/consuming.md` "Data hygiene"). Our controls stay upstream of the call: treated inputs, `purpose`, binding guard. Provider retention/region is a contract matter (V3 `PulsoModelProfile`), outside the gateway.
4. **Logging policy**: runtime logs only `kind, model, cause`; the gateway logs no content (verified); do not enable any content capture in OTEL; `labels` carry only ids. `/internal/v1/version` must list the upstream as a double when local (`llm-upstream:scripted`).
5. **Token hygiene**: the consumer token is only in the runtime env and the gateway env; never in receipts, ledger rows, exports, `version` or logs.
6. **Canary tests** (section 3.4): provider-key canary, consumer-token canary, prompt-content canary, egress canary.
7. **Tampering risk**: the registry release chooses model and price. A compromised publish path could pick an expensive model or a zero price. Mitigations: assetcheck/compile guard (2.4), approval gate, provider-side key limits, and (ask) gateway-side allowlist (Q1).

### 2.7 Failure modes: fail closed, never a silent template
| Situation | Today | Required behaviour |
|---|---|---|
| Env vars absent | `UnconfiguredLLMGateway`: every call `unavailable` with only a log line | Runtime refuses to start (config error, exit code like other missing config) in every profile **except** an explicit `PULSO_LLM_MODE=disabled` used by fixture tests; `/readyz` includes `llm_gateway`. We own `main.py`, so this is a wiring check before `resolve_ports`, not an AC change |
| Half pair / bad URL | AC reports a config problem (good) | keep |
| Gateway unreachable at runtime | `GatewayError.unavailable` | agent node: `gave_up`, see below; `respond/generate` nodes: Core falls back to the **template** (M8 behaviour) |
| Bad/rotated token | gateway 401 -> AC maps to `unavailable` (indistinguishable from outage) | auth probe at readiness and every N seconds (empty-body POST: 400 = ok, 401 = bad token); log `llm_gateway_auth_failed` once, flip readiness to not-ready |
| `invalid_output` | Core regenerates once | keep; meter every attempt (D1) |
| `rate_limited`, `timeout` | agent node gives up | job-level retry with a new attempt number and fresh reservation (never inside Core) |
| Timeout after the request left | usage unknown | keep reservation as unknown until reconciled; do not auto-retry the same attempt (V3: "no se asume idempotencia") |

Agent-node outage semantics (the important one): a `GatewayError` in an `agent` node ends as `esc_gave_up` -> `escalate(reason_code: low_confidence)` (flow lines 89-93). That is a **typed escalation that means "model could not conclude"**, and the engine could record it as a negative finding. Required: the invoke/TaskAdapter must classify a stage outcome as `dependency_unavailable` (engine: `waiting_dependency`/`failed_infra`, no finding, no "negative result") when the `model_call_ledger` (D5) has any `timeout|unavailable|rate_limited` row for that attempt, regardless of the Core escalate reason; V3 already specifies "agent_step failed/error_kind, gave_up seguro, senal con denominador, no exito ni coste conocido inventado" (V3 line 1121) and failed nodes carry `error_kind` in the event (`AC:agent_core/domain/events.py:177`). Using our ledger avoids depending on the export pipeline.
For the attention-demo world (`respond/generate`) the template fallback is by design in Core; the runtime marks that world's runs `degraded_generation` through the same ledger and we document it as a double-labelled behaviour. It must never apply to evolution stages (they have no `generate` respond nodes; add an assetcheck rule that forbids them in `pulso-evolution`).

### 2.8 Idempotency and retries
- Gateway: none. `HttpLLMGateway`: none (one POST). Core: one regeneration on `invalid_output`.
- Ours: job/stage-level idempotency already exists via command key and receipts; model-level retries are a new **attempt** (new `attempt` in `budget_meter`), never a hidden retry. Backoff for `rate_limited` is an engine/worker decision using the `error_kind` surfaced by D5.
- Because HTTP calls can be duplicated by a client library retry or a proxy, the runtime's `httpx.Client` must not enable transport retries (AC default `httpx.Client()` has none: `AC:http_gateway.py:50` constructor); add a test that asserts one request per `generate` against the double.
- Latency: client timeout = `timeout_s + 5` (`AC:http_gateway.py:37,72`). Our current profile has `timeout_s: 60`, which is **above the ALB default idle timeout of 60 s** that ADR4 item 3 warns about: either infra sets idle timeout >= 300 s (or uses service discovery/Service Connect) or our profiles stay <= 50 s. Assetcheck should enforce the ceiling (2.4).

---

## 3. Local stack and tests

### 3.1 `local/core` compose changes (Claude-owned paths)
Add to `local/core/compose.core.yaml` (profiles `real_local` and, when e2e needs it, `fixture`):
- `llm-gateway`: image `${PULSO_LLM_GATEWAY_IMAGE:-localhost/llm-gateway:unset}` built from a **pinned checkout** (`references/llm-gateway` at SHA, same convention as `references/agent-core`; script `local/core/lib/llmgw.ps1` builds with `podman build` from a clean `git archive`, tag `llm-gateway:<sha7>`, checks `HEALTHCHECK` is not relied on). Environment: `GATEWAY_CONSUMERS`, `GATEWAY_TOKEN_PULSO_CORE_RUNTIME` (generated into `core.env`, like other secrets), `LLM_ENDPOINTS` (aliases of 2.5 -> `http://llm-upstream:9000/v1`, key envs `LLM_KEY_SCOUT` etc. = throw-away generated values), `OTEL_EXPORTER_OTLP_ENDPOINT` -> the existing collector fragment when present. Compose `healthcheck: test: ["CMD","/llm-gateway","-healthcheck"]`, `mem_limit: 64m`, runner labels (cgroups disabled) like every service.
- `llm-upstream`: the scripted OpenAI-compatible **double** (labelled `com.pulso.role: double`), implemented in `local/core/doubles/run_doubles.py` as a new port (for example `SIM_LLM_PORT=8631`), speaking `POST /v1/chat/completions` with the scenarios used in my probe (ok, fenced JSON, no usage, 429, 500, slow, content_filter, truncated) plus admin endpoints `/_e2e/config` (scripted rules, reuse `world.llm_answer` rule format from `e2e-core`) and `/_e2e/captured` (requests received, for the canary tests).
- `core-runtime`: replace `LLM_ENDPOINTS`/`PULSO_LLM_API_KEY` with `AGENTCORE_LLM_GATEWAY_URL: http://llm-gateway:8080` and `AGENTCORE_LLM_GATEWAY_TOKEN: ${GATEWAY_TOKEN_PULSO_CORE_RUNTIME}`; `depends_on: llm-gateway: {condition: service_healthy}`. Update `Grants.Tests.ps1:30-31` accordingly.
- Networks: `core-net` (existing) with `llm-gateway` aliased `[llm-gateway]`; new `llm-egress-net` that contains **only** `llm-gateway` and `llm-upstream`. The runtime is not on it, so it cannot resolve or reach the upstream (egress canary). The same shape maps to the AWS SG rule "provider egress only from the gateway workload".
- The local port rule: no host ports in the includable fragment (current rule); the gateway is reachable only inside `core-net`; any host publishing for debugging uses `127.0.0.1` and a unique port from `lib/ports.ps1`.

### 3.2 e2e-core changes
- Remove the image overlay that bakes `AGENTCORE_LLM_GATEWAY_*` and the gateway-protocol double at `/llm/v1/generate`; the stack now provides the real gateway + upstream double. `stack.core_env_lines()` writes only the generated token pair names the compose consumes.
- Point the scripted rules (`/_e2e/config llm_rules`) at the **upstream** double's admin API; same rule format, so existing live tests keep their scripts.
- Set non-zero prices in e2e profiles so cost/budget assertions are real: `cost_usd` now comes from the real gateway arithmetic, and `bud-e2e` (cap 5 USD) is exercised.
- `report.py` declared gap `llm_gateway_env_not_passed_through_compose` is closed.

### 3.3 Test plan (strict TDD; first RED per item)
Unit (`core-bridge/tests/llm/`, no containers):
1. `HttpLLMGateway` through our wrapper stack with `httpx.MockTransport`: success, each error kind with and without usage, 401 -> `unavailable`, undecodable body, one request only per call, `traceparent` and `labels` present.
2. Metering D1-D5: failed call with usage is metered; the crossing call is recorded then subsequent calls refused; reservation released/settled; `usage_known:false` sets the flag; concurrent calls cannot exceed cap + one in-flight reservation (threads against real PG in the existing PG test pattern, `PULSO_TEST_PG_ADMIN`).
3. Fail-closed startup: missing env/half pair/bad URL/runtime env containing a provider key name -> exit config error; `PULSO_LLM_MODE=disabled` allowed only when explicit and is reported in `doubles[]`.
4. Readiness: probe semantics (400 = ok, 401 = not ready, connect error = not ready), non-blocking and cached.
5. Outcome classification: `escalate(low_confidence)` + ledger `timeout|unavailable|rate_limited` -> `dependency_unavailable`; same escalate with only `invalid_output` -> stays low confidence.
6. Contract test against the pinned gateway OpenAPI (`references/llm-gateway/api/openapi.yaml`): every ModelProfile in `agent-core-assets` produces a request that validates against `GenerateRequest` (decimal string prices, ranges, label keys, `timeout_s <= 300`), plus recorded request/response fixtures from the real container (generated by script, checked in) so unit tests do not drift.
7. Assetcheck: aliases declared in `gateway-aliases.json`; price has `source`/`as_of`; no `respond/generate` in `pulso-evolution`; `timeout_s <= 50`.
Integration (Podman `pulso-dev`, throw-away namespace, real gateway container + upstream double):
8. Real gateway matrix: the same scenarios as my probe through `HttpLLMGateway` and our wrappers (success cost equals price arithmetic; no-usage; each error kind; slow -> `timeout`; gateway stopped mid-run -> stage `dependency_unavailable`, never completed, never a template).
9. Budgets end to end: cap exhausted mid-stage stops the next call; two parallel stages share nothing but their own rows.
Live e2e (`e2e-core/tests/live`): scout stage happy path through runtime -> gateway -> upstream with scripted hypotheses; outage test (stop `llm-gateway`) expecting `waiting_dependency`; token rotation test (restart gateway with new token, runtime readiness flips, recovers after runtime restart).

### 3.4 Canary tests (data-leak)
- **Provider key canary**: gateway key env = `CANARY-PROVIDER-KEY-<uuid>`. After a run, assert it is absent from: runtime env/`/proc` of the runtime container, runtime logs, all bridge/runtime/eval DB dumps, export outbox, receipts/artifacts, ingest/control-api double captures, `/internal/v1/version`; present only in the gateway env and in the `Authorization` captured by the upstream double.
- **Consumer token canary**: same assertions for the runtime->gateway token (present only in gateway and runtime env).
- **Prompt content canary**: put `CANARY-INPUT-<uuid>` in a briefing/wiki input; assert it **is** in the upstream double capture (it must reach the model) and **absent** from gateway logs, runtime logs, OTLP spans collected from the gateway, and DB tables other than the evidence store that already holds it by design.
- **Egress canary**: from inside the runtime container, TCP to `llm-upstream:9000` and to an external address must fail; from the engine/bridge containers likewise; from the gateway the upstream must succeed.
- **Price canary**: profile price of `1000000` and a 1000/500 call is rejected by the assetcheck guard and by the runtime pre-reservation (never reaches a 1500 USD call).

---

## 4. Infra implications for OUR infra (notes only, infra is separate)
- ADR4 is accepted but "nothing is declared in Terraform and nothing is deployed". Alignment items for our side:
  - **ADR 0003 (ours) must change in the same PR pair** as ADR4's consequence: remove `LLM_ENDPOINTS`, per-endpoint keys and provider hosts from the `pulso-core-runtime` contract; keep `AGENTCORE_JEV_API_KEY` and `api.typesafe.ai` until AC consumes `/v1/jev` (ADR4 assumes Jev has already moved; AC 789d6c8 has not: Q4).
  - V3 CAP-50 (`LLM_ENDPOINTS`), CAP-60 variables list and CAP-62 network row (V3 lines 2583, 2692, 2721) and plan F6 ("`core-runtime` -> NAT -> 443, `api.typesafe.ai` + `LLM_ENDPOINTS` hosts") are now stale: runtime needs gateway reachability, not provider egress.
- New secret entries (names only; values out of band): `GATEWAY_TOKEN_PULSO_CORE_RUNTIME` in **both** the gateway task and the `pulso-core-runtime` task (same value, two consumers of one entry, readable by exactly those two roles); one provider key per stage alias; `JEV_API_KEY` for the gateway if/when `/v1/jev` is adopted. Rotation: new token = restart gateway and runtime (Fargate env secrets change only with a new task, same as our key files, ADR 0008 item 6); support two tokens per consumer upstream would allow zero-downtime rotation (Q6).
- Network: `pulso-core-runtime` SG egress only to the gateway SG on 8080 (plus its other private dependencies); gateway SG ingress only from the runtime SG; gateway is the only workload with `controlled_nat`; destination control stays `dependency_blocked` as in plan F6 (an open 443 rule does not prove "only these hosts").
- Reachability: ALB internal vs service discovery is open in ADR4. If ALB: idle timeout >= 300 s or all our profiles `timeout_s <= 50` (our current profile is 60: conflict, see 2.8). TLS: runtime-to-gateway should be https in staging/prod; the runtime accepts http(s) (AC validates scheme only).
- Health: ECS container health command `["/llm-gateway","-healthcheck"]` must be declared in the task definition (distroless, no shell; the image HEALTHCHECK is not honoured by OCI builds); target-group health `GET /healthz`.
- Deploy order addition (CAP-62): gateway healthy -> runtime updated -> readiness (includes the gateway auth probe). Rollback: previous digest pair.
- Observability: gateway spans via OTLP to the same collector; alarm on gateway 5xx rate and on runtime readiness `llm_gateway` failing; spend dashboards come from our ledger, not from the gateway.
- Image pinning: infra deploys only a digest; the first `v0.x.y` tag has never been published (release workflow never ran): blocker for staging.

---

## 5. Consequences for V3 (amendments to record, not applied here)
- Line 798, 758-762 and the model-integration sections still say `OpenAICompatGateway`/`LLM_ENDPOINTS` and "no building a gateway"; replace with: external **llm-gateway** service consumed through `HttpLLMGateway` (AC ADR 0024); no proxy of ours; the Pulso side owns metering, reservation, binding guard and outcome classification.
- CAP-50 table: `LLM_ENDPOINTS` row becomes gateway-side; add `AGENTCORE_LLM_GATEWAY_URL/TOKEN`; "alias absent" becomes the gateway-side `unavailable` plus our readiness/bootstrap check.
- `ModelReceipt` fields `provider_request_id` and a true `resolved_route` **cannot be filled** from the gateway (it returns only `model` as reported by the provider); record `model_as_reported`, gateway request id (our own `X-Request-Id`, which the gateway echoes) and mark provider id as unavailable (Q5).
- These go into `docs/V3_SUCCESSOR_AMENDMENTS_CLAUDE.md`-style amendment, not into the canonical V3 file.

## 6. What the Rust engine (Codex) needs to know
Verified: the engine never calls LLMs directly.
- V3 line 5 (scope correction), 798 and 762: models are accessed only through Core's gateway port; `ModelInvocation`/`ModelReceipt` are internal Pulso DTOs and "no hay endpoint proxy propio"; the consumer "reserva cuota ... vía Core". Plan line 24: Claude's runtime composes Core; Codex does not import Python. A scan of `D:\.codex\factored\improvement-engine` (`*.rs, *.toml, *.yaml, *.md, *.tf`) finds no references to OpenAI/Anthropic/OpenRouter/`chat/completions`/`LLM_ENDPOINTS`/`LLM_GATEWAY`/`/v1/generate`/`api.typesafe`/`JEV_API_KEY`.
- Therefore: no gateway URL, token, endpoint alias or provider key in engine/worker/control-api environments, SGs or compose; the engine's only model-related surface is task invocation and the receipts it reads back. If a Codex simulator ever needs a model it must ask the runtime for a task stage with its own `purpose`/budget (V3 line 523); it must not open a second path to the gateway.
Asks to Codex:
1. Add a typed outcome for a stage ended by model dependency failure: `dependency_unavailable` (reason `model_timeout|model_unavailable|model_rate_limited`), mapped to `waiting_dependency`/job retry with backoff, never to "no finding / negative result". We will surface it in the stage receipt (from our ledger, D5), not only in Core's `escalate(low_confidence)`.
2. Receipt DTO: accept `usage.cost_known=false`, `usage_known=false` as first-class and per-attempt `cost_usd`/tokens including failed attempts (D1); reservation semantics unchanged (unknown until reconciled after timeout).
3. Do not add engine-side retry of a model stage within the same attempt/command key; a retry is a new attempt with a new reservation.
4. Budget fields in the sealed invocation (`budget.cost_usd_max`) are authoritative for our ledger cap; confirm no other budget channel exists.
5. Confirm they do not rely on `ModelReceipt.provider_request_id` / `resolved_route` being present (gateway cannot provide them).
6. Local stack: nothing to change on their side except tolerating the new compose service names if they consume `local/core` output (we only add services).

## 7. Questions for the llm-gateway / agent-core humans (to relay)
Gateway:
- Q1 Per-consumer policy: allowlist of `(endpoint_alias, model)` and maximum `price`/`max_tokens`/`timeout_s` per consumer (today any authenticated caller can pick any model and any price up to 1,000,000 USD/Mtok). Is this planned, or should all cost control stay at provider keys?
- Q2 Server-side rate/concurrency limit per consumer and per alias (today 120 parallel calls all pass) and a configurable maximum in-flight.
- Q3 Server-side spend accounting or at least token/cost fields in the `request` log line (today only spans carry usage), so an independent ledger can audit our metering.
- Q4 `HttpJevTransport` direct vs `/v1/jev`: is there an agent-core change planned to consume the gateway's JEV route? ADR4 and ADR 0024 both assume the JEV key leaves agent-core; AC 789d6c8 still reads `AGENTCORE_JEV_API_KEY` and calls `api.typesafe.ai`.
- Q5 Can the response (and error) carry a provider request id and the resolved route/provider alias, for audit receipts?
- Q6 Two active tokens per consumer (rotation without downtime) and an authenticated check route (`GET /v1/whoami` or authenticated `/readyz`) instead of our empty-body POST trick.
- Q7 Idempotency: any intent to accept an `Idempotency-Key` and dedupe within a window, or to forward one upstream? A timed-out call may still bill and we cannot detect it.
- Q8 First release: when is `v0.x` tagged and the GHCR digest published? Is GHCR pull from AWS planned (private repo) or ECR mirroring (infra owns)? Also build the image with `--format docker` or document that HEALTHCHECK is ignored.
- Q9 `usage` handling: non-integral usage is treated as `unavailable` (design doc line 75): which providers have you seen? Native `response_format` support per provider is router-dependent: do you recommend `prompted` universally (our agent node requires it anyway)?
- Q10 Error `message` strings are Spanish (`schema: ... palabra clave no soportada`); fine for logs, but can a stable `code` field be added?
Agent-core:
- Q11 Should `UnconfiguredLLMGateway` remain the default when env is absent, or can `serve` offer a strict mode (fail startup) so consumers need not reimplement the check?
- Q12 `HttpLLMGateway` maps `unauthorized` to `unavailable`: can it log or expose a distinct reason (counter) so readiness can alert on a bad token?
- Q13 Can `labels` accept `tenant`/`job`/`stage` (or a free `trace`-style key set) so provider-side and gateway-side logs join to our ledger without `run_id` lookups?
- Q14 `LLMAgentPort` does not propagate `usage_known` (V3 line 1109 residual): any plan to fix it, so budgets can treat unknown cost correctly?
- Q15 Client reuse: is `HttpLLMGateway` safe for concurrent runs (single `httpx.Client`) and what is the expected connection-pool size for parallel stages?

## 8. Prioritised implementation backlog (disjoint paths)
Order reflects value/risk. Work packages touch disjoint paths so they can run in parallel; wiring lines in `main.py`/`internal/app.py`/`pyproject.toml` are owned by the L3a agent and listed as "wiring needed".

| P | WP | Paths (owner Claude unless stated) | Content | Depends on |
|---|---|---|---|---|
| P0 | WP-A Metering v2 | `core-bridge/src/pulso_core_runtime/llm/{metering.py,ledger.py,classify.py}`, `core-bridge/src/pulso_core_runtime/store/receipts.py` (add reservation/outcome SQL only), `core-bridge/tests/llm/test_metering_*.py` | D1-D5, `model_call_ledger` table, outcome classification helper | none |
| P0 | WP-B Fail-closed config and readiness | `core-bridge/src/pulso_core_runtime/llm/{config.py,probe.py}`, `core-bridge/tests/llm/test_config_*.py,test_probe_*.py` | env validation (no provider keys in runtime, both vars), auth probe, readiness check object `llm_gateway_check(...)` | none |
| P0 | WP-C Local stack | `local/core/compose.core.yaml`, `local/core/lib/llmgw.ps1`, `local/core/profiles/*.env.example`, `local/core/doubles/{llm_upstream.py,run_doubles.py}`, `local/core/tests/*.Tests.ps1` | gateway + upstream double services, networks, healthcheck, generated tokens, ref pinning script | none |
| P1 | WP-D e2e-core | `e2e-core/src/codex_standin/{stack.py,fixtures_app.py,report.py}`, `e2e-core/tests/**` | remove overlay and protocol double, rules to upstream double, non-zero prices, outage and rotation tests, canaries | WP-C |
| P1 | WP-E Assets and assetcheck | `agent-core-assets/worlds/pulso-evolution/model_profiles/**`, `agent-core-assets/gateway-aliases.json`, `agent-core-assets/tools/assetcheck.py`, its tests, affected `releases/` and `expected-state.json` | per-stage profiles/aliases, price source/as_of, ceilings, forbid `respond/generate` in evolution | none (digests regenerate) |
| P1 | WP-F Wiring (L3a owner) | `core-bridge/src/pulso_core_runtime/main.py` (wire: readiness check, metering v2 swap at line 277, startup validation), `core-bridge/src/pulso_core_runtime/internal/app.py` if a route is added | single wiring PR consuming WP-A/B | WP-A, WP-B |
| P2 | WP-G Contract tests | `core-bridge/tests/contract/test_llm_gateway_contract.py`, `core-bridge/tests/contract/fixtures/llm_gateway/**`, `references/llm-gateway` pin note | OpenAPI validation of all profiles, recorded fixtures | WP-E |
| P2 | WP-H Docs | `core-bridge/docs/adr/0009-llm-gateway-consumer.md`, `core-bridge/docs/journal/claude-00NN-llm-gateway.md`, `core-bridge/docs/flows/llm-gateway-calls.md`, `core-bridge/README.md` env table, `docs/V3_AMENDMENTS_LLM_GATEWAY_CLAUDE.md` | ADR, flows, amendment list (section 5) | none |
| P2 | WP-I Cross-team notes | `docs/` (no code): infra notes (section 4), Codex asks (section 6) as an agreement entry for the plan Section 16 ledger | Codex/infra owners decide | none |
| P3 | WP-J JEV via gateway | after Q4 | switch the Jev provider to `/v1/jev` once AC ships it; then drop `AGENTCORE_JEV_API_KEY` from runtime | upstream |
| P3 | WP-K Gateway-side controls | upstream | adopt Q1-Q3/Q6 when available; until then provider-key limits are mandatory | upstream |

Immediate first slice (about one agent-day): WP-B + WP-C + WP-A tests-first, then WP-F; it yields a runtime that fails closed, a local stack with the real gateway, and correct metering of failed calls, which are the behaviours the V3 spec cares about most.

## 9. Risks and open items
- The gateway repo is a few hours old (3 merged PRs, no tag, no published image). Pin the SHA, and expect contract additions (`/v1` is additive-only per its decisions doc).
- Spend accuracy depends on **our** registry prices; wrong price = wrong budget. The assetcheck guard and the provider-side caps are the compensating controls.
- `timeout_s` 60 versus ALB idle 60 s is a latent production failure (2.8, 4).
- Unverified: real provider behaviour (no live key was used by anyone, per the gateway decisions doc); the gateway's `go test -race` (not run here); network behaviour on AWS (Section 4 is design only).
