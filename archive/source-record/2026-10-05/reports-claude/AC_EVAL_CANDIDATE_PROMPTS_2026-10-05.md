# agent-core `evaluate` never exercised candidate prompts (analysis and fix)

## Where the binding happens
- `RegistryService.evaluate` (registry/service.py) builds `EvalTarget("candidate", cand.release, SnapshotRegistry(cand.release, cand.entities))`
  (and the same for base). `Candidate.entities` is the FULL exact-ref closure of the candidate release (agent, flows, prompts,
  templates, profiles, decisions...), so the engine's `registry` (flows, `resolve_ref`, `Responder`, `LLMAgentPort`) already sees the candidate.
- `EngineScenarioHarness.run` (composition/evaluation.py) passes `registry=target.registry` to `build_turn_engine`, BUT
  `gateway=_ProbingGateway(self._gateway)`: ONE gateway shared by all targets, built in `serve_ports` as
  `HttpLLMGateway(pg_registry, url, token)`, i.e. bound to the LIVE Postgres registry.
- `HttpLLMGateway.generate(prompt_ref)` does `self._registry.get(prompt_ref, Prompt)` + the `ModelProfile`: the candidate ref
  (`p/resumen_radicado@1.0.1`) does not exist in the live registry, so the call fails, the responder falls back to the template.
  A text-identical bump therefore "fails" the assertions the base passes (base ref resolves live).

## Smallest additive design
No overlay class needed: the candidate closure is already a registry. Bind the gateway to the target's registry.
1. `HttpLLMGateway.bound_to(registry)`: same client/token/url, other registry.
2. `EngineScenarioHarness(..., bind_gateway: Callable[[RegistryPort], LLMGateway] | None = None)`; when given, each run uses
   `bind_gateway(target.registry)`; when None, behaviour is exactly as before.
3. `build_registry_service_for_serve` passes `ports.gateway.bound_to` when the gateway is an `HttpLLMGateway`
   (Unconfigured/other gateways: unchanged).
Effect: base is evaluated against base entities, candidate against candidate entities; non-LLM paths unchanged.
~25 lines of code. Tests: bound_to resolves another registry's prompt (respx); harness with `bind_gateway` shows the candidate
prompt text in events and the base keeps its own; without binding the old behaviour is unchanged.

## Caveat
agent-core's scorer does not read response text, so the native assertions only see candidate prompts through outcome/fallback/
`response_failed`; wording checks remain probes (REG1).
