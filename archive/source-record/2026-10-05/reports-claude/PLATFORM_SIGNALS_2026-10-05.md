# Platform signals for the improvement engine (2026-10-05)

Lane PLAT2. Sources: support-platform `origin/main` a451001 (worktree `worktrees/support-platform-claude-signals`, branch `feat/engine-signal-sources`), engine `origin/main` 2b870e11 (`platform-contract/` 1.2.0, `platform-exporter/`, `events_sensor.rs`, `scripts/contracts/drift_digest.py`), reports MAGIC_ROUND1C, SPA_S22, E2E_RIG (G1-G11), DETECTION_GAP (items 6, 8). Aggregates and field names only; no customer data read. Paths are relative to `backend/src/cc_platform` (platform) unless noted.

## 1. Headline

1. The platform already records almost every interaction the engine needs, as ids/enums/counters in `event_log` (89 audited types; the contract admits 53 of 57 known). What blocks real signals is not missing data but (a) three contract/catalog gaps and (b) two missing join keys, both now closed platform-side.
2. The engine does NOT call the platform to read events. `platform-exporter` reads the platform database directly (SQLite file, or a Postgres read-only role) through an allow-list of tables and columns, then ships `pulso-observations-2` to the Rust control-api. Free text is dropped client-side (fail closed, per-type `EVENT_FREE_TEXT_KEYS`). A platform export route is therefore NOT needed for event content (item c below).
3. Contract 1.2.0 misses 32 platform event types. Seven matter (section 6). The exporter's `cases` allow-list also lacks `case_type`, the dimension S21/S22 maturity and every per-type slice depend on.
4. Evidence links were the real integration hole (G1): findings hold opaque cell hashes, the announce needs `CASE-` ids, and the announce only checks id format, not existence. Closed with a read-only cell-to-sample route.

## 2. Inventory: what interaction data exists

"Contract" = in catalog 1.2.0 (admitted). "Exporter" = readable today by `platform-exporter`.

