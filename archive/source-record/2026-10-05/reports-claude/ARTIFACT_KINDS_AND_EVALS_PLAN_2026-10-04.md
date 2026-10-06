# Plan: proposing every agent-core artifact kind from our engine, and the eval suites behind them (2026-10-04)

Author: Claude (read-only research). Companion of `SPIKE_B0_AGENTS_2026-10-04.md` (how constructor-chat works, agent authoring path, tools, LLM plumbing: NOT repeated here), `PLATFORM_ATTACH_PLAN_2026-10-04.md` (section 7 feasibility table is the starting point) and `PLAN_PROPOSER_AND_ATTACH_2026-10-04.md`.

Evidence base: scratchpad clones `agent-core 547e608` (= origin/main after `git fetch`, nothing newer), `support-platform eeb73a8`, `llm-gateway 63155b6` (both fetched, nothing newer); our worktree `improvement-engine-claude-w6-demo`; V3 spec. Nothing was run against a service (no containers, no model calls, no AWS, no repo modified, nothing under D:\Nexus touched).
**New in this report: I ran agent-core's own pure-Python `build_candidate` / `validate_candidate` / `EvalSuite` / `suite_problems` in memory** (scratchpad `x/exp.py`, with `rfc8785` and `psycopg` stubbed because they are only imported, never used by these functions) over the `registry-e2e` fixtures. Statements marked EXPERIMENT E# below come from that run and are the strongest evidence in this file. VERIFIED = read in code. INFERRED = reasoned, not shown. Paths: `AC/` = agent-core, `OURS/` = our worktree.

---

## 0. Summary table

Effort = agent-hours for the SIMPLEST USEFUL slice (offline goldens first, then real-core-live evidence), assuming the shared foundation F (section 2.1, about 8 h) exists. "BK0 today" is `contracts/artifact-kinds/matrix.json` (pin `c814c2b`; registry code identical at `547e608`).

| # | Kind | Core accepts it? | BK0 today (propose) | Evaluable natively? | Effort offline + live (h) | Order | Verdict / main blocker |
|---|---|---|---|---|---|---|---|
| F | Foundation: generic compile (ref grammar with `/`, ReadBase closure, full ordered `changes[]`, cascade prediction, absent-digest for add) | n/a | n/a (seeded world is hard-coded) | n/a | 8 | 0 | Prerequisite of everything; shared with the V3 U46 work |
| 1a | Template `t/*` | YES (EXPERIMENT E6, E7, E9) | denied(kind_not_supported) | Only as "no regression + 4 platform guardrails"; response TEXT is not assertable | 4 + 3 = 7 | 1 | GO. Lowest risk. Must keep every locale of the agent (G0-12) |
| 1b | Non-protected policy | YES technically (E8). "Protected" is NOT enforced by Core, only by a human approver | denied | same as templates | +2 on top of 1a | 1 | GO but low value: the only policy in the fixtures is owned by `riesgo` and holds the 500 USD threshold; our deny-list must treat it as human-owned |
| 2 | **NEW AGENT** | YES via proposal with base `None` (E2, E4, E5). Gaps: release-level fields (injection ruleset, interrupts) | denied (BKA) | YES if task-mode (no JEV); conversational clone needs JEV key | 10 + 6 = 16 | **2 (right after templates)** | GO in two variants: "task twin" (no key) and "conversational clone with a one-prompt delta". Needs a human admin for interrupts and an approver + promote |
| 3 | Flow / decision tree | YES (E13) | denied (BKF) | YES (conv. needs JEV; task does not) | 10 + 5 = 15 | 4 | GO, most authoring work; business literals need a policy (G0-08) |
| 4 | Existing tool used in a flow/agent | YES (E12 for `Agent.tools_allowed`) | denied | Yes, sandbox seeds the reply; tool IDENTITY not assertable | 3 + 2 = 5 (after 3) | 5 | GO but depends on kind 3: `Agent.tools_allowed` alone changes no runtime behaviour |
| 5 | Decision model | Schema yes; provider `rule` and `llm_structured` are NOT wired in `serve` (only `jev`, `classifier`); thresholds come from a calibration artifact outside the registry | denied; `jev` blocked | Needs JEV key (jev) or Core change (rule) | 4 offline (edit jev `questions`/criteria text); live BLOCKED | 6 | PARTIAL. Real alternatives to Jev exist in the library but are not usable at head without a Core change plus a calibration artifact (section 4) |
| 6 | NEW tool | ToolDef: yes (E11: needs a referencer; E12 shows `tools_allowed` is enough). Executor: only the tool-service, by name | denied; `blocked(executor-registration)` | Sandbox seeds replies, so Core evaluates it WITHOUT the service | 6 engine-side + human dependency | 7 | PARTIAL. We can propose the ToolDef plus a handler spec; implementing and deploying the handler is another team's code; promote to prod must wait for it |
| E | Eval suite generator (ScenarioFactory minimal) | YES (draft kind) | supported (add), real-core-live | n/a | 8 offline + 3 live (counted from step 1) | 1 (parallel with F) | GO for structural regression suites. NOT able to judge text quality |

Recommended order (new agent as early as feasible): **F -> E (minimal) -> 1a template -> 2 NEW AGENT (task twin, then clone with prompt delta) -> 4 flow -> 5 existing tool -> 6 decision model (jev edit, offline) -> 7 new tool -> 1b policy any time.** Cumulative to a first live "new agent" proposal frozen and evaluated: about 8 + 8 + 7 + 16 = 39 agent-hours, plus asks (section 9).

Four findings that change the plan:
1. **A brand-new agent proposal must carry the whole closure** (E1: draft with only the agent fails REG-PIN on every reference; E2/E5: closure of 26 entities with a renamed agent builds a valid candidate). Entities identical to published ones are accepted as is (same id@version and hash is not VERSION-TAKEN).
2. **A new agent made this way loses the donor's `fraude` interrupt and its injection ruleset** (E5: `interrupts=[]`, `injection_ruleset=None`). Interrupts need an `admin` human (`put_draft` refuses otherwise) and both are `release_settings`, which our bridge denies. This is a safety gap, not a detail.
3. **The native eval cannot see text or tool identity.** Assertions are over a closed event catalog (`engine.tool_called` carries status/latency/attempt, no tool id; no response text). No LLM judge is wired in `serve`. A native `pass` means "ran, reached the expected outcome, zero platform-guardrail hits", never "better answer".
4. **Task-mode agents with `input` are not evaluable by suites**: the harness starts runs with `{agent, idempotency_key, lang}` only (`AC/agent_core/composition/evaluation.py:run`), no `input`. So Scout/Verifier-type agents (input_schema) cannot be gated natively; the disputas "task twin" (our `attention-task` world, start-only) can.

