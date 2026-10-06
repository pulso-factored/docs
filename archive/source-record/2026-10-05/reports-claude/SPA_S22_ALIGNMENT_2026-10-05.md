# SPA S22 alignment (support-platform main 6ce2581) - 2026-10-05

Read-only. Sources: `origin/main` 6ce2581 (S22 #23, S21 #19), open PR #24 (frontend layout fixes only, no backend/contract change, no effect on us), our PR #17 (`feat/builder-proposal-announce`, merge base aecab6d), engine `claude/w12-dossier` (3832b6e3), Codex `DOSSIER_SPEC.md`. Paths below are in support-platform unless stated.

## 1. What S22 gives the magic experience, and where our proposals appear

Supervisor-only section "Automatizacion" (rail item, only while AI is on; dot when a type is `ready`): `/supervision/automation` (case type panorama + type panel), `/automation/proposals` (list), `/automation/proposals/:id?type=` (one proposal), `/automation/agents[/:id]`, plus builder chat with "Nueva conversacion" (`docs/platform/api/slice-22-automation.md` s1-s3).

Our proposal surfaces in exactly three places:
- **Proposals list** (`ProposalsScreen.tsx:100-126`): title, agent, state glyph, source, updated. `proposalSource` already accepts `engine` and draws a sparkles icon plus "Del motor de mejora" (`proposals.ts:75-83`; contract s3 last paragraph: "ready for the improvement engine (PR #17, not merged)"). It reads `GET /builder/proposals`, so PR #17's announce is what feeds it.
- **Proposal detail** (`ProposalScreen.tsx:47` title = `proposal.title`; `:203` each change card = kind badge, entity id, version, `docs.description`, `Why: docs.rationale`, `Changelog: docs.changelog`; `:100-118` "Herramientas/Idiomas" from the agent entity only). Then stepper Borrador..Activa, the real approve/reject/publish with TOTP step-up dialog, the evaluation report gate by gate (`EvaluationReport.tsx`), and "Siguiente paso" by state.
- **Agent page / type panel**: type panel lists proposals whose `agentId` equals the type's agent (`TypePanel.tsx:209-250`); agent page lists its proposals, prod rollback and "Pasar a producción".
- The notification bell is NOT touched by S22: `main` has no `improvement_proposed`. Only PR #17 adds it, and its target is `PATHS.supervision.root` (PR17 `model.ts` diff), not the proposal.

Approval path: all registry data (proposal, draft changes, eval report, aliases, releases) comes from agent-core via the platform's `/builder/*`; the platform DB holds only the proposals index (`builder_proposals`: title/state cache, source, registered_by), stages/agent_id per type (`case_type_maturity`) and audit. Step-up is a fresh 6-digit authenticator code per decision (approve, reject, publish, prod promotion, activation), wrong code shows attempts left, 423 locks (contract s3 "(decisions)"). Evaluate needs an `eval_suite` in the draft or on the base release, else 404 "Este agente no tiene suite de evaluacion" and nothing can be approved (s6, first gap).

## 2. Conflicts with PR #17 and the minimal rebase

`git merge-tree` main vs pr17: content conflicts in 5 files, all mechanical. Logic does not overlap: S22 added no announce, no `engine` source adoption, no notification change. S22 explicitly anticipates PR #17 (`source` read as text, `engine` label) and says nothing depends on it.

Conflicts and fixes:
1. `application/ai/use_cases.py`, `bootstrap/container.py`: S22 touched `_build_builder`/`_build_assistant` (stage/activation wiring in container.py). Keep both: our `announce=AnnounceImprovement(...)` field and `notifications` param next to S22's additions. Re-run `ruff`/`pyright`.
2. `frontend/src/features/notifications/model.ts`: S22 did not change kinds, but i18n 23b/c (#21, #22) moved all notification copy into catalogs (`t('kinds.*')`, see main `model.ts:67-177`). Our hard-coded Spanish string `Nueva propuesta de mejora para ${agentId}` must become a `kinds.improvementProposed` key in the es and pt-BR `notifications` catalogs, using `appearance('up','accent','review')`-style entries.
3. `docs/platform/DATA_MODEL.md`, `README.md`: take both sides (S22 added rows for `case_type_maturity.agent_id`; ours adds `registered_by` no FK, `proposal_id/agent_id/improvement`).
4. `schema.gen.ts`/`openapi.json` auto-merged; regenerate with `check:api` anyway.

Schema: both slices change `tables.py` and neither has migrations (S22: delete `backend/cc_platform.db`, new column `case_type_maturity.agent_id`; ours: dropping the `registered_by` FK and 3 notification columns). One DB recreate covers both; say so in both docs. `registered_by` FK drop and `source='engine'` do not collide with S22 (S22 reads `source` as free text; `proposalSource` default branch "other" is never hit).

Closed notification enum: `NotificationKind` is closed on both sides (backend StrEnum, front `Record<NotificationKind,...>` exhaustive switch): adding `improvement_proposed` forces the front `NOTIFICATION_KIND` record and `notificationCopy` switch, which PR #17 already does; S22 added no new kinds so no clash.

Adapt, not just rebase (what S22 changes about our design):
- **Notification target**: change `PATHS.supervision.root` to `automationProposalPath(proposalId)` (`app/paths.ts`, S22). Evidence links `CASE-…` open `supervisionCasePath` as already documented.
- **Dossier is not visible in S22**: the platform keeps our `ImprovementDossier` (problem/evidence/expectedEffect/links) only inside the notification; `ProposalScreen` never shows it. Either add a small card on the proposal page reading the notification/dossier (needs a `GET` on the proposals index to return the dossier), or accept that the registry `docs` fields are the only thing a supervisor sees (see s3). Recommend asking the SPA team for a "Dossier" block (ask A2).
- `registered_by="engine"` appears in `ProposalSummary.registeredBy`; S22 does not display it (grep: no use in `features/automation`), safe.
- Idempotency: announce keys on proposal id, `track` ("Seguir") on the same id calls `adopt` and is idempotent: a supervisor tracking an engine proposal first would make it `source='tracked'` and our announce then returns the existing row (`known` check, builder.py:~445) - fine, but the notification still fires. Document it.
- PR #17 `ImprovementDossier` caps: title 120, problem 600, evidence 600, effect 400, links 8 (`CASE-…`). Our dossier title max is 200 (`dossier.rs:27`) and its sections are longer. Engine side must cut to these caps.
- PII regex hazard: platform `_EMAIL = [^\s@]+@[^\s@]+\.[^\s@]+` would reject our legitimate `id@1.0.0` entity references (dossier.rs header says `id@version` is allowed), and `(?:\d[ \-.]?){9,}` rejects any 9 digits with separators. Our counts print as `117.021` (6 digits) so are safe, but sections quoting `recepcion@1.0.0` would 422 the announce. Ask: loosen `_EMAIL` to exclude `\w+@\d` versions, or we strip versions from announce text.

## 3. Fields our dossier/proposal must fill (what renders)

| Platform surface | Field | Cap | Our source (claude/w12-dossier) |
|---|---|---|---|
| Proposals list row, detail H1, type panel link | `proposal.title` | none in UI; PR17 `title` 120 | `dossier.rs:27` TITLE_MAX 200, out `title` at `:504` - must be <=120 for announce |
| Change card text (`ProposalScreen.tsx:203`) | `changes[i].docs.description` | agent-core 4,000 | `DESCRIPTION_MAX` 3,800 `dossier.rs:25`, built `:493-495` |
| "Why:" line (`:204-209`) | `docs.rationale` | 4,000 | `RATIONALE_MAX` 1,500, `:500` |
| "Changelog:" line (`:210-215`) | `docs.changelog` | 8,000 | `CHANGELOG_MAX` 1,500, `:501` |
| Notification bell | `improvement.{title,problem,evidence,expectedEffect,evidenceLinks}` | 120/600/600/400/8 | map from `sections` (`:504`): Problema observado to `problem`, Evidencia y comparacion to `evidence`, Efecto esperado to `expectedEffect`; links empty (aggregates only) |
| Detail "Herramientas / Idiomas" | agent entity `tools_allowed`, `supported_locales` | - | only if the proposal carries a `kind: agent` change; a prompt/template patch shows none (fine) |
| Evaluation block | `eval_suite` in changes, or on base release | - | REQUIRED to approve anything (s1); the dossier says "GateItems 15/15", but the SPA needs the real suite |

Rendering gaps that hurt us (verified in source):
1. `description` is rendered as plain text in one `<span className="text-14">` with no `whitespace-pre-line` (`ProposalScreen.tsx:203`; grep "whitespace" returns nothing). Our `\n\n**Label.** text` blocks collapse into one paragraph with literal `**` asterisks. Fix on their side (ask A1) or ours: emit plain labels without markdown for the first release.
2. Description is not truncated or collapsible: 3,800 chars in one paragraph defeats the "30 seconds" goal. Same ask A1: split on `\n\n`, bold the leading `**label.**`.
3. A change card needs `kind` and `content.id`; template/prompt entities render "Plantilla/Instrucciones t/estado_pqr versión x" from `changeView` (`proposals.ts:123-134`), good. `docs` is per change; with 2 changes each shows the same dossier - keep description on the first change and short docs on the rest.
4. Case type: S22 ties a proposal to a type only by the URL `?type=` (the chat adds it). Engine proposals have no type, so the page says nothing about type and "Activar" asks the supervisor to pick among `ready` types (`ProposalNextStep.tsx:173` to `ActivatePanel`). Our proposals patch an EXISTING agent (`recepcion`, `disputas`), so Activar (first agent of a type) is the wrong end step: the right one is publish then "Pasar a producción" on the agent page (s6 last-but-two gap). Ask A3.

## 4. Maturity stage alignment (S21 vs our `seams/crates/maturity/src/lib.rs`)

Stages: platform `MaturityStage` 0..3 + `AgentStatus none/ready/active` (`domain/ai/maturity.py`); ours `Stage::S0..S3, Agent` (`lib.rs:25-31`) + `agent_proposed` flag (`:336`). Mapping is exact: ours S3+`agent_proposed` = `ready`; ours `Agent` (has_agent) = `active`. Output JSON uses 0..3 and "agent" (`:32-40`), so a consumer must split "agent" into ready/active (we emit both signals, OK).

Transitions - same shape, different measures:
| Step | Platform rule (slice-21 s2) | Ours |
|---|---|---|
| 0 to 1 | 10 cases resolved by people | any copilot question (`q>0`, `:315`) - MISMATCH |
| 1 to 2 | 20 closed cases with copilot questions (counts cases, no question text) | same question over >=20 cases (`repeat_q_min_cases` 20) - stricter semantics, same number |
| 2 to 3 | tool used in >=70% of cases where proposed, min 10 | `tool_use_min` 0.7, `k_min` 10 - MATCH |
| 3 to ready | >=80 of last 100 drafts sent as-is or minor edit (<=150 permille) | `draft_accept_min` 0.8, window 100, counts `!= Discarded` over AsIs/Minor/Discarded (`:296`) - platform counts "edited" (larger changes) as NOT accepted; ours has no such class, so a heavy edit must be mapped to `discarded` by our source adapter |
Case type ids: platform `unrecognized_charge, undue_charge, app_issue, branch_service, service_quality, virtual_card` (never `none`); no id list appears in our repo, ours are whatever the input JSON says. Our inputs must be per-platform type id or the supervisor panorama will not match. Signals on the platform are counted "since the type reached the current stage"; ours are not (aggregate windows), so numbers can differ: display ours as "engine view", never overwrite the platform stage. Stage strip belongs to the platform (it is its record); our `maturity` stays an input for proposals, as agreed.

## 5. New asks and changes to our plan

Asks to the SPA team (this is where it lands; contact via the user, not direct):
- A1. Render `docs.description` with `whitespace-pre-line` and bold the `**label.**` prefixes (or a tiny sectioned renderer); optional collapse after the first 3 sections. Without it the dossier is an unreadable blob.
- A2. Show the improvement dossier (problem, evidence, expected effect, evidence links) on the proposal page for `source=engine`, and make the bell link to `automationProposalPath(id)`.
- A3. For a proposal on an existing agent (published, agent already serves a type): replace "Activar" by "Pasar a producción" (agent page action) and do not require `?type=`; derive the type(s) from `stages[].agentId == proposal.agentId`.
- A4. Eval suite for `recepcion`/`disputas` (platform s6): nothing can be approved without one. Biggest blocker for the live demo path; ours must write or reference an `eval_suite` in `changes` (the dossier carries REG1 GateItems, which is evidence, not the suite).

Our changes:
- C1. Rebase PR #17 per s2: conflict fixes, notification copy to catalogs es + pt-BR, link to proposal path, recreate-DB note (one for both slices).
- C2. Engine dossier output: title <=120; add `announce_payload` = {problem<=600, evidence<=600, expectedEffect<=400, evidenceLinks []} cut from `sections`; no `id@version` strings in those texts (or A5: platform loosens the email regex).
- C3. Plain-text mode (`--format plain`) of the description for the first demo, until A1 lands.
- C4. Maturity adapter: map to platform type ids, "edited" to `discarded`, publish as "engine view" and note the 0 to 1 difference; decide with the user whether we align our S1 rule to "10 resolved cases".
- C5. Demo path: announce a proposal on `disputas` (agent that already serves "Cargo no reconocido" in the seed) so the type panel (`TypePanel.tsx:209`), list, bell and detail all light up; do NOT claim live approve/publish until the eval suite exists (A4).
