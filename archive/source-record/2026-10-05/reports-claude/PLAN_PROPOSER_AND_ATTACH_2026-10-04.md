# Consolidated plan v2: how Pulso integrates with agent-core and support-platform

Status: DRAFT v2 for iteration with the user (consolidates rounds 1-4). Nothing in sections 6-9 has been started: the user has NOT given the go-ahead to implement the attach/reasoning work.
Date: 2026-10-04. Author: Claude (orchestrator).
Evidence (same folder): `SPIKE_B0_AGENTS_2026-10-04.md` (verified file:line answers), `PLATFORM_ATTACH_PLAN_2026-10-04.md`, `INTEGRATION_AND_DEMO_PLAN_2026-10-04.md`,
`STAR_STORY_QUEJAS_2026-10-04.md`. Pending: `ARTIFACT_KINDS_AND_EVALS_PLAN_2026-10-04.md` (per-kind authoring + eval anatomy; sections 7-8 will be refined with it).
Legend: **[V]** verified in code/docs, **[I]** inferred, **[?]** unknown. No requests to Codex for now (user decision).

## 1. The vision in one page

support-platform is THE real application. agent-core is already integrated INTO it (copilot `copiloto-asesor`, assistant `recepcion`, `disputas`, `consultas`, builder `constructor-chat`, registry, tools).
Our engine sits underneath, as a separate service:

1. it WATCHES the data (platform events, the bank dataset, E0) and DETECTS signals deterministically (done);
2. it REASONS about a verified signal with three agents (Scout, Verifier, Builder) that are agents we develop with agent-core and invoke from our service;
3. it PROPOSES an improvement to a REAL agent-core artifact (a prompt change, an eval suite, later templates/policies/flows/decisions/tools/a new agent) and, ideally, also the TEST CASES that evaluate it;
4. it creates and freezes the proposal in the agent-core registry, with provenance and evidence. From there agent-core manages it (evaluation, approval state, publication) and tells the platform SPA ("there is an improvement proposal, approve it?");
5. a human approves in the platform (step-up/TOTP), staging moves, and agent-core's `release.*` / `run.closed` events tell the engine what happened.

Responsibility line: WE detect, reason, propose, write the proposal. agent-core MANAGES proposals (state, evaluation, approval, publish) and is the one that surfaces them to the SPA. We do not build platform screens; we leave forwardable asks.

## 2. Decisions taken by the user (binding)

1. Same agent-core (no Pulso-owned Core, no separate wiki runtime). The spec's "Core externo with own agents" is dropped.
2. Reasoning agents are NEW agent-core agents, similar to `constructor-chat`, invoked from our service. Three agents: Scout, Verifier (independent), Builder.
3. Everything runs on three data sources: the bank dataset, E0, and the Product team's data model = platform contract 1.2.0 (derived from platform head `eeb73a8`).
4. Triggers: `explicit` + `scheduled` are enough; `window_complete` and `data_loaded` only if cheap; agent-core `release.*`/`run.closed` events are very valuable (outcome trigger).
5. Relax conditions everywhere: simplest thing that works, 2-3 hour increments.
6. Star story: complaints ("quejas"), with the platform's Automatización experience (case-type maturity -> proposed agent) as the reference UX. Real model allowed with synthetic data; E0-derived TREATED aggregates allowed to the model (scanner stays on, raw rows/ids/free text blocked).
7. AWS is the least important point; adjust to the Free Plan; a different background agent applies infra.
8. No go-ahead yet for the attach/reasoning implementation; keep iterating on this plan.

## 3. Architecture and data flow

```
support-platform DB (events, cases)  [theirs]     bank dataset + E0 (Parquet/CSV -> raw/augmented)  [data team, loaded by user]
        \                                              /
         v   read-only source adapters (sources crate, done) + watermark
ENGINE `pulso run` (ours)  --  triggers: explicit | scheduled | (window_complete, data_loaded) | outcome
  detect   rust-events sensor (replication, discards, k>=10)                      [done]
  reason   Scout -> Verifier -> Builder  (sections 6)                             [gap]
  compile  ChangeSpec -> draft artifact (BK0-validated); eval cases (section 8)   [partial]
  write    create+put_draft+freeze proposal in agent-core registry (auto_detect)  [minimal, section 9]
  ledger   viable | not_viable | not_evaluable (+ reason) per proposal             [done]
        |
        v  agent-core registry/Core [theirs]: native evaluation, state, notifies SPA
        v  support-platform SPA [theirs]: human approval with step-up; publish -> staging
        ^  agent-core events: /v1/export/runs, /runs/{id}/events, /registry-events (pull, exporter role)
ENGINE debug-console (ours): runs, panels, Automatización replica = preview/backoffice only
```

## 4. Inputs

| Source | Mode | How read | Status |
|---|---|---|---|
| Platform events/cases (contract 1.2.0: 39 admitted event types, free text dropped) | `platform` | `product-sqlite` / `product-postgres` adapters, `event_log.sequence` watermark | adapters + sensor done [V]; platform has no case-type, no draft dispositions, no tool-use events [V] |
| Bank dataset (13 CSV tables; complaints, contacts) | `dataset` | Parquet -> Postgres `raw/augmented` via loader; aggregate-only projections | loader + DDL done [V]; user uploads data |
| E0 (9 operational tables, 2000 disputes) | `dataset` | local treated aggregates (k>=10) | script done [V]; E0 has no draft/suggestion rows [V] |

Signals the Rust sensor finds today (per language/channel cell): reassignment rate, recurrence rate, first-response and resolution delay; discards named. Case-type maturity metrics (repeated question, tool use, draft acceptance over 100) are computable from E0 for stage 1->2 only; the rest comes from a SIMULATED draft stream, labelled.

## 5. Triggers

| Kind | Fires on | Status |
|---|---|---|
| `explicit` | CLI/HTTP "run now" with idempotency key | CLI done; HTTP endpoint small |
| `scheduled` | poll interval, new batch after watermark, history gate (14 days, 200 cases) | done |
| `window_complete`, `data_loaded` | window closes / new `_batch_id` | only if cheap |
| `outcome` | agent-core `release.*`, `run.closed` (and registry events) for our proposals | next after the core path; pull-only [V]; poll with overlap, dedupe on `event_id`; needs the exporter role |

All triggers carry `tenant`, `mission`, `source`, `config digest`; `trigger_key = SHA256(...)` makes duplicates impossible (spec §563).

## 6. The reasoning agents (Scout, Verifier, Builder)