---

## 1. How a draft op looks (our ChangeSpec) and how it maps to Core

Our ChangeSpec op (V3 section 17; `OURS/seams/crates/steps/src/compile.rs`): `{op: add|replace|disable, target_kind, target_ref "kind:name@major", new_ref, precondition_digest "sha256:<Core content_hash>"}` plus `base_bundle_ref`, `workflow_bridge_ref`, `affected_routes`, `rollback_ref`.

Core side (VERIFIED, `AC/agent_core/registry/service.py`, `candidate.py`): `PUT /v1/registry/proposals/{pid}/draft {expected_rev, changes:[{kind, content, docs{description 1..4000, rationale<=4000, changelog<=8000}}]}` replaces the WHOLE draft each time (max 50 changes incl. the suite, 262144 B per entity, 200 flow nodes). `content` carries `id` and exact `version`. Candidate = base entities + drafted entities, then `_cascade` bumps patch of every non-drafted entity that references an edited one by exact version, then `pin_release`. No ordering is required between kinds in the draft; dependencies are reference edges.

| Our op | Core draft translation | Verified behaviour |
|---|---|---|
| replace | one change with the FULL new content and `version` > base | E9: same version with other content = `REG-VERSION-TAKEN`; E6: template 1.0.1 yields `new_versions` = agent 1.0.1, flow 1.0.1, template 1.0.1 and `auto_bumped` = agent + flow |
| add | new change with initial version AND a change of a consumer that references it | E11: a new tool nobody references = `REG-UNREFERENCED`; E12: referencing it from `Agent.tools_allowed` is enough |
| disable | no delete exists. New version of the CONSUMER without the reference | V3 section 27.2; not part of any simplest slice |

Draft op example (template, derived from the real fixture `t/pqr_radicado@1.0.0`):

```json
{"op": "replace", "target_kind": "template", "target_ref": "template:t/pqr_radicado@1",
 "new_ref": "template:t/pqr_radicado@2", "precondition_digest": "sha256:<content_hash of t/pqr_radicado@1.0.0>"}
```
compiles to `changes[0] = {"kind":"template","content":{"id":"t/pqr_radicado","version":"1.0.1","locales":{"es":"...","pt":"..."}},"docs":{...}}` and predicted `expected_derived = [agent:disputas@1.0.1, flow:disputa-cargo@1.0.1]`.

Registry errors you will see (VERIFIED `registry/errors.py`): `validation_failed` 422 (payload = violations `{rule, path, flow, node_id, message}`: REG-SCHEMA, REG-KIND, REG-DUPLICATE, REG-LIMIT, REG-PIN, REG-UNREFERENCED, REG-VERSION, REG-VERSION-TAKEN, REG-SUITE, REG-AGENT, REG-LOCKED, REG-KNOWLEDGE, plus flow rules G0-01..27, AG-01..04, MT-01..06), `forbidden_role` 403 (platform_* edits, interrupts without admin), `proposal_stale` 409 (rev or base moved), `candidate_changed` 409, `gate_failed` 409, `quota_exceeded` 429 (auto_detect: 10 proposals / 24 h, 20 evals per proposal), `loosening_not_accepted` 409, `illegal_transition` 409. `validate` returns HTTP 200 with `violations` (not success when non-empty).

### 2.1 What the foundation F must contain (shared by every kind)
Gaps found in our code that block every kind except prompt and eval_suite:
1. **Ref grammar.** `compile.rs::parse_ref` accepts names `[A-Za-z0-9._-]+`; Core ids contain `/` (`t/pqr_radicado`, `p/resumen_radicado`, `registry/put_draft`, `pulso/...`). Today it works for the prompt only because the seeded world hard-codes `resumen_radicado` and adds `p/`. Needs a [CONTRACT-CHANGE] on `engine-steps` compile in/out schemas and the `artifact-ref` grammar.
2. **`target_kind` enum** is `["prompt","eval_suite"]` in `validate()`, and `World::seeded_base()` is a single hard-coded flow/prompt/suite. Needs a BaseSnapshot (ReadBase: alias -> `ReleaseDetail` -> per-entity `GET /entities/{kind}/{id}?version=`; at head `ReleaseDetail` also returns interrupts, language_detection, injection_ruleset and max_input_chars, so V3 section 31.4.7 "GET release does not return them" is stale, see section 10).
3. **Absent-digest for `add`.** Today "add eval_suite" means next version of an existing suite. A truly new entity needs a sentinel precondition (`absent`) and a nullable `base_bundle_ref` (V3 CapabilityBundle `base_ref` nullable for a new agent).
4. **Cascade prediction** (`expected_derived`) with the same fixed point as `candidate._cascade`, and `auto_bumped` comparison after dry-run (V3 CAP-15). EXPERIMENT E6/E10/E13 give ready goldens.
5. **`closure_copy`** for new agents (read donor closure, re-emit unchanged), section 7.
6. BK0 rows: each kind's `propose` row moves from `denied(kind_not_supported)` to a stand-in verdict first; digest changes -> `[CONTRACT-CHANGE]`; new reasons needed: `protected_authority` (policy deny-list), maybe `provider_not_wired` (decision model `rule`/`llm_structured`).
Effort F: about 8 h (4 grammar + schemas + goldens, 3 ReadBase and DraftPlan, 1 cascade).

---

## 3. Kind 1: templates (`t/*`) and non-protected policies

