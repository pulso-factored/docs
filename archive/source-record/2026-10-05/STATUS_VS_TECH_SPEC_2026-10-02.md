# Pulso Improvement Engine — estado frente al Tech Spec V2

**Corte de la auditoría:** 2 de octubre de 2026, America/Bogota. Las consultas a GitHub ocurrieron después de los merges registrados en UTC el 3 de octubre.  
**Objetivo:** establecer qué existe de verdad, dónde, y qué falta para terminar; no es una declaración de release ni una autorización para desplegar.  
**Spec de referencia:** [`TECH_SPEC_PULSO_AUTOMEJORA_V2.md`](TECH_SPEC_PULSO_AUTOMEJORA_V2.md), especialmente §§1, 11–12, 17–30.  
**Base autoritativa del engine:** `main` SHA `dcb5bd750485ca1fda7d6fff1df02dea50b8dae7` (merge de PR #68).  
**Base autoritativa de infra:** `main` SHA `8aff5a165207c28165e4736f6ab95789a7d0af70` (merge de PR #15).

> **Lectura ejecutiva:** tenemos una cantidad importante de contratos, componentes de dominio y una ruta local de simulación. Todavía no tenemos el producto autónomo E2E descrito por el spec. La ejecución actual de `main` del engine está bloqueada por un error sintáctico que hace fallar format/build/test; el caso de éxito E0 autenticado (dataset → evidencia U12-E → Scout U13-E → propuesta) no está conectado al runner; tampoco existe el ciclo completo de evaluar, publicar bajo aprobación, observar resultado y usar memoria en otra corrida. La fundación Terraform está declarada, no desplegada.

## 1. Cómo leer este mapa

Los estados describen el **alcance del caso de uso**, no sólo la existencia de un archivo:

| Estado | Significado |
|---|---|
| **Integrado, parcial** | Código y tests están en `main`, pero sólo una parte del caso de uso o del DoD del spec está cubierta. |
| **Integrado, base funcional** | El contrato/feature está en `main` y tiene pruebas focales; aún no equivale al recorrido de producto completo. |
| **En progreso local** | Hay cambios en un worktree, sin commit/PR; no cuenta como entregado ni como parte de `main`. |
| **Branch-only** | Hay un merge/commit en una rama distinta de `main`; no está disponible a un clon de `main`. |
| **Pendiente** | No encontré implementación suficiente para el caso de uso requerido. |
| **Bloqueado** | Una dependencia, autoridad externa o fallo de verificación impide afirmar aceptación. |

Cuando el status documentado contradice el árbol de código o el historial Git, este mapa da prioridad al SHA de `main`, a la ruta de código/tests en ese SHA y al `baseRefName` real del PR. Un contrato, test unitario, mock, PR mergeado en una rama lateral o Terraform válido **no** se cuenta como ejecución del sistema completo.

## 2. Estado de entrega y bloqueos que afectan todas las fases

### Engine

- GitHub reporta `main = dcb5bd7`. No hay PR abierto al momento de la consulta.
- El workflow ejecutado para ese SHA (`37089177840`) terminó **failure** en Windows, Ubuntu y el job PostgreSQL. El error raíz es sintáctico en `crates/source-adapters/tests/source_adapters.rs`: delimitador sin cerrar dentro de `original_contacts_expose_only_suppressed_snapshot_counts_by_safe_categories` (la lista iniciada cerca de la línea 35 vuelve a abrir un `for` antes de cerrar el anterior). Por ello, el check de formato falla y el job PostgreSQL tampoco puede compilar. No debe describirse `main` como actualmente verde/ejecutable hasta reparar esto y repetir el CI del nuevo head.
- PRs #63–#68 se integraron en `main`. **PR #69 y PR #71 aparecen como “merged”, pero sus destinos fueron ramas feature, no `main`:** #69 se mergeó en `feat/p2-e0-retry-error-overlap`; #71 en `feat/e0-frozen-memory-cycle`. Ambos tuvieron checks verdes en su propio head, pero su contenido adicional no forma parte de `main` por ese hecho.
- El checkout principal local está en `feat/l0-engine-foundation` (`6bf9c3d8`), no en `main`. Hay 55 worktrees del engine en disco; 8 muestran cambios sin commit, entre ellos el worktree del runner U12→U13-E. Es inventario, no autorización para borrar: varios contienen trabajo recuperable.
- No hay PR abierto; Issue [#70](https://github.com/pulso-factored/improvement-engine/issues/70) sigue abierto para componer U12-E→U13-E en el runner. El worktree `feat/p2-u12-u13-e0-runner-compose` tiene 15 archivos modificados más `.target-u12-u13/`; su `HEAD` es `b5850c8`, basado en una línea antigua. Comparado con `main`, el diff heredado incluye decenas de eliminaciones de cambios ya integrados. No es publicable directamente; se requiere port selectivo a una rama fresca.

### Infra

- GitHub reporta `main = 8aff5a1`; no hay PR abierto. PR #15 pasó checks Windows y Ubuntu.
- Terraform en `terraform/envs/{staging,prod}` y `terraform/modules/` declara una foundation con red/seguridad, identidad, buckets, secretos, RDS, ECS/Fargate y telemetría básica. **No hay evidencia de `plan/apply` ni de un entorno AWS desplegado.** CI es validación sin credenciales; no existe despliegue automático.
- El repo deja explícito que el engine posee Podman/Compose/LocalStack y su suite local. Infra no debe duplicar ese runtime.
- Permanecen prerequisitos externos: OIDC y backend/state aprobados, secretos/rol de DB runtime, egress controlado para Jev/LLM, ingreso privado/autenticado para debugging, y métricas/alarms operacionales del engine. Agent Core aún no se declara como workload Terraform.
- El checkout local de infra tampoco está en `main`; está en una rama U01. Para medir lo desplegable se tomó el SHA de GitHub y `docs/architecture/deployment-status.md`, no ese checkout.

## 3. Estado por fase P0–P5 del spec (§30.3)

| Fase | Estado | Ya existe | Para pasar el gate del spec |
|---|---|---|---|
| **P0 — Base mínima** | **Parcial; bloqueada por CI rojo** | Repos separados, workspace Rust, contratos/manifests de fuentes, almacenamiento versionado y migraciones, CI del engine y Terraform staging/prod. Hay wrapper local para E0. | Reparar CI en `main`; comprobar desde clone limpio `doctor`/arranque, Podman Compose PostgreSQL+S3 local, snapshot readonly reproducible y persistencia real. Cerrar grants/cuota y job/admisión con fencing; no basta el ledger de eventos. |
| **P1 — Tracer técnico** | **Parcial** | Ingesta de observaciones U29, sensor determinista U30, algunas señales E0, progreso CLI y lectura autenticada de timeline. | Integrar trigger→job→task/receipt→query adaptable→timeline. Completar ruta de observabilidad real de las cuatro capas a U29, instrumentación del propio engine y Jev/LLM bajo presupuesto. Aún no hay endpoint/UI de debugging. |
| **P2 — Hallazgo explicable** | **Parcial; principal brecha de demo** | Sensores deterministas, Scout, verificador y simulación local. E0 tuvo un smoke histórico acotado con métricas agregadas; no prueba causa ni lift. | Conectar evidencia sellada U04/U08-E→U12-E→U13-E en el runner y ejecutar la muestra aumentada sin labels en discovery; verificar propuesta sustentada/no-op, salida privada y holdout segregado. Añadir un camino original que llegue a oportunidad sin llamar “causal” a un conteo descriptivo. |
| **P3 — Cambio evaluable** | **Mayormente contratos aislados; no gate completo** | Bridge, eligibility, compiler, registry writer en memoria, plan/oracle sellado y sandbox sintético stateful tienen piezas y pruebas propias. | Flujo integrado oportunidad→alternativa/`do_nothing`→bundle compatible→writer→sandbox real→comparación baseline/candidato con oracle sellado. Diferenciar native evaluation de admisión; hoy U19 no ejecuta ni produce veredicto. |
| **P4 — Automejora E2E** | **Parcial/prototipos; no cumple el caso de éxito** | Memoria versionada/gobernada, CAS, recibos, protocolos temporales y piezas Frozen E0. Existe composición adicional de dos runs en rama feature. | Una corrida debe descubrir sin guía humana, proponer y evaluar; aprobación humana excepcional y mock fiel de release; evento de plataforma provoca segunda corrida que usa/contradice memoria. Cerrar persistencia U33-E y grant transaccional U05; conectar U22/U23 con scheduler/eventos. PR #71 no está en `main`. |
| **P5 — Entrega robusta** | **Parcial** | CI engine e infra; AWS foundation declarada para staging/prod; run event/debug read model interno; docs/ADRs/journal existen. | CI verde sostenido, métricas/trazas/alarmas operables, consola técnica/API autenticada, carga/chaos, runbooks, Terraform plan/deploy manual aprobado, smoke/rollback y reproducción por tercero. No se incluye F7/F8 ni despliegue bancario real. |

**Conclusión de fase:** no hay ninguna fase cerrada según su gate normativo. P0/P1 contienen infraestructura útil pero no cierre de aceptación; P2 tiene el prototipo local más demostrable; P3/P4 aún no conectan la ruta de producto; P5 tiene declaraciones y checks, no operación desplegada.

## 4. Mapa de features y casos de uso U01–U36 (§30.8)

| ID | Caso de uso del spec | Estado frente a `main` | Qué falta para aceptar el caso de uso completo |
|---|---|---|---|
| **U01** | Levantar entorno mínimo; doctor detecta setup roto | **Integrado, parcial** — workspace, Rust CI, utilidades locales y compose del engine existen | Un `doctor` coherente/validado desde clone limpio y stack local reproducible; el CI de main debe volver a verde. |
| **U02** | Publicar artefacto inmutable y avanzar head por CAS | **Base funcional** — migraciones, refs/digests y contratos de escritura | Validación durable de concurrencia/tenancy contra PG real y recorrido desde el runner/job; fallos actuales de compile impiden revalidar en el SHA. |
| **U03** | Registrar y reproducir snapshot original readonly | **Integrado, parcial** — adapter/proyección de fuente original y reglas de privacidad | Manifest/cutoff reproducible para los facts usados por descubrimiento; llegar desde snapshot a señal/oportunidad, no sólo recuento. |
| **U04** | Registrar E0 con namespace, procedencia y clock | **Integrado, parcial** — source adapter y replay V2/U04-B están en core | Ejecutar el contrato autenticado a través de todo el CLI; el runner actual usa preparación/proyección segura separada. |
| **U05** | Resolver grant vigente y reservar presupuesto global | **Parcial/bloqueante** — hay referencias de grant/cuota en contratos y consumidores | Autoridad, versión, liveness/revocación y saldo deben resolverse dentro de límites transaccionales; dependencia crítica para escritura/publicación durable P4. |
| **U06** | Deduplicar triggers y ejecutar jobs con lease/fencing | **Pendiente/parcial** — no está cerrado el scheduler/admission durable | `logical_key`, lease, SKIP LOCKED, fencing, retry/DLQ y recuperación de restart conectados al engine; U07 no lo reemplaza. |
| **U07** | Consultar actividad durable del run por API/cursor | **Integrado, parcial** — PR #59 y migración/ledger; relacionado con U24 V2 | Conectar reducer/eventos con admisión/leases U06 y runner; probar continuidad/recuperación como un job completo. |
| **U08** | Ejecutar queries adaptativas con scratch aislado | **Parcial** — lab local/SQL y ruta de query E0 están en core | Aislamiento real por run, grant, tabla/campo y cutoff; que la query del runner emita receipt que autentique al sensor. |
| **U08-E** | Consultar E0 únicamente hasta el reloj/corte permitido | **Base de contrato integrada** — ver `e0_query_lab.rs` y fuente sellada | Conectar al CLI/sensor en un recorrido autenticado; test contra el paquete E0 real. |
| **U09** | Ejecutar etapa Core fijada y recuperar receipt | **Parcial/simulado en demo** | Integración contractual ejecutable con Agent Core y receipt real; hoy la ruta local usa simuladores/adapters. |
| **U10** | Llamar modelo externo con presupuesto y receipt | **Pendiente como integración real** — interfaces/simuladores existen | Gateway/servicio externo acordado (no construir otro gateway), proveedor con policy/PII/budget/timeouts y smoke live autorizado. |
| **U11** | Ejecutar decisión Jev tipada y calibrar baja confianza | **Pendiente como integración real** — hay contrato/código de decisión | Primitivas de Agent Core/Jev conectadas, versión/policy/receipt y casos live; no hay llamada efectiva desde el flujo. |
| **U12** | Medir señal determinista con denominador y missingness | **Integrado, parcial** — sensor genérico y reglas de señales E0 en core; runner local usa señales descriptivas | Usar U12-E sobre `VerifiedE0QueryResult` desde el runner y fijar contract/transform/cutoff end-to-end. |
| **U12-E** | Medir señal diagnóstica sobre evidencia E0 sellada | **Implementado en core, no cableado al runner** | La entrada autenticada y sus receipts tienen que recorrer CLI; agregar positivo, cero, evidencia drift y contrato incompatible. |
| **U13** | Investigar señal y emitir drafts con procedencia | **Base funcional parcial** — Scout genérico y drafts simulados en el camino local | Integrar autenticación/receipts y no usar un `QueryResult` público como evidencia. |
| **U13-A** | Admitir sólo candidatos Scout verificados | **Integrado como boundary** — capacidad opaca/batch y tests | Consumidor U14 en flujo persistente y verificación completa de commitments; no equivale a propuesta durable. |
| **U13-E** | Admitir Scout E0 autenticado | **Implementado en core, no cableado al runner** — exige U12-E más receipts U09/U10 | Resolver receipts compatibles sin falsificarlos; composición CLI y prueba positiva sobre muestra. La lane actual simula receipts y está sin PR. |
| **U14** | Verificar/refutar hipótesis independientemente | **Parcial** — verificador estructural soporta supported/refuted/uncertain | Consumir candidatos del runner; Jev real y persistir reports; demostrar evidencia distinta de la señal original. |
| **U14-E/EQ** | Consistencia Frozen E0 y calificación sin causalidad | **Parcial, contrato local** | Durabilidad e integración downstream; no afirmar outcome, causalidad ni elegibilidad comercial antes de U16/U20/U35. |
| **U15** | Leer/transformar wiki en scratch autorizado | **Parcial/local** — transformaciones y resúmenes E0 existen | Integrar recuperación libre pero gobernada con el agente y el flujo de propuesta; redacción/auditabilidad en ejecución. |
| **U15-EQ** | Preparar resumen Frozen sin filtrar texto | **Boundary local implementado** | Consumir y publicar duraderamente; hoy no es memoria durable lista para segundo run. |
| **U16** | Convertir evidencia verificada en bridge/mecanismo y alternativas | **Integrado como contrato parcial** — `WorkflowBridge`, `do_nothing` y grados de evidencia | Producir alternativas de negocio con trazabilidad a hallazgo; conectar con plan U20 y posterior build. |
| **U17** | Compilar cambio autorizado a drafts inmutables | **Parcial/contractual** — compiler sellado existe | Consumir una propuesta real y compilar un artefacto Agent Core válido, probar compatibilidad real del schema Core. |
| **U18** | Escribir/fijar candidato en registry gobernado | **Parcial, adapter en memoria** | Writer durable transaccional e integración real con registry/Agent Core; evidencia que el payload congelado coincide con el autorizado. |
| **U19** | Ejecutar candidato nativo en sandbox y obtener `EvalRun` | **Bloqueado** — existe gate de admisión U19-0, no executor/verdict | Agent Core Unit 6 `EvalPort`, harness/sandbox y registered candidate readback; no reportar resultado simulado como evaluación nativa. |
| **U20** | Sellar baseline, oracle, suites y plan antes del candidato | **Boundary implementado, integración parcial** — evaluación plan/oracle E0 existen | Completar selección independiente del candidato y conectar U19/U27 con fixtures/suites exactos sin leakage. |
| **U20-E** | Fijar oracle de seguridad E0/identidad | **Boundary local implementado** | Consumirlo en candidato/sandbox E0; faltan campañas reales del runner y registro reproducible. |
| **U21** | Aprobación humana y release simulado/staging con receipt | **Pendiente como recorrido** | Contrato de decisión/step-up, release ack mock fiel y estado/timeout realista conectados al candidate aprobado. |
| **U22** | Evento dispara segunda investigación que usa memoria | **Boundary gobernado parcial** | Evento→job→segundo run real, receipt de uso y memoria exacta en la corrida; el ciclo está fragmentado. |
| **U22-E** | Iterar a partir de E0/replay con memoria | **Pendiente de integración** | Runner/campaign, U13/U14/U21/U23/U33 y receipt en un flujo automático. |
| **U23** | Ejecutar replay Frozen/Continuous sin leakage | **Parcial** — protocolo temporal/frozen local | Runner de campañas, cobertura/scoring y relación con un outcome observable; Continuous requiere evidencia posterior aceptada. |
| **U23-A / U23-E** | Activar sólo lo aprobado; revalidar uso publicado Frozen | **Parcial/local; durabilidad bloqueada** | U05 grant liveness y U33-E publication en una transacción PG; sin esto no hay recibo durable/autónomo. PR #71 no está en main. |
| **U24** | Consultar timeline autenticado sin shell | **Boundary de lectura integrado, parcial** — PR #68, secuencia y paginación tenant-scoped | Exponer endpoint/API y consola técnica con auth real, streams/read models completos; actualmente interno/read-only. CI de main está rojo. |
| **U25** | Desplegar imagen por manifest y rollback | **Infra declarada, despliegue pendiente** | Bootstrap/state/OIDC, pipeline manual aprobado, image digest, migración, health/smoke/rollback y staging aplicado. |
| **U26** | Sandbox stateful con acciones y readback por brazo | **Boundary simulado/local funcional** | Integrarlo con U19 real, separar namespaces/semillas y probar fault/reset/no-sharing; no es servicio bancario real. |
| **U27** | Comparar baseline/candidato sin fabricar lift | **Parcial/contractual** | Evaluación pareada ejecutable, oracle congelado, suficiente cobertura y registro de mejora/inconcluso; no hay resultado de negocio causal. |
| **U28** | Lab remoto AWS con grants por objeto | **Pendiente** | Sesión/remoto/IAM/TTL real y aislamiento, tras U25/U05. No bloquea la primera demo local. |
| **U29** | Ingerir observaciones durables de las cuatro capas | **Integrado, parcial** — schema/proyección, tenant, contrato y persistencia | Consumir stream/export real de plataforma y probar cursors/coverage operacional; sampled OTel no representa denominador. No construir F7/F8. |
| **U30** | Detectar señales por capa desde observaciones | **Sensor integrado** — PR #41 y pruebas | Seleccionar/meter señal en U13 con issuer/receipt autenticado; el camino a oportunidad/propuesta sigue incompleto. |
| **U31** | Proponer evolución del propio detector con juez externo | **Pendiente** | Casos/test-suite de evolución, juez independiente y ejecución de candidato de motor sin que el candidato altere el oracle. |
| **U32** | Inspeccionar queries/modelos/evals/memoria en consola | **Pendiente** | Read models U32-M/V/W más API/console U24; debugging actual sólo cubre actividad segura. |
| **U33** | Publicar/revocar memoria versionada por CAS | **Parcial, límites en main** — revisiones, heads/tombstones/receipts genéricos; piezas Frozen E0 locales | Publicación E0 durable, grant resuelto transaccionalmente, revocación/restore en runtime y segunda corrida. |
| **U34** | Pausar/cancelar run con receipt veraz y fencing | **Boundary implementado, integración parcial** | Integrarlo al lifecycle U06 y al proceso real; manejar unknown/timeout sin declarar cancelación falsa. |
| **U34-F/FE** | Fork inmutable de corrida original o E0 | **Parcial, boundary in-memory** | Conectar persistencia, grants, scheduler, artefactos y replay futuro revocado. |
| **U35** | Permitir construir sólo con evidencia/bridge/plan listos | **Gate determinista parcial** | Conectarlo antes de U17/U18 en el journey completo; no prueba que la propuesta sea de valor ni fue evaluada. |
| **U36** | Proteger identidad/acción sensible en sandbox fixture | **Boundary de fixture implementado** | Integrar con U19/E0 journey; no es un IdP ni control de identidad real de la plataforma. |

## 5. Fuentes/datasets y qué se ha demostrado

| Fuente/recorrido | Evidencia disponible | Lo que no demuestra |
|---|---|---|
| **Dataset original** | Preparación/read-only y proyección segura por razón × canal. Recuenta filas CSV (`record_count`), usa supresión `k`, no deduplica `interaction_id`. | No es cohorte temporal; no permite inferir contactos repetidos, PQR/SLA, outcome, causalidad ni ahorro. El PR #69 que añade una propuesta descriptiva fue mergeado a rama feature, no a main. |
| **Muestra aumentada E0** | Smoke local histórico descrito por el status: 200 casos Arranque; recurrence de una query opaca 154/200; errores técnicos 0/187 y 13 missing; overlap no evaluable por cobertura; tres candidatos y una propuesta exploratoria. Las labels no entran a discovery y la salida tuvo PII sentinel scan. | No confirma solución automática, calidad semántica de un candidato, causalidad, lift, impacto financiero ni una nueva ejecución de la cadena autenticada U12-E→U13-E en main. La lane actual sólo probó un caso no-op (1/1) después de cambios; la prueba positiva anterior no cubre todos los cambios recientes. |
| **Observabilidad de la plataforma** | Contratos U29 y sensores U30 sobre observaciones preparadas. | No hay captura live de OTel/trazas de las cuatro capas y no debe usarse cobertura muestral como denominador de casos reales. |

## 6. PRs, ramas, worktrees y estado de pruebas

| Ítem | Estado verificado | Implicación |
|---|---|---|
| Engine PRs abiertos | Ninguno | No hay un PR listo para que el usuario revise ahora. |
| Engine PR #69 | Merged a `feat/p2-e0-retry-error-overlap`; checks de su head verdes | Proyección descriptiva→propuesta adicional está en rama acumulativa, no en `main`. |
| Engine PR #71 | Merged a `feat/e0-frozen-memory-cycle`; checks de su head verdes | Composición de lecturas de memoria entre runs está fuera de `main`; es local/in-memory, no durabilidad de producción. |
| Issue #70 | Abierto, `ready-for-agent` | Objetivo del slice central U12-E→U13-E CLI. Worktree sucio y base antigua, no se puede convertir en PR sin port selectivo. |
| Otros Issues | Siguen abiertos varios IDs U08-E/U12-E/U13-E/U17–U20/U22–U23/U30/U34 | El issue abierto no siempre indica ausencia de código; algunos contratos ya están en `main`. Debe reconciliarse backlog contra SHA antes de reasignar. |
| CI engine | El check de `main` dcb5bd7 está rojo; los merges rápidos #63–68 dejaron runs cancelados y el run de #68 fallido | Primer gate al reanudar: reparar el delimitador en rama, TDD, validar workspace completo local, abrir PR correctivo y esperar CI verde antes de seguir consolidando sobre `main`. |
| Worktrees engine | 55 registrados; 8 dirty en inventario | Riesgo de perder trabajo y de abrir diffs obsoletos. No borrar ni hacer reset por conveniencia; primero asignar dueño, distinguir artefactos `target/` de cambios valiosos y decidir port/archivo. |
| Infra PRs | Ninguno abierto; main #15 y CI del PR #15 verde | La foundation está en main, pero el siguiente paso depende de decisiones/accesos externos; no se debe confundir CI Terraform con deploy. |

## 7. Qué impide terminar y el orden de cierre más eficiente

Esto es una lectura de dependencias del spec, no un calendario comprometido (no tenemos fecha límite ni capacidad/horas del equipo confirmadas en esta conversación).

1. **Restablecer `main` como base verificable.** Reparar error de sintaxis/CI en una rama de fix; local fmt, clippy y tests antes del PR, luego CI Win/Linux/PostgreSQL. No añadir features encima de una base roja.
2. **Reducir y reconciliar ramas antes de nuevos PRs.** Identificar los cambios que hoy sólo están en ramas de feature: primero incorporar de forma deliberada #69 y #71, validando conflictos y que su test set no elimine código ya integrado. Mantener sus limitaciones honestas.
3. **Cerrar el tracer E0 autenticado (P2, #70).** Partir de un worktree fresco en el nuevo `main`; llevar sólo el cambio U02/U04/U08→U12-E→U13-E y sus negativos. TDD RED→GREEN para positivo, cero señal, contrato incompatible, drift/PII; luego smoke de la muestra aumentada sin labels y revisión adversarial. Etiquetar como simulación si receipts Core/LLM son simulados.
4. **Cerrar el recorrido de evidencia hasta propuesta.** Original y E0 deben ser caminos distintos que convergen en el mismo modelo de señal→hipótesis→propuesta. No llamar propuesta a un recuento agregado ni mezclar resultado de holdout con discovery.
5. **Conectar evaluación P3.** Un candidate compatible y congelado debe ejecutar en sandbox stateful contra baseline/oracle sellados. Hasta tener Agent Core Unit 6/`EvalPort`, mantener native evaluation `dependency_unavailable`; no simular el resultado de runtime.
6. **Cerrar segundo run P4.** Persistir memoria y su autorización/revocación de forma transaccional; el evento debe crear un sucesor idempotente que reutiliza o contradice el aprendizaje. El humano autoriza efectos de publicación, no el hallazgo.
7. **Completar plataforma operable P1/P5.** OTel/receipts de las cuatro capas como insumo de detección y telemetría propia del engine como operación son dos cosas distintas. Cerrar issuer→Scout para U29/U30, API/console técnica, alarmas de cola/progreso/error/costo, runbook y tests de carga/fallos.
8. **Cerrar deploy/reproducibilidad.** Local clone/test + sample reproducible; después staging AWS con inputs autorizados, CI/CD manual, health/migration/smoke/rollback. `prod` es demo; no producción bancaria. No empezar por AWS si el tracer local sigue rojo.

**Agrupación PR recomendada para que sea reviewable sin trivializar:** (A) reparación CI + status docs canónicos; (B) runner E0 autenticado + dataset smoke; (C) camino original y convergencia evidence→proposal, incluyendo el port de #69; (D) sandbox evaluation + baseline/oracle + gates; (E) memoria cross-run durable + #71 port; (F) señales de plataforma a proposals + instrumentación/console/operación. Los grupos pueden paralelizarse sólo cuando sus contratos/file ownership no se solapen; cada grupo requiere tests y revisión adversarial propios. Esta recomendación no presupone fechas ni autoriza merge automático.

## 8. Gaps de documentación que deben corregirse al reanudar

- `improvement-engine/docs/IMPLEMENTATION_STATUS.md` en `dcb5bd7` está desincronizado: llama a U07/U24 y otros cortes “implemented in cumulative branch (not yet merged)” aunque los PRs/commits correspondientes están en el historial de `main`; por otro lado, el propio historial Git muestra PRs #69/#71 mergeados sólo a ramas laterales. Actualizar el status contra el commit exacto y destino de PR.
- Infra `docs/architecture/deployment-status.md` y `docs/gaps/OPEN_GAPS.md` sí distinguen Terraform declarado de entorno aplicado; conservar esta distinción.
- Cada slice que se incorpore debe actualizar docs de comportamiento y journal con commit/base, RED/GREEN, comando, prueba omitida, entorno, limitación y revisión adversarial. No registrar “completo” sólo por tener módulo o issue cerrado.

## 9. Fuentes consultadas

- Spec: `docs/TECH_SPEC_PULSO_AUTOMEJORA_V2.md` — §§1, 11–12, 17–30 y catálogo U01–U36.
- Engine `main`: `dcb5bd750485ca1fda7d6fff1df02dea50b8dae7`; `docs/IMPLEMENTATION_STATUS.md`; `docs/local-e0-e2e-runner.md`; `docs/journal/0050–0053-*`; CI run `37089177840`.
- GitHub engine: [PR #68](https://github.com/pulso-factored/improvement-engine/pull/68), [PR #69](https://github.com/pulso-factored/improvement-engine/pull/69), [PR #71](https://github.com/pulso-factored/improvement-engine/pull/71), [Issue #70](https://github.com/pulso-factored/improvement-engine/issues/70). También se consultaron PRs abiertos y issues abiertos al corte.
- Infra `main`: `8aff5a165207c28165e4736f6ab95789a7d0af70`; `README.md`, `docs/architecture/deployment-status.md`, `docs/gaps/OPEN_GAPS.md`; [PR #15](https://github.com/pulso-factored/infra/pull/15).
- Worktrees: `git worktree list --porcelain` y `git status --porcelain` ejecutados sobre los 55 worktrees registrados; se inspeccionaron las ramas del E2E, P2, P4 y P1.
- Auditorías read-only independientes: E2E/P2; P0/P1/P3 e infraestructura; P4 memoria. No se ejecutó implementación, no se abrió ni cerró PR, no se limpió ningún worktree.
