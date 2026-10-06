# Solicitud al equipo agent-core (motor de mejora Pulso)

Hola equipo. Estamos conectando el motor de mejora (Rust) al Core compartido para el lazo detectar -> proponer -> evaluar -> aprobar -> liberar -> observar. Verificado contra `main` ae437bb: ya existen `GET /v1/registry/proposals`, `Idempotency-Key` y `GET /v1/registry/runs/{id}/lineage`, no pedimos nada de eso. Quedan 6 puntos, en orden de prioridad.

**1. (P0) Entrada en `--staff-keys` para nuestro principal `builder`.**
Cambio: agregar nuestra clave publica (kid `pulso-engine-<aa-mm>`, la enviamos en b64url) al archivo de staff-keys del Core compartido; principal `pulso-improvement-engine`, tipo builder, roles `[constructor]`, sin `actor=human`. Solo configuracion. Aviso: el Core valida claims, no un techo por kid, asi que es una concesion de confianza a nuestra clave (`registry/http.py:123-127`, `registry/roles.py:30-41`). Aceptacion: `POST /v1/registry/proposals` con `origin=auto_detect` devuelve 201; recarga en ~5 s (README:101). Por que: sin esto no hay "proponer".

**2. (P1) Rol `exporter` y export habilitado.** Mintear `exporter` para el mismo principal (o un kid aparte) y confirmar `/v1/export/runs|registry-events` activo en el Core compartido (`registry/roles.py:43-47`, `composition/export_http.py:50`). Aceptacion: `GET /v1/export/registry-events` -> 200 con ese principal. Por que: cierra "observar" (reloj post-release).

**3. (P1) `agent` y `alias` en eventos `release.*` y entrega real.** Hoy `ReleaseData` solo lleva `release_id` y `proposal_id` (`registry/outbound.py:21`) y el relay solo publica a un puerto. Cambio aditivo: campos opcionales `agent_id`, `alias` (y `before`) en `ReleaseData`. Aceptacion: evento `release.promoted` trae `agent_id=disputas`, `alias=prod`. Por que: atribuir el efecto a la celda correcta.

**4. (P2) Escenarios `dataset`.** Hoy `dataset_source_disabled` (`registry/suite.py:172,209`; tema #20). Pedimos habilitarlo (id + hash, sin datos en el repo) o una fecha. Por que: reproducir casos reales contra el candidato.

**5. (P2) Alias `canary` + `traffic_pct`.** Hoy solo `staging`/`prod` (`AliasChange` sin porcentaje, `registry/models.py:143`). Propuesta aditiva: alias `canary` con porcentaje y ruteo en la creacion de run. Por que: liberar gradual antes de prod.

**6. (P1, Langfuse)** (a) Extraer `traceparent` entrante en `api/tracing.py:39` (`ctx = extract(request.headers)` pasado a `start_as_current_span`); sin esto no hay traza entre servicios. (b) Ampliar la lista cerrada `spans.py:46-62` con `langfuse.session.id`, `langfuse.release`, `langfuse.trace.tags`, `langfuse.observation.type`, `langfuse.trace.metadata.*`, derivados de `bind(session_id, release, agent, locale)`. Aceptacion: una traza unica motor -> gateway -> Core visible en Langfuse.

Pregunta: los escenarios corren como `customer` (`composition/evaluation.py:95`); si `advisor` fuera posible, `copiloto-asesor` seria evaluable.
