# V3 successor amendments proposed by Team Claude (revision `CL-amendments-3`)

Status: PROPOSALS ONLY. `TECH_SPEC_PULSO_AUTOMEJORA_V3.md` (canonical) is not edited by this file. Nothing here is agreed until both teams record it in the shared journal (plan 17.9.5). Until then Claude implements the compatible reading and blocks only the affected case.

Sources: (a) AM-01..AM-22 from the definitions phase (`v3_amendment_proposals.md`, revision `CL-definitions-1`, consolidated below with their evidence unchanged); (b) AM-23..AM-37, new findings from the implementation (journal CL-0010..CL-0017, `BITACORA_PULSO.md` Claude entries of 2026-10-02/03); (c) AM-38..AM-50, findings since `CL-amendments-2` (journal CL-0018..CL-0022, pin bump to `789d6c8`, e2e-core, local-identity, demo, LLM gateway adoption, infra reconcile; section 3b).

Field legend per item: **V3** location; **Current** text or behaviour; **Proposed** text; **Evidence** (file or commit; `pin/` = `D:\.codex\factored\references\agent-core` at `86a7674`; commits are on branch `claude/r-runtime-wire` in worktree `improvement-engine-claude-r` unless stated); **Owner** (who authors the change); **Class**: `V3` = V3 amendment, `PLAN` = plan or annex D fix (plan body is Codex-owned outside section 17), `UP` = upstream agent-core request, `NONE` = our composition, no text change needed. Agreement: C = Codex, O = owner/user, U = upstream.

Evidence marked TBV was not executed. Implementation evidence below was executed locally by Claude on real PostgreSQL 16 (Podman machine `pulso-dev`, containers `--cgroups=disabled`, removed afterwards); see plan 17.12.

## 1. Index

| # | V3 location | Issue | Pri | Class | Agree |
|---|---|---|---|---|---|
| AM-01 | 31.2.5 CAP-05 | Route-class table lacks executor->lab-broker, `core-credentials`, evaluation purposes | P2 | V3 | C |
| AM-02 | 27.2/29.6/31.5.9/31.7.1/31.7.5 | Two evaluate models without a statement of which applies when | P1 | V3 | C, O |
| AM-03 | 31.7.1 CAP-38 | "409 body is the only copy" / `evaluation_result_lost` wrong for Flow path and service idempotency | P1 | V3 | C |
| AM-04 | 29.6/29.8/CAP-32/CAP-42 | "Each write has its own key derived from the command" is not what Core does | P1 | V3 | C |
| AM-05 | 31.5.4 CAP-27 | ContextVar as the context channel | P1 | V3 | C |
| AM-06 | 31.5.1 CAP-24 (2) | `replace(ports, registry=Pinned...)` does not cover all resolution points | P2 | NONE | - |
| AM-07 | 31.7.3 CAP-40 | Stock `EngineScenarioHarness` replays by `eval-{scenario.id}` | P1 | UP+V3 | U, C |
| AM-08 | 31.7.1/31.5.8/31.7.2 | `max_workers=1` serialises per call only | P2 | NONE | - |
| AM-09 | 31.5.6 CAP-29 | `lab_write_scratch` not callable by agent nodes; no artefact reader | P2 | V3 | C |
| AM-10 | 31.5.4 CAP-27 | `bind_context` facts: three booleans vs four stages | P3 | V3 | C |
| AM-11 | 31.5.1/N-06 | Composition surface larger than "~5"; shared `NullTranscript` | P3 | NONE | - |
| AM-12 | 31.6.1 CAP-34 | Exporter watermark, eval detection, handoff dispatcher, args/result exclusion | P2 | V3 | C |
| AM-13 | 24/31.6.2-31.6.4 | Batch union/contiguity vs Rust U29 DTO; chain attestation; release kinds | P1 | V3 | C |
| AM-14 | 31.9.2/31.9.3 | `already_seeded` code does not exist; import all-or-nothing | P2 | NONE | - |
| AM-15 | 31.11.3/31.11.1 | `--app-role` grants; rootless `pids`; two error names | P2 | UP+V3 | U, C |
| AM-16 | 31.11.5 CAP-62 | Manifest heads, "both directions", key files as mounts, network table, "signed" | P2 | V3 | C, O |
| AM-17 | 4.1 | Nine module names that do not exist; EC2 vs Fargate | P3 | V3 | O |
| AM-18 | 31.4.1 CAP-11 | Generated schema destination is a Codex path | P2 | V3 | C |
| AM-19 | 15/20.1/20.2/25/29.8 | Debug/product DTO shapes undefined | P1 | V3/PLAN | C |
| AM-20 | 31.5.10 CAP-33 | Evaluation admission/arm/bank routes only in plan annex | P2 | V3 | C |
| AM-21 | 30.8/31.1 | Plan says U56; V3 is right | P3 | PLAN | - |
| AM-22 | 31.5.5/31.5.8 | Core `output_schema` is a closed subset | P2 | V3 | C |
| AM-23 | 31.5.4 CAP-27, 29.8, plan 17.3.3 | Pinned Core keeps run-input slots `claimed`; flows cannot read `slots.*` | P1 | V3+UP | C, U |
| AM-24 | plan 17.3.5 (and V3 evaluation acceptance if any) | Evaluation run ids: 6 (shared suite) or 9, not 7 | P1 | PLAN | - (CX-0023/CX-0025 agree) |
| AM-25 | 31.5.10 / annex D | `evaluation_context_ref` format and length | P2 | V3/PLAN | C |
| AM-26 | 31.8 / annex D sandbox | Entity ids contain no dots (underscore forms) | P2 | PLAN | C |
| AM-27 | 31.7.1 CAP-38, 31.7.5 CAP-42 | Early run close is explicit evidence (`closed_early`) | P2 | V3 | C |
| AM-28 | 31.7.1 CAP-38 | `evaluation_in_progress` and consumed-past-deadline semantics | P2 | V3 | C |
| AM-29 | 31.5.9 CAP-32 / 31.7.1 | `native_evaluate` broker digest covers a broad tuple | P2 | V3 | C |
| AM-30 | 29.6/CAP-32, plan 17.4.2 | Write-key ordinal is the index in the committed `operations` array | P1 | V3/PLAN | C |
| AM-31 | annex D.2, 31.5.5 | Fact shapes as implemented (builder alternatives, ArtifactRef evidence) | P2 | PLAN | C (CX-0021, CX-0028 accept) |
| AM-32 | annex D (DTOs) | DTO additions: `registry_mutation_commitment`, `memory_snapshot_ref`, `extract_manifest_ref`, `campaign_ref`; ArmRequest/ArmReport differences | P2 | PLAN | C |
| AM-33 | 31.11.1 CAP-58, 31.11.2 | Podman on `pulso-dev` needs `--cgroups=disabled` for any container | P2 | V3+NONE | C (aggregate doctor) |
| AM-34 | 31.5.6 CAP-29, A03 | Broker JWT keypair and claims | P3 | NONE (done) | - |
| AM-35 | 31.6.1 CAP-34 | Exporter implementation findings (pending batch, ArtifactRef, per-attempt token) | P3 | NONE | - |
| AM-36 | 31.5.10 CAP-33 | Composed runtime security hardening (tenant claim, iat/exp, body bounds) | P3 | V3 | C |
| AM-37 | 31.5.4 / 31.5.7 | Registry `reopen` and `evaluate` ToolDef arguments in the writer | P2 | PLAN+UP | C |
| AM-38 | 31.5.10 CAP-33, 31.2.5 | Deployment tenant allow-list; foreign tenant claim is 403 `pulso:tenant_mismatch` | P1 | V3 | C |
| AM-39 | 31.5.4 CAP-26/27, 31.5.9 | Stage/agent pairing enforced: 422 `pulso:stage_agent_mismatch` | P2 | V3 | C |
| AM-40 | 31.5.10 CAP-33, 31.7.1 | Admission bound to tenant + job_id + `binding_ref`; evaluate-only invocation path (A04) proven | P1 | V3 | C |
| AM-41 | 31.6 / V3 l.1121, 23 | Dependency failure = audit `agent_step` failed + `error_kind`; no new receipt outcome | P1 | V3 | C (CX-0073/0075) |
| AM-42 | CAP-44, plan 16.13.2 | HumanAuthorizationPort rules: Core ignores binding attrs, Principal has no `jti` | P1 | V3+PLAN | C |
| AM-43 | plan 16.13.2 / D.1, DR-08 | local-identity (sandbox human issuer) routes, claims, errors | P2 | PLAN | C |
| AM-44 | 31.5.7, writer allowlist | `release_settings` drafts denied by default; upstream gate wanted (NF-01) | P2 | V3+UP | C, U |
| AM-45 | annex D, 31.4 | `ReleaseDetail` carries 4 new fields at `789d6c8`; strict DTOs must follow | P1 | PLAN | C |
| AM-46 | 31.4.1 CAP-03/11, A02 | Pin identity is SHA + MANIFEST digest `890edd7a...`, not `contracts/VERSION` | P2 | V3 | C |
| AM-47 | 31.11 CAP-60/62 | Key delivery from Fargate secrets: env to key files; no path for bridge/exporter keys; no tmpfs | P2 | V3+UP | C, O, U |
| AM-48 | CAP-50/60, l.758-762/798, F6 | LLM gateway consumer: names, fail-closed config, readiness, receipt fields | P1 | V3+UP | C, U |
| AM-49 | 31.6.1 CAP-34 | Export boundary: our read-only PG exporter stays; `/v1/export/*` off by default | P3 | NONE | - |
| AM-50 | 31.5.4 / AM-23 | Update of AM-23: `claimed` input slots confirmed upstream design (UP request dropped) | P1 | V3 | C |

