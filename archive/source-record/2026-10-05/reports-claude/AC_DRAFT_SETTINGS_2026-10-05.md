# agent-core: release settings in evaluation drafts for cloned agents (2026-10-05)

## Problem
`RegistryService.put_draft` (agent_core/registry/service.py) refuses a `release_settings` draft whose `interrupts` is set unless the actor has `admin`
(`forbidden_role`; `changes_interrupts` in validation.py; decision D-17 / N-07). The engine `builder` (role `constructor`) cannot, so a CLONE of an
existing agent (new-agent proposal: no base release, so the candidate release gets defaults: no interrupts, 4000 chars, no ruleset) is not
evaluable without the donor's settings (evaluate answers 500). Evidence: improvement-engine W13 doc (`release_settings_assumed`, live run used a staff
admin credential as a labelled stand-in; production result would be `not_announced:infra_failed`).

## What the code actually enforces today
* Only `interrupts` is admin-gated. `language_detection`, `injection_ruleset`, `max_input_chars` (ceiling 100000) are open to a constructor.
* Platform guard (REG-LOCKED, candidate.py `locked_interrupt_violations`): a `locked` interrupt of the BASE cannot be removed, lowered, re-actioned or unlocked,
  by anyone including admin. It compares against the base only: with no base (new agent) nothing is protected, and `locked` written by the caller has no authority.
* Approve, publish, promote need a human approver with step-up (`require_approver`/`require_admin`); the approver sees `release_changes` diff. A constructor
  (also the bot) can never approve or publish. So any draft is non-publishable without a human step-up already.
* Note: a new agent with NO settings already gets zero interrupts (no fraud). Adding interrupts to a new agent is never weaker than that baseline; the real
  risk of letting a constructor WRITE interrupts is (i) removing/lowering a donor's fraud interrupt, (ii) adding a higher-priority `start_flow` interrupt that
  pre-empts the escalation, (iii) forging `locked: true` flags.

## Options (ranked)
1. **(c) donor reference, resolved server-side. RECOMMENDED.** `release_settings.inherit_from: <release_id>`; for an agent with no base the server copies the
   donor release's interrupts, language detection, injection ruleset and max_input_chars. The caller never writes the values, so nothing can be removed,
   weakened, re-prioritised or forged; explicit `interrupts` still need admin; REG-LOCKED applies against the donor even for admin; rejected if the agent has a
   base. Additive field, default behaviour unchanged, ~35 source lines. Publish still needs approver step-up. Cost: contract change (ReleaseSettings schema).
2. **(a) constructor may add/copy as a superset of donor.** Needs a donor reference anyway (to define "superset") plus a per-field weakening comparison
   (priority, action, locked, ordering/pre-emption); more code, more edge cases (ii above). Strictly more complex than (c) with no extra capability for our use.
3. **(b) evaluation-only manual proposals flagged non-publishable.** Needs a new proposal flag, a state-machine/approve guard and migration of stored
   proposals; larger, and the real settings still would not be proven. Not small.
4. **(d) keep admin-only; engine skips native evaluation for new agents and announces `not_measured`.** Zero agent-core risk, but the proof of a new agent is
   lost (the finding cases cannot run natively), which is exactly what W13 delivers. Fallback if the agent-core team rejects (c).

## Decision
Implemented (c) on branch feat/constructor-release-settings-eval-drafts (see PR). Question for the agent-core team: is a constructor allowed to name any
published release as donor (current choice, since constructors can already read the registry and the clone closure already copies donor entities), or
must the donor be restricted (same tenant/allowlist, or only releases aliased `staging`/`prod`)?
