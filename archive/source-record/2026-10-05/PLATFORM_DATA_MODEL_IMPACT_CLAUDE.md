# Platform data model: impact on the Pulso detection and self-improvement engine

Author: Team Claude (leader). Date: 2026-10-03. Status: analysis for decision; no spec edit made yet.
Inputs: the Product team's data-model artifact (claude.ai/artifact/BWx4saeWfYsLbQEbkNKMPg, "LATAM Bank Support Platform: Data Model"), `TECH_SPEC_PULSO_AUTOMEJORA_V3.md` (§3, §7 F7/F8, §24, §24.1, §28), `pulso_muestra_e0/contratos/platform_history.json` v0.5.1, and `PLAN_DOS_EQUIPOS_CODEX_CLAUDE_V3.md`.

Scope: this document analyses only the data-model artifact. The Product team is a separate group of humans we cannot contact; open questions in section 7 go to the user for relay, not to the shared journal.

## 0. Framing from the Product team: three phases, and the no-regression rule

Product's plan, as relayed by the user:

1. **Phase 1: a functional support platform.** The model in the artifact is the *minimum the platform needs to work*. It has no AI. It is also part of our input.
2. **Phase 2: trees, flows and agents on top of the platform, together with Agent Core and us.** This is what the Agent Core team is already building.
3. **Phase 3: detection of improvement opportunities, analysis, evaluation and proposal to apply them.** This is the Pulso engine, i.e. spec V3.

Consequences:
- **The V3 spec is the target and does not regress.** The artifact is the Phase 1 state of the source, not a replacement contract. Everything V3 defines for E0/`platform_history` 0.5.1 (Core artifacts as the output, the grades, the gates, the AI-layer detector families) stays as is. Phase 1 data only narrows what can run *today*.
- **Earlier remarks in this analysis that "findings should not all go through Agent Core" are withdrawn.** Product sees Agent Core as step two, not as a mismatch. Until Phase 2 exists there is simply nothing in the platform for a Core artifact to replace, so Phase-1-only findings stay as evidence/insight, not as publishable proposals. No new product promise is made.
- **Design rule: additive only.** Every change below is additive and behind a capability profile, so a source that later gains `routing_step`, `tool_call`, `identity_check`, etc. (the synthetic `platform_history` 0.5.1 is almost certainly the Phase 2/3 shape of the data) lights up the existing detector families with no code change to them.

## 1. What the artifact says (the facts that matter to us)

The real platform today (Phase 1) is a deliberately small **subset** of the synthetic `platform_history` contract the spec was built on.

