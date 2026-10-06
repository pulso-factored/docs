# Auditoría final — backend e integración frontend

Fecha: 01-10-2026. Revisor independiente `live_final_backend`.

## Alcance y evidencia

Inspección documental de V2, especialmente §§15/20.1/20.2/24/24.1/24.2/27/30, y lectura de las notas A/B/C y del análisis consolidado de producto. Las rutas y contratos son propuestos: no se ejecutaron APIs ni tests de producto. La navegación publicada corresponde al agente principal; este dictamen no atribuye navegación propia al revisor y se ampliará al contrastar su evidencia.

## Resultado de la revisión cruzada

No encontré un bloqueo arquitectónico que requiera más servicios, tablas o un frontend de atención propio. Los gaps de rondas anteriores están cerrados documentalmente:

- API canónica `/api/v1/evolution`; ingesta interna y Core mantienen superficies distintas.
- `CommandRef` discriminado y lookup durable; receipt, no click/202, determina éxito. Unknown externo domina el estado del job.
- Trials de desarrollo tienen plan, lectura de resultado y turnos con CAS/idempotencia; no escriben historia productiva ni exponen holdout.
- Decisión respondida no equivale a release publicada ni activada; promote/revoke fijan release/agent y digest interno sin inventar wire Core.
- Policy histórica fijada no elude revocación vigente; las fuentes temporales y métricas mixtas mantienen provenance.
- U24 es consola propia + pruebas contract-consumer/headless del producto externo; no implementación F8. Los controles de seguridad son prerrequisitos, no trabajo pospuesto a frontend/P5.

## Precisión mínima antes de cerrar U21

**Continuidad de reautenticación.** §20.2 define `waiting_human_reauthentication`, prepare/acquire y prohibición de persistir tokens, pero no fija explícitamente cómo el consumidor vincula una nueva autenticación al comando aceptado. No bloquea U01–U20 ni exige IdP nuevo; sí debe quedar cerrado antes de integrar el botón de aprobación con el dispatch asíncrono.

Fix mínimo: `CommandStatus` en espera expone una referencia autorizada de challenge/acción, no credenciales; la plataforma completa el step-up mediante `HumanAuthorizationPort` vinculado a command/decision/actor/target/operation vigentes. La reanudación es idempotente y CAS, no una segunda DecisionResponse. No adquirir firma para un command desconocido, finalizado, otro actor o target stale. No enviar de nuevo una operación unknown antes de reconciliar.

Tests de aceptación U21/U07: expire en cola→espera→reauth→un dispatch; callback duplicado; challenge consumido/expirado; actor o target cambiado; permiso revocado durante step-up; crash entre acquire y dispatch sin token durable; operación previamente enviada unknown conserva reconcile. El emisor local de tests puede materializar este contrato; la integración real continúa dependency_blocked si el puerto externo no está disponible.

## Veredicto por cortes

| Corte | Veredicto documental |
|---|---|
| Base, scheduler, datos y tracer U01–U14 | Listos para TDD incremental bajo aceptación existente |
| Memoria, propuesta y evaluación U15–U20/U26/U27/U35/U36 | Listos; separar builder/juez y no flexibilizar final/security gates |
| API y consola U07/U24/U32 | Listas como contratos por materializar; no prueba de UX funcionando |
| Autoridad/release U21 | Listo al incorporar la precisión de continuidad anterior en el contrato de integración |
| Segunda iteración/replay/operación | Listos por dependencias reales y estados unsupported explícitos; no asumir canary upstream |

Esta revisión no acredita implementación, provider/SSO reales, compatibilidad wire compilada ni efectos bancarios. Los schemas/fixtures OpenAPI y el recorrido API→PG→worker→Core→sandbox son gates de construcción, no razones para otra expansión de diseño.

## Recheck independiente: continuidad cerrada

Inspeccionada la precisión «Continuidad de reautenticación (U07/U21)» de §20.2 en el archivo actual y contrastada con HumanAuthorizationPort/CommandRef y target discriminado de la misma sección. **El hallazgo anterior queda cerrado documentalmente:** la vinculación identifica command/decision/actor/target/revision/operation, el status expone sólo referencia/expiry, la reanudación usa CAS sin segunda decisión, y un callback duplicado puede recuperar el recibo pero no adquirir otra firma ni repetir el envío. Stale/revocación/terminal/expiry y unknown están cubiertos explícitamente, con pruebas adscritas a U07/U21. No encontré una nueva incompatibilidad que impida construir ese corte. La implementación debe materializar schema y tests; no se acreditan por esta lectura.

Leído `AUDITORIA_NAVEGADA_PRODUCTO.md`: la evidencia publicada confirma de forma parcial centro de trabajo/Herramientas, ocho pantallas de automatización, propuesta full screen, árbol y una anotación de aprobación independiente. Es coherente con separación de efecto/autoridad, pruebas y readiness del spec. El inventario de 77 artboards **no prueba navegación de los 77**; acceso, supervisión, administración y app siguen pendientes de cobertura del principal en el registro inspeccionado. Mi veredicto backend/front es listo para implementación incremental, no cierre global de la auditoría navegada ni acreditación de todos los estados visuales.

## Recheck de integridad de presentación y cronología

Leídas la nueva precisión §20.2 y la evidencia adicional de supervisión/administración/app/acceso/paleta del registro navegable. Texto tipado, escape seguro, snapshot conocido al solicitar y eventos posteriores identificados cierran correctamente los dos defectos visibles (`[object Object]` y verificación posterior presentada en solicitud anterior). No aparece nueva brecha contractual backend/front: la regla de disponibilidad de §20.2 sigue exigiendo received/availability antes del cutoff, por lo que «conocido» no debe implementarse sólo con occurred_at. La autorización vigente en dispatch sigue distinta del soporte histórico mostrado. Los tests U07/U24/U32 propuestos cubren tipo/XSS/orden y atribución temporal; U21 conserva autoridad/revalidación. Sin nuevas tablas, servicios o correcciones al artefacto externo.

La cobertura navegada creció a los ocho grupos e interacciones representativas, pero aún no prueba todas las variantes lazy-loaded ni cada control. Éste sigue siendo un cierre documental por rol, no una certificación visual integral.