## 2. Definitions-phase proposals AM-01..AM-22 (consolidated)

The text of each item is unchanged from revision `CL-definitions-1` except where section 3 supersedes it. Because the original scratchpad file is not a durable document, the proposed wording is reproduced here.

### AM-01 CAP-05 route-class table (V3 31.2.5, l.1995-2004)
- **Current:** two rows (Rust->bridge; bridge/exporter->control-api). The lab-broker audience appears only in CAP-29 (31.5.6); `core-credentials/issue` names `purpose=credential_issue` in the CAP-33 table but CAP-05 lists neither.
- **Proposed:** append row "Executor -> lab broker (`/internal/v1/broker/*`: authorizations/check, artifacts, lab, wiki, sandbox) | Service JWT, own keypair (not the callback key, not the Core principal key), minted per call, TTL <= 60 s | `iss=core-bridge`, `aud=lab-broker`, singular `scope in {lab, wiki, artifact_read, authz_check, sandbox}`, `tenant_id`, `purpose`, `job_id`, `exp`, `jti`". Rust->bridge row adds routes `core-tasks/*`, `core-state/*`, `core-authoring/*`, `version`, `core-credentials/issue`, `evaluation/*` and purposes `core_task_invoke, core_task_read, alias_read, authoring_dry_run, version_probe, credential_issue, evaluation_admit, evaluation_arm_run, evaluation_arm_read`. One host may serve both audiences if `aud` is verified per route group with separate public-key sets.
- **Evidence:** pin CAP-29 text; plan 16.4/16.5 cites "31.4.7" (that is CAP-17), correct is 31.5.6. Implemented in `b3af773` (see AM-34).
- **Owner:** Codex (verifier). **Class:** V3. **Agree:** C. Related DR-22, CLQ-04.

### AM-02 Two evaluate models (V3 27.2 step 6, 29.6 step 5, 31.5.9, 31.7.1, 31.7.5)
- **Current:** 27.2 step 6, CAP-38 and CAP-42 describe Rust-side create/put/freeze/evaluate over REST (`orphan_candidate`, `pulso-key:<k>` titles); 29.6 step 5 and CAP-32 describe the constructor Flow with `BuilderToolExecutor` (10 tools incl. `evaluate`).
- **Proposed (new 31.7.0 "Evaluate modes"):** `RegistryMutationExecutionMode` is a per-campaign setting. `native_builder_flow` (demo): the constructor Flow performs create_proposal, put_draft, validate, freeze, reopen and evaluate through `BuilderToolExecutor`; Rust never POSTs evaluate for the same candidate/attempt; 27.2 step 6, CAP-38 transport and CAP-42 `orphan_candidate` apply only to `registry_http_contract`. `registry_http_contract` is a separate campaign and namespace. `RegistryMutationCommitment.operation_set in {author, evaluate, author_evaluate}`. Replace the unconditional "Worker ejecuta POST ... evaluate" by "In `registry_http_contract`, the worker executes ...".
- **Evidence:** pin `composition/builder_tools.py`; implemented: writer evaluates in-flow via `FlowEvaluationGate` (`122dca4`, `3e4a041`, `5a09323`).
- **Owner:** Codex (plan 4.2/D.2 already mix both; A04 agreed in CL-0008). **Class:** V3. **Agree:** C, O.

### AM-03 CAP-38 fail body and lost-response recovery (V3 31.7.1, l.2448-2458)
- **Current:** "the full 409 body is the only copy accessible by HTTP"; `pulso:evaluation_result_lost` needs re-freeze.
- **Proposed:** the 409 body is the only copy on the stock route; in the Pulso composition the bridge wraps `RegistryService.evaluate`, stores the full `EvalReport` (or `gate_failed` payload) in `pulso_bridge.eval_reports` keyed `(proposal_id, evaluation_attempt)` and returns it through the bridge API. Timeout: re-POST with the same admission header or re-read through the key; the service returns the stored report/409 without re-running and without consuming quota; `evaluation_result_lost` applies only when no admission key exists; `failed_infra` is replayed too, a retry needs `evaluation_attempt+1`.
- **Evidence:** `pin/registry/service.py:428-501` (`_stored_eval`, `idempotency_conflict`); `pin/registry/http.py:148-151`; implemented full-report persistence in `122dca4`/`3e4a041` (tests/l5).
- **Owner:** Codex. **Class:** V3. **Agree:** C. Related DR-04, CLQ-09, CLQ-33.

### AM-04 Write keys (V3 29.6/CAP-32/CAP-42; plan 4.2)
- **Current:** "each write has its own key derived from the command".
- **Proposed:** in `native_builder_flow` the engine key of each draft write is the Core `action_id` (`pin/actions/execution.py:93`). The Pulso `IdSource` returns, for `IdKind.action` inside a writer invocation, `"pulso-w:" + sha256(command_key | stage | ordinal)[:48]` so the engine key equals the command-derived key and `get_write(key)` serves verify and reconciliation across runs. Rust validates receipts with the same formula. Superseded in detail by AM-30 (ordinal definition).
- **Evidence:** implemented `PulsoIds` (`4098240`), writer executor (`0fb361b`), golden vectors `core-bridge/tests/l3b/test_d2_facts_and_ordinals.py`. Plan CL-0008 residual (17.11.3): Codex replaces the plan 4.2 sentence.
- **Owner:** Codex (plan text) + Claude (vectors). **Class:** V3/PLAN. **Agree:** C. Related DR-01, CLQ-10.

### AM-05 Context channel (CAP-27, V3 31.5.4, l.2352-2360)
- **Current:** "pending verification: contextvars propagation into the synchronous FastAPI thread".
- **Proposed:** the primary channel is the signed `Principal.attrs.task_binding_ref`, resolved to an immutable `InvocationContext` held by the bridge; a ContextVar is only a redundant second channel; mismatch yields `denied` `pulso:context_mismatch`. Gate: N concurrent invocations with distinct jobs echo their resolved `(tenant, job)`, plus a thread-pool variant.
- **Evidence:** `pin/api/tracing.py:47-56`; `pin/registry/evaluation/evaluator.py:92-94` (`ThreadPoolExecutor.submit` without `copy_context`). Implemented and tested in `0fb361b` (`InvocationRegistry` + ContextVar secondary): 32-way concurrency + ThreadPoolExecutor variant pass (tests/l3b, 59 tests).
- **Owner:** Codex (consumer of denial codes). **Class:** V3. **Agree:** C. Related DR-05.

