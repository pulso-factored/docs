# Agent Core pin bump 2 analysis: `789d6c8` -> `894fa65` (Claude)

> STATUS 2026-10-04: IMPLEMENTED AND MERGED in improvement-engine#82 (`5ec0530`, 2026-10-03T23:37Z; ADR 0010, dual-pin kept, wire MANIFEST regenerated, F-01 test inverted, in-flight 409 retried within `lease_ttl`). The pin on `main` is `894fa65`. The analysis text below is unchanged history.

Status: ANALYSIS ONLY. Nothing in this document has been implemented, committed or pushed; no repo was modified (scratch clones, venvs and probes live under the session scratchpad and `%TEMP%`). Companion documents: `AGENT_CORE_PIN_FINDINGS_CLAUDE.md` (Sections 0, 3, 7 with the new `Status at 894fa65` column, and Section 9 with the re-test), `AGENT_CORE_RELAY_FOR_USER.md` (what is still open for the Agent Core team).

Date: 2026-10-03. Current pin in our tree: `agent_core@789d6c8` (contracts 1.3.0). Candidate: `894fa65575d83420523f33ec1c6919b8965f7ebe` (`main`, contracts/VERSION still 1.3.0).

## 1. Verdict

Bump to `894fa65` is worth doing and is small, but it is not a no-op: `compat` passes, `gen_wire` fails on a hard-coded release id, 10 wire files change, one of our tests directories (`agent-core-assets`) fails 4 tests, and several mock/runtime behaviours need decisions. pin-watch says `breaking` (exit 30); the real size is "needs-bump-work plus a mechanical regeneration".

The team's message is only partly accurate:

- PR #29 is on `main` and fixes 9 of our 10 findings; F-04 is PARTIAL (customer and anonymous reads fixed; advisors and services are still whatever the `AuthzPort` says). Evidence per item: findings doc Section 0 and Section 9.
- PRs #23 (registry OpenAPI + Idempotency-Key on writes), #24 (proposals list) and #28 (JEV through llm-gateway) are NOT on `main`: they were merged into stacked side branches (`ccr-a4781bdb-dnrn7q`, `feat/registry-contratos`, `feat/http-llm-gateway`) after their parent PRs had been merged. `git merge-base --is-ancestor` is false for all three; the files they add (`jev_gateway.py`, `registry_openapi.py`, `contracts/registry-openapi.json`, `list_proposals`) do not exist at `894fa65`. So JEV still uses `AGENTCORE_JEV_API_KEY` directly and the OpenAPI contract is unchanged (7 paths, no registry route).
- PR #30 is open, adds no migration and touches `serve.py` (see findings Section 9.5).

## 2. What changed between `789d6c8` and `894fa65` (everything is PR #29)

56 files (+953/-91). Consumer-visible:

| Area | Change | Impact on us |
|---|---|---|
| Evaluation | harness key now `eval-<eval_run id>-<label>-<scenario>` | none (our `PulsoScenarioHarness` already uses a per-job key; keep) |
| Run idempotency | `reserve_run_idempotency` / `release_run_idempotency` on `UnitOfWork`; `run_idempotency.result_json` nullable, `reserved_until` added; concurrent same-key request -> `409 idempotency_conflict` | invoke 409 handling and reconciler (section 5.2) |
| Task input | `Agent.input_schema` (task only); slots become `validated`; M1 rule AG-04 | decision on ADR 0004 (section 6); assets validation passes today |
| Release settings | `Interrupt.locked`, REG-LOCKED, admin role for interrupts, `max_input_chars <= 100000`, review `release_changes` | mock fidelity; tools/builder.py default deny can be relaxed later; release ids with interrupts change |
| Authorization | customer/anonymous cannot read other principals' runs regardless of port | none (our `PulsoAuthz` stays) |
| Limits | only spending operations count; `Retry-After`; in-flight reservation; `RateLimitConfig.service_multiplier`; env knobs; `build_api_deps(limits=)`; `rate_limits_from_env` | `main.py:340` passes `RateLimitConfig()`; wire env knobs |
| Export | `runs.change_xid` commit-ordered cursor; `RunSummary.cursor` required; `list_runs(after_cursor, limit)` | our runtime nulls export by default (`PULSO_CORE_EXPORT_ENABLED`); only compat symbol list and docs |
| Outbox | `pending()` tolerant of unknown types | none (we do not run the relay) |
| CLI | `sweep` builds the S3 blob factory; stdout/stderr forced to UTF-8 | none |
| Contracts | 7 schema files changed, `openapi.json` identical, VERSION not bumped | wire regeneration |
| SQL | `schema.sql`: `change_xid` column + index, `result_json` drop not null, `reserved_until` | deploy order and ownership (section 8); our Codex-owned init grants already cover it |

