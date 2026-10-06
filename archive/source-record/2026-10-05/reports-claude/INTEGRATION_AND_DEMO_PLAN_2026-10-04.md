# Integration state, seams and demo ladder (Pulso engine team)

Date 2026-10-04. Author: Claude (read-only research). Scope: facts from GitHub (`gh`) and shallow clones in the scratchpad (agent-core fetched with `--shallow-since=2026-08-01`; support-platform, data-lab, data-pipeline, llm-gateway fetched to `origin/main`). Nothing was run: no tests, no builds, no AWS. Every "breaks" statement below is from reading code and contracts, not from running our drift gates; the first action of any follow-up is to run them (section 1.6).

Conventions: times are UTC-5 as git shows them. "Pin" = what our engine is built against (agent-core `c814c2b`, contracts 1.3.0; platform capture `a492bfa`, platform-contract 1.1.0). `doubles[]` vocabulary: real, real-narrow, local-model, agent_roleplay, recorded, stand-in, simulated (plus not_exercised and blocked(dep) from plan section 1.1).

---

## Part 1. Current state (facts)

### 1.1 Head vs pin

| Repo | Our pin | Head of `main` (2026-10-04) | Distance | Open PRs |
|---|---|---|---|---|
| agent-core | `c814c2b` 2026-10-03 16:03 (merge of PR #30) | `56354dd` 2026-10-04 14:49 (merge of PR #32 `feat/e2e-stack`) | 6 commits, 2 PRs (#31, #32) | 0 (31 of 32 PRs merged, rest side branches) |
| support-platform | `a492bfa` (slices 0-3, contract 1.1.0 captured 2026-10-03) | `eeb73a8` 2026-10-04 15:33 (merge of PR #10) | 42 commits total in repo, 10 PRs, all merged today | 0 |
| llm-gateway | `63155b6` 2026-10-03 11:12 | same `63155b6` | 0 | 0; 0 tags, 0 releases |
| data-pipeline | n/a | `2f36f6b` 2026-10-04 | | |
| data-lab (E0 contracts, synthetic sample) | n/a | `0e666a6` 2026-10-04 | | |

Important facts about the pins:

1. **`a492bfa` does not exist any more.** The platform was split out of the data repo on 2026-10-04 (`4333271` "Split platform into its own repository", then `ace293a` on the data side) and the history was rewritten: `git cat-file -t a492bfa` fails in support-platform, data-lab and data-pipeline, and `gh api .../commits/a492bfa` returns 422. The closest equivalent by slice naming is `7d2ae3a` "Plataforma S3: supervision" (2026-10-03). That mapping is my inference, not a statement from the product team. Our contract README, `model.py`, `r1-gap-list.md` and the journals cite a SHA nobody can resolve. Action: re-stamp the platform contract against a SHA that exists (see 2.B, P1).
2. **agent-core pin is nearly current.** Only two things changed since `c814c2b`, and both are on our side's ask list (below). The big movement is not in agent-core, it is in the platform (1.3).
3. **The Core bridge has a dual pin** (ADR 0010 of `core-bridge`): `PIN_SHA = c814c2b...` in `pulso_core_runtime/__init__.py` while the wire snapshot directory is `agent_core@894fa65/` (the merge of PR #29). Both are ancestors of `main`.

### 1.2 agent-core: what changed since `c814c2b`

| Commit / PR | Date | Theme | What it changes for us |
|---|---|---|---|
| `59ad52f` / PR #31 `fix/improvement-contract-followups` | 2026-10-03 (merged 2026-10-04 02:00Z) | New problem code `idempotency_in_progress`; `resolve_ports` contract | **Closes our N8-02 ask** (ambiguous 409 `idempotency_conflict`). Additive enum value in `contracts/schemas/ProblemCode.json` and the 409 descriptions in `contracts/openapi.json`. `contracts/VERSION` stays `1.3.0` and `info.version` stays `1.3.0`: an enum was extended without a version bump. Our drift gate must key on a digest, not on the version string. Our wire snapshot (`gen-wire.ps1 -Check`) and `bridge-contract/gen.py --check` will report this diff on a bump (expected, not run). |
| `44707bd` | 2026-10-04 | Handoff resolution events are chained like the rest of the audit | Audit chain content for handoff resolution changes; relevant only if we verify chains over handoff events (our exporter does chain verification). |
| `0c75429` / PR #32 `feat/e2e-stack` | 2026-10-04 | Local e2e stack (`scripts/e2e/*`), `registry-e2e` fixtures (5 agents, 5 releases, 5 flows, tools), copilot answer quality (typed data in agent output), `docs/plan-e2e-produccion.md` and `docs/runbook-e2e.md` | Gives us **the real artifact set the platform runs** (G5 of our gap list is answered by fixtures, see 2.A, A5). Test-only for the engine proper (`agent_core/composition/serve*.py`, `builder_tools.py` changed: `serve --registry-api` now routes `registry/*` tools to `BuilderToolExecutor` under service identity `constructor-bot`). |

Not changed since the pin: runtime OpenAPI paths (still 7: runs, run, transcript, session turns, session lineage, handoff, handoff resolution), `contracts/events/catalog.json` (types `run.started|closed|transferred`, `handoff.created|resolved`, `release.published|promoted|revoked`), registry route list, artifact kinds, `contracts/VERSION`.

Themes you asked about, state at head (`56354dd`):

| Theme | State at head |
|---|---|
| New artifact kinds / worlds / tools | No new kinds. Fixtures `registry-e2e`: agents `recepcion`, `disputas`, `consultas`, `copiloto-asesor`, `constructor-chat` (all `@1.0.0`, alias `prod` in releases `recepcion-demo`, `disputas-demo`, ...), flows `recepcion`, `disputa-cargo`, `consulta-pqr`, `asistir`, `construir`, decision models (`understand-turno`, `match-cargo@2.0.0`, `elegir-especialista`, ...), 10 tools (`leer_movimientos`, `leer_productos`, `leer_pqr_cliente`, `radicar_pqr`, `obtener_handoff`, `leer_transcript`, ...). Tools are synthetic (`cust-001`); real `ToolExecutor` is not built (ADR 0025 is only a draft inside platform ADR 0004). |
| Jev / decision models | **PR #28 `feat/jev-via-gateway` is still NOT on main** (head `6c8aad8`, 2026-10-03; `git grep '/v1/jev'` finds code only on that branch; its base was `feat/http-llm-gateway`, which had already been merged by PR #26 an hour earlier). Main still needs `AGENTCORE_JEV_API_KEY` and a direct Jev transport. Conversational agents (all five e2e agents use `understand`) need Jev to work at all: without it every turn falls under threshold. |
| Evaluation / approval / publication API | Registry routes at head: `POST /proposals`, `GET /proposals/{id}`, `PUT .../draft`, `.../validate`, `.../freeze`, `.../reopen`, `.../evaluate`, `.../approve`, `.../reject`, `.../publish`, `POST/GET /aliases/{agent}/{alias}`, `GET /versions/{kind}/{id}`, `POST /releases/{rid}/revoke`, `GET /releases/{rid}`, `GET /releases/{a}/diff/{b}`, `GET /entities/{kind}/{id}`, `GET /runs/{id}/lineage`. **There is no list-proposals route** (PR #24 `feat/registry-listados` and PR #23 `feat/registry-contratos` are merged only into side branches, not main; `Idempotency-Key` handling does exist in `registry/service.py`). Only a human at `step_up` can approve, reject, publish, promote, revoke. Evaluation needs an `eval_suite` entity; **no e2e agent has one**, so nothing past `candidate` is reachable on them (the platform team found the same, slice-16 section 8). |
| Registry / alias semantics | Release yamls bind `agent@^1` to alias `prod`. The platform builder bases new proposals on the agent's `staging` release (slice-16). Quotas as in our plan (10 proposals per 24 h, 20 evaluations per proposal). Alias-effect semantics for in-flight sessions are not documented (ask A-6). |
| Events / outbox / exporter | Outbound event contract v1 (`contracts/events/`), outbox relay (`agent_core/relay`, ADR 0023, opt-in S3 blobs, SNS publisher, DB pool, all OFF in e2e). Export API `/v1/export/runs`, `runs/{id}/events`, `registry-events` behind role `exporter` (staff issuer must mint the role). Release events carry no actor and no free text (`ReleaseData`: release, proposal ids). |
| DB / Postgres | Postgres 16 is the only real store (compose, e2e port 55432), `agentcore migrate` exists (expand-only policy, ADR 0022). ADR 0023 scale-out (S3 blobs, relay, pool) merged in PR #27 but its AWS validation is on the "separate test in staging" list. |
| Auth / service identities | Ed25519 JWS principals and delegations; `--identity-keys` (runs) and `--staff-keys` (registry) are different key sets (a staff-signed credential on a run is `credentials_invalid`, found by the platform team); lazy key reload every 5 s. `grant_active` and `AuthzPort` are still demo doubles behind `AGENTCORE_ALLOW_DEMO=1`. |
| Deploy / Docker | `Dockerfile` (non-root, `AGENTCORE_GIT_SHA` build arg, `GET /version` unauthenticated), `scripts/e2e/*.ps1` (Docker Desktop based), compose with Postgres only. |

Roadmap documents in agent-core that state the plan: `docs/plan-e2e-produccion.md` (2026-10-03, phases 0-5; says preparation is built, tests with real models need keys; lists production blockers: real tools, `AuthzPort`, persistent transcript, calibration, `FieldClassifier`, identity with `grant_active`, `ALLOW_DEMO` off, secrets/Terraform, M11 audit-replay divergence, S3/relay/pool in staging, eval gate for agents without suite, builder retention caps) and `docs/runbook-e2e.md`. ADRs 0019-0024 are the relevant series (internal agents, evaluation, agent transfer, stable surfaces, AWS scale-out, gateway as service).

### 1.3 support-platform: what changed (the real news)

All 10 PRs and ~20 commits landed on 2026-10-04 between 10:44 and 15:33, authored by Juan José Zapata (`juazapataca`, the agent-core owner) and Juan Esteban Mejía (frontend, brief). The same person owns agent-core and the platform's AI integration, so the two integrations are one design.

Timeline (all merged today): PR #1 brief refresh (15:44Z) -> #2 English routes -> #3 **S13+S14 assistant** (17:48Z) -> #4 **S15 copilot** (18:32Z) -> #5/#7 language marks -> #6 **S17 sweep, `grant_active` endpoint, ADR 0004** (19:06Z) -> #8 Portuguese policy H1 -> #9 **S16 agent builder** (20:18Z) -> #10 S17 hardening (20:28Z).

What the platform now is (ADR 0003 "Accepted in principle", 2026-10-04): **agent-core integrated INTO the platform**.

| Slice | State | What it does |
|---|---|---|
| S13 | done | `AgentCredentialIssuer` (platform signs Ed25519 principals/delegations, publishes keys that `agentcore serve` loads), `AgentRuntime` and `AgentRegistryClient` ports with HTTP adapters and in-memory fakes, contract tests against `agent-core-openapi.json` + `contracts/registry/*.json` copies |
| S14 | backend done, frontend not wired | AI-handled customer chat: new case status `with_assistant`, turn author role `assistant`, `assistant_sessions` table, `AgentTurnProcess`, fallback to the language queue on failure, escalation via handoff packet, resolution sent back at close. Env: `CC_AGENT_CORE_URL`, `CC_AGENT_KEYS_FILE`, `CC_ASSISTANT_AGENT` (default `recepcion@prod`), `CC_BANK_CUSTOMER_LINKS_FILE` |
| S15 | backend done | Analyst copilot (`copiloto-asesor`), `copilot_threads` |
| S16 | backend done, screens are "the frontend team's" | Supervision/Administration agent builder: proposals, draft, validate, freeze, evaluate, approve/publish/promote with a **fresh TOTP code per decision** (`stepUpCode`, platform grants `step_up` for 2 minutes), builder chat (`constructor-chat`), `builder_proposals` index (agent-core cannot list). `builder.*` audit events (family `agents`) carry ids/states/counters only |
| S17 | partial | Sweep for lost assistant work, `GET /api/v1/internal/grants/{grantRef}` (answers agent-core's `grant_active`). **Not done:** Postgres + migrations (still SQLite with `create_all`, `OutdatedSchemaError`: delete the DB), real email, real customer auth, outbound-event consumption, trace ids across both systems |
| T | **planned, no code** | Tool backend: `HttpToolExecutor` in agent-core (ADR 0025 draft) + `tool-service` over data-pipeline `gold_restricted.duckdb` (ADR 0004 "Proposed, design only") |

Statement of the integration plan (ADR 0003 section 9): "The platform's event log emits the AI entities of the `platform_history` contract again (routing step, tool call, copilot query)... agent-core's outbound events (`run.*`, `handoff.*`, `release.*`) are consumed later, by the relay or the export API, for analytics and not for state." So release/observation exposure for us (EXT-2) is deliberately deferred by the platform.

Platform and our improvement engine: grep of ADRs, brief, README and RUNBOOK finds **no mention** of the improvement engine, release exposure to external consumers, or EXT-2. The only release-shaped data the platform produces are its own `builder.proposal_published`, `builder.alias_promoted`, `builder.release_revoked` audit events (ids/states only, in `event_log`, family `agents`).

Docs staleness: `docs/platform/DATA_MODEL.md` says "slices 0 to 12", "for people only", lists 4 case statuses and 3 author roles; the code (`tables.py`, `domain/cases/values.py`) already has `with_assistant`, `assistant`, `assistant_sessions`, `copilot_threads`, `builder_threads`, `builder_proposals`, `bank_customer_links`. Treat code and `backend/openapi.json` as the truth.

### 1.4 What breaks our assumptions (read from code, not run)

**Platform contract 1.1.0 vs platform head** (compare `platform-contract/platform_contract/model.py` with `domain/cases/values.py` and `tables.py`):

| Our 1.1.0 | Platform head | Effect on our row validation (fail-closed) |
|---|---|---|
| `cases.status` in queued/assigned/in_progress/closed | adds **`with_assistant`** | Every assistant-handled case row fails validation. This is the main breakage once S14 is on. |
| `turns.author_role` in customer/analyst/system | adds **`assistant`** (`author_id` = `id@version`) | Every assistant turn row fails. Also `cases.last_*_author_role`. |
| `turns.kind` in message/routing/notice | adds `transcript`, `note`, `email` | Rows fail. |
| `cases.channel` in app_chat/web_chat | `chat_app chat_web phone_inbound phone_outbound email` (DATA_MODEL; naming differs even for chat) | Enum mismatch; verify against `openapi.json`. |
| `cases.priority` in low/medium/high | `none low medium high critical` | Rows with the new default `none` fail. |
| `assignments.reason` (1.1.0 list) | adds `outbound_call`, `assistant_handoff` | Rows fail. |
| allow-listed case columns | new columns `rating_*`, `open_escalation_id`, `active_call_id`, `queue_label`; new tables `escalations`, `calls`, `notifications`, `assistant_sessions`, ... | Not selected (allow-list), so no leak; but our schema fingerprint will differ and the contract says "Any table not allow-listed is refused by default" (correct). |
| Event catalog 1.1.0 | new types `case.priority_changed`, `case.rated`, `case.assistant_started`, `case.assistant_released`, `assistant.*` (session_started, input_queued, turn_answered, step_up_verified/rejected, ended), `copilot.query_asked/answered`, `builder.*` (13 types), many `staff.*` | Per our policy unknown/planned types are counted, quarantined with a finding and the batch still confirms: **no hard failure, a flood of quarantine findings.** The AI events are exactly the signal families we want and they are all `unknown` to the exporter today. |
| Denied auth events | `auth.password_accepted`, `auth.mfa_*` still emitted | Still denied, still fine. |

**agent-core assumptions**:

| Assumption | Status |
|---|---|
| Jev `blocked(jev)`, DEMO-0 uses `llm_structured` stages | Still true: PR #28 not on main. |
| Ambiguous 409 `idempotency_conflict` (N8-02), we disambiguate by reconcile read | Now fixable: `idempotency_in_progress` exists at `79233c4`. Keep the reconcile fallback until the pin moves. |
| Only `prompt` (replace) and `eval_suite` (add) are proposable (BK0 matrix) | Unchanged at agent-core; the matrix stays valid. |
| `/internal/v1` and `release_events` EXT-2 | `/internal/v1` is OUR bridge API (`pulso_core_runtime`), not agent-core's. agent-core's own HTTP surface is `/v1/*` plus `/v1/registry/*`. A bump affects us at the Python import level (our runtime composes the pinned `agent_core` package, closed pin-symbol list in `pin.py`), not at the HTTP level. |
| Alias `prod` is the platform's live alias; we publish to `staging` only | The platform runs `recepcion@prod` by default and builds proposals on `staging`. Publishing to `prod` changes what customers get. Our staging-only rule is consistent with that. |

**Not breaking**: llm-gateway unchanged since pin; `/v1/generate` contract the Core uses is unchanged.

### 1.5 Branches and who works on what

- agent-core: only one author line matters (Juan José Zapata `juazapataca`, 355+29+26 commits since 2026-09-28, plus Claude sessions: 138 commits) so, in practice, one human plus Claude sessions. No open PR. Unmerged side branches with work: `feat/jev-via-gateway` (#28), `feat/registry-listados` (#24), `feat/registry-contratos` (#23) are merged into other branches but not into main; `claude/m5-m8-m4-parallel-8z4wxx`, `feat/m4-m5-m8-pendientes`, `feat/m9-api`, `feat/cableado-motor` are older.
- support-platform: branches `feat/agent-builder`, `feat/agent-core-assistant`, `feat/analyst-copilot`, `feat/assistant-hardening` (all merged). Next named work (ADR 0003/0004): S17 remainder (Postgres, migrations, real auth, outbound-event consumption), track T (tool service). No dates anywhere. Frontend wiring of S14-S16 is stated as "another team's".
- llm-gateway: branches `feat/consumer-docs-release-and-input-caps`, `feat/jev-passthrough` (merged). `release.yml` exists, **0 tags, 0 releases** (no image to pull).
- data-pipeline (same author): `2f36f6b` adds a read-model contract and `demo_links` (deterministic platform-customer to dataset-customer links, private output under `data/demo`): this is the bridge for `CC_BANK_CUSTOMER_LINKS_FILE` and for our G4.
- GitHub Issues: none open in any of the three repos.

### 1.6 First checks before trusting any of this (about 1 agent-hour, do first)

1. `gen-wire.ps1 -Check` and `bridge-contract/gen.py --check` against `56354dd` in a scratch checkout: expect only the `ProblemCode` / 409 description diff.
2. Re-run `platform-contract` conformance against rows produced by `support-platform` at `eeb73a8` seeded (SQLite, `CC_SEED_DEMO_DATA=true`): expect the enum failures of the table in 1.4.
3. Diff `backend/openapi.json` (platform) against what `platform-sim` mimics.

---

## Part 2. Integration plan: seams, port by port

Format per seam: **exists** (our side), **mock** (what we fake today), **real now** (usable at the pinned versions), **ask** (to forward, one sentence with why), **risk if they change**, **contract test**.

### 2.A agent-core (seam = our `core-bridge` runtime composing the pinned package, plus its public HTTP)

**A1. Invoke a stage (scout, verifier, builder, writer) through Core.** Exists: `/internal/v1` invoke, receipts CAS, `agent-core-assets/worlds/pulso-evolution`, reconcile. Mock: model answers (roleplay shim / scripted gateway). Real now: yes, real Core image, 44 live e2e tests per plan; the stage agents run in `task` mode and need no Jev. Ask: none beyond A8. Risk: pin bump moves import symbols (closed pin-symbol list fails closed, which is the intent). Test: `bridge-contract` conformance with `CONTRACT_TARGET=real` + `core-bridge` `modules-scan`.

**A2. Registry proposal lifecycle (create, draft, validate, freeze, evaluate, approve, publish, alias read).** Exists: bridge routes and BK0 matrix; real Core for `prompt` replace + `eval_suite` add, all four verbs. Mock: human issuer simulated; kinds other than the two are `denied(kind_not_supported)` by our compile step. Real now: the whole lifecycle on our seeded world; on the **platform's artifacts** only `validate` (dry-run is kind-generic) and drafts; `evaluate` needs an `eval_suite` and, for conversational agents, a Jev provider. Ask (A-3): confirm that an engine-authored `eval_suite` for `disputas`/`recepcion` is acceptable and who owns suite content, since the platform builder cannot go past `candidate` without one. Risk: registry rule change (quota, protected policies `403 registry_forbidden`, `release_settings` needs `admin`). Test: `contracts/artifact-kinds` digest + matrix evidence pointers; `bridge-contract` golden flows.

**A3. Evaluation arms.** Exists: native evaluate, admissions, arms, `PULSO_EVAL_BUDGETS`. Mock: scripted gateway outputs; our own GSIpy judge stand-in. Real now: attention-task world (task mode, no Jev). For platform agents: blocked on Jev (A8) or a `recorded` decision provider. Ask: A-9. Risk: eval quota 20 per proposal, 10 proposals per 24 h throttles live demos (budget 3-4 live runs a day). Test: `core-evaluation-admission-arms` flows tests.

**A4. Identity and approval authority.** Exists: bridge signers (`bridge-identity`, `bridge-staff`, ...), sandbox human issuer, durable single-use approval intention. Mock: the human. Real now: **the platform already implements the real human step-up** (S16: fresh TOTP per decision, platform signs the staff credential). Ask (A-4 and P-4): one registry, our service identity with roles `constructor` + `exporter` and never `aprobador`; humans approve through the platform's builder API. Risk: two issuers (platform keys and ours) must both be trusted by the same `--staff-keys`; a key rotation by one breaks the other. Test: bridge credential tests + a conformance case that our service identity gets `403` on approve.

**A5. Target catalogue (what we propose changes to).** Exists: seeded `attention-task` world only (`target_world = seeded`). Real now: `registry-e2e` fixtures define the platform's real artifacts: agents `recepcion`, `disputas`, `consultas`, `copiloto-asesor`, `constructor-chat`, prompts `p/*`, templates `t/*`, release alias `prod`. Our read path: `GET /entities/{kind}/{id}`, `/versions/{kind}/{id}`, `/aliases/{agent}/{alias}`, `/releases/{rid}`. Ask (A-4): the registry URL/environment the platform really uses, and the alias convention (`staging`, `prod`). Risk: entity ids and versions are immutable by hash; a re-import (`-ResetDb`) changes ids. Test: target-catalogue read test pinned to the fixtures' digests (new, 3 h).

**A6. Release/observation events (EXT-2).** Exists: simulator events, `release-contract` schemas (`release.published`, `release.rolled_back` as `event_log` rows, identity only). Mock: platform-sim emits them. Real now: **agent-core already emits `release.published|promoted|revoked`, `run.closed`, `handoff.created|resolved`** (outbound contract v1; delivery via relay/SNS opt-in) and serves `/v1/export/registry-events` and `/v1/export/runs` with cursors. That is a better EXT-2 source than waiting for the platform event log. Ask (A-5): enable and document a delivery path for us (export API with `exporter` role, or relay to a topic we can read) and confirm `run.closed` carries `release_id` so effects attribute to a release. Risk: `ReleaseData` is deliberately thin (no actor, no reason); our observation needs the release id and proposal id only, which it has. Test: outbound `OutboundEvent.json` digest gate + replay of recorded export pages (new, 4 h).

**A7. Jev.** Exists: Python/Rust `JevDecisionPort` plans (M5a/M5b), shim serving `/v1/jev`. Mock: `llm_structured` stages. Real now: nothing on main. Ask (A-1): land PR #28 or say it is abandoned. Risk: if #28 lands as is, Core needs the gateway to hold the Jev key; our stage policy (`PULSO_LLM_STAGE_POLICY`) stays unchanged. Test: gateway conformance on `/v1/jev` + a `blocked(jev)` honesty test that flips to red when the capability appears.

**A8. Tool executor.** Exists: our `pulso/*` dispatcher and protected writer. Real now: kind `tool` stays `blocked(executor-registration)`; the platform wants `HttpToolExecutor` (ADR 0025 draft) so real tools may come from another service. Ask (A-7): timeline. Risk: our proposals touching `tool` stay `not_evaluable` until then. Test: BK0 matrix row `tool` stays `blocked` (digest).

**A9. Pin governance.** Exists: `PIN_SHA`, `DIGEST.json`, `assetcheck.py`, `gen.py --check`. Ask (A-2/A-8): permission and cadence to bump `c814c2b` -> `56354dd` (additive), and a changelog or manifest digest per bump (we saw 5 bumps in 21 h earlier; this time only 1 additive change in 25 h). Risk: enum extended without version bump (happened). Test: digest-keyed gate on `contracts/` as a whole, not on `VERSION`.

### 2.B support-platform (seam = source adapter, release exposure, approval surface, and the platform as consumer of our published aliases)

**P1. Read the product's data (signals).** Exists: `platform-exporter` (Python, allow-list, contract 1.1.0), Rust `sources` crate with `product-sqlite`, `product-postgres`, `dataset-pg` adapters, watermark store, `pulso monitor`. Mock: `platform-sim` generates a stream; E0 maps to platform tables. Real now: the platform at `eeb73a8` with `CC_SEED_DEMO_DATA=true` and a SQLite file (snapshot, read-only). It runs from `docker compose up` (api + web, no agent-core, no Postgres). Needs: contract refresh (1.4 table). Ask (P-1): publish `backend/openapi.json` as the contract of record, tag a commit we can pin, and say when `with_assistant`/`assistant` become stable. Risk: highest of all seams; enums are closed in our schemas and fail closed. Test: `platform-contract` conformance run against a seeded DB at the new SHA (new, 4 h) + schema fingerprint check in the adapter (exists in design, fails closed).

**P2. Event catalog and the AI events.** Real now: `case.assistant_started|released`, `assistant.*`, `copilot.*` exist in `event_log`. They are `unknown` to catalog 1.1.0 (quarantined). Our best signal families (handoff rate, assistant abandonment, step-up failures, copilot use, CSAT via `case.rated`) live there. Ask (P-1b): payload shapes per type (EXT-1) and confirmation that payloads carry ids/enums only, never free text. Risk: free text leakage into payload (G9). Test: payload-shape schemas per new type, `x-sensitive-text` scan (extend `platform-contract`).

**P3. Release/observation exposure (EXT-2).** Platform side: audit events `builder.proposal_published`, `builder.alias_promoted`, `builder.release_revoked` in `event_log` (ids/states only). Ours expects `release.published`/`release.rolled_back` rows with `release_id`, `agent_id`, `alias`. Mock: platform-sim. Ask (P-2): either add `release_id`/`agent_id`/`alias` to those three events (identity only), or confirm we should take release facts from agent-core (A6) and treat the platform's as corroboration. Recommendation: **use agent-core as the authoritative release source** and label the platform source `corroborating`. Risk: two sources disagree. Test: `release-contract` schemas run against both producers.

**P4. Platform as consumer of the alias.** The platform runs `recepcion@prod` (env `CC_ASSISTANT_AGENT`) and `constructor-chat@prod` (`CC_BUILDER_AGENT`); a promoted alias changes customer behaviour from the next run. Real now: set `CC_ASSISTANT_AGENT=recepcion@staging` in a demo stack to show a published candidate affecting a conversation. Ask (P-5): confirm staging vs prod alias convention and that pointing the demo platform to a staging alias is intended. Risk: an accidental promote to `prod`; keep `--promote` off. Test: our `publish` refuses non-staging target (exists in demo; add as bridge contract case).

**P5. Approval surface (human).** Exists: control-api approval with durable single-use intention; sandbox issuer. Real now (backend): platform `POST /builder/proposals/track` brings an agent-core proposal into the platform list; approve/publish/promote need `stepUpCode`. Slice-16 builds proposals "based on the agent's staging release". Recommended: engine creates the proposal in agent-core with `origin` set, tracks it in the platform, humans approve in Supervision (screens are frontend's, so API/Bruno until they exist). Ask (P-4). Risk: step-up TOTP for seeded accounts is a dev code; a real approver needs enrollment. Test: contract test over the builder API subset we call (new, 5 h).

**P6. Outcome metrics from the product.** CSAT (`cases.rating_score`, `case.rated`), SLA (`first_response_at`), escalation, `handoff_quality` (`useful|incomplete|unnecessary` sent at close to agent-core). Real now in SQLite. Not allow-listed in 1.1.0: rating columns need a contract revision. Ask: include in 1.2.0 allow-list. Risk: small samples; keep `weak`/`insufficient_history` honesty.

**P7. Identity linkage.** Platform `CUS-...` to dataset `customer_id` through `bank_customer_links`; `data-pipeline` `demo_links` produces the file. Our G4 (PSN- to CLI-). Real now: usable for the demo only if we never read raw ids; we only need counts. Ask: none for the demo; for production, the keyed non-reversible join. Test: loader refuses `pseudonym_map` (exists).

**P8. Simulator parity.** `platform-sim` must reproduce platform head enums. Test: run the same conformance suite on the sim and on the seeded platform (`known_different` table shrinks).

### 2.C llm-gateway (`63155b6`, unchanged)

| Seam | Exists | Mock | Real now | Ask | Risk | Test |
|---|---|---|---|---|---|---|
| G1 `/v1/generate` for Core stages | Core `HttpLLMGateway`, stage policy, profile `pulso-evolution-structured@1.0.0` alias `pulso-evolution-llm` | our roleplay shim behind `LLM_ENDPOINTS` | Go gateway built from source if a Go builder image exists (ASK-4) | G-1: tag a release and publish the image digest (0 tags, 0 releases) so we pull instead of build | alias/model/price mismatch rejected by stage policy | `bridge-contract` + M0RP JSON-step round trip |
| G2 `/v1/jev` | M5a/M5b ports | shim | merged in gateway (PR #2), needs `JEV_API_KEY`, unusable by Core until agent-core PR #28 | via A-1 | double hop of retries | gateway `/v1/jev` conformance |
| G3 per-consumer controls | `GATEWAY_CONSUMERS` bearer | none | no alias allowlist, rate limit, idempotency or cost log | G-2: per-consumer alias allowlist and a cost log (we own spend ceilings today) | runaway spend | `PULSO_LLM_SPEND_CEILING` + kill-file tests (exist) |
| G4 real model | none | roleplay | needs a capped key (ASK-9) | none for gateway | data class rules | TPS scanner (plan) |

---

## Part 3. Demo ladder

Principle: the "magic demo" must be shown at specific places with bank CSV/E0-derived data, using mocks, ports and simulations where the real thing is not there, and each rung removes one double and says so. All statements derive from `doubles[]` produced by the engine.

Hours are focused agent-hours (implement plus own tests plus first review), one cargo slot, one stack at a time (host 16 GB; plan section 6). Ranges are guesses at ~80% bands, not measurements.

| # | Name | Data | Ports (real / mock / simulated) | Exists today | Effort to show |
|---|---|---|---|---|---|
| L0 | DEMO-0 offline thread | E0-derived fixtures (generated sample), recorded | Rust engine run-once real-narrow (recompute, validation); Core `DoublePort` stand-in (offline); scout/opportunity scripted; gate GSIpy `stand-in`; issuer `simulated`; platform in-process `simulated`; model none | yes: `scripts/demo-magic.ps1`, `pulso demo`, console over SSE (`docs/reports/demo-magic`) | 2-3 h polish and rehearsal |
| L1 | Real-Core arms on E0 signal | E0 (local only, never to hosted models) through `pulso run/monitor` in dataset mode | Sensor `real-narrow` (Rust on E0); Core **real** pinned image, native evaluate real on `attention-task` world, `prompt` replace + `eval_suite`; models `agent_roleplay` (treated payloads) or scripted; issuer `simulated`; publish to staging alias real; alias read real | most: e2e-core THREAD01 steps 5, 6, 8, 9 real; `demo/run.ps1` real_local; roleplay lanes; `pulso monitor` (b1197d6) | 6-10 h to string monitor output into the Core stack and console with doubles printed |
| L2 | Propose against the platform's real artifacts | E0 signal + `registry-e2e` import (`disputas`, `recepcion` prompts/templates) | Proposal draft and **validate (dry-run) real** on real platform artifacts; evaluate `not_exercised(jev)` or `recorded`; gate stand-in with `quality_claims: forbidden`; issuer simulated; no publish (or publish to a sandbox registry only) | none yet; fixtures exist in agent-core `tests/fixtures/registry-e2e` | 8-14 h (import fixtures into our Core DB, target catalogue read, a prompt replace on a real prompt, diff view) |
| L3 | Live platform signals | Platform at `eeb73a8` seeded (SQLite snapshot), customer simulator, optional agent-core e2e stack with demo doubles for the assistant | Source adapter real-narrow on the product snapshot after the 1.2.0 contract refresh; assistant/copilot events become real signals (handoff rate, step-up, CSAT); Core real; release/observation `simulated`; approvals simulated | `pulso monitor` + `product-sqlite`; platform repo runs by compose; contract refresh is NOT done | 16-24 h (contract 1.2.0, catalog types, schema fingerprint, snapshot, console labels) |
| L4 | Approve in the platform's builder (real step-up) and observe via agent-core events | L3 plus a proposal tracked in the platform | Engine creates proposal in the shared registry (service identity `constructor`), tracks it in the platform, **human approves with TOTP step-up through the platform builder API**, publish to `staging`; observation from agent-core `release.*` + `run.closed` (export API) | none; backend pieces exist on both sides | 14-22 h (+ asks A-4, A-5, P-4, P-5) |
| L5 | Before/after with simulated customers | L4 plus N scripted customer conversations before and after | Platform assistant on `recepcion@staging` vs `@prod`; a model through the gateway (real capped key or roleplay) and Jev (key) for the e2e agents; measured effect from `handoff.*`, `run.closed`, CSAT | none | 24-40 h and needs ASK-9 (capped key), the Jev key and PR #28 or a direct Jev key; one 20-eval budget per proposal limits repetition |
| L6 | Same on the 3-host AWS staging | L5 data | Engine, Core, gateway, Postgres on AWS; images by digest from CodeBuild; platform stays local or on staging | infra in progress (3 hosts, CodeBuild) | 16-30 h after infra is up and images are pushed (no hosted CI; receipts local) |

### 3.1 What each rung shows in the debug-console and what it can honestly claim

| Rung | Audience sees | Honest claim | Cannot claim |
|---|---|---|---|
| L0 | Banner with every double; ten steps streaming; native gate; panels Investigation/Diff/Decision mostly empty (known gap) | The orchestration and honesty labelling work end to end and never promote a stand-in to `real` | Any detection quality, any real Core behaviour |
| L1 | Real Core receipts, evaluate admission, alias read; signals from E0 with support counts; `doubles[]` lists roleplay | A real Core validates and evaluates a candidate generated from a signal found by a real sensor on a generated sample | That the fix is good (`quality_claims: forbidden`); the finding is about the generator (`data_origin=generated_sample`) |
| L2 | Diff of a real platform prompt/template, dry-run validation verdict, evaluation `not_exercised(jev)` | The engine addresses the artifacts the platform actually runs, by registry ids | Evaluation result, publication |
| L3 | Platform events (handoff, CSAT, escalation) as signals with `n` and window, `insufficient_history` where applicable, quarantine counts | Real product telemetry (seeded and simulated customers) flows through our allow-listed adapter | Production data, causal anything |
| L4 | Proposal in both systems, human approval with real second factor, release event, observation window opened | Authority path is real: human step-up approves, engine publishes to staging, release seen through agent-core events | That the effect is attributable (window just opened) |
| L5 | Before/after metrics per release with intervals | Descriptive before/after on simulated customers with a labelled model | Causal attribution, real customer benefit |
| L6 | Same, with AWS target labels | The deployment shape works on staging | Production readiness |

### 3.2 Recommended order

1. **L0 rehearsal** (2-3 h): keeps something showable every day.
2. **L1** (6-10 h): the strongest honest "real Core" demo available now.
3. In parallel, the **contract refresh** (P1/P2, 6-8 h) because it gates L3 and protects every later rung; and the **pin bump check** (1.6, 1 h).
4. **L2** (8-14 h), then **L3** (16-24 h).
5. **L4** after the answers to A-4, A-5, P-4 arrive. **L5** only with ASK-9 and Jev. **L6** when infra is ready, in parallel as infra lands.

Total to L3: roughly 35-55 agent-hours, about 3-5 working days at LVL-A (3 implementers, one stack at a time). L4-L6 are weeks unless the asks come back fast.

### 3.3 Minimum demo for the next 48 hours

Target: three things, in this order, each with `doubles[]` printed first.

1. **L0 live** (`scripts/demo-magic.ps1`), 20 minutes of story, labelled stand-ins. 2-3 h.
2. **L1** with one E0-derived signal, a `prompt` replace + `eval_suite` against the real pinned Core image, evaluate, simulated approval, publish to staging, alias read, console showing the real receipts. 6-10 h. Fallback inside the rung: use the `demo/run.ps1` real_local path that already exists.
3. **L2-lite (read-only slice, 4-6 h):** import `registry-e2e` into the sandbox Core DB, read the target catalogue, show a proposed prompt change as a diff against `disputas` with real dry-run validation, `evaluate` explicitly `not_exercised(jev)`. This is what makes the audience see that the engine speaks to the platform's artifacts without pretending to evaluate them.
4. A slide (not a demo) with the platform's `with_assistant` finding and the contract refresh plan: it shows we are tracking the integration.

Realistic total 13-20 h of agent work. Do not promise L3 in 48 h: the contract refresh is a precondition and has not started.

### 3.4 Fallback if the real Core or platform integration is late

1. Show **L0 replay** plus the `recorded` rung (digest-keyed replay of the last good L1 run), clearly labelled `recorded`.
2. Platform side: `platform-sim` stream + Rust sensor over events (exists), labelled `product=simulated`; release/observation `simulated`.
3. Registry side: `platform-sim/registry_mock` for validate/evaluate shapes, labelled `stand-in`, with the divergence report (`mock-vs-contract.json`) on screen.
4. Say out loud which of the three real dependencies is missing (Core stack, platform contract refresh, Jev) using `blocked(dep)`.
5. Never let the console show `real` for anything the engine did not observe; the honesty tests are the guard.

### 3.5 Top 10 risks

1. **Platform contract drift** (`with_assistant`, `assistant`, new enums): rows fail closed, and the platform's AI telemetry is invisible until refreshed. Mitigate: contract 1.2.0 now; schema fingerprint check in the adapter.
2. **Unresolvable platform pin** (`a492bfa` rewritten away): our evidence and journals cite a dead SHA. Mitigate: re-stamp with `eeb73a8`; ask for tags.
3. **No `eval_suite` anywhere, plus Jev not on main:** platform agents cannot be evaluated or published; L2+ stays `not_exercised`. Mitigate: author our own suite on the seeded world; push A-1, A-3, A-9.
4. **Evaluation quotas** (10 proposals per 24 h, 20 evals per proposal) throttle rehearsals and live demos; plan 3-4 live runs a day and use `recorded`.
5. **Two issuers, one agent-core** (platform keys and ours): rotation or misconfiguration breaks one side silently (`credentials_invalid` for the wrong key set). Mitigate: single key-set owner and a conformance case per issuer.
6. **Accidental production effect:** the platform runs `@prod`; a promote or wrong alias changes customer-visible behaviour. Mitigate: staging-only refusal as a contract test.
7. **Single owner on both sides:** the same person drives agent-core and the platform integration, so changes arrive in bursts (10 PRs in 5 hours) with enum extensions and no version bump. Mitigate: digest-based gates, short pin-bump cadence, direct channel through the user.
8. **Data-class violation under demo pressure:** E0/CSV rows reaching a roleplay or hosted model. Mitigate: TPS scanner is a precondition for any L1 live run; local-only otherwise.
9. **Resource limits on one 16 GB host:** Core + gateway + Postgres + platform + agent-core e2e (Docker Desktop vs our Podman) cannot all run; two container runtimes on one machine. Mitigate: one stack at a time, `recorded` for the rest.
10. **Over-claiming:** E0 is generated and the generator encodes the mechanisms; platform data is seeded and simulated; production agent-core runs on demo doubles (`ALLOW_DEMO=1`). Mitigate: print `data_origin`, `doubles[]` and "quality_claims: forbidden" on every report; no causal wording.

### 3.5b What we did NOT verify

No test, build or AWS call was run. The platform's stated 4 case statuses vs head, the `channel` naming and the claim that our drift gates will fire come from reading code. The mapping `a492bfa` ~ `7d2ae3a` is an inference. The branch ancestry of PRs #23 and #24 was checked with a depth-limited fetch (a negative result is weaker than for PR #28, whose code is absent from main by grep).

---

## Part 4. Asks to forward (one sentence each, with why)

### agent-core team

- **A-1** Please merge PR #28 (Jev through the gateway) into main, or tell us it is abandoned, because it is merged only into a side branch and all conversational agents (and our Jev port) are blocked on it.
- **A-2** Please bump `contracts/VERSION` (or publish a manifest digest and changelog) on every contract change, because `idempotency_in_progress` was added to `ProblemCode` without a version change and our drift gate keys on versions.
- **A-3** Please tell us who owns `eval_suite` content for `recepcion`, `disputas`, `consultas` and whether an engine-authored suite is acceptable, because without a suite nothing goes past `candidate` and both teams are blocked.
- **A-4** Please tell us the registry/Core environment the platform runs against (URL, alias names, `staging` vs `prod`) and confirm our service identity may hold roles `constructor` and `exporter` (never `aprobador`) on that same registry, because proposals must target the platform's real artifacts.
- **A-5** Please document and enable a delivery path for `release.*` and `run.closed` (export API with `exporter` role or relay topic) and confirm `run.closed` carries `release_id`, because this is the real source for release/observation (our EXT-2) and the platform does not expose it.
- **A-6** Please state what a promoted alias does to in-flight sessions and whether `agent@alias` is cached, because our observation window has to start at the right run.
- **A-7** Please give a date for `HttpToolExecutor` (ADR 0025), the `grant_active` adapter and a real `AuthzPort`, because proposals for kind `tool` stay `not_evaluable` until then.
- **A-8** Please confirm we may bump our pin `c814c2b` -> `56354dd` and announce breaking changes to `contracts/registry/*`, `ProblemCode` and `OutboundEvent` a day ahead, because we have a closed pin-symbol list that fails on drift.
- **A-9** Please confirm evaluation arms can run with a recorded or scripted decision provider (calibration) for conversational agents, or share a Jev key budget, because we cannot evaluate `understand`-based agents otherwise.

### support-platform team

- **P-1** Please publish `backend/openapi.json` as the contract of record, tag a commit we can pin, and update `DATA_MODEL.md` (it still says "slices 0 to 12, people only"), because our 1.1.0 contract rejects `with_assistant`, author role `assistant`, new channels, priorities, turn kinds and assignment reasons, and the stamped SHA `a492bfa` no longer exists.
- **P-1b** Please give payload shapes (ids and enums only, no free text) for `assistant.*`, `copilot.*`, `case.assistant_*`, `case.rated`, `case.priority_changed`, because these are the signal families we need and they are quarantined as unknown today (EXT-1).
- **P-2** Please add `release_id`, `agent_id`, `alias` to `builder.proposal_published`, `builder.alias_promoted` and `builder.release_revoked` (identity only), or confirm we should use agent-core's events as the authority, because EXT-2 has no producer yet.
- **P-3** Please give dates for Postgres and migrations (S17) and, meanwhile, a read-only SQLite snapshot path or a read replica for us, because the platform is SQLite with no migrations and a model change means deleting the database.
- **P-4** Please confirm that proposals created by our engine (with `origin` set) can be tracked via `POST /builder/proposals/track` and approved by a human with step-up in your Supervision screens, because that is the authority path we want to show instead of a simulated approver.
- **P-5** Please tell us the staging vs prod alias convention and whether a demo platform may run `CC_ASSISTANT_AGENT=recepcion@staging`, because it is how a published candidate becomes visible without touching prod.
- **P-6** Please provide a deterministic scripted customer simulator run (seed, N conversations) and the `demo_links` file procedure, because L5 needs repeatable before/after traffic.

### llm-gateway owner

- **G-1** Please tag a release and publish the image digest, because there are 0 tags and 0 releases and we would otherwise build Go from source.
- **G-2** Please add per-consumer alias allowlist and a cost log, because spend control is only on our side today.

### From the user (not a team)

- Decide who forwards these (the agent-core and platform owner appears to be the same person), and re-confirm ASK-1/ASK-9 (treated payloads, capped key) because L5 depends on them.

---

## Appendix. Evidence index

- agent-core: `gh pr list -R pulso-factored/agent-core --state all` (32 PRs, 0 open); `git log c814c2b..origin/main` (6 commits); `contracts/openapi.json` diff (409 text only); `contracts/schemas/ProblemCode.json` (+`idempotency_in_progress`); `contracts/VERSION` 1.3.0; `git grep '/v1/jev'` empty on main, present on `feat/jev-via-gateway` `6c8aad8`; `docs/plan-e2e-produccion.md`, `docs/runbook-e2e.md`, `docs/informes/2026-10-02-solicitudes-n01-n11-decisiones.md`; `tests/fixtures/registry-e2e/*`.
- support-platform: `docs/platform/adr/0003-agent-core-integration.md`, `0004-tool-service.md`; `docs/platform/api/slice-14-assistant.md`, `slice-15-copilot.md`, `slice-16-agent-builder.md`; `ENGINEERING_BRIEF.md` slice table; `backend/src/cc_platform/domain/cases/values.py`, `.../sqlalchemy/tables.py`; `docker-compose.yml` (api + web only); `git cat-file -t a492bfa` fails.
- Our side: `platform-contract/README.md`, `platform_contract/model.py`, `release-contract/README.md`; `bridge-contract/README.md`; `agent-core-assets/README.md`; `contracts/artifact-kinds/README.md`; `docs/plan-real/r1-real-system-design.md`, `r1-gap-list.md`; `demo/README.md`; `docs/reports/demo-magic/README.md`; `core-bridge/README.md`; plan `PLAN_HACIA_SISTEMA_REAL_CLAUDE_2026-10-04.md` sections 1.1-1.3, 3.2-3.3, 14.
- Scratchpad clones: `.../scratchpad/{agent-core,support-platform,llmgw,data-lab,data-pipeline}`.