### AM-06 CAP-24 step (2) pin (V3 l.2300)
- **Current:** `replace(ports, registry=PinnedRegistryPort(...))` as complete pin.
- **Proposed:** the pin affects `resolve_release` only, driven by the signed `pin_release_id` attr of the run principal; exact release ids are exact elsewhere. Verification: two releases of one Agent version, alias moved mid-run, release revoked between pre-check and start.
- **Evidence:** `pin/composition/serve_ports.py`; `pin/registry/postgres/runtime.py:55-70`; implemented `PinnedRegistryPort` (`4098240`) and real-Core alias-pin tests (`8925163`: alias pin, wrong-agent pin).
- **Owner:** Claude. **Class:** NONE. **Agree:** -.

### AM-07 CAP-40 and "Evaluacion de tasks" (V3 31.7.3 l.2468; 29.8)
- **Current:** stock `EngineScenarioHarness`; rationale "not invocable with a task-agent `invocable_by:[builder]`".
- **Proposed:** `PulsoScenarioHarness` replaces it: (1) `RunInput.input` from the sealed manifest; (2) unique idempotency key per job `eval-<sha256(execution_id|scenario_id|arm|repetition|nonce)>`; (3) builder principal; (4) own `authz`; (5) per-job `EvalStorage` or unique keys; (6) budget meter; (7) non-candidate failures -> `HarnessUnavailable`. The `invocable_by` rationale is dropped (the engine does not enforce it, `pin/api/authorization.py:35-62`). Add upstream request N-12: `EngineScenarioHarness` should make the eval idempotency key unique per execution.
- **Evidence:** `pin/composition/evaluation.py:80-140`; the replay was reproduced on PG16 and `PulsoScenarioHarness` implemented (`122dca4`, "collision first RED"). Distinct run ids confirmed (AM-24).
- **Owner:** Claude (harness), upstream (N-12). **Class:** UP + V3. **Agree:** U, C. Related DR-02, CLQ-32.

### AM-08 Serialisation of evaluate (V3 l.1428, 2384, 2443)
- **Proposed:** "serialised per evaluation (`max_workers=1`); across concurrent evaluations the bridge enforces a process-wide semaphore of 1 with a bounded queue (`HarnessUnavailable("evaluation_busy")` -> `failed_infra`) and a per-proposal single flight in `pulso_bridge.admissions`" (see also AM-28 for the in-progress denial actually implemented).
- **Evidence:** `pin/registry/evaluation/evaluator.py:55-97`. **Owner:** Claude. **Class:** NONE.

### AM-09 CAP-29 catalogue (V3 31.5.6, l.2370)
- **Current:** `lab_write_scratch` listed as write; agent nodes may call only `read|compute` tools.
- **Proposed:** catalogue `bind_context` (read), `lab_query` (compute; CTAS inside the query), `lab_get_result` (read; folded into `lab_query` when paging is internal), `wiki_read`, `wiki_explore`, `wiki_transform` (compute), `artifact_get` (read; sealed artefacts for builder_design and writer; size-limited, digest-checked). Update U43. Read keys in agent nodes are derived: `query_key = sha256(binding_ref|session_ref|expected_session_revision|normalised_sql)`.
- **Evidence:** `pin/flows/rules/phase5.py:54-66`; `pin/interpreter/handlers/agent.py:45,120-121`; implemented closed `pulso/*` catalogue (`0fb361b`) and `BrokerArtifactPort` (integrator gap 2: GET `/artifacts/{id}`, scope `artifact_read`).
- **Owner:** Codex (broker endpoint). **Class:** V3. **Agree:** C.

### AM-10 `bind_context` facts (V3 l.2352)
- **Proposed:** boolean facts `is_scout`, `is_verifier`, `is_builder` (the builder_design stage) and `is_writer`. Superseded in scope by AM-23 (bind_context is now also the only input channel).
- **Owner:** Codex. **Class:** V3. **Agree:** C.

### AM-11 Composition notes (CAP-24 / N-06, V3 l.1519, 2749)
- **Proposed:** N-06 replaces "(~5 functions)" by the surface list (`resolve_ports, ServePorts, DemoContext, build_api_deps, ApiDeps, create_app, registry_extension, RegistryService, ScenarioEvaluator, LocalSandbox, EngineScenarioHarness, EvalStorage, UowRunReleases, OtelTurnTelemetry, setup_observability, PostgresStore, PostgresRegistry, PgRegistryStore, build_candidate (deep import `agent_core.registry.candidate`), BuilderToolExecutor, load_identity_verifier`), guarded by the pin contract CI (`compat.py`). CAP-24: evaluation uses its own ephemeral transcript and `EvalAuthz`; `main` exits 2 `pulso:demo_double_in_real_mode` when `AGENTCORE_ALLOW_DEMO` is set.
- **Evidence:** implemented in `4098240` (compat closed pin list; exit-2 matrix; preflight). **Owner:** Claude. **Class:** NONE.

### AM-12 CAP-34 exporter (V3 31.6.1, l.2414-2425)
- **Proposed:** (a) per-run cursor `(run_id -> last confirmed seq)` and per-run head `max(seq)`, no time overlap; (b) second detector of `pulso:eval_db_misconfigured` = startup check `current_database()` equals the runtime DB, `has_database_privilege('exporter_ro','core_eval','CONNECT')` false, exporter role has no grant on `runs`; (c) "Core has no handoff dispatcher in the pin; `PostgresOutbox.pending()` is a SELECT and `mark_delivered()` an UPDATE nothing calls; the exporter uses neither"; (d) CAP-64: Core events can carry audit-filtered `args`, `result`, `reportable_attrs`; the exporter forwards an allowlisted projection only (canary-tested).
- **Evidence:** `pin/adapters/sql/schema.sql`; implemented in `8a820b1` (23 tests) and review `784f220` (49 tests, privilege grants guard).
- **Owner:** Codex (receiver). **Class:** V3. **Agree:** C.

### AM-13 Observation batch vs Rust U29 DTO (V3 24, 31.6.2-31.6.4)
- **Proposed:** the exporter posts a Pulso HTTP `PlatformBatch` (RFC3339Z, unknown fields rejected) translated by control-api to the stored batch; digests computed server-side only; `Idempotency-Key = request_digest`; ACK means committed; `coverage_marker` maps to batch coverage plus a lateness derived from `received_at - occurred_at`; for `registry` and `outbox`, `cursor.from_seq/to_seq` are exporter-assigned contiguous ordinals and the true `seq` travels in `source_event_id`; `chain_attestations[] {run_id, verified_through_seq, tail_hash, genesis_ok, events_in_chain, events_exported}` validated by `CoreChainVerifierPort`; event kinds `release_published|promoted|revoked`; `LayerMapping` gains `target_system`; up to three source ids per target system.
- **Evidence:** `engine/crates/core/src/platform_observations.rs` (U29 DTO, `SequenceGap`, `CoreChainVerifierPort`); implementation: audit observations carry `source_event=null` + native hash + ref to exact-bytes NDJSON chain artifact, registry/outbox carry the pinned public projection (L6, `8a820b1`, `784f220`).
- **Owner:** Codex. **Class:** V3. **Agree:** C. Related DR-10..DR-14, CLQ-06/07/29..31.