- **Authoring format.** `AC/contracts/schemas/Template.json`: `{id, version, locales{xx: text}, reads[]}`; `Policy.json`: `{id, version, owner, expr (JSON Logic), rationale}`. Fixtures: `tests/fixtures/registry-e2e/templates/t/*.yaml`, `policies/*.yaml`.
- **Validation (EXPERIMENT).** E6 valid. E7: template without `pt` -> candidate builds but `validate_candidate` reports `G0-12 t/pqr_radicado@1.0.1 no tiene los locales pt del agente disputas@1.0.1` (Template schema alone passes, so the failure only appears at validate/freeze: `validation_failed`). Every template a flow or the agent engine-slot references must cover the agent's `supported_locales` (disputas: es, pt).
- **Dependencies.** None upstream. Downstream: every flow and agent that pins it gets a patch bump (cascade), so a one-template change touches 3 versions; the diff of the release must equal ChangeSpec + auto_bumped (V3 `pulso:diff_exceeds_change_spec`).
- **Policy specifics.** E8: policy replace validates. Core does NOT enforce "protected" (ADR 0009: only human approval/owner; `put_draft` has no policy guard). So the engine's own compile must refuse by deny-list: any policy referenced by a `rule` node holding a business threshold, or whose `owner` is a human team (fixture: `escalamiento-disputa-monto`, owner `riesgo`, expr `> 500`). Reason code `protected_authority`. In practice kind 1b adds little until there are non-owned policies.
- **Evaluable?** Yes but narrowly: a scenario that traverses the template's node proves reachability, outcome, and that the 4 platform guardrails stay 0 (a template that echoes a `sensitive_values` string counts as `platform_pii_leak`). It CANNOT assert the new wording. The "improvement" claim must come from our own evidence (V3 link grades), not from Core.
- **Risk.** Low. Main risk: an improvement hypothesis about wording that the native gate cannot test.
- **Compiler/BK0 needs.** F + `replace_template` op family (full-content replace, locales superset check as L1 prefilter G0-12), golden = E6 (`new_versions`, `auto_bumped`), negative goldens E7 (G0-12) and E9 (VERSION-TAKEN). Live evidence: dry-run via bridge, then create/put/validate/freeze/evaluate on a real Core with a suite that traverses the node.
- **Effort.** Offline 4 h, live 3 h. Policy: +2 h (op family plus deny-list).

---

## 4. Kind 3 (user's list item 3): decision models, and what exists besides `jev`

**Schema** (`AC/agent_core/domain/entities.py:326-348`): `DecisionModelDef{id, version, output_schema, calibrated_fields[], input_view[], providers[] (min 1, ordered chain), calibration{method none|isotonic|platt|temperature, run?}, thresholds_from?}`; `ProviderSpec{provider ∈ {jev, classifier, llm_structured, rule}, config{}}`. Providers are a fallback chain: first one that returns a schema-valid output wins (2 attempts each); if all fail the node gets empty value and `low_confidence`.