Not changed: `ServePorts`, `create_app`, `ApiDeps` fields (it already had `limits`), route table, problem-code enum, `registry/http.py` (so registry write idempotency semantics are exactly what we integrated at `789d6c8`: `publish` requires `Idempotency-Key`; other writes use the `get_write` readback; no new header behaviour from #23 because #23 is not on `main`).

Our write-key formula (`pulso-w:` keys via `write_key(receipt.idempotency_key, stage, ordinal)` and the `get_write` readback in `adapters.py`) is therefore unaffected. If #23 later lands on `main` and changes the registry write contract, re-check this (`WriteRecord`, readback by idempotency key).

## 3. Our checks against `894fa65`

Tools: pin-watch (`scripts/core/pin-watch/pin_watch.py` run with `--run-tests --include-prs`, output redirected to the scratchpad; the tool needed `PYTHONUTF8=1` because `real_gh` decodes `gh` output with the Windows code page, see section 9), plus manual runs in a scratch copy of `improvement-engine-claude-r` (`git archive HEAD`) against the `894fa65` venv extended with `core-bridge/runtime-requirements.txt`.

| Check | Result |
|---|---|
| `assert_compat()` (PYTHONPATH = scratch checkout + `core-bridge/src`) | PASS. Our 28 closed-list symbols exist with the names we use. It does not look at the new surface (section 5.1). |
| `gen_wire.py` as is | FAIL: `pulso:wire_gen_failed seeded release rel-98130317a1003849 missing` (`core-bridge/scripts/gen_wire.py:158` hard-codes the seed release id; the upstream `registry-demo` seed now sets `locked: true` so its id is `rel-e26df0070f6be82f`). |
| `gen_wire.py` with the id patched in a throwaway copy | PASS, 250 files. Diff vs committed `wire/agent_core@789d6c8`: no added or removed files, `openapi.json` identical (route table unchanged), 10 changed files: `schemas/Agent.json`, `Interrupt.json`, `Release.json`, `RunSummary.json`; `registry/ReleaseDetail.json`, `ReleaseSettings.json`, `StoredRelease.json`; `derived/ProposalDetail.schema.json`, `derived/ReleaseDetail.schema.json`; `golden/hash_vectors.json` (new release id/hash). |
| Non-PG subset: `pytest -c pyproject.toml -k "not pg and not postgres and not integration" tests ../platform-sim/tests` with `TARGET=a2` | PASS: 467 tests, 453 passed, 14 skipped, 0 failed. |
| `TARGET=a2` parity + wire only (`platform-sim/tests/parity tests/wire`) | 165 passed, 2 skipped (`mock_only`; no `contracts/agent_core/pin.json` in the scratch copy). Parity a2 passes because it runs against the platform-sim seed and the recorded fixtures only assert shapes we already have; it does NOT exercise the new behaviours (admin gate, REG-LOCKED, cap, `locked`, `release_changes`, `input_schema`), so a green parity run is not evidence that the mock matches. |
| PG subset: whole `tests ../platform-sim/tests` with `PULSO_TEST_PG_ADMIN` (throwaway `postgres:16`, `pulso-dev`, `127.0.0.1:47521`) | 749 tests: 734 passed, 14 skipped (same 14 as the non-PG run), **1 failed**: `core-bridge/tests/l5/test_collision.py::test_stock_harness_replays_on_a_persistent_eval_db`. That test is our FIRST RED that pins the F-01 upstream defect (stock harness replays one run for base and candidate); it fails now because Core fixed F-01 (`stock harness is expected to replay one run for base and candidate`: the two run ids differ). It is a positive failure; action in WP3: invert it into a regression guard (stock harness no longer replays) and update the docstring/ADR. Nothing else in `core-bridge/tests` or `platform-sim/tests` fails against `894fa65`, including the composed-runtime integration tests on real PG16 and real Core. |
| `agent-core-assets` (`AGENT_CORE_CHECKOUT` -> `894fa65`): `assetcheck.py check` and `validate` | PASS. `agentcore validate` on both worlds: no violations (so AG-04 does not hit our four task agents: they read `facts.binding.*`, never `slots.*`). |
| `agent-core-assets/tests` with the new checkout | 18 passed, 4 failed (all in `test_agentcore_tier.py`): pin SHA assertion (expected), "attention-demo is the pinned fixture" (our copy of `registry-demo/releases/demo.yaml` is no longer byte-identical: upstream added `locked: true`), `state_matches_expected_state` and `in_memory_import_semantics` (expected-state.json: `attention-demo` release id `rel-98130317a1003849` -> `rel-da313458b550780a`, plus `ReleaseDetail` content now has `locked`; the four `pulso-evolution` release ids are unchanged). |
| `pin-watch` verdict | `breaking` (exit 30): signature signals for `serve.py`, `ports/export.py`, `ports/uow.py`; 7 schema files; 4 new env vars; problem-code change. All explained above; none is a removed symbol we use. |

## 4. Which of our workarounds can be simplified or removed (list only, nothing done)

Verification gate for each: re-run the item's repro on the final bumped stack (PG + real Core) before touching code.

| # | Workaround | Where | Can it go? | Honest assessment |
|---|---|---|---|---|
| W1 | Per-job unique run `idempotency_key` and own harness | `harness.py` | KEEP | Upstream fixed the stock key, but our harness also does sealed task input, budget metering, snapshot-only registry, `HarnessUnavailable` mapping. The "never use the stock harness with a persistent store" rule in our docs can be softened. |
| W2 | Default-deny of `release_settings` drafts in the writer | `tools/builder.py:161`, ADR 0003 | RELAX LATER | Core now gates interrupts behind `admin`, caps `max_input_chars`, shows `release_changes` and supports `locked`. We could allow the non-interrupt fields (`max_input_chars`, `language_detection`, `injection_ruleset`) for the constructor bot. Do not do it before (a) our mock enforces the same gate and (b) `seed` marks the platform interrupt `locked`. Default deny costs nothing; keep until a product need appears. |
| W3 | `bind_context` re-exposes run inputs as `facts.binding.value.*` | ADR 0004, `tools/bind.py`, `stages/catalog.py` | KEEP (assessment below) | Section 6. |
| W4 | Own `RateLimitConfig()` and no use of Core's env knobs | `main.py:340` | SIMPLIFY | Replace with `rate_limits_from_env(env)` so operators can tune; behaviour improves (reads and replays no longer count). Keep our principal type (`builder`), so no x10 multiplier applies. |
| W5 | Own read-only exporter instead of `/v1/export/*` | `exporter/` | KEEP | N-08 is fixed for the cursor but NF-03 (no tenant scoping, no read audit) stands; Core's export is also nulled by default. |
| W6 | Own strict `PulsoAuthz` | `factories.py` | KEEP | F-04 is only PARTIAL; also builders and services are never covered by the new hard rule. |
| W7 | In-process single-flight per `(tenant, key)` in the invoke service (`_live`) | `invoke/service.py` | KEEP | Cheap and works across nothing but one process; Core's reservation is the cross-replica backstop. Keep both; map the new 409 correctly (5.2). |
| W8 | UTF-8/`PYTHONIOENCODING` handling when scripts call the registry CLI (if any) | scripts | CHECK | I found none in `core-bridge/scripts`, `scripts`, `local`, `e2e-core`; if Codex's scripts set it for `agentcore registry`, it is redundant after F-08. |
| W9 | Per-job eval storage (own schema) | `registry_service.py`/`evaluation/` | KEEP | Isolation property, not only the F-01 workaround. |
| W10 | Documentation that `claimed` slots are by design and "Core validation of run-input slots is NOT to be expected" | ADR 0004 / 0008 | UPDATE | Now outdated: Core added `input_schema` (opt-in). |

## 5. What breaks or needs work, exactly

### 5.1 Compat and symbols (`core-bridge/src/pulso_core_runtime/compat.py`)

Passes unchanged. Suggested additions so future drift is caught (not required for the bump): `agent_core.api.limits.RateLimitConfig` fields incl. `service_multiplier`; `agent_core.composition.serve.rate_limits_from_env`; `Agent.input_schema` and `Interrupt.locked` as field checks; `agent_core.registry.candidate.locked_interrupt_violations`; `agent_core.registry.models.MAX_INPUT_CHARS_CEILING`; `UnitOfWork.reserve_run_idempotency`; `RunSummary.cursor`; change `build_api_deps` required names to include `limits` only if we start passing it.

### 5.2 Invoke path and reconciliation (L3a)

1. `invoke/service.py::_after_response`: any 409 from Core is mapped to `manual_reconcile` with reason `core_idempotency_conflict` and HTTP 409 `pulso:digest_conflict` ("Core saw this key with another body"). After #29 a 409 can also mean "same key, same body, still in flight (or a crashed first attempt holds the reservation for `lease_ttl` = 60 s)". Today that would park a healthy job in `manual_reconcile`. Action: distinguish by the problem `detail` ("otra petición con esta clave sigue en curso") or, better, ask the team for a distinct code (relay item). Interim: treat "in flight" as `unknown` (retry/reconcile later) rather than `manual_reconcile`.
2. `reconcile/reconciler.py::_reconcile` reads `get_run_idempotency` first. A reserved-but-uncommitted row is invisible (query filters `result_json IS NOT NULL`), so the reconciler can fall to "never sent"/"sent_without_binding" while the original attempt is still running. Action: do not conclude "no effect" before `receipt.sent_at + lease_ttl + margin`; use `PgRunReader` plus a direct check of `run_idempotency.reserved_until` if needed.
3. Same-key concurrency from our own side is now safe at Core; the single-flight guard stays.

### 5.3 Runtime composition (L2)

`main.py`: use `rate_limits_from_env(env)`; keep the dataclass replace. `readiness.py` and `factories.py`: no change. Remember Core's `sweep` job (if we run one) needs the same `AGENTCORE_BLOB_BUCKET` env as `serve`.

### 5.4 Wire, mock, assets

- `core-bridge/scripts/gen_wire.py`: replace the hard-coded `rel_id` with the id derived from the seeded release (or read it from the generated seed), so it stops needing an edit on every pin; regenerate `core-bridge/wire/agent_core@894fa65/**` (10 changed files), add `contracts/agent_core/pin.json`, write ADR 0010.
- `platform-sim`: the old release id appears in `registry_mock/sim_common.py`, parity tests (6 hits), `bridge_contract` test, and `fixtures/agent_core_wire/789d6c8/*.json` (dozens of recorded fixtures). Re-record with `platform-sim/tests/parity/record.py --target real` (needs PG) into a `894fa65` directory; then check the mock still matches. New mock behaviours needed for fidelity: `Interrupt.locked` in release detail output; admin-only `interrupts` in `release_settings` (`forbidden_role`); `max_input_chars` cap (freeze `validation_failed`); REG-LOCKED; `ApprovalReview.release_changes`; `Agent.input_schema` field and AG-04 on import/freeze.
- `agent-core-assets/expected-state.json` and the `attention-demo` fixture copy must be regenerated (4 failing tests, section 3). Optional separate decision: add `input_schema` to the four task agents (changes their entity hashes and release ids).

## 6. The `claimed` slots decision (ADR 0004): honest assessment

What changed: Core now lets a task agent declare `input_schema: {slot: {type, required}}` (types `string|integer|decimal|date|boolean`). `start_run` validates the input against it (`missing_required_slot`, `slot_not_accepted` for undeclared names, `slot_type_mismatch`) and stores the slots as `validated`. Without it nothing changed: the slot stays `claimed`, flows reading it escalate, and AG-04 now rejects such a flow at publish. I verified all three paths live (`probe_task_input_new.py`).

Can `bind_context` facts be removed? Technically the input-exposure role could be replaced: our inputs are refs and one boolean, which fit the allowed types, `slot_not_accepted` equals our `unknown_input_slot` check, and `agentcore validate` would enforce AG-04. But I recommend NOT removing it, for these reasons:

1. `bind_context` also carries the binding gate: facts exist only after the binding callback is confirmed, so a denied binding means the model is never reached (ADR 0004 item 5). Validated slots exist from `start_run`, before any binding proof. Removing the facts removes that gate unless we re-implement it elsewhere.
2. It also provides `binding_state`, `tenant_id`, `job_id` and the stage flags as tool-origin facts; slots are not facts and are not calibrated.
3. Every Flow and asset (L4) and the CI catalogue check (`stages/catalog.py::check_against_assets`) depend on `facts.binding.*`; migrating changes all four stage assets, their hashes and release ids, and invalidates recorded goldens.
4. Slot values would become visible to flows through a path we do not control (`validated` slots are readable by M1 rules and templates).

Possible low-risk use of the new feature: declare `input_schema` on our four task agents as defense in depth (Core rejects malformed inputs before any effect), while keeping `bind_context`. That is an asset change for a later decision, not part of this bump. Update ADR 0004's last paragraph (W10) either way.

## 7. Ordered bump plan (disjoint work packages)

Pre-step (user/Codex, no code): decide to bump to `894fa65` now (recommended; JEV is unchanged so nothing about the llm-gateway changes) and send the relay (open items) to the Agent Core team. If #23/#24/#28 land on `main` later, treat them as a separate pin-watch cycle.

| WP | Owner | Paths (disjoint) | Depends on | Content |
|---|---|---|---|---|
| WP1 pin + wire | Claude (L1) | `core-bridge/scripts/gen_wire.py`, `core-bridge/wire/agent_core@894fa65/**`, `contracts/agent_core/pin.json`, `core-bridge/docs/adr/0010-*.md`, `core-bridge/tests/wire/**` | none | derive rel id instead of hard-coding; regenerate wire; update pin; ADR |
| WP2 mock + parity | Claude (L1) | `platform-sim/**` | WP1 | re-record fixtures at `894fa65` (real PG), update id constants, add the mock behaviours in 5.4, parity a2 and real |
| WP3 runtime | Claude (L2/L3a) | `core-bridge/src/pulso_core_runtime/{compat,main}.py`, `invoke/service.py`, `reconcile/reconciler.py`, `core-bridge/tests/l5/test_collision.py`, matching tests | WP1 | 5.1 symbols, 5.2 409 and quarantine, 5.3 rate limits env, invert the F-01 RED test |
| WP4 assets | Claude (L4) | `agent-core-assets/{expected-state.json,worlds/attention-demo,tests/**}` | WP1 | regenerate expected-state; refresh the byte-identical fixture copy; optional `input_schema` decision |
| WP5 infra/ops | Codex | `local/compose.yaml`, `core-bridge/Dockerfile`/build args, `.github/workflows/*`, `e2e-core/**`, infra ADR 0003 | none | see section 10 |
| WP6 verification | Claude | scratch only | WP1-WP4 | PG subset + integration + e2e on the final stack; re-run `pin-watch` expecting `additive-safe` or `needs-bump-work` with an empty drift list |

WP2, WP3 and WP4 are parallel after WP1. WP5 is independent and should start now.

## 8. Risks

1. Export cursor (only if we enable `/v1/export`): first page after migration returns all legacy runs; any long transaction in the DB stalls it; mixed-version writers; table rewrite on `ALTER`. Mitigation: keep export nulled; deploy order: migrate (owner role) then all pods.
2. 409 semantics (5.2): without WP3 a retry storm or a manual_reconcile pile-up is possible under timeouts.
3. Mock fidelity: parity a2 green does not prove the mock enforces the new rules; risk of divergence between sim and Core in tests that rely on interrupts/limits.
4. Release ids: any consumer pinning `rel-98130317a1003849` (platform-sim fixtures, expected-state, golden hashes) breaks silently or loudly; the Rust side (`crates/*`, Codex) must not hard-code ids (I did not search `crates` beyond file-level grep; ask Codex to confirm).
5. `contracts/VERSION` was not bumped despite schema and validation changes: our contract-drift job keys on SHA, not on VERSION.
6. #23/#24/#28 may land on `main` soon and change registry OpenAPI, proposal listing and JEV env; plan a second small bump rather than waiting.
7. Rate limiting defaults: `RateLimitConfig()` default 30 per 60 s per principal and 5 USD/day apply to the invoke principal; verify throughput of parallel stages before enabling real LLM cost.
8. Local tooling: pin-watch defects (section 9) can produce a false `tests: fail`.

## 9. Tests and commands (reproducible)

```text
# venv for the new SHA (pin-watch builds %TEMP%\pulso-wire-venv-894fa65), then:
uv pip install --python %TEMP%\pulso-wire-venv-894fa65\Scripts\python.exe -r core-bridge\runtime-requirements.txt
$env:PYTHONUTF8=1
python scripts/core/pin-watch/pin_watch.py --json --run-tests --include-prs --out-dir <scratch>\out --state-file <scratch>\state.json --scratch-root <scratch>\sr
# non-PG (from a copy of core-bridge):  TARGET=a2 python -m pytest -c pyproject.toml -p no:cacheprovider -k "not pg and not postgres and not integration" tests ../platform-sim/tests
# PG: same with PULSO_TEST_PG_ADMIN=postgresql://...@127.0.0.1:<port>/agentcore (throwaway postgres:16 on pulso-dev, --cgroups=disabled, removed after)
# gen_wire (needs a shadow dir containing contracts/agent_core/pin.json with the new sha, as pin-watch does):
python <shadow>/core-bridge/scripts/gen_wire.py --checkout <ac894> --out <dir> --expected-sha 894fa65575d83420523f33ec1c6919b8965f7ebe
# assets: AGENT_CORE_CHECKOUT=<ac894> python agent-core-assets/tools/assetcheck.py check|validate ; pytest agent-core-assets/tests
```

Two defects in the pin-watch tool itself (not fixed, tool is outside this task): (1) `real_gh` decodes `gh api` output with the Windows code page and crashes on a UTF-8 byte in a PR file list (workaround `PYTHONUTF8=1`, fix `encoding="utf-8"` in `subprocess.run`); (2) `--run-tests` builds the new-SHA venv with `uv sync --locked` only, which lacks `jsonschema`/`referencing` (our `runtime-requirements.txt`), so the first collection error stops the run and reports `tests: fail` (fix: install `core-bridge/runtime-requirements.txt` into the checks venv). The report's `tests: fail` in section 3 was this tool artefact; the real results are the manual runs above.

## 10. What Codex must be told

1. Pin moves `789d6c8` -> `894fa65` (contracts 1.3.0, unchanged VERSION). Update every place that names the SHA or the build arg: `core-bridge/Dockerfile` build args, `.github/workflows/*`, `local/compose.yaml` (if it pins), `e2e-core/src/codex_standin/stack.py`, infra ADR 0003 pin text (relay item B7).
2. New optional env on the Core/runtime workload: `AGENTCORE_RATE_MAX_HITS` (default 30), `AGENTCORE_RATE_WINDOW_SECONDS` (60), `AGENTCORE_DAILY_BUDGET_USD` (5.00), `AGENTCORE_RATE_SERVICE_MULTIPLIER` (10). Invalid values make startup exit 2. If a sweep job exists it needs `AGENTCORE_BLOB_BUCKET` and AWS credentials exactly like `serve`.
3. Database: `schema.sql` adds `runs.change_xid` (volatile default, table rewrite on first ALTER), `run_idempotency.result_json` nullable and `reserved_until`. Run `agentcore migrate` with the table-owner role before the new pods; `core_app` grants in `local/core/init/12-app-grants.sql` need no change. Avoid long idle-in-transaction sessions if export is ever enabled.
4. Idempotency: Core now answers `409 idempotency_conflict` to a same-key request that is still in flight; clients must retry, not give up. Any Rust/Control-plane caller of Core run creation must handle it (our bridge will, WP3).
5. Hard-coded release ids: `rel-98130317a1003849` becomes `rel-da313458b550780a` for the attention-demo world (any release with interrupts changes id); please confirm no `crates/*` code or Rust fixtures embed old ids.
6. No change to routes, ports, auth, JEV (still `AGENTCORE_JEV_API_KEY` on `main`) or the llm-gateway integration. Do NOT plan on #28/#23/#24 until they are on `main`.
7. Heads-up for the Windows runner scripts: the registry CLI now forces UTF-8 output, so `PYTHONIOENCODING` workarounds can be dropped after verification.