| Data | Platform source | Contract | Exporter | Notes |
|---|---|---|---|---|
| Copilot draft decision: used / edited / discarded / ignored, `edit_distance_permille`, escalation recommendation accepted | `copilot.suggestion_decided`; table `copilot_suggestions` (texts purged at 24 h, hash kept) | NO (quarantined as unknown) | no table; event only if admitted | Biggest labelled set. Now carries `turn_id`, `agent`, `release` (this PR) |
| Suggestion produced / empty / failed | `copilot.suggestion_requested\|ready\|none\|failed` (`kinds`, `count`, `truncated`, `run_id`, `trace_id`, `failure_code`) | NO | event only | `ready`/`none` now carry `release` |
| Copilot tool used by the analyst | `copilot.tool_used` (`tool`) | NO | event only | feeds S21 stage 3 |
| Copilot Q&A (what analysts ask) | `copilot.query_asked` (`question_id`, `question_length`), `copilot.answered` | yes | yes | text stays in `copilot_threads.messages`, never exported. Repeated query = same case, many `question_id` |
| Escalation to supervision | `escalation.opened` (`motive` FREE TEXT, dropped), `answered`, `taken`, `reassigned`, `withdrawn`, `closed`, `acknowledged` | yes | yes | motive text is not available; only the copilot's `reason_code` (policy code, bounded) would cluster motives without text (ask A5) |
| AI to human handoff | `assistant.ended.result` (resolved/escalated/ended/failed/released), `handoff_ref`; `case.assistant_released.reason` | yes | yes | `failed`/`released` = strong failure labels |
| Handoff quality label useful/incomplete/unnecessary | sent to agent-core (`application/ai/staff.py:226`), NOT in event_log | no | no | needs a platform event or agent-core export (ask A4) |
| Assistant turn outcome | `assistant.turn_answered` (`agent`, `run_id`, `trace_id`, `status`, `outcome`, `awaiting`) | yes | yes | now carries `release` |
| Customer rating | `case.rated` (`score`; `comment` free text dropped); `cases.rating_score` | yes | yes | |
| Advisor actions: pickup, reassignment, availability | `case.assigned` / `assignments` (`reason`, `waited_seconds`, `previous_staff_id`, `open_cases_at_assignment`), `staff.availability_changed` | yes | yes | queue pickup latency = `waited_seconds` |
| Time to first action / resolution | `case.first_responded`, `case.closed` (`close_reason`; `note` free text dropped), `case.opened` | yes | yes | events sensor families `first_response_delay`, `resolution_delay` |
| Priority changes | `case.priority_changed` | yes | yes | |
| Case type (the S21/S22 dimension) | `cases.case_type`; `case.type_changed` (`from`, `to`) | NO | NO (`case_type` is neither allow-listed nor known-unreadable: it will show as schema drift) | highest-value small contract fix (ask E1) |
| Case type maturity S21/S22 | `ai.stage_advanced\|moved_back`, `ai.agent_ready\|activated` (`case_type`, stages, `agent_id`); table `case_type_maturity` | NO | no | engine already computes its own view (SPA_S22 section 4) |
| AI switch | `platform.ai_toggled` | NO | no | needed to avoid reading the "AI off" period as degradation |
| Calls | `call.*` | yes | yes | secondary |
| Builder lifecycle (proposals, decisions) | 15 `builder.*` (`proposal_evaluated.verdict`, `approved`, `rejected` with `reason_length`, `published.release_id`, `alias_promoted.before`) | yes | yes | decision trail for FDBK1 (reject rate by finding kind) |
| Release markers | `builder.proposal_published`, `builder.alias_promoted`, `builder.release_revoked` | yes | yes | before/after cut points |
| Agent runs and outcomes | `assistant.turn_answered`, `suggestion_ready`; `run_id`/`trace_id` join to agent-core; tool errors/retries do not exist (DATA_MODEL: no tool_call event) | partial | partial | TEL1 `AG_*` aggregates come from agent-core, not the platform |

Platform types not in 1.2.0 (32): `copilot.suggestion_*` (5), `copilot.tool_used`, `case.type_changed`, `ai.*` (4), `platform.ai_toggled`, `staff.*` (14, planned: names/e-mails in payloads, keep out), `team.*` (3, planned).

## 3. How the engine reads the platform today

- `platform-exporter` (Python): `SqliteSource` (engine authorizer, read-only URI) or `PostgresSource` (read-only transaction; infra PL-L5 role). All SQL built by `policy.select_sql` over `ALLOWED_COLUMNS`: `event_log`, `cases` (id, customer_id, channel, language, priority, opened_at, sla_due_at, previous_case_id, rating_score, rated_at), `customers`, `staff`, `turns` (no text), `assignments`, `customer_case_slots`. `cases.status`, `close_reason`, `case_type`, closure and text columns are not readable: state is rebuilt from events.
- Delivery: per-attempt service JWT to the control-api, `POST /internal/v1/platform/observations`; quarantine, holes and late rows handled client-side; unknown/denied types are withheld with a payload-free stub.
- The only platform HTTP routes the engine uses: `POST /internal/builder/proposals/announce` (PR 17, merged) and, new in this PR, `GET /internal/evidence/cases`. Both on `CC_INTERNAL_SERVICE_TOKEN`, unset means 404.
- Sensor consumer: `events_sensor.rs` reads `events.ndjson` (identifier/enum/time columns, never payload) and `cases.ndjson` (`case_id, channel, language, previous_case_id`); cells are `language/channel`; families: reassignment_rate, recurrence_rate, first_response_delay, resolution_delay. It does not read any suggestion or release data yet.

## 4. Decisions on (a)-(e)

### (a) Admit `copilot.suggestion_*` in 1.3.0 with `turn_id` and bounded fields: platform side DONE, contract side is the engine's

