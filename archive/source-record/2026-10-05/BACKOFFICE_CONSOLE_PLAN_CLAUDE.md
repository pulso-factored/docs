> **CORRECTION (2026-10-03, user):** `debug-console` is the internal backoffice of OUR detection and self-improvement system, to see what happens under the hood while the engine and the whole system run (as agreed with Codex when the spec was written, §25). It is NOT a product API/UI, not the bank system and not the tool for the product team's business operations. This plan over-reached: the "operator layer over `/api/v1/evolution`" as default landing, personas P2 (product owner) and P3 as product roles, and the framing "reference consumer of §20.1" are **withdrawn**. What stays valid: the adapter seam (section 5), the diagnostic screens over `/internal/v1/debug` (§25), source coverage/health views (§32), the authority rules, a11y/i18n, and phased packages restricted to those. The spec's current §25.1 (rewritten by the spec owner) already states the boundary: the platform's attention backoffice and any product UI/API are out of Pulso scope, and `debug-console/` is the internal operation/observability surface with the private debug API; `/api/v1/evolution` product routes are the platform's concern, not a console dependency. Where this document disagrees with this banner, the banner wins. The "ready to paste" §25.1 text in section 8 below is obsolete and must NOT be applied.

# Pulso engine backoffice: evolving the debug console into an operator front (Team Claude plan)

Status: PROPOSAL (planning document, no code changed). Owner: Team Claude (L7 console). Date: 2026-10-03.

> **IMPLEMENTATION STATUS (2026-10-04 01:20 UTC, verified with `gh api`; the proposal text below is unchanged).** Merged on improvement-engine `main`: Phase 0 seam (B0.1 equivalent) in **#85** (`a4ccb0a`): typed `DebugApi` port with `http`, `fixture` and `stand-in` providers selected by `public/config.json` (`dataProvider`, `apiBase`), hand-written zod DTOs for the section 25 debug routes, uniform `DebugApiError`/`Problem` parsing (including the 410 `recovery` body), SSE resume (`after_sequence`/`Last-Event-ID`, dedup by run+sequence, gap backfill, 410 recovery), commands enabled only from the server's `available_commands[]` (acks always `requested`), mode declaration next to the stand-in banner, run list migrated end to end; 199 vitest tests, contract suite 29/29. Also merged: the fixture-backed console (#74), demo narrative panels with alternatives, gate attempts, hypotheses and hook states (#77), and the Sources view (capability profile per source, detector eligibility, exporter counters, insight cards) from the platform package (#80), which covers the B4.2 "Sources" input but not its integration into an operator shell. **Not started:** B0.2/B0.3 (operator shell, provenance badge), all of Phases 1-2 (overview, opportunities, proposals, decision inbox, feedback), Phase 3 `gen:contract` and the `provider=real_local` flip, Phase 4 technical group, audit and the a11y/security pass. **Blocked on Codex:** B3.1/B3.3/B3.4/B3.6/B3.7 (the Rust control-api HTTP surface and `contracts/product/`); field names of several debug routes and the 410 body shape are provisional until it publishes them. Reminder from the correction above: this is the internal backoffice of the detection/self-improvement system, not a product UI. See `ESTADO_IMPLEMENTACION_CLAUDE_2026-10-03.md`.
Sources: spec V3 §7 F8, §20, §20.1, §20.2, §24.1, §25; plan V3 §7, §16.10-16.15, §17.3.7 (screens S1-S10, scenarios F01-F25), annex D; `docs/ANALISIS_PRODUCTO_DESIGN.md`, `ANALISIS_DESIGN_A/B/C.md`;
console at `worktrees/improvement-engine-claude-r/debug-console` (main as merged; read only); shared journal `pulso_implementation_shared-_bitacora.md`.
Convention: **[spec]** = defined in V3 spec; **[plan §16]** = Codex field-level proposal, not yet ACKed as final; **[proposal]** = invented here, not in spec or plan, needs agreement; **[console]** = exists in the console today.
Reality check (journal CX-0079/CX-0084/CX-0093): **the Rust `control-api` HTTP service does not exist yet**; every route below is "missing" on the Codex side. The console works today only against its own fixture server and the stand-in demo model.

---

## 1. Target and personas

**Target.** One web application, same repo and same SPA as `debug-console/`, with two layers over the same engine facts:
1. **Operator layer (new, default landing):** answers "what is the engine doing, what did it find, what does it propose, what is waiting for a human, what happened after" in product language, over `/api/v1/evolution` (§20.1).
2. **Technical diagnostic layer (existing, secondary):** run graph, timeline, model calls, queries, evals, memory diff, external commands over `/internal/v1/debug` (§25), reachable from any operator screen by a "technical detail" link and kept intact.

**Frontier (hard).** This is the backoffice of the *improvement engine*. It is NOT the bank attention UI: no customer chat, agent office, case queue, CRM, abono approval, agent editor, wizard (§7 F8, §20 last sentence, §24.1 first paragraph, plan §7). The platform may embed or re-render the same read models; the backoffice is the engine's own reference consumer (§20: "Monitor minimo de demo consume la misma API").