| Aspect | Real platform (artifact) | What V3 assumes (E0 / `platform_history` 0.5.1) |
|---|---|---|
| Storage | SQLite, portable to Postgres, 11 tables | Parquet files read through `SourceStore` (file:// or s3://) |
| Conversation data | `cases`, `turns`, `assignments`, `customer_case_slots`, `event_log`, `customers` | `case, identity_check, turn, routing_step, copilot_query, tool_call, approval, suggestion, case_close, signal, component` |
| Case fields | no `origin`, no `topic`, **no `complaint_id`** | all three present; `complaint_id` is the declared bridge to the bank dataset |
| Close | folded into `cases` (`close_reason` enum, `close_note`); no `resolved` bool, no `resolution_code`, no CSAT | separate `case_close{resolved, contact_reason, resolution_code, followup_at, csat}` |
| Routing | direct assignment to a person (`assignments`: reason, `policy_rule_id` H1, strategy, `open_cases_at_assignment`, `waited_seconds`, `previous_staff_id`, `paused_override`) | `routing_step` over tiers (classifier/tree/AI/human) |
| Channels | `app_chat`, `web_chat` | `phone, email, web_chat, app_chat` |
| AI features | none: no tool calls, identity checks, copilot, approvals, suggestions, signals, components | all present as team-generated history |
| Event log | one append-only `event_log` with a **global contiguous `sequence`**, `event_id`, `event_type`, `entity_id`, `case_id`, actor, `event_time` AND `ingested_at`, JSON `payload` | no global event log; `ingested_at` physically absent in every E0 table (replay-mode assumption) |
| Mutation | `cases`, `staff`, `customer_case_slots` are mutable (optimistic `version`); `turns`, `assignments`, `event_log` are append-only | history tables assumed immutable facts |
| Planned | `teams` table, `staff.team_id`, `admin_roster`, new `staff.*`/`team.*` events; conversation tables unchanged | n/a |

The artifact's own conclusion: if the AI team connects to the real platform, "the data they will find are cases, messages, assignments, closures and people events"; everything else exists only in the synthetic sample.

## 2. What changes for our system versus spec V3

### 2.1 Things that get easier or better than the spec assumed

1. **Real `ingested_at`.** V3 §28.2/§28.6 forces "replay mode" (availability assumed at event time, `ingestion_lag=0` labelled as an assumption) because `ingested_at` is absent in E0. The real `event_log` has both `event_time` and `ingested_at`, so `available_at` becomes a measured value and late events become detectable (the spec already requires window revision and dependent-signal revalidation for late events).
2. **A global, gap-checkable cursor.** Core has no global cursor (order only inside a run), so §24 admits we cannot prove no gaps across runs. The platform `event_log.sequence` is a single total order, and `turns.sequence` is gap-free per case. That gives `PlatformObservationBatch{from_seq,to_seq}` a real source position (`kind=platform_event`, `source_sequence` non-null) and a completeness proof the Core path cannot offer. Caveat: a SQL autoincrement sequence can skip values after rolled-back transactions; a gap is a "verify with the owner", not automatically data loss.
3. **Exact recontact linkage.** `cases.previous_case_id` plus the one-open-case-per-customer rule is a platform-declared identifier relationship, which is exactly what §24.1 requires before counting a recontact ("deduplicate only by an accredited external identifier/relationship"). Close reasons (`customer_unresponsive`, `duplicate`, `out_of_scope`, `resolved`, `other`) let us separate declared outcomes from verified ones.
4. **Operational ground truth for queueing and load.** `waited_seconds`, `open_cases_at_assignment`, `policy_rule_id` (H1 language rule), `paused_override`, `sla_due_at`, `first_response_at`, `analyst_availability` and `case.viewed`/`case.read` events allow exact first-response, queue-wait, reassignment and workload measures with denominators, without the inference E0 needs.
5. **Mutation is observable through events.** State transitions are logged (`case.status_changed`, `case.assigned`, `case.closed`), so as-of reconstruction is possible without reading the mutable row.

### 2.2 Things that get harder or must be marked unsupported

1. **The bridge to the bank dataset is gone.** No `complaint_id`, no `topic`, no `origin`. Linking a platform case to a bank complaint or transaction can only be `unlinked` or `mechanism_proxy` through an explicit customer mapping (`CUS-…` pseudonymised vs `customers.customer_id`, which V3 §28.2 already says is not a direct join). Practical effect: on the real platform the grade `same_outcome_linked` is unreachable; findings about disputes/charges cannot be sustained from platform data alone.
2. **Most detection families lose their evidence.** The spec's families need `routing_step`, `tool_call`, `identity_check`, `approval`, `copilot_query`, `suggestion`. Real platform detectors can only use: first-response and SLA, queue wait, language-eligible assignment (H1), reassignment churn, load imbalance, close-reason mix, reopen/recontact chains, message volume/turn patterns, availability, and supervisor access. The existing rule applies and is correct: "human resolves with stable pattern" without human action evidence is `insufficient_human_evidence`; tool/AI-layer hypotheses are `unsupported` with the missing capability named. No fabricated fill-in (§28.2: "suggestion/component absent means capability not present").
3. **Phase 1 findings have no Core artifact to change yet.** The data supports operational findings (SLA, language queue wait, load imbalance, reassignment churn), but today the platform has no trees, flows or agents, so there is nothing for a Core proposal to replace. This is the expected Phase 1 state, not a gap in V3. Handling: these findings are produced with full evidence and denominators and stop at `insufficient_*`/`unsupported` for the proposal step (the existing fail-closed behaviour). Their authority class is (b) platform governance if anyone wants to act on them (§24.1). Optional, non-regressive: a read-only insight view; no new publishable output class is introduced.
4. **State is mutable on the cases table.** Reading `cases` at extraction time leaks the future (final `status`, `close_reason`, `assigned_analyst_id`, `version`) into a cutoff-dated extract. Consistency with §28.2 ("case_close only after closed_at; windows only after window_end; labels never in discovery reads") requires deriving state from `event_log` (and append-only `assignments`/`turns`), using the table only for dimensions with a snapshot digest.
5. **Sensitive tables must never be ingested.** `login_accounts` (password hash, lockout), `mfa_challenges`, `staff_sessions`, staff email/name are credential or personal data with no detection value for us. Auth events (`auth.*`) are security telemetry: allow-list by event type; default deny. `turns.text`, `staff.name`, `customers.display_name` follow the existing "treatment before ModelPort" rule (§28.2) and the local-only egress rule if the data is not authorized for hosted models.
6. **Synthetic customers inside the real platform.** `customers.simulator` and `suggestions` (demo data) mean the real database contains demo rows. They must be tagged `evidence_kind=team_generated`/excluded from population statistics and from value claims, or findings would count demo traffic.
7. **Schema is moving.** `teams`, `staff.team_id`, `admin_roster` and new `staff.*`/`team.*` events are coming. The Rust U29 DTOs are `deny_unknown_fields` (CL/DR-10), so an additive event type would fail a batch. Required behavior: unknown `event_type` is counted and quarantined with a quality finding, never a hard batch failure, and new types are admitted by a versioned allow-list.
8. **Case ids collide by design.** `CASE-…` is a platform identity; V3 §28.2 already says a `case_id` equal to a `complaint_id` is not the same entity. Source namespace must be explicit (`source_namespace=platform_live`), distinct from E0 case ids.
9. **SLA constants.** `sla_due_at` is platform-supplied (5/15/60 min by priority). V3 §24.1 says SLA must come from policy/country/calendar. Treat the field as a platform-declared value with provenance; do not generalize the 5/15/60 minutes or claim "regulatory violation"; pauses and hold are not modelled (only analyst availability), so waiting time is elapsed time with a labelled assumption.

### 2.3 Spec V3 sections that need an additive amendment (proposed, not applied)

| Section | Change |
|---|---|
| §3 | Add a second source family: a live/operational platform database (not only the 13 CSVs/Parquet). Source is read-only, snapshot-by-cursor, never written. |
| §7 F7 / §24 / §24.2 | Make `platform_event` concrete: the real event catalog (cases, `turn.created`, `staff.availability_changed`, allow-listed `auth.*`), `source_sequence = event_log.sequence`, real `available_at = ingested_at`, per-case `turns.sequence` completeness. State that the batch is two-level as for Core. |
| §28.2 / §28.6 | Add `PlatformLiveAdapter` beside `EnrichedHistoryAdapter`; define the **capability profile** (which of origin/topic/complaint_id/identity_check/routing_step/tool_call/approval/suggestion/case_close/csat exist) so detectors compute denominators and emit `unsupported`/`insufficient_*` from the profile, not from ad-hoc checks; channel set differs; `close_reason` vs `resolved` semantics. |
| §24.1 | No new output class required. Optionally note that findings without a Core target in Phase 1 end at `insufficient_*`/`waiting_dependency` and are exposed as read-only insight; the Core-artifact output of V3 is untouched. |
| §5 | No new tables. Cursor, batches and manifests reuse existing `pulso_*` artifacts/cursors (the spec's rule "no new domain tables" holds). |
| §20 / §25 | Coverage view per source: capability profile, per-detector eligibility, late-event revisions, gap/quarantine counters. |
| §30.8 | New catalog entries (section 5) with first RED per unit. |

## 3. Who should do what

Rule of thumb from the existing split: Codex owns the Rust engine (detection, evidence, proposals, evaluation); Claude owns everything at the boundary of external systems (bridge, exporter, mocks, console, infra for our own services). The platform integration has the same shape as the Agent Core one, so I propose the same split.

### 3.1 Team Codex (engine core, Rust)

| ID | Work | Why Codex |
|---|---|---|
| PL-C1 | Rust `PlatformLive` source adapter and `platform_event` mapping in the U29 ingestion path: closed event catalog + quarantine of unknown types, `source_sequence`/gap rules, `available_at=ingested_at`, late-event revision, as-of reconstruction from events (no future leakage) | owns U04/U29 DTOs and §28.2 projection |
| PL-C2 | Capability profile in the source contract and its use by detectors (U30): operational families on the real subset (first response/SLA, queue wait/H1 starvation, load imbalance, reassignment churn, close-reason mix, recontact via `previous_case_id`), explicit `unsupported`/`insufficient_*` for the missing families | detector semantics and denominators are the engine |
| PL-C3 | (deferred, optional) read-only insight surface for Phase 1 findings that have no Core target; no change to the proposal model of §16/§17 | keeps V3 intact |
| PL-C4 | Privacy treatment for the platform fields (turn text, staff and customer names), allow-list of tables/events, credential tables denied by construction | engine privacy gate |
| PL-C5 | Evaluation on this data: no oracle exists for these findings; define what "improvement" means for an operational recommendation (replay/simulation of assignment policy against history, holdout by time) | gate semantics are Codex's (U19/U35) |
| PL-C6 | Spec amendment text for the sections in 2.3 (Codex edits the canonical spec; Claude supplies review) | spec canon is edited by the owner of the semantics |

### 3.2 Team Claude (boundary, parallelizable now)

| ID | Work | Why Claude |
|---|---|---|
| PL-L1 | **Platform exporter** `platform-exporter` (mirror of `core-exporter`): read-only cursor over `event_log` (and the append-only conversation tables), emit `PlatformObservationBatch` to `POST /internal/v1/platform/observations`; digest, retry until durable ack, backfill by sequence, schema-drift tolerant | same pattern, code and deployment as the existing exporter |
| PL-L2 | **Platform simulator**: extend `platform-sim` with a generator that reproduces this exact model (11 tables, event types, `sequence`, `ingested_at`, mutable `cases`, demo `simulator` rows, late events, gaps, unknown event types) plus the planned `teams`/`staff.team_id` evolution, so it is the Pulso-side double of the platform, as `core_mock` is for Core | existing ownership of `platform-sim` and mocks |
| PL-L3 | **Contract pack for the platform**: JSON Schemas for the allow-listed tables and the event catalog, golden examples, conformance suite (same approach as `bridge-contract/`), drift check against the artifact version; this is also what Codex tests against | already building this style of pack |
| PL-L4 | Console views: source coverage/capability profile per source (with the Phase 1/2/3 level), platform event feed, late-event/gap/quarantine counters, read-only insight cards for Phase 1 findings | console is Claude's |
| PL-L5 | Infra for our side: read-only credentials secret for the platform DB (not ours to own), reader role/SG for the exporter, tmpfs/secret delivery as in ADR 0009, shared Cloud Map name; no duplication of the platform's own infra | infra for our own services |
| PL-L6 | Real-dependency tests: exporter against real SQLite and real Postgres (platform says SQLite, portable), Podman; end-to-end exporter → control-api stand-in → batch ack with gap/late/unknown-type cases | Podman test discipline already in place |

### 3.3 Parallelism and ordering

- **Can start today, in parallel, without waiting on Codex:** PL-L2 (simulator), PL-L3 (contract pack), PL-L1 (exporter against the simulator), PL-C6 (spec amendment text), PL-C4 (allow-list/privacy design). PL-L1/L3 depend only on the DTO already agreed for `PlatformObservationBatch` (CLQ-07, X-3).
- **Optional:** PL-C3 (insight surface) is deferred; PL-C5 shrinks to "what evidence is enough to stop at insight" because no candidate is evaluated in Phase 1.
- **Sequential:** PL-C1 ← PL-L3 golden vectors; PL-C2 ← PL-C1; PL-L6 end-to-end ← PL-C1 landed or its stand-in.
- **Does not block the "magic demo".** The demo runs on E0/synthetic data and Core. Real-platform ingestion is a second demonstration (an operational finding, e.g. Portuguese queue wait, ending at documented insight), valuable because it is the only dataset that is genuinely the product, but it is a phase after the Core connection.
- **Capacity:** Codex is currently saturated with the Core engine and cannot reach GitHub; assigning it only PL-C1..C6 (all semantic) is the minimum. Everything else is Claude's and parallel.

## 4. Risks if we do nothing (or if we over-adapt)

- Detectors trained on E0 would silently run on a platform that lacks their evidence and report empty or wrong findings; the capability profile makes this explicit.
- A `deny_unknown_fields` batch breaks on the first new `staff.*`/`team.*` event.
- Reading mutable `cases` leaks the future into discovery and invalidates evaluation.
- Demo/simulator customers inflate statistics and any value claim.
- Over-adapting V3 to the Phase 1 subset would regress the spec; keep changes additive and profile-gated.
- Credential tables are one careless `SELECT *` away from entering a lab.

## 5. Proposed new catalog entries (for §30.8, first RED each)

| ID | First RED |
|---|---|
| PL-01 source contract for platform_live | a read of `login_accounts` is refused before any query; allow-list proves the 6 conversation tables + event_log |
| PL-02 event catalog and quarantine | an unknown `event_type` produces a counted quality finding and the batch is still acked |
| PL-03 cursor and gaps | skipped `sequence` yields `gap_suspected` and a backfill request, not silent acceptance |
| PL-04 available_at | late event (`ingested_at` after window close) triggers window revision |
| PL-05 as-of reconstruction | a case closed after the cutoff appears open in the extract; `close_reason` is absent |
| PL-06 capability profile | a tool-call detector against this profile returns `unsupported` naming `tool_call`; the profile is versioned by phase and a superset profile (0.5.1 shape) enables it |
| PL-07 recontact | `previous_case_id` chain counted once; `customer_unresponsive` close not counted as failure by default |
| PL-08 simulator rows | `customers.simulator=true` excluded from population and flagged `team_generated` |
| PL-09 SLA | `sla_due_at` breach measured with provenance label; no "regulatory" wording |
| PL-10 phase gating | a Phase 1 finding with no Core target stops at `insufficient_*`/`waiting_dependency` and never reaches `publish`; when the profile later declares routing_step/tool_call, the same detector runs with no code change |

## 6. Recommendation

1. Treat the artifact as the **Phase 1 profile** of the source contract. E0 / `platform_history` 0.5.1 stays the rich world for the demo and is the likely Phase 2/3 shape of the real data; V3 is not changed in substance.
2. Make the capability profile **versioned by phase**, so growth of the platform enables detector families without touching them (no regression, no rework).
3. Approve the split in section 3: Claude starts PL-L2, PL-L3, PL-L1 now (disjoint from Codex's files); Codex takes PL-C1, C2, C4, C6 after the current E0 branch lands. PL-C3 and most of PL-C5 are deferred.

## 7. Open questions for the Product team (via the user; not the journal)

0. What is the roadmap for Phase 2 data (routing, tool calls, approvals, identity, suggestions)? Will it follow the `platform_history` 0.5.1 entities, and which release brings each?
1. How will Pulso read the platform: read-only DB access, a replica, or an exported snapshot/feed? Is there an API with `after_sequence` paging?
2. Payload schema per `event_type` (especially `turn.created`, `case.assigned`, `case.status_changed`, `case.closed`): which fields, and does any payload carry message text?
3. Is `event_log.sequence` contiguous even after rolled-back transactions? Can `ingested_at` be trusted as the commit time?
4. Will `origin`, `topic`, `complaint_id` ever exist on real cases? Without `complaint_id`, is there a planned customer id mapping to the bank dataset?
5. Will AI-layer facts (tool calls, identity checks, approvals, close outcome `resolved`, CSAT) be captured by the platform, and when? This decides which detector families can ever run on the real source.
6. Which rows are demo (`customers.simulator`, `suggestions`)? Is there a stable marker to exclude them?
7. Timeline for `teams`, `staff.team_id`, `admin_roster` and the new event types; will event types be versioned?
9. Retention/redaction rules for message text and staff data, and whether the data may reach hosted models or must stay local (E0 rule: local only).
