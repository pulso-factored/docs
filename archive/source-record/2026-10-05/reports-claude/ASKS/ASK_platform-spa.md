# Solicitud al equipo plataforma / SPA (motor de mejora Pulso)

Hola equipo. El motor de mejora detecta problemas, crea propuestas en el registry de agent-core y necesita que un supervisor las vea y decida en la plataforma. Verificado contra `main` f76169f: `internal.py` solo expone `GET /grants/{ref}`, `track` exige sesion humana (`api/routers/builder.py:148`), no existe `improvement_proposed` en `NotificationKind` y no hay pantalla de builder en `frontend/src`.

**1. (P0) `POST /api/v1/internal/builder/proposals/announce`.** Bearer `CC_INTERNAL_SERVICE_TOKEN`, body `{proposalId}`; llama `adopt(source="engine")` (ya se usa con `source="chat"` en `application/ai/builder_chat.py:295`). Idempotente. Aceptacion: tras llamarla, la propuesta aparece en `GET /builder/proposals` de un supervisor. Por que: sin esto la propuesta nunca llega a la lista (solo se lee la tabla `builder_proposals`).

**2. (P0) Pantalla Agentes leyendo propuestas con `origin=auto_detect`.** Sabemos que ya la construyen: pedimos su contrato de datos (campos de lista y detalle, limites de texto, es/pt) para alinear nuestro dossier (problema, evidencia con baseline, diff, base vs candidato, gates, `candidate_hash`, efecto esperado, riesgos). Hoy lo volcamos en `docs.rationale` (<=4000). Aceptacion: dossier de ejemplo renderizado sin truncar. Por que: decision humana en 30 s.

**3. (P1) Notificacion `improvement_proposed`** (rol Supervision) emitida por el announce, con `proposalId` y agente (`domain/notifications/notification.py:38`). Por que: el supervisor se entera.

**4. (P1) Admitir `copilot.suggestion_{requested,ready,none,failed,decided}` en el catalogo 1.3.0** (hoy emitidos y auditados, `domain/ai/events.py:128-186`, pero fuera del catalogo) y agregar `turn_id` a `decided`. Por que: las correcciones del asesor son un dataset etiquetado gratis.

**5. (P1) Campo `release` (y `agent_version`) en payloads** de `assistant.turn_answered`, `copilot.suggestion_ready`, `copilot.answered` (ya existe en `application/ai/runtime.py:93-112`). Por que: medir antes/despues de una release.

**6. (P2, Langfuse)** Backend con OTel (FastAPI + httpx; inyectar `traceparent` en el cliente de agent-core, `container.py:406`), `session.id` = caso/conversacion, ids pseudonimos. La SPA solo envia `traceparent` y `X-Session-Id` y el feedback pasa por el backend (sin claves Langfuse en el navegador); CORS debe permitir `traceparent` y `baggage`. Aceptacion: traza unica SPA -> backend -> agent-core.

Pregunta: cuenta de supervisor demo con TOTP, y si copilot/asistente leen `@staging` o `@prod`.