| Provider | What it is | Needs a key? | Wired in `serve` at head? | Can drive a `decide` branch? |
|---|---|---|---|---|
| `jev` | external Jev API, questions/criteria text in `config` | YES (`AGENTCORE_JEV_API_KEY`, read lazily only on a call; PR #28 gateway route stranded) | yes | yes (p from Jev, thresholds from calibration) |
| `rule` | `config{cases:[{when:{path,equals}, value}], default}`; first match wins, `p_raw=1.0`; no match -> `default` with p 0.0; deterministic; `RuleProvider` in `AC/agent_core/decision/providers/rule.py` | no | **NO**: `serve_ports.py:353` builds `providers={"jev", "classifier"}` only, so a DM that lists `rule` raises `DecisionConfigError: proveedor sin adaptador registrado: rule` at run time | yes in principle, with thresholds |
| `classifier` | TF-IDF + logistic regression, JSON artifact `tfidf-logreg-v1` (format `{vocab, idf, classes, coef, intercept, data_hash}`), pure Python, deterministic, `config.artifact` = reference | no | registered by NAME, but its loader is a deployment factory (`--classifier module:attr`); at e2e head that factory is a demo double `ScriptedProvider` (`testing/serve_demo.py:59`); our bridge reports `classifier assets directory absent` unless `PULSO_CLASSIFIER_DIR` exists | yes, with an artifact trained by a data scientist and thresholds |
| `llm_structured` | gateway `generate` with a prompt ref (`config.prompt`) | gateway token only | **NO** (not in `providers`) | NO: it returns `p_raw=None` for every field, so every field is below threshold: "baseline in evaluation, no threshold" (module docstring) |

Three further constraints (VERIFIED `decision/service.py:_calibrate/_passes`): (a) `above_threshold` needs an entry in the calibration artifact keyed `(field, label, provider, locale)` read from `thresholds_from`; absent = never passes -> branch `low_confidence`. The calibration source is a deployment piece (demo `InMemoryCalibrationSource`; ours `PULSO_CALIBRATIONS_DIR`), NOT a registry entity, so an engine draft cannot create thresholds for `rule`. (b) `understand` (the Agent-level model) builds a closed schema from the release and calibrates `command`/`flow`/`interrupt`; with `rule` it can only match on exact equality of inputs (`text`, `current_node`...), useless for free text. (c) `Agent.understand` is optional: task agents need no DM at all.

**What `understand`/`decide` can use without a JEV key, honestly:** nothing practical at head on the shared Core. `classifier` works only if the Core operator provides a real artifact loader and thresholds. `rule` works only after a ~2 line Core change (register `RuleProvider` and `LlmStructuredProvider`) PLUS a calibration artifact with `rule` thresholds. Decisions WITHOUT any decision model exist and are the real Jev-free route: `rule` NODE with `policy` ref or inline JSON Logic over facts/slots (G0-08: no business literals inline, use a policy), `collect` with enum validators, and the `agent` node (ReAct, LLM via gateway; G0-22 forbids using its output in `rule`/`tool.args`/`verify`). Our own `attention-task` world confirms the pattern: a task agent with no decision model evaluated end to end on a Core that composes no jev.

**Registry check.** EXPERIMENT E10: a DM whose provider is `rule` builds and validates; the registry does not check provider availability. So the failure mode is at run/eval time, not at freeze: our compile must carry a capability gate (`provider_not_wired`) fed by the `doctor`/version probe.

- **Draft op.** `{op: replace, target_kind: decision_model, target_ref: "decision_model:match-cargo@2", new_ref: "...@3"}`; V3 first cut: "without changing calibration" (keep `calibrated_fields`, `thresholds_from`).
- **Evaluable?** Conversational agents run `understand` through Jev on every user turn, so evaluating a DM edit needs the JEV key on the evaluating Core. Task agents calling a `decide` node with a Jev/`classifier` model need the same.
- **Simplest useful slice.** Edit the criteria/question text of an existing `jev` model (config is free JSON): offline compile + goldens (E10 shape), 4 h. Live evidence: BLOCKED until a JEV key (or the gateway route) is available to the evaluating Core; then 4 h.
- **Risk.** High for quality (Jev calibration thresholds are tied to the old criteria: `calibration`/`thresholds_from` do not move with your text), medium for plumbing.

---

## 5. Kind 2: flows and decision trees

- **Format.** `AC/contracts/schemas/Flow.json`: `{id, version, priority, nodes[]}`; node types usable: `collect, tool, tool_write (action_from confirm | draft), decide, rule, confirm, verify, respond, end, escalate, knowledge, agent`. `subflow`, `await_approval`, `transfer` are disabled/out (G0-01 / AG-03). `next` maps outcome labels to node ids. Parsed by `parse_flow` (`FlowSchemaError` -> violations).
- **Rules that bite (VERIFIED in `flows/rules/*.py`, `flows/agent.py`):** G0-01 (schema/shape), G0-02 (unresolved ref), G0-03 (next to existing node), G0-05 (a write needs a prior `confirm`; `write_draft` excepted), G0-07 (`agent` node tools read/compute only), G0-08 (no business literals in inline `rule.expr`; use a policy: ADR 0009), G0-09 (`respond.generate` needs `fallback_template_ref`), G0-12 (template/prompt locales cover the agent's), G0-16 (no waiting nodes in task flows), G0-22 (agent output cannot feed rule/tool args/verify), G0-24 (agent tools need `description` + closed `args_schema`), AG-01 (flow mode = agent mode), AG-02, AG-03, AG-04 (a flow reading `slots.X` needs a `collect`/`input_schema`/`accepts` that can write it), REG-LIMIT (200 nodes).
- **Dependencies.** Templates, prompts (-> model profile), tools, policies, decision models; the flow must be referenced by an agent `entry_flow`, an interrupt, or the release or it is `REG-UNREFERENCED`. EXPERIMENT E13 (insert a `respond` node on the `umbral:false` edge of `disputa-cargo`, version 1.1.0): candidate valid, `new_versions` = flow 1.1.0 + agent 1.0.1, `auto_bumped` = agent.
- **Authoring approach.** The engine must not hand a raw LLM-written flow to the registry (V3: LLM JSON never activates directly). Compile from a small TREE DSL in the ChangeSpec (restricted ops: insert_node on an edge, reroute a branch, add an escalate/clarify branch), then L1 prefilter + dry-run. That is "compiled trees" (BKF).
- **Evaluable?** Yes: scripted steps drive the new branch, `seed.tools` feeds the FIFO tool replies (no argument matching, so branches that depend on args need one queue per branch or are `not_evaluable_native`), `expect.outcome/escalated` and `assertions` on `engine.escalated{reason_code}` check the path. Conversational agents need JEV for `understand`; task agents need nothing.
- **Evidence gap today.** BK0 flow `validate` is `not_exercised`: the only live evidence is a dry-run asserting a node-limit VIOLATION. A VALID flow dry-run is the first RED to turn green (E13 shape is the offline golden).
- **Risk.** Medium-high: largest surface; branch tests must come from the base behaviour, not from the change (section 9 circularity).
- **Effort.** Offline 10 h (DSL ops, L1 rules G0-03/G0-12/G0-08, goldens E13 + negatives), live 5 h.

---

## 6. Kinds 4 and 5: existing tool, new tool

### 6.1 Using an EXISTING tool
- **Where it is declared.** `Agent.tools_allowed` (list of `RefSpec` like `buscar_transacciones@1`), `tool` nodes in flows (`config.tool`, `args` paths such as `slots.x`, `facts.y.value.z`, `save_as`, branches `ok/error/timeout/denied`), and `agent` node `config.tools_allowed` (a subset in practice).
- **Important:** at runtime only the `agent` node enforces its own `tools_allowed` (`interpreter/handlers/agent.py`); flow `tool` nodes need the tool to exist in the closure (G0-02) but are not checked against `Agent.tools_allowed` (VERIFIED by grep: no other consumer). So adding a tool to `Agent.tools_allowed` alone changes no behaviour; EXPERIMENT E12 shows it still validates and makes a new ToolDef "referenced". A useful slice therefore edits the FLOW (kind 3).
- **Constraints.** Write tools (`write_reversible`...) need `confirm -> act -> verify` with `readback_by` (G0-05) -> first slice read/compute only; for `agent` nodes G0-07 + G0-24 (`description`, `args_schema`).
- **Eval.** Sandbox replies are seeded per tool id (`LocalSandboxTools`: FIFO, last repeats, `error: sin respuesta sembrada` when missing). `engine.tool_called` has no tool id, so you cannot assert "tool X was called" (only `expect.actions_verified` works for writes). The effect must show downstream (outcome, escalation, a rule threshold).
- **Effort.** 3 h offline + 2 h live, after kind 3.

### 6.2 A NEW tool
- **Authoring.** `ToolDef{id, version, risk_class, min_auth_level, max_auth_age?, idempotent, readback_by?, untrusted_fields, source?, confirmation_ttl, description?, args_schema?}` (writes need `readback_by`). The registry stores the definition only; there is no executor field (`executor_ref` does not exist in Core).
- **"Registered by name".** `HttpToolExecutor` (ADR 0025, `AC/agent_core/adapters/tools/http_executor.py`, enabled with `serve --tools agent_core.adapters.tools:http_tool_executor` + `AGENTCORE_TOOL_SERVICE_URL/TOKEN/TIMEOUT_S`) posts `POST {url}/v1/tools/{id}/execute` with `{tool:"id@x.y.z", args, bound_params, context{...verified claims}, idempotency_key}`. A tool is "registered" iff the service has a handler for that `{id}`. There is ONE URL/token/timeout for all tools of a Core process; only `registry/*` is routed in-process (`BuilderToolExecutor`). Publishing a release does NOT check that the service implements the tool (ADR 0025 "Abierto": `GET /v1/tools` not built). Nuance: the e2e demo double `LazyDemoTools` accepts ANY ToolDef name (falls back to a canned `_radicar` handler), so a demo run will look fine for a tool nobody implemented.
- **Who implements.** The tool-service team (platform side; ADR 0004 in support-platform is "Proposed, no code"; agent-core PR #34 is open). Not us, not the registry. Classification: a new tool's `source` also needs a `FieldClassifier` entry or its fields are tokenised as `pii_direct` (SPIKE fact 4).
- **What the engine can do.** Propose the ToolDef + the flow/agent wiring + a seeded sandbox scenario, and emit a HANDLER SPEC (input `args_schema`, response shape, examples, `source` classification request) as a human-owned dependency (`dependency_blocked(tool_without_executor)` stays the BK0 reason until the service lists the tool).
- **Evaluable?** Yes natively WITHOUT the service, because the sandbox replaces the executor. That makes a native `pass` safe to compute but only a statement about the flow, not about the real tool. Promotion to `prod` must wait for a human to confirm the handler exists (otherwise the node routes to `esc_tool`: `tool_failure` escalation for real customers).
- **Risk.** Medium (ownership) and the main honesty risk (green eval, tool absent).
- **Effort.** Engine side 6 h (ToolDef + wiring + handler spec + seeded scenarios, after kind 3). Live blocked on the service.

---

## 7. Kind 6: NEW AGENT (the user's priority)

### 7.1 How an agent comes to exist (VERIFIED)
`create_proposal(agent_id, origin, title)` does not require the agent to exist; it reads `base = alias(agent_id,"staging")`, which is `None` for a new id. `publish` handles this explicitly (`tx.lock_agent`: "the first publication has no alias to lock", `service.py:600`; `current != p.base_release_id` holds with both `None`). **"First publish has no staging base" therefore means: `Proposal.base_release_id = None`, the candidate is built from the draft ALONE, there is no old yardstick (D3) and no base to clone from.** The "base" is created by the first publish itself (it sets `staging`); `prod` appears only when a human `promote`s. Nothing needs to be created beforehand. The alternative `agentcore registry import <dir>` is admin-only, has no HTTP route, sets `staging` and `prod` at once and has NO eval gate (SPIKE fact 5); it is the infra path, not the engine's.

### 7.2 One proposal, many entities; order and dependencies
One proposal carries everything: no ordering inside the draft, closure computed from references:
`agent` -> `entry_flow`, 7 engine templates (`clarify, abstain, handoff, pending_ack, pending_offer, unsupported_language, input_too_large`), `tools_allowed`, `understand`/`slots_model` (decision models) ; `flow` -> templates, prompts (-> `model_profile`), tools, policies, decision models ; release-level -> `language_detection` (taken from the draft), `injection_ruleset`, `interrupts`, `max_input_chars` (NOT entities). Limits: 50 changes including the suite. The disputas closure is 26 entities (EXPERIMENT: agent 1, flow 1, decision models 2, policy 1, templates 12, prompt 1, model profile 1, tools 5, language detection 1, injection ruleset 1) + the suite = 27 changes.

### 7.3 Experiments that define the minimum (EXPERIMENT E1..E5)
| Draft | Result |
|---|---|
| E1: only the new agent `disputas-corto` | `REG-PIN`: entry flow and the 7 templates do not resolve. A new agent is never "agent + delta"; it must be self-contained |
| E2: full donor closure with new agent/flow/prompt, donor injection ruleset included | `REG-UNREFERENCED` for the injection ruleset (nothing references it without `release_settings`) |
| E5: same closure without the injection ruleset | candidate OK, `new_versions` = 25 (all new in an empty registry; entities identical to published ones are accepted by hash), `release.interrupts = []`, `release.injection_ruleset = None`, `language_detection` resolved from the draft. **The donor's `fraude` interrupt and the injection guard are silently gone.** |
| E4: E2 closure + `release_settings{"injection_ruleset":"injection-rules"}` | candidate OK with the ruleset |
| (side) | cloning `accepts` without `routing` fails `AG-03` at validate (set both or neither) |

Release-level facts (VERIFIED `candidate._decl`, `models.py:ReleaseSettings`, `validation.py:changes_interrupts`): with base `None`, interrupts default to `[]`, injection ruleset to none, `max_input_chars` to 4000. `release_settings.interrupts` needs role `admin` on the writer; `injection_ruleset`/`language_detection`/`max_input_chars` are allowed for `constructor` at the registry, but **our bridge denies `release_settings` entirely** (`release_settings_not_allowed`, BK0 row). Also interrupts matter operationally: an agent without interrupts breaks Jev's Understand schema for conversational agents (SPIKE section 1).

### 7.4 Minimum viable new agent, derived by cloning (two variants)
Naming (no namespaces exist: ids are flat, `^[a-z0-9][a-z0-9_/-]*$`; `/` is only a convention such as `p/`, `t/`, `registry/`): **agent ids must NOT contain `/`** because the alias routes are `/aliases/{agent_id}/{alias}` (entity routes use `{eid:path}`, alias routes do not). Give every NEW entity a distinct id or version so it never collides with a published one (`REG-VERSION-TAKEN`); recommend agent `disputas-corto`, flow `disputa-cargo-corto`, prompt `p/resumen_radicado_corto`, all `1.0.0`; mark engine origin in `Proposal.title` (`[motor:<opp-id>]`) and `docs.rationale`; `origin = auto_detect` (quotas 10/day, 20 evals).

**Variant N-A: task twin (no JEV; first to build).** Clone of our `attention-task` shape on top of the shared tools (`buscar_transacciones`, `seleccionar`, `convertir_moneda`): `mode: task`, no `understand`, flow `start-only` (tool nodes, `rule` with policy, `respond.generate` with template fallback, `escalate`), suite scenarios with only `{op: start}` steps. Our world already proves this shape evaluates end to end on a Core without a jev provider (`OURS/agent-core-assets/worlds/seeded-base.world.yaml`). Draft: agent + flow + prompt/templates + tools + policy + model profile + language detection + suite (about 20 changes).
**Variant N-B: conversational clone with a one-prompt delta.** `disputas-corto` as in the table above: re-emit the 24 unchanged entities, add the 3 new ones, add the suite; evaluation needs the JEV key (understand) on the evaluating Core.

Procedure (what the engine runs): ReadBase donor (`GET /aliases/{donor}/staging` -> `GET /releases/{rid}` -> `GET /entities/{kind}/{id}?version=` x26) -> compile `closure_copy` + delta -> L2 dry-run via bridge (base `None` path) -> `POST /proposals {agent_id:"disputas-corto", origin:"auto_detect", title}` -> `PUT draft` (one write, `expected_rev` 0) -> `validate` -> `freeze` -> `evaluate {suite_id, suite_version}` -> STOP (human). Human: `aprobador` + TOTP approves the candidate hash, `publish` (needs `Idempotency-Key`) points `staging`; separate human `promote` to `prod`; an `admin` human must add interrupts/injection via `release_settings` BEFORE promote (until Core or our bridge allows the engine to carry them for a new agent). Traffic requires platform configuration (agents are wired by name) or directory `routing`; none of that is ours.

### 7.5 Evaluation of a brand-new agent
No base -> no old yardstick: the gate is only (a) the 4 platform guardrails = 0 and measured, (b) every scenario of the engine-authored suite passes in ALL repetitions, (c) each NEW `gate`/`guardrail` metric of the agent has a self-set `floor` (`_new_items`). The suite and the floors are written by the same actor that wrote the agent (ADR 0020 "accepted risk"; spec section 8.5: a new agent's suite is reviewed in depth by the approver). So `pass` = "starts, behaves on N synthetic scenarios, no guardrail hit". Mitigations: parity suite from the donor (same scenarios as the donor's behaviour, sealed beforehand), floors set from the donor's measured values, never from the candidate's own runs, and a human review item "suite and floors" (section 9).

### 7.6 Effort and risk
Offline 10 h (ReadBase closure copy, add-agent/flow/prompt op families with absent-digests, base-`None` dry-run, goldens E1/E2/E4/E5 as negatives/positives, `release_settings` gap documented as `release_level_change`), live 6 h (task twin first: no key; then clone with key). Risk: high for the safety gap (7.3) and for approvals/promote being human; medium technically.

---

## 8. Eval part 1: what a suite is in agent-core, how it is defined and run

### 8.1 Anatomy (VERIFIED `AC/agent_core/registry/suite.py`, `contracts/registry/EvalSuite.json`)
`EvalSuite{id, version (exact), agent_id, repetitions 1..10 (default 3), scenarios[1..200], thresholds{metric_id -> {noise_margin>=0, floor?}}}`, `extra=forbid`.
- **Scenario (`source: scripted`, enabled):** `id ^[a-z0-9][a-z0-9_-]*$`, `principal{id, attrs{str->str}}` (always run as principal type `customer`: `composition/evaluation.py:_principal`), `steps[1..50]` with exactly one leading `start`, then `turn{text<=4000, lang?}` or `confirm{answer yes|no}`; each step has `auth anonymous|session|step_up` (default **step_up**), `seed.tools{tool_id:[{status,result,error}]}` (FIFO, last repeats), `sensitive_values[]`, `expect{outcome?, actions_verified[], escalated?}`, `assertions[<=20]{event, where[<=8 predicates], expect at_least_one|none}`, `repetitions?`.
- **Scenario (`source: dataset`):** `{dataset_id, dataset_hash}`; DISABLED (`dataset_source_disabled`, open topic #20).
- **Inputs:** only the scripted turns; a `task` agent gets no `input` (finding 4).
- **Outcomes/oracles:** `Outcome` enum {resolved, abstained, cancelled, clarify_exhausted, completed, failed, abandoned, escalated, transferred}; assertions over the CLOSED catalog `AC/agent_core/domain/metric_catalog.py`: `engine.turn_completed{entry,duration_ms,degraded}`, `engine.escalated{reason_code,target_queue,priority}`, `engine.run_closed{outcome,closed_by}`, `engine.tool_called{status,latency_ms,attempt}`, `engine.agent_step`, `engine.action_verified{result}`, `engine.response_emitted{kind,fallback_used,validator.ok,llm.*}`, `engine.response_failed`, `engine.access_denied`, `engine.injection_flagged`, `engine.handoff_resolved`; `registry.*` events are unobservable in a scenario (left unmeasured, never zero). No response text, no tool id, no slot values.
- **Metrics and thresholds:** metrics live in `Agent.metrics` (`MetricDef{id, description, role guardrail|gate|monitor, higher_is_better, expr}`), a DSL (event, filter, count/sum/avg/percentile/rate, window); thresholds in the suite (`missing_threshold` / `unknown_threshold_metric` otherwise). `platform_*` metric ids and thresholds are reserved: `MT-05` and `forbidden_role` at `put_draft`. Four universal platform guardrails, zero tolerance, must be measured: `platform_pii_leak` (any `sensitive_values` string found in serialized events), `platform_unverified_success_claim`, `platform_unverified_write`, `platform_unapproved_knowledge_citation`.
- **Judge / LLM-as-judge:** a `Judge` port exists in `ScenarioEvaluator` (informative `judge_notes`) and `JudgeExpr` exists in the metric DSL, but **`serve` builds `ScenarioEvaluator(harness, LocalSandbox, max_workers=1)` with no judge** (`composition/serve_registry.py`) and the in-memory evaluator leaves any `judge` metric unmeasured ("no judge in the gate"). So at head: no LLM-as-judge, no semantic scoring.
- **Determinism:** scripted steps and seeded tools, sandbox per run (`LocalSandbox.provision/teardown`; tools must report `is_sandbox`). The model calls are real (gateway, JEV) so output varies; that is why repetitions exist and a scenario passes only if ALL repetitions pass; metrics pool all events of all repetitions; `avg`/`rate` rounded to 4 decimals. Runs one scenario at a time in `serve` (shared clock/ids).
- **Budgets:** per run `Agent.budgets` (disputas: 0.50 USD, 20000 tokens, 3 model calls/turn); per proposal 20 evaluations when `origin=auto_detect`; per-proposal cost cap deferred (`quotas.py`). Cost of one evaluate = scenarios x repetitions x (1 JEV call per user turn for conversational agents + each `respond.generate` / `agent` step).

### 8.2 Defined and stored
- A suite is a DRAFT KIND `eval_suite` inside the same proposal: `{kind:"eval_suite", content:<EvalSuite>, docs}`; counts against the 50 changes and 256 KiB; changes `candidate_hash`.
- Stored as a versioned entity (blob + `reg_versions`), readable through `GET /v1/registry/entities/eval_suite/{id}?version=`; NOT part of the engine release; recorded as `eval_suite_refs` of the published release (one suite per agent; the next proposal's OLD yardstick). Immutable: any byte change needs a new version (`REG-VERSION-TAKEN`).
- Who may write: any principal `builder` with `constructor` (our engine); approval is human. Nobody can edit `platform_*` from a proposal. Weakening a base suite (remove/alter scenarios, lower floor, widen noise margin, remove metric, lower repetitions) is classified `yardstick_changes` and the approver must pass `accept_yardstick_loosened` or get `loosening_not_accepted` 409. Adding scenarios/metrics, raising floors is free ("tightening").
- Registry-e2e fixtures contain NO `eval_suites/` (e2e runbook): every proposal against the shared registry today must ship its own suite, and that suite becomes the base yardstick (D3 means the old yardstick is skipped when the base recorded none).

### 8.3 Executed
`POST /v1/registry/proposals/{pid}/evaluate {suite_id, suite_version?}` (role `constructor`, synchronous). Preconditions: state `candidate` (frozen), `suite_problems` empty, candidate hash unchanged. Runs `cand_on_new`; with a base that recorded a suite also `base_on_old` and `cand_on_old` (same suite shared -> one candidate run measured with both definitions). Result `EvalReport{verdict pass|fail|failed_infra, items[GateItem{metric_id, phase base_yardstick|new_yardstick|platform, role, value, base_value, noise_margin, floor, passed, reason}], runs{...}, results[ScenarioResult], judge_notes, yardstick_changes, detail}`.
| Verdict | HTTP | Proposal state |
|---|---|---|
| pass | 200 `EvalReport` | `evaluated` |
| fail | **409 `gate_failed`**, payload = EvalReport (+ `eval_run_id`, see section 10) | back to `draft`, `rev+1`, `candidate_hash=null` (must re-freeze) |
| failed_infra (gateway or provider failed during a scenario) | 200 `EvalReport(verdict="failed_infra", detail)` | stays `candidate`; never approvable |
Keys/infra: gateway URL + token (provider key lives in the gateway), JEV key for conversational/jev paths, a separate eval Postgres DSN (`agentcore_eval`), staff-key principal `builder` + `constructor`.

### 8.4 A minimal valid suite for `disputas` (validated)
I validated this exact document with agent-core's `EvalSuite.model_validate` and `suite_problems(disputas@1.0.0, suite) == []` (disputas declares no metrics, so `thresholds` can be empty; the platform guardrails are measured automatically). It follows the flow `disputa-cargo` (collect -> `buscar_transacciones` -> `match-cargo` -> `seleccionar` -> `convertir_moneda` -> policy `> 500` -> `confirm` -> `radicar_pqr` -> `verify obtener_pqr` -> `respond`), adapted from the demo suite in our `attention-demo` world. NOTE: scenario 1 depends on the stand-in classifier/Jev behaving at the `match` and `understand` steps; against a real Core it needs the JEV key.

```json
{
  "id": "disputas-eval", "version": "1.0.0", "agent_id": "disputas", "repetitions": 3,
  "scenarios": [
    {"id": "resuelto",
     "principal": {"id": "cust-001", "attrs": {"country": "CO"}},
     "steps": [{"op": "start", "auth": "session"},
               {"op": "turn", "text": "no reconozco un cargo de ciento veinte dolares en una tienda", "auth": "session"},
               {"op": "confirm", "answer": "yes", "auth": "step_up"}],
     "seed": {"tools": {
        "buscar_transacciones": [{"result": [{"transaction_id": "tx-1", "amount": "120.50", "currency": "USD"},
                                             {"transaction_id": "tx-2", "amount": "30.00", "currency": "USD"}]}],
        "seleccionar": [{"result": {"transaction_id": "tx-1", "amount": "120.50", "currency": "USD"}}],
        "convertir_moneda": [{"result": "120.50"}],
        "radicar_pqr": [{"result": {"status": "Open", "id": "pqr-t-1"}}],
        "obtener_pqr": [{"result": {"status": "Open", "id": "pqr-t-1"}}]}},
     "expect": {"outcome": "resolved", "actions_verified": ["radicar_pqr"], "escalated": false},
     "assertions": [{"event": "engine.action_verified", "where": [{"field": "result", "op": "eq", "value": "verified"}]},
                    {"event": "engine.response_failed", "expect": "none"}]},
    {"id": "escala_por_monto",
     "principal": {"id": "cust-002", "attrs": {"country": "CO"}},
     "steps": [{"op": "start", "auth": "session"},
               {"op": "turn", "text": "no reconozco un cargo de seiscientos dolares", "auth": "session"}],
     "seed": {"tools": {
        "buscar_transacciones": [{"result": [{"transaction_id": "tx-9", "amount": "600.00", "currency": "USD"}]}],
        "seleccionar": [{"result": {"transaction_id": "tx-9", "amount": "600.00", "currency": "USD"}}],
        "convertir_moneda": [{"result": "600.00"}]}},
     "expect": {"outcome": "escalated", "escalated": true},
     "assertions": [{"event": "engine.escalated",
                     "where": [{"field": "reason_code", "op": "eq", "value": "policy:escalamiento-disputa-monto"}]}]}
  ],
  "thresholds": {}
}
```
Draft op carrying it: `{"kind":"eval_suite","content":<above>,"docs":{"description":"...","rationale":"...","changelog":"..."}}`; then `evaluate {"suite_id":"disputas-eval","suite_version":"1.0.0"}`. Cost sanity: 2 scenarios x 3 repetitions x (1-2 Jev calls + 1 generation) per evaluate.

---

## 9. Eval part 2: can OUR engine generate suites for the agents it modifies?

**Feasibility: yes for structural regression suites, no for quality judgments.**

Simplest version (about 8 h offline + 3 h live; precondition of every proposal because the shared registry has no suites):
1. **Inputs:** the target agent closure (ReadBase), the flow graph (nodes/branches from the compiled Flow), the tools with their `args_schema`, and the signal's evidence cells (segment, channel, country, category) from the verified signal.
2. **Scenario families from graph coverage, not from the change:** one scripted scenario per terminal path of the base flow (resolved, each `escalate` reason, `abstained`, `cancelled`, tool error/timeout/denied branches via `seed.tools[...].status`), plus locale variants (es/pt via `lang`), plus an injection-attempt turn. These are the REGRESSION ("guard") scenarios.
3. **Evidence-derived scenarios ("target"):** N scenarios (start with 3-5) whose principals/attrs and synthetic message wording come from the signal cells (country, product kind) with synthetic paraphrases; `expect` states the outcome the signal says should change (for example outcome `resolved` where the base escalated). These are the ones the base is allowed to fail (the gate skips base-failing scenarios in `_base_items`) and the candidate must pass.
4. **Fixed oracle assertions:** `expect.outcome`, `expect.escalated`, `actions_verified` for writes, `engine.escalated{reason_code}`, `engine.response_failed` none, plus `sensitive_values` (synthetic canaries) so `platform_pii_leak` is exercised.
5. **Seeds:** FIFO tool replies from a deterministic reference trace (V3 CAP-22); a scenario whose branch depends on arguments or state is marked `not_evaluable_native` and moves to the Pulso campaign.
6. **Thresholds:** none for agents with no metrics; for new metrics, `floor` from the DONOR/base measured values, never from the candidate's run.

Pitfalls (each one a test to write):
- **Circularity.** If the engine writes both the change and the test of the change, the test can pass vacuously. Rules: guard scenarios are derived only from the BASE flow graph and base policies; target scenarios are derived from the signal and sealed (digest) BEFORE the candidate is compiled (V3 section 17 and ScenarioFactory: OracleSpec versioned before executing candidates); the scenario author and the change author are different lanes (our Verifier or a fixed generator, not the Builder); `expect` must not be copied from the candidate's runs.
- **Native blind spots** (section 8.1): no response text, no tool identity, no slot values, no judge, FIFO seeds without argument matching, no `input` for task agents, principal fixed to `customer` (advisor-only `copiloto-asesor` and builder-only agents like `constructor-chat` are very likely not evaluable; the harness would be refused by the agent's `invocable_by`: INFERRED, verify in a live S0 step). A green native verdict must never be presented as improvement evidence; it is the Core yardstick (V3 `CombinedGate`).
- **Split and leakage.** `dataset` scenarios are disabled, so real E0 cases cannot enter the suite by id/hash. The suite is stored in the registry and is readable by any builder, including future proposals: only synthetic content, abstracted from E0 aggregates (k-anonymity as in the treated payload rules), and never `final_locked` cases (V3 CAP-21: `pulso:final_locked_leak` canary over `changes`, `docs`, `GET proposal`). Map: development scenarios = what the Builder can see and iterate on = the Core suite; validation = held-out variants of the same families, run in the Pulso campaign; `final_locked` = sealed, only Pulso campaign, never in the registry.
- **Yardstick loosening.** The generator may only ADD scenarios or raise floors for an agent that already has a suite; anything else triggers `accept_yardstick_loosened` and must be a deliberate human act. Never regenerate a base scenario with changed content.
- **Cost.** Each evaluate is real LLM spend (repetitions x scenarios); 20 evals per `auto_detect` proposal. Start with `repetitions: 3` and at most 8 scenarios.
- **Version discipline.** Same suite id + version with different bytes is `REG-VERSION-TAKEN`; bump the suite version when scenarios change; `evaluate` names the exact `suite_version` (never "latest").

Must stay human-owned: (1) approving the suite as its own review item, especially for a NEW agent (floors are self-set); (2) any `yardstick_loosened` acceptance; (3) the list of safety families that must never regress (fraud/escalation, PII) and their oracles; (4) thresholds/floors of existing metrics and the platform guardrails (not editable anyway); (5) `final_locked` sets; (6) the decision to promote to prod; (7) interrupts and injection ruleset of a new agent.

---

## 10. Discrepancies and open points found while reading

1. V3 section 27/31.7.1 and H6 say the 409 `gate_failed` report carries no `eval_run_id`. `service.py:_gate_payload` merges `eval_run_id` into the payload (note "N-10"). Verify on the pinned image; if confirmed, the V3 wording and any code built on "no eval_run_id" are stale.
2. V3 section 31.4.7 says `GET /releases/{rid}` does not return interrupts/language_detection/injection_ruleset/max_input_chars. At head `ReleaseDetail` returns them (`models.py:206-221`, `_detail`). Stale; it enables a local `release_hash` check (N-03).
3. V3 section 31.4.4 puts "create a new agent" outside the first cut (D-10). This plan proposes revisiting D-10 after F + templates, with the release-settings gap (section 7.3) as the explicit condition.
4. `ReleaseSettings` fields `injection_ruleset`, `language_detection`, `max_input_chars` are writable by `constructor`; only `interrupts` demands `admin`. A narrow bridge exception (new agents only, those three fields) would remove the injection gap without touching interrupts. Needs a decision by the bridge owner and the user.
5. UNKNOWN: whether a task-mode agent with an `agent` node completes on the shared Core, and whether the harness refuses a non-`customer` agent; both need one live check each (about 1 h).
6. Experiment limits: `build_candidate`/`validate_candidate` use the fixtures only; no Postgres, no HTTP, no quotas, no evaluate. The service-level behaviours (409 vs 200, quota, publish) are read from code, not executed.

## 11. Asks to forward (one sentence each)
- agent-core team: register `rule` and `llm_structured` in `serve` providers (or a documented `--providers` factory), and say how calibration thresholds for them are supplied.
- agent-core team: allow a new agent proposal to carry `injection_ruleset` without admin (already allowed) and consider a "clone-from-agent" base (`create_proposal` with `base_agent_id`) so a clone does not have to re-send 24 unchanged entities or lose interrupts.
- Core operator/admin: add interrupts and injection ruleset of any engine-born agent before `promote`; provide the JEV key to the evaluating Core for conversational evaluations.
- tool-service owners: implement `pulso`/new tool handlers by name before any release that references a new tool reaches `prod`; publish `GET /v1/tools` (ADR 0025 open item).
- bridge owner (ours): allow the three `release_settings` fields for new agents only; extend the ref grammar to `/`.

## 12. Evidence index
- Registry: `AC/agent_core/registry/{service,candidate,suite,validation,models,roles,errors,quotas,http,entities}.py`; `registry/evaluation/{evaluator,gate,scoring,report,yardstick,metric_eval,local_sandbox}.py`; `composition/{evaluation,serve_registry,serve_ports,serve,decision,builder_tools}.py`; `decision/{service,understand}.py`, `decision/providers/{rule,classifier,llm_structured}.py`; `domain/{entities,nodes,metrics,metric_catalog,base}.py`; `flows/{agent,rules/phase5}.py`.
- Contracts: `AC/contracts/registry/EvalSuite.json`, `contracts/schemas/{Agent,DecisionModelDef,ProviderSpec,ToolDef,Template,Policy,Flow,RunInput}.json`; ADRs 0009, 0018, 0019, 0020, 0025; spec `docs/specs/2026-09-30-evaluacion-y-metricas-design.md`.
- Fixtures: `AC/tests/fixtures/registry-e2e/**` (no `eval_suites/`).
- Ours: `OURS/contracts/artifact-kinds/{matrix.json,DIGEST.json,README.md}` (digest `sha256:ae0ffc15...`), `OURS/seams/crates/steps/src/compile.rs`, `OURS/docs/reports/e2e/bknl-denied-kinds.md`, `OURS/agent-core-assets/worlds/{attention-demo,attention-task,seeded-base.world.yaml}`, `OURS/core-bridge/src/pulso_core_runtime/factories.py`.
- V3 spec: sections 16, 17, 27, 31.4.3-31.4.12, CAP-13..22.
- Experiment script (scratchpad, not a repo): `$env:USERPROFILE\AppData\Local\Temp\claude\D---codex-factored\18ab5ab6-8b27-4650-818f-7d8bb6599946\scratchpad\x\exp.py` and `x\suite.json`; its output is the source of every "EXPERIMENT E#" claim and can seed the offline goldens.
