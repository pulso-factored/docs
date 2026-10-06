# Brief for the platform team: make support-platform deployable on the shared environment

From: Pulso improvement-engine team (Claude). Date: 2026-10-05. Delivery: ready PRs in github.com/pulso-factored/support-platform plus one short report. We consolidate, deploy and test in the real environment; you implement.

## 1. Context
The platform (FastAPI backend with SQLite, `event_log`, WebSocket; React 19 SPA in es and pt-BR) will run on an EC2 host behind CloudFront, next to the shared Core (`agentcore serve`), llm-gateway, tool-service and ONE shared Postgres used by all services (decision taken 2026-10-05). Today the platform has no migrations (a schema change means deleting the DB), no CI workflow, SQLite only, and several things only work when agent-core is up. Already merged and in use: S19/S21/S22 (Automatizacion screen reads source `engine`; TOTP step-up on every decision), PR 17 (announce route, `POST /api/v1/internal/builder/proposals/announce`), PR 27 (`release` on events, `turn_id` on `copilot.suggestion_decided`, `GET /internal/evidence/cases`), PR 28.

## 1.1 Boundaries: who owns what (read before starting; avoids overlap)
- YOU (platform): the support-platform repo only: backend, SPA, schema and migrations, the events the platform EMITS (types, fields, `schema_version`), its images, health, env contract, seed.
- US (engine team), already in progress, do not duplicate: (a) the ENGINE side of the event catalog 1.3.0: admitting the new types in our exporter contract and its pinned drift digests, and adding `cases.case_type` to our `platform-exporter` allow-list; (b) the engine calling `GET /internal/evidence/cases` when it announces proposals; (c) the announce client. You keep emitting the events and keep both routes' contracts stable.
- INFRA (us, github.com/pulso-factored/infra): Terraform, EC2 compose/systemd/user_data, the shared Postgres instance and CREATING its databases and roles (including the engine's read-only role: you tell us which grants it needs, we create it), secrets generation and injection, CloudFront and security groups (you tell us the path and WebSocket needs, we configure them), S3. Do not edit infra.
- agent-core team: the Core (`agentcore serve`), which is being hardened in parallel from its own brief; code against its documented API and env contract, not against its internals.
- Things already DONE and merged, do not redo: announce route (PR 17), `release` on `assistant.turn_answered` and `copilot.suggestion_ready/none`, `turn_id` on `suggestion_decided`, the evidence route (PR 27), Automatizacion with TOTP step-up.
If something seems to belong to someone else, tell us instead of doing it.

## 2. What we need (priority order)

### P1. Postgres support and migrations (P0)
- `DATABASE_URL` (Postgres, psycopg3 or asyncpg as you already use) for production; SQLite stays supported for local dev and unit tests.
- Real migrations (Alembic or equivalent): an initial migration equal to the current schema, plus the two columns added by slices 21/22 and PR 27. `cc-api` (or a `cc-migrate` command) applies migrations on start, idempotent, guarded by an advisory lock. No more "delete the DB".
- Roles: document in `docs/platform/deploy-env.md` the exact grants the app role (read/write) and a READ-ONLY role for the engine's `platform-exporter` need (tables and columns: `event_log`, `cases` including `case_type`). Infra creates the roles from your document; you do not create cloud-side roles. The exporter allow-list change itself is ours.
- Tests run on both SQLite and a Postgres container (Podman is fine); the event_log append-only guarantee must hold on Postgres (trigger or constraint test).

### P2. Production runtime contract (P0)
- Env contract in `docs/platform/deploy-env.md`: every `CC_*` variable (name, required or optional, default, secret or not, example shape without real values), including: `CC_ENV`, database URL, base public URL, allowed origins, cookie settings, session and TOTP secrets, `CC_INTERNAL_SERVICE_TOKEN`, the Core base URL and tokens, `CC_EVIDENCE_MIN_CELL`, copilot toggle defaults. Fail fast with clear messages when a required one is missing; never log secret values.
- `GET /healthz` (liveness) and `GET /readyz` (readiness: DB reachable and migrated; Core reachable reported as degraded, not fatal, because the platform must keep serving non-AI screens when the Core is down). Unauthenticated, fast, JSON, no secrets.
- Behind CloudFront and a reverse proxy (you document what the app needs: paths, WebSocket upgrade, idle timeouts, headers; infra configures CloudFront and the proxy): trusted proxy headers (X-Forwarded-*), secure cookies, correct WebSocket upgrade and idle timeouts through the edge (document the CloudFront behaviour and path rules you need: `/api/*`, `/ws/*`, static), CORS.
- Graceful shutdown and a restart-safe WebSocket client reconnect.

### P3. Container images (P0)
Dockerfile for the backend and one for the SPA (static build served by nginx or equivalent; say which and why), multi-stage, non-root, base pinned by digest, linux/amd64 and linux/arm64, `HEALTHCHECK`, small. A compose example with Postgres, the backend and the SPA. Build must work locally with Podman (no hosted CI). Document the build and run commands.

### P4. Core integration behaviour (P1)
- Core base URL, timeouts, retries with backoff and circuit breaker for assistant, copilot and evaluate calls; clear user-facing degraded mode when the Core is down (assistant says it cannot answer and hands to a human; copilot silent).
- Verify end to end against the real `agentcore serve` (not doubles) for: a customer conversation, an escalation, a copilot suggestion and its decision event, and the Automatizacion flow on a proposal announced by the engine (evaluate, approve, publish, prod with TOTP).
- Pass traceparent to the Core on assistant and copilot calls (no Langfuse in the platform itself).

### P5. Event catalog and signals for the engine (P1)
- Your part of catalog 1.3.0 is the EMITTING side only: make sure the platform emits, with stable documented payloads, `copilot.suggestion_ready/_none/_shown/_decided/_ignored`, `copilot.tool_used`, `case.type_changed`, the `ai.*` events and `platform.ai_toggled`; add a `schema_version` to every event payload and to your own event catalog document, and publish the list with payload fields in `docs/platform/api/engine-signals.md` (the file PR 27 created). We admit them in the engine exporter and re-pin our digests; send us the final list and the version number.
- `release` on the remaining AI events (`copilot.answered`, `assistant.ended`); `reason_code` on copilot escalation in `suggestion_decided`; a handoff-quality event (what the advisor needed to ask again after a handoff).
- All aggregate-friendly, no free text, no PII.

### P6. Dossier and decision UX (P1, from ASK_platform-spa.md)
FIRST check whether this is already in your backlog or partly built (we asked earlier through ASK_platform-spa.md and your S22 slice may cover parts): if so, only close the delta and tell us. Render the engine's improvement dossier on the proposal page (plain text only, Spanish with Portuguese variant, title up to 120 chars), show evidence links as real case links (use the evidence route; `CASE-` ids), show base versus candidate eval results and the verdict story, label "Pasar a producción" correctly, and display reject `reason_code` selection (7-value closed list from agent-core PR 53) when a supervisor rejects.

### P7. Seed and demo data (P1)
Reuse what exists before building: the data-lab repo has a synthetic platform-history generator (check it and the platform's own seed first) and the platform has its seed accounts. An idempotent seed command that creates realistic volume (enough closed cases per type, channel and language that the evidence route returns results with `CC_EVIDENCE_MIN_CELL=10`), accounts per role, and a replay of at least 1,000 synthetic cases and events so the engine's sensors and the supervisor screens have something to show. Synthetic only, labelled as such.

## 3. How to test (required)
1. Unit and API: RED first; `ruff`, `ruff format`, `mypy`, full backend suite on SQLite AND Postgres, frontend lint, type-check and unit tests, SPA build.
2. Migrations: fresh DB to head; existing slice-22 SQLite dump migrated; running twice is a no-op; two processes starting at once do not race.
3. Compose smoke: Postgres, backend, SPA, real `agentcore serve` and llm-gateway (OpenRouter models mimo flash for agents). Script: log in as analyst, supervisor and admin (dev TOTP only for seeded accounts), run a customer conversation, an escalation, a copilot suggestion, then the Automatizacion flow on an engine-announced proposal. Browser e2e (Playwright or similar) for the Automatizacion flow and the dossier page.
4. Resilience: stop the Core and confirm degraded mode and `/readyz` semantics; stop Postgres and confirm `/healthz` 200 and `/readyz` 503; restart and confirm recovery without manual steps; WebSocket reconnect.
5. Engine contract: `POST .../announce` and `GET /internal/evidence/cases` keep working (our acceptance script runs against your compose).

## 4. Definition of done
- A fresh clone plus one compose command brings up a working platform on Postgres with the seed; no manual DB deletion ever required again.
- Env contract, health endpoints, images (amd64 and arm64) and the build/run docs merged.
- Catalog 1.3.0 and the event additions merged with drift digests re-pinned and documented.
- Dossier page and evidence links working against an engine-announced proposal.
- All new behaviour covered by tests on both databases; the e2e passes against real `serve`.
- Report to us: PR list, test counts, e2e summary, remaining gaps.

## 5. Constraints
No secrets in code, tests, logs or PRs. Synthetic data only. Additive changes with defaults (`null`) so the engine keeps working; do not change the announce and evidence contracts without telling us. Ask us if a value or credential is missing; do not invent.
