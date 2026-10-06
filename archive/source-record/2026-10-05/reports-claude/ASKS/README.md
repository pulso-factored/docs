# Solicitudes a equipos humanos (via el usuario)

Verificado contra main el 2026-10-04: agent-core ae437bb, support-platform f76169f, llm-gateway 63155b6, infra fe07ae7. Ya resuelto en agent-core, NO se pide: `GET /proposals`, `Idempotency-Key`, `/runs/{id}/lineage`. Infra es nuestro (PR propio), sin ask. Langfuse: incorporado desde LANGFUSE_INTEGRATION_PLAN_2026-10-05.md.

| Orden | Equipo | Ask | Prioridad |
|---|---|---|---|
| 1 | llm-gateway | consumer `engine` + alias openrouter | P0 |
| 2 | agent-core | staff-keys `builder` (constructor; concesion de confianza) | P0 |
| 3 | plataforma | `POST /internal/builder/proposals/announce` | P0 |
| 4 | plataforma | contrato de datos de la pantalla Agentes (dossier) | P0 |
| 5 | plataforma | notificacion `improvement_proposed` | P1 |
| 6 | agent-core | rol exporter + export activo | P1 |
| 7 | agent-core | agent+alias en `release.*` y entrega | P1 |
| 8 | plataforma | `release` en payloads; `copilot.suggestion_*` en catalogo 1.3.0 + `turn_id` | P1 |
| 9 | gateway | env OTLP a Langfuse + labels `langfuse.*` + captura opt-in | P1 |
| 10 | agent-core | extraer traceparent (`tracing.py:39`) + lista `spans.py:46-62` | P1 |
| 11 | plataforma | OTel backend + traceparent en SPA | P2 |
| 12 | agent-core | escenarios `dataset`; alias `canary` | P2 |
| 13 | agent-core, tool-service | alinear ToolDef de registry-e2e con `GET /v1/tools` (`source`, `args_schema`, `leer_perfil`); catalogo versionado (ASK_tool-alignment.md) | P1 |

Envio: gateway y agent-core primero (desbloquean la demo en vivo); plataforma en paralelo.
