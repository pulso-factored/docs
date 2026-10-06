# Solicitud a agent-core y plataforma: motivo estructurado al rechazar una propuesta (motor de mejora Pulso)

Hola equipos. El motor de mejora quiere aprender de las decisiones humanas ("esta propuesta no se aprobo porque X") para no volver a proponer lo que ya se rechazo por una causa que no cambia, y para mostrar al supervisor un historial en el dossier. Verificado contra `main` de agent-core `630a4a7` y de support-platform `a451001`. Hoy el motivo de un rechazo es texto libre obligatorio que nadie puede leer por HTTP, y puede traer datos personales. Pedimos un cambio pequeno y aditivo; no hace falta nada para la expiracion (la derivamos nosotros).

## Lo que encontramos

- `POST /v1/registry/proposals/{pid}/reject` recibe `reason: str` obligatorio (`agent_core/registry/http.py:92-93,244-246`); el servicio lo guarda cortado a 2000 caracteres en `reg_approvals.reason` (`registry/service.py:622-631`, `postgres/schema.sql:25-27`). Ninguna ruta lo devuelve: `ProposalDetail` no trae aprobaciones (`service.py:147-151`) y el evento `rejected` no lleva motivo (`registry/models.py:157-171`, `service.py:630`).
- La plataforma pide el motivo como texto libre de 1 a 2000 caracteres (`backend/src/cc_platform/api/schemas/builder.py:368-370`, `frontend/src/features/automation/components/ProposalNextStep.tsx:300-308`) y en su auditoria solo guarda la longitud (`application/ai/builder.py:669-692`, `domain/ai/events.py:293-298`).
- Tras rechazar, la propuesta vuelve a `draft`; no existe estado `rejected` ni expiracion.

## Lo que pedimos (en orden)

**1. (P1, agent-core) Campo `reason_code` de vocabulario cerrado, opcional.**
Cambio: `ReasonBody` (reject) acepta `reason_code` opcional con exactamente estos valores: `insufficient_evidence`, `wrong_target`, `risk`, `duplicate`, `policy_conflict`, `wording`, `other`. Se guarda en `Approval` (campo opcional nuevo) y se copia al evento `rejected` como `reason_code`. El evento NO lleva el texto libre. `reason` sigue aceptandose igual, asi los clientes actuales no se rompen; un `reason_code` fuera de la lista es 422. Los eventos se guardan como JSON (`reg_events.event_json`), por lo que no hace falta migracion para el evento; `reg_approvals` necesita `ADD COLUMN IF NOT EXISTS reason_code text`.
Aceptacion: tras `reject` con `reason_code=duplicate`, `GET /v1/export/registry-events` devuelve un evento `rejected` con `reason_code: "duplicate"`; sin `reason_code` el campo es `null` y todo lo demas queda igual.

**2. (P1, plataforma) Selector de motivo en el dialogo de rechazo.**
Cambio: `RejectRequest` agrega `reasonCode` (enum anterior; requerido en la pantalla nueva, opcional en la API por compatibilidad) y lo reenvia a agent-core; `BuilderProposalRejected` agrega `reason_code` a la auditoria. El texto libre pasa a ser nota opcional, acotada a 280 caracteres, con la advertencia "no incluyas datos personales". Aceptacion: el rechazo desde la pantalla Agentes envia el codigo y la auditoria lo registra.

**3. (P2, agent-core, opcional) Ultima decision en el detalle.**
Cambio: `GET /v1/registry/proposals/{pid}` agrega `last_decision {decision, reason_code, at}` (sin nota ni actor). Por que: leer el motivo sin recorrer eventos. No bloquea nada: con el punto 1 nos basta.

## Por que ayuda y que no hacemos con el texto

Con `reason_code` el motor aplica una regla de enfriamiento (no reproponer el mismo cambio al mismo artefacto para la misma familia de hallazgo durante 30 dias si el motivo fue `wrong_target`, `duplicate`, `policy_conflict` o `risk`) y muestra "historial: N similares aprobadas, M rechazadas por R". El texto libre se trata como no confiable: nunca lo guardamos ni lo enviamos a un modelo; solo conservamos su longitud. Sin el punto 1 todo rechazo se lee como `unknown` y la regla no actua (comportamiento seguro, ya implementado y probado).

Quedamos atentos. Lector del lado motor: `scripts/feedback/decision_feedback.py`, notas en `docs/dev/DECISION_FEEDBACK.md` (rama `claude/fdbk1-decision-feedback`).