Facts that shape the design [V from spike B0]:
- `constructor-chat` is a conversational agent: collect -> an `agent` node (ReAct, structured output `{changes[]}`) -> in-process tools `create_proposal`, `put_draft`, `validate` as `constructor-bot` -> respond. LLM calls go through llm-gateway; Jev is used only by the Understand node.
- Agent definition = registry YAML entities (agent, flow, prompt, template, tool, model_profile) with a closed node catalogue. A NEW agent enters via `agentcore registry import` (CLI with DB access, admin human at step-up, creates staging and prod at once, no HTTP route) or via the proposal API (needs an eval_suite, human approve at step-up, publish, promote).
- `POST /v1/runs` returns only `end.output_map` of primitive slots; rule G0-22 forbids exposing an agent node's output. So the Core CANNOT return a model's structured JSON over HTTP. Workaround (derived, not yet tried): the agent calls a read-class tool `pulso/submit_*`; our service receives the args, validates and stores them.
- HttpToolExecutor (ADR 0025) posts to ONE global tool-service URL + token per Core; `pulso/*` tools work only if our service IS that tool service or the operator runs a composite `--tools` factory. Our pin `c814c2b` lacks the executor (has the factory hook).
- Jev key is NOT needed for agents without understand/decide; needs `AGENTCORE_LLM_GATEWAY_URL/_TOKEN` + a gateway alias + OpenRouter key. Per-principal limits 30 hits/min, 5 USD/day (x10 for `service`), per-agent budgets we choose, 10 s tool timeout.

Agent shapes (task agents, one `agent` node each, tools backed by our service):
| Agent | Input | Output (JSON Schema validated by us) | Tools |
|---|---|---|---|
| Scout | verified signal, treated extract, memory notes | `hypotheses[]` with support/counter evidence, falsifiers | `bind_job`, `get_signal`, `get_extract`, `read_memory`, `submit_hypotheses` |
| Verifier (independent: different agent, ideally other model; sees only hypothesis + evidence) | hypothesis + evidence | per-check verdicts, `supported/weakened/refuted` | `get_signal`, `get_extract`, `recompute_metric`, `submit_verdict` |
| Builder | verified hypothesis, current text of the target artifact, allowed ops (BK0), capability list | alternatives (do nothing / change / add eval) + ChangeSpec + rationale (+ eval cases, section 8) | `read_artifact`, `list_capabilities`, `validate_changespec`, `submit_changespec` |

The model proposes, code disposes: schema, evidence refs that resolve, BK0, treated-payload scanner, deterministic recompute. A malformed/ungrounded answer is `blocked(model_*)`, never a silent fallback (ModelPort already behaves this way [V]).

Two backends behind the SAME `ModelPort` contract (roles/prompts/schemas shared):
- **Path G (now, demo):** the engine calls llm-gateway directly (already ~70% built; real model on SYNTHETIC data). Not agent-core agents, labelled as such.
- **Path C (target):** the three agents defined in agent-core, invoked via `/v1/runs`, `submit_*` tools back into our service (`CoreAgent` backend). Blocked ONLY by operator-side items outside our repos: tool-service routing, FieldClassifier entries (otherwise tool fields are tokenised), an admin importing our seed, our key in identity-keys, gateway consumer token + provider key. A Pulso-owned local core-bridge stack already has `pulso-evolution` agents if Path C must be shown (labelled as non-shared Core).
- First live check (1-2 h): the `submit_*` callback and a task run with an `agent` node (nobody has run either).

## 7. What we can propose (artifact kinds) [from attach plan section 7; refine with ARTIFACT_KINDS_AND_EVALS plan]

| Kind | Now | Notes |
|---|---|---|
| Prompt replace (e.g. `disputas` `p/resumen_radicado` 1.0.0->1.0.1; `p/copiloto`) | FEASIBLE | BK0 real-core-live; disputas is evaluable; copilot likely not (inferred) |
| Add `eval_suite` | FEASIBLE | draft-only kind; precondition for any gate; no agent has a suite today [V] |
| Templates, non-protected policies | after small BKT | protected policies never |
| Flows / decision trees | after BKF | most work; 200-node cap; needs agent bump |
| Decision models | `jev`: blocked until PR 28 reaches main; `rule`/`classifier`: feasible after BKD | to confirm alternatives in the kinds plan |
| Use an existing tool | via flow/agent change | needs tools_allowed + executor |
| New tool | blocked | ToolDef is data; real execution needs tool-service implementing it by name |
| New agent (VITAL for the user) | blocked by other kinds + first-publish-without-staging-base | paths: `registry import` (admin) or proposal API; minimal route = clone an existing agent (e.g. disputas) and change something; to be detailed in the kinds plan |
| release_settings | never by the engine | admin human only |

The Builder always lists the blocked ones as alternatives with `not_evaluable(reason)` in the ledger (honest, part of the story).

## 8. Tests: how agent-core evaluates and what the engine can define [partly pending the kinds plan]

- agent-core evaluates a proposal by running the REAL agent against an `eval_suite` (draft-only kind) with real LLM calls; caps: 20 evaluations/proposal, 1.00 USD/run budget; failure returns a gate result (409 `gate_failed` shape on `evaluate`); scenarios are customer-principal only (hard-coded), so customer-facing agents (`disputas`) are evaluable, `copiloto-asesor` probably not [V/I].
- The user's idea: our engine ALSO defines the test cases for the agents it modifies. Feasible in a simple form: N scenarios derived from the signal's evidence cells (language/channel, case type) + fixed oracle assertions, written as an `eval_suite` draft alongside the prompt change. Pitfalls to design against: circularity (the suite must not encode the improvement), development/validation/final_locked split by cohort, leakage, and what must stay human-owned (final acceptance). Anatomy (scenarios, oracles, metrics, thresholds, determinism) to be confirmed by the kinds plan before building.
- Honesty: the Core's yardstick is the platform's verdict; our structural gate is a stand-in and must not be presented as the platform's verdict.

## 9. Writer and compiler (relaxed scope; target 2-3 agent-hours)

- Minimal HTTP client to the REAL registry API `/v1/registry` (principal JWS, our key in identity-keys, role `constructor`, never `aprobador`): create, `put_draft`, `freeze`, `get`. Provenance in `origin=auto_detect`, `created_by`, title prefix `[improvement-engine]`, `docs.rationale` (<=4000 chars: evidence refs, gate results, run id, ledger digest). No Idempotency-Key at main: deterministic title + draft digest, look up before create. Quotas: 10 proposals/24 h, 20 evals/proposal.
- Compiler: one fixed template first (prompt replace + eval suite for `disputas`), BK0-validated.
- Out of the first cut: golden fixtures per problem code, close-the-loop reader, local-stack script, platform patch.
- The platform builder lists only ITS OWN DB index (not the registry) [V]: a proposal made by us is visible in the SPA only after they register/track it (their endpoint or "track by id"); no PR in their repo without the user's OK.

## 10. Surfaces

- Platform SPA (theirs): where humans see/approve proposals. Missing today: the builder/Automatización screens in the SPA (backend S16 exists; role removed) [V]. Our job: the engine API and the asks.
- Our debug-console (ours, internal backoffice): runs, panels, reasoning summaries, and the Automatización replica (`#/automatizacion`, built: maturity crate, API `/internal/v1/automation/*`, simulated draft stream, E0-treated stage 1->2, source badges). It is a preview, not the product screen.

## 11. Demo (star story: quejas)

