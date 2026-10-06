# MAGIC round 1C: SPA + platform surfaces for the improvement engine (2026-10-04)

Read-only survey. `SP` = `D:\.codex\factored\tmp\shared\support-platform` (fast-forwarded to main `5e105a7`, includes PR #12 copilot suggestions); `PC` = `...\improvement-engine-claude-cons\platform-contract` (catalog 1.2.0); `B` = `SP/backend/src/cc_platform`; `D` = `SP/docs/platform`. We build no screens; every "ask" goes to the platform team via the user.

## Headline findings

1. **The SPA has no screen for agents, proposals, copilot or builder.** Supervisor rail = Colas, Equipo, Escalados, Auditoria (`SP/frontend/src/app/roles.ts:111-130`); routes in `app/paths.ts:34-45`; `schema.gen.ts` has zero `builder`/`copilot` hits. Backend for slices 14/15/15b/16 is done "and no screen was touched" (`D/api/slice-16-agent-builder.md:3`). So a proposal from us has no human-facing page today; the platform frontend team must build "Supervision / Agentes" (spec: slice-16 §6).
2. **Every builder route needs a human staff session** (Supervision/Admin) + TOTP `stepUpCode` for approve/reject/publish/promote/revoke (`B/api/routers/builder.py:27,146,266,307`; slice-16 §3). Our engine cannot call them. The only service-token route is `/internal/grants/{ref}` (`B/api/routers/internal.py:19,29,40`, `CC_INTERNAL_SERVICE_TOKEN`), unset = 404.
3. **The proposal path already has an "automatic detection" slot**: `ProposalOrigin.AUTO_DETECT = "auto_detect"` (`B/application/ai/registry.py:28-32`; `builder_proposals.origin`, `D/DATA_MODEL.md:501`) and an index fed by `POST /builder/proposals/track` (`B/application/ai/builder.py:405-450`, emits `builder.proposal_tracked`, idempotent, needs only a proposal id the registry confirms). Nothing creates `auto_detect` proposals yet: that is our hook.
4. **The notification bell is a closed enum** (`B/domain/notifications/notification.py:38-57`; SPA drops unknown kinds, `features/notifications/model.ts:357`). A new kind needs a frontend template.
5. **Catalog gap**: `copilot.suggestion_{requested,ready,none,failed,decided}` are emitted and audited (`B/domain/ai/events.py:128-186`, `application/audit/catalog.py:69-73`) but are NOT in `PC/event-catalog.json` 1.2.0 (copilot has only `query_asked`/`answered`), so they would be quarantined as unknown. Also: catalog 1.2.0 lists 57 types, **53 admitted** + 4 denied (not 39); no `planned`.

## (1) Map of surfaces

| Surface | Exists today | Where a proposal could appear (evidence) | Minimal additive platform change (ask) | Effort |
|---|---|---|---|---|
| Supervision > Agentes (proposal list/detail, stepper, gate items, approve w/ TOTP, publish, alias diff) | Backend only; no route/screen | The natural home: `GET /builder/proposals` shows our `auto_detect` row once indexed (slice-16 §4, §6) | Frontend builds slice-16 §6 (run `pnpm gen:api`) | L (their) |
| Notification bell + toasts (supervisor role) | Yes, derived from events by `NotificationProjector` (`D/api/slice-10-notifications.md` §3) | "Nueva propuesta de mejora para disputas" | New kind `improvement_proposed` triggered by `builder.proposal_tracked` where origin=auto_detect (or `source=engine`); recipients = active Supervision; SPA template | S-M |
| Auditoria (`/supervision/audit`) | Yes; backend family `agents` exists | Row "Se siguio una propuesta" for `builder.proposal_tracked`; filter by case/actor/`q` | Add "Agentes" option to the family Select (slice-16 §9) | S |
| Rail indicator (badge) | Yes, keyed (`roles.ts:21-28`) | Count of proposals awaiting decision on an "Agentes" item | New `RailIndicatorKey` fed by `GET /builder/proposals?state=evaluated` | S |
| Builder chat "Constructor" (`POST /builder/chat/messages`) | Backend only | Supervisor asks "que mejorarias de disputas?"; the agent can name our proposal id, platform adopts any id the registry confirms (`source: chat`) | None for backend; agent-core's builder agent needs a tool/knowledge to read our findings | M (agent-core) |
| Escalados / supervisor case view / Equipo (`RecentRating`) | Yes | Evidence links: finding cites `CASE-...`; supervisor opens `/supervision/cases/:id` (read-only, records `case.viewed`) | Deep link only; none | none |
| Analyst Workspace "Copiloto" panel | Backend (15, 15b), no screen | Analysts never see engine output (and shouldn't: supervisors hold no customer data, analysts hold no builder) | none | n/a |
| Customer simulator | CSAT survey exists (`RatingSurvey`, `ConversationSurvey`) | "Que mejoramos por ti" is not feasible without a customer-facing page | out of scope | n/a |
| Internal API (`/internal/*`) | grants only | Service-token entry for the engine | `POST /internal/builder/proposals/announce {proposalId}` = `adopt(source=tracked)` without a human session, emits `builder.proposal_tracked` | S |

Chain we need end to end: engine -> registry proposal (`origin=auto_detect`, evidence in `docs.rationale/changelog`; needs agent-core to accept a service/engine principal for create+draft+validate+freeze+evaluate, ADR 0018) -> `announce` -> bell + Agentes list -> human approves with TOTP. The human gate stays exactly as designed (ADR 0003 §7).

## (2) Events/data that can trigger or feed detection

| Signal | In contract 1.2.0? | Where (table / event) | Notes |
|---|---|---|---|
| Customer CSAT 1-4 + comment | Yes `case.rated` (`score, comment, analyst_id`; `comment` free text) | `cases.rating_*`; `PC` catalog | Closest "thumbs"; comment text is free-text key |
| Escalation to supervision + motive | Yes `escalation.opened` (`motive` free text), `answered`, `taken`, `reassigned`, `withdrawn`, `closed`, `acknowledged` | `escalations` | Motive = labelled "agent/analyst could not solve" |
| AI -> human handoff | Yes `assistant.ended` (`result: resolved/escalated/ended/failed/released`, `handoff_ref`), `case.assistant_released` (`reason`, `handoff_ref`) | `assistant_sessions` (`state`, `failure_code`, `handoff_ref`) | `failed` and `released` (supervisor took over) = strong failure labels |
| Assistant turn outcome | Yes `assistant.turn_answered` (`agent` id@version, `run_id`, `trace_id`, `status`, `outcome`, `awaiting`) | event_log | `run_id`/`trace_id` join to agent-core lineage |
| Step-up rejected, input queued | Yes `assistant.step_up_rejected` (`attempts`), `input_queued` | event_log | friction signals |
| Copilot draft decision: used / edited / discarded / ignored + `edit_distance_permille`; escalation recommendation accepted | **No** (emitted, not catalogued): `copilot.suggestion_decided` (`subject`, `decision`, `edit_distance_permille`); `suggestion_ready` (`kinds`, `run_id`, `trace_id`), `none`, `failed` (`failure_code`) | `copilot_suggestions` (`reply_decision`, `edit_distance_permille`, `reply_hash`, `escalation_accepted`; texts purged at 24h, `D/DATA_MODEL.md:495`) | Biggest free label set; ask Product to admit in 1.3.0 |
| Analyst sent text | Yes `turn.created` (`text` free text, author role, audience) | `turns` | The "edited" ground truth; no `from_suggestion_id` (DATA_MODEL:617) so joining to a suggestion is by case+time |
| Copilot Q&A (what analysts ask) | Only sizes: `copilot.query_asked` (`question_length`), `answered` | `copilot_threads.messages` text (not exported) | Question text stays in the platform DB |
| Handoff quality label (`useful/incomplete/unnecessary`) | **No**: sent to agent-core, not stored in event_log (`B/application/cases/commands.py:158-175`) | agent-core | Ask agent-core export, or platform event |
| Close reason / priority change / SLA | Yes `case.closed` (`close_reason`, `note`), `case.priority_changed`, `case.first_responded`, notification `sla_at_risk` (derived) | `cases` | repeat contact via `previous_case_id` (no event) |
| Retries / failures | Partial: `copilot.suggestion_failed` (not catalogued), `assistant.ended result=failed`; no tool-call events (DATA_MODEL:623) | | tool_call/routing_step "do not exist" |
| Calls | Yes `call.*` (`hold_seconds`, `end_reason`, `duration_seconds`) | `calls` | secondary |
| Builder lifecycle | Yes all 15 `builder.*` (`proposal_evaluated` has `verdict`, `items_failed`; `proposal_published`, `alias_promoted` with `before`) | event_log family `agents` | decision trail for our own proposals |

## (3) Did a released change work? What the platform records after release

- Release markers: `builder.proposal_published` (`release_id`), `builder.alias_promoted` (`alias`, `release_id`, `before`), `builder.release_revoked`; each carries actor + `step_up` (`PC` catalog).
- Outcome metrics already in events, sliceable by time/agent: resolved-without-handoff rate (`assistant.ended`), `failed`/`released` rate, step-up rejections, `case.rated.score`, `escalation.opened` rate, `case.closed.close_reason`, copilot draft used/edited/discarded and median edit distance.
- Attribution: `assistant_sessions.agent` is `id@version`, `AgentRun.release` exists in the runtime result (`B/application/ai/runtime.py:93-112`, `SessionLineageRun.release`) but **events do not carry release**, only `agent`, `run_id`, `trace_id`. Ask: add `release` (and `agent_version`) to `assistant.turn_answered`, `copilot.suggestion_ready`, `copilot.answered`; otherwise before/after is by timestamp around `alias_promoted`, polluted by prod/staging mixing.
- Caveat: no A/B; `staging` vs `prod` aliases give a natural canary only if staging traffic exists (simulator).

## (4) Magic ideas, ranked (magic value / effort)

| # | Idea | Evidence | Ask | Eff. | Who |
|---|---|---|---|---|---|
| 1 | **Proposal lands in the supervisor's bell and Agentes list, with the evidence cases linked** ("12 disputes escalated for the same missing step; proposed fix evaluated: pass") | `auto_detect` origin; `track` idempotent (builder.py:405); bell projector (slice-10 §3) | `POST /internal/builder/proposals/announce`; kind `improvement_proposed`; Agentes screen | S+M | platform team |
| 2 | **Advisor corrections of copilot drafts = free labelled dataset** (draft hash, decision, edit distance, sent text) for prompt/policy proposals | `reply_decision`, `edit_distance_permille` persisted (DATA_MODEL:495); `turn.created.text` in catalog | Admit `copilot.suggestion_*` in 1.3.0; add `turn_id` to `decided`; drafts live only 24h: capture draft from agent-core run output by `run_id` | S | Product/platform via user; us for mining |
| 3 | **"Impact after release" card** on the proposal (resolved rate, CSAT, escalations before/after, with n) | release events + outcome events above | `release` in event payloads | M | us (compute) + platform (card) |
| 4 | **Supervisor weekly digest** ("3 findings, 1 proposal awaiting approval, last release +4 pts CSAT") | no digest/email exists besides onboarding mails (`/email` port, dev mailbox only) | a notification kind `weekly_digest` (bell is simplest), or builder-chat message | M | platform + us |
| 5 | **Ask the builder chat about a finding** (supervisor types "why?"; Constructor cites our evidence) | chat adopts ids the registry confirms (slice-16 §4) | agent-core: tool to read engine findings | M | agent-core via user |
| 6 | **Escalation motive clustering** ("Escalados": recurring motives become one proposal) | `escalation.opened.motive` free text admitted | none | S | us |
| 7 | **Handoff-quality loop** (`incomplete`/`unnecessary` labels reveal bad escalations) | labels sent to agent-core (commands.py:158) | agent-core exports them, or platform emits an event | S-M | agent-core/platform via user |
| 8 | **Safe-by-design "gate card"**: show eval gate items per proposal (never a composite) with our rationale beside | `ApprovalReview.gate` (registry.py:168) | Agentes screen "Evaluacion" tab | S (given #1) | platform |
| 9 | **Canary verdict on staging before prod** ("staging release looked better on 40 simulated cases") | `alias_promoted.before`, staging default on publish | simulator traffic labelled by alias | L | Codex independent + platform |
| 10 | **Rail badge "Agentes (2)"** for proposals evaluated and awaiting a decision | rail indicator keys (roles.ts:21) | `RailIndicatorKey` | S | platform |

Blockers worth stating: no demo agent has an `eval_suite`, so nothing passes `candidate` yet (slice-16 §8; ADR 0003 §7); agent-core has no list-proposals call (the platform index is the only list); copilot suggestions agent unset and "never run" until agent-core ADR 0026 (slice-15b status); production hardening (Postgres, real auth) is slice 17.
