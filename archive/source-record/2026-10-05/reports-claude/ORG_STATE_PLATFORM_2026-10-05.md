# support-platform: state on main, 2026-10-05

Source: `origin/main` @ 5261ecf (2026-10-05 09:52 -05, "Sync builder proposals with agent-core's list ... (#28)"), read via `git show origin/main:<path>` in D:\.codex\factored\tmp\shared\support-platform after `git fetch`. Nothing was run (no tests, no servers); everything below is from code and docs unless marked UNVERIFIED. `gh pr list` returned no open PRs. The local checkout there was 25 commits behind; no branch was changed.

## 1. What exists

Product: LATAM Bank transaction-dispute contact center (hackathon). Backend: Python 3.12 / FastAPI, hexagonal, SQLite, event log, WebSocket realtime. Frontend: React 19 + Vite SPA, es and pt-BR. Paths are English (`/analyst`, `/customer`); RUNBOOK/README still mention old Spanish paths (`/analista`, `/cliente`).

### SPA routes (frontend/src/app/paths.ts, router.tsx)
| Route | Role | What it does |
|---|---|---|
| `/login`, `/login/verify`, `/login/locked` | public | email+password, 6-digit TOTP step, locked-account screen |
| `/activate?token=`, `/reset-password?token=` | public | invitation activation (password policy + TOTP QR enrolment), admin-issued reset |
| `/dev/mailbox` | public, dev only | emails the platform "sends" (invitation/reset links) |
| `/customer` | none (simulator) | pick demo customer; chat, simulated call, simulated email; past conversations; CSAT; assistant controls (confirm action, second-factor code, ask for a person) |
| `/analyst/home` | analyst | Inicio: availability toggle, status counters, first cases, "while you were away", team now |
| `/analyst/cases` (`?case=&status=`) | analyst | Workspace: case list by urgency, conversation (chat/call/email), customer file, close with reason, escalate, change priority/type, handoff packet, copilot panel (Q&A, suggestions, tools, stage strip) |
| `/supervision/queues` | supervisor | queues per language, assign/reassign |
| `/supervision/team` (`?analyst=`) | supervisor | analysts, load, sheet per analyst |
| `/supervision/escalations` | supervisor | answer / take / reassign escalations |
| `/supervision/cases/:id` | supervisor | read-only case view (audited `case.viewed`) |
| `/supervision/audit` | supervisor | event-log audit view |
| `/supervision/automation` (`?type=`) | supervisor, only if AI switch on | Tipos de caso: stage per case type, signals, thresholds, move back, ask builder chat for an agent |
| `/supervision/automation/proposals`, `/proposals/:id` | supervisor | proposals from agent-core (sources: created here / builder / tracked by id / "Del motor de mejora" / registry); detail with evaluate, approve, reject, publish, activate |
| `/supervision/automation/agents`, `/agents/:id` | supervisor | agents, where prod/staging run, versions, prod rollback |
| `/admin/users`, `/admin/teams`, `/admin/audit`, `/admin/platform` | admin | users and roles (invitations, reset link, unlock, deactivate), teams, audit, "Plataforma" = AI on/off switch |

The notification bell and toasts live in the shell (all staff roles), not in routes.