Platform payloads (all ids, enums, counters; the platform test `test_the_events_carry_ids_and_enums_never_a_text` and the new API test assert no text):

| Event | Keys (new in bold) |
|---|---|
| `copilot.suggestion_requested` | `analyst_id`, `trigger`, `based_on_sequence` |
| `copilot.suggestion_ready` | `analyst_id`, `agent`, `kinds[]`, `count`, `truncated`, `run_id`, `trace_id`, **`release`** |
| `copilot.suggestion_none` | `analyst_id`, `agent`, `run_id`, `trace_id`, **`release`** |
| `copilot.suggestion_failed` | `analyst_id`, `failure_code` (problem code, never a message) |
| `copilot.suggestion_decided` | `subject` (reply\|escalation), `decision` (used\|edited\|discarded\|ignored\|accepted), `edit_distance_permille` (null unless edited/used), **`turn_id`**, **`agent`**, **`release`** |
| `copilot.tool_used` | `tool` |

Join: `turn_id` = `turns.id` of the analyst message (`turn.created` entity id); set only for used/edited. Discard/ignore/escalation have none by construction.

### (b) `release` on agent-originated events: DONE (additive)

`assistant.turn_answered.release`, `copilot.suggestion_ready|none.release`, `copilot.suggestion_decided.release`. Source: agent-core `AgentRun.release` at `start_run`, persisted in two new nullable columns (`assistant_sessions.agent_release`, `copilot_suggestions.release`). Not done: `copilot.answered` (the Q&A thread keeps no release), `assistant.ended`. Release is the registry release id (same value as `builder.proposal_published.release_id`), so before/after can key on the alias-promotion event AND on the release of each run, removing the staging/prod mixing in the timestamp cut.

### (c) Export route for the engine: NOT needed for events; the existing exporter is enough