Acts, with honest labels (doubles[] vocabulary): 1 signal (real sensor on simulated platform data or E0-treated aggregates) -> 2 reasoning (real model on synthetic data / E0-treated aggregates, Path G) -> 3 proposal compiled (real, BK0) -> 4 proposal created+frozen in the real registry and evaluated by Core (real-narrow; verdict as Core gives it; needs LLM keys, else stops at `candidate`) -> 5 human approval in the platform (theirs; simulated issuer if late), publish to staging -> optional outcome via `release.*`.
Data facts for the story [STAR_STORY]: complaints are 17% of contacts but 41% of unresolved; E0: advisors repeat the same query in 154/200 cases (stage 1->2 computable, replicated 93.1%). The spec has no maturity model; the screens come from the user's design boards.

## 12. Infrastructure (background, least priority)

Account is on the AWS Free Plan (only free-tier-eligible instance types). Applied: bootstrap (state bucket, ECR) and stage 1 network (no NAT). `free_plan` profile: core host m7i-flex.large (+ Postgres container), platform/engine t3.small, CloudFront public origin (WAF off), CodeBuild SMALL or build-on-host. A background agent applies stages 2-5 (data/IAM, images, compute, edge) and reports. The attach/reasoning work does not depend on AWS (local first).

## 13. Work plan (2-3 hour blocks; nothing below has the go-ahead except what is marked done/in flight)

Done: detection stack, panels, `pulso run` pieces, contracts 1.2.0 + drift digest, Automatización replica (reviewed), infra foundations/free_plan.
In flight (background): `pulso run` wiring (monitor -> sensor -> pipeline -> ledger), infra apply agent, kinds+evals plan (read-only).
Proposed next (awaiting go-ahead):
| Block | What | Needs |
|---|---|---|
| B1 | role contracts (JSON Schemas, prompts, validators) + ModelPort real path on the Gateway with a real model on SYNTHETIC data; Scout -> Verifier -> Builder reasoning visible in the console | gateway + model key |
| B2 | minimal registry writer + fixed compiler (section 9) against the local real registry | local agent-core stack |
| B3 | wire B1+B2 into `pulso run`: signal -> reasoning -> compile -> write -> ledger; one command | wiring lane merged |
| B4 | engine-defined eval cases (section 8) alongside the proposal | kinds plan |
| B5 | `submit_*` tool callback spike + `CoreAgent` backend (Path C), with whatever operator-side items we can get | operator items |
| B6 | broaden kinds: BKT (templates/policies), then BKF flows, then new agent path | kinds plan |
| B7 | `outcome` trigger (poll export/registry events) | exporter role |
| B8 | demo script, rehearsal, fallback (recorded replay) | B3 |

## 14. Risks

Core cannot return structured JSON over HTTP (workaround untested); Path C blocked by operator-side items; no list-proposals route or Idempotency-Key at main (stranded PRs 23/24/28) so our lookup-before-create is best-effort; LLM/JEV keys needed for evaluation; proposals invisible in the SPA until they track them; single-writer/staleness (`proposal_stale` if a human edits the draft; engine must write once and stop); model variability and cost (persisted answers, budgets, recorded fallback); platform and agent-core change daily (digest-based drift gates exist); E0 has no draft data; maturity beyond stage 1->2 is simulated.

## 15. Open decisions for the user

1. Go-ahead for B1+B2 (and in which order)? 2. Provider/model for the three agents (key set by the user as an env var); may the Verifier use a different model? 3. First target artifact: `disputas`/`p/resumen_radicado` (evaluable) vs copilot prompt (not evaluable)? 4. Path G now with Path C as target behind the same ModelPort: confirmed? 5. Who asks agent-core's operator for the Path C items (tool-service routing, identity key, gateway token, FieldClassifier, seed import)? 6. Priority of broadening kinds (BKT, BKF, new agent) vs polishing the demo.

## 16. Asks to forward (agent-core and platform only)

agent-core: merge or abandon PR 28; list-proposals route + Idempotency-Key on main (PRs 23/24); an `eval_suite` for `disputas`; a way for an external service to return structured output (or confirm the `submit_*` pattern), tool-service routing for `pulso/*`, identity key and gateway consumer token for our service, delivery path for `release.*`/`run.closed`/registry events to a service with the exporter role.
platform: endpoint to register/track engine proposals (`source=engine`) or auto-track registry proposals by our identity; Supervisión/Agentes/Propuestas screens in the SPA; emit case type, copilot query signature, draft disposition, tool-use events; Postgres + migrations timeline.

## 16b. Round 5: priorities, model, and the MINIMAL agent-core change set

User priorities (binding), in order:
1. The engine runs every X time (`scheduled`) or on demand (`explicit`).
2. The engine's agents (Scout, Verifier, Builder) are EXECUTED WITH agent-core and generate the proposals and (nice to have) the evaluations that come back to the engine.
3. Proposal types by priority: (1) NEW AGENTS, (2) prompt changes, (3) links to EXISTING tools, (4) NEW tools (only if viable now; lower otherwise), (5) policies, (6) trees/flows, (7) rule/classification.
4. The engine sends the proposal to agent-core; agent-core does ALL management: evaluation, showing it to the SPA, the approval flow and the release.
Model for all agents: `deepseek/deepseek-v4.1-flash` (id NOT verified against OpenRouter; confirm exact id and that it supports tool calling + structured output; same model for Scout and Verifier weakens independence: mitigate with isolated prompts/contexts and deterministic recompute).
Agent-core changes are allowed as PRs (additive, behind config, tests, version bump on contract change), only for what we REALLY need.

What we really need from agent-core (re-thought against these priorities):
| Need | Is a code change needed? | Why |
|---|---|---|
| Run our three agents inside the shared agent-core | NO (config + human admin approval of the three agents once) | register `pulso-scout/verifier/builder` via the proposal API (human approve+publish+promote) or `registry import` by an admin; our key in identity-keys; gateway consumer token + model alias |
| Builder creates the proposal | NO if the Builder is a `constructor-chat`-style agent that uses the in-process registry write tools (`create_proposal`, `put_draft`, `validate`) and returns only the proposal id as a primitive string slot; evidence goes in as a string input slot | removes most engine-side compile work for complex kinds (agents, flows, templates): the Core validators check the draft; our engine keeps a deterministic compiler for simple cases (prompt replace) and a post-hoc deny-list/BK0 check. TO VERIFY (spike S1): which registry tools an agent we define may use, whether `freeze`/`evaluate` are available to the bot, size limits of string input slots |
| Scout/Verifier return structured results | YES, one small additive PR: route tool names by prefix (`pulso/*` -> our service) in HttpToolExecutor (today ONE global tool-service URL per Core); until then Scout/Verifier can run on Path G while the Builder already runs in agent-core | needed for `pulso/get_*` and `pulso/submit_*` tools |
| Our tool results reach the model as numbers, not tokens | MAYBE a small PR: let a ToolDef declare field classes (public/non-PII) so the FieldClassifier does not tokenise our evidence | otherwise the model sees tokens; TO VERIFY how the classifier is configured |
| Proposals visible to the SPA/anything | YES, but it already exists in branches: merge the stranded PRs 23/24 (list-proposals route, `Idempotency-Key`, OpenAPI) into main | the platform (their integration) lists proposals through it; safe retries for us |
| New agent proposals | NO code change: the proposal API accepts a new agent with its full closure (26 entities for disputas), born at staging; a human approves/publishes, another promotes | human admin must add `fraude` interrupt + injection ruleset (a clone loses them) before prod |
| Broader evaluation (text assertions, non-customer principals, task input) | NO (nice to have, skip for now) | native eval + structural suites are enough for customer-facing agents; the engine/Builder can generate a structural eval_suite (required for human approval) |
| Proposal metadata field, `proposal.*` events, capabilities endpoint, HTTP agent-import route, `rule`/`llm_structured` providers in `serve` | NO for now | origin=auto_detect + rationale cover provenance; polling registry-events/export suffices; rule/classifier is the lowest priority |
So the minimal PR set to agent-core is THREE items: (a) merge stranded PRs 23/24, (b) tool routing by prefix, (c) optional tool-field classification. Everything else is configuration, a human admin action, or work on our side.

