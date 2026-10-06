# Agent Core pin bump 3 analysis: `894fa65` -> `c814c2b` (Claude)

> STATUS 2026-10-04: IN PROGRESS (being finished by another agent). Local branch `claude/r4-pin-c814c2b` (worktree `improvement-engine-claude-a`) has `e55f7a8` (`synthesise_args` from the real serve-parser defaults, the WP1 fix) and `a44003e` (pin constants, wire with only MANIFEST changed, bridge-contract, fixtures, ADR 0012). No GitHub PR exists yet (`gh pr list --head claude/r4-pin-c814c2b` is empty at 2026-10-04T01:15Z); improvement-engine `main` (`83516eb`) still pins `894fa65`. Note: the ADR proposed here as 0011 is now 0012, because #86 took 0011 for the Annex D alignment. Agent-core `main` is still `c814c2b` (no newer commits).

Read-only analysis. No repo code changed, `references\agent-core` untouched, no `references\agent-core-c814c2b` created yet,
no containers used. Scratch: clone of agent-core at `c814c2bad9f154d10c092326558815dca9562be7` and a `git archive` of
improvement-engine `origin/main` (5ec0530) under the session scratchpad; venv `%TEMP%\pulso-wire-venv-c814c2b` (reusable
for the bump; `core-bridge/runtime-requirements.txt` + pytest installed in it).

## 1. Verdict

**Bump, but it is not a pure pin change: one small code fix is mandatory.** The wire is byte-identical, but
`synthesise_args` (core-bridge `main.py`) builds an `argparse.Namespace` by hand and the new `resolve_ports` reads
`args.lang_thresholds` unconditionally, so the real runtime would die with `AttributeError` at startup on `c814c2b`.
Neither `assert_compat` nor the non-PG tests catch it (they stub `resolve`); only the PG/real-Core tests
(`tests/integration/conftest.py`, `tests/l3a/test_real_core.py`) would. Repro (no PG needed):
`Namespace` from `synthesise_args` -> `serve_ports._lang_thresholds(ns, {}, [])` -> `AttributeError: 'Namespace' object has no attribute 'lang_thresholds'`;
with `lang_thresholds=None` it returns `{}` (feature off). Worth doing now: it is cheap, and the bump is the moment the
fix is testable; the fix is dual-pin safe (an extra Namespace attribute is ignored by `894fa65`).

## 2. What changed upstream (`894fa65..c814c2b`, 6 commits, all PR #30)

97 files. Under `agent_core/` only 3 files: `composition/{builder_tools,serve,serve_ports}.py` (+65/-4). Everything else is
`scripts/e2e`, `testing/{chat,demo_identities,e2e_demo}.py`, docs, tests and `tests/fixtures/registry-e2e/**`.
`contracts/`, migrations, `api/`, `registry/`, `domain/`, `uv.lock`, Dockerfile: untouched.
- `serve_ports.py`: new `--lang-thresholds FILE` / `AGENTCORE_LANG_THRESHOLDS` (JSON `{thresholds_from: LangThresholds}`),
  new `ServePorts.lang_thresholds` field (default `{}`), new `_lang_thresholds(args, env, problems)`; a broken file is a
  config problem (not silent). Without it language switching by detection stays off (threshold 1.0).
- `serve.py`: `build_api_deps` passes `EngineConfig(lang_thresholds=ports.lang_thresholds)` (`EngineConfig` already had the
  field); `run_serve` (only) wraps `ports.tools` in `RoutedTools(BuilderToolExecutor(registry_service, constructor_bot(clock), ids), ports.tools)`
  when the registry API is on; new `constructor_bot()` principal.
- `builder_tools.py`: adds class `RoutedTools` (routes `registry/*` to the builder executor, the rest to the deployment
  tools). `BuilderToolExecutor`, `BUILDER_TOOL_DEFS` and the 10 tool defs are unchanged.

## 3. Our checks against `c814c2b` (pin-watch from the scratch copy, `PYTHONUTF8=1`, `--run-tests`)