Reasons: the exporter already reads the exact table `event_log` with an allow-list, drops free text per type, and handles holes/lateness; privacy is enforced by construction on the engine side and the DB role. A platform route would duplicate the exporter and add a second privacy surface. Caveats to state, not to build now:
1. It needs database reachability. In the e2e rig (SQLite on the host) that holds. In a hosted deployment the infra team provides the read-only Postgres role (PL-L5). If the DB cannot be shared, the platform would need a cursor route: `GET /internal/events?after=<sequence>&limit=<=500&types=...` returning only contract-allowed keys per type (the engine's `EVENT_PAYLOAD_KEYS` minus `EVENT_FREE_TEXT_KEYS`), stable on `event_log.sequence`. Sequence is already the exporter's cursor, so this is S-M and a pure wrapper over `event_log.search`. Not built: no consumer asks for it and the exporter is proven.
2. Case ids exported are the real `CASE-` ids, not pseudonyms. That is deliberate: supervisors open them (`/supervision/cases/:id`) and the platform's own announce takes them. Customer ids are exported raw today as `customers.id` (platform ids, not bank ids); if the engine ships them past the exporter it must hash. This is an engine policy decision, flagged here.

### (d) Case-id resolution for evidence links: DONE with the least invasive design

Options weighed: (1) engine-side demo map file (R5): works for the demo only; (2) a route that resolves an opaque hash to ids: the platform would have to know the engine's hashing and keep an index of cell membership: new state, rejected; (3) cell to sample: a read-only route over `cases` that the engine calls with the dimensions of the finding. Chosen (3). No new table, no hash coupling, no stored mapping.

`GET /api/v1/internal/evidence/cases?caseType&channel&language&priority&closeReason&openedFrom&openedBefore&limit` returns `{suppressed, matched, caseIds}`. Bound: `limit` 1-8 (the announce's 8 links). k-safe: fewer than `CC_EVIDENCE_MIN_CELL` (default 10) matches gives `{suppressed: true, matched: null, caseIds: []}`. Newest-first deterministic sample. Ids only. Same token pattern as PR 17. Backward compatible: new route, new setting with a default.
Consequence for the engine: findings need dimensions that map to these parameters (case type, channel, language, priority, close reason, period). A finding on `language/channel` cells maps directly. Still open: the announce verifies id FORMAT only (ask A3: verify existence).

### (e) Advisor-behaviour signals that matter for proposals, by value / effort

| Signal | Already derivable? | Needs | Value | Effort | Verdict |
|---|---|---|---|---|---|
| Copilot draft acceptance and edit distance by agent / release | now yes (`decided` carries agent, release, edit distance) | contract 1.3.0 admits the 5 `suggestion_*` + `tool_used` | H | S | do first (blocked only on contract) |
| Same, by case type | join `case_id` to `cases.case_type` | exporter allow-list gets `cases.case_type` (E1) | H | S | do with E1 |
| Edited drafts as correction dataset (draft hash, sent text) | text dropped by design; hash kept | agent-core run output by `run_id` holds the draft (24 h window) | H | M | engine-side, later; privacy review first |
| Time to first action | yes (`case.first_responded`, `case.opened`) | none | M | S | already a sensor family |
| Queue pickup latency | yes (`assignments.waited_seconds`) | none | M | S | add a family to `events_sensor.rs` |
| Reassignment / escalation rate by cell | yes (`case.assigned` twice, `escalation.*`) | none | M | S | reassignment is a family; add escalation rate |
| Escalation motive clusters without text | NO (`motive` is text) | include the copilot recommendation's `reason_code` in `suggestion_decided` (subject escalation), bounded policy code | M | S | ask A5 (platform, 5 lines) |
| Repeated queries to the copilot | yes: count of `copilot.query_asked` per case (`question_length` bucket) | none | M | S | add family; text-free |
| Handoff quality useful/incomplete/unnecessary | NO | a platform event `case.handoff_rated` or an agent-core export | M-H | S-M | ask A4 |
| Outcome attribution after release | now yes | `release` on events (done) plus contract 1.3.0 keys | H | S | done platform-side |
| AI-off periods | NO | admit `platform.ai_toggled` | L-M | S | cheap guard against false drift |

## 5. What was implemented (PR to support-platform `main`, branch `feat/engine-signal-sources`)

Four commits, TDD, backend only (no frontend change: the new route is not in `openapi.json`, so `schema.gen.ts` is untouched):

1. Fix a stale test on main (`copilot.suggestion_ready` requires `truncated`; `test_maturity.py::test_the_case_facts_come_from_the_event_log` was failing before this branch).
2. `release` and `turn_id` on the AI events (domain, application, persistence, tests at domain, application and API level).
3. `GET /internal/evidence/cases` and `CC_EVIDENCE_MIN_CELL` (use case `SampleEvidenceCases`, `CaseRepository.sample_cell` in both adapters; tests over memory and SQLAlchemy, plus the HTTP contract).
4. Docs: `docs/platform/api/engine-signals.md`, DATA_MODEL rows, README index.

Verification (touched areas only): `ruff check` and `ruff format --check` clean on `src tests`; `mypy` clean (292 files); pytest: `tests/unit/domain` (285), `tests/unit/infrastructure`, `test_architecture`, `test_openapi`, `test_maturity`, `test_suggestions`, `test_suggestion_process`, `test_assistant*`, `test_evidence` (memory + sqlalchemy), `api/test_internal_evidence_api`, `api/test_internal_announce_api`, `api/test_copilot_suggestions_api`. The full suite was not run (too slow on this machine).
Local note: on Windows the project venv lacks `tzdata`; `uv pip install tzdata` into `.venv` before running pytest (not committed; CI runs Linux).

Backward compatibility: every payload key is added with a default (`None`); existing consumers (maturity projector, audit, notifications) ignore it; events written before the change simply lack the keys (the engine must treat them as null). DB recreate note: delete `backend/cc_platform.db` once (no migrations); it is the same recreate as slices 21/22 and the announce.

## 6. NOT done, and asks

Not done (platform): export route (c) beyond the exporter; `release` on `copilot.answered` and `assistant.ended`; `reason_code` on escalation decisions; handoff-quality event; announce existence check for evidence links; `platform.ai_toggled` is already emitted, only the contract lacks it.

Asks:
- A1 Product/engine (contract owner): publish contract 1.3.0 (note below).
- A2 Platform team: review and merge the PR; recreate the dev DB.
- A3 Platform: make the announce verify that each `evidenceLink` exists (S; 422 on unknown) once the engine calls the sampler.
- A4 Platform/agent-core: emit the handoff-quality label as an event or export it.
- A5 Platform: add the copilot escalation `reason_code` to `copilot.suggestion_decided` (subject escalation) after reviewing that agent-core cannot put prose in it.
- A6 Engine: wire `PULSO_PLATFORM_URL` + token to the evidence route in the announce path (map finding dimensions to the query), keep demo-map as a fallback only in profile demo.

## 7. Engine-side contract note (for the engine repo; NOT edited here)

Proposed `platform-contract` 1.3.0, additive over 1.2.0, from platform `origin/main` plus this PR (`EVENT_CATALOG_VERSION` 1.3.0, `CONTRACT_VERSION` 1.3.0, `PREVIOUS` 1.2.0; update `README.md` revision section, regenerate schemas with `python -m platform_contract`, re-pin `scripts/contracts/pinned_digests.json` with `drift_digest.py --write` after review: this PR changes `domain/ai/events.py` and `tables.py`, both in `PLATFORM_FILES`, so the digest gate WILL report drift until re-pinned).

New admitted event types (data class `copilot`, no free text):
`copilot.suggestion_requested`, `copilot.suggestion_ready`, `copilot.suggestion_none`, `copilot.suggestion_failed`, `copilot.suggestion_decided`, `copilot.tool_used`.
Also admit (class `operational` / `assistant`): `case.type_changed` (`from`, `to`), `ai.stage_advanced` (`case_type`, `from_stage`, `to_stage`), `ai.stage_moved_back` (+ `agent_cleared`), `ai.agent_ready` (`case_type`), `ai.agent_activated` (`case_type`, `agent_id`), `platform.ai_toggled`. Keep `staff.*` and `team.*` planned.

`EVENT_PAYLOAD_KEYS` additions:
```
"assistant.turn_answered": + "release"
"copilot.suggestion_requested": ("analyst_id", "trigger", "based_on_sequence")
"copilot.suggestion_ready": ("analyst_id", "agent", "kinds", "count", "truncated", "run_id", "trace_id", "release")
"copilot.suggestion_none": ("analyst_id", "agent", "run_id", "trace_id", "release")
"copilot.suggestion_failed": ("analyst_id", "failure_code")
"copilot.suggestion_decided": ("subject", "decision", "edit_distance_permille", "turn_id", "agent", "release")
"copilot.tool_used": ("tool",)
"case.type_changed": ("from", "to")
```
`EVENT_FREE_TEXT_KEYS`: none for the new types. Enums: `decision` in {used, edited, discarded, ignored, accepted}; `subject` in {reply, escalation}; `kinds` items in {reply, tool, action, escalate}; `trigger` in {customer_message, manual, handover}.
Exporter: add `cases.case_type` to `ALLOWED_COLUMNS["cases"]` (bounded enum: unrecognized_charge, undue_charge, app_issue, branch_service, service_quality, virtual_card, none); the exporter should treat a missing `release`/`turn_id` key (rows written before this PR) as null, never as drift. New tables `assistant_sessions.agent_release` and `copilot_suggestions.release` are on non-allow-listed tables: no exporter change.
Sensor: new events-sensor families `draft_acceptance_rate` and `draft_edit_distance` by (agent, release) and by case type; `copilot_repeat_queries`, `queue_pickup_wait`, `escalation_rate`; outcome attribution joins post-release runs by `release`.