Consequences for our build order: (1) scheduled/explicit trigger + `pulso run` wiring (in flight); (2) run the Builder as an agent-core agent (spike S1 first: registry tools available to our agent, structured id return) and the Scout/Verifier on Path G meanwhile; (3) compile support in priority order agent > prompt > existing tool link > new tool > policy > flow/tree > rule/classifier, using the Core's own validators wherever the agent builds the draft; (4) eval suites generated by the Builder (nice to have).

## 16c. Round 6 (user): scope corrections

- NEW TOOLS (artifact kind `tool`) are PAUSED until further notice: the new `tool-service` (pulso-factored/tool-service) cannot create tools by POST or similar yet. Linking EXISTING tools (priority 3) stays, limited to what the tool-service catalog already serves.
- We drop offline stubs/mocks as a goal: everything must serve the REAL integration (agent-core + SPA). Offline pieces only where they protect a real flow (tests), never as deliverables on their own.
- Upstream moves fast: watch agent-core, support-platform, llm-gateway, tool-service, data-pipeline, data-lab (script `D:\.codex\factored\buildbox\watch-repos.sh` reports heads/PRs/new repos each cycle). Seen so far: agent-core head e725e91 (PR 36 http grant_active merged), OPEN PR 34 (serve with the tool-service + published field classification incl. an overlay for the engine's own fields), new repo tool-service (head 4b0b12e), platform PR 11 (ADR 0004: tool service receives verified claims, not a JWS), data-pipeline read-model contract commit.
- Codex idea (nice to have, independent, REAL): see chat; candidates are real-data work in Codex's own lane (an independent, reviewed signal portfolio for complaints on the real bank dataset + E0 to cross-check our Rust sensor, and resolving the E0 operational-validation blocker), NOT offline scenario factories.

## 16d. Spike S1 verdicts (SPIKE_S1_VALIDATION_2026-10-04.md) and corrections to 16b

- MODEL: `deepseek/deepseek-v4.1-flash` EXISTS on OpenRouter (checked on the public models list, 2026-10-04): context 1,048,576; supports tools, tool_choice, response_format, structured_outputs; very low input price, output about 2.4 USD per million tokens. (An earlier WebFetch summary said otherwise: it was wrong, replaced by the direct list.) Core step format is prompted JSON through a plain chat/completions passthrough gateway: any JSON-following model works; no model allow-list; ship OUR model profile (the fixture's `max_tokens: 400` would truncate).
- H1 CONFIRMED with limits: `registry/*` tools reach any agent that lists them in `tools_allowed` (serve needs `--registry-api`); rule AG-02 forces `invocable_by: [builder]` so our engine must sign a `builder` principal (a `service` principal fails validation); the bot can create, put_draft, freeze, reopen, evaluate, validate; NEVER approve/publish/promote; the `agent` node can only call read/compute tools, so freeze/evaluate/create/put_draft need their own `tool` nodes in the flow; quota 10 proposals/24 h global, 20 evals/proposal; `put_draft` needs the `expected_rev` returned by `create_proposal`.
- H2 CONFIRMED by in-memory run: only the agent node output and the `put_draft` result are barred from `end.output_map`; `create_proposal` and `validate` results are legal, so a task flow can return `{proposal_id, valid}`; end outcome must be `completed`. CAVEAT: slot text is wrapped as untrusted and PII-tokenised (digit runs of 6+, emails, ranges become tokens; de-tokenised only in tool-call args): keep evidence compact, short numbers, slug ids, no long digit runs or ranges.
- H3: confirmed statically/in memory; live run UNKNOWN (needs gateway URL+token and a builder-signed identity via POST /v1/runs).
- H4 partly REFUTED: the new tool-service serves only customer/advisor principals (`principal_not_served` for others) and the Core has ONE global tool URL; slash tool ids would 404 on it (use slash-free ids). Field classification needs NO code: one overlay JSON file (e.g. `{"pulso_signal":{"field_class":"public"}}`) via `AGENTCORE_FIELD_CLASSIFICATION_FILES`, but that file-driven classifier is in OPEN PR 34 (includes 35).
- ADR 0019 matches our design: a `task` constructor driven by a signal, `origin=auto_detect`, principal `builder`, constructor-bot with `write_draft`; listed there as pending. Our Builder can BE that task constructor.
- PRs 23/24 (list-proposals, Idempotency-Key) are still NOT on main (docs are right); PRs 33 and 36 are on main (36 irrelevant to us).
- CORRECTED minimal agent-core change set: Builder in Core = ZERO code (needs: admin import of `pulso-builder`, operator overlay file, PR 34 merged, gateway token, builder-signed identity); Scout/Verifier in Core = ONE additive PR (route tools by prefix to a separate URL+token; tool-service does not remove this need); PRs 23/24 optional (only for writing via registry HTTP or listing); tool-field classification = no PR.
- Development path that does not wait for anyone: a LOCAL instance of the same agent-core code (e2e stack: Postgres + `agentcore serve --registry-api --port 8001` + gateway, head + PR 34 branch), labelled as our own instance, until the shared Core imports `pulso-builder`.

## 16e. Round 7: the MINIMUM PATH TO REAL VALUE (what we do first, what we cut)

Problem named by the user: the engine does not traverse the bank tables (complaints, contacts, surveys, transactions): dataset mode only consumes platform-shaped events and E0 aggregates. The system must find REAL recurring problems and improvement opportunities (also inefficiencies) and propose ADEQUATE solutions.

Simplest design that gets there (the "value loop v0"):
1. **Aggregator, not a raw-row sensor in Rust.** A Python (pyarrow/duckdb) job reads the bank tables locally and emits TREATED CELL TABLES (period x dimensions, numerator/denominator, k>=10, no ids/free text), same pattern as `scripts/e0/treated_aggregates.py` (done). Output = `cells` package (ndjson) per metric family.
2. **Generalise the existing Rust statistical sensor to cells.** Same method as `rust-events` (discovery/holdout, Bonferroni/BH over ALL explored cells, replication, named discards, k>=10) but its input is a cell table instead of events. One new package type; reuse tests/generators.
3. **Valid replication design decided by the DATA AUDIT** (running): the Codex doc says interaction timestamps are naive (no timezone), so temporal windows may be unsafe; fall back to cross-sectional replication (customer-hash split, branch/channel/product) where needed.
4. **Reasoning**: Scout -> Verifier on Path G (deepseek via gateway), Builder as `pulso-builder` agent in a local agent-core (S1), on the signals from step 2 and on the E0/platform signals.
5. **Mapping findings -> real agents and artifacts** (ARTIFACT_ANATOMY research, running): without a mapping a finding stays `unlinked`/descriptive (spec rule). Stage honestly: bank findings tell WHERE (which reasons/channels are worst), E0/platform findings give the concrete mechanism (e.g. repeated copilot query) for a proposal.
6. **Benchmark**: Codex's independent catalog (lite version below) scores steps 1-4 (recall/precision/ranking); adequacy rubric (ARTIFACT_ANATOMY) scores proposals.

DEFERRED, NOT CUT (round 8, user: lower priority is fine, cutting is not; these are important parts and stay in the roadmap as PHASE 2, each with an entry criterion):
| Item | Phase | Why it matters | Effort (agent-h) | Entry criterion / dependency |
|---|---|---|---|---|
| Outcome loop (`release.*`, `run.closed`, registry events via `/v1/export`) | 2a | closes the loop: what happened after approval, before/after, learning | 8-12 | first proposal approved/published in a Core we can read; exporter role minted |
| Triggers `window_complete`, `data_loaded` | 2b | runs fire when a window closes or a new batch lands, not only by clock/demand | 4-6 | scheduler done; loader writes a batch marker |
| Broader evaluation | 2c | our suites richer (scripted scenarios + assertions); agent-core extensions only if Phase 1 proves a real limit (text assertions, non-customer principals, task input) | 12-20 incl. PRs | Phase 1 shows which eval limits actually block us |
| Flows / decision trees | 2d | high-value improvements beyond prompts | ~15 | Builder-in-Core stable; BKF design (Codex's offline compiler as reference) |
| rule / classifier decision models | 2e | Jev-free decisions | 10-15 + PR | agent-core `serve` registers `rule`/`llm_structured` providers (PR) + calibration artifacts |
| Templates and non-protected policies (BKT) | 2f | cheap, low risk kinds | 7-9 | generic compile foundation |
| Scout/Verifier INSIDE the Core | 2g | the user's goal that all engine agents run in agent-core | ~14 (PR 6-8 + agent defs 8) | tool-routing-by-prefix PR written and accepted |
| agent-core PRs 23/24 (list-proposals, Idempotency-Key, OpenAPI) | 2h | listing and safe retries; platform visibility | 2-4 (rebase) | schedule with 2a |
| NEW TOOLS | blocked | tool-service cannot create tools yet | ~6 once unblocked | tool-service gains tool creation/registration |
| Automatización screens polish / platform SPA proposals screen | 2i | the human-facing surface | depends on platform | platform exposes the proposals listing |
Phase 1 stays the minimum value loop; Phase 2 starts as soon as Phase 1's acceptance (scored against the benchmark) is met, in the order a, b, h, g, f, c, d, e; none is dropped.

Build order (relaxed, agent-hours): (a) research now: BANK_DATA_AUDIT + ARTIFACT_ANATOMY (2-4 h, running); (b) aggregator + cells sensor (8-12 h) ; (c) Scout/Verifier on Path G with real model + Builder-in-Core local (12-16 h) ; (d) minimal registry writer or Builder tools (2-3 h) ; (e) score against Codex catalog and rubric (4 h) ; in parallel: Codex OPBENCH-lite (8-12 h), pulso engine Dockerfile + infra fixes (background).

Critical items to do NOW (no dependencies, no waiting for approvals): data audit; artifact anatomy + rubric; fix infra issues found by the apply agent (state key in `aws-prod.ps1`, `enabled=false` host semantics, `.dockerignore` of agent-core for core-bridge build, engine Dockerfile); keep PR 97 integration and wiring review moving; watch upstream (script).

## 16f. Round 9: development environment (credentials supplied) and the implementation start

The agent-core and llm-gateway teams gave the user dev env files (names readable, values never printed): `D:\.codex\factored\agent-core.env` (AGENTCORE_ALLOW_DEMO, AGENTCORE_EVAL_DSN, AGENTCORE_JEV_API_KEY, AGENTCORE_KEYS_FINGERPRINT, AGENTCORE_KEYS_TOKEN_MAP, AGENTCORE_LLM_GATEWAY_TOKEN/URL, AGENTCORE_REGISTRY_DSN, GATEWAY_TOKEN_AGENT_CORE, OPENROUTER_API_KEY, OTEL_EXPORTER_OTLP_ENDPOINT) and `D:\.codex\factored\llm-gateway.env` (GATEWAY_CONSUMERS, GATEWAY_TOKEN_AGENT_CORE, JEV_API_KEY, LLM_ENDPOINTS, OPENROUTER_API_KEY). They are the inputs of the agent-core e2e stack (`scripts/e2e`): REAL OpenRouter + JEV keys, so locally everything can run for real.
Local stack (all on Podman machine `pulso-dev`, 4 GiB, plus host processes): Postgres 16 container (agent-core compose, port 55432, DBs core/registry and agentcore_eval), llm-gateway container (no Go on the host: `podman build` its Dockerfile; env from llm-gateway.env; consumer for agent-core and a consumer token for our engine), `agentcore serve --registry-api --port 8001` on the host via `uv` (head e725e91 + PR 34 branch for the file-driven field classification; identity-keys including OUR builder-signed identity; field overlay file with `pulso_signal` public), our `pulso` engine. Estimated 0.7-1.2 GB beyond the VM; heavier cargo builds must not run at the same time.
Rules: values are never printed or committed; the env files are not copied into AWS secrets without the user's explicit OK; AGENTCORE_ALLOW_DEMO is a local-only flag (forbidden in prod).
Implementation start (Phase 1 lanes, once the user says go): L1 cells sensor, L2 reasoning roles + real gateway call with `deepseek/deepseek-v4.1-flash` (now testable with the real key), L3 `pulso-builder` agent + run invoker against the local stack; then the aggregator (after BANK_DATA_AUDIT) and scoring (after the Codex catalog and ARTIFACT_ANATOMY).
Closing PRs first (user priority): infra#32 and improvement-engine#97 must be mergeable by the user; implementation starts in parallel only on lanes that do not touch those branches.

## 17. Iteration log

- Round 1: same agent-core; three agents as agent-core agents; we create proposals and send them to agent-core, which tells the SPA; relax conditions.
- Round 2: read the unverified points now (spike B0 done); triggers; assume dataset + E0 + Product data model.
- Round 3: triggers `explicit`+`scheduled`; `release.*`/`run.closed` valuable; data model = contract 1.2.0; which kinds can we propose (answer in section 7).
- Round 4: propose templates/policies, flows/trees, decision models (check Jev alternatives), tools, a new tool, and ESPECIALLY a new agent; define what composes a test and consider the engine defining the eval cases (kinds+evals plan launched). Spike B0 results integrated (section 6). Codex: forget asking for now.

### Iteration 18 (2026-10-04, after PR 97/98/99 merged)
- Done on main: cells sensor + aggregator (L1), reasoning roles + real gateway ModelPort (L2), local stack + pulso-builder (L3), scoring (SC1), pull trigger poller (TR1), OPBENCH-lite catalog (Codex, PR 98).
- Scoring of L1 output vs OPBENCH-lite: recall 1.0 (3/3), non-findings reported 0/5, ranking Spearman 1.0, precision 0.18 (catalog holds only 3 positive cells; the other 14 corroborated cells are real per BANK_DATA_AUDIT but outside the catalog: ask Codex to extend catalog to all audited findings).
- Adjustments: (a) 93.1% E1 figure is not reproducible (79.4% cross-case); catalog entry OPB-04 to be re-checked; (b) M6 channel semantics (survey send channel vs interaction channel); (c) E1 copilot repeat is already covered by `leer_movimientos` -> report as covered, not as an opportunity.
- In flight: B2 registry writer (proposal -> agent-core as builder), TR2 trigger endpoint (debug-api). Next: first end-to-end live pass (cells -> reasoning -> B2 -> real agent-core proposal) and scoring of the proposal with the rubric + judge of another model family; outcome loop (release.* -> verdict) after.

### Iteration 19 (2026-10-04): magic research synthesis (rounds 1A-1E)
Reports: MAGIC_ROUND1A..1E in this folder. Pillars of the virtuous loop: DETECT (cells sensor + more sources + eval probes) -> PROPOSE (Scout/Verifier/Builder, right artifact kind) -> EVALUATE BEFORE TANGIBLE (regression suite that fails on base, freeze+evaluate, boundary probes, pairwise judge) -> HUMAN DECISION in SPA (dossier) -> RELEASE -> OBSERVE (outcome verdict honest, usually inconclusive on stationary data) -> back to DETECT. Cross-cutting: O11Y (Langfuse Cloud as the AI observability plane: gateway OTLP, engine spans, agent-core run-trace bridge; content capture off by default) and a continuous AGENT TEST SUITE (scenarios on every candidate and scheduled on prod agents; failures are detection signals).
Wave 1: evaluate-before-propose + regression suite (must fail on base); dossier; o11y (gateway OTLP, engine spans, run-trace bridge); segment cells + AG2 sources; agent test suite + boundary probes. Wave 2: outcome loop with T1, pseudo-replay, fixed attacker pack, copilot suggestion dataset, digest. Wave 3: cross-source finding, live attackers, canary/dataset replay (needs agent-core).
Note: SPA team is building the builder/proposal screen: align dossier fields with their data contract.

## 18. Work items from the magic research (rounds 1A-1E, Langfuse decision), 2026-10-05

Framing: the product magic is the virtuous loop DETECT -> PROPOSE -> EVALUATE BEFORE TANGIBLE -> HUMAN DECISION (SPA) -> RELEASE -> OBSERVE -> back to DETECT. Two cross-cutting pillars: O11Y (understand what agents do and why) and a continuous AGENT TEST SUITE.
Priority scale: P0 blocks the demo of the loop, P1 high magic per effort, P2 valuable but later, P3 deferred (not cut). Effort S/M/L. Owner: US (Claude lanes), CODEX (independent, in progress), AC (agent-core team via the user), PLAT (platform/SPA team via the user), USER.
Every item: live tests are mandatory (stack up, credentials only in the process environment, real results reported). Models: generation xiaomi/mimo-v2.6-flash, Verifier/validators xiaomi/mimo-v2.6-pro, other-family judge z-ai/glm-5.3-flash.

### Wave 1

**W1-1 Evaluate before proposing, with a regression suite that fails on the base (P0, M, US; builds on B3, EV1, EV2).**
- Context: agent-core already has pre-release evaluation (freeze + evaluate runs the real engine, LLM and JEV on the candidate in memory; double-yardstick gate; GateItems; ApprovalReview for the SPA; scripted scenarios only). Nothing is approvable without an eval_suite and none exists for real agents.
- Scope: from a detected finding build a regression eval_suite (cases derived from the failing cell; ES/PT; templated utterances, fake slots, no PII); check it FAILS on the base artifact and PASSES with the candidate; the Builder loop freezes and evaluates, retries once on failure, and only announces proposals that pass; the proposal carries the verdict story (attempt 1 failed X, attempt 2 passed, GateItems).
- DoD: a live run on the local stack produces a proposal whose suite fails on base and passes on candidate, with the real GateItems recorded; a negative test shows a non-improving candidate is NOT announced; the dossier verdict-story field is filled; rubric score recorded.
- Dependencies: B3 merged; EV1 (minimal disputas suite) as seed.

**W1-2 Decision dossier (P0, S-M, US + CODEX spec T4).**
- Context: a supervisor must understand the proposal in 30 seconds. The SPA screen is being built by the platform team (no concrete info yet): align fields with their data contract when it arrives.
- Scope: the engine fills proposal rationale/changelog and an attached dossier: problem, evidence (numbers with same-channel baseline), diff, base vs candidate result, both gates, candidate_hash, expected effect and how it will be measured, risks, what stays unchanged; Spanish with Portuguese variant.
- DoD: 3 golden dossiers from real audited aggregates pass the DOSSIER_SPEC checks; the acceptance script (T4b) is green against the local stack; fields mapped to what the SPA can show (plus the list of what it cannot).

**W1-3 Observability with Langfuse Cloud for the gateway, agent-core and the engine (P0/P1, M, US; PRs in other repos allowed).**
- Context (user decisions, 2026-10-05): Langfuse Cloud US project created by the user, credentials in D:\.codex\factored\langfuse.env (names LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_BASE_URL). ALL content goes to Langfuse (full request/response content, prompts and outputs, not only metadata); standing authorization recorded in memory, do not ask again. Scope: llm-gateway, agent-core and our improvement-engine. The platform/SPA does NOT use Langfuse. Hobby plan is enough (50k units/month, 30-day retention, public API 30 req/min: batch scores). Judges are implemented by us with agent-core primitives, NOT Langfuse-managed evaluators. Research: LANGFUSE_INTEGRATION_PLAN_2026-10-05.md.
- Architecture: the engine cannot do TLS or OTel directly, so a small LOCAL OTLP forwarder/collector (scripts/o11y/otlp_forwarder.py, stdlib) is the single egress: it receives OTLP/HTTP from the engine bridge and from any local service, holds the Langfuse key, forwards to LANGFUSE_BASE_URL (/api/public/otel/v1/traces, Basic auth), masks secrets/tokens. The Python bridge (scripts/o11y/runtrace_bridge.py, branch claude/o11y1-run-trace-bridge) converts agent-core run exports and engine stages into traces with gen_ai.* and langfuse.* attributes, content included.
- Correlation trace id: ONE W3C trace id per story (32 hex), derived deterministically from the story key (finding key + run id) so every component can recompute it; propagated by `traceparent` header engine -> llm-gateway and engine -> agent-core runs; session = run id; tags low-cardinality (agent, release, locale, case-type, stage); finding key in metadata; Baggage carries session/release/tags. Mark agent-core's own `chat` span as a plain span to avoid double generations. Register custom model prices via POST /api/public/models: xiaomi/mimo-v2.6-flash 1.4e-7 in / 2.8e-7 out, xiaomi/mimo-v2.6-pro 4.35e-7 / 8.7e-7, z-ai/glm-5.3-flash 1.5e-7 / 5e-7.
- PRs (we open them; the user merges): llm-gateway (langfuse.* labels, session/release/trace linkage, opt-in content capture as gen_ai input/output attributes, traceparent extraction); agent-core (extract inbound traceparent at api/tracing.py:39, extend the closed attribute list spans.py:46-62 so langfuse.* and content attributes pass, opt-in content capture on agent spans, tokens on agent_step); engine (Rust: traceparent header + labels in llm_gateway.rs:93-98, story trace id derivation, stage spans through the forwarder).
- DoD: real traces with content visible in Langfuse US (verified through the public API: counts, expected spans and attributes, content present); one end-to-end story trace from finding to proposal joining engine, gateway and agent-core spans by the same trace id; cost per stage matches the price table within 5%; models registered; a score per trace (gate pass) visible.
- Status: bridge built and tested locally (19 unit tests, 44 spans from 2 real runs against a local receiver); the first Langfuse send and model registration were denied by the permission layer in the subagent session (relayed authorization does not count): the send is run from the main session after the user's direct authorization (given 2026-10-05).

**W1-4 More and better detection (P1, S, US).**
- Context: the sensor on M1-M6 has recall 1.0 and 0 non-findings reported; AG2 added M7-M10 (7,995 real cells): M7/M9 refuted, M10 dependent on M1, M8 is a level risk (about 50% of sends to non-consenting customers) that a vs-rest sensor cannot show.
- Scope: segment cells (language x channel) in the aggregator and sensor; a second finding type "level risk" with explicit baseline/threshold so M8 surfaces; keep BH, holdout and named discards; extend with agent-behaviour cells when Codex T3 lands.
- DoD: the new finding type covered by RED/GREEN tests; a real run lists M8 as a risk finding and M9 as refuted; scoring vs OPBENCH v2 (Codex T5) keeps recall 1.0 and reports precision.

**W1-5 Continuous agent test battery and scheduled probes (P1, M, US with the CODEX attacker pack).**
- Context: no test series exists for the real agents. Agent-core scenarios are scripted (expect.outcome/escalated/actions_verified, event assertions, 4 platform guardrails); live attackers cannot run inside evaluate.
- Scope (EV2 running): amount-boundary probes (249/250/251/499/500/501, split transfers, es/pt; the 500 vs 250 policy discrepancy is a human-owned finding), a fixed attacker pack (injection, PII elicitation, es/pt switching, angry, vague, fraud pretext), a runner that executes base vs candidate on the local stack and as a scheduled health check of current agents; a failing scenario becomes a detection signal (cells agent x scenario_family x outcome, labelled probe); results also go to Langfuse as scores/datasets.
- DoD: the battery runs live against the real local agents with real pass/fail; defects found in the demo agents are reported; JSON ingestible by the cells sensor; scheduled run through the trigger path.

### Wave 2

- **W2-1 Outcome loop (P1, M, US + CODEX T1).** release.* events -> before/after on the same cell vs controls -> verdict card (improved / no_detectable_change / worsened / inconclusive, including underpowered). Expect mostly inconclusive on stationary bank data: show that honestly. Needs agent-core lineage (GET /runs/{id}/lineage, run_started.release), the exporter role, and a `release` field in platform events (PLAT). DoD: estimator from T1 wired; a simulated release yields a correct verdict in placebo/injection tests; a live release in the local stack yields a card.
- **W2-2 Pseudo-replay of real cells (P2, M, US + CODEX).** Queja/phone and E0 recurrence rebuilt as scripted scenarios with templated utterances, 5-8 scenarios x 3 repetitions, provenance by cell hash. DoD: base vs candidate separation detected for an injected 30-point fix.
- **W2-3 Choose the right artifact kind (P2, M, US).** Mapping finding -> template / flow / injection rule / interrupt / existing tool link / new agent beyond prompts (registry accepts all kinds except knowledge). DoD: three kinds proposed live and validated by the Core.
- **W2-4 Copilot suggestion dataset (P2, S for us, PLAT for the catalog).** Advisor corrections of copilot drafts (used/edited/discarded/ignored + edit distance) as a free labelled dataset for prompt improvement; needs copilot.suggestion_* admitted in catalog 1.3.0 and a turn_id. DoD: a miner producing treated aggregates; the ask delivered.
- **W2-5 Weekly supervisor digest and impact card (P2, M, PLAT + US).** Needs the platform screen/route.
- **W2-6 Value card lite (P2, S, US).** Case-count range and direction, low/base/high with labelled assumptions; USD only with a handling-cost input from the user; no recontact claims (no contact-to-complaint chain in the data).
- **W2-7 Pairwise before/after transcript card with an order-swapped judge (P2, S-M, US).** glm judges mimo outputs; labelled uncalibrated until 30 human-labelled pairs exist (USER).

### Wave 3 (deferred, not cut)
Cross-source finding with link grade (bank says where, E0/platform says why; only complaint_id joins); live attacker loop on /v1/runs that freezes successful attacks into a persistent adversarial suite (success by deterministic checks); canary/staged release and real-run dataset scenarios (need an agent-core ADR+PR); knowledge as a proposal artifact; chat-constructor citing findings (agent-core tool); handoff-quality labels; wired MEM1 memory; policies/trees/flows and rule/classifier proposals; new tools (paused).

### Asks (tracked, not blocking Wave 1)
- PLAT (we may open the PRs ourselves in support-platform, the user merges; Langfuse is NOT used in the platform): POST /internal/builder/proposals/announce (service token) + a notification kind + the Agentes screen (the team is already building the screen: align dossier fields with their contract); admit copilot.suggestion_* in 1.3.0; `release` in event payloads.
- AC: staff-keys entry for our `builder` principal (a trust grant), exporter role, agent+alias in release.* events and delivery, dataset scenarios, canary alias; list route + Idempotency-Key on main (PRs 23/24 were merged into stacked non-main bases; the agent-core team re-lands them).
- INFRA (ours, PR in preparation): agent-core as the shared Core, gateway reachability and generated tokens.
- USER: handling cost per contact (value card), 30 human-labelled proposal pairs; decided: all content may go to Langfuse.

### Codex status (shared journal CX-R2-009..011)
Codex is working round 2 (T1 outcome estimator, T2 eval bank, T3 run-trace source, T4 dossier spec + acceptance, T5 OPBENCH v2). T5 is in adversarial review gates (privacy suppression, M6 non-actionable invariant, E0 exporter contract) and full local CI passed. No results from T1-T4 inspected yet. Our scoring harness runs against the v2 catalog when it lands.


### 18-bis. Decisions and findings log, 2026-10-05 (supersede any conflicting text above)
- PRs in other repos: the user authorized us to open PRs in agent-core, support-platform, llm-gateway and infra (small, additive, tested, draft); the user merges. The asks in docs/reports-claude/ASKS/ become PRs by us where the change is small: (a) llm-gateway: engine consumer + openrouter alias config, langfuse.* labels, content capture opt-in, traceparent; (b) agent-core: traceparent extraction, attribute allowlist, `agent_id` + `alias` in release.* events (ReleaseData), tokens on agent_step; (c) support-platform: POST /internal/builder/proposals/announce (service token, source engine), notification kind improvement_proposed; the 1.3.0 catalog (copilot.suggestion_* + turn_id) and the `release` event field stay asks to the Product/platform owners unless the repo is ours.
- agent-core main now has GET /proposals, Idempotency-Key on registry writes and GET /runs/{id}/lineage (PRs 23/24 content landed as PR #41) and, as of 46d7b98+, the real transcript/calibration/classifier pieces. The engine registry-writer sends Idempotency-Key = finding key. Still human-owned: the shared Core needs AGENTCORE_TOOL_SERVICE_URL and DSN/JEV/OpenRouter values.
- Shared Core = the agent-core repo's own `agentcore serve` image (not our core-bridge). Infra PR 37 (draft, ADR 0009): Terraform-generated gateway/engine tokens and Ed25519 keys; review found 3 blockers before apply/demo (no merge-only reseed tooling; engine env contract mismatched: PULSO_LLM_GATEWAY_KEY, IP-literal gateway address, PULSO_SERVICE_SEED_HEX; Core startup needs tool service URL and artifact dirs) and a trust finding: the engine key in staff-keys can mint human/step_up credentials and approve/publish, and every host can read the whole secret. Fixes in progress; apply only on the user's order.
- Engine image: PR 100 merged (98 MB, built and run). Eval: EV1 minimal suites (disputas-min 20 cases, consultas-min 11) pass 20/20 and 11/11 live on the local stack; they are baselines, not regression proof: REG1 builds finding-specific suites that must FAIL on base and PASS on candidate; defects of the local calibration/classifier doubles documented (PULSO_SERVE_E2E=1).
- Detection: AG2 added M7-M10 (7,995 real cells): M7/M9 refuted, M10 dependent on M1, M8 is a level risk the vs-rest sensor cannot show (needs the level-risk finding type, W1-4).
- Codex: ownership carve-out merged (PR 101): T1/T3 under scripts/aggregate/outcome and agent_runs, T2 under agent-core-assets/eval-suites/codex-bank (X-DOC). CODEX continues round 2.
- Models: generation xiaomi/mimo-v2.6-flash, Verifier and heavy reasoning xiaomi/mimo-v2.6-pro, other-family judge z-ai/glm-5.3-flash. Judges (rubric, pairwise) are our own code over agent-core/gateway primitives.
- Process: a 15-minute cycle reads the shared journal, reviews all running agents and keeps parallel lanes busy; every agent must run its live tests.

### 18-ter. Status log, 2026-10-05 (late)
- Langfuse closed: live proof on Langfuse Cloud US (2 story traces with engine+gateway+agent-core spans under one trace id, 2 agent-run traces, 4 scores per story, 3 priced models, 32 spans forwarded, 0 failed). Verifier fixed for the retired observations endpoint (HTTP 410). Engine PR 107 (forwarder, bridge, closure script) pending conflict resolution; agent-core 48 and llm-gateway 4 merged by the user.
- Open PRs for the user: agent-core 53 (reject reason_code, last_decision), support-platform 27 (release on events, turn_id on suggestion_decided, GET /internal/evidence/cases), improvement-engine 108 (Codex R3-2).
- Focus: detection engine. DET1 (full-period cells, pooled support, exploratory profile) and ART2 (tighten-only policy, read-only tool link; compilers pushed on claude/art2-policy-toollink) resumed. ENV1 (integrated rig) waits for RAM.
- Open items from PLAT2: contract 1.3.0 (32 missing platform event types) and cases.case_type in the exporter allow-list (engine/Product); engine should call the evidence route when announcing; tool definitions drift between engine fixtures and tool-service (every tool link is refused until aligned).

### 18-quater. Progress against the Wave plan and Codex delegation candidates, 2026-10-05 (evening)
Status per item (DONE = merged and proven live locally, PART = partly, NOT = not started):
- W1-1 Evaluate before proposing with a regression suite that fails on base: DONE (suite proven; non-improving candidates not announced). Open defect E8: the engine's proof scratch proposals (evaluation base / candidate-N) are visible to supervisors and can move staging.
- W1-2 Decision dossier: PART. Engine fills ES/PT dossier and the platform shows it in the notification; the proposal page does not render it yet (platform brief P6).
- W1-3 Langfuse: DONE (live on Langfuse Cloud US; PR 107, agent-core 48, gateway 4).
- W1-4 More and better detection: DONE for the sensor (level_risk, DET1 full-period cells, exploratory tier, 19 to 37 corroborated); PART for measurement (recall vs OPBENCH v2 not rescored; Codex).
- W1-5 Agent test battery: PART (EV2 live battery found real defects; scheduled run via trigger path not wired).
- W2-1 Outcome loop: PART (ran end to end live on synthetic planted data, verdict inconclusive, never on a real release; T1 estimator not calibrated).
- W2-2 Pseudo-replay of real cells: PART (Codex R3-3: 18 scenarios schema-validated only, never run live).
- W2-3 Right artifact kind: PART (patch, template, eval_suite, new agent via inherit_from, read-only tool link, tighten-only policy proven; LLM-driven tool link/policy in progress; flows and knowledge NOT).
- W2-4 Copilot suggestion dataset: PART (platform emits, catalog 1.3.0 admitted; EVT1 building the event cells).
- W2-5 Weekly digest, W2-6 value card lite, W2-7 pairwise transcript card: NOT.
- Wave 3: NOT (cross-source finding with link grade has Codex R3-4 tables only).
Cross-cutting production readiness: infra PR 37, 39, 40, 41, 42 merged (nothing applied), engine image with steps_cli (PR 112), loader unmeasured, `serve` hardening and platform Postgres/images delegated by briefs to the agent-core and platform teams (no feedback yet).
Codex delegation candidates for the next round (Codex is paused by the user; nothing assigned until it returns): (1) rescore DET1 and the exploratory tier against OPBENCH v2 and report recall/precision; (2) run the R3-3 scenario pack live (attach_eval_suite pattern) and report which defects it reveals; (3) independent calibration of the proposal judge with a second labeller and the 40 golden proposals; (4) calibrate and review the T1 outcome estimator (power, placebo, leakage) before any real-release claim; (5) adversarial review of the new tool-link and policy compilers and of the loader IAM design (assume-role path); (6) interpret R3-4 E0 and bank 'why' tables into candidate hypotheses for the sensors; (7) R3-5 adversarial corpus stays out of scope.