### Feature table
| Area | State (from code/docs) |
|---|---|
| Roles/auth | analyst, supervisor, admin; password + TOTP (dev code `000000` only for seeded accounts; invited accounts use a real authenticator); lockout 5 tries/15 min; session 480 min; Argon2id; per-tab sessionStorage |
| Channels | chat_app, chat_web, phone_inbound, phone_outbound, email (all simulated: no telephony, no mail server) |
| Case lifecycle | queued -> assigned -> in_progress -> closed (reason required), plus `with_assistant`; one open case per customer; reopen = new linked case; first-response SLA 15 min; language routing (rule H1); priority; case type; escalations (open/withdrawn/answered/taken/reassigned/closed); calls (ringing/active/hold/ended); CSAT |
| Assistant (customer) | slices 14/19: agent-core agent (`recepcion@prod`) answers chats of dataset-linked customers in es/pt; step-up confirm; ends by resolve / escalate with handoff packet / fallback to people. Requires `CC_AGENT_CORE_URL` + keys, else people-only |
| Copilot (advisor) | slices 15/15b/20/21: Q&A thread (`copiloto-asesor`), typed suggestions reply/tool/action/escalate (OFF unless `CC_COPILOT_SUGGESTIONS_AGENT` set; docs say the real agent needs agent-core ADR 0026 and the adapter was never run against a real agent-core), stage strip per case type |
| Maturity per case type (ADR 0006) | stages 0-3 + agent; types: none, unrecognized_charge, undue_charge, app_issue, branch_service, service_quality, virtual_card; team-rule thresholds; seeded sample story (Cobro indebido ready at 84/100 drafts as-is; Cargo no reconocido served by agent `disputas`) |
| Automatizacion (S22) | proposal -> evaluate -> approve -> publish -> activate (promotes `prod` alias, records `agent: active`); every decision asks supervisor's fresh TOTP (step-up); builder chat (`constructor-chat`) in her UI language; move-back; agents list/rollback. "Revocar" (admin) not drawn |
| Engine as a source | proposals with `source: "engine"` via announce; bell "Nueva propuesta de mejora para {agentId}"; list label "Del motor de mejora". The `improvement` dossier is documented as only in the notification, not on the proposal page (check whether #28 changed it: UNVERIFIED) |
| Notifications | persisted per person, bell Nuevas/Anteriores + live toasts. Kinds: assigned_on_arrival, assigned_from_queue, assigned_by_supervisor, reassigned_away, customer_returned, escalation_answered/taken/reassigned, case_rated, case_escalated, case_queued, sla_at_risk, account_locked, invitation_accepted, improvement_proposed |
| Realtime | WebSocket `/api/v1/ws` with per-staff/case/ai/platform topics |
| i18n | es + pt-BR for UI and server texts, per-person preference |

### event_log and catalog
- Table `event_log`: sequence PK, event_id `EVT-...`, event_type, entity, entity_id, case_id, actor_role, actor_id, event_time, ingested_at, payload JSON; append-only (DATA_MODEL.md).
- Event types (from `domain/*/events.py`): case.* (opened, queued, assigned, status_changed, read, first_responded, closed, rated, priority_changed, type_changed, assistant_started, assistant_released, viewed), turn.created, escalation.* (7), call.* (6), assistant.* (session_started, turn_answered, input_queued, step_up_verified, step_up_rejected, ended), copilot.* (query_asked, answered, suggestion_requested/ready/none/failed/decided, tool_used), builder.* (proposal_created/tracked/validated/frozen/reopened/evaluated/approved/rejected/published, draft_saved, alias_promoted, release_revoked, question_asked, answered), ai.* (stage_advanced, stage_moved_back, agent_ready, agent_activated), platform.ai_toggled, auth.* (7), staff.* (~15), team.* (4), customer.session_started.
- Catalog version: I found NO explicit event-catalog version or schema_version (grep for schema_version / catalog_version / event_version found nothing). The in-code catalog is `application/audit/catalog.py` (family, mutating flag, description per type; a test fails on an unknown emitted type). Payloads hold ids, enums, counters, never free text.
- Signals added for the engine (docs/platform/api/engine-signals.md): `release` on `assistant.turn_answered` and `copilot.suggestion_ready/none`; `turn_id`, `agent`, `release` on `copilot.suggestion_decided`. I found no event stream/export API for the engine; reading event_log is via staff audit routes or the DB (what `/audit` exposes to a service identity: UNVERIFIED).

### Internal APIs (not in openapi.json; Bearer `CC_INTERNAL_SERVICE_TOKEN`; 404 if unset, 401 if wrong)
| Route | Purpose |
|---|---|
| `GET /api/v1/internal/grants/{grantRef}` | agent-core `grant_active` check |
| `POST /api/v1/internal/builder/proposals/announce` | engine announces a proposal (title<=120, problem<=600, evidence<=600, expectedEffect<=400, <=8 `CASE-` evidenceLinks, no email / 9+ digit runs). Idempotent by proposalId; proposal must exist in agent-core registry with origin `auto_detect`. Adopts, never approves; notifies all active supervisors once |
| `GET /api/v1/internal/evidence/cases` | up to 8 real case ids for a cell (caseType, channel, language, priority, closeReason, openedFrom/Before); k-anonymity: cells under `CC_EVIDENCE_MIN_CELL` (default 10, min 2) return `{suppressed:true}` |

### Data / seed
First start with `CC_SEED_DEMO_DATA=true`: 15 staff (RUNBOOK section 5; password `demo1234`, MFA `000000`; Tatiana uses real TOTP, Bruna has a pending invitation, Mariana is locked ~13 min, Andres deactivated), ~17 seeded cases (101-117: escalations, a call, an email, closed history), 5 simulator customers plus the seeded-case customers, seeded notifications, seeded AI stages per type. No migrations: after schema changes delete `backend/cc_platform.db` (else `OutdatedSchemaError`). Assistant needs customers linked to dataset ids via private `CC_BANK_CUSTOMER_LINKS_FILE`.

### Tests / maturity
- File counts only: 123 backend `test_*.py`, 134 frontend `*.test.ts(x)`, 9 Playwright specs (admin, ai, auth, automation, channels, chat, home, i18n, supervision). Docs record green gates on 2026-10-03 for an earlier state (pytest 673, vitest 592); I did NOT re-run anything, so current pass status is UNVERIFIED. No `.github` workflows exist on main. Contract tests against agent-core 1.4.0 copies in `backend/tests/contracts`.

## 2. What can be demoed now

### A. People-only platform (no agent-core)
1. Backend: `cd backend && uv sync && uv run cc-api` (127.0.0.1:8000). Frontend: `cd frontend && pnpm install && pnpm dev` (localhost:5173). Alternative: `docker compose up -d --build`. Needs uv, Node 22, pnpm 10; no .env.
2. Check: `curl http://127.0.0.1:8000/api/v1/health`; Swagger at `/api/v1/docs`.
3. Use separate tabs (not "duplicate tab"). Tab 1 `/customer`: pick e.g. Natalia Guzman and write a dispute message. Tab 2 `/login` as `daniela.rios@latambank.example` / `demo1234` / code `000000`: Inicio -> "Empezar a atender" -> the case arrives in Casos -> reply, start a call, send email, escalate (cases 101 and 113 are already escalated).
4. Tab 3 Lucia Herrera (`lucia.herrera@latambank.example`): Colas (cases 109/111/112), Equipo, Escalados (answer/take), Auditoria, bell with seeded notifications.
5. Tab 4 Valeria Quintero (admin): Usuarios (invite -> `/dev/mailbox` -> activate -> TOTP from pyotp), Plataforma (AI switch). Also PT-BR toggle in the account menu, CSAT in the simulator.

### B. Automatizacion / engine path
1. As Lucia with the AI switch on (default in dev): "Automatizacion" in the rail shows the 7 case types with stage bars; "Cobro indebido" is ready for an agent; open its panel (signals, thresholds, move back). Works without agent-core (seeded sample data).
2. Proposals and Agents: without agent-core only known ids show, with a notice. Evaluate/approve/publish/activate need agent-core started with `--registry-api`, and per slice-16 section 8 no demo agent has an `eval_suite`, so a proposal cannot pass `candidate`; approve -> publish -> prod is NOT demoable end to end per the docs (UNVERIFIED against current agent-core main).
3. Engine announce (curl): set `CC_INTERNAL_SERVICE_TOKEN`, connect agent-core holding a real `origin=auto_detect` proposal, then `POST /api/v1/internal/builder/proposals/announce` -> supervisors' bell shows "Nueva propuesta de mejora" -> opens `/supervision/automation/proposals/:id` ("Del motor de mejora"). Without agent-core the call answers 404. The evidence route only needs the token (reads local DB) but the small seed leaves most cells suppressed unless `CC_EVIDENCE_MIN_CELL=2`.
4. Live assistant and copilot need agent-core running with the platform public keys (`python -m cc_platform.scripts.gen_agent_keys`, `CC_AGENT_CORE_URL`, `CC_AGENT_KEYS_FILE`), seed agents loaded (`recepcion`, `copiloto-asesor`, `constructor-chat`, `disputas`) and a customer links file. Not demoable standalone.

## 3. Gaps / risks
- Approve/publish/prod chain blocked by missing `eval_suite` on demo agents (slice-16 section 8): the Automatizacion last mile depends on agent-core content.
- Copilot suggestions: real agent absent (agent-core ADR 0026); adapter never exercised against real agent-core; off by default.
- Engine dossier (`improvement`) reportedly visible only in the notification, not on the proposal page.
- No explicit event-catalog version and no event export API for the engine.
- Evidence route k-anonymity (default 10) vs ~17 seeded cases: demos need a bigger dataset or `CC_EVIDENCE_MIN_CELL=2`.
- No migrations: slices 18-22 each required deleting the SQLite DB.
- No CI workflow in repo; I did not run tests, so pass status is unverified.
- Dev defaults (MFA `000000`, dev secrets); `CC_ENV=prod` refuses to start (no real email adapter): demo-grade by design.
- Docs path drift (`/analista` vs `/analyst`); seed AI stage signals are sample values, not measured.
- Local checkout in tmp/shared/support-platform is 25 commits behind origin/main: pull before running.

## 4. Evidence (paths at origin/main)
- README.md; docs/platform/RUNBOOK.md (run, env vars, accounts, seeded cases); docs/platform/DATA_MODEL.md (event_log, lifecycles)
- frontend/src/app/paths.ts, router.tsx; frontend/src/routes/**; frontend/src/features/{automation,copilot,customer-chat,conversation,supervision,admin,notifications,home,cases}
- docs/platform/api/slice-22-automation.md, slice-21-stages.md, slice-16-agent-builder.md (section 8), slice-14-assistant.md, slice-15-copilot.md, slice-15b-copilot-suggestions.md, slice-12-channels.md, slice-10-notifications.md, improvement-announce.md, engine-signals.md
- docs/platform/adr/0003-agent-core-integration.md, 0006-ai-maturity-by-case-type.md, 0007-improvement-engine-announce.md
- backend/src/cc_platform/api/routers/{internal,builder,ai_stages,notifications,audit,dev}.py
- backend/src/cc_platform/domain/{cases,ai,people,platform,customers}/events.py, domain/ai/maturity_events.py, domain/notifications/notification.py, application/audit/catalog.py
- backend/src/cc_platform/infrastructure/seed/{maturity,people,cases,notifications}.py; docker-compose.yml
- Tests: backend/tests/{api,unit,contracts}, frontend/e2e/*.spec.ts