### AM-14 Seed idempotency (V3 CAP-47/48, l.2533-2562)
- **Proposed:** seeding per agent; `registry:illegal_transition` is reclassified by `pulso-bootstrap` as `already_seeded` followed by verification against `expected-state.json`; idempotency is a verification postcondition; the second run performs zero Core writes.
- **Evidence:** `RegistryService.import_seed` (all agents in one transaction; `illegal_transition` if any agent already has a `staging` alias). Implemented in L8: second start seed writes nothing (marker digest), release ids equal the manifest (BITACORA 2026-10-03 14:59). **Owner:** Claude. **Class:** NONE.

### AM-15 CAP-60 / CAP-58 (V3 l.2671, 2690)
- **Proposed:** CAP-60: the migrate role and the runtime role are the table owner, or `core-grants` (after `migrate`) grants the minimum on `runs`, `outbox`, `usage`; report the `--app-role` gap in `known_gaps.json`. CAP-58: the cgroup limitation is connection-specific; `doctor` probes the selected connection and reports one code `runtime_cgroup_unavailable` with a sub-reason (`pids`, `memory`). **Note:** the last sentence of the original proposal ("it never passes `--cgroups=disabled`") is superseded by AM-33.
- **Evidence:** `pin/composition/migrate.py` (`apply_schema` grants `SELECT, INSERT ON audit_events` only). **Owner:** Claude + upstream. **Class:** UP + V3. **Agree:** U, C.