| Persona | Real job | Decisions they make in the UI | Scopes (§20.1) |
|---|---|---|---|
| P1 Operator (engine ops) | Keep runs flowing; read lag, quota, dead jobs, dependency health | Pause/resume/cancel run, retry job, request diagnostic bundle (all `debug_operator`, §25 commands) | `evolution:read`, `evolution:operate`, `evolution:debug` |
| P2 Product owner / analyst | Understand opportunities, value range, counter-evidence, alternatives incl. "do nothing"; follow proposals | Open/prioritise reading (no side effect), give expert feedback (support/challenge/knowledge/request_review) | `evolution:read`, `evolution:feedback` |
| P3 Release approver (human authority for Registry) | Respond to `DecisionRequest` for a specific candidate hash | approve / approve_with_loosening / reject / publish / promote / revoke, each a separate request (§20.1, §31.7.2) | `evolution:read`, `evolution:decision` + Registry grant |
| P4 Domain expert / evidence reviewer | Check mechanism, sources, coverage; run dev trials on a candidate | Feedback, dev trial and trial turns (never `final_locked`) | `evolution:read`, `evolution:feedback`, `evolution:trial` |
| P5 Engineer (existing debug_viewer) | Diagnose a stuck run without shell | Read-only technical panels; fork-replay if operator | `evolution:debug` (+ `operate`) |
| P6 Auditor (read only) | Verify who decided what, on which hash, with which receipt | None | `evolution:read` (+ `debug` for audit) |

Out of scope persona: customer, bank agent/supervisor, platform administrator. Identity/SSO/MFA are external (§20.1); the console builds no IdP.

## 2. Information architecture and navigation

Primary navigation (left rail; hash routes today, `react-router` per plan §17.3.7 when screens exceed 6). URL carries filters (§25 "URL compartible"). Each item lists the existing console feature it reuses and what is new.

| # | Section (route) | Purpose | Reuses [console] | New |
|---|---|---|---|---|
| 1 | **Overview** `#/` | Active research/iteration, lane queues, metrics with denominators, prioritised opportunities, dependency health, mode banner | `RunList`, `ModeBanner`, `Profile` | Operator overview page over `GET /overview`; metric tiles with `<Metric value reasonCode>` null rule; opportunity list; "waiting for you" strip |
| 2 | **Opportunities / finding dossier** `#/opportunities`, `#/opportunities/:id` | Problem, population/window, support vs counter-evidence, bridge linkage grade, hypotheses and discarded candidates, alternatives (do-nothing first), value range, assumptions | `Investigation` panel, `Alternatives` panel, `hypothesesOf` | List + dossier route (S3, plan §17.3.7); evidence drawer; feedback form (P2/P4) |
| 3 | **Proposals and tests** `#/proposals/:id` (tabs Change, Diff, Compare, Gates, Trials) | ChangeSpec, bundle diff with cascade/affected consumers, paired comparison, **two independent gates + combined decision**, readiness (compilation/policy/evaluation/improvement/authority/alias/activation/exposure), dev trials | `Gates` panel, `Diff` panel, `GateAttempt` history, `attemptOutcome` | Proposal route (S4/S5), comparison (5 dev examples, "not comparable" state), readiness stepper, Trial runner (P4) |
| 4 | **Decisions / approvals** `#/decisions`, `#/decisions/:id` | List of exceptions, not a wizard; per-operation request, status, deadline, evidence, step-up | `DecisionPanel`, step-up, CAS 409 handling, `commandTracker` | Decision inbox (S6), per-target card showing hash/base release, command status page, "approve is not publish" copy, four-eyes denial display |
| 5 | **Runs and activity** `#/runs`, `#/runs/:id`, `#/activity` | Feed of what the engine is doing and why; drill to graph/timeline | **Entire S2: graph, timeline, drawers, SSE client, reconnect, 410 banner** | `GET /activity` feed (product wording) on top; "technical detail" link into existing run view |
| 6 | **Sources and coverage** `#/sources` | Which sources/snapshots/contracts feed the engine, cutoff, completeness per table/partition, platform-observation coverage, `traces_unavailable` gaps | (claude-p worktree is adding a Sources view: **coordinate, do not duplicate**; this plan consumes its component) | Coverage-first layout; source_kind never summed; platform-observation detail (`/platform-observations/{id}`) |
| 7 | **Memory** `#/memory` | Mounted head, pages read, proposed/published diff, lint, CAS lost, revocations | `MemoryView` (S7) | Memory diff with typed fields (plan §16.10.4); revoked/tombstone states |
| 8 | **Capabilities** `#/capabilities` | What the engine can do vs `simulated/unsupported/dependency_blocked` (e.g. canary unsupported) | none | S10 over `GET /capabilities` |
| 9 | **Settings and audit** `#/admin` | Session/tenant (read-only), identity (simulated flag), mode/profile, retention info, access audit view | `ModeBanner`, session | **[proposal]** audit list (no audit read route in §20.1/§25; see WP-B9); no tenant selector (ADR 0005 forbids), no editing of policy |
| 10 | **Technical** `#/tech/...` | The existing debug panels, grouped | Model calls, queries, evals, external commands, health/dependencies, diagnostic bundles, fork-replay, compare runs (S8) | Mostly relocation; S8/S9 as planned |

Design rules that stay: no wizard; every list is cursor-paged (max 100); loading/empty/error/gap states per list; empty is never "all resolved"; unknown is `null+reason`, never 0; `GET` never triggers work; closing a panel is local UI state (§20.1 DecisionRequest).
Design source mapping (ANALISIS_PRODUCTO_DESIGN, tableros Panorama, Tema abierto, Propuesta, Prueba, Activacion, Agentes, Ficha) is a **layout/content reference only**; illustrative numbers (88%/120, 10/50/100 selector) are not data: exposure only from a receipt (§20.1 readiness), no selector (design Activacion `pick` is cosmetic).