- pin-watch verdict `needs-bump-work` (exit 20). Its "signature_change removed" for serve.py / serve_ports.py is a
  heuristic false positive (lines were edited, no pinned signature changed); the "new_env_var" hits in `scripts/e2e/*` are
  upstream-only.
- `assert_compat()`: pass. `gen_wire.py`: pass, 250 files. `wire_diff`: clean: **0 schemas / registry / events /
  derived / golden hash vectors / openapi changed, 0 routes added or removed**. The only byte difference to the committed
  `wire/agent_core@894fa65` is in `MANIFEST.json`: the two sha fields (lines 1028 and 1030).
  New MANIFEST digest for `contracts/agent_core/pin.json`: **`68f335f27cae0fa713c90537066bdc1d88b595e417312f75ca1cb967bffb876a`**
  (the 894fa65 digest was `ed000b81...809b5`).
- Non-PG core-bridge tests vs c814c2b: pass (first run failed only because the fresh venv lacked `jsonschema`; after
  installing `runtime-requirements.txt` all green, 4 skip groups as before). PG tests not run (see 1: the real
  `resolve_ports` path is the one that would fail).
- `agent-core-assets`: `assetcheck.py check` ok and 21 of 22 tests pass; the one failure is `test_checkout_is_the_pin`
  (expects 894fa65), i.e. exactly the pin constant. Release ids unchanged (seed untouched), so `expected-state.json` and
  `manifest.yaml` digests stay; only the `pin.sha` fields move.

## 4. Impact on our consumer side