### AM-16 CAP-62 deployment (V3 31.11.5, l.2714-2728)
- **Proposed:** manifest `agent_core:{image_digest, git_sha, contracts_version, schema_digest:{runtime, eval}, pulso_package_sha}` replacing migration heads; `exporter.image_digest == agent_core.image_digest`; `console.image_digest=null` with `reason:'dependency_blocked:edge'`; `signature` is `dependency_blocked` until key custody is decided; rollback reverts the image pair as a unit, CI proves N-1 image vs schema N and schema N over a database built with N-1 (not both directions); two key files materialised from secret env into tmpfs by the entrypoint; Red: add SG `core-runtime` -> `engine-api`:8080 and `core-exporter` -> `engine-api`:8080.
- **Evidence:** `pin/composition/migrate.py` docstring (no versions, no `down`); delivered `infra/release/` deploy-manifest schema + validators M-01..M-10 (`5561d6f`, `1e2f852`, `a21ea73`; merged via infra#17). **Owner:** Claude (schema), Codex (engine manifest), O (custody). **Class:** V3. **Agree:** C, O.

### AM-17 Section 4.1 modules and EC2 lines (V3 l.141, 289, 401-403, 599, 965)
- **Proposed:** replace the 4.1 module table by `bootstrap` (external), `network`, `connectivity` (deferred), `edge` (`dependency_blocked`), `identity`, `compute` (runtime), `database`+`storage` (data), `secrets`, `observability`, `security` (SG per flow); Fargate per 31.11.5 supersedes the EC2 demo references; a different topology needs a new ADR.
- **Evidence:** infra modules `compute, database, identity, network, observability, secrets, security, storage`; ADR 0003 rewritten (infra#17). **Owner:** owner decision. **Class:** V3. **Agree:** O.

### AM-18 CAP-11 generated schema destination (V3 31.4.1)
- **Proposed:** the generator writes `core-bridge/wire/agent_core@<sha7>/` with `MANIFEST.json`; Codex copies or path-references the directory by digest into `crates/core/wire/agent_core@<sha7>/` and owns `contracts/agent_core/pin.json`.
- **Evidence:** delivered `core-bridge/wire/agent_core@86a7674/` (193 schemas + 2 events + openapi, `17b8e6f`); plan 17.11.3 residual. **Owner:** Codex. **Class:** V3. **Agree:** C.

### AM-19 Product/debug DTOs (V3 15, 20.1, 20.2, 25, 29.8)
- **Proposed (Codex authors; Claude lists the minimum):** closed versioned enums for node/run status and `current_stage` + stage->phase table; node fields `attempt, lease_ref, worker_ref, next_wakeup_at, trace_id, core_run_ref, phase`; event fields `job_ref, node_id`; `entity_ref {type,id}`; SSE contract (`Last-Event-ID` and/or `after_sequence`, heartbeat, gapless sequence, close notice); 410 `Problem{code:'cursor_expired', current_ref, recovery_after_sequence, snapshot_url}`; session endpoint, CSRF header, logout; decision/command DTOs; `OpportunityProjection`, `EvaluationProjection`, `MemoryDiff`; `deployment_profile`; one route family (20.1).
- **Evidence:** console consumer assumptions registered in CL-0014 (409 `stale_revision`, nullable graph `trace_id`, decision `domain_revision`, authorised 410 recovery), cross-checked in CX-0022/CX-0028; fixtures in `debug-console` (merged as improvement-engine#74, `consumer_proposal` zod schemas). **Owner:** Codex. **Class:** V3/PLAN. **Agree:** C.

### AM-20 Admission, arms and bank routes (V3 31.5.10 CAP-33 table)
- **Proposed:** append rows `POST /internal/v1/evaluation/admissions`, `arms/run`, `arms/{execution_id}`, `arms/by-key/{key}` with purposes `evaluation_admit|evaluation_arm_run|evaluation_arm_read`; the registry evaluate route keeps the exact upstream body; the private header `X-Pulso-Evaluation-Context` resolves the admission and the service key is `pulso-eval:<evaluation_context_ref>`.
- **Evidence:** L5 `ROUTES` lacked `/arms/run` and `/arms/by-key` (BITACORA L5 finding); `bridge_mock` routes (`26dd6bd`). **Owner:** Codex. **Class:** V3. **Agree:** C.

### AM-21 U-range (V3 30.8/31.1)
- V3 says U37-U55 (correct); plan section 9 says "U37-U56". No V3 text change; correct the plan note. **Class:** PLAN. **Agree:** none.

### AM-22 Fact schemas (V3 31.5.5 CAP-28, 31.5.8 CAP-31)
- **Proposed:** each stage fact has a Core-subset schema embedded in the Flow and a strict JSON Schema 2020-12 in the bridge, with a CI assertion that the Core-subset is a relaxation of the strict one; no non-integer JSON numbers in facts (decimals are strings); `completed` without a required fact is `pulso:output_missing`.
- **Evidence:** `pin/domain/schema.py` `_SUPPORTED`; implemented in `core-bridge/src/pulso_core_runtime/facts/schemas/*.strict.json` (`0fb361b`, `669cfb8`). **Owner:** Codex (validates with same files). **Class:** V3. **Agree:** C.

## 3. New findings from the implementation (AM-23..AM-37)

### AM-23 Pinned Core keeps run-input slots `claimed`; flows read inputs via `bind_context` facts
- **V3:** 31.5.4 CAP-27 (`bind_context`), 29.8 stage inputs; plan 17.3.3 stage input slot names (`briefing_ref`, `hypotheses_ref`, `design_input_ref`, `draft_plan_ref`).
- **Current:** stages are assumed to receive their inputs as run-input slots that Flow nodes read.
- **Proposed:** "In the pinned Core (contracts 1.3.0) run-input slots enter the run as `claimed`; a Flow can read only `validated` slots, and slots become `validated` only through a `collect` node, so any Flow node reading `slots.*` escalates before the first tool call. Pulso stages therefore receive their inputs as tool-origin facts from `pulso/bind_context` (`facts.binding.value.*`); `CoreTaskInvocation.input` is bound into the invocation context by the bridge. `bind_context` returns the stage booleans (AM-10) plus the bound inputs. No wire change." Add an upstream request: a documented path for trusted run-input to become `validated` without a collect node (optional).
- **Evidence:** commit `447772b` ("Flows read run inputs from bind_context facts (Core 1.3.0 never validates run-input slots); scout and writer E2E green"); strict xfail in `core-bridge/tests/integration/test_scout.py` that proved the escalation before the fix; journal CL-0016 "Finding about the pinned Core"; BITACORA integrator entry.
- **Owner:** Claude (flows and bridge), Codex (confirm no Rust change). **Class:** V3 (+UP request). **Agree:** C, U.

### AM-24 Evaluation run ids: 6 or 9, not 7
- **V3/plan:** plan 17.3.5 requires 7 distinct run ids for base + candidate + 3 repetitions.
- **Current:** acceptance count 7.
- **Proposed:** replace by "the number of distinct run ids equals the declared arm/repetition matrix: 6 for a shared suite with 3 repetitions (3 base + 3 candidate), 9 when old and new suites differ (the old suite's base arm adds its own); do not hard-code a count". The extra "seventh run" in the plan has no referent.
- **Evidence:** journal CL-0012, CL-0015; CX-0021, CX-0023/CX-0025 (independent reviewer `/root/e2e_audit` confirms the plan count is erroneous); L5 tests (`122dca4`, `179d4f6`): 78 tests (240 after review r2) on PG16, stock-harness replay reproduced.
- **Owner:** Codex (plan 17.3.5 is in Claude's section 17; the correction is recorded in plan 17.12.3 and the 17.3.5 body text is left unedited in this pass). **Class:** PLAN. **Agree:** C (already accepted in CX-0023).

### AM-25 `evaluation_context_ref` format
- **V3:** 31.5.10 CAP-33 / annex D admission response and `X-Pulso-Evaluation-Context` header.
- **Current:** opaque string.
- **Proposed:** "`evaluation_context_ref` is ASCII, at most 200 characters, matching the full-match pattern `[A-Za-z0-9_.:-]{1,200}\Z` (no whitespace or newline; the bridge matches the whole value, not a prefix); the service key `pulso-eval:<evaluation_context_ref>` therefore stays within the registry idempotency-key limit."
- **Evidence:** `179d4f6` ("_EVAL_REF full match", "deny newline refs in FlowEvaluationGate" `3e4a041`); ADR `core-bridge/docs/adr/0002`. Pattern in `tools/builder.py:41`; Codex must use the same charset in its validator.
- **Owner:** Codex (Rust validator) + Claude. **Class:** V3/PLAN. **Agree:** C.

### AM-26 Entity ids contain no dots
- **V3/plan:** sandbox tool/entity names such as `sandbox/case.open`, bank manifest ids.
- **Current:** dotted ids.
- **Proposed:** "Registry/Core entity ids follow the pinned `EntityRef` pattern, which rejects dots; sandbox and bank ids use underscores (`sandbox/case_open`, `sandbox/get_action`). The bank manifest and any generated ids use the same form."
- **Evidence:** L5 finding ("dotted sandbox tool ids invalid as EntityRef"); CL-0012; CX-0028 confirms "Pinned EntityRef rejects dots, so underscore IDs are correct".
- **Owner:** Codex (bank manifest) + Claude. **Class:** PLAN. **Agree:** C (accepted in CX-0028).

### AM-27 Early run close is explicit evidence
- **V3:** 31.7.1 CAP-38, 31.7.5 CAP-42 (evaluation result and arm reporting).
- **Current:** a run that closes before its scenario script ends is not distinguished.
- **Proposed:** "A run that the engine closes before the scenario finished is recorded as `closed_early` evidence: `ArmReport.closed_early` and `closed_early_runs`, and the same fields in the bridge copy of the stored eval report. The upstream 409 `gate_failed` body is never modified. The gate may use the count; it is never silently treated as success."
- **Evidence:** `179d4f6` (L5 review r2: closed_early in `RunRecord`/`ArmReport`/stored report); CL-0015.
- **Owner:** Codex (DTO/consumer). **Class:** V3. **Agree:** C.

### AM-28 `evaluation_in_progress` and consumed-past-deadline
- **V3:** 31.7.1 CAP-38 admission state machine.
- **Current:** `admitted` -> `consumed`; second caller undefined.
- **Proposed:** "Admission CAS is `admitted -> consumed`. A concurrent second caller on an admission already consumed and still within its deadline is denied `evaluation_in_progress` (HTTP 409) without mutating state. A consumed admission past its deadline with no stored result becomes `unknown` (never re-run with the same key). Retrying a `failed_infra` needs a new admission with `evaluation_attempt+1` (AM-03)." (Complements AM-08.)
- **Evidence:** `179d4f6`; CL-0015 "evaluation_in_progress (409) without mutating state; consumed past deadline with no stored result becomes unknown".
- **Owner:** Codex (client handling of 409 code). **Class:** V3. **Agree:** C.

### AM-29 `native_evaluate` broker digest is one broad tuple
- **V3:** 31.5.9 CAP-32, 31.7.1 (authorization check for the evaluate action) and 31.5.6 `authorizations/check`.
- **Current:** digest scope of the authorization check unspecified (narrow: proposal only).
- **Proposed:** "The `native_evaluate` broker authorization digest is `sha256` over `(proposal_id, evaluation_context_ref, candidate_hash, suite_id, suite_version, suite_digest)`; the broker check and the evaluation gate recompute the same digest from their own inputs (single implementation in `evaluation/digests.py`), so a check issued for one candidate/suite cannot authorize another."
- **Evidence:** ADR `core-bridge/docs/adr/0002` ("Canonical native_evaluate broker digest"), `179d4f6`. **Wiring:** verified in the integrated head: `tools/builder.py` imports `native_evaluate_digest` from `evaluation/digests.py`.
- **Owner:** Codex (broker verification of digest) + Claude. **Class:** V3. **Agree:** C.

### AM-30 Write-key ordinal is the index in the committed `operations` array
- **V3/plan:** CAP-32 key formula; plan 17.4.2; supersedes the "position of the action within the invocation" wording of AM-04.
- **Current:** "`ordinal` = position of the action within the invocation".
- **Proposed:** "The `RegistryMutationCommitment` carries an ordered `operations[]` of committed non-evaluate write operations (e.g. `create_proposal`, `put_draft`, `freeze`). `ordinal` is the zero-based index of the operation in that array; `stage` is `writer`; key = `pulso-w:` + `sha256(command_key|stage|ordinal)[:48]`. Evaluate is not an operation of the array. Rust computes the same golden vectors."
- **Evidence:** commit `669cfb8` (ordinal = index in `commitment.operations`); golden vectors `core-bridge/tests/l3b/test_d2_facts_and_ordinals.py`; journal CL-0012; CX-0028 ("Write ordinal is zero-based within the ordered committed non-evaluate operations. No disagreement remains").
- **Owner:** Codex (Rust vectors) + Claude. **Class:** V3/PLAN. **Agree:** C (accepted CX-0028).

### AM-31 Fact shapes as implemented (annex D.2)
- **V3/plan:** D.2 fact shapes and V3 31.5.5.
- **Proposed (consolidated):** Scout `hypotheses[] {id, statement, mechanism, evidence_refs, counterevidence_refs, missing_evidence, next_queries}`; Verifier `assessments[] {hypothesis_id, verdict, evidence_refs, counterevidence_refs, limitations}`; builder_design `{change_spec, rationale, evidence_refs, alternatives[] {id, kind in {do_nothing, proposed_change}, summary, limitations?}}` (`limitations` optional; Codex normalises an omitted value to an empty list; per CX-0021 the richer `OpportunityProjection.alternatives` with `change_ref` and `value_metric_refs` is generated downstream by Codex only). Every `evidence_refs`/`counterevidence_refs` item is an `ArtifactRef {id, digest (64 lowercase hex), media_type}`, and the bridge checks it against the artifacts the invocation actually fetched.
- **Evidence:** `669cfb8`; schemas under `facts/schemas/*.strict.json`; CL-0012; CX-0021, CX-0025, CX-0028 (accepted).
- **Owner:** Codex (Rust validators use the same shapes). **Class:** PLAN. **Agree:** C (accepted).

### AM-32 DTO additions and differences (annex D)
- **V3/plan:** annex D (CoreTaskInvocation, ArmRequest, ArmReport, AdmissionRequest); 17.3.5.
- **Proposed additions (not in annex D):** `CoreTaskInvocation` optional `registry_mutation_commitment` (writer stage only; includes ordered `operations[]`), `memory_snapshot_ref`, `extract_manifest_ref`; `ArmRequest` optional `campaign_ref` (annex D has it; re-added after the integrator pass), `seed_manifest_ref` (the bridge opens the sandbox session itself, so annex D `sandbox_session_ref` and `deadline` are absent).
- **Differences to confirm or send as a change request:** annex D `execution_profile in {attention_stateful_complementary, evolution_task}` vs our `mode in {native, task_builder, stateful_attention}`; arm `baseline|candidate` vs a free string of at most 64 characters; idempotency key is a header in annex D vs a body field; extra fields on our side `schema_version`, `agent_id`, `target_commitment`, `oracle_ref`, `supersedes_execution_id` (the models use `extra=forbid`, so Codex must send them or we drop them); `ArmReport` carries every step-8 field plus `oracle_ref`, `reason`, `detail`, `closed_early`, `closed_early_runs`; `AdmissionRequest` matches annex D plus `schema_version`; `supersedes_execution_id` must name an unknown arm of the same tenant; empty scenario list yields `failed_infra manifest_empty`.
- **Evidence:** CL-0015, CL-0016; `bridge_mock` schemas (`26dd6bd`) are our reading because no DTO schema files exist in the repo; integrator gap 2 (`ArmRequest.campaign_ref`). No Codex confirmation yet (CX-0021 declares them questions, not silence-accepted).
- **Owner:** Codex. **Class:** PLAN. **Agree:** C.

### AM-33 Podman rootless/rootful containers need `--cgroups=disabled` on `pulso-dev`
- **V3:** 31.11.1 CAP-58 (`doctor` cgroup probe), 31.11.2 (local runner), AM-15.
- **Current:** CAP-58 says rootless has no `pids`; rootful works; both connections reach the same WSL VM.
- **Proposed:** "On the Claude development machine both connections (`pulso-dev`, `pulso-dev-root`) fail to start any container with `crun: controller pids is not available`; image builds are unaffected. Local Core containers are therefore created with `--cgroups=disabled --pids-limit=0`. `podman compose` cannot express either option (and drops `x-*` keys in `compose config`), so the standalone Core runner encodes them as `com.pulso.runner.*` labels and `lib/runner.ps1` runs `podman create`. `doctor` reports `runtime_cgroup_unavailable` with sub-reasons and states that `--cgroups=disabled` removes the resource limits (limits are then not enforced locally; the doctor says so). Do not claim limit enforcement in `target=real_local` evidence while the flag is used." Replaces the last sentence of AM-15 ("never passes `--cgroups=disabled`"). Codex's `pulso-codex` machine will probably show the same symptom; Claude offers the runner as a reference.
- **Evidence:** CL-0011 environment finding; CL-0016; `85f2a66` (L8), `3ff1c98`; BITACORA 2026-10-03 14:59 UTC ("Podman pulso-dev cgroup finding"); throwaway PG16 containers on `pulso-dev` all required `--cgroups=disabled`.
- **Owner:** Claude (runner, doctor.core.ps1), Codex (aggregate doctor, V3 wording). **Class:** V3 + NONE. **Agree:** C. Related AM-15, DR-18, DR-20.

### AM-34 Broker JWT keypair and claims (A03)
- **V3:** CAP-29, CAP-05 (AM-01).
- **Current:** broker JWT minted with the callback key at first integration (flagged as known gap in the integrator entry).
- **Proposed:** none beyond AM-01; recorded so that nobody re-opens it: executor->lab-broker JWTs use a separate executor keypair, singular `scope`, `tenant_id`, `purpose`, per-attempt `jti`, `aud=lab-broker`.
- **Evidence:** `b3af773` ("A03: separate executor keypair for lab-broker JWTs; broker tools send tenant_id/purpose/singular scope"). **Owner:** Claude (done). **Class:** NONE.

### AM-35 Exporter implementation findings
- **V3:** 31.6.1.
- **Proposed (informative, confirms AM-12/AM-13):** a pending batch is persisted before POST and never overwritten (crash after ACK before cursor commit re-POSTs the same bytes -> `200 duplicate`); `evidence_refs` are `ArtifactRef` objects per annex D; tokens are per route and per attempt (`aud=control-api scope=observations`; `aud=lab-broker scope=artifact_write`); the exporter refuses to start with unexpected privileges (grant guard); rescan rows are verified against the signed event; open-run prefixes re-export without double counting; wire size margin includes the digest.
- **Evidence:** `8a820b1` (first RED: crash after ACK before cursor commit must not double count), `784f220`. **Owner:** Claude. **Class:** NONE.

### AM-36 Runtime hardening
- **V3:** 31.5.10 CAP-33 (auth of `/internal/v1`).
- **Proposed:** "The service JWT verifier requires the `tenant_id` claim, finite numeric `iat` and `exp`, per-route audience, purpose and scope, and a `jti` replay table (`pulso_bridge.jti_seen`) whose retention boundary is `now >= exp + skew` (default skew 60 s, max 60 s; plan 16.17 P2). Request bodies are bounded; expired invocation contexts are swept; the budget ledger never goes negative; the issuer for `core-credentials/issue` requires a tenant claim and TTL <= 15 min."
- **Evidence:** `4984d92` (final review), `8d620da` (L3a review), `4098240`. **Owner:** Codex (verifier parity). **Class:** V3. **Agree:** C.

### AM-37 Registry ToolDefs in the writer
- **V3/plan:** plan 17.3.3 writer tool arguments; V3 31.5.7.
- **Current:** `registry/evaluate` args `{proposal_id}` only; writer allowlist as in the plan.
- **Proposed:** "The pinned `registry/evaluate` ToolDef requires `suite_id` and `suite_version`; the writer receives them through the admission slots (sealed in the commitment) rather than model choice. The writer Agent asset allows `registry/reopen@1`, because a rejected evaluation needs `reopen -> put_draft -> freeze` before a new attempt. Request to upstream: a ToolDef variant taking only `{proposal_id}` (or default suite resolution)."
- **Evidence:** L3b gaps ("writer Agent asset lacks registry/reopen@1"; `0190f95` "reopen now allowed end-to-end in tests", `60042a9`), CL-0011 request (2). **Owner:** Claude (assets), Codex (plan text), upstream (UP). **Class:** PLAN + UP. **Agree:** C, U.

## 3b. Findings since `CL-amendments-2` (AM-38..AM-50)

Sources: journal CL-0018..CL-0022 and CX-0073/0075; `BITACORA_PULSO.md` Claude entries after the pin bump; core-bridge ADR 0004..0008 and journals claude-0009/0010; `local-identity/README.md`, `e2e-core`, `demo/README.md`; `docs/AGENT_CORE_PIN_BUMP_ANALYSIS_CLAUDE.md`; `docs/LLM_GATEWAY_ADOPTION_CLAUDE.md`; infra `agent-core-overlap-and-engine-plan.md`. Branch `claude/r-runtime-wire`, pin `789d6c8` unless stated. Each item: **Owner** and **Class** (`V3`, `PLAN`, `UP` = upstream relay via the user, `NONE`). Executed evidence is local (real Core image on Claude's `pulso-dev`, PG16); no joint H4 run.

### AM-50 Update of AM-23: `claimed` input slots are the intended upstream design
- **Change:** CL-0019 (pin-bump analysis) confirms that upstream treats run-input slots as `claimed` by design (flows read `bind_context` facts). The optional upstream request in AM-23 ("documented path for trusted run-input to become `validated`") is downgraded to a documentation request; finding F-03 (`validate` reports no violations on unreadable slots) stays upstream's.
- **Proposed V3 text:** CAP-27 / 29.8: stage inputs are `facts.binding.value.*` from `pulso/bind_context`; `CoreTaskInvocation.input` is bound by the bridge. No Rust change.
- **Evidence:** ADR 0004 (`core-bridge/docs/adr/0004-run-input-slots-via-bind-context-facts.md`), CL-0019. **Owner:** Claude (flows), Codex (V3 text). **Class:** V3. **Agree:** C.

### AM-38 Deployment tenant allow-list and `pulso:tenant_mismatch` (403)
- **Current:** CAP-33/AM-36 require a tenant claim; nothing says which tenants a deployment serves.
- **Proposed:** the runtime requires `PULSO_TENANT_ID` (optional `PULSO_ALLOWED_TENANTS`); a service-JWT tenant outside that set is rejected on EVERY route with `403 pulso:tenant_mismatch` (not 404, not 401). The Rust client treats it as a non-retryable configuration error. Add to the D.1 error table.
- **Evidence:** commit `0c273ec`; e2e-core `test_05_restart_and_tenancy` (xfail flipped to an assertion); CL-0020 contract facts (2). **Owner:** Claude (runtime), Codex (client mapping, D.1). **Class:** V3. **Agree:** C.

### AM-39 `pulso:stage_agent_mismatch` (422)
- **Proposed:** invoking a stage whose agent/pin does not match the stage catalogue pairing is `422 pulso:stage_agent_mismatch` with zero effects. Add to the error table next to AM-38.
- **Evidence:** commit `0c273ec`, e2e-core live tests; CL-0020 (3). **Owner:** Claude / Codex (table). **Class:** V3. **Agree:** C.

### AM-40 Admission bound to tenant, job_id and `binding_ref`; evaluate-only path proven (A04)
- **Current:** AM-20/AM-28 describe admission and `evaluation_in_progress` without binding the admission to the invocation.
- **Proposed:** an evaluation admission is bound to (`tenant`, `job_id`, `binding_ref`) of the evaluate-only invocation that consumes it; `binding_ref = sha256_text("<tenant>|<Idempotency-Key>")`, computable by the engine BEFORE dispatch, so it can pre-authorize. A different job or key cannot consume it. `evaluation_in_progress` (409, no state change) is a documented code (AM-28). Receipts of evaluate-only runs carry `native_evaluation{eval_run_ref, report_digest}` and `candidate_hash`; no reopen happens. The evaluate-only invocation (frozen proposal + `evaluate_enabled` -> evaluate -> verify -> end) is the A04 native path and is proven end to end.
- **Evidence:** commits `ed28bdb`, `e64bccf`, `47326e8`; e2e-core admission and consumed-admission assertions; CL-0020 (1)(4). **Owner:** Claude (runtime), Codex (compute `binding_ref`, parse receipt fields). **Class:** V3. **Agree:** C.

### AM-41 Dependency-failure evidence (no new receipt outcome)
- **Previous proposal:** LLM adoption doc 2.7/6 proposed a `dependency_unavailable` outcome classified from our model-call ledger.
- **Agreed (supersedes that proposal):** per CX-0073/CX-0075 and CL-0021/CL-0022, only a correlated, schema-valid audit event `type=agent_step`, `payload={node_id, step, kind:"failed", error_kind, latency_ms}` with `error_kind in {timeout, unavailable, rate_limited, invalid_output, refused}` classifies a dependency failure. The task receipt keeps its outcomes (`terminal_failed` / `escalated` / `unexpected_outcome`) and exposes `core_run_id` for correlation; RunResult `gave_up` is never reinterpreted. The exported observation is a `core_event` (`native_event_id`, `source_event_digest` = audit hash, `source_run_ref` = `core_run_id`, `source_sequence` = seq, `coverage_marker`, `source_event: null`); chain order and gap semantics are unchanged. A legitimate low-confidence run has NO failed `agent_step`. Spend stays a bridge-side guard; the `ModelReceipt` mapping stays Codex's (V3 section 23).
- **Evidence:** CL-0022; sanitized fixtures `core-bridge/tests/fixtures/dependency_evidence/` (real Core + real exporter, PG16); commit `703a0a9`. **Owner:** Codex (engine classification), Claude (fixtures). **Class:** V3. **Agree:** C (CX-0073/0075).

### AM-42 HumanAuthorizationPort rules
- **Current:** CAP-44 / plan 16.13.2 describe the authorization JWS but not where binding enforcement lives.
- **Proposed:** Core checks only signature, `auth.level=step_up`, role and `exp`; it ignores the binding attrs and the Principal has no `jti`, so a JWS is replayable for its 60 s lifetime. The port MUST (1) atomically consume a durable single-use intention, (2) assert the binding (operation, target, hash, revision, tenant, actor) from values READ FROM THAT INTENTION, never from the request (`local_identity.client.assert_bound`), (3) pass `now` from its own clock, (4) send the same JWS bytes to Core. Never log or persist the JWS. Real-profile human authority stays `dependency_blocked` (CAP-44).
- **Evidence:** CL-0022; `local-identity/tests/test_review_hardening.py`; e2e-core `human_port` and `test_07_human_approval.py` (replay -> `IntentionConsumed` and Core `illegal_transition`; wrong hash -> `candidate_changed`). **Owner:** Codex (real port), Claude (stand-in). **Class:** V3+PLAN. **Agree:** C.

### AM-43 local-identity routes, claims and errors (sandbox human issuer)
- **Proposed (plan 16.13.2 / D.1 text):** internal port 8083, never deployed to staging or prod. `POST /internal/v1/human/session-assertions/issue` `{tenant_id, actor_ref, session_intent_ref, nonce}` -> `{assertion, kid, exp}`; `POST /internal/v1/human/command-authorizations/issue` `{tenant_id, actor_ref, command_ref, operation, target, challenge_ref, nonce}` -> `{authorization_jws, kid, exp, metadata{auth_simulated, operation, binding_digest}}`. Service JWT `aud=human-issuer`, TTL <= 60 s, skew 60, fresh `jti`, receiver-owned replay table. `authorization_jws` is a Core `principal+jws` (`kid local-sim-human-*`, roles constructor+aprobador, `admin` only for `revoke`, `auth.level=step_up`, `auth.simulated=true`, exp +60 s); `binding_digest` is sha256 of the sorted compact JSON of the binding. Errors (D.1 envelope): `pulso:auth_invalid` 401, `pulso:auth_denied` 403, `pulso:service_token_replayed` 401, `pulso:tenant_mismatch` 403, `pulso:actor_not_allowed` 403, `pulso:role_not_allowed` 403, `pulso:nonce_replayed` 409, `pulso:invalid_request` 422, `pulso:payload_too_large` 413. Start guards exit 2 `local_identity:{profile_not_local, remote_environment, kid_not_local, key_reuse, service_keys_invalid, identities_invalid}`; the CAP-63 scan fails on `local-sim-*` kids or `auth.simulated=true` in remote config. Only the PUBLIC human key goes into the local Core staff set.
- **Evidence:** `local-identity/README.md`; proof against real Core `789d6c8` (bot `forbidden_role`; session-level JWS `step_up_required`; approve then publish moves staging only; promote moves prod only when explicit; admin-only revoke; replay `illegal_transition`; expired `principal_expired`); local stack service `human-issuer` (commit `c190dca`). **Owner:** Claude (service), Codex (control-api caller, D.1). **Class:** PLAN. **Agree:** C.

### AM-44 `release_settings` drafts denied by default (N-07)
- **Current:** V3 31.5.7 and the plan writer allowlist do not mention release-level settings, which N-07 lets a draft replace wholesale (interrupt list, `max_input_chars`).
- **Proposed:** the protected writer denies any `registry/put_draft` whose changes contain `kind: release_settings` (`pulso:release_settings_not_allowed`, zero effect, checked before the commitment, so a committed digest cannot carry it; variants of the kind are covered). Re-enabling needs a Pulso-side guardrail (role, diff against the base, caps). **UP:** NF-01 asks Agent Core for a stronger role or a base-vs-candidate diff and a cap on `max_input_chars`.
- **Evidence:** ADR 0008 consequences; `core-bridge/tests/l3b/test_release_settings_denied.py`; findings NF-01. **Owner:** Claude (guard), upstream (gate). **Class:** V3+UP. **Agree:** C, U.

### AM-45 `ReleaseDetail` gains four fields at `789d6c8`
- **Fields:** `interrupts`, `language_detection` (required), `injection_ruleset`, `max_input_chars` (required) (N-03/N-07). Strict Rust DTOs must accept them in the same change as the wire; reference sample `core-bridge/wire/agent_core@789d6c8/golden/hash_vectors.json::release_detail`. Content, release and candidate hash vectors are byte-identical to `86a7674`.
- **Also:** N-10 adds `eval_run_id` to the `gate_failed` 409 body; N-02 adds alias-read and versions-read routes (route table 18 in our mock). Annex D should list them.
- **Evidence:** CL-0019/CL-0021, ADR 0008, parity cases. **Owner:** Codex (DTOs), Claude (wire). **Class:** PLAN. **Agree:** C.

### AM-46 Pin identity: SHA + wire MANIFEST digest, never `contracts/VERSION`
- **Proposed (A02 / CAP-03 / CAP-11):** `contracts/VERSION` stayed `1.3.0` across 11 upstream commits and the whole bump, so it is not a drift signal. Identity is the checkout SHA plus the `manifest_sha256` of `wire/agent_core@<sha7>/MANIFEST.json`. For `789d6c8` the digest is `890edd7aeea261061d3e0dad2268900f9dc52c15ebe0f76781f7e3bec35d6565`; it supersedes `79758b46...` quoted in CL-0019, CL-0021 and the BITACORA 19:00Z entry (derived output schemas now use serialization mode; golden hashes unchanged). PR #76 still carries the older digest; a follow-up carries the corrected wire. `scripts/core/pin-watch` reports drift verdicts (no-change, additive-safe, needs-bump-work, breaking).
- **Evidence:** ADR 0008; `core-bridge/docs/journal/claude-0010-ci-parity.md` (`contract-drift` PASS with that digest). **Owner:** Claude. **Class:** V3. **Agree:** C.

### AM-47 Key delivery from Fargate secrets
- **Current:** CAP-60/62 treat keys as mounts; Fargate delivers secrets only as environment variables at task start.
- **Proposed:** `docker-entrypoint.sh` materialises identity, staff and service key files from env secrets before start; a rotated secret needs a new task (N-09 hot reload re-reads the file but cannot change env). Gaps found (infra reconcile entry in BITACORA, ADR 0008 item 6): the entrypoint has no path for the four bridge signer seeds and two exporter key seeds; the generic `workload` module has no tmpfs, so key files land on ephemeral task storage. A corrupt key file keeps the previous keys (cannot revoke, NF-04); `last_reload_error` is visible at `/internal/v1/version`, and our readiness fails on key reload errors.
- **Questions:** tmpfs in the Core workload slice; who runs the `pulso_bridge` DDL (see `AGENT_CORE_RELAY_FOR_USER.md`). **Owner:** Claude (entrypoint), infra owner (module), user. **Class:** V3+UP. **Agree:** C, O, U.

### AM-48 LLM gateway consumer: configuration, fail-closed behaviour, receipt fields
- **Current:** V3 lines 758-762/798, CAP-50, CAP-60, CAP-62 and plan F6 describe an in-runtime `OpenAICompatGateway`, `LLM_ENDPOINTS` and provider egress.
- **Proposed:** Core calls the external llm-gateway through `HttpLLMGateway` (AC ADR 0024); our wrappers (binding guard, spend metering) still wrap the Core port. Config names: `AGENTCORE_LLM_GATEWAY_URL` and `AGENTCORE_LLM_GATEWAY_TOKEN` (both required unless `PULSO_LLM_MODE=disabled`, for fixture tests only; the placeholder token `unset` is rejected), `PULSO_LLM_STAGE_POLICY` / `PULSO_LLM_STAGE_POLICY_JSON`, `PULSO_LLM_POLICY_REQUIRED`, `PULSO_EVAL_BUDGETS_JSON`, plus `PULSO_TENANT_ID` (AM-38). Fail closed: missing or half config exits 2 naming the piece (never a silent `UnconfiguredLLMGateway`); `/readyz` includes gateway reachability/auth probe and key reload errors; metering v2 counts failed calls with usage and over-cap spend, honours `usage_known` and writes `model_call_ledger` (metadata only). The runtime needs gateway reachability only, no provider keys or egress; engine environments hold no gateway URL, token or provider key (the Rust engine never calls an LLM). `ModelReceipt.provider_request_id` and a true `resolved_route` cannot be filled (the gateway returns only the provider-reported `model`): record `model_as_reported` and our own request id and mark the provider id unavailable. Template fallback on `respond/generate` nodes is Core behaviour, labelled `degraded_generation` for the demo world only.
- **UP:** gateway questions in `AGENT_CORE_RELAY_FOR_USER.md`. **Evidence:** commits `bf7f06c`, `10c3569`, `637f1d1`, `703a0a9`; e2e-core `test_06_gateway_consumer.py`; LLM gateway adoption doc. **Owner:** Claude (runtime), Codex (V3 text), user (relay). **Class:** V3+UP. **Agree:** C, U.

### AM-49 Export boundary
- **Note (no text change):** upstream N-08 `/v1/export/*` has no outbox, re-serialises event JSON, handles no holes and needs an `exporter` staff credential; the runtime keeps `/v1/export` OFF by default (`PULSO_CORE_EXPORT_ENABLED`) and our read-only PG exporter stays the ingest path. Upstream cursor issue NF-02 (bigserial assigned at INSERT, not COMMIT) is in the relay.
- **Evidence:** ADR 0008 decision 3, findings NF-02. **Owner:** Claude. **Class:** NONE.

## 4. Agreement summary

| Needs Codex (C) | AM-01, 02, 03, 04, 05, 07, 09, 10, 12, 13, 15, 16, 18, 19, 20, 22, 23, 25, 26, 27, 28, 29, 30, 31, 32, 33, 36, 37, 38, 39, 40, 41 (accepted CX-0073/0075), 42, 43, 44, 45, 46, 47, 48, 50 (AM-24, 26, 30, 31 already accepted in CX-0021/0023/0025/0028) |
|---|---|
| Needs owner/user (O) | AM-02 (execution boundary), AM-16 (signature custody, ADR 0003), AM-17 (module/topology wording) |
| Upstream agent-core (U) | AM-07 (N-12), AM-15 (`--app-role` grants), AM-37 (`evaluate` ToolDef), AM-44 (release_settings gate), AM-47 (tmpfs), AM-48 (gateway questions); the AM-23 upstream request is dropped (AM-50) |
| No agreement needed (NONE) | AM-06, 08, 11, 14, 34, 35, 49 |
| Plan-text fix only | AM-21, AM-24 (Claude's section 17.3.5), AM-26, AM-30, AM-31, AM-32 |

Highest priority before the real-profile claim: AM-38/AM-40/AM-42 (tenant set, admission binding, human port rules), AM-45 (strict DTOs), AM-23 (inputs through `bind_context`), AM-04/AM-30 (key formula), AM-07/AM-24 (harness and run counts), AM-02 (evaluate mode), AM-13 (observation contract).

## 5. Process

1. Items marked accepted by Codex in the journal still need the text applied by the canonical-spec owner; this file is not that application.
2. Claude does not edit `TECH_SPEC_PULSO_AUTOMEJORA_V3.md` or plan sections 1-16. Codex replies by entry id; a rejection is a change request, resolved jointly.
3. Revision `CL-amendments-2` superseded the scratchpad revision `CL-definitions-1` for AM-01..AM-22 and added AM-23..AM-37; revision `CL-amendments-3` adds AM-38..AM-50 (section 3b). AM-41 supersedes the `dependency_unavailable` outcome proposed in `LLM_GATEWAY_ADOPTION_CLAUDE.md` 2.7/6.