## 3. Roles and permissions model (three authorities)

Principles (§24.1, §20.1, §20.2):
1. **The UI never derives authority from a role label.** Every control is enabled only if the server-sent `available_commands[]` for that object contains it AND the session scope is present; the server remains the enforcer (403 does not leak existence, 404 uniform).
2. **Three authorities are separate and the backoffice only touches (c):** (a) financial approval of a case action (bank/sandbox) and (b) permission/policy change (platform governance) are **never** actionable here; they appear only as refs/states (`dependency_authorization` decision = `provide_feedback|decline` only, §20.1). (c) Approval/publication of a candidate is **Registry authority**: the console only collects an *intent* via `POST /decisions/{id}/responses`; the worker obtains the human JWS through `HumanAuthorizationPort` (§20.2); the browser never sees a JWS/JWT. UI role, badge, or "approver" claim in the session does not grant (c).
3. `approve`, `publish`, `promote`, `revoke` are four separate decisions with distinct targets (§20.2 target discriminated); the UI never offers a combined "approve and publish".
4. Author/approver separation (G1) is enforced server-side; the UI shows "denied: same actor" from the Problem body and does not offer role switching. A local role selector exists only in the fixture/local-identity profile and is labelled `auth.simulated=true`.
5. `debug_operator` does not inherit approver (§25). Bots have no approve control (plan T-E).
6. Revocation and step-up: expired session -> banner, no retry loop; step-up is a challenge ref + command status poll (`waiting_human_reauthentication`), modal close never approves (plan §16.13.6).

Role -> scope -> screen matrix (UI gating; server authoritative):

| Capability | Overview/Opp/Proposal read | Feedback | Trial | Decision respond | Run commands | Debug read | Export bundle |
|---|---|---|---|---|---|---|---|
| Scope | `evolution:read` | `evolution:feedback` | `evolution:trial` | `evolution:decision` | `evolution:operate` | `evolution:debug` | `evolution:operate` + purpose |
| P1 Operator | yes | no | no | no | yes | yes | yes |
| P2 Product | yes | yes | no | no | no | no | no |
| P3 Approver | yes | no | no | yes (+Registry grant) | no | no | no |
| P4 Expert | yes | yes | yes | no | no | no | no |
| P5 Engineer | yes | no | no | no | optional | yes | optional |
| P6 Auditor | yes | no | no | no | no | optional | no |

Role-to-scope mapping is versioned server-side (§20.1); the console reads `scopes[]` and `roles[]` from `GET /api/v1/auth/session` [plan §16.13.6] for display only.

## 4. Per-screen data contract (1:1 with spec §20.1 / plan §16)

Legend for Codex status (journal 2026-10-03: no HTTP control-api): **ABSENT** = not implemented anywhere on main; **Console fixture** = served by `fixture-server/` today. Shapes are from plan §16.10/16.14 (Codex proposal, pending final ACK) unless marked.

All reads return `ReadEnvelope` [spec §20/§20.1] = `tenant_id, projection_revision, as_of, environment, source_kind, validation, status, blocking_reasons[], next_automatic_action, available_commands[]` + `schema_version, entity_ref, links, coverage`; collections `items,next_cursor` (max 100); unknown query = 400; errors `Problem` [spec §20] + `cursor_expired,not_found,csrf_failed,validation_error,artifact_too_large` [plan §16.10.1].