- **Bridge / `main.py`**: only the `lang_thresholds` Namespace issue above. Optional follow-up (our call, not Core's): expose
  `PULSO_LANG_THRESHOLDS` -> `Path` in `synthesise_args` and check `app.state`/limits like the rate-limit knobs; the
  pulso-evolution `language_detection` asset (`lang-evolution`) currently runs with detection-driven switching off, the same
  as before. Keep `None` for the bump and decide the feature separately.
- **`RoutedTools` / builder tools in serve**: do not apply to us. Our `main` does not call `run_serve`; it composes
  `resolve_ports` + `build_api_deps` itself and wires our own `PulsoToolDispatcher` with `ProtectedBuilderToolExecutor`
  (own `BuilderToolExecutor(service, actor_for(ic), ids)`). `BuilderToolExecutor` and `BUILDER_TOOL_DEFS` (both used by
  `tools/{factory,builder,dispatcher}.py`) are byte-identical in behaviour. Not adding `RoutedTools` or `lang_thresholds` to
  `compat.PIN_SYMBOLS` keeps `assert_compat` valid on both pins (same dual-pin rule as ADR 0010 #3).
- **Registry client / release_settings / PinnedRegistryPort / registry service**: nothing changed (no `registry/` or
  `api/` diff; `RELEASE_SETTINGS` and `ReleaseSettings` untouched).
- **Image / compose**: `core-bridge/Dockerfile` already has `CORE_SHA=894fa65...` ARGs (twice, lines 9 and 25), plus
  comments in `local/core/compose.core.yaml` and references in `local/core/{doctor,smoke}.ps1`, `lib/evidence.ps1`,
  README and tests: mechanical sed. No new env var the runtime needs; Core's `AGENTCORE_LANG_THRESHOLDS` is optional.
- **E2E fixtures (`tests/fixtures/registry-e2e`)**: 5 real agents (`recepcion`, `consultas`, `disputas`, `copiloto-asesor`,
  `constructor-chat`), 5 flows, 24 templates, 10 tools, 5 releases, calibration `cal-transfer-demo`, plus a builder agent
  that calls the 10 `registry/*` tools. Agent ids do not collide with ours (`atencion`, `pulso-*`). **Entity collisions if
  both were loaded into one registry** (same id@version, different bytes, so an immutable-digest conflict):
  `decision_models/{match-cargo@2.0.0,understand-turno@1.0.0}`, `language_detection/lang-es-pt@1.0.0`,
  `model_profiles/perfil-generacion@1.0.0`, `prompts/p/resumen_radicado@1.0.0`, and all 10 `tools/registry/*@1.0.0`
  (these differ from our pulso-evolution `registry` defs). 17 attention-demo files are byte-identical. Usefulness for us:
  low-moderate. They are tuned for the Spanish/Portuguese PQR demo against a real JEV/LLM gateway (`scripts/e2e`), not for
  our task stages, and `constructor-chat` relies on Core's `RoutedTools` path which we do not use. Reasonable use: read-only
  reference for a multi-agent routing example (`recepcion` -> specialists) and for the `registry/*` tool-call shape; do not
  import them next to our worlds. If ever loaded into a Core of ours, use a separate registry/namespace.

## 5. Ordered work packages (bump)

1. **WP1 (core-bridge, Claude, 1 PR):** RED test first: `synthesise_args(...)` namespace passes real
   `serve_ports._lang_thresholds` (fails on c814c2b, passes on 894fa65 and c814c2b after the fix); add `lang_thresholds=None`
   to `synthesise_args`. Move `PIN_SHA` (`__init__.py`), `gen-wire.ps1`/`ci.ps1`/`build-image.ps1`/`prepare-core-context.ps1`
   constants, `gen_wire.py` fallback, `expand_contract_worker.py`, the ~47 files that carry the sha (tests/wire, l3a, l5,
   runtime, integration; `OLD=894fa65`/`NEW=c814c2b` in `test_expand_contract`, no schema change so trivial), regenerate
   `wire/agent_core@c814c2b/` (250 files, only MANIFEST differs; `git mv` the dir), new ADR 0011 (dual-pin kept, MANIFEST
   digest above), journal entry. Run full `core-bridge/tests` on PG16 (pulso-dev, `--cgroups=disabled`, 127.0.0.1) in the
   `c814c2b` venv.
2. **WP2 (platform-sim / mock):** none required. Wire and routes are identical, so `fixtures/agent_core_wire/` need no
   re-record; only rename/pin strings if a test asserts the sha.
3. **WP4 (assets):** change `pin.sha` in `manifest.yaml`, `tests/conftest.py`, `tools/assetcheck.py`, README; rerun
   `assetcheck.py write-state` (digests expected unchanged; `release_ids` unchanged).
4. **WP5 (Codex):** `core-bridge/Dockerfile` `CORE_SHA` ARGs, `local/core/*` references, workflows' pinned checkout,
   `e2e-core/src/codex_standin/stack.py`, `contracts/agent_core/pin.json` (sha + MANIFEST digest `68f335f2...b876a`),
   `references\agent-core-c814c2b` checkout (create with `git clone` from the scratch clone and `git checkout c814c2b`).
5. Not needed: new `PIN_SYMBOLS`, runtime logic changes, mock fidelity work.

## 6. Risks

- Hand-built `Namespace` is a recurring fragility: any new `args.<x>` read upstream in `resolve_ports` breaks us silently
  until PG tests run. Consider making `synthesise_args` start from the real parser defaults
  (`add_serve_parser` -> `parse_args([])`-style) in WP1 so future flags default correctly; this is the real fix, the
  one-line attribute is the minimum.
- Rollback to 894fa65 is safe (no schema/data change, wire identical).

## 7. For the user to relay to the agent-core team (not the shared journal)

1. `resolve_ports` reads `args.lang_thresholds` with attribute access; embedders that build `Namespace` by hand (we do) break.
   Ask for `getattr(args, "lang_thresholds", None)` (tolerant) or a documented minimal args contract. This has the same shape
   as earlier ServePorts additions.
2. Ask whether `RoutedTools` / constructor service principal in `run_serve` is meant to become reusable (a public
   `compose_builder_tools(ports, registry_service)` helper) for embedders that do not call `run_serve`; otherwise we keep our
   own protected builder composition and nothing is needed.
3. Fixture hygiene: `registry-e2e` reuses ids/versions of `registry-demo` (`match-cargo@2.0.0`, `understand-turno@1.0.0`,
   `lang-es-pt@1.0.0`, `perfil-generacion@1.0.0`, `resumen_radicado@1.0.0`) with different content; confirm they are only
   ever loaded in separate registries (immutable digests).
4. Still open from bump 2 (unchanged): distinct problem code for the in-flight `idempotency_conflict` (we match the text
   `sigue en curso`).
