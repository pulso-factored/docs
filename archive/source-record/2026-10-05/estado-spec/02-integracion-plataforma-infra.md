# 02 - Integration / platform / infra boundary vs spec V3 (improvement-engine main 41492cb, infra main dab52ab)

## Method
- Code truth: read-only worktree `improvement-engine-main-ro` (41492cb; PR bodies #76/#88-#91 via `gh pr view`) and infra via `git show origin/main:path` after a fresh fetch (`dab52ab`, equals `gh api` head). Nothing was executed here: test counts are PR-body claims (all "local validation", PG16 on Podman, GitHub Actions budget exhausted; hosted `rust-ci` is red on every recent main commit and its logs return 404). I verified by reading code that each cited component exists, not that its tests pass.
- Starting point `ESTADO_IMPLEMENTACION_CLAUDE_2026-10-03.md` (written at main 83516eb) was re-checked: main has since moved (PR #91 pin c814c2b, Codex #88 OTel, #90 ValueModel kernel). Its Python-half claims hold; its "implemented and merged" list for CAP-24..32/47..52/58..61/63 hides that the Rust half of most of them does not exist.
- Status codes per rubric. For every CAP the Python/bridge half and the Rust half are shown separately. Rule used: PARTIAL = Python half done, Rust consumer TODO; STANDIN = only a double or a domain-level Rust fragment that does not speak the Core wire. Blocked-by-decision CAPs (23, 41, 44, 62) count as TODO and a second % excludes them.
- Caveat on every DONE: no Python/console/Terraform-module suite runs in any GitHub workflow. `.github/workflows/ci.yml` on main is Rust-only (plus a Python unittest contract-fixture step and Pester). core-bridge, platform-sim, e2e-core, bridge-contract and debug-console run only via local scripts (`core-bridge/scripts/ci.ps1`). DONE here means "implemented on main, green in the author's local run per PR body, with real PG16 and a real built Core image where stated", not "green in CI".
- Denominator: 16 units (U24, U25, U28, U32, U37-U48) + 64 CAP + 11 section-32 items (PL-L1..L6, PL-C1,C2,C4,C5,C6; PL-C3 deferred) + 10 PL-01..10 first-RED + 14 section 26/4.1/10 items = 115.

## What was actually exercised with real dependencies
- Real: PG16 (Podman `pulso-dev`, `PULSO_TEST_PG_ADMIN`); a locally built `pulso-core-runtime:<core7>-<pulso7>` image from the pinned agent-core SHA c814c2b driven by e2e-core (44 live passed, 1 skipped at #91); real `RegistryService` over PG16 in-process (platform-sim real_local); real Core human-principal verification for local-identity (7 tests); real PG16 + SQLite for platform-exporter (51 tests).
- Doubles (declared in `e2e-report.json doubles[]`): scripted llm-gateway (no real model or Jev call has ever gone through the runtime), control-api, lab-broker, bank/sandbox fixture, ingest fixture, the "codex-standin" engine (Python), local human issuer, fixture console API. `real-wire` (external `agentcore serve`) was never run. No AWS call was ever made.
- The only engine that has ever called the bridge is the Python stand-in `e2e-core/src/codex_standin`. The Rust workspace has no HTTP client/server, JWT, JCS or Core wire code: `Cargo.toml` members are core, source-adapters, runner; no reqwest/hyper/axum; no `agent_core_http`, `AgentCoreEndpointProfile`, `HumanAuthorizationPort` or `core_content_bytes` on main or in any Codex worktree (grep over all worktrees). Rust `core_task.rs` still pins `SUPPORTED_CONTRACT_SHA=53e729d6...`/`0.5.0` (a pre-86a7674 Core), and `change_compiler.rs` uses its own `canonical_json`, not shown to equal Core's `content_hash`.

## Table 1 - Units (spec 30.8)
| ID | Short name | Phase | Status | Evidence / missing |
|---|---|---|---|---|
| U24 | Read console on real U07 | P1 | STANDIN | `debug-console/` (#74,#77,#80,#85) runs on fixtures/stand-in with a typed `DebugApi` seam; `provider=http` has no server because no control-api exists (Rust `debug_console.rs` is a projection with no transport). Spec: fixtures do not accredit integration |
| U25 | Deploy by manifest, rollback | P5 | PARTIAL | infra `release/validate_manifest.py`, `validate_plan.py`, `deploy_plan.py --dry-run`, runbook, `engine_platform`/`bridge_services` modules (infra #17,#23,#24,#26), default off, mock-provider tests, nothing applied. Missing: OIDC/CD workflows, smoke, rollback drill, image digests; CAP-62 blocked |
| U28 | AWS lab session | P5 | STANDIN | only `engine_platform` `sandbox-lab` task declared (unapplied); `auxiliary_roles` not wired; no dispatcher/grants code, no IAM/TTL/escape tests |
| U32 | SQL/model/eval/memory panels | P4/P5 | STANDIN | `DemoPanels.tsx`/`Panels.tsx` on fixtures with `consumer_proposal` schemas; no backend |
| U37 | Endpoint profile, HTTP client, classifier (Rust crate) | P1 | STANDIN | no Rust crate; Python stand-in client in `e2e-core/src/codex_standin` and bridge-side `invoke/core_client.py` only |
| U38 | Core credentials, step-up relay | P1/P4 | PARTIAL | Python: `credentials/issuer.py`, `internal/auth.py` (aud/jti), `local-identity/` (71 tests, 7 vs real Core), e2e `test_07_human_approval` (11 live). Rust service-JWT signer and `HumanAuthorizationPort` TODO |
| U39 | Pinned wire, content hash, wire-drift | P3 | PARTIAL | Python: `core-bridge/wire/agent_core@c814c2b/` (250 files, MANIFEST digest reproduced), `gen_wire.py` drift gate. Rust `crates/core/wire` + `core_content_bytes` TODO |
| U40 | Faithful registry/bridge mocks | P1 | PARTIAL | `platform-sim/registry_mock`, `bridge_mock` (mock 246 passed at #91). Bridge-contract mock suite carries 149 xfails with divergence ids; mock lacks `release_settings`, `/version`, export |
| U41 | Dual-run suite, pin, bump | P1 | PARTIAL | parity suite mock/a2/real_local, `pin-watch`, ADRs 0010/0012, bump to c814c2b done. Spec path `contracts/agent_core/pin.json` + `record-wire` absent (pin = `PIN_SHA` constant + wire MANIFEST); `real-wire` not run; not in CI; no Rust wire check |
| U42 | `pulso-core-runtime` composition + image | P1 | DONE | `core-bridge/src/pulso_core_runtime` (7 factories, readiness, `/internal/v1/version`), `test_image.py` 24, `test_main_matrix`, real PG16, real image build; a real start-up bug (`synthesise_args`) found and fixed in #91 |
| U43 | Lab/wiki executors and ToolDefs | P1 | PARTIAL | `tools/{lab,wiki,broker,factory}.py`, ToolDef-handler checks; backend is the lab-broker double (Rust lab not exposed over HTTP) |
| U44 | agent-core-assets, seed, bootstrap | P1 | PARTIAL | worlds `attention-demo` + `pulso-evolution`, `manifest.yaml`, `expected-state.json`, validators (22 tests), `local/core/init/seed_assets.py` (second run writes nothing), in-memory tier checks of already-seeded/bot/session codes. Missing: `pulso-bootstrap core` CLI and `bootstrap-report.json` (grep: none) |
| U45 | Core state reader | P3 | PARTIAL | bridge `GET core-state/aliases/{agent}/{alias}` (#82). No release-entities-by-hash route; Rust `BaseSnapshot`/`AliasState` TODO |
| U46 | Compiler plan, cascade, dry-run | P3 | PARTIAL | bridge `POST core-authoring/dry-run` (candidate_hash/auto_bumped equal to freeze on PG16). Rust `change_compiler.rs` (1248 lines) is domain-only: 6 entity kinds, no `DraftPlan`, no `expected_derived`, no Core wire, no dry-run call |
| U47 | CoreEvalPackage (suite, metrics, queues) | P3 | STANDIN | hand-written suites in assets accepted by Core validate/evaluate; no Rust emitter from `ScenarioCase`, no `queue_order_sensitive` checks |
| U48 | Capture the six `evaluate` results | P3 | PARTIAL | bridge `evaluation/{native,report,http_campaign}.py` persists report and 409 body, handles `failed_infra`; bank lost-response live test skipped; `evaluation_result_lost` not found in code; Rust worker persistence TODO |

## Table 2 - Capabilities CAP-01..64 (spec 31)
Py = Python bridge/runtime/tooling half; Rust = engine-side half (Codex). TODO in the Rust column means nothing on main and nothing in local worktrees.
| CAP | Capability | Py | Rust | Status | Evidence |
|---|---|---|---|---|---|
| 01 | endpoint profile + reach | n/a | TODO | STANDIN | Python stand-in only; doctor probes in PowerShell |
| 02 | Rust HTTP client | n/a | TODO | STANDIN | no reqwest in workspace |
| 03 | classify responses/errors | partial | TODO | STANDIN | classification inside Python `core_client.py`/stand-in |
| 04 | builder credential | done | TODO | PARTIAL | `core-credentials/issue`; e2e: bot cannot approve/publish |
| 05 | internal service JWT | done | TODO | PARTIAL | per-route aud, jti replay, `sub=worker:<id>`, job_id binding (#86); Rust signer absent |
| 06 | instance identity/probe | done | TODO | PARTIAL | `GET /internal/v1/version`; Rust probe TODO |
| 07 | read staging release + entities | alias only | TODO | STANDIN | no entities-by-release route in bridge |
| 08 | read alias | done | TODO | PARTIAL | #82 route (real PG16) |
| 09 | release-agent, run-release | partial | TODO | PARTIAL | `invoke/pin.py`, receipts |
| 10 | verify created: diff/lineage/ref map | partial | TODO | PARTIAL | dry-run outputs; `core_ref_map` Rust TODO |
| 11 | pinned schemas | done | TODO | PARTIAL | wire dir + MANIFEST + gen-wire gate |
| 12 | JCS content_hash as Core | reuse | TODO | STANDIN | Rust `canonical_json` not parity-tested vs Core |
| 13 | ChangeSpec to `changes[]` | n/a | domain-only | STANDIN | `change_compiler.rs`, no wire |
| 14 | produce each EntityKind | n/a | domain-only | STANDIN | 6 kinds in Rust enum, no policy/eval_suite |
| 15 | versions + cascade prediction | Core-authoritative via dry-run | TODO | STANDIN | |
| 16 | pre-roundtrip validation | done | TODO | PARTIAL | dry-run L2 (#82) |
| 17 | closure + candidate_hash compare | via dry-run | TODO | STANDIN | |
| 18 | `docs` without hash pollution | n/a | TODO | TODO | |
| 19 | limits/quotas at compile | n/a | TODO | TODO | |
| 20 | base precondition per op | partial | TODO | PARTIAL | writer executor preconditions (`tools/builder.py`) |
| 21 | eval_suite from ScenarioCase | n/a | TODO | STANDIN | hand-written assets only |
| 22 | seed tool-answer queues | partial | TODO | STANDIN | sandbox_port fixtures |
| 23 | release-level changes | n/a | n/a | TODO | blocked N-07 |
| 24 | compose/boot Core runtime | done | n/a | DONE | U42 evidence |
| 25 | invoke task | done | boundary with stale pin, no transport | PARTIAL | e2e live scout/verifier on real image, scripted model |
| 26 | pin exact release | done | boundary only | PARTIAL | `invoke/pin.py`, `test_tenant_pin` |
| 27 | bind private context before effects | done | TODO (binding endpoint = control-api double) | PARTIAL | `invoke/binding.py`, e2e unknown-state tests |
| 28 | read result + facts | done | TODO | PARTIAL | `facts/whitelist.py`, strict schemas |
| 29 | lab/wiki ToolDefs | done | TODO | PARTIAL | broker is a double |
| 30 | reconcile uncertain invoke | done | TODO | PARTIAL | `reconcile/`, kill -9 test, e2e |
| 31 | time/size/concurrency/cancel/rate | partial | TODO | PARTIAL | rate-limit env, budget ledger; Core has no cancel |
| 32 | real builder executor | done | n/a | DONE | `tools/builder.py`, `test_writer`, e2e writer test |
| 33 | versioned bridge contracts | done | n/a | DONE | `bridge-contract/` (real 337 passed) |
| 34 | extract Core observations | done | TODO (ingest) | PARTIAL | exporter delivers to an ingest fixture; Rust U29 store exists without HTTP |
| 35 | cursor/dedupe/gaps/batch | done | TODO | PARTIAL | e2e exporter exactly-once, outage resume |
| 36 | layer mapping | done | n/a | DONE | `layer_mappings/atencion@1.0.0.yaml`, exporter |
| 37 | release correlation (U50) | none | TODO | TODO | no `release.*` handling anywhere |
| 38 | evaluate + capture results | partial | TODO | PARTIAL | see U48 |
| 39 | combined native+improvement gate | n/a | TODO | TODO | no `CombinedGate` in crates |
| 40 | PulsoScenarioHarness | done | n/a | DONE | `harness.py`, `l5/test_harness`, real executor test |
| 41 | sandbox bank in native gate | n/a | n/a | TODO | blocked D-7 |
| 42 | lost-response reconcile + quota | partial | TODO | PARTIAL | 429 path covered; bank lost-response live test skipped |
| 43 | local human step-up | done | TODO | PARTIAL | local-identity; `HumanAuthorizationPort` absent |
| 44 | AWS human identity | n/a | n/a | TODO | blocked D-5 |
| 45 | approve, publish, promote | done | TODO | PARTIAL | e2e `test_07` 11 live tests driven by the Python stand-in |
| 46 | assets layout/worlds | done | n/a | DONE | |
| 47 | seed empty registry | done | n/a | DONE | idempotent marker, in-memory import tier |
| 48 | reproduce world (`pulso-bootstrap`) | partial | n/a | PARTIAL | seed + start scripts; no bootstrap CLI/report |
| 49 | minimal world + baseline suite | done | n/a | DONE | `pulso-evolution`, `pulso-smoke` |
| 50 | models/keys/deploy params | partial | n/a | PARTIAL | fail-closed gateway consumer config; no real model profile exercised |
| 51 | drift of seeded world | done | n/a | DONE | `assetcheck.py`, `check-digests.py`, doctor `assets_drift` |
| 52 | registry mock | done | n/a | DONE | |
| 53 | bridge mock | partial | n/a | PARTIAL | 149 xfails |
| 54 | a2 in-memory real code | done | n/a | DONE | a2 245 passed |
| 55 | dual-run parity | done | n/a | DONE | local only |
| 56 | forced limits/quotas +-1 | partial | n/a | PARTIAL | few quota tests found |
| 57 | pin/drift/bump governance | done | n/a | DONE | pin-watch, ADRs, expand/contract test; local only |
| 58 | real Core local with Pulso | partial | n/a | PARTIAL | standalone `local/core` stack + fragments; not the single Compose project with `dev.ps1 up --with-core` (no `scripts/dev.ps1` on main) |
| 59 | `doctor` | done | n/a | DONE | `doctor.core.ps1` with V3 codes, Pester 100 |
| 60 | runtime image | done | n/a | DONE | `core-bridge/Dockerfile`, `test_image` |
| 61 | first real E2E | done (Python) | TODO | PARTIAL | e2e-core 44 live on real image; engine = Python stand-in, model scripted |
| 62 | joint AWS deploy | n/a | n/a | TODO | blocked, nothing applied |
| 63 | creds/test data without leak | done | n/a | DONE | gen_keys, CAP-63 scan, leak tests |
| 64 | traces + known_gaps by SHA | minimal | TODO | TODO | only `trace_id` in bridge error envelope; no `traceparent`, no `known_gaps.json` |

## Table 3 - Section 32 platform live source
| ID | Item | Status | Evidence |
|---|---|---|---|
| PL-L1 | platform-exporter | DONE | `platform-exporter/` (#80): read-only cursor, persist-before-POST, redaction, quarantine; 51 tests on real PG16 + SQLite |
| PL-L2 | platform_live simulator (11 tables) | DONE | `platform-sim/platform_live` (20 tests) |
| PL-L3 | platform-contract | DONE | schemas + event catalog + drift gate (26) |
| PL-L4 | console Sources view | PARTIAL | view on fixtures, no control-api |
| PL-L5 | exporter infra (secret, SG, keys) | PARTIAL | infra #26, off by default, unapplied |
| PL-L6 | tests with real deps | PARTIAL | real SQLite/PG yes; exporter-to-control-api E2E absent (no ingest endpoint) |
| PL-C1 | `platform_live` adapter in U29 path (Codex) | TODO | no `platform_live` in crates |
| PL-C2 | capability profile in detectors | TODO | none on main |
| PL-C4 | allow-list/privacy | LOCAL | uncommitted `platform_source_policy.rs` in worktree `improvement-engine-p2-platform-verifier` (branch feat/pl-c4-platform-privacy-guard), unverified |
| PL-C5 | stop at insight | TODO | |
| PL-C6 | integrate section in 30.8 catalog | TODO | section 32 exists, no U-IDs in catalog |
| PL-01 | login_accounts rejected pre-query | DONE | `policy.py DENIED_TABLES`, `test_pl01_allowlist` |
| PL-02/03/04 | unknown type / gap / late event | PARTIAL | exporter-side findings tested; engine review-window opening absent |
| PL-05 | as-of extract | PARTIAL | `asof.py`; detector-side reconstruction TODO |
| PL-08 | simulator customers excluded | PARTIAL | marked at exporter; population exclusion in engine TODO |
| PL-06,07,09,10 | detector unsupported / chain / SLA / stop | TODO | Rust U30 side |

## Table 4 - Sections 26, 4.1, 10
| Item | Status | Evidence |
|---|---|---|
| 26 living docs (architecture, flows, contracts docs) | PARTIAL | `docs/architecture` has 2 files, no `docs/flows`; ADR indexes added in #89; no doc-link CI gate |
| 26.1 AGENTS/CLAUDE/docs/agents | DONE | both repos |
| 26 ADR + journal | DONE | core-bridge ADR 0001-0012, engine 0001-0005, infra 0001-0006, journals |
| 26.2 engine CI | PARTIAL | Rust-only workflow with PG17 migration jobs; red on main; Python/console/contract suites local only |
| 26.2 infra CI | PARTIAL | fmt/validate/contracts; `workload`, `workload_iam`, `engine_platform`, `bridge_services`, `envs/*` tftests not in CI; `core_data` test fails on TF 1.16.4 |
| 26.2 CD/OIDC/release-plan-deploy workflows | TODO | spec says future; none |
| 26.3 local observability | PARTIAL | #88 opt-in LGTM profile; render/startup not runtime-verified |
| 26.3 AWS alarms/metric contract | STANDIN | log groups, CPU alarms, `core_alarms` module unwired; no engine metrics, no firing/resolved evidence |
| 4.1 foundation modules | PARTIAL | network/identity/compute/storage/secrets/observability declared, mock-provider tests, nothing applied, `ci_roles` count=0 |
| 4.1 bootstrap module | TODO | absent (external prerequisite) |
| 4.1 edge/ingress | TODO | blocked by design |
| 4.1/10 engine + bridge workloads | PARTIAL | `engine_platform`, `bridge_services` wired behind default-off switches; no `core-migrate`, sweep, alarms |
| 10 local stack with Core | PARTIAL | see CAP-58; main compose = postgres/localstack/otel; no control-api, worker or debug-console services |
| 10 public demo | STANDIN | `demo/run.ps1` local driver (steps labelled real/stand-in/simulated); no public replay surface |

## Summary (weights DONE 1, PARTIAL .5, STANDIN .2, LOCAL 0 / .5 in last column)
| Block | Items | DONE | PARTIAL | STANDIN | LOCAL | TODO | Weighted % | % incl. local |
|---|---|---|---|---|---|---|---|---|
| Units | 16 | 1 | 10 | 5 | 0 | 0 | 43.8% (7.0/16) | 43.8% |
| CAP-01..64 | 64 | 16 | 28 | 11 | 0 | 9 | 50.3% (32.2/64); 53.7% excl. 4 blocked CAPs | 50.3% |
| Section 32 (PL-L, PL-C) | 11 | 3 | 3 | 0 | 1 | 4 | 40.9% | 45.5% |
| PL-01..10 | 10 | 1 | 5 | 0 | 0 | 4 | 35.0% | 35.0% |
| Sections 26/4.1/10 | 14 | 2 | 7 | 2 | 0 | 3 | 42.1% | 42.1% |
| Total | 115 | 23 | 53 | 18 | 1 | 20 | 46.2% (53.1/115) | 46.6% |

Units by phase: P1 (U24,U37,U38,U40-U44) 48.8%; P3 (U39,U45-U48) 44.0%; P4/P5 (U25,U28,U32) 30.0%.
Rust half: 38 of the 64 CAPs have an engine-side (Rust) half; on main none of them is DONE, a few have only a domain-level fragment (CAP-13, 14, 25, 26), the rest TODO. The 22 Python-only CAPs are mostly DONE (14 DONE, 6 PARTIAL, plus blocked ones).

## Key findings
1. The Core integration is a Python bridge plus a Python stand-in engine. Every capability labelled Rust (client, classifier, JWT signer, `HumanAuthorizationPort`, JCS hash, compiler/DraftPlan, eval-suite emitter, worker result persistence) is TODO on main and absent from every Codex worktree. This, not the bridge, is why a non-mocked end-to-end with the real engine does not exist.
2. No control-api (no HTTP server in the Rust workspace). The bridge's binding callbacks, the exporter's ingest and the console `provider=http` all point at a double. U24, U32, PL-L6 and the last hop of CAP-34 depend on it.
3. Real vs double: real PG16 and a real built Core image have run the bridge (44 live e2e tests), but the LLM was always scripted; lab broker, bank, ingest and control-api were doubles; the E2E driver was Python. No real Jev/LLM call, `real-wire` never ran, no AWS call.
4. Stale Rust pin: `crates/core/src/core_task.rs` declares contract 0.5.0 / SHA 53e729d; main's Python pin is c814c2b (contracts 1.3.0). A Rust client must be built against `bridge-contract/` and the c814c2b wire, not that constant.
5. Evidence is local-only: no workflow runs the Python/console/Terraform suites and hosted CI is red/quota-exhausted. DONE rows rely on PR-body claims; the "merged" language in journals should not be read as CI-verified.
6. Docs vs code: the V3 implementation note lists CAP-58/61 as implemented; reality is a standalone Core stack (no joint Compose or `dev.ps1`) and a stand-in-driven E2E. CAP-37 (release correlation) and CAP-64 (traceparent, `known_gaps.json`) have no implementation and are not in that note.
7. Infra is declaration-only: modules and offline release validators are tested with mocked providers, but nothing is applied; OIDC, state, bootstrap, CD, alarms, `core-migrate` and sweep are open (OPEN_GAPS); CAP-23, 41, 44, 62 are blocked by decisions outside our code.
8. Codex platform half: PL-C1/C2 absent; PL-C4 exists only as uncommitted local files; 7 Codex worktrees hold unpublished, uncommitted changes (journal CX-0182).

## Open uncertainties
- No test was run by me; the hosted-CI red cause is unknown (logs 404). All counts are PR-body claims.
- Statuses for CAP-15, 17, 20, 22, 31, 56 rest on grep-level reading of Python code and could move one notch.
- Whether Codex has Rust bridge-client work outside `D:\.codex\factored\worktrees` is unknown; the journal CX-0150..0182 mentions none.
- Infra test counts are PR-body claims; infra git was read from origin/main after fetch.