| Screen | Routes (base `/api/v1/evolution` unless noted) | DTO | Spec | Codex today | Console today |
|---|---|---|---|---|---|
| Overview | `GET /overview` | `OverviewProjection` (active_runs, lane_queues, metrics[MetricProjection], opportunities[OpportunitySummary], dependencies, `operational_summary`, `deployment_profile` §16.14.3) | §20.1 | ABSENT | partial: `/internal/v1/debug/runs` + `/profile` [console] |
| Overview (mode) | `GET /api/v1/auth/session` (+`deployment_profile` pre-auth), `GET /capabilities` | session projection; `CapabilityAvailability` | §20.1 (capabilities); session is plan §16.13.6 | ABSENT | `session`, `profile` [console, consumer_proposal] |
| Opportunities list | `GET /opportunities` | `Page<OpportunitySummary>` | §20.1 | ABSENT | none (list is runs) |
| Dossier | `GET /opportunities/{id}` | `OpportunityProjection` + `hypotheses[]`, `examined_candidates[]` (§16.14.5), bridge linkage `same_outcome_linked|mechanism_proxy|unlinked|not_evaluable`, alternatives incl. `do_nothing` | §20.1 | ABSENT | `investigation`, `alternatives` [console, consumer_proposal] |
| Feedback | `POST /opportunities/{id}/feedback` + `Idempotency-Key`, `expected_revision` = opportunity domain revision | `ExpertFeedbackRequest` (text is string, objects rejected 422) -> 202 `{command_ref,status_url,entity_ref}` | §20.1, §20.2 | ABSENT | none (deferred to L10 per plan) |
| Proposal | `GET /proposals/{id}`; `GET /proposals/{id}/diff` | `ProposalProjection`, `DiffProjection`, `change_spec`, `draft_plan` | §20.1; diff route [plan §16.14.4] | ABSENT | `diff` (lines) [console, consumer_proposal] |
| Comparison | `GET /proposals/{id}/comparison` | `ComparisonProjection` (dev examples only; `not_comparable` state) | §20.1 | ABSENT | none |
| Gates | `GET /candidates/{id}/evaluation` [plan §16.14.2] and `/internal/v1/debug/runs/{id}/evals` | `native_evaluation` + `ImprovementGate` + `combined_decision`; two cards, never one green | §25 evaluation panel, §20 row "Laboratorio" | ABSENT | `gates` [console, consumer_proposal] |
| Readiness | `GET /proposals/{id}/readiness` | `ReleaseReadiness` (compilation, policy, evaluation, improvement, authority, published_alias, activation_ack, exposure) | §20.1 | ABSENT | none |
| Trials | `POST /proposals/{id}/trials`, `GET /trials/{id}`, `POST /trials/{id}/turns` | `TrialRequest` (expected_revision = candidate_revision), `TrialProjection` | §20.1, §20.2 | ABSENT | none (L10) |
| Decisions | `GET /decisions`, `GET /decisions/{id}`, `POST /decisions/{id}/responses` | `DecisionProjection`, `DecisionResponseRequest`; target discriminated proposal/release | §20.1, §20.2 | ABSENT | `decision`, `respond` hard-coded `dec-1` [console] |
| Command status | `GET /commands/{kind}/{id}` | `CommandStatus` (+`waiting_human_reauthentication` substatus, `authorization_challenge`) | §20.1, §20.2 | ABSENT | `command` [console] |
| Step-up | `POST /api/v1/auth/step-up` | challenge_ref + command_ref -> 202 | plan §16.13.6 (not in spec) | ABSENT | `stepUp` [console] |
| Activity feed | `GET /runs/{id}/activity`, `GET /activity` | `Page<ActivityRow>` + `next_after_sequence` | §20.1 | ABSENT | events [console, debug path] |
| Stream | `GET /internal/v1/debug/runs/{id}/stream?after_sequence` (+`Last-Event-ID`) | SSE `id=sequence, event=run_event, data={event_id,run_id,sequence,entity_ref,projection_revision,kind}`, `410 cursor_expired` with `recovery{after_sequence,snapshot_url}` | §25, §20, plan §16.15 Q2/Q3 | ABSENT | `streamEvents` implements it vs fixture |
| Runs/graph/events | `/internal/v1/debug/runs`, `/runs/{id}/graph`, `/runs/{id}/events` | `RunRow`, `GraphNode(node_kind job|material_step)`, events | §25, plan §16.10.4/16.14.1 | ABSENT (only `run_timeline_v2.rs` internal projection) | yes [console] |
| Technical panels | debug `/runs/{id}/model-calls`, `/queries`, `/evals`, `/memory-diff`, `/external-commands`, `/artifacts/{ref}`, `/health/dependencies`; `POST /runs/{id}/diagnostic-bundles`, `GET /diagnostic-bundles/{id}`; `POST /runs/{id}/pause|resume|cancel`, `POST /jobs/{id}/retry`, `POST /runs/{id}/fork-replay` | per plan §16.10.4 | §25 | ABSENT | none of these (only graph/events/investigation/gates/diff/memory proposals) |
| Platform observation | `GET /platform-observations/{id}` | `PlatformObservationProjection` | plan §16.10.2 (not spec §20.1) | ABSENT | none |
| Sources and coverage | **No dedicated route in spec.** Use `coverage` in every envelope + `/overview.dependencies` + `/platform-observations/{id}` | n/a | §20.1 envelope `coverage`; §24.2 | ABSENT | claude-p worktree (separate) |
| Memory | debug `/runs/{id}/memory-diff` (+ current `/memory` list is a consumer proposal, not in spec) | `MemoryDiff` | §21, §25 | ABSENT | `memory` [console, consumer_proposal] |
| Audit view | **[proposal]** `GET /api/v1/evolution/audit-events?cursor&from&to&actor&target` | `AuditEventProjection` (actor, scope/grant, reason, target ref, result, digest) | spec has `pulso_audit_events` (§25) but no read route | ABSENT | none |

### Exact asks for Codex (ordered by unblocking value)
- **A1 (contract package).** Publish `contracts/product/` (OpenAPI + JSON Schema + fixtures valid/invalid, N/N-1) for every DTO above, generated from Rust types with a drift gate (§20.1, §26). Mark each plan §16.14/16.15 shape final or amended. This is the prerequisite for generated TS types (§5).
- **A2 (skeleton).** `control-api` HTTP service with: `GET/POST /api/v1/auth/session`, `/logout`, `/step-up`; CSRF (`X-CSRF-Token`) and `__Host-` cookie; uniform `Problem`; `ReadEnvelope`; cursor paging; 404 uniform / 403 non-leaking; **per-object `available_commands[]`** computed from scopes+grants+state; scopes `evolution:*` mapping (§20.1). Local-identity issuer integration (CL-0022) for dev.
- **A3 (first read slice).** `GET /overview`, `GET /opportunities`, `GET /opportunities/{id}`, `GET /activity`, `GET /runs/{id}/activity`, debug `/runs`, `/graph`, `/events`, and SSE `/stream` with `after_sequence`/`Last-Event-ID`, `ping` 15 s, `410 cursor_expired` + `recovery.snapshot_url` (plan §16.15 Q2/Q3). All read-only, no side effects.
- **A4 (decisions).** `GET /decisions`, `GET /decisions/{id}`, `POST /decisions/{id}/responses`, `GET /commands/{kind}/{id}`, step-up through `HumanAuthorizationPort`, CAS on `domain_revision`, one-transition-under-concurrency test (§20.1 tests U21/U24), `waiting_human_reauthentication` substatus.
- **A5 (proposal/test slice).** `GET /proposals/{id}`, `/diff`, `/comparison`, `/readiness`, `GET /candidates/{id}/evaluation`, `GET /capabilities`, then `POST /proposals/{id}/trials`, `GET /trials/{id}`, `POST /trials/{id}/turns`, `POST /opportunities/{id}/feedback`.
- **A6 (answer, not build).** Confirm the three **[proposal]** items: (i) audit read route, (ii) a sources/coverage projection (or confirm that `coverage` + `/overview.dependencies` suffices), (iii) a typed `GET /memory` list for the memory index (today a console consumer proposal).
- **A7 (technical layer).** Remaining debug routes in §25 (model-calls, queries, evals, memory-diff, external-commands, artifacts, health, diagnostic bundles, run/job commands, fork-replay) in the order Claude's screens land (see §6).

