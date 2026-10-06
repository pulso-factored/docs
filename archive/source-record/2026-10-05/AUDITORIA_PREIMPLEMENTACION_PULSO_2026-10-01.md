# Auditoría preimplementación — Pulso V2

## Alcance y método

Nueva auditoría, sin asumir que el cierre anterior probaba ausencia de errores. Tres revisores independientes actuaron como backend distribuido/AI, data/evaluación e infraestructura/SRE/frontend. El editor contrastó además persistencia, referencias, hashes e invalidación. Se corrigió el spec, no código de producto ni upstream.

## Hallazgos y contratos corregidos

| Hallazgo | Corrección normativa | Regresión exigida |
|---|---|---|
| Config nueva abre otro presupuesto | PK de cuota sin config_ref; contador global por ventana, consumo/reservas preservados | A reserva 80/100 y B pide 30: rechazo salvo ampliación autorizada |
| Dos start_run con misma key antes del commit | Single-flight y binding CAS a un único CoreRun antes de modelo/query/write | POST concurrentes y crash después de write, sin segunda propuesta |
| RunState ausente interpretado como no ejecución | Readback in_progress/unknown/terminal, consulta de writes antes de sucesor | Kill entre write y commit conserva unknown sin retry ciego |
| PK/FK y refs implícitas | PK artifact con revisión; refs tenant-aware; eventos validan raíz y pertenencia | FK cross-tenant, hijo usado como raíz y job de otro run rechazados |
| Baseline elegida después del resultado | BaselineSelectionReceipt sellado antes del candidato | Baseline post hoc o release cambiada invalida campaña |
| Mejora por excluir casos difíciles | Universo sellado, pares comunes y guardrails de cobertura/unknown | Candidato que falla en grupo difícil no pasa por denominador reducido |
| IAM task compartido no aísla sesión | Broker concede URLs por objeto exacto, task sin S3 amplio, TTL/revocación | Task A no lee/escribe/lista B |
| Backend Terraform/OIDC inexistente en primer clone | Bootstrap administrativo y migración state; luego CI OIDC | Segundo bootstrap idempotente y doctor falla si faltan prerequisitos |
| Memoria/hash sin semántica uniforme | JCS interno, decimales como strings, overlay revocación, SourceRef con namespace/mundo/snapshot | Golden bytes Rust/Python y restore con tombstone |
| EvaluationPlan acepta configuración incompleta | Validación fail-closed de métricas, CI, cobertura, mínimos y baseline | Plan incompleto rechazado antes de llamar proveedores |

## Comprobaciones y límites

Backend, data e infraestructura revalidaron sus correcciones con cierre documental favorable. La precisión adicional de PK artifact/raíz se incorporó después del recheck; también se aclaró la expiración residual de URLs ya emitidas. La comprobación estructural del spec pasó: 29 secciones ordenadas, fences, anchos de tablas y enlaces locales. No implica verificación semántica automática.

Los tests de la tabla son requisitos para TDD, no resultados ejecutados. No se acredita runtime, integración, seguridad efectiva, benchmark ni despliegue. El contrato queda propuesto para aprobación; S0 debe materializar schemas/fixtures/versiones y probar el primer recorrido vertical antes de integrar el resto.
