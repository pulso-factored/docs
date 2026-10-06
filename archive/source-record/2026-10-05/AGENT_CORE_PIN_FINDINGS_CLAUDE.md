# Agent Core pin findings (Claude, DRAFT)

STATUS NOTE 2026-10-04 (UTC): agent-core `main` is now `c814c2b` (PR #30 merged 2026-10-03T21:03Z; 6 commits, wire byte-identical, only `composition/{builder_tools,serve,serve_ports}.py` changed under `agent_core/`). improvement-engine `main` pins `894fa65` (PR #82 merged); the `c814c2b` bump is in progress (`AGENT_CORE_PIN_BUMP_3_ANALYSIS_CLAUDE.md`). The findings below were not re-run at `c814c2b`, except: PRs #23, #24 and #28 are still NOT on `main` (re-verified with `gh api`: heads `5705e58`, `19e7a10`, `3499f94` are not ancestors of `c814c2b`; `registry_openapi.py`, `contracts/registry-openapi.json`, `jev_gateway.py` absent from `main`); F-04 stays PARTIAL; the in-flight `409 idempotency_conflict` ambiguity (N8-02) stays open (our runtime matches the text `sigue en curso`, improvement-engine#82). New since this document: `resolve_ports` reads `args.lang_thresholds` unconditionally (embedders with a hand-built `Namespace` fail at startup) and the builder-tools / `registry-e2e` overlap question. The consolidated relay list is `AGENT_CORE_RELAY_FOR_USER.md`.

UPDATE 2026-10-03 (late): re-verified at `894fa65575d83420523f33ec1c6919b8965f7ebe` (current `main`, PR #29). Verdict: the 10 top findings are FIXED except F-04 (PARTIAL). See the new column `Status at 894fa65`, the notes under Section 0, and Section 9 (re-test, new findings, what #23-#29 really changed). Important: PRs #23, #24 and #28 are merged into stacked side branches, NOT into `main` (Section 9.1).

Status: DRAFT for internal review. Nothing here has been filed, pushed or opened upstream. We cannot contact the Agent Core team directly: Section 0 is written so the user can relay it as is.
Pin under test: `86a767474042a566a0dbd6ed23588959f27ebdb3` (contracts/VERSION 1.3.0), re-verified at `789d6c89b2fca90fc10e2abf157da51dc81c5d51` (current `main`; contracts/VERSION still 1.3.0). Note on SHAs: `b32b1e9` (PR #25, N-01..N-11) is an ancestor; since then PR #26 (HttpLLMGateway, ADR 0022/0024, merged as `d7f8b8d`) and PR #27 (AWS scale-out: S3 blobs, outbox relay, pool, sweep DSN, merged as `789d6c8`) landed, so "b32b1e9 plus open PRs #26/#27" is now simply `main`. Both PRs are closed/merged (#26 head `71a5713`, #27 head `1fbccde`).
Frame: Agent Core as a platform used by several consumers, not only the automejora system.

## 0. Top 10 for the Agent Core team (relay-ready, priority order, verified on `789d6c8`; status re-verified on `894fa65`)

Each item has a runnable repro in the scratch clone (scripts in `...\scratchpad\ac_probes\`); ids refer to sections below. Items 1, 3, 4, 7, 9, 10 date from the pin and are unchanged by N-01..N-11 / PR #26 / PR #27.

1. **Evaluation gate replays stale runs (F-01, S1).** `EngineScenarioHarness` uses `idempotency_key = f"eval-{scenario.id}"` and fixed `client_turn_id`s; with the persistent eval DB that `serve --registry-api` wires, a second evaluation of the same scenario/principal returns the first run's 37 stored events without executing anything (a gateway that now always fails is not noticed; `repetitions: N` are N copies). Fix: key from `(eval_run_id, scenario, repetition, label)`. **Status at 894fa65: FIXED. `probe_eval.py` at 894fa65: runs #1-#3 return three distinct run ids (37 events each, really executed); with a gateway that always fails the same-scenario run #4 now raises `HarnessUnavailable` (`Boom.generate` calls = 2). Key is now `eval-<eval_run id>-<label>-<scenario>`.**
2. **`agentcore sweep` cannot read registry entities once S3 blobs are on (PR27-01, S1 for any deployment that enables `AGENTCORE_BLOB_BUCKET`).** `build_sweeper` builds `PgRegistryStore(...)` without the blob factory (`agent_core/cli.py:187`); `migrate` drops the `reg_blobs` FK, new blobs live only in S3, so `sweep` raises `IntegrityError: no existe el contenido ...` for any agent version published after the switch. Fix: pass `blob_factory_from_env(os.environ)` (as `serve` and `registry` do) and add a test with the S3 + Postgres combination. **Status at 894fa65: FIXED. `build_sweeper` passes `blob_factory_from_env(os.environ)`; with `AGENTCORE_BLOB_BUCKET` set in the sweep process `probe_pr27_sweep_blobs.py` prints `sweeper registry: OK` (moto S3 + PG). Operational rule: the sweep job must receive the same bucket env as `serve`.**
3. **Concurrent `POST /v1/runs` with the same Idempotency-Key creates duplicate runs (F-02, S1).** 12 parallel requests -> 12 runs (201 each). `get_run_idempotency` is checked in a separate UoW and stored with `ON CONFLICT DO NOTHING` without checking the row count. Task agents with write tools execute side effects N times. Fix: reserve the key first / advisory lock in the same transaction. **Status at 894fa65: FIXED, with a semantics change: 12 concurrent same-key requests give 8 x 201 (same single run_id) + 4 x 409 `idempotency_conflict` (key reserved first; `reserve_run_idempotency`). Clients must treat a 409 as retry, see N8-02.**
4. **Task runs cannot read their own `input` (F-03, S1).** `RunInput.input` becomes `claimed` slots; flows only read `validated`, the only writer is `collect` on a `slot_answer` a task run never receives, `validate` says "sin violaciones". The run escalates `validation_failed`. Fix: input schema for task agents stored as `validated`, plus an M1 rule against reading unwritable slots. **Status at 894fa65: FIXED, opt-in: new `Agent.input_schema` (task agents only) makes `start_run` validate the input and store slots as `validated`; without it the slot is still `claimed` and a new M1 rule AG-04 rejects a flow that reads such a slot at publish/import time. `probe_task_input_new.py`: no schema -> `escalated validation_failed`; with schema -> `completed`, slot `validated`; wrong type -> `400/422 invalid_request input: slot_type_mismatch`.**
5. **Outbox relay crashes on a message type it does not know (PR27-02, S2; crash loop on rolling deploys).** `PostgresOutbox.pending()` validates every row as `OutboxMessage` whose `type` is `Literal["handoff_created"]`; one row of another type raises an uncaught pydantic `ValidationError` (service mode: process exit, restart, same row). The relay's own `unknown` counter is dead code. Fix: read rows tolerant of unknown types (skip and count, or dead-letter) and catch per row. **Status at 894fa65: FIXED. `PostgresOutbox.pending()` filters by known `type` in SQL and skips corrupt rows; a `future_type` row no longer raises (`probe_outbox_new.py` -> `pending -> []`). Residual: the skipped row stays pending forever and is not counted anywhere (N8-05).**
6. **`release_settings` (N-07) lets the `constructor` role drop all interrupts and set an unbounded `max_input_chars` with no extra gate (NF-01, S2).** A bot with only `constructor` published a release with `interrupts=[]` (the base `fraude` escalation gone) and `max_input_chars=2_000_000_000`; the evaluation gate passed and the approver sees the new `release_settings` content but no diff against the base (what was removed is not shown). Fix: require `admin`/specific role for interrupt removal or show a base-vs-candidate diff, cap `max_input_chars`, make platform interrupts non-removable. **Status at 894fa65: FIXED. A constructor-only bot changing `interrupts` gets `forbidden_role: ... exige el rol admin`; `max_input_chars` is capped at 100000 (rejected at freeze with `validation_failed`, `put_draft` still accepts it); interrupts can be `locked` (REG-LOCKED); the approver review now carries `release_changes` (field, before, after). `probe_n07_new.py`.**
7. **Run/transcript read isolation depends entirely on the consumer's `AuthzPort` (F-04, S2).** With a permissive port an anonymous principal reads a customer's run and transcript (200). Fix: hard rule in `authorize_read` for customer/anonymous principals; ship a port contract-test kit. **Status at 894fa65: PARTIAL. `authorize_read` now denies customer and anonymous principals that do not own the run whatever the port says (anonymous -> 403 `subject_forbidden`). An advisor WITHOUT delegation still reads the run with a permissive port (200), and a service principal is still entirely up to the `AuthzPort`; no contract-test kit shipped.**
8. **Export cursor can skip rows and never refreshes status (N-08, NF-02, S2).** `run_seq` is a `bigserial` assigned at INSERT, not at COMMIT: a transaction that took a lower number and commits later than a higher one is never delivered to a consumer that advanced its cursor (SQL-level repro, exact export query). Also the cursor is creation order, so a run exported as `open` is never re-exported when it closes. Fix: expose a commit-ordered cursor (xmin/`pg_snapshot` watermark or an `updated_at`/`event_seq` stream) and document that summaries are snapshots. **Status at 894fa65: FIXED, with caveats (N8-03). Cursor is now `runs.change_xid` (commit-ordered, below the snapshot xmin) and a run is re-exported when it changes. Live: with tx A open and tx B committed, page 1 is empty; after A commits both appear (`probe_nf02_new.py`).**
9. **Rate limit (F-06, S2).** Blocks reads and idempotent replays (a throttled client cannot recover its run id), no `Retry-After`, racy (soft cap), per-principal so a service principal throttles a whole tenant, not configurable from `serve`. **Status at 894fa65: FIXED (largely). Only run creation and turn processing consume quota; reads and idempotent replays do not (live: GET and replay return 200 while the 30th POST is 429); `Retry-After: 60` on 429; in-flight reservation (60 concurrent distinct keys -> 29 x 201 + 31 x 429 with a limit of 30); env knobs `AGENTCORE_RATE_MAX_HITS`, `AGENTCORE_RATE_WINDOW_SECONDS`, `AGENTCORE_DAILY_BUDGET_USD`, `AGENTCORE_RATE_SERVICE_MULTIPLIER` (service principal x10). Still per principal and per replica.**
10. **Registry CLI reports failure after the write committed (F-08, S2, Windows).** `print(dumps(result))` raises `UnicodeEncodeError` on cp1252 stdout (release docs contain a unicode arrow) after `publish` committed; exit 1, retry with the same key crashes again, a new key returns `illegal_transition`. Fix: `sys.stdout.reconfigure(encoding="utf-8")` or `ensure_ascii=True`. **Status at 894fa65: FIXED. `main()` calls `_force_utf8_streams()` (stdout/stderr reconfigured to utf-8); in-process probe with a cp1252 stdout prints the arrow as UTF-8 bytes.**

Next tier (not in the top 10): F-07 scenarios cannot express subject/input/principal type; F-05 `serve` outside demo; PR27-03..05 (pool sizing and readiness, S3 rollback hazard, relay head-of-line and leader liveness); NF-04 key reload failures are silent; F-09/F-10/F-11/F-12/F-14/F-15 friction items still open.

Honest scope note: items 1-4, 7, 9, 10 and PR27-01, PR27-02, NF-01, NF-02 were reproduced live (scripts named in each section). PR27-03..05, NF-03 and the PII remark in NF-03 are from code reading and are labelled as such.

## 1. Environment

| Item | Value |
|---|---|
| Scratch clone | `$env:USERPROFILE\AppData\Local\Temp\claude\D---codex-factored\18ab5ab6-8b27-4650-818f-7d8bb6599946\scratchpad\agent-core-pin` (clone of the read-only reference, `git checkout` at the pin, `git rev-parse HEAD` verified equal) |
| Reference repo | `D:\.codex\factored\references\agent-core`, never edited. `git status` shows only an untracked `.nexus-outbox/` that I did not create. |
| Install | `uv sync --locked --python 3.12` OK |
| OS | Windows 11, Python 3.12.10 |
| PG | throwaway `postgres:16` on podman connection `pulso-dev`, `--cgroups=disabled`, `127.0.0.1:47311`, name `ac-pin-pg-claude`, removed afterwards (verified gone). First two port choices (55611, 55633) failed with "Couldn't listen on requested ports" (Windows port reservation), 47311 worked. |
| Probe scripts | `...\scratchpad\ac_probes\` (probe_eval.py, probe_task_input.py, http_probe.py, http_conc.py, env.sh, reg_task/) |
| Demo | Brief mentions `agentcore demo atencion/disputa-cargo`. There is **no `demo` subcommand** at the pin (see F-17). Equivalent exercised: `agentcore record resuelto` + `agentcore replay --mode fixture` on `tests/fixtures/registry-demo` (atencion / disputa-cargo): `match - fixture - run-0001@demo`; and `agentcore serve` in demo mode with real PG + HTTP. |

## 2. Suite results

| Run | Command | Result |
|---|---|---|---|
| Unit, no PG | `uv run pytest -p no:cacheprovider -q` | 4124 collected: **4018 pass, 1 fail, 105 skip** (104 PG-integration + 1 perf), 451 s |
| PG-backed | same, `AGENTCORE_TEST_DATABASE_URL=postgresql://...:47311/agentcore AGENTCORE_REQUIRE_POSTGRES=1` | 4124: **4120 pass, 3 fail, 1 skip** (perf only, needs `AGENT_CORE_PERF=1`), 158 s. 68 integration tests ran: 68 pass, 0 skip |
| Contracts | `agentcore contracts --check` | exit 0 (no drift in the generated files) |

The failures are all in `tests/composition/test_transfer_spans.py` and **change between runs** (run 1 `test_without_a_request_span...`, runs 2/3 different tests of the same file): flaky, see F-16. No PG test failed.

## 3. Findings

Severity: S1 = wrong results / data duplication / security-relevant, S2 = blocks or seriously hurts a consumer, S3 = friction, S4 = nit.

| Id | Sev | Title | Status at 789d6c8 | Status at 894fa65 |
|---|---|---|---|---|
| F-01 | S1 | Evaluation replays previous run when eval DB is persistent (fixed idempotency key) | still present | **FIXED** |
| F-02 | S1 | `POST /v1/runs` idempotency is not concurrency-safe: duplicate runs | still present | **FIXED** (409 while in flight) |
| F-03 | S1 | Task runs cannot read their own `input`; static validation accepts such flows | still present | **FIXED** (opt-in `input_schema`, rule AG-04) |
| F-04 | S2 | Run/transcript read isolation is delegated entirely to the consumer `AuthzPort` (fail-open with a permissive port) | still present | **PARTIAL** (customer/anonymous fixed; advisor/service still via port) |
| F-05 | S2 | `agentcore serve` outside demo: 7 factories, only `DemoContext`, and no production implementation of 4 of them ships in the wheel | still present (pool added, rest unchanged) | still present (not re-run; `serve.py` only gained rate-limit env) |
| F-06 | S2 | Rate limit is not configurable from `serve`, per-principal (a service principal throttles the whole tenant), racy, no `Retry-After` | still present | **FIXED** (largely; per principal/replica remains) |
| F-07 | S2 | Scenario harness cannot express task input, subject, principal type; always `customer` | still present | still present (`evaluation.py` scenario model unchanged apart from the key) |
| F-08 | S2 | Registry CLI crashes with `UnicodeEncodeError` on Windows after the write has committed | still present | **FIXED** |
| F-09 | S3 | Registry write idempotency is only partially exposed (HTTP/CLI) and inconsistent in error codes | still present | still present (registry HTTP unchanged) |
| F-10 | S3 | problem+json is not one schema: registry vs M9 bodies differ, 405 maps to `invalid_request` | changed (partly) | still present (405 -> `invalid_request` re-observed live) |
| F-11 | S3 | OpenAPI contract: 2xx responses untyped (`{}`), registry API absent, version mismatch with contracts | changed (partly) | still present (openapi.json only 7 paths, no registry; `#23` not on main) |
| F-12 | S3 | Registry CLI: bad credential prints a Python traceback; `promote` cannot carry a reason; `evaluate` has no suite version | still present | still present (CLI unchanged except utf-8) |
| F-13 | S3 | Demo `serve` identity double accepts only staff tokens; customer tokens need `--identity-keys` (undocumented) | still present | still present (unchanged) |
| F-14 | S3 | Conversational run accepts arbitrary `input` from a customer principal | still present | still present (unchanged) |
| F-15 | S3 | `replay --mode audit <run_id>` is a dead path (no DSN option); messages say "needs engine" | changed (partly) | still present (unchanged) |
| F-16 | S4 | `test_transfer_spans.py` is flaky on Windows; suite without PG is 3x slower because every PG test waits for a connect | not reproduced (code unchanged) | not reproduced (not re-run) |
| F-17 | S4 | Docs/brief mention a demo command that does not exist; `testing/` is outside the wheel but is the only home of reference ports | still present | still present |

### F-01 (S1) Evaluation replays the first run when the eval DB persists

- Repro: `uv run python ac_probes/probe_eval.py postgresql://agentcore:agentcore-dev-only@127.0.0.1:47311/agentcore` (builds the stock `EngineScenarioHarness` exactly as `build_registry_service_for_serve` does, with `PostgresStore` as eval storage, `SystemIds`).
- Expected: each `harness.run(...)` executes the scenario again, so a regression in the candidate is observed; `repetitions: N` are N independent runs.
- Actual: run 1 creates run `...e3`; runs 2, 3 return the **same run_id and the same 37 stored events** without executing anything. After swapping the gateway for one that always raises `GatewayError`, run 4 (same scenario id, same principal) still returns the old 37 events and **no `HarnessUnavailable`**; `Boom.generate` calls = 1 (only the later run with a different principal executes and then correctly raises `HarnessUnavailable`).
- Cause: the harness fixes `idempotency_key = f"eval-{scenario.id}"` and `start_run` is idempotent per `(principal.key, key)`; the follow-up `handle_turn` uses `client_turn_id = f"c-{n}"`, also replayed. Then `storage.audit.read(run_id)` returns the first run's events.
- Evidence: `agent_core/composition/evaluation.py:117` (key), `:118-130` (client_turn_id), `agent_core/turn/engine.py:774-784` (replay path), `agent_core/composition/serve_registry.py:20-24` (persistent `api.eval_uow_factory`). The in-memory demo hides it (`testing/registry_demo.py` builds a fresh `InMemoryStore` per call and `FakeIds` restart at `run-0001`).
- Impact: with `serve --registry-api` the gate (`pass/fail`) for a candidate (or a base release) can be computed from a **previous** evaluation's events. With `repetitions > 1` the repetitions are identical copies. This breaks the central guarantee of the registry.
- Workaround we use: give each evaluation job its own storage (fresh schema/DB or `InMemoryStore`) via the `storage` callable, and make the idempotency key unique (our own harness subclass). Never reuse the stock harness with a persistent store.
- Proposed upstream: build the key from `(eval_run_id/job id, scenario.id, repetition, label)`; pass a job nonce through `ScenarioHarness.run`; add a test running the same scenario twice against a persistent store with different candidates.

### F-02 (S1) Concurrent `POST /v1/runs` with the same Idempotency-Key creates duplicate runs

- Repro (server from `agentcore serve --registry-api --identity-keys ...` in demo mode): `uv run python ac_probes/http_conc.py` sends 12 concurrent `POST /v1/runs` with the same `Idempotency-Key` and body.
- Expected: one run; the others return the same `RunResult` (or 409).
- Actual: 12 x `201` with **12 distinct run_ids**. Sequential replay works (same run_id), so only the race is broken.
- Cause: `start_run` checks `get_run_idempotency` in a separate UoW before doing the work and stores the key at commit with `INSERT ... ON CONFLICT DO NOTHING`, so the loser silently commits its own run and drops its key.
- Evidence: `agent_core/turn/engine.py:777-784` (check), `:839` (put), `agent_core/adapters/postgres_uow.py:312-314` (`ON CONFLICT DO NOTHING`; the unique violation is swallowed, rowcount never checked).
- Impact: for task agents with write tools a client retry/double-submit executes the side effects N times. For conversational runs it creates N sessions.
- Workaround: serialize start per `(principal, key)` in the caller; use a deterministic key at our edge and a lock (advisory) before calling Agent Core.
- Proposed: reserve the key first (insert row `status=pending` or `pg_advisory_xact_lock(hashtext(principal||key))` in the same transaction as the check); on conflict return the stored result. Add a threaded PG test.

### F-03 (S1) Task run `input` is unreadable; static validation does not catch it

- Repro: `uv run python ac_probes/probe_task_input.py` (m04 harness, task agent `tarea-in`, flow with a tool node `args: {cliente: slots.cliente}`, `RunInput.input={"cliente": "demo-1"}`). Registry form: `agentcore validate ac_probes/reg_task` prints `sin violaciones`.
- Expected: either input slots are readable by the flow, or the validator rejects reading a slot nobody can write, or `RunInput.input` is rejected.
- Actual: slot stored as `('demo-1', 'claimed')`; the node escalates `validation_failed` (`status=escalated`). Only a `collect` node writes `validated`, and `collect` only validates on `resume.kind == "slot_answer"`; a task run has no user to answer. `validate_slot` also rejects any non-string (`:28`), so structured or numeric task inputs could never be validated anyway.
- Evidence: `agent_core/turn/engine.py:794-797` (claimed), `agent_core/interpreter/resolve.py:29` (claimed treated as missing), `agent_core/interpreter/handlers/collect.py:28,62`, `agent_core/interpreter/handlers/base.py:49` (rule data uses validated only), `tests/m04/test_start_run.py:88-92` (test only asserts the claimed storage). Spec statement: `docs/specs/motor/m04*.md:282` "`input` de un run task entra como slots `claimed`".
- Related shape friction: a task agent must still declare conversational-only fields (`templates`, `max_clarifications`, `on_clarify_exhausted`, `default_target_queue`: `G0-01 campo obligatorio`), and one release cannot contain both a task and a conversational agent (`AG-01`).
- Impact: a task agent cannot receive parameters at all, so Pulso-style "run this job for subject X with these params" must smuggle them through tool args or the subject.
- Workaround: pass parameters via `subject` + tools reading from our own store; do not rely on `input`.
- Proposed: add an `accepts`/`input_schema` to task agents, validate and store as `validated` (typed, non-string allowed) at `start_run`; add M1 rule "a flow may only read slots written by collect/accepts"; relax conversational-only required fields for `mode: task`.

### F-04 (S2) Read isolation of runs and transcripts is only as good as the consumer's `AuthzPort`

- Repro: demo `serve` (with `SyntheticAuthz`, which returns allowed for everything): `uv run python ac_probes/http_probe.py`: an **advisor without delegation** and an **anonymous principal** both get `200` on `GET /v1/runs/{id}` and `GET /v1/runs/{id}/transcript` of cust-001's run (entries with assistant text). Posting a turn is blocked (`principal_mismatch`), reads are not.
- Expected (defense in depth): a `customer` principal can never read another customer's run regardless of what the port says; anonymous never reads identified runs.
- Actual: `authorize_read` returns early only for the owner, otherwise trusts `authz.authorize_subject(principal, obo, run.subject)`.
- Evidence: `agent_core/api/authorization.py:89-98`. `SyntheticAuthz` lives in `testing/engine_world.py:118`; the only table implementation (`TableAuthz`) lives in `testing/fakes/authz.py:35`, i.e. not in the wheel.
- Not a defect of a correct port, but any consumer that ships a permissive or buggy port silently leaks transcripts (PII). Tenant isolation is also absent at the DB level (single `runs` table, no tenant column; the `principal.key` is the only partition).
- Workaround: our `AuthzPort` denies by default and implements `authorize_subject` strictly; contract test for "customer A cannot read B's run" in our own suite.
- Proposed: hard rule in `authorize_read` for customer/anonymous principals; ship a contract-test suite for `AuthzPort` (`tests/contracts`) that consumers can import; document tenant model.

### F-05 (S2) `agentcore serve` without demo: usability for a non-demo consumer

- Repro: `agentcore serve --port 48111` without env prints 10 problems (good diagnostics). With everything supplied you must pass 7 `module:attr` factories: `--tools --authz --transcript --calibration --classifier --field-classifier --grant-active`, each called with `DemoContext(clock, ids, registry)` only.
- Gaps: (a) the reference implementations of tools executor, authz (`TableAuthz`), transcript (`InMemoryTranscript`) live under `testing/` which is **not packaged** (`pyproject.toml:41 packages = ["agent_core","agent_telemetry"]`) and `_is_test_double` forbids them outside demo; there is **no production TranscriptStore or ToolExecutor** in `agent_core`. A consumer must write them without a contract-test kit. (b) Factories receive no env/DSN/config: they must read process env themselves. (c) `providers` is hard-wired to `{"jev": JevProvider(HTTP), "classifier": <your factory>}`; a different decision provider cannot be registered (`serve_ports.py:271`). (d) `serve` never runs `migrate`; readiness only pings the main DB (`serve_ports.py:277`). (e) `--grant-active` factory returns a bare callable (no grant store port). (f) The error text `falta AGENTCORE_KEYS_FINGERPRINT (demo-secret-env)` calls the production env-key provider "demo".
- Evidence: `agent_core/composition/serve_ports.py:48-56,137-146,271`; `agent_core/adapters/env_keys.py:36`; README line 70 (README itself says the real provider for specialist choice is open).
- Workaround: we do not use `agentcore serve`; Pulso builds `ApiDeps`/`create_app` itself (`agent_core.composition.build_engine` + `create_app`) with its own ports.
- Proposed: ship `agent_core.testing`-style reference ports in the wheel (or a `agent-core-testkit` extra) plus port contract suites; pass a `ServeContext(env, dsn, clock, ids, registry)`; make providers pluggable; add `--limits`.

### F-06 (S2) Rate-limit semantics

- Repro: `uv run python ac_probes/http_probe.py` (tail) and `http_conc.py`.
- Observed semantics: (1) rolling 60 s window, 30 hits per principal; the 30th request is `429 rate_limited` (default `RateLimitConfig`), daily budget 5.00 USD. A "hit" is a `usage` row written by a **committed** turn/run, so idempotent replays, 4xx and GETs do not count. (2) The check also blocks **reads** (`GET /v1/runs/{id}` returned 429) and an **idempotent replay** of an already created run (`POST /v1/runs` with a used key returned 429 instead of the stored result), so a throttled client cannot poll or recover its run id. (3) No `Retry-After` header (`retry-after=None`), `detail` empty. (4) Racy read-then-act: 60 concurrent starts from a fresh principal (plus 12 earlier) allowed 31 more `201` before the first `429`; the limit is a soft cap. (5) Anonymous principals (`principal.id is None`) are never limited ("outside the engine"). (6) Keyed by principal: a `service` principal that acts for many subjects (Pulso backend) shares one 30/min, 5 USD/day bucket. (7) `serve` builds `ApiDeps` without passing `limits`, so none of this is configurable from the CLI/env.
- Evidence: `agent_core/api/limits.py:12-40`, `agent_core/adapters/postgres_uow.py:377-397` (`hits`/`spent_today` from `usage`), `agent_core/composition/serve.py:36-52` (no `limits=`), `agent_core/api/problems.py:46-55` (no headers).
- Workaround: build our own `ApiDeps(limits=RateLimitConfig(...))`; enforce edge rate limiting in the gateway; use distinct service principals per tenant.
- Proposed: return stored result for idempotent replays before limiting; `Retry-After` from window; per-principal-type config (service/builder higher); do not count/limit reads; make the counter atomic; expose limits in `serve`.

### F-07 (S2) Evaluation scenarios cannot model task agents, subjects or principal types

- Evidence: `agent_core/registry/suite.py:38-43` (`Step` has only `op/text/answer/lang/auth`), `agent_core/composition/evaluation.py:91-98` (principal always `"type": "customer"`, `exp = now + 1h`), `:113-117` (`start` builds `RunInput` with only `agent`, `lang`, `idempotency_key`: no `subject`, no `input`), `:119` (`# modo task: el run ya terminó en start`).
- Impact: agents with `subject_kinds`, `invocable_by: [service]` or task mode (and `input`, see F-03) cannot be evaluated faithfully; evaluation also bypasses `RunAuthorizer` because it calls the engine directly, so authz regressions are invisible to the gate.
- Workaround: custom `ScenarioHarness` in Pulso building `RunInput` with subject/input and the right principal.
- Proposed: add `principal.type`, `subject`, `input` and an `authorize: true` option to scenarios.

### F-08 (S2) Registry CLI crashes on Windows after the write committed

- Repro (Windows, default cp1252 console/pipe, no `PYTHONIOENCODING`): `AGENTCORE_ALLOW_DEMO=1 agentcore registry --credential <supervisor> publish <proposal> k1`.
- Expected: JSON of the `ReleaseDetail`, exit 0.
- Actual: the publish **commits** (release `rel-46df1a5633eb49c4` exists, state `published`), then `print(dumps(result))` raises `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'` (the release docs contain a unicode arrow), exit 1, no output. Retrying with the same key crashes the same way; a new key returns `illegal_transition`. A user sees failure for a successful write. With `PYTHONIOENCODING=utf-8` replay works and returns the same release id.
- Evidence: `agent_core/composition/registry.py:166` (print), `:164` (`ensure_ascii=False` on the error path, same hazard for `detail` text with accents/arrows).
- Workaround: always set `PYTHONIOENCODING=utf-8` (or `-X utf8`).
- Proposed: `sys.stdout.reconfigure(encoding="utf-8")` in `main`, or `ensure_ascii=True`.

### F-09 (S3) Registry write idempotency is partial and inconsistent

- Service supports `idempotency_key` for `create_proposal`, `put_draft`, `freeze`, `reopen`, `evaluate` (`agent_core/registry/service.py:265,297,343,368,438`), but neither HTTP (`registry/http.py:105-170`: only `publish` has `Idempotency-Key`) nor the CLI (`composition/registry.py:99-123`: `publish` only) exposes it. Observed via CLI: retrying `draft --rev 0` after success gives `proposal_stale` (409), not the stored result; double `approve` gives `illegal_transition`. `approve`, `reject`, `promote`, `revoke` have no replay semantics at all.
- `publish` key is global (not per actor/proposal) and reuse with another proposal returns `illegal_transition` (`service.py:549`) while `put_draft` uses `idempotency_conflict`.
- Workaround: treat these as at-most-once and read back state (`show`) before retrying.
- Proposed: accept `Idempotency-Key` on all POST/PUT; use `idempotency_conflict` uniformly; make `approve`/`promote` replay-safe when state already matches.

### F-10 (S3) problem+json is not a single contract

Observed live (`http_probe.py`):

| Source | `type` | `title` | other |
|---|---|---|---|
| M9 (`/v1/runs`...) | `urn:agentcore:problem:<code>` | Spanish human title | `detail` string, `trace_id` |
| Registry (`/v1/registry`) | `urn:agentcore:registry:<code>` | equals the code | `detail` Spanish text with free wording, `violations`/`payload`, `trace_id` may be `null` |
| Registry standalone `_creds` handler | missing | missing | only `code,status,trace_id` |
| 405 | `...:invalid_request` with `status=405` | | status/code mismatch (`PROBLEM_STATUS[invalid_request]` is 422) |

`ProblemBody` in OpenAPI requires `detail` and `trace_id` as strings, which the registry bodies can violate. Titles are localized, so clients cannot rely on them. Evidence: `agent_core/api/problems.py:20-40,60-70,87-95`, `agent_core/registry/http.py:62-77,101-107`. Consistent positives: no secret or input value leaked in any problem body or log line (garbage bearer, odd agent text, oversized key, bad JSON; `serve.log` has no echo of the values; security log has code + trace only). Workaround: client parses `code` only. Proposed: one problem builder for both; machine-readable titles or `title` in English; document 405.

### F-11 (S3) Contract drift: OpenAPI vs runtime vs `contracts/`

- `contracts/openapi.json` documents the 7 core paths, but every 2xx response schema is `{}` (script in this section's repro: iterate `paths[*][*].responses`), although `contracts/schemas/RunResult.json` and `TurnResult.json` exist; and HTTP does not publish those shapes (`confirmation` becomes `action_summary`, `step_up.simulated` added, `agent_core/api/schemas.py:73-101`). Clients cannot be generated from the contract.
- The live `/openapi.json` of `serve --registry-api` contains 16 `/v1/registry/*` paths absent from `contracts/openapi.json` (`agentcore contracts --check` still passes because it only checks the registry-less app).
- Versions: `contracts/VERSION` = 1.3.0, OpenAPI `info.version` = 1.0.0 (`api/app.py` `FastAPI(version="1.0.0")`).
- 405 and 503 (`/readyz`) are not documented (readyz is `include_in_schema=False`).
- Workaround: we hand-write response models from `contracts/schemas` and the registry API from the service models. Proposed: type the responses with response models, include extensions in the generated contract, tie `info.version` to `VERSION`.

### F-12 (S3) Registry CLI rough edges

- Bad/expired credential: raw traceback ending in `CredentialsInvalid` (`agent_core/composition/registry.py:152`, verify is outside the `try` at `:160`). No secret appears, but exit code and format are inconsistent with the `RegistryError` JSON path.
- `promote` has no `--reason` (`registry.py:111-114`, `_dispatch` `:196`); service accepts reason (`service.py:603`). A prod promotion can be recorded with an empty reason.
- `evaluate` has no `--suite-version` (HTTP has `suite_version`).
- Documented design (`registry-design.md:11`) allows a human to self-approve their own proposal; consumers needing separation of duties must enforce it outside.

### F-13 (S3) Demo serve identity

`AGENTCORE_ALLOW_DEMO=1` without `--identity-keys` installs the staff verifier as the only principal verifier (`serve_ports.py:252-253`), so customer tokens from `testing.demo_identities` return 401 (observed: first probe run all 401). You must run `python -m testing.demo_identities --public-keys f` and pass `--identity-keys f`. Not mentioned in README's serve section. Also demo credentials have a 10 year TTL (`registry_demo.py` `ttl=timedelta(days=3650)`): fine for a double, dangerous if copied.

### F-14 (S3) `input` accepted on any run

`CreateRunBody.input` is accepted for a conversational agent from a `customer` principal (`201`, observed). The values become `claimed` slots and are exposed in handoff packets as `claimed_not_verified` (`handoff/builder.py:43`). Low impact but surprising; reject `input` unless the agent is `mode: task` (or restrict to service/builder).

### F-15 (S3) `replay --mode audit <run_id>` has no implementation path

`agentcore replay 01a1029b-... --mode audit --registry ...` prints "replay por run_id necesita un almacén de auditoría y el motor: motor no disponible..." and exits with the usage code even though the engine is available and `AGENTCORE_DATABASE_URL` is set; there is no `--dsn` on `replay`. Evidence: `agent_core/cli.py:83-87`. Also `sweep` reads `AGENTCORE_DATABASE_URL` while `serve`/`registry`/`migrate` read `AGENTCORE_REGISTRY_DSN` (`cli.py:57` vs `serve_ports.py:44`): two DSN variables for one database.

### F-16 (S4) Test-suite hygiene

- `tests/composition/test_transfer_spans.py` is flaky on Windows (1 failure in the unit run, 3 in the PG run, different tests each time). It orders spans with `sorted(..., key=start_time)` (`:40`) and compares `start_time >= end_time` (`:64`), which tie at Windows clock resolution.
- Without PG, each of ~100 integration tests spends `connect_timeout=3` trying `127.0.0.1:5432` (`tests/integration/conftest.py:20`): 451 s vs 158 s with PG. Probe once per session.

### F-17 (S4) Docs and packaging

- No `agentcore demo` command; demo pieces are `testing.*` modules and `serve` with `AGENTCORE_ALLOW_DEMO=1`.
- `testing/` is excluded from the wheel but `agentcore record`/`replay` import `testing.replay` (`cli.py:68`) and serve demo imports `testing.*`: those commands work only from a source checkout (the code already degrades with "motor no disponible").
- Repo language is Spanish (errors, CLI text, details); consumers in other locales get untranslatable `detail` strings.

## 4. Checked and found sound

- Secret hygiene: no token or input value in problem bodies or logs for malformed credential, hostile agent selector, oversize idempotency key, non-object input, invalid JSON; `ping`/readiness swallow DB messages; `migrate`/`sweep` print only exception class.
- Sequential idempotency of `POST /v1/runs`: same key+body returns the same run; same key+different body is `409 idempotency_conflict`.
- Principal mismatch on turns, subject spoofing (`403 subject_forbidden`), version pin by customer (`403 version_pin_forbidden`), unknown agent (`404`), expired/garbage credentials (`401`).
- Registry lifecycle on real `PgRegistryStore` through the CLI: import, propose, draft, freeze, evaluate (`pass`), bot approve (`forbidden_role`), human approve, publish, publish replay with same key (same release), promote prod; stale/illegal transitions return typed errors. Immutability triggers and 68 PG integration tests pass.
- `agentcore contracts --check` clean; `validate`, `record`, `replay --mode fixture`, `sweep` run.

## 5. Priority for Pulso

1. F-01 and F-02 first: do not use the stock evaluation harness with a persistent store and serialize `start_run` per key until fixed.
2. F-03 and F-07 shape how Pulso passes parameters to task agents and how we evaluate them.
3. F-05, F-06 and F-04 decide the integration style (own composition root, own limits, own strict AuthzPort).
4. All other items are friction with workarounds listed above.

No issue, PR or push was made to the agent-core repository. No other repo was edited.

## 6. Re-test at `789d6c8` (current `main`, includes N-01..N-11, PR #26, PR #27)

Environment: scratch clone `...\scratchpad\agent-core-new` (detached at `789d6c89...`, `uv sync --locked --python 3.12`), throwaway `postgres:16` on podman connection `pulso-dev` (`--cgroups=disabled`, `127.0.0.1:47419`, name `ac-new-pg-claude`, removed afterwards and verified gone), `agentcore serve --registry-api` on `127.0.0.1:38121` (stopped afterwards). The reference checkout `D:\.codex\factored\references\agent-core` was not touched (still `86a7674`, only the pre-existing untracked `.nexus-outbox/`). No push, issue or PR upstream.

Suite: PG-backed full run `AGENTCORE_TEST_DATABASE_URL=... AGENTCORE_REQUIRE_POSTGRES=1 uv run pytest -p no:cacheprovider -q`: 4174 collected, **4173 pass, 0 fail, 1 skip** (the perf test), no flaky failure this time. `agentcore contracts --check` exit 0. `test_transfer_spans.py` run 6 more times in isolation: 9/9 pass each time (file and its helpers unchanged since the pin).

What changed in code relevant to the pin findings (`git diff 86a7674 789d6c8 --stat -- agent_core`): `engine.py`, `evaluation.py`, `authorization.py`, `limits.py`, `problems.py`, `collect.py`, `registry/suite.py` are **byte-identical**; so F-01, F-02, F-03, F-04, F-06, F-07 are unchanged by construction and were re-run anyway.

| Id | Status | Evidence at `789d6c8` |
|---|---|---|
| F-01 | **still present** | `probe_eval.py`: run#1, #2, #3 all return run `01a1029e-...cee08b` with the same 37 events; with a gateway that always fails run#4 still returns 37 events, `Boom.generate` calls = 1 (only the different-principal run#5 executes and raises `HarnessUnavailable`). |
| F-02 | **still present** | `http_conc_new.py` (fresh principal): `same-key concurrent: Counter({201: 12}) distinct run_ids: 12`. Sequential replay still returns the same run (`replay same run_id: True`), same key plus other body gives `409 idempotency_conflict`. |
| F-03 | **still present** | `probe_task_input.py`: `status/outcome: escalated escalated`, slots `{'cliente': ('demo-1', 'claimed')}`, event `escalated reason=validation_failed`. |
| F-04 | **still present** | `http_probe_new.py`: advisor without delegation and anonymous both get `200` on `GET /v1/runs/{id}` and the transcript of cust-001's run. |
| F-05 | **still present** (one improvement) | Same 7 module:attr factories, `testing/` still outside the wheel (`packages = ["agent_core","agent_telemetry"]`), providers still hard-wired, `serve` still never runs `migrate`. New: `AGENTCORE_DB_POOL_MAX`, `--keys-reload-seconds`, LLM through `AGENTCORE_LLM_GATEWAY_URL/TOKEN` (startup warning if unset). Turns in demo `serve` without `AGENTCORE_JEV_API_KEY` still end as `500 internal_error` (`DecisionConfigError` at request time, not at startup). |
| F-06 | **still present** | 30th `POST /v1/runs` gives `429`, then `replay of idem-1 while limited` gives `429` and `GET /v1/runs/{id}` gives `429`; `retry-after=None`; no `limits=` in `build_api_deps`. |
| F-07 | **still present** | `evaluation.py` and `registry/suite.py` unchanged. |
| F-08 | **still present** | `agentcore registry --credential <supervisor> publish <pid> k1` with default cp1252 stdout: `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'`, exit 1, after the publish committed (`registry.py:169` unchanged). |
| F-09 | **still present** | `registry/http.py` only gained two GET routes; `Idempotency-Key` still only on `publish`. |
| F-10 | **changed (partly)** | Validation errors on registry routes now use `urn:agentcore:problem:invalid_request` (422, `detail` like `body.agent_id: missing`). Domain errors still use `urn:agentcore:registry:<code>` with `title == code` (404 `not_found`, 403 `forbidden_role`), and 405 still maps to `invalid_request` with `status=405`. |
| F-11 | **changed (partly)** | `info.version` now equals `contracts/VERSION` (1.3.0); `contracts/registry/*.json` publishes the registry bodies and models (N-01). Still: all 7 `contracts/openapi.json` 2xx responses are untyped (`{}`), the file has 7 paths while the live `/openapi.json` has 27 (registry plus `/v1/export/*`). `VERSION` was not bumped for the additive registry/export surface. |
| F-12 | **still present** | Bad credential gives a Python traceback ending `CredentialsInvalid`; `promote` and `evaluate` still lack `--reason` / `--suite-version`. |
| F-13 | **still present** | Customer tokens need `--identity-keys` (I passed it; the demo staff verifier path is unchanged). |
| F-14 | **still present** | `POST /v1/runs` by a customer with `input` gives `201`. |
| F-15 | **changed (partly)** | `sweep` now reads `AGENTCORE_REGISTRY_DSN` (legacy `AGENTCORE_DATABASE_URL` still accepted), so the two-DSN problem is fixed. `replay <run_id> --mode audit` still prints "replay por run_id necesita un almacén de auditoría y el motor..." (no DSN option). |
| F-16 | **not reproduced** | See Suite above. Code unchanged, so it may still flake on a slower clock. |
| F-17 | **still present** | No `demo` subcommand (`{contracts,validate,sweep,replay,record,llm-smoke,registry,serve,migrate,blobs-backfill,relay}`); `testing/` still not packaged. |

## 7. New findings introduced by N-01..N-11, PR #26 and PR #27

| Id | Sev | Area | Title | How verified | Status at 894fa65 |
|---|---|---|---|---|---|
| NF-01 | S2 | N-07 | `release_settings` removes interrupts and sets unbounded `max_input_chars` with no extra permission or diff | live (`probe_n07.py`) | **FIXED** |
| NF-02 | S2 | N-08 | Export `run_seq` cursor can skip committed runs; run summaries are never refreshed | live SQL (`probe_n08_seqgap.py`) | **FIXED** (caveats N8-03) |
| NF-03 | S3 | N-08 | Export: no tenant scoping, no read audit, O(n) registry-event paging, PII depends on the consumer's catalog | HTTP live plus code reading | unchanged |
| NF-04 | S3 | N-09 | Hot reload: failures are invisible, partial writes reject valid tokens transiently, I/O under a lock | live (`probe_n09.py`) | unchanged |
| NF-05 | S4 | N-10 | `eval_run_id` only appears on `gate_failed`, not in the pass response | live | unchanged |
| NF-06 | S4 | N-02/N-04 | Small API inconsistencies (`/version` unauthenticated, unknown kind returns 200 `[]`, contract version not bumped) | live | unchanged |
| PR27-01 | S1* | PR #27 | `agentcore sweep` ignores S3 blobs | live (`probe_pr27_sweep_blobs.py`, moto + PG) | **FIXED** |
| PR27-02 | S2 | PR #27 | Outbox relay crashes on a message type it does not know | live (`relay --once`) | **FIXED** (residual N8-05) |
| PR27-03 | S3 | PR #27 | Pool: up to 3 pools per process, readiness bypasses the pool, pools never closed | code reading | unchanged |
| PR27-04 | S3 | PR #27 | S3 blobs: rollback hazard, corruption masked by the fallback, backfill aborts untidily | code reading | unchanged |
| PR27-05 | S3 | PR #27 | Relay: poison message at the head of the queue, advisory-lock leader not revalidated, lock through a proxy | code reading | unchanged |

\* S1 only for deployments that turn on `AGENTCORE_BLOB_BUCKET`; for the rest it is latent.

### NF-01 (S2) N-07: `release_settings` is an unguarded way to remove release-level safeguards

- Repro: `uv run python ../ac_probes/probe_n07.py` from the repo root (in-memory registry `World` from `tests/registry`). A principal with **only** the `constructor` role (type `builder`, no human attribute) calls `put_draft` with `EntityDraft(kind="release_settings", content={"interrupts": [], "max_input_chars": 2000000000})`.
- Observed: accepted (no violation at `freeze`), the fake evaluator passes, a human with `aprobador` approves and publishes. Base had `[('fraude', 100, 'escalate')]` and `max_input_chars=4000`; the published release has `interrupts=[]` and `max_input_chars=2000000000`. The approver's review lists the new `release_settings` content (`{'interrupts': [], ...}`) but not what disappeared relative to the base.
- Cause: `ReleaseSettings.interrupts` "replaces the whole list; `[]` empties it" (`registry/models.py:56`), `max_input_chars` is a bare `PositiveInt`, `put_draft` only requires `require_constructor`, and `platform_edits` only inspects agent metrics and suite thresholds (`registry/validation.py:40-56`). The evaluation gate has no check on interrupts, and the demo suite does not exercise them.
- Impact: the fraud/injection escalation behaviour and the input-size cap (a cost and prompt-stuffing control) become editable by an automated builder; the only barrier is a human approve step that is shown the new value, not the difference. Combined with F-12 (a human holding both roles can self-approve) this is a one-person change to a safety control.
- Workaround: our builder never emits `release_settings`; our review UI diffs `get_release(base)` against the candidate for `interrupts`, `max_input_chars`, `injection_ruleset`, `language_detection`; reject `max_input_chars` above our own limit.
- Proposed: add a change entry (old/new) to `functional_changes`, make platform interrupts non-removable (like `platform_*` metrics), cap `max_input_chars`, require `admin` or a dedicated role to touch `release_settings`.

### NF-02 (S2) N-08: export cursor correctness

- Repro: `uv run python ../ac_probes/probe_n08_seqgap.py` runs the exact export query (`SELECT run_seq ... WHERE run_seq > %s ORDER BY run_seq LIMIT n`, `postgres_uow.py:406`) while transaction A has inserted (took seq 1) but not committed and B inserted and committed (seq 2). Page 1 returns only `race-B`, the consumer sets `next_after = 2`, A commits, page 2 after 2 is empty: `race-A` is never delivered.
- Cause: `run_seq` is `bigserial` (`schema.sql:7`), assigned at INSERT, not at COMMIT. The docstring of `ports/export.py` claims a consumer "se pone al día con dos cursores sin perder nada". The window is the length of the commit transaction (milliseconds), but it is real under concurrent starts.
- Second effect: the cursor orders by creation and `RunSummary` is read from the current `state_json`, so a run exported while `open` is never delivered again when it closes. A consumer that wants outcomes must re-poll by id, or the export needs an update-ordered cursor.
- Checked and fine (live): `after` beyond int64 gives `200` with empty items and echoes the cursor; `limit=0`, `limit=501` and negative `after` give 422 problem+json; unknown run id gives `200 {"items":[],"next_after":-1}` (does not leak existence).
- Workaround: re-read a trailing window (for example the last 1000 `run_seq` values) on every poll and dedupe by `run_id`; refresh status of non-closed runs by id.
- Proposed: cursor on a commit-ordered column or hold back rows newer than the oldest in-flight transaction; add `updated_at` / `state_version` and order by it.

### NF-03 (S3) N-08: export scope and exposure (partly code reading)

- Auth is sound (live): no token, customer, advisor, anonymous, expired all give 401; staff `supervisor` and `constructor_bot` without the role give 403 `forbidden_role` (registry-style problem body, see F-10); `admin` gives 200. It uses the staff verifier only, not the customer gate.
- No tenant scoping: one exporter sees every run and registry event of the deployment (Agent Core has no tenant column, see F-04); the role is global. Fine for one consumer, not for a multi-tenant platform.
- No `Cache-Control: no-store` on export responses (observed `cc=None`), no audit event for export reads, no rate limit.
- Run summary omits principal id, slots and facts (keys are `run_seq, run_id, session_id, release, agent, principal_type, mode, locale, status, outcome, created_at, closed_at`); `session_id` is exported and is the handle customer APIs use. Exported audit events include `tool_called.args` and `result` after the audit view: `pii_direct` fields are masked (`mask(text, tag)`), but `financial`/`public` classes pass in clear (`views/service.py:195-206`), and `run_started.reportable_attrs` goes out as is. So real exposure is decided by the consumer's data catalog. I could not drive a full conversation over HTTP in demo `serve` (turns return 500 without `AGENTCORE_JEV_API_KEY`), so I did not diff real tool payloads. The start-only runs I could produce had no text, no customer id and no card number (the card number I put in `input` of a conversational run did not appear: needle grep negative).
- Performance: `RegistryService.list_events(after, limit)` does `tx.events()[after:after+limit]` (`service.py:693-696`): loads all events and slices on every page, O(n) per request; the offset cursor also assumes the table stays append-only.

### NF-04 (S3) N-09: hot reload edge cases

- Repro: `uv run python ../ac_probes/probe_n09.py` (real `ReloadingIdentityVerifier`, FakeClock, key file with two kids, staff-style `delegation=False`).
  - A writer rewrites the file in place and a reader sees only the first complete line (valid YAML with one kid): the token signed by the other kid is **rejected** until the write completes (next interval in the probe). Atomic rename on the publisher side avoids it; the verifier cannot tell a partial file from an intended one.
  - Truncated mid-key and deleted file: last good keys are kept (good for availability) and `last_reload_error=SchemaError`. But nothing reads `last_reload_error` (no log line, no `/readyz` signal), so a corrupt or missing file is invisible, and a key removed for revocation **stays valid** while the file is broken. Once the file is fixed with the key removed, the token is rejected within the interval.
  - `_current()` reads the file while holding the lock every request takes, once per interval; a slow network filesystem stalls all requests at that moment. `verify` and `grant_active` can see different generations within one request (benign).
- Proposed: log (class only) and expose `last_reload_error` plus the age of the last good load in `/readyz` or `/version`; document atomic-rename publishing; read the file outside the lock.

### NF-05 (S4) N-10: `eval_run_id`

Verified over the CLI with real PG: a failing evaluation returns `gate_failed` with `payload.eval_run_id` (`01a102a4-8df9-7ba7-b95f-44b28a8d1a0c`); the **pass** response is the bare report without `eval_run_id` (the id is available through `GET /v1/registry/proposals/{id}` under `last_eval.eval_run_id`). The idempotent replay path has the same shapes (`_stored_eval`). A failing evaluation still resets the proposal to `draft` with `candidate_hash=None` and `rev+1`, so the consumer must re-freeze before evaluating again. Proposed: put `eval_run_id` in both response shapes.

### NF-06 (S4) Small API items (N-02, N-04)

- `GET /version` is unauthenticated and returns `{"package":"0.1.0","contract":"1.3.0","sha":null}` (`sha` from `AGENTCORE_GIT_SHA`). By design (N-04), but it fingerprints the build for anyone who can reach the port; keep it off any public listener in AWS.
- `GET /v1/registry/aliases/{agent}/{alias}` works for any staff principal including `constructor_bot`; a missing alias and a missing agent both give the same 404.
- `GET /v1/registry/versions/{kind}/{id}` with an unknown kind returns `200 []`, while `GET /v1/registry/entities/zzz/x` returns 404.
- `contracts/VERSION` stays `1.3.0` although `ReleaseDetail` gained required fields (`language_detection`, `max_input_chars`) and about a dozen routes appeared; the ADR on stable surfaces should say whether that is a minor bump.

### PR27-01 (S1 when S3 is enabled) `agentcore sweep` cannot read entities stored in S3

- Repro: `uv run python ../ac_probes/probe_pr27_sweep_blobs.py` (moto S3 plus real PG, fresh DB, `migrate` with `AGENTCORE_BLOB_BUCKET` set, registry-demo imported through the S3 read-through store). Output: `reg_blobs rows: 0 | s3 objects: 26`, `serve-style registry (with blob factory): OK atencion`, `sweeper registry: IntegrityError integrity_error: no existe el contenido f94fef358826...`.
- Cause: `build_sweeper` (`cli.py:187`) calls `PgRegistryStore(lambda: psycopg.connect(dsn, autocommit=False))` with no blob factory, while `serve_ports.py:288` and `composition/registry.py:47` pass `blob_factory_from_env`. After `migrate` detaches the FK and writers stop writing `reg_blobs`, the sweeper only looks in Postgres.
- Impact: abandoned-run cleanup (`sweep --once`, the scheduled task in AWS) fails for runs whose agent version was published after the switch; open runs never get closed. The existing tests do not combine S3 with the sweeper (`test_sweep_cli.py` uses a fake sweeper).
- Fix: `PgRegistryStore(..., blob_factory_from_env(os.environ))` in `build_sweeper`.

### PR27-02 (S2) The relay dies on an unknown outbox message type

- Repro: insert into `outbox` a row whose `message_json` has `"type": "handoff_resolved"`, then `AGENTCORE_EVENTS_TOPIC_ARN=... AGENTCORE_REGISTRY_DSN=... agentcore relay --once`: traceback `ValidationError: 1 validation error for OutboxMessage type Input should be 'handoff_created'`, exit 1. In service mode (`_serve`) the exception escapes the loop, so the task exits and ECS restarts it into the same state.
- Cause: `PostgresOutbox.pending()` does `OutboxMessage.model_validate(...)` on every row and `OutboxMessage.type` is `Literal["handoff_created"]` (`domain/shared.py:65`); `OutboxRelay._relay` returns `"unknown"` for other types but can never be reached. `run_once` only catches `PublishError` / `ValidationError` around projection, not around the read.
- Impact: the first time an engine version writes a new outbox message type, every relay still on the older image stops delivering everything. Mixed versions are normal in a rolling deploy.
- Fix: read `type` as text, skip and count unknown ones (advance past them or dead-letter), keep the strict model only for known types.

### PR27-03 (S3, code reading) Pool behaviour

- `AGENTCORE_DB_POOL_MAX` is applied up to three times per process: `PostgresStore(dsn, pool_max)` for the engine, `_registry_connect(dsn, pool_max)` for the registry and `PostgresStore(eval_dsn, pool_max)` for evaluations, each with `min_size=1`. The documented meaning "conexiones máximas por proceso" is really 2-3x, which matters for the RDS Proxy sizing the ADR is about.
- `/readyz` uses `PostgresStore.ping()`, which still opens a brand-new connection each time (`postgres_uow.py:98`), so readiness stays green while the pool is exhausted and each probe creates a connection through the proxy.
- `open_pool` and `close` exist but `serve` never calls them (lazy open on first request, no close on shutdown). Pool exhaustion raises psycopg `PoolTimeout` after the default 30 s, which surfaces as `500 internal_error` rather than 503. Also check that no UoW holds its connection across an LLM or tool call, otherwise a small `POOL_MAX` can stall turns; I did not test this.
- Positive: `release()` returns the connection and the pool discards one left in a transaction; `tests/integration/test_pool_postgres.py` passes.

### PR27-04 (S3, code reading) S3 blob store

- Rollback hazard: once S3 is on and `migrate` removed the FK, new entity versions exist only in S3. Rolling the image or env back (or any reader without `AGENTCORE_BLOB_BUCKET`, see PR27-01) cannot read them; there is no reverse backfill. The ADR should say rollback needs a reverse backfill or dual writes during the window.
- `ReadThroughBlobStore.get` catches `IntegrityError` from the S3 side, which `verified()` also raises on a hash mismatch, so a corrupt or tampered S3 object silently falls back to Postgres (and fails there with a misleading "does not exist" after the backfill). Corruption should be a distinct, logged error.
- `backfill` runs `verified()` before upload and one corrupt row raises `IntegrityError` out of `run_blobs_backfill` as a traceback (only `psycopg.Error` is caught), aborting the rest; the docstring says it is "rejected".
- No `ExpectedBucketOwner` on S3 calls; SSE-KMS only when a key is configured (otherwise bucket default). Positive: content-addressed keys, verified on read, exceptions carry only the class name.

### PR27-05 (S3, code reading) Relay semantics

- A message that always fails projection (valid type, bad payload) stays at the head of `ORDER BY seq`; with `batch` or more of them `progress == 0` and later messages are never reached. No dead-letter and no attempt counter; the `failed` figure is only the last pass.
- Leader election is a session-level `pg_try_advisory_lock` on a dedicated connection that is never re-checked: if that connection dies silently, another instance becomes leader while the old one keeps publishing (duplicates; consumers dedupe by `event_id`, so tolerated). Through RDS Proxy a session advisory lock pins the connection; the relay DSN should point at the cluster endpoint.
- Positive: marks delivered only after the bus confirms (at-least-once), SNS errors reduced to the class name, SIGTERM finishes the pass, `--once` exit code reflects failures.

## 8. Reproduction index (scripts in `...\scratchpad\ac_probes\`)

`probe_eval.py` (F-01), `probe_task_input.py` (F-03), `http_probe_new.py` and `http_conc_new.py` (F-02/F-04/F-06/F-10), `probe_n08_http.py` and `probe_n08_seqgap.py` (N-08), `probe_n07.py` (N-07), `probe_n09.py` (N-09), `probe_pr27_sweep_blobs.py` (PR27-01); the registry lifecycle and relay repros are the CLI commands quoted above. `env_new.sh`, `idkeys_new.json`, `ids_new.json` hold throwaway test credentials signed with the public TEST keys of the repo (no real secrets).

Not covered: N-01, N-03, N-05, N-06, N-11 beyond the checks above (contract files exist and `contracts --check` passes; `ReleaseDetail` now carries the release-level fields); the PR #26 `HttpLLMGateway` (looked at only through its effect on `serve` wiring and `llm-smoke`); a full conversational turn over HTTP (needs a decision provider).

## 9. Re-test at `894fa65` (current `main`, PR #29 on top of `789d6c8`)

Environment: fresh scratch clone `...\scratchpad\ac894` (checked out at `894fa65575d8...`, `uv sync --locked --python 3.12`), throwaway `postgres:16` on podman connection `pulso-dev` (`--cgroups=disabled`, `127.0.0.1:47521`, unique name `ac894-pg-claude-*`, removed afterwards), `agentcore serve --registry-api` against it. Probes are in `...\scratchpad\ac_probes894\` (ports and token files adapted; tokens regenerated by `gen_ids.py` because the old ones had expired). `D:\.codex\factored\references\agent-core*` untouched. I did not re-run the upstream suite (their PR states green); I ran each repro below.

### 9.1 What actually is on `main` (the team's claim vs the repository)

`git log 789d6c8..894fa65` has exactly one change set: PR #29 (`038f4a8` plus merge `894fa65`). Verified with `git merge-base --is-ancestor <sha> origin/main`:

| PR | Merge commit | Base branch it was merged into | On `main`? |
|---|---|---|---|
| #29 hardening | `894fa65` | `main` | yes |
| #28 JEV through llm-gateway (`POST /v1/jev`) | `3499f94` | `feat/http-llm-gateway` (merged 16:21, after #26 had already merged at 16:11) | **NO** (branch is 2 ahead, 6 behind `main`; `agent_core/decision/providers/jev_gateway.py` does not exist on `main`; `.env.example` and `serve_ports.py:168` still use `AGENTCORE_JEV_API_KEY`) |
| #24 proposals list with filters/pagination | `19e7a10` | `feat/registry-contratos` | **NO** (no `list_proposals` in `registry/service.py` or `registry/http.py`) |
| #23 registry OpenAPI contract and Idempotency-Key on writes | `5705e58` | `ccr-a4781bdb-dnrn7q` | **NO** (`contracts/registry-openapi.json` and `agent_core/composition/registry_openapi.py` do not exist on `main`; `contracts/openapi.json` still has 7 paths, no registry route) |
| #30 e2e agents copiloto/constructor | open (head `527751d`) | `main` | no (open) |

So of the PRs the team listed besides #29, none changed `main`. The Idempotency-Key requirement on registry `publish` (header missing -> 422 `header.idempotency-key: missing`, re-observed live) predates #23 and is what we already had at `789d6c8`.

### 9.2 Re-test results (live)

See the status notes in Section 0; summary: F-01, PR27-01, F-02, F-03, PR27-02, NF-01, NF-02, F-06, F-08 FIXED; F-04 PARTIAL. Other rows in Section 3 not re-run (code unchanged by #29).

### 9.3 New findings and behaviour changes introduced by #29

| Id | Sev | Title |
|---|---|---|
| N8-01 | S2 | #23, #24 and #28 are not on `main` (stacked-PR merge order): retarget or re-merge. Until then the registry OpenAPI contract, the proposals list and JEV-through-gateway do not exist for any consumer pinned to `main`. |
| N8-02 | S3 | `409 idempotency_conflict` now has two meanings (same key with another body; same key still in flight, or held by a crashed attempt for `lease_ttl`, 60 s) with the same code and no `Retry-After`. A consumer cannot tell "retry" from "your key is poisoned". Reserved-but-uncommitted rows are invisible to `get_run_idempotency` (it filters `result_json IS NOT NULL`), so a reconciler reading the table cannot see an in-flight attempt. Suggest a distinct code (`idempotency_in_progress`) plus `Retry-After`. |
| N8-03 | S3 | Export cursor caveats: (a) `limit` counts commits, and after `migrate` every pre-existing run shares one `change_xid` (verified: 5 legacy rows all got the same xid), so the first page after the upgrade returns ALL legacy runs, unbounded; (b) the cursor is bounded by `pg_snapshot_xmin`, so any long transaction anywhere in the database (idle in transaction, a backup, a replication slot) stalls the export for every consumer; (c) pods still on the old version update runs without setting `change_xid`, so closes done by them are not re-exported during a rolling deploy; (d) `ADD COLUMN ... DEFAULT (pg_current_xact_id()...)` is a volatile default, which rewrites the `runs` table under an ACCESS EXCLUSIVE lock (not an online expand on a big table; code reading). Consumers must now upsert by `run_id` (a run reappears when it changes). |
| N8-04 | S3 | New schema pieces are expand-only but not rolling-safe: `run_idempotency.result_json` becomes nullable and `reserved_until` is added; an old pod reading a reserved row calls `RunResult.model_validate(loads(None))` and fails (only for a key being reserved by a new pod at that moment; code reading). Document the deploy order (migrate, then all pods) or make old readers tolerant. |
| N8-05 | S3 | `PostgresOutbox.pending()` skips unknown-type and corrupt rows silently: they stay pending forever, are not counted, do not alert and are not dead-lettered. |
| N8-06 | S3 | Rate-limit in-flight accounting is per process: with N replicas the burst bound is N x max_hits. A `service` principal gets x10 (`AGENTCORE_RATE_SERVICE_MULTIPLIER`), the right shape, but it silently raises the cap for any consumer that uses a service principal on a user-facing path. The knobs are env-only and not echoed at startup. |
| N8-07 | S3 | Release identity changes: `Interrupt` gained `locked` (default false) and the release hash changed for releases that carry interrupts (our `attention-demo` world: `rel-98130317a1003849` before, `rel-da313458b550780a` now; releases without interrupts, e.g. our `pulso-evolution` agents, kept their ids). Anyone who pins release ids or golden hashes must regenerate. The upstream `registry-demo` seed now sets `locked: true` (id `rel-e26df0070f6be82f`). |
| N8-08 | S3 | New M1 rule AG-04 can make previously publishable task flows unpublishable (a flow reads `slots.X` with no `collect`, `input_schema` or `accepts`; verified on our `reg_task` probe at import time). Correct, but it is a validation change inside the same contracts 1.3.0: `contracts/VERSION` was not bumped although the `Agent`, `Interrupt`, `Release`, `ReleaseDetail`, `ReleaseSettings`, `StoredRelease` and `RunSummary` schemas changed (`RunSummary.cursor` is a new REQUIRED field). |
| N8-09 | S4 | `put_draft` accepts `max_input_chars` above the new cap and only freeze rejects it (late feedback). |

### 9.4 Interface changes for consumers (symbols, routes, SQL)

- `ServePorts`: unchanged. `build_api_deps(..., limits: RateLimitConfig | None = None)`: new optional keyword (additive). `create_app` unchanged. New `rate_limits_from_env(env)` in `composition/serve.py`.
- `UnitOfWork` protocol (`ports/uow.py`): two new methods `reserve_run_idempotency(principal, key, body_hash, now, ttl)` and `release_run_idempotency(principal, key)`. Any consumer-side UoW implementation or fake must add them (the bridge uses `PostgresStore` from agent-core, so no change there).
- `RunExport` protocol: `list_runs(after_cursor, limit)` (parameter renamed; commit order; `limit` counts commits); `RunSummary` has a new required `cursor` field and `RunSummary.of(run_seq, state, cursor)`.
- JSON schemas changed (7 files in `contracts/`): `Agent` (`input_schema`), `Interrupt` (`locked`), `Release`, `ReleaseDetail`, `ReleaseSettings`, `StoredRelease`, `RunSummary`; `contracts/openapi.json` unchanged (same 7 paths and route table).
- Registry: `ApprovalReview.release_changes: list[ReleaseSettingChange]` (additive in the proposal review), `put_draft` of `release_settings.interrupts` requires role `admin`, violations `REG-LOCKED` and `AG-04`, `MAX_INPUT_CHARS_CEILING = 100_000`.
- Problem codes: no new code; `EngineError(retry_after=...)` and a `Retry-After` header on 429; `idempotency_conflict` is also used for in-flight.
- SQL (in `schema.sql`, applied by `agentcore migrate`): `runs.change_xid bigint NOT NULL DEFAULT pg_current_xact_id()::text::bigint` plus index `runs_change_idx`; `run_idempotency.result_json` DROP NOT NULL; `run_idempotency.reserved_until timestamptz`. Table-level grants in `local/core/init/12-app-grants.sql` cover the new column (core_app has SELECT/INSERT/UPDATE/DELETE on `runs` and `run_idempotency`); the role that runs `migrate` must own the tables.
- Env: new `AGENTCORE_RATE_MAX_HITS`, `AGENTCORE_RATE_WINDOW_SECONDS`, `AGENTCORE_DAILY_BUDGET_USD`, `AGENTCORE_RATE_SERVICE_MULTIPLIER` (invalid value -> startup exit 2); `sweep` now also needs `AGENTCORE_BLOB_BUCKET` (+ AWS credentials) when blobs live in S3.
- JEV: unchanged on `main` (`AGENTCORE_JEV_API_KEY`, direct `HttpJevTransport`). If #28 reaches `main`: `AGENTCORE_JEV_API_KEY` disappears and JEV needs `AGENTCORE_LLM_GATEWAY_URL` plus `AGENTCORE_LLM_GATEWAY_TOKEN` (the gateway holds `JEV_API_KEY`); without them a JEV call raises `DecisionConfigError`.

### 9.5 Open PR #30 (not on `main`, advisory)

Adds the `copiloto-asesor` and `constructor-chat` agents, `RoutedTools` in `serve --registry-api` (tools `registry/*` go to a `BuilderToolExecutor` with the `constructor-bot` identity), `testing/chat.py`, `scripts/e2e/*` and `fixtures/registry-e2e`. It edits `agent_core/composition/serve.py` but adds no migration. Its own findings worth noting for Pulso: JEV rejects an `interrupt: enum []` schema (500) when a release has no interrupts; `respond(await)` + `collect` loses the user message. Re-run pin-watch when it merges.

### 9.6 Reproduction index at `894fa65`

`ac_probes894\`: `probe_eval.py` (F-01), `http_conc_new.py` and `http_probe_new.py` (F-02/F-04/F-06/F-10), `probe_task_input_new.py` (F-03 with `input_schema`), `probe_n07_new.py` (NF-01), `probe_nf02_new.py` (NF-02: `PostgresRunExport` with a late-committing transaction), `probe_outbox_new.py` (PR27-02), `probe_pr27_sweep_blobs.py` (PR27-01, env set), `gen_ids.py` (fresh tokens), `staffkeys.json`. F-08 verified in-process with a cp1252 `TextIOWrapper`.
