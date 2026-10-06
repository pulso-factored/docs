# Auditoría final de preparación: data, seguridad, infra y operación

Fecha: 2026-10-01. Revisor independiente del implementador documental. Alcance: spec V2 completo, contraste focal de §§3–10, 18–21, 24–30 con análisis de producto A/B/C. No se modificó el spec. La navegación online pertenece al principal; este informe no afirma haber ejecutado los prototipos ni pruebas del producto.

## Veredicto

**Implementable por cortes TDD, con dos precisiones operativas pequeñas indicadas abajo.** No encontré motivo para rediseñar almacenamiento, aumentar servicios ni bloquear el tracer local con AWS/UX externa. La autorización para implementar y los gates de runtime siguen pendientes: esto acredita definición documental, no seguridad bancaria ya comprobada.

## Contraste desde la experiencia hasta los controles

| Experiencia observada en notas de producto | Contrato que la soporta | Resultado adversarial |
|---|---|---|
| Identidad/cuenta/contexto previo a llamada o email | §§24.1/24.2, 28.6 y 29.8: grants, identidad determinística, available_at por campo | Coherente: sesión/canal no prueba identidad; respuestas correctas no llegan a modelos/telemetría |
| Supervisora aprueba dinero; automatización aprueba release | §§20.1/20.2 y 27: autoridad por tipo/target, autorización humana justo antes del dispatch | Coherente: approve no significa efecto ni publish; TTL/revocación/asíncrono mantienen unknown sin retry ciego |
| Retención, roles, nueva consulta reutilizable | §§19/21/24.2: policy externa, tombstones, derived refs, executor existente | Coherente: interfaz administrativa no crea derechos bancarios; ToolDef sin executor queda bloqueada |
| Seguimiento de reclamo/respuesta solicitada | §§24 y 20.2: eventos durables, disponibilidad recibida, clocks y requested_reply | Coherente: recontacto no es necesariamente fallo; cierre no equivale resolución; SLA necesita policy/calendario |
| Panorama/valores/comparación | §§9/18/20: coverage, denominadores, factor_provenance y FX | Coherente: cifras ilustrativas no son observación; baseline se sella antes; brazos unknown no fabrican mejora |
| Activar 10/50/100%, probar interacción | §§20/27/29: dev TrialPlan independiente y capacidades unavailable | Coherente: selector no acredita canary upstream; pruebas dev no contaminan final ni producción |
| Debug completo y progreso visible | §§8/9/25: durable events + OTel auxiliar, permisos por objeto | Coherente: collector caído no borra estados; debug no exporta PII/final/raw ni concede autoridad Registry |

## Hallazgos a resolver sin ampliar arquitectura

### D1 — Divulgación acumulada en exploración SQL

Severidad: gate de seguridad **antes de datos bancarios reales**; no bloquea el primer recorrido sintético autorizado. §§3/19 aplican tratamiento y mínimo de agregación por resultado, pero ese mínimo aislado no evita inferir una persona restando dos consultas muy similares ni recuperar grupos pequeños mediante consultas repetidas.

Fix mínimo: fijar en SourceContract/policy del extracto un perfil de divulgación que distinga `synthetic_authorized` de información real; permitir pseudónimos sólo cuando el propósito/partición autorice observaciones individuales. Si se admiten sólo agregados sobre datos sensibles, denegar dimensiones/selectores individualizantes y contabilizar consultas/resultados acumulados por sesión, con política conservadora de solapamientos. No afirmar garantía formal de privacidad por un simple `n>=k`; ante política incapaz de controlar inferencia, materializar vistas agregadas aprobadas o bloquear ese perfil. No es necesario introducir differential privacy en el primer prototipo.

Tests: consultas con grupos aceptados individualmente cuya diferencia revela singleton; consulta repetida con filtros cambiados; escape por ORDER/LIMIT/proyección; sesión nueva no resetea indebidamente el presupuesto de divulgación del mismo propósito; false positive conservador queda reason visible, no éxito vacío.

### D2 — Restauración con objetivos medibles

Severidad: definición de aceptación operativa AWS; no bloquea desarrollo local. §19 especifica restore coherente PG/S3, tombstones y fail-closed, pero no fija objetivos de recuperación ni evidencia cronometrada por entorno.

Fix mínimo: RunConfig/DeploymentProfile versionado debe declarar RPO/RTO por entorno, estrategia PG/S3 y owner/runbook, explicitando que son objetivos hasta el drill. Antes de aceptar P5 AWS ejecutar restore aislado y medir pérdida real/tiempo; comprobar revocaciones posteriores al backup antes de servir, jobs/leases inciertos y ledger externo sin reenvío. No inventar 0 pérdida ni añadir HA innecesaria a demo local.

