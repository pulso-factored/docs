# Infra PR #37 adversarial review (ADR 0009, journal 0019)

Reviewer: independent, read-only. Head 95ec18d vs main. agent-core checked at origin/main ae437bb (fetched). Engine code: worktrees/improvement-engine-claude-cons @ 6e3de82d. No terraform plan/apply, no AWS, Nexus untouched.

Verdict: no merge blocker in the infra change itself (nothing applies on merge, ADR is "Proposed"). Three cross-repo / apply-time blockers are listed under "Blockers before apply or demo".

## 1. Security

- Ed25519 derivation: CORRECT. I re-implemented the HCL bit regrouping in Python: PKCS#8 seed = bits 128..384 of the base64 body (+2 pad bits, 43 base64url chars); SPKI key = chars 16..59. Both reproduce RFC 8032 test vector 1 exactly. The test overrides all four roles with the same vector, so it does not prove the four keys are distinct (they are: for_each tls_private_key).
- Sensitivity: private_key_pem is provider-sensitive, so seeds, seed_bits, generated_secrets and secret_string stay sensitive. Outputs expose only kid and public key. Seeds do sit in plaintext in Terraform state (documented) and in the secret, plus env files (600, host) and container env (visible to docker inspect on the host). NON-BLOCKER.
- Staff-keys trust: CONFIRMED against agent-core `registry/roles.py`. Approve/publish/promote require role aprobador + attrs.actor=human + auth.level step_up, all claimed inside the credential. The engine key is in staff-keys, so whoever holds the engine seed can mint a credential claiming all of those and approve/publish/promote. Documented honestly in ADR, secrets-keys. Worse than documented: the single secret is readable by all three hosts (ADR 0007), so the engine host (and core host) can also read the platform STAFF seed. The "engine never approves" guard is code discipline only. NON-BLOCKER (documented), but flag to owner. Mitigation: give the engine its own key list for `--staff-keys` only if agent-core adds per-kid role ceilings; otherwise split the secret per host.
- SG: core 8080 from engine SG only, platform 8081 from core SG only, matching egress, no 0.0.0.0/0 added (network test asserts cidr null). Gateway published on host 0.0.0.0:8080 but only reachable via SG. OK.
- Caddy 8081: only /healthz and /api/v1/internal/grants/*, 404 otherwise; bearer still enforced by the platform. Low: Caddy does not clean `..` segments before the prefix match; irrelevant behind SG + bearer. NON-BLOCKER.
- No secrets in compose, user_data or S3 bundle: confirmed. `extra_env` (S3 .env) only carries AGENTCORE_PIECE_* module:attr, validated UPPER_SNAKE single line. IAM: unchanged by the diff.
- Migration runs with the same DSN as the runtime and no `--app-role`: runtime gets owner-level DB rights, or migrate lacks DDL rights. NON-BLOCKER, flag to db-bootstrap owner.

## 2. Correctness

agent-core flags and env, all verified in origin/main: `serve --host --port --identity-keys --staff-keys --registry-api --tools --authz --field-classifier --grant-active --transcript --calibration --classifier`; `migrate` uses AGENTCORE_REGISTRY_DSN/EVAL_DSN. Env names match: AGENTCORE_GRANTS_URL/TOKEN, AGENTCORE_FIELD_CLASSIFICATION_FILES, AGENTCORE_AUTHZ_BIND_KEYS, AGENTCORE_SERVE_AGENTS, AGENTCORE_BLOB_BUCKET/PREFIX, AGENTCORE_KEYS_FINGERPRINT/TOKEN_MAP (`k1:base64`, 32 bytes, distinct), AGENTCORE_LLM_GATEWAY_URL/TOKEN. Key JSON shapes (principal_keys, delegation_keys optional for staff) match identity_keys.py. Entrypoint `sh -c '... exec agentcore "$@"' agentcore <cmd>` is correct; `$$` escaping correct; /tmp writable for uid 10001. The DB password rendering path (jq @tsv then printf) preserves single-line JSON.

- Fail-closed claim: TRUE as written. Empty `--transcript ""` becomes chosen[""], `_load("")` fails, ServeConfigError, exit non-zero; demo doubles need AGENTCORE_ALLOW_DEMO=1 and the Dockerfile copies only agent_core and agent_telemetry (no `testing`).
- Claim "no real transcript/calibration/classifier exists" is STALE: agent-core main 46d7b98 (PR #42, 2026-10-04) ships `composition.transcript:transcript` (Postgres), `composition.artifacts:calibration` and `:classifier_provider`. The latter two additionally need AGENTCORE_CALIBRATION_DIR and AGENTCORE_CLASSIFIER_ARTIFACTS_DIR (directories of trained artifacts, still open in agent-core). `agent_core_serve_pieces` is a sane fail-closed hook but cannot be finished with it: the compose passes no such env vars and mounts no directories, and extra_env only produces AGENTCORE_PIECE_*. Update ADR, OPEN_GAPS, secrets-keys and service-deployment. NON-BLOCKER.
- Second reason Core cannot start: AGENTCORE_TOOL_SERVICE_URL stays `CHANGE_ME` (not an http(s) URL, so http_tool_executor raises). Documented as "no tool service". Fail-closed. Not solved by the pieces variable.
- Image flow: ok. Clean-tree + HEAD (or explicit 40-hex) -> GIT_SHA build arg; zip is the checkout alone; Dockerfile at root. Caveat: with no .git and an explicit commit nothing verifies the content; no commit is pinned in the ADR (old pin c814c2b removed). NON-BLOCKER.
- Engine env names vs improvement-engine code (MISMATCHES):
  1. PULSO_LLM_GATEWAY_TOKEN is not read; the engine reads `PULSO_LLM_GATEWAY_KEY` (models/llm_gateway.rs).
  2. PULSO_LLM_GATEWAY_ADDR=core.<zone>:8080 is rejected: `private_host` accepts only IP literals or localhost, unless PULSO_GATEWAY_ALLOW_REMOTE_PLAINTEXT=yes.
  3. PULSO_CORE_KID, PULSO_CORE_PRINCIPAL_ID, PULSO_CORE_SIGNING_SEED are not read anywhere. The live Core port (real_core.rs) wants PULSO_CORE_PORT=live, PULSO_BRIDGE_ADDR, PULSO_SERVICE_KID, PULSO_SERVICE_SEED_HEX (64 hex chars; infra gives base64url), PULSO_HUMAN_KID/SEED_HEX, PULSO_LIVE_*, PULSO_E2E_FX_ADDR. It is built for the old core-bridge, not agent-core serve.
  4. Matching: PULSO_LLM_GATEWAY=enabled, PULSO_CORE_ADDR (RegistryClient host:port). PULSO_CORE_URL still used by cli.rs (kept).
  ADR says these names are "this repository's contract; the engine reads or maps them". Honest, but the engine cannot consume them today. NON-BLOCKER for infra, BLOCKER for the demo (see below).
- Apply impact: adds tls x4, random x6, SSM params, 4 SG rules; in-place S3 objects and two SSM values; `moved` blocks move the two gateway SSM params from placeholder (ignore_changes value) to derived (no ignore), so any value the owner set out of band for GATEWAY_CONSUMERS/LLM_ENDPOINTS is overwritten (intended). No user_data change, no replacement, no destroy; core-exporter removal is bundle-only. Consistent with the PR claim.
- Untouched secret version (`ignore_changes = [secret_string]`): safe for security (fails closed) but not operationally safe. On the existing secret the 13 generated keys are absent: Core gets empty key files and does not start (fail closed). The platform compose now always sets CC_AGENT_KEYS_FILE from an empty AGENT_KEYS_JSON, so a platform restart before reseeding likely crash-loops the support API (platform outage; I could not run it). Reseed option (a) `-replace` of the secret version resets EVERY out-of-band key to CHANGE_ME, including DB_PASSWORD_* (out of sync with an already bootstrapped DB), CC_TOTP_SECRET_KEY (invalidates enrolled TOTP) and CC_SESSION_SECRET; the old version stays as AWSPREVIOUS only. Option (b) is impractical (owner must pull seeds out of state and paste them). NON-BLOCKER for merge; BLOCKER before apply on an existing stack: ship a merge-only seeding helper (read current secret JSON, add only missing generated keys) or reseed only on a fresh secret, and order platform deploy after reseed.

## 3. Tests and docs

- Terraform tests are meaningful (derivation vector, key-file shapes, token equalities, SG rules, bundle assertions). Python contract tests are mostly string greps (weak but cheap); `test_no_secret_value_is_an_output` checks only module outputs. Pester covers commit resolution and zip layout. None validate flags against agent-core. I did not re-run them.
- Docs defects: (a) docs/service-deployment.md lines 102 and 104 contain BEL (0x07) bytes: `.\scripts<BEL>ws-prod.ps1` and `D:\src<BEL>gent-core` (an `\a` escape got interpreted), so the documented commands are broken. Fix before merge (trivial). (b) ADR item 4 claims `<SERVICE>__FILE_<NAME>` secrets are written as files by pulso-stack-prepare and mounted as compose secrets; prepare.sh has no such code and the PR instead uses env plus entrypoint (the README of the same PR says so). Correct the ADR. (c) the stale "no real pieces" statements above.

## Blockers before apply or demo

1. Reseed path for the existing secret (above): no safe merge tooling; option (a) destroys out-of-band values.
2. Engine env contract mismatch (gateway key name, DNS host rejected, Core credential vars unread, seed encoding, live port is bridge-based): engine-side work, tracked against improvement-engine.
3. Core cannot start: tool service URL, calibration/classifier artifact dirs and (until wired) the three pieces; the compose cannot carry the two directory env vars today.

## Merge-time asks (small)

Fix the BEL corruption, correct ADR item 4, refresh the stale agent-core claim, record the pinned agent-core commit, and add a line that the engine host can read the platform staff seed.
