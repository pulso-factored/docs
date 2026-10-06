# ASK infra: engine loop job env (compose.loop.yaml, PR 40)

Engine side is `pulso loop` (improvement-engine docs/dev/ENGINE_PROD.md). Exact lines for `deploy/hackathon/engine/compose.loop.yaml`:

```yaml
    command: ["loop"]                 # not PULSO_LOOP_COMMAND placeholder text: the entrypoint is `pulso`
    environment:
      PULSO_LOOP_COMMAND: loop        # keep if the variable stays in the file; value must be exactly `loop`
      PULSO_REGISTRY_ENV: shared      # label of where proposals go (default is local)
      PULSO_CELLS_SOURCE: bank        # infra must set: synthetic | bank | e0 (nothing sets it today); demo profile only with synthetic
      PULSO_LOOP_INPUTS_DIR: /var/lib/pulso/inputs   # the S3-synced engine/inputs mirror; file cells.ndjson (PULSO_LOOP_CELLS_FILE to rename)
      PULSO_REGISTRY_VIA: api
      PULSO_EVAL_BEFORE_ANNOUNCE: "on"
```
- Already rendered and used: PULSO_CORE_ADDR (registry address), PULSO_SERVICE_SEED_HEX, PULSO_SERVICE_KID, PULSO_LLM_GATEWAY_ADDR/KEY, PULSO_WORK_DIR. Add `PULSO_LLM_GATEWAY: enabled`.
- Not read by `pulso loop`, safe to drop: PULSO_CORE_PORT, PULSO_MODEL_PORT, PULSO_CORE_URL, STEPS_RUNNER_EXE.
- Announce needs PULSO_PLATFORM_URL and PULSO_PLATFORM_SERVICE_TOKEN (both set, else announce is off).
- Mount `/var/lib/pulso` read-write (lock, records) and inputs read-only. systemd: `SuccessExitStatus=75 143`, `RestartPreventExitStatus=2`; exit 3 = finished with an infra failure (alert).
- Requires the engine image built from the ENGPROD image PR (python3 + regression scripts inside).