Tests: backup anterior a revocación, blob faltante, restore PG/S3 desalineado, job enviado sin ACK y acceso aún cerrado mientras overlays no se reconciliaron. Receipt del drill registra targets/resultados/entorno/digests/limitaciones.

## Infra, rendimiento y scope

- EC2/Podman corresponde a demo pública, ECS/Fargate/RDS a producto AWS: distinción expresa en §10, no incoherencia a eliminar unificando stacks.
- LocalStack sólo S3; no acredita permisos IAM/VPC/ECS. U28 requiere smoke AWS real autorizado; U25 manifest mínimo no acredita todos los componentes.
- Control API, worker, gateway y Core/bridge son procesos distintos; lógica por etapa no obliga microservicios adicionales.
- Claims PG cortos, SKIP LOCKED/fencing, cuotas atómicas, fairness por lane y reservas conservadoras definen concurrencia; tests de carga y fallos son entregables, no resultados actuales.
- `ingested_at` original y disponibilidad E0 están separados. E0 sin timestamp de recepción usa replay/lag supuesto; no convierte estado final en predictor histórico.
- E0/derivados permanecen locales por restricción particular del paquete; proveedores reales usan fixtures permitidos. No interpretar permiso genérico como excepción automática.
- GitHub/OIDC/locking/state/manifest/rollback, scripts compartidos y gates CI están definidos. No se requiere despliegue desde PR no confiable con secretos.
- F7/F8, asignación de asesores, autenticación cliente, ejecución financiera y canary real son plataforma externa; el motor ofrece contratos, pruebas fieles y estados dependency_blocked, no los reemplaza silenciosamente.

## Auditoría inversa y criterio de cierre

El implementador de U03/U04/U08/U29 debe poder demostrar fuente/clock/ref/permiso de cada factor. U20/U27/U35 demuestra juicio independiente y mejora emparejada; U21 demuestra autorización puntual sin token durable; U25/U28 demuestra entorno real y restore medido; U24/U32 sólo construye consola interna. Estas responsabilidades ya están adscritas al plan y no requieren nuevas unidades. Los dos fixes anteriores son adiciones a U08/U05 y U25/P5, respectivamente.

No hay un blocker documental de arquitectura para empezar P0/P1. Antes de datos reales o aceptación AWS, D1/D2 deben quedar precisados y luego probados. La revisión visual online y los veredictos frontend/backend/AI son evidencia separada necesaria para el cierre global.

## Recheck independiente de la corrección

Se volvieron a leer los dos párrafos normativos nuevos de §19 y la evidencia parcial de `AUDITORIA_NAVEGADA_PRODUCTO.md` después de la modificación del principal.

**D1 cerrado documentalmente:** la política se comparte entre sesiones por principal/propósito/extracto, incorpora consultas repetidas y diferencia/solapamiento, y define fail-closed mediante vistas agregadas aprobadas o bloqueo cuando no pueda evaluarse conservadoramente. Esto evita exigir un detector general perfecto de inferencia: el fallback restrictivo es explícito y verificable. Las observaciones individuales autorizadas se distinguen de agregados sensibles y del perfil sintético. Los cuatro tests negativos solicitados están incluidos. No acredita aún que el broker implemente esas restricciones; antes de información bancaria real deben pasar tests y revisión independiente de seguridad. La implementación no puede alegar que mínimo de grupo o presupuesto numérico solos demuestran privacidad.

**D2 cerrado documentalmente:** DeploymentProfile fija RPO/RTO por entorno y el drill AWS queda como gate medido, con pérdida/tiempo, estrategia, owner, revocaciones y reconciliación de efectos inciertos. Exceder el objetivo no pasa automáticamente. Aprobar un objetivo versionado distinto es una decisión explícita, no prueba de haber cumplido el anterior; ambos resultados deben conservarse en receipt/bitácora. Las pruebas PG/S3 desalineado, blob ausente, lease y ACK perdido están nombradas. No existe evidencia de restore ejecutado, correctamente reservado a la implementación.

**Veredicto actualizado:** no quedan blockers documentales en el ámbito data/security/infra/operación revisado para comenzar los cortes TDD. El cierre global aún requiere completar la navegación online y la revisión de otros roles; ni este recheck ni un Markdown válido sustituyen los gates de ejecución, autorización y despliegue.