## 5. Adapter seam: swapping the demo model for a typed API client

Today: `src/api/client.ts` is already a single fetch layer with zod parsing, CSRF, Problem mapping, SSE reader, and `public/config.json {provider}`; screens call `api.*` and `demoModel.ts` derives view data from the fixture-served consumer-proposal schemas. Risk: `demoModel` mixes view-model derivation with fixture-shaped data (`hypothesesOf` regex-parses summaries; `respond` hard-codes `dec-1`; `COMPETING` regex).

Seam design (no screen rewrite):
1. **Ports per feature, DTO-shaped.** `src/api/ports.ts` defines `OverviewPort, OpportunityPort, ProposalPort, DecisionPort, ActivityPort, DebugPort, SessionPort, StreamPort` returning *contract DTO types* (not UI shapes). Screens depend only on ports via hooks (`useOverview()` etc.).
2. **Three adapters, one interface:** `HttpAdapter` (typed client over `/api/v1/evolution` and `/internal/v1/debug`), `FixtureAdapter` (same HTTP to `fixture-server`, as today), `StandInAdapter` (in-process, used when no server; produces the same DTOs from `fixtures/demo-world.json`). `config.json.provider` selects `fixture|standin|real_local`; **adapters are chosen once at boot; no per-route silent fallback**. A mixed mode (some panels real, others stand-in) is allowed only if each panel renders a provenance badge (`real`/`stand-in`), enforced by a component test; `ModeBanner` rule stays (client says real but server declares doubles -> red).
3. **View-model mappers are pure functions** `dto -> view` in `src/features/*/model.ts` (move `demoModel.ts` logic here, gated by DTO fields such as `hypotheses[]` and `combined_decision`; the regex derivation stays only in `StandInAdapter` as a documented compatibility shim and is deleted when A1 lands).
4. **Types from the contract.** Until A1: hand-written zod (current rule, plan §17.3.7). After A1: generate TS types and zod from `contracts/product/` (JSON Schema/OpenAPI) in a `npm run gen:contract` step; runtime validation stays zod (tolerant on enums: unknown value -> "unrecognised: code" + structured warning). A drift test fails if `schemas.ts` diverges from the generated set; every `consumer_proposal` marker is removed only when its CLQ is closed. New dependencies (generator) need an ADR (plan §17.3.7).
5. **Error envelope.** One `ApiError` carrying `Problem{code,message,correlation_id,retryable,current_ref?,blocking_refs?,recovery?,field_errors?}`; map `409 stale_revision` to "reload head" UX with a **new** Idempotency-Key; `422` shows field errors without echoing values; `429` shows retry-after; `503` marks the panel degraded, never shows a last invented state (§25).
6. **SSE.** Keep the own fetch-reader (native `EventSource` hides status). Contract: `id=sequence`; resume by `Last-Event-ID` header (wins) or `after_sequence`; dedupe `(run,sequence)`; lower `projection_revision` dropped; gap -> `GET /events?after_sequence`; `410` -> use `recovery.snapshot_url`, replace the projection, set floor = `recovery.after_sequence`, show "earlier history purged", no invented events; second consecutive 410 backs off; silence != completion (stale after 2x heartbeat); `event: close` / `session_revoked` -> terminal, 401 on reconnect. Already implemented against the fixture; real-server conformance is WP-B5.
7. **Auth.** Browser holds only an HttpOnly session cookie + in-memory CSRF token (never in storage/URL). Login: in the local profile `POST /api/v1/auth/session {test_identity_id}` with the server-side local-identity issuer assertion (Ed25519, `auth.simulated=true`, plan §16.13.6/CL-0022); non-local profile = redirect to configured IdP flow (external; no console-built login). Step-up through `/api/v1/auth/step-up` bound to `challenge_ref + command_ref`.
8. **Keeping stand-in mode.** The stand-in stays as a first-class, labelled provider for demos before control-api exists and for offline UX work (journal: Claude's stand-in path). Rules: banner "DEMO with simulated engine" permanent; stand-in data carries `source_kind=assumption|sandbox_evaluated` honesty; the same contract tests run against `fixture`, `standin` and `real` (`CONTRACT_TARGET`), so promotion to real is a config change, not a rewrite (plan §7: "Cambiar proveedor fixture->real implica configuracion").

## 6. Phased work packages

Sized small (about 0.5-2 working days of an agent each). "First RED" is the first failing test to write. P = can run in parallel with its siblings.

| WP | Owner | Deliverable | Depends on | First RED | Par |
|---|---|---|---|---|---|
| **Phase 0 - seam and shell (Claude only, no Codex dependency)** | | | | | |
| B0.1 | Claude | `ports.ts` + `HttpAdapter/FixtureAdapter/StandInAdapter` skeleton; move calls behind ports; behaviour unchanged | none | component test: `App` renders with a stub port set and never imports `fetch` directly | no |
| B0.2 | Claude | Operator shell: nav rail, route table, "technical detail" link, i18n keys es/en structure, role-gating helper `can(cmd, obj)` from `available_commands[]` | B0.1 | unit: control disabled when command absent even if role label says approver | P with B0.3 |
| B0.3 | Claude | Provenance badge + mixed-mode rule; extend `ModeBanner` tests | B0.1 | component: panel from standin adapter without badge fails | P |
| **Phase 1 - read-only operator screens on fixtures** | | | | | |
| B1.1 | Claude | Overview screen (metrics null rule, lanes, opportunities, waiting-for-you) + fixture `GET /overview` per §16.10.2 | B0.2 | contract: unknown metric renders "unknown · source_unavailable", never 0 | P |
| B1.2 | Claude | Opportunities list + dossier (reuse Investigation/Alternatives), counter-evidence, bridge grade, do-nothing | B0.2 | component: `mechanism_proxy` never labelled as proven saving (§20 row 2) | P |
| B1.3 | Claude | Proposals: change, typed diff, affected consumers, closure incomplete banner | B0.2 | unit: incomplete closure cannot render "safe change" | P |
| B1.4 | Claude | Comparison + two-gate cards + readiness stepper; `not_comparable` blocks lift | B1.3 | component: native pass + improvement unknown => "blocked", no green | no |
| B1.5 | Claude | Activity feed `GET /activity` over existing SSE/timeline; link to graph | B0.2 | e2e: >=50 events keep focus/scroll (existing T-A01) | P |
| **Phase 2 - decisions and commands (fixtures)** | | | | | |
| B2.1 | Claude | Decision inbox + per-operation card, remove hard-coded `dec-1`, `approve` != `publish` copy | B1.4 | e2e: no combined approve+publish control exists | no |
| B2.2 | Claude | Command tracker + step-up UI against `waiting_human_reauthentication` | B2.1 | component: closing modal never calls respond; status poll after timeout, no blind resubmit | P with B2.3 |
| B2.3 | Claude | Feedback form (P2/P4): string-only notes, 422 on object, escaped text | B1.2 | unit: object note rejected before send; `<script>` rendered as text | P |
| **Phase 3 - contract and Codex** | | | | | |
| B3.1 | Codex | A1 `contracts/product/` + drift gate (§20.1) | none | contract test: Rust type change without schema regen fails CI | P |
| B3.2 | Claude | `gen:contract` (types+zod) + drift test vs `schemas.ts`; retire consumer_proposal markers as closed | B3.1 | drift: field added in schema, not in zod => red | no |
| B3.3 | Codex | A2 skeleton: session/CSRF/Problem/Envelope/paging/available_commands | none | cross-origin POST w/o CSRF => 403 | P |
| B3.4 | Codex | A3 read slice + SSE (U07) | B3.3 | SSE resume by `Last-Event-ID`; purged => 410 with recovery | no |
| B3.5 | Claude | Flip `provider=real_local`; run existing contract/e2e suites against real (`CONTRACT_TARGET=real`, `E2E_TARGET=real`); fix drift | B3.4, B3.2 | `test:contract` real: first failing response vs zod | no |
| B3.6 | Codex | A4 decisions/commands/step-up with `HumanAuthorizationPort` (U21) | B3.3 | two concurrent responses => one transition, one 409 | P with B3.4 |
| B3.7 | Codex | A5 proposal/test slice; A7 remaining debug routes incrementally | B3.3 | stale candidate => 409 with authorised head only | P |
| **Phase 4 - technical layer, sources, memory, polish** | | | | | |
| B4.1 | Claude | Technical group: model-calls, queries, evals, external-commands, health (S9), diagnostic bundle download link | B3.7 | component: GET never creates export; expired bundle => null link | P |
| B4.2 | Claude | Sources and coverage screen integration (merge claude-p Sources view into the shell) | claude-p merged | component: sampled source cannot render as complete coverage | P |
| B4.3 | Claude | Memory diff (typed), capabilities (S10), compare runs (S8), fork-replay | B3.7 | e2e: revoked memory shows tombstone, no stale page | P |
| B4.4 | Claude | Audit view (only if A6(i) accepted) | A6 | contract: audit row lacks PII/secret fields | no |
| B4.5 | Claude + independent reviewer | A11y/security/i18n pass (see §7); evidence manifest update | B4.1-4.3 | axe on all new screens; canaries absent from DOM/HAR/storage | no |

Critical path: B0.1 -> B1.x -> B2.x (all Claude, fixtures) while B3.1/B3.3 (Codex) start immediately; B3.5 is the join. Nothing in Phases 0-2 waits for Codex.

## 7. Non-functional requirements

**Accessibility (spec §25 acceptance, plan §17.3.7).** Keyboard-only for all actions; dialogs/drawers with accessible name, initial focus, Escape returns focus; one rate-limited `aria-live=polite` region; reconnect and progress never steal focus; graph/lists have text equivalents; no state conveyed by color alone; reduced-motion disables pulses. Reported as "no axe critical/serious on listed screens" + keyboard operable, never "WCAG compliant"; screen-reader review stays `not_run` until a human does it; reviewer is not the author.

**i18n es/en.** Today es-419 only (`src/i18n/es419.ts`, test rejects hard-coded JSX text). Plan: add `en.ts` with the same key set (parity test fails on a missing key), runtime locale from user preference/`navigator.language`, persisted only as a UI convenience (no domain data in browser storage). Machine codes (status, reason_code, command ids) stay verbatim in both languages; dates/numbers via `Intl`; documentation stays English. Spec language is Spanish; copy for decision options must use exact operation names (approve/publish/promote/revoke) to avoid implying authority.

**Security.** (1) The UI never touches broker, Core, PG or S3; only same-origin `control-api` through the container proxy (§25, plan §16.13.6). (2) No JWT/JWS/Core token in browser memory, URL, storage or logs; HttpOnly `__Host-` cookie; CSRF header on every mutation; origin check; mutation without CSRF is never sent (existing). (3) CSP without `unsafe-inline` (existing `nginx/security-headers.inc`; keep asserted by `csp.test.ts`); `Cache-Control: no-store` on sensitive responses; no `dangerouslySetInnerHTML`; all notes/summaries/artifact previews rendered as text (§20.2 XSS, `[object Object]`). (4) `clientScrubber` stays as defence in depth; canaries (`CANARY_FINAL/PII/SECRET`) tested in DOM, HAR, console, storage, cookies. (5) Trace links only to `traceLinkOrigins[]` with `rel="noopener noreferrer"`. (6) `final_locked` never rendered; comparison shows only authorised dev examples. (7) Deployment: internal only (ALB internal + VPN/SSM/identity proxy), no public demo route (§25); if product people need access it goes through the same identity proxy. (8) Stand-in must be impossible to mistake for real (banner + provenance badge).

**Performance.** List/timeline p95 <= 500 ms for 100 rows is a server budget (§8, §25), verifiable only at H4 against the real API; client side: cursor paging (max 100), lazy detail panels, virtualise timelines > 1,000 events (`@tanstack/react-virtual` per plan, needs ADR since not yet installed), `projection_revision` guard to avoid re-render storms, SSE wake-up + re-read (no per-event full reload when bursts: coalesce re-read at most once per animation frame / 250 ms), code-split technical layer. Load test: 100 runs x 1,000 events in the browser E2E (§25).

**Observability.** Console emits a structured client error stream (no payloads) only to the console log/`security.unredacted_payload` today; add a small `reportClientEvent(kind,code,count)` that posts to an engine endpoint only if Codex accepts one **[proposal]**; otherwise stays local. Correlate with `correlation_id` from Problem and `trace_id` links (degraded panel when null: `trace_unavailable`). Never log user input text.

## 8. Proposed ADDITIVE amendment (Spanish, ready to paste)

Rules followed: nothing in §25 is removed or weakened; every sentence of §25 stays in force; the new text adds a layer and states precedence in case of doubt.

### 8.1 Insertar al final de §25, como `### 25.1 Perfil backoffice de operador (aditivo)`

```markdown
### 25.1 Perfil backoffice de operador (aditivo)

Esta subsección **añade** un perfil a la consola de §25 y no modifica ni deroga ninguna de sus pantallas, rutas, comandos, controles de seguridad ni criterios de aceptación. `debug-console/` pasa a ser el **backoffice del motor de automejora** para operadores y personas de producto, con dos capas sobre los mismos hechos: (1) una **capa operativa** por defecto que muestra panorama, oportunidades y expediente, propuestas y pruebas, decisiones, actividad, fuentes y cobertura, memoria, capacidades y auditoría, consumiendo únicamente las rutas de producto de §20.1 bajo `/api/v1/evolution`; y (2) la **capa de diagnóstico técnico** de §25, que permanece íntegra como capa secundaria accesible desde cada pantalla operativa mediante un enlace explícito, y consume `/internal/v1/debug`.

**Frontera.** El backoffice es del motor, no de la atención bancaria: no implementa chat, oficina de agentes, cola de casos, CRM, aprobación financiera de casos ni administración de usuarios o permisos de la plataforma (§7 F8, §20, §24.1). La plataforma puede incrustar o reconstruir las mismas proyecciones; el backoffice es el consumidor de referencia de esos contratos.

**Autoridad.** La interfaz no deriva autoridad de una etiqueta de rol. Un control sólo se habilita si el servidor lo incluye en `available_commands[]` del objeto y la sesión tiene el scope correspondiente (`evolution:read|feedback|trial|decision|operate|debug`); el servidor sigue siendo quien autoriza. Las tres autoridades de §24.1 permanecen separadas: el backoffice **no** actúa sobre (a) aprobación financiera de un caso ni (b) cambios de permiso o policy de la plataforma, y sólo recoge la **intención** humana para (c) aprobación y publicación de candidato mediante `POST /decisions/{id}/responses`; la firma humana la obtiene el worker por `HumanAuthorizationPort` (§20.2) y el navegador nunca recibe JWT/JWS. `approve`, `publish`, `promote` y `revoke` son solicitudes distintas sobre un target concreto; no existe control combinado ni «aprobar y publicar». `debug_operator` no hereda `approver`; la separación autor/aprobador se aplica en servidor aunque la interfaz local ofrezca cambiar de identidad de prueba, y esa identidad se rotula `auth.simulated=true`.

**Veracidad y estados.** Todo valor ausente se muestra como `unknown` con su razón, nunca como cero; `mechanism_proxy` no se presenta como ahorro comprobado; las fuentes (`source_kind`) no se suman; el gate nativo de Core y el gate de mejora de Pulso se muestran como dos tarjetas independientes con la decisión combinada, nunca un único verde; la exposición sólo se muestra con recibo de plataforma; un 202 significa «solicitado» y la confirmación proviene de `GET /commands/{kind}/{id}`. Cerrar un panel es estado local de la interfaz y no responde ni vence una decisión.

**Modos y proveedor.** La interfaz declara siempre su modo (`provider`, `target`, `runtime_profile`, `doubles[]`) y distingue en cada panel si sus datos son reales o de un doble (stand-in) cuando coexistan. Cambiar de proveedor fixture/stand-in a API real es configuración, no reescritura; los mismos tests de contrato corren contra ambos.

**No regresión.** Se conservan sin cambios: la lectura por defecto sólo-lectura, el acceso exclusivo mediante el `control-api` (sin acceso directo a PG/S3/broker/Core), cursor `after_sequence` con `410 cursor_expired` y snapshot de recuperación, CSP, CSRF, redacción, la prohibición de ver `final_locked`, los comandos acotados de §25 con `expected_revision`, `Idempotency-Key` y auditoría, el despliegue sólo interno (ALB interno + VPN/SSM/identity proxy), las reglas de accesibilidad y el DoD de ingeniería. Ante duda, prevalece el texto de §25 y de §24.1.

**Idioma.** Textos de interfaz en es-419 y en; los códigos de máquina se muestran literales.

**Aceptación adicional.** (i) Recorrido operativo `panorama → oportunidad → propuesta → comparación → prueba dev → decisión` con estados activos, `unknown`, `unsupported` y `blocked` (alineado con U24, §20.1); (ii) prueba de que ningún control de decisión se habilita sin `available_commands[]` ni scope, y de que un bot no tiene control de aprobación; (iii) prueba de que con consola apagada el motor corre idéntico y de que un `GET` no crea eventos ni jobs; (iv) axe sin violaciones críticas/serias en las pantallas listadas, recorrido por teclado, y paridad de claves es/en; (v) la capa técnica de §25 mantiene su E2E.
```

### 8.2 Nota de una línea para §7 F8 (añadir al final del párrafo)

```markdown
**Nota (aditiva):** el motor incluye además un backoffice de operador de ingeniería (§25.1) que consume los mismos read models de §20.1 y es el consumidor de referencia de esos contratos; no sustituye la consola integral de la plataforma ni se presenta como UX del banco.
```

## 9. Open questions for the user (product decisions) with recommended default

| # | Question | Recommended default |
|---|---|---|
| Q1 | Who actually uses this: only the engine team, or also bank product people? | Both; product people get read + feedback; only a named approver group gets decisions. |
| Q2 | Standalone app or embedded into the platform? | Standalone (internal, behind identity proxy) as reference consumer; keep routes/components embeddable. Revisit at H4. |
| Q3 | Who may press approve/publish/promote/revoke, and is four-eyes mandatory outside local? | Separate groups for approve and publish; four-eyes mandatory when policy says so (§20.1, G1); revoke needs a distinct grant. |
| Q4 | Default landing for each persona: operator overview, or decisions inbox for approvers? | Overview for all; approvers see a "waiting for you" strip and a badge count. |
| Q5 | Is the dev trial (conversational sandbox) in the first backoffice release or deferred? | Deferred (L10); ship read-only comparison first. |
| Q6 | Expert feedback: free text only or structured (support/challenge/knowledge/request_review)? | Structured type + treated text, per §20.1; no attachments initially. |
| Q7 | Languages: es-419 and en at launch, or es first? | Both keysets from B0.2; copy reviewed in es first. |
| Q8 | Notifications (email/Slack) for pending decisions? | None in the engine (platform concern, §20.1 snooze is platform); in-app badge only. |
| Q9 | Audit view: needed in v1? Retention window visible? | Read-only audit list in Phase 4, only if Codex accepts the route (A6); show retention as informational. |
| Q10 | Exposure/rollout: show the 10/50/100 selector from the design? | No. Show exposure only from receipt; canary upstream is `unsupported` (§20.1 readiness). |
| Q11 | Single tenant UX or tenant switcher? | Tenant read-only from session (ADR 0005 forbids selector). |
| Q12 | Name: keep "debug console" or rename (e.g. "Pulso backoffice")? | Rename the product shell to "Pulso backoffice"; keep "Technical" as the debug layer name and the `debug-console/` directory for now (avoid churn in plan/CI references). |
| Q13 | Sources screen: single owner? | The claude-p Sources view merges into the backoffice shell; this plan only adds navigation and coverage rules. |
| Q14 | May we add dependencies (`react-router`, `@tanstack/react-query`, `react-virtual`, contract generator)? | Yes with one ADR; they are already approved in plan §17.3.7 except the generator. |

## 10. Risks and notes
- Biggest risk: Codex control-api is absent; Phases 0-2 are deliberately independent so Claude progress is not blocked, but the stand-in can drift from the final DTOs. Mitigation: B3.2 drift test and the single contract suite across providers.
- Many field shapes are Codex proposals (plan §16) awaiting Claude ACK/final freeze; keep `consumer_proposal` markers until closed.
- The spec lists 11 product projections plus session/auth routes that are only in plan §16.13.6; treat session routes as agreed-by-plan, not spec.
- No endpoint here is invented except those tagged **[proposal]**: audit-events read, typed memory list, client-event report, and the "sources and coverage" projection if `coverage` proves insufficient.
- Nothing here changes Core wire, Rust, CI, or the other worktree; the amendment text in §8 is not applied to the spec by this document.
