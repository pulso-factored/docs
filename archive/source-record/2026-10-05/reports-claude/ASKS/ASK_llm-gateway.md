# Solicitud al equipo llm-gateway (motor de mejora Pulso)

Hola equipo. El motor de mejora llama al gateway con perfil por request (alias `openrouter`) y queremos ver cada llamada como generacion en Langfuse Cloud. Verificado contra `main` 63155b6: ya hay span `chat <model>` con `gen_ai.*`, `traceparent` honrado y export OTLP/HTTP por variables `OTEL_*`.

**1. (P0) Consumer `engine`.** En `GATEWAY_CONSUMERS`: `"engine":{"token_env":"GATEWAY_TOKEN_ENGINE"}` y en `LLM_ENDPOINTS` el alias `openrouter` (`base_url https://openrouter.ai/api/v1`, `api_key_env OPENROUTER_API_KEY`). Solo configuracion (README:57; infra ya nombra el secreto). Aceptacion: request con el token de `engine` -> 200 y span con `llmgateway.consumer=engine`.

**2. (P1) Export OTLP a Langfuse por entorno.** `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=<base Langfuse>/api/public/otel/v1/traces` y `OTEL_EXPORTER_OTLP_HEADERS=Authorization=Basic <b64 pk:sk>,x-langfuse-ingestion-version=4` (claves puestas en infra, nunca en repo). Sin cambios de codigo. Aceptacion: una llamada produce una generacion con modelo y tokens en Langfuse.

**3. (P1) PR aditivo (~40 lineas) en `internal/telemetry/telemetry.go`.** (a) En `labelAttributes` emitir tambien `langfuse.session.id`, `langfuse.release`, `langfuse.trace.metadata.agent`, `langfuse.trace.metadata.run_id` desde los labels cerrados existentes. (b) Opt-in `LLM_GATEWAY_CAPTURE_CONTENT=true` que fije `langfuse.observation.input/output` (apagado por defecto; el usuario autorizo enviar contenido a Langfuse, y la bandera deja el control al gateway). Aceptacion: con la bandera la generacion muestra prompt y respuesta; sin ella nada cambia. Por que: observabilidad y costo por etapa (scout/verifier/builder) del lazo.
