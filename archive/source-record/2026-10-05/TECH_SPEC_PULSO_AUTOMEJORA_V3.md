# Pulso — tech spec V3: motor autónomo de detección y automejora

**Repos y entorno confirmados:** `pulso-factored/improvement-engine` e `pulso-factored/infra`, checkouts locales homónimos. Sustituyen los nombres inicialmente propuestos `pulso-engine`/`pulso-infra`. Desarrollo inicial Windows/PowerShell; WSL es alternativa a evaluar sólo ante incompatibilidades importantes, no requisito automático de bootstrap. Los controles de aislamiento Linux del sandbox se validan dentro del backend de contenedores, sin presumir que el host Windows los aplica nativamente. Los stacks y paths quedan reconciliados con estas decisiones; las capacidades externas y el aislamiento efectivo siguen sujetos a verificación antes de su uso.

**Corrección de alcance vigente — 01-10-2026:** implementamos exclusivamente el servicio de detección y automejora y su infraestructura. `agent-core` y el acceso a modelos son dependencias externas: no se construye otro Agent OS/runtime ni un `llm-gateway` propio. El repositorio real de infraestructura es `pulso-factored/infra` (local `infra/`); `pulso-infra` era un nombre propuesto. Las obligaciones anteriores de construir proxy/gateway, imágenes/endpoints y U10 quedan sustituidas por integración con capacidades externas y pruebas del consumidor. No se elimina tratamiento de datos, presupuestos, receipts ni observabilidad del motor. Ver [decisión y pendientes](ADR_ALCANCE_SERVICIO_AUTOMEJORA.md). **Reconciliación documental cerrada:** §§4/10/23/29/30 y sus dependencias reflejan esta frontera. Las capacidades externas, credenciales y enforcement siguen pendientes de verificar por sus cortes de integración; este cierre no acredita servicios desplegados ni autoriza construir un gateway.

**Corrección I03 de ownership — 01-10-2026:** `improvement-engine` es autocontenido para desarrollo, pruebas e integración: posee sus manifests/fixtures, `Podman Compose`, PostgreSQL efímero de CI, LocalStack y perfiles de test. `infra` posee exclusivamente Terraform y la infraestructura AWS de despliegue (red, IAM, state, cómputo, datos administrados, observabilidad y runbooks de despliegue). Ningún PR del motor llama workflows reutilizables de `infra`, fija SHA de otro repositorio para probarse, ni deposita sus fixtures locales allí. Esto elimina una dependencia de permisos GitHub inter-repo que no prueba el producto. La migración I03 mueve esos recursos al motor y retira el caller; `infra` no conserva una copia de Compose ni un workflow de pruebas del motor. Ver ADR y bitácora para trade-off y secuencia.

**Alineación I08 de despliegue — 02-10-2026:** la frontera anterior es el diseño objetivo, no una afirmación de paridad ya operativa: el CI PostgreSQL del motor está aislado, pero su stack local Compose/LocalStack todavía requiere su propio corte verificado antes de retirar la última capacidad local heredada. En AWS, `infra` declara red, IAM, ECS/Fargate, RDS, S3, Secrets y el sustrato inicial CloudWatch/SNS; no hay `apply`, despliegue, ingress debug, conectividad runtime→RDS ni alarma operacional del motor acreditados. Las fuentes vivas por repo mantienen la matriz `declarado|diferido|prerrequisito externo` y los gaps bloqueantes.

**Corrección de pin Agent Core — 03-10-2026:** el pin vigente pasa de `53e729d624c8284e906249df84c1a1df84cc8d40` a `86a767474042a566a0dbd6ed23588959f27ebdb3` (72 commits de diferencia) y `contracts/VERSION` pasa de `0.5.0` a `1.3.0`. §17 queda reescrita para reflejar los campos exactos verificados en ese SHA: el tipo de resultado de publicación es `Release` (no `ReleaseDecl`, que sigue existiendo pero sólo como insumo de autoría previo a `pin_release`), y aparecen familias de tipos nuevas upstream (`Transfer*`, `AwaitApproval*`, `StepUp*`, `MetricDef`/`MetricExpr`, `EncryptedBlob`, `Fingerprint`, `OutboxMessage`) que el spec previo no contemplaba. Ninguna de ellas cambia alcance: siguen siendo capacidades de plataforma que Pulso no construye ni emite en el primer corte, sujeto a verificación conforme avance la integración real. Esta revisión (V3) también fija una estrategia de integración en dos cortes obligatorios y secuenciales — mocks fieles al contrato HTTP primero, agent-core real levantado en local después — ver §27.6.

**Adición aditiva — 03-10-2026 (§32):** el equipo de producto publicó el modelo de datos de la plataforma real (Fase 1 de su plan). §32 define el perfil de fuente `platform_live`, el reparto Codex/Claude y las pruebas; no cambia el sentido de §§1–31.

**Autorización del usuario sobre E0/CSV — 04-10-2026 (aditiva, vigente sobre §28.6):** el usuario levantó la restricción de que `pulso_muestra_e0` y los CSV del banco no salgan del host local para (a) pruebas locales y (b) su traslado, cuando sea necesario, a nuestra propia infraestructura (cuenta AWS y bases compartidas propias). No autoriza por sí sola enviar contenido E0/CSV a proveedores de modelos alojados de terceros: eso sigue exigiendo datos tratados y una autorización explícita adicional. La semántica de egreso en `RunConfig` y los README del paquete deben reflejarlo (responsable: Codex en el motor; documentación del paquete: quien lo mantenga).

**Aclaración de alcance — 03-10-2026 (§§7/F8/25):** `debug-console` es el backoffice interno del motor Pulso para observar y operar de forma acotada su detección/automejora autónoma; no es sólo un panel de ingeniería ni el backoffice de atención de la plataforma. Su contrato privado `/internal/v1/debug` y comandos limitados pertenecen al motor (§25). Las superficies F7/F8 y `/api/v1/evolution` de la plataforma siguen fuera de alcance. Véanse CX-0116/0117 en la bitácora compartida.


**Decisiones provisionales de integración — 03-10-2026:** el dueño adoptó la opción recomendada de las 12 decisiones abiertas de §31 como decisión PROVISIONAL "hasta nuevo aviso"; todas se revisarán con el equipo de agent-core (detalle y revisores en `DECISIONES_ABIERTAS_V3_AGENT_CORE.md`).
- D-1: un único proceso Python `pulso-core-runtime` compone Core y monta `/internal/v1/*` (opción A).
- D-2: Pulso escribe las siete fábricas; dobles etiquetados en `doubles[]` (A).
- D-3: imagen propia del runtime; ADR 0003 corregido con el manifest (A).
- D-4: exporter Python propio con rol Postgres de sólo lectura (A).
- D-5: emisor de prueba local; IdP de la organización o paso fuera de banda en AWS (A).
- D-6: un compose con `postgres-core` PG16 propio (A).
- D-7: colas FIFO precalculadas en el gate nativo; banco stateful complementario (A).
- D-8: lectura de base y alias por el bridge, degradación a `ObservedAlias` (A).
- D-9: prefiltro Rust, dry-run en el bridge y `/validate` autoritativo (A).
- D-10: mundo `attention-demo` como `contract_fixture`, kinds K1.
- D-11: `real-wire` diario/manual/por PR relevante; bump en PR dedicado con revisor independiente (A).
- D-12: un principal por `(tenant, rol)` con `RateLimitConfig` explícita (A).

**Integración vigente con Agent Core:** contrato `1.3.0`, commit `894fa65575d83420523f33ec1c6919b8965f7ebe` (pin vigente en `main` de improvement-engine desde el PR #82, 03-10-2026; historial preservado: `86a767474042a566a0dbd6ed23588959f27ebdb3` fue el pin de este análisis original y `789d6c89b2fca90fc10e2abf157da51dc81c5d51` el intermedio; el bump a `c814c2bad9f154d10c092326558815dca9562be7` está en curso y no es pin hasta que se fusione). Las secciones 17, 24, 27 y 29 y el [expediente de contratos](AGENT_CORE_CONTRATOS_Y_ALINEACION.md) fijan formatos y capacidades verificadas (el expediente referenciado aún cita el pin previo y requiere su propia actualización, ver §30 backlog). `CapabilityBundle`, `ReleaseAck`, `ReleaseDetail`, `PlatformReleasePort`, `LayerAttempt` y `ScenarioCase` son modelos internos o extensiones de plataforma de Pulso, **no objetos ni endpoints de Agent Core**. `ReleaseDetail` es la vista Pulso sobre el `Release` publicado por el registry (§17) — envuelve sus refs con metadata propia (p.ej. `agent_id`), nunca un tipo wire alternativo a `Release`. El primer corte simula el registry disponible: autonomía hasta `evaluated`; aprobación, publicación y promoción requieren humano firmado. Shadow/canary, composición grupal task y publicación dinámica de conocimiento son capacidades pendientes, no condiciones que el mock pueda fingir satisfechas. Una simulación exploratoria de esas extensiones no acredita compatibilidad upstream.

Los ejemplos previos de permisos internos/grants no sustituyen roles del registry. Toda referencia a shadow/canary en diagnóstico/experiencia es diseño futuro no requisito del mock inicial; `shadow` de un detector analítico sí es validación interna de sensores, distinta del rollout de atención. Timestamps, secuencias, identificadores y Problem de Pulso no se agregan al body Core. La API de Pulso y la de Core pueden compartir nombres de rutas en hosts distintos; no son la misma superficie.

**Estado:** propuesta técnica para aprobación; no describe software ya implementado. **Actualizado:** 03-10-2026. **Sustituye a:** `TECH_SPEC_PULSO_AUTOMEJORA_V1.md` en decisiones de implementación. **Fuente inicial:** dataset sintético Factored entregado; sus tablas/CSV permanecen inalterados. **Decisión del equipo:** Rust, Git, Podman local, LocalStack para los servicios AWS efectivamente usados y Terraform para despliegue. Todos los límites, umbrales, presupuestos, cadencias y flags operativos son **configurables y versionados** (§6). Una cifra de ejemplo no es conocimiento bancario.

## 1. Norte del producto y criterio de éxito

**Producto de referencia:** experiencias complementarias de `design/`, catalogadas en [ANALISIS_PRODUCTO_DESIGN.md](ANALISIS_PRODUCTO_DESIGN.md). App/acceso/atención/supervisión/administración pertenecen a plataforma; el motor se integra en panorama, expedientes, propuestas, pruebas y decisiones mediante §§20.1/20.2/24.1/24.2. El catálogo visual «Agentes» representa capacidades heterogéneas Core. La auditoría por conjuntos de secciones y cuatro rondas de revisión queda trazada en ese análisis; los diseños ilustran requisitos, no autoridad ni resultados reales.

Este spec construye el **motor autónomo de detección y automejora**, no toda Pulso. La plataforma de atención es un sistema vecino: posee las cuatro capas, el runtime, los agentes que atienden, sus herramientas operativas y la experiencia del cliente. Nuestro motor consume datos bancarios y evidencia operacional de esa plataforma; detecta problemas, investiga, propone cambios de capacidades, los evalúa y solicita su liberación. También expone estado/evidencia para que la plataforma muestre qué está haciendo, con intervención humana excepcional. Durante la hackathon la plataforma vecina se representa mediante **contratos versionados y un simulador de integración con fallos realistas**, no se implementa F7/F8. El motor sí debe estar listo para sustituir ese simulador por una plataforma real sin cambiar su dominio.

**Caso de éxito principal:** sin codificar «quejas» como respuesta ni seleccionar manualmente el hallazgo, el motor detecta e investiga, identifica una ruta automatizable, produce `EntityDraft[]` compatibles, crea una propuesta `origin=auto_detect`, valida/congela y compara candidato/base con `EvalSuite` y gate de mejora Pulso. Itera autónomamente hasta `evaluated` o detención justificada; muestra aprobación requerida ligada a `candidate_hash`. Un humano firmado autoriza approve/publish; el mock confirma release y staging bajo protocolo upstream. Segunda corrida utiliza o contradice memoria. A acredita hallazgo no dirigido; B efecto sandbox sobre capacidad afectada, no causalidad sobre no resolución/SLA del CSV. Grado `same_outcome_linked|mechanism_proxy|unlinked|not_evaluable` permanece. Humano no dirige el hallazgo ni construye la propuesta.

```mermaid
flowchart LR
  D[Dataset original + histórico enriquecido E0 + eventos de plataforma] --> S[Sensores generales]
  S --> I[Investigación y falsificación]
  M[Memoria versionada] --> I
  I --> O[Oportunidad sustentada]
  O --> P[Alternativas y cambio de capacidad]
  P --> E[Escenarios, baseline y evaluación]
  E -->|gates pasan| H[Aprobación humana requerida por Core]
  H --> R[Publicar staging en registry simulado]
  E -->|falla o inconcluso| M
  R --> A[Contrato de plataforma / simulador]
  A --> T[Eventos, trazas y resultados por capa]
  T --> M
  T --> S
```

| Capacidad de producto | Contrato que existe desde el diseño | Primer corte ejecutable |
|---|---|---|
| Plataforma de atención — **externa** | `InteractionObservation`, `LayerAttempt`, `ToolReceipt`, `GoalOutcome`, `CapabilityBundle`, `ReleaseAck` | Simulador de contrato con árbol/IA1/IA2/humano, fallos y resultados reproducibles; no runtime ni UI de atención propios |
| Capacidades que el motor propone | `ChangeSpec` y bundle versionado, diff, compatibilidad, evaluación y release request | Generar y validar cambios; la plataforma/simulador posee activación y ejecución |
| Detección, investigación, portafolio | sensores configurables, SQL libre aislado, verificación, oportunidad y valor marginal | ≥2 familias de sensores con selección no hardcodeada |
| Automejora y memoria | propuestas, tests, simulación, release, experiencia acumulada y olvido | una propuesta vinculada, evaluación y una segunda corrida que aprovecha o invalida memoria |
| Visibilidad del motor | feed de actividad, expedientes, evaluaciones, memoria, decisiones excepcionales y estado de release | API/read models/SSE para la plataforma; además, consola técnica de desarrollo (§25), distinta de su UX |
| Operación futura | canary real, multi-tenant, políticas reales, fuentes continuas | contratos y estados; efectos externos reales deshabilitados sin Agent OS autorizado |

La presentación y video son entregables externos, **no** forman parte de este spec de ingeniería. El deployment de demo es una capacidad técnica, no un producto bancario live.

## 2. Auditoría de simplificación: qué se conserva y qué se elimina

La V1 mezclaba diseño de largo plazo con infraestructura de un primer corte. Estas son decisiones sustitutivas, no una lista de opciones para que cada desarrollador elija:

| Antes en V1 | Decisión V2 | Razón/condición para volver a separar |
|---|---|---|
| ~15 crates y servicios conceptuales por etapa | **Dos repos Git**: `improvement-engine` y `infra` | Servicio de automejora e infraestructura separados; Core/modelos externos, sin gateway propio |
| PostgreSQL + S3 + SQS, inbox/outbox/leases en todas partes | PostgreSQL para estado y **cola durable de jobs**; `LISTEN/NOTIFY` sólo despierta, polling recupera; S3 para blobs grandes/inmutables. Sin SQS inicial | Añadir broker cuando throughput/contención medidos superen criterios §8; no por previsión abstracta |
| Tabla/clase durable por cada Signal, Claim, Opportunity, Proposal, Scenario, Evaluation, Memory, Detector, etc. | **`artifacts` versionados** con `kind` tipado y JSON Schema por familia; sólo jobs, heads, lineage, auditoría, decisiones, cuotas, cursores de ingesta y comandos externos tienen tabla propia (§5) | Episodios/efectos de atención pertenecen a plataforma; extraer tabla concreta del motor sólo con consumer/medición |
| `DatasetRevision`/Parquet obligatorios de toda la fuente | CSV/tablas originales **readonly**; `SourceSnapshot` es manifest de paths, digests, schema y cutoff. Cache columnar derivado es opcional y reconstruible | Materializar Parquet por partición sólo si benchmark de lectura lo exige |
| Dos orquestadores/reconcilers y muchos puertos finos | Un worker con jobs tipados, Core externo y sandbox | No duplicar runtime, gateway ni atención |
| Multitud de clocks/epochs/campos repetidos en cada artefacto | Envelope común pequeño + campos propios sólo donde se consultan o hacen cumplir invariantes; `run_config_ref`, `source_snapshot_ref`, `parent_refs` | Añadir campo cuando haya query, gate o test que lo use |
| Canary de clientes reales como feature P0 | No se implementa en el corte compatible; extensión de plataforma futura | Registry promueve staging/prod completos; simulación de cohortes no acredita soporte Core |

Regla de diseño: ninguna columna durable entra sólo porque «podría ser útil». Cada campo tiene consumer (query, autorización, reconstrucción, visibilidad o prueba) y retención. Campos no usados se descartan; metadata aprobada puede quedar en blob versionado. No persistimos múltiples clocks/epochs por artefacto: envelope pequeño; fencing en jobs/comandos externos y control de permisos.

## 3. Datos: fuente intacta, relaciones explícitas y privacidad

Las 13 tablas entregadas (`customers`, `products`, `branches`, `service_agents`, `marketing_campaigns`, `daily_exchange_rates`, `transactions`, `call_center_interactions`, `call_transcripts`, `satisfaction_surveys`, `digital_events`, `complaints`, `campaign_sends`) son el **sistema fuente** de esta simulación de banco. `SourceStore` implementa `file://` local (`PULSO_DATA_ROOT`) y `s3://` AWS desde el **mismo manifest lógico**; ambos adapters sólo leen y verifican digest/versión de objeto, nunca ejecutan `ALTER`, `UPDATE`, `DELETE` ni escriben en la fuente. Nuevas tablas `pulso_*` son **del producto**, en PostgreSQL separado. Referencian la fuente con `SourceRef{source_namespace,world_ref,snapshot_ref,table,source_pk,file_digest,observed_cutoff}`; no se impone FK física hacia CSV/tablas ajenas. Ante corrección del CSV/partición se crea otro snapshot y se marca derivado stale; nunca se reescribe el original. `SourceSnapshot` guarda manifest y conteos, no copia el dataset completo a PostgreSQL.

**Bytes de `SourceSnapshot` (normativo).** Cuando el manifest se publica como artefacto U02 `source_snapshot`, su payload conserva el documento original UTF-8 en el único campo `source_snapshot_json`. Ese string —incluidos whitespace y orden de claves— es la entrada del `binding_digest` U04; está prohibido reconstruirlo desde `serde_json::Value` o aceptar alias de campo. U08/U20 resuelven exclusivamente ese campo y vuelven a parsearlo para validar tenant, tabla y binding. Un artefacto histórico sin string válido, con bytes que no reproduzcan el binding o con tenant divergente queda no elegible y falla cerrado; se publica una revisión nueva, nunca se muta el artefacto pasado.

DuckDB lee exclusivamente un **extracto tratado y sellado** por investigación. Un extractor confiable abre la fuente readonly, aplica proyección, pseudonimización, ventana, tenant y partición informacional, escribe derivados en un directorio por run sin acceso al root original y produce manifest con digest/filas/columnas. Sólo ese directorio se monta en `sql-sandbox`; ni CSV originales, ni socket Podman, ni credenciales, ni directorios de otros runs se montan allí. El agente razona y escribe SQL/tablas temporales dentro de la DuckDB efímera. El broker deniega IO externo, `ATTACH`, `COPY`, extensiones no permitidas y resultados individuales que violen el umbral de divulgación. Un cache Parquet **derivado** por columna/partición puede acelerar lecturas sin cambiar el esquema original: clave `(file_digest, transform_revision, allowed_columns, purpose, information_partition)`, inválida al cambiar cualquiera; sólo se materializa después de medir. PII directa no aparece en prompts/logs/trazas. Dado el permiso confirmado para enviar datos a modelos, el `ModelPort` envía el subconjunto mínimo tratado bajo configuración de tratamiento/retención y `ModelReceipt`; no una fila entera cuando bastan atributos. Se registran propósito/proveedor/versión; un cambio de permiso invalida nuevos usos.

| Relación | Confianza permitida | Prohibición concreta |
|---|---|---|
| `call_center_interactions.interaction_id ↔ call_transcripts.interaction_id` | join exacto, cobertura parcial | texto plantilla no es gold de motivo |
| `satisfaction_surveys.interaction_id ↔ call_center_interactions.interaction_id` | join exacto si poblado; CSAT/NPS sólo respondentes | no extrapolar encuestas a todos los contactos |
| `complaints.origin_interaction_id ↔ interaction_id` | schema admite, copia local auditada lo trae vacío | no inventar contacto causante por cercanía |
| `transactions.customer_id`, `digital_events.customer_id`, `call_center_interactions.customer_id` | secuencia/segmento agregado con `link_method=temporal_candidate` | proximidad no prueba causa ni error transaccional |
| `products.customer_id`, `customers.customer_id` | snapshot actual | no usar saldo/mora/status actuales como historia de 2023 |

Hallazgos de calidad previamente auditados deben **recontarse** al iniciar: transcripciones parciales, texto de `saldo` repetido incluso bajo `Queja`, motivos gruesos y descripciones PQR templáticas. Por tanto, los detectores sobre transcripciones originales usan estructura/fechas/estados; ese texto no produce prevalencia semántica ni oracle histórico. El texto enriquecido E0 sí permite investigación semántica y secuencial dentro de su población simulada (§28), sin extrapolar su prevalencia al banco. Los ejemplos PT son generados y revisados, no presentados como tráfico original. Para dinero, USD lleva fuente/conversión o es supuesto explícito.

`SourceContract` por tabla declara PK, tipos consumidos, tiempo de evento, nulabilidad observada y reglas de exclusión; la V1 §24.1 contiene la matriz inicial de siete fuentes, pero en V2 **los contratos JSON versionados en el repositorio son la autoridad ejecutable** (`contracts/sources/*.json` + golden CSV de header). Se eligió JSON para que el schema, el contenido hasheado y la referencia inmutable no tengan una representación YAML paralela; la decisión está en ADR 0002 del motor. El archivo físico manda sobre su header y toda diferencia produce quality finding. No se cambian columnas del dataset para acomodar el contrato: se cambia el adapter o se declara unsupported.

Las fuentes complementarias son **el histórico enriquecido E0** (§28) y **la observabilidad operacional de plataforma**, no columnas inventadas del CSV. `PlatformObservationBatch` y spans/logs tratados (§24) informan qué pasó en clasificador, árbol, IA1, IA2 y humano. Sus `SourceContract` propios declaran secuencia, correlación, clocks, versión, cobertura y política de sampling. El simulador genera esta fuente en local; producción la recibiría de la plataforma real. Nunca se mezclan tasas del histórico sintético con tasas observadas del simulador sin distinguir población, periodo y `evidence_kind`.

El histórico enriquecido `pulso_muestra_e0` es una fuente de primera clase: se asume realidad operacional del entorno de evaluación, sin negar su procedencia aumentada. Complementa los datos bancarios y la futura telemetría; no reemplaza ninguna fuente ni necesita un motor distinto. §28 fija ingesta, descubrimiento, evaluación y aprendizaje continuo para esa fuente.

## 4. Código, Git y límites de proceso

**Decisión de ejecución sustitutiva (§29):** Rust conserva el control plane, procesamiento de datos, sandbox, gates y persistencia Pulso. El razonamiento autónomo y los juicios Jev se describen y ejecutan mediante Agent/Flow/nodos agent y decide de Agent Core, en su runtime Python separado. No construir un segundo ReAct ni otro cliente Jev Rust. agent-core-assets/ almacena definiciones versionadas, prompts y suites del propio sistema de automejora; Core es dependencia fijada, no código copiado dentro de crates/app.

Se usan **dos repositorios Git**: `improvement-engine` para dominio, API, worker, contratos, integración Core, fixtures, stack local y CI de integración; `infra` para Terraform, entornos AWS, despliegue, IAM y observabilidad de infraestructura. Agent Core y modelos son externos. `pulso-core-runtime` es el proceso Python único que compone Core y expone `/internal/v1` (nombre canónico del proceso, de la imagen y del servicio compose/ECS; su código vive en el directorio `core-bridge/`; §31.5.0); no construimos gateway. El simulador es dependencia de tests/demo, no atención bancaria.

```text
improvement-engine/
  crates/core/            # entidades, estados y validaciones puras
  crates/app/             # coordinación durable, métricas, gates, eval y memoria; razonamiento en Core
  crates/adapters/        # PG, S3, DuckDB, plataforma, cliente Core y capacidades del lab
  crates/control-api/     # comandos/read models/SSE del motor
  core-bridge/            # `pulso-core-runtime` (composición de Core, fábricas, `/internal/v1/*`), `pulso-core-exporter` y `pulso-bootstrap`
  agent-core-assets/      # Agents/Flows/prompts/decisiones/suites de evolución
  debug-console/          # UI interna de desarrollo; consume sólo control-api
  crates/worker/          # scheduler, jobs y reconciliación
  # Sin crate/servicio gateway: integración de modelos mediante Core externo
  crates/platform-sim/    # sólo test/demo: cuatro capas y banco sandbox simulado
  contracts/              # OpenAPI, schemas, fuentes y eventos de plataforma
  migrations/             # sólo tablas nuevas pulso_*
  local/                  # Podman Compose, PG, LocalStack y perfiles aislados por test/worktree
  tests/ fixtures/ docs/architecture/ docs/flows/ docs/decisions/ docs/runbooks/ docs/journal/
  .github/workflows/      # CI del motor, incl. PG efímero y contratos de integración
infra/
  terraform/modules/      # red, datos, compute, seguridad, identidad, storage, secrets, observabilidad
  terraform/envs/         # staging y prod; prod es la demo
  docs/architecture/ docs/runbooks/ docs/decisions/ docs/journal/
  .github/workflows/      # CI actual fmt/validate/contratos; plan/deploy futuros y deshabilitados
```

Cada repo excluye CSV/Parquet, PII, secretos, state Terraform, outputs y grabaciones. `main` protegido, PR con contrato/test/ADR y lockfiles; imágenes por digest. La futura entrega U25 podrá hacer que infra consuma un manifest firmado de digests/schema/migración/config del engine; la fundación Terraform ya declara recursos AWS, pero no consume aún dicho contrato ni acredita plan/apply. Un release futuro pinneará ambos commits, imágenes, migración y `RunConfigRevision`; rollback volverá a imágenes/capacidades anteriores sin borrar hechos. **Documentación técnica y bitácora son entregables de cada corte, no actividad opcional al final** (§26). Los repos ya están inicializados: el estado de implementación se acredita por commit, test y CI, no por este documento.

### 4.1 Frontera y baseline Terraform de infraestructura

El estado objetivo de `infra` no contiene Compose, LocalStack, doctor de Podman, fixtures ni tests de integración del motor: son dependencias locales de `improvement-engine`. La limpieza sólo se considera cerrada cuando el motor aporta su reemplazo versionado y smoke verificable; PostgreSQL efímero de CI no prueba ese stack local. Su único producto es infraestructura AWS versionada y sus runbooks. Sólo existen dos entornos: `staging` y `prod`; **prod es la demo**, no tráfico bancario real. Ningún pipeline aplica, publica imágenes ni hace `terraform apply` automáticamente en este corte. CI valida formato, módulos, contratos de variables y plan sólo cuando una identidad OIDC y backend ya autorizados lo hagan posible.

El baseline se implementa como módulos Terraform con entradas mínimas y outputs no sensibles, no como un monolito por ambiente:

| Módulo | Responsabilidad y límite verificable |
|---|---|
| `bootstrap` | **Prerrequisito externo**: bucket de state cifrado/versionado, locking y trust role GitHub OIDC restringido por organización/repos/branch; no se crea recursivamente desde los roots del servicio ni es dependencia de `fmt`/`validate` |
| `network` | VPC, dos AZ, subnets públicas/privadas y rutas; NAT por entorno como decisión de coste/versionada; no abre una ruta de administración pública |
| `connectivity` | **Diferido**: no existe módulo VPN/TGW mientras no haya customer gateway, CIDRs y aprobación; no se crea una VPN ficticia |
| `edge` | **`dependency_blocked`**: la ruta elegida será `acceso privado → proxy de identidad → ALB interno → task`; no hay API Gateway placeholder, ALB público ni regla inbound directa hasta contrato de listener/auth/health y prueba de integración |
| `identity` | roles separados de CI deploy, runtime, task sandbox y lectura de observabilidad; trust y recursos permitidos mínimos; nunca secretos persistentes de GitHub |
| `runtime` | ECS/Fargate privado declarado para el motor; imágenes por digest; el servicio del motor no incluye Agent Core ni gateway propios. El workload Agent Core (`pulso-core-runtime`) es otro servicio ECS, con imagen, base y rol propios, según el ADR 0003 de `infra` (§31.11.5). Conectividad a DB, health del servicio, inyección de secreto y escalado de jobs siguen contrato de integración, no se infieren del recurso |
| `data` | PostgreSQL administrado, S3 de artefactos/extractos/mailbox, cifrado, backup/retención y separación por entorno; nunca una copia no tratada del dataset en el state ni outputs |
| `secrets` | nombres/referencias y políticas de lectura de Secrets Manager/KMS; valores los aporta un canal autorizado y no Terraform ni CI |
| `observability` | log group, SNS y alarmas CPU diagnósticas declaradas; logs/métricas/trazas del motor y alarmas accionables de disponibilidad, error, cola, progreso, presupuesto e ingesta requieren contrato engine→infra, owner, destino y prueba firing/resolved |

La red, roles y stores se validan por contrato y por `terraform validate`/plan cuando haya credenciales autorizadas; LocalStack no acredita IAM, VPN, VPC, OIDC ni alarmas AWS. Las alarmas se distinguen de telemetría de negocio: OTel/`pulso_run_events` alimentan la detección, mientras CloudWatch confirma salud del despliegue. El runtime usa `database_connection_secret_arn` versionado por entorno (secreto RDS-managed o application secret autorizado, con host/port/dbname/username/password); Terraform no aporta valores, el task recibe sólo ref, IAM lee exactamente ese ARN vía Secrets Manager/KMS y un smoke tratado verifica binding endpoint/secreto/rotación. Egress es `aws_private_endpoints_only` o `controlled_nat` explícito: una regla TCP/443 amplia es plumbing temporal, no prueba de que sólo llega a AWS. Los security groups se permiten por flujo explícito (`proxy→ALB interno→runtime`, `runtime→data`, `runtime→AWS APIs/proveedor por perfil aprobado`); queda prohibido `0.0.0.0/0` entrante a runtime/data. La documentación del módulo enumera dependencia, threat model breve, variables, salidas, test y rollback por cada recurso.

## 5. Modelo persistente mínimo: diez tablas nuevas del motor

PostgreSQL almacena el **control plane y observaciones normalizadas del motor**, no episodios/efectos operativos de atención ni un espejo del dataset. Todas las tablas nuevas llevan prefijo `pulso_` y `tenant_id` aunque la demo tenga un tenant. `artifact_id` identifica algo lógico, `revision` una versión inmutable. Contenido JSON se valida con schema por `kind/schema_version` **antes** de persistir; columnas de búsqueda se derivan del mismo JSON dentro de la transacción. Blob S3 se usa sólo si el cuerpo supera límite configurable o contiene material que requiere política de retención aparte. Una relación durable se usa porque alguien navega, invalida o autoriza por ella; no por decoratividad del ERD.

| Tabla | Columnas/índices que sí tienen consumidor | Por qué no basta un blob |
|---|---|---|
| `pulso_jobs` | `id,tenant_id,run_ref,kind,logical_key,generation,parent_job_id,status,lane,priority,due_at,attempt,lease_owner,lease_until,lease_version,last_event_sequence?,input_ref,config_ref,reserved_cost_usd,actual_cost_usd,error_code`; UNIQUE `(tenant_id,kind,logical_key,generation)`, índice parcial de pendientes | agenda, concurrencia, retry y backpressure; `run_ref` permite ver el árbol de trabajos sin inferirlo de logs; sólo el job raíz mantiene `last_event_sequence` |
| `pulso_artifacts` | `(tenant_id,id,revision)` PK; `kind,schema_version,body_json_or_blob_ref,digest,created_at,source_snapshot_ref,config_ref,information_partition,search_text` | revisiones consultables y memoria FTS; `kind` se valida con schema |
| `pulso_artifact_heads` | `(tenant_id,scope_key)`, `artifact_id,revision,head_version`; CAS; scopes `run_config/<environment>`, `bundle_candidate/<route>/<environment>`, `memory_index/<scope>` | publicación/versiones del motor; head activo de atención es externo |
| `pulso_artifact_edges` | `tenant_id,from_id,from_rev,to_kind,to_ref,to_rev?,relation`; `to_kind=artifact\|source_row\|source_snapshot\|policy`; índice en origen y destino tipado | lineage, invalidez transitiva y refs a CSV sin FK física; ambos extremos se validan en mismo tenant |
| `pulso_decisions` | `id,tenant_id,artifact_ref,actor_ref,grant_ref,status,expires_at,expected_head,response_ref` | autoridad humana mínima y expiración |
| `pulso_audit_events` | `id,tenant_id,actor_ref,action,target_ref,result,at,trace_id` con payload tratado | registro de permiso, rechazo y publicación |
| `pulso_run_events` | `id,tenant_id,run_ref,job_ref?,sequence,event_at,stage,event_code,status,reason_code?,artifact_ref?,trace_id?,details_ref?`; UNIQUE `(tenant_id,run_ref,sequence)`, índice `(tenant_id,run_ref,sequence DESC)` | cronología durable de transiciones y decisiones que la consola técnica puede reconstruir aunque OTel esté caído; detalle voluminoso vive en trazas/blobs tratados |
| `pulso_quotas` | PK `(tenant_id,resource,window_start)`; `config_ref,limit_units,reserved_units,actual_units,window_end,version` | contador global estable entre revisiones; config_ref documenta política, no abre otra bolsa; reserva atómica worker/Core |
| `pulso_ingest_cursors` | PK `(tenant_id,source,partition)`; `offset_or_watermark,source_digest,updated_at,last_batch_ref` | reanudar eventos/trazas de plataforma sin duplicar ni perder lote |
| `pulso_external_commands` | `tenant_id,command_key,target,request_digest,status,receipt_ref,attempt,created_at,reconcile_after`; UNIQUE `(tenant_id,target,command_key)` | release/rollback hacia plataforma con confirmación, unknown y reconciliación |

No hay tablas iniciales separadas para `Signal`, `Claim`, `Opportunity`, `Proposal`, `Scenario`, `Evaluation`, `Memory`, `Detector`, `Portfolio`, `Bundle`, `RunConfig` ni `SourceSnapshot`: son `pulso_artifacts.kind` con schemas distintos. `pulso_artifact_heads` lleva config, wiki activa y bundle **propuesto**; la plataforma posee el head del bundle **activo en atención**. No hay episodios ni tool effects propios: llegan como observaciones desde la plataforma y se guardan en blobs/artefactos tratados con lineage. Job, artefacto y evento de transición se crean/actualizan **en la misma transacción PG**; `NOTIFY` es hint no durable y polling recupera. `pulso_run_events` no registra tokens ni cada lectura de archivo: es el ledger pequeño de cambios de estado, decisiones, checkpoints, fallos y esperas; OTel/blobs aportan detalle con retención distinta. S3 puede quedar con blob huérfano si cae antes de commit; GC por digest/edad lo elimina tras retención. Los comandos de release/rollback externos usan `pulso_external_commands`; si el receptor exige broker/outbox, se añade por ADR y test de fallo.

**Contrato relacional de implementación.** IDs internos son UUIDv7 sin PII. Excepto pulso_artifacts, cuya PK es `(tenant_id,id,revision)`, tablas con id tienen PK `(tenant_id,id)`; jobs parent_job_id/run_ref apuntan a jobs del mismo tenant (raíz se referencia a sí misma). Referencias internas a revisiones usan objeto `ArtifactRef{tenant_id,id,revision}` y FK compuesta cuando existe columna relacional; no confundirlas con VersionRef Core ni SourceRef. Heads y extremos artifact de edges deben resolver una revisión existente del mismo tenant. Edges hacia fuentes sólo validan el manifest/namespace, no crean FK sobre CSV. Borrado no hace cascade de evidencia: retención/purga pasa por tombstones y auditoría. NOT NULL/CHECK cubren revision>=1, head_version>=1, attempt/generation>=0, unidades no negativas y status por reducer; campo nullable debe tener motivo documentado, no default silencioso. Errores de validación no consumen una revisión publicada.

External_commands añade `run_ref,job_ref,request_ref,version,updated_at`: request_ref apunta al payload tratado inmutable usado para reconciliar; receipt no sustituye el request perdido. Binding CoreRun se persiste como receipt enlazado al comando con CAS de version y digest. Índices `(tenant_id,status,reconcile_after)` y `(tenant_id,run_ref)` tienen consumidor en reconciler/consola. UNIQUE de key y payload distinto retorna conflicto; no sustituye exclusión de un proveedor que no admite idempotencia. El ERD siguiente muestra navegación lógica, no garantiza FK directa job→artifact: esa navegación usa run_events/edges y los refs anteriores.

**Inmutabilidad, hashes e invalidación.** Payloads JSON internos se canonicalizan mediante RFC8785/JCS; cantidades decimales/USD se representan como strings de precisión declarada, timestamps UTC RFC3339. Digest interno es SHA256 de bytes canonicalizados; blobs binarios se hashean sobre bytes exactos. Este algoritmo no sustituye canonical_bytes/hashes propios de Core. Cambiar schema/config crea revisión nueva. Estado revoked/stale se aplica como overlay de tombstone/permiso antes de servir una revisión, no editando su JSON histórico; índices y caches consultan también ese overlay. Mismo digest nunca concede acceso entre tenants/particiones. Tests: round-trip Rust/Python con golden bytes, FK cross-tenant, head a revisión inexistente, request conflictivo, restore con tombstone y ausencia de cascade destructivo.

**Cuotas al cambiar configuración.** config_ref documenta el cálculo, pero no abre presupuesto nuevo dentro de la misma ventana. Al activar otra config, se arrastra consumo/reserva acumulado por tenant/resource/window y se aplica el límite nuevo; bajar el límite por debajo del consumo difiere trabajo adicional sin saldo negativo. El cambio de config y reserva usa el mismo lock de recurso que claim; tests de dos revisions concurrentes prueban que no se duplica cupo. Una nueva ventana sólo reinicia presupuesto por política de calendario, no por nuevo config_ref.

Run_events tiene FK `(tenant_id,run_ref)` y `(tenant_id,job_ref)` hacia jobs; valida además root.run_ref=root.id y job.run_ref=event.run_ref mediante constraint trigger transaccional. FK a cualquier job no demuestra pertenencia al run. Tests rechazan hijo usado como raíz y evento asociado a job de otro run. Crear raíz con self-reference ocurre en una transacción con FK diferible; hijos sólo después de raíz válida.

```mermaid
erDiagram
  pulso_jobs ||--o{ pulso_artifacts : produces
  pulso_artifacts ||--o{ pulso_artifact_edges : relates
  pulso_artifacts ||--o{ pulso_artifact_heads : publishes
  pulso_artifacts ||--o{ pulso_decisions : may_require
  pulso_artifacts ||--o{ pulso_external_commands : requests_release
  pulso_ingest_cursors ||--o{ pulso_artifacts : ingests_observations
```

**Familias de artefactos y campos propios obligatorios:**

| `kind` | Campos propios mínimos | Lectura/acción que los necesita |
|---|---|---|
| `signal` | metric_ref, population_ref, numerator, denominator, comparator, interval, source_refs, query_receipts | priorizar y falsificar |
| `opportunity` | claim, support_refs, counter_refs, population, status, value_range_ref, workflow_link_ref | expediente y selección |
| `proposal` | opportunity_ref, alternatives[], selected_change_ref?, expected_mechanism, affected_routes[] | comparar, construir y revisar |
| `capability_bundle` | Schema canónico por estado en §17; no redefinir campos aquí | Envoltorio Pulso, nunca entidad Core |
| `scenario_set`/`evaluation` | cases_ref, split, oracle_ref, baseline_ref, candidate_ref, results_ref, limits | prueba y gate |
| `memory_wiki` | scope, purpose, base_head_ref, snapshot_blob_ref, index_digest, source_manifest_ref, diff_digest, lint_receipt_ref, tombstone_refs | montar, publicar, navegar, revisar y olvidar wiki sin esquema rígido por claim |
| `detector` | metric_spec, source_contract_refs, status, shadow_results_ref | ampliar sensores sin autorrefuerzo |
| `run_config` | detector/settings refs, budgets, concurrency, cadence, thresholds, model refs, feature_flags | repetibilidad y control |
| `source_snapshot` | ordered file refs/digests, source schemas, observed_cutoff, quality_ref | seleccionar fuente original reproducible sin copiarla |
| `platform_observation` | source_id, sequence_range, batch_digest, coverage, event_blob_ref, contract_ref, trace_refs | detección por capa, replay y cursor durables sin duplicar episodios operativos |
| `model_receipt` | invocation_ref, model_profile_ref, provider_route, output_digest, usage/cost, validation, status | auditoría y presupuesto de Jev/LLM reales sin guardar prompts sensibles en logs |

Los blobs y eventos tienen `retention_class`; invalidación de fuente o permiso marca derivados `stale/revoked`, bloquea retrieval y promoción inmediatamente y encola purga física según política. No se promete inmutabilidad eterna de PII. Un `artifact_edge` a una fuente es referencia lógica `SourceRef`, no FK a CSV. Índices FTS sólo de texto tratado y reconstruibles. `JSONB` no es permiso para almacenar campos arbitrarios sin schema: unknown field relevante a decisión falla validación, migraciones/upcasters se prueban N/N−1.

## 6. Contratos y configuración que hacen reproducible el sistema

**Envelope wire v2:** `{schema_version,tenant_id,artifact_or_event_id,correlation_id,created_at,source_snapshot_ref?,config_ref?,evidence_kind,body}`. UUIDv7 para IDs nuevos; UTC RFC3339 para tiempos; dinero decimal string + `currency`; enums `snake_case`; `unknown` es valor explícito. `evidence_kind=supplied_synthetic|team_generated|external_assumption|future_bank`; `validation=unverified|reproducible|offline_evaluated|live_observed` y `environment=none|sandbox|live` son ejes independientes. No se agregan todos los clocks a todas las entidades: fuente tiene event/observed time, atención tiene at, policy tiene vigencia, job usa reloj real para lease. SQL y modelo reciben refs y presupuestos; payload sensible no viaja en eventos genéricos.

`RunConfigRevision` es artefacto inmutable y **único dueño de settings del motor**: detectores, ventanas/splits, quality gates, límites SQL, concurrencia, cadencias, modelos/Jev/temperatura/prompts, presupuestos, evaluación, retención, reglas de release sandbox y flags. Cada campo tiene tipo/rango/default/owner/efecto en `contracts/run_config.schema.json`; no hay const/env oculto que cambie semántica. Secretos son refs a secret store, nunca valor en config. Activación por CAS; cada run fija `config_ref`. Cambio crea nuevo run o cancelación explícita, no muta trabajo in-flight. API muestra diff/autor/versión; rollback mueve head. La plataforma tiene configuración de atención propia, fuera de este RunConfig.

| Comando/puerto | Entrada y salida mínima | Condición de fallo |
|---|---|---|
| `schedule_run` | `{mission_ref,source_snapshot_ref,config_ref,trigger_ref,idempotency_key}` → job ref | source/config faltante o permiso denegado |
| `analyze` | manifest de vistas tratadas + SQL/budget → `QueryReceipt{digest,rows,bytes,duration,truncated}` | límite/escape/PII → rechazo y traza |
| `publish_artifact` | kind, schema_version, body, expected_head, source/config refs → revision | CAS stale o schema inválido |
| `prepare_bundle` | base_ref, ChangeSpec, policy_ref → bundle revision o errores tipados | ruta/tool/skill inexistente, ciclo, permiso |
| `invoke_model` | perfil/model ref, purpose, treated input/state, schema/pregunta tipada, budget, idempotency key → `ModelReceipt` | proveedor no permitido, PII/retención, timeout/costo/schema → fallo tipado |
| `observe_platform` | PlatformObservationBatch tipado (§24.2) + cursor/manifest → reducer → InteractionObservation artifact | gap de secuencia/coverage, versión de contrato o tenant inválido |
| `execute_scenario` | scenario, fixture, bundle_ref, seed → traza/resultado del simulador de plataforma | fixture/oracle ausente → `not_evaluable` |
| `registry_proposal` / `publish` | `EntityDraft[]`, expected_rev, candidate_hash, suite_id/version; publish con Idempotency-Key → `ReleaseDetail` | contrato Core §§17/27; approval/publish/promote/revoke requieren humano firmado; ReleaseAck sólo extensión futura |
| `mount_memory` / `publish_memory` | scope/purpose/cutoff/partition → wiki workspace; luego base head+diff → revision | stale/revoked/final holdout nunca se monta ni publica |

`PolicyPort` del simulador valida identidad, propiedad de recurso, operación, scope y versión de política para escenarios; en producción esa validación pertenece a plataforma/Agent OS. Agentes del **motor** proponen cambios/release, pero un receptor confirma cada efecto externo. Lectura de SQL/wiki es libre dentro del perímetro montado, sin otro tenant ni final sellado; mutaciones de plataforma pasan por comando tipado, autorización y `pulso_external_commands`. No implementamos policies bancarias reales ni asumimos autoridad por prompt.

**Contrato de enlace más importante:** `WorkflowBridge`/`OpportunityToScenarioLink` exige `{opportunity_ref,target_outcome,source_population,workflow_ref,eligible_fraction_range,scenario_refs[],change_route_ref,link_grade,blocking_reasons[]}`. `same_outcome_linked` exige el mismo outcome/población y mecanismo capaz de alterarlo; `mechanism_proxy` sólo autoriza afirmar que un mecanismo relevante funcionó en sandbox; `unlinked/not_evaluable` impide claim de mejora. La validación exacta está en §16. Una señal gruesa `Queja` no se transforma mágicamente en submotivo de saldo. Un caso PQR con `complaint_id`/categoría/fecha vinculables puede proponer subruta de seguimiento/triage, pero su evaluación sandbox **no** demuestra reducción real de incumplimientos SLA. Tests positivos y negativos comprueban cada grado.

## 7. Flujos completos y comportamiento esperado

### F1. Fuente/atención → trigger sin intervención humana

`worker` despierta por (a) nuevo `SourceSnapshot` o corrección, (b) agenda de `RunConfigRevision`, (c) umbral de eventos/trazas **emitidos por la plataforma externa** —handoffs, intentos fallidos por capa, herramientas unknown, latencia, regresión—, (d) solicitud humana explícita. Un coalescer agrupa señales del mismo ámbito/ventana y crea un `pulso_jobs(kind=detect)` idempotente. No crea una investigación por cada fila o span. `pulso_ingest_cursors` conserva offset/watermark hasta que el lote tratado y su manifest queden durables; pérdida de NOTIFY/OTel no equivale a pérdida de evento de plataforma. El scan del CSV mira los 13 schemas y calidad, pero sólo abre vistas requeridas. Un archivo nuevo no corrige el viejo sin `supersedes`. **Aceptación:** dos triggers simultáneos producen un run lógico; evento atrasado se reprocesa sin duplicar hallazgo; caída de telemetría se muestra como cobertura desconocida, no como cero fallos.

### F2. Detectar → investigar → corroborar/refutar

Sensores deterministas calculan `MetricSpec` con grano, población, numerador, denominador, ventanas, baseline, calidad y costo; cubren **todas las familias**: atención/contactos, PQR/SLA, transacciones/rechazos, fricción digital, productos/activación, marketing, cartera descriptiva y salud del motor. No se ejecutan todas las métricas cada minuto: `RunConfig` define prioridad/cadencia y `SourceContract` qué fuente habilita cada una. Un scout LLM puede explorar **SQL libre** sobre DuckDB efímera tratada y proponer nuevas métricas/detectores; no promueve un detector por haber encontrado una correlación.

`Verifier` independiente aplica checks configurados: schema y cobertura, denominador, temporalidad, mezcla/canal/país cuando válido, duplicados, multiple testing, sensibilidad de ventana y contraejemplos. Jev se usa para preguntas estrechas tipadas; LLM para hipótesis alternativas y explicación, nunca para sustituir el cálculo. Publica `signal` y `opportunity` con soporte, contradicción y status `candidate|candidate_descriptive|corroborated|corroborated_descriptive|uncertain|refuted`; los estados descriptivos son los resultados normativos de los perfiles §14 y conservan fuerza de evidencia explícita. Si falta evidencia, publica hallazgo negativo/unknown y agenda reintento sólo ante fuente/config nueva. `detector` aprendido pasa `candidate→shadow` sobre ventanas independientes → `active` tras verificación; señales propias no corroboran su hipótesis originaria. **Aceptación:** el mismo código/config encuentra o refuta la anomalía al permutar evidencia sin renombrar `Queja`; no convierte la categoría gruesa en causa; registra todas las celdas exploradas. La partición temporal y gates estadísticos del contrato inicial se materializan en `contracts/discovery_v1.yaml` antes del primer run (V2 §14 fija los perfiles propuestos; no se eligen post hoc).

### F3. Oportunidad → portafolio → propuesta concreta

`worker` monta la wiki autorizada para que el agente navegue libremente y mapea población/objetivo a capacidades **publicadas por la plataforma**. Genera alternativas: no cambiar, árbol, contexto/skill/tool soportados por el catálogo, IA1 Jev, IA2 LLM, routing/handoff o dependencia externa. `PortfolioDecision` resta solapamiento de población/costo. `proposal` incluye `do_nothing`, mecanismo, población elegible, ruta, precondiciones, costo/esfuerzo/riesgo y supuestos. `ChangeSpec` propone modificación versionada; `prepare_bundle` valida refs y compatibilidad, no construye runtime. LLM puede explorar/diseñar/iterar, pero no activa su JSON directamente. **Aceptación:** alternativas trazables; si no hay ruta/llave/oracle, `unlinked`; dos builders mismo head no se pisan.

### F4. Escenarios y evaluación realista

`ScenarioFactory` toma episodios/atributos del dataset sólo cuando son vinculables y temporalmente válidos, histórico enriquecido E0 bajo el protocolo §28, observaciones de la plataforma externa, variantes sandbox y agentes adversariales que interactúan por el **contrato público de plataforma/simulador**, no por un runtime nuestro. El simulador reproduce las cuatro capas, un banco con estado/policy, efectos y fallos inyectables; sus fixtures generados se marcan `team_generated` y no se atribuyen al CSV. `OracleSpec` compara objetivo, acción permitida/prohibida, estado final y handoff; `was_resolved` histórico es señal operacional débil, no veredicto del candidato. Baseline y candidato usan mismo caso, semilla, versión del simulador y límites, con DB/namespace reseteado entre brazos. Casos finales se separan por cliente/episodio/plantilla y tiempo, nunca alimentan builder/memoria de desarrollo.

La pieza evaluada P0 es **el cambio que el motor descubra y proponga**, sea Flow, DecisionModelDef, Prompt o configuración de Agent nativamente soportados; skills se compilan a entidades existentes, conocimiento nuevo/runtime queda dependency_blocked; no se fija el clasificador como ganador. Jev se usa por el motor para juicios tipados cuando aporte, y el simulador puede emular la clasificación de plataforma. `EvaluationPlan` sella métrica primaria ligada al `WorkflowBridge`, tamaño, split, presupuesto y gate antes de correr: seguridad, cobertura, handoff/resolución verificable según objetivo, p50/p95 latencia, costo por caso e intervalos. Un fallo de tool/banco/oracle es `unknown/not_evaluable`, no éxito ni culpa automática del candidato. Iteración produce revisión nueva y reevalúa en desarrollo; final se abre una vez **por familia/campaña de propuesta** y luego se retira, sin feedback granular al builder (§18). **Aceptación:** baseline/candidato comparables; seguridad no se compensa con costo; casos normal/ambiguo/humano ES/PT de contrato; fallo adversarial produce regression case sólo si procede de split de desarrollo/validación; si no mejora se conserva release anterior y la memoria registra hipótesis fallida sin contaminar final.

### F5. Release y aprendizaje posterior

El motor lleva la propuesta Core a `evaluated` automáticamente, conserva su hash y solicita decisión humana (§27). `approve` y `publish` usan credencial humana firmada; publish confirma staging, no exposición a clientes. `promote(prod)` es cambio completo de alias, no canary. `pulso_external_commands` conserva ledger local y respuestas; no agrega idempotencia al API upstream. Unsafe/regresión bloquea la solicitud de publicación y conserva la versión anterior. Rollback actual requiere humano y promoción de release anterior activa; no revocar mientras prod la use. **Aceptación:** sin humano no publicación; timeout no implica éxito; staging cambiado exige rebase/reevaluación/aprobación nueva. Shadow/canary se reserva para extensión de plataforma futura, no se implementa para fingir compatibilidad.

### F6. Memoria: persistir, usar y olvidar

La memoria es una **wiki de trabajo mantenida por agentes**, no un packet top-k de claims preseleccionados. Cada investigación recibe un workspace efímero con fuentes autorizadas readonly, índice, páginas temáticas y log; el agente puede navegar, buscar, cruzar y reescribir libremente páginas/síntesis dentro de su workspace. Esas ediciones no son durables hasta `publish_memory`, que verifica procedencia, ausencia de PII/holdout, contradicciones, policy y diffs; luego crea snapshot inmutable y mueve el head por CAS. La wiki activa crece y se reorganiza en nuevas revisiones; el agente puede crear páginas, enlaces, hipótesis, métodos útiles y notas de fallos sin un schema rígido por oración. `MemoryUseReceipt` registra páginas leídas/ediciones influyentes, no pretende demostrar causalidad del modelo. Olvido = dejar de servir contenido revocado/stale, consolidar/sustituir páginas obsoletas y purgar cuando la retención lo exige; un hecho durable no decae sólo por no haber sido leído. §21 fija el protocolo completo.

### F7. Plataforma de atención: contrato externo, no implementación

La plataforma posee clasificación, flows, ejecución de agentes, humano, estado del cliente, efectos y episodios. Jev es proveedor tipado de DecisionModelDef, no tipo de Agent. Nuestro motor **no** implementa esas capas: genera artefactos nativos y usa un adaptador de registry simulado conforme §§17/27. Ingiere EngineEvent mediante exportador acordado (§24), sin inventar un feed HTTP Core. Episodio/capa/humano son enriquecimientos externos con cobertura explícita. **Aceptación:** mocks reproducen cuerpos/estados/errores disponibles, capacidades faltantes unsupported; no se exige construir atención. Sustituir mock por Core requiere pruebas de transporte/composición además de schemas, no se promete enchufe sin verificación.

### F8. Experiencia de la plataforma: fuera del motor, visibilidad obligatoria

La consola integral de atención, oficina de agentes, árbol visual y experiencia de cliente son responsabilidad de la plataforma. Nuestro motor expone **read models y un feed de actividad** con estado actual, siguiente acción automática, evidencia, grado de enlace, cambios, tests, decisión requerida y resultados; la plataforma puede renderizarlos. La consola de §25 sí es el **backoffice interno de operación y debugging del motor de automejora**: permite ver de forma integral qué ejecuta el sistema, qué encontró, por qué decidió, en qué estado están sus jobs/propuestas/evaluaciones y qué dependencias fallaron; puede ofrecer los comandos operativos acotados ya definidos en §25. No es el backoffice de atención del banco, no es una API de producto para clientes ni sustituye las experiencias de la plataforma. El humano de producto responde a `DecisionRequest` excepcionales; esas decisiones no se convierten en control manual paso a paso del motor. **Aceptación:** corrida automática visible de principio a fin, incluso estados negativos/unknown y esperas; ausencia de UI no bloquea jobs; respuesta humana expirada no habilita release. F7/F8 de la plataforma siguen fuera del motor; la consola interna de §25 sí es parte del producto Pulso y puede usar fixtures/stand-ins claramente etiquetados cuando falte una integración real.

## 8. Rendimiento, throughput, concurrencia y asincronismo

La atención interactiva pertenece a la plataforma; nuestro motor sólo tiene latencia de ingesta, API de visibilidad, integración externa de modelos y jobs asíncronos. Detección, investigación, evaluación y memoria pueden tardar minutos sin detener atención. `control-api` confirma comandos durables con job ID; SSE entrega progreso y polling recupera pérdidas. El simulador de plataforma no comparte pool de CPU/PG con scans del motor.

| Presupuesto inicial propuesto, en `RunConfigRevision` | Objetivo de ingeniería, no medición actual | Degradación segura |
|---|---|---|
| Integración externa de modelos p95 por perfil | límite versionado por Jev/LLM/proveedor, medido separadamente del tiempo de job | timeout/circuit open → job `waiting_dependency` o alternativa permitida; no juicio inventado |
| API read model p95 | ≤500 ms para página ≤100 con índices/proyección | mostrar estado parcial y cursor, no traer grafo entero |
| Detección de nuevo snapshot/evento | disparar job ≤5 min; completar depende de bytes/costo | estado `queued/deferred` visible, nunca pérdida silenciosa |
| SQL libre por consulta | tiempo, RAM, bytes/filas y CPU configurados por run/tenant | cortar query, conservar receipt de truncación/error |

Estos objetivos no constituyen SLO productivos validados. Antes de fijar EC2/ECS se miden lotes de eventos de plataforma, distribución Jev/LLM real por perfil, MB/s CSV/extractos, p95 de queries, duración de escenarios, cola y presión PG/integración-modelos. `arrival_rate × service_time` estima concurrencia de cada pool del motor; carga 1×, 3× y ráfaga 10× de eventos/jobs, más scan simultáneo. Comparar p50/p95/p99, errores, CPU/RAM/IOPS, pool PG, costo por 1.000 invocaciones de modelo y por oportunidad corroborada. Sin benchmark, infraestructura y límites son parámetros, no garantías.

**Job queue en PG:** `(tenant_id,kind,logical_key,generation)` es único; mismo input/config/snapshot devuelve job existente, mientras nuevo ciclo tras terminal crea `generation+1` con `parent_job_id`/razón. `lane=platform_ingest|detection|evaluation|maintenance`. Workers reclaman lotes pequeños con `SELECT ... FOR UPDATE SKIP LOCKED`, orden por cuota de lane y `priority DESC,due_at,id`, asignan `lease_owner,lease_until,lease_version` en la misma transacción y ejecutan fuera de ella; heartbeat renueva. Escritura final comprueba `(job_id,lease_version,status=running)` y head esperado. Si worker muere, sweeper reencola; viejo worker fenced. `LISTEN/NOTIFY` sólo despierta, polling recupera. Backoff/jitter, máximos y `dead` visible; ledger local conserva keys mientras efectos sean relevantes; unknown sigue matriz por operación §27, no lookup command_key universal.

**Concurrencia y límites:** `RunConfigRevision` asigna cupos separados para SQL sandboxes, decisiones Jev externas, LLM externos, evaluaciones adversariales e ingesta/mantenimiento; cuota por tenant y presupuesto USD/tokens/CPU. Workers controlan jobs activos/lease bajo advisory transaction lock por `(tenant,lane,resource)`; el consumidor aplica slots locales y reserva global en `pulso_quotas`, sin presumir control de réplicas externas. Cada invocación reserva cota superior mediante `UPDATE ... WHERE reserved_units + requested <= limit_units RETURNING version`; llamada adicional requiere nueva reserva. Ante crash la reserva no se rebaja hasta cerrar ventana, por seguridad; receipt registra costo real y sobre-reserva. Si cuota no cabe, job se difiere sin fingir respuesta. Coalescing evita N jobs por N eventos; scan usa particiones/pushdown, no carga el dataset completo en memoria. Particionar jobs/artefactos sólo si tamaño/EXPLAIN lo justifica; índices iniciales `jobs(status,due_at,priority)`, `artifacts(tenant_id,kind,created_at)`, `run_events(tenant_id,run_ref,sequence)`, `ingest_cursors(tenant_id,source,partition)` y FTS tratado. Listas usan cursor; read models cargan refs en lote.

**Backpressure:** si cola/PG/integración-modelos/proveedor/sandbox supera thresholds versionados, se difieren scans de baja prioridad, se recorta exploración por presupuesto y se muestra lag/razón a plataforma. No se degrada seguridad ni se salta verificación. Circuit breaker por proveedor deja `unknown/waiting_dependency`; fallback sólo si el perfil versionado permite otro modelo/región/tratamiento de datos. Workers escalan con imágenes propias; la capacidad externa se negocia; la plataforma sigue independiente. **Gatillo SQS:** si benchmark muestra contención/p95 de claim PG fuera de presupuesto aun con índices/lotes/pools razonables, ADR medido y outbox+SQS con redelivery; hasta entonces una cola.

**Pruebas obligatorias de rendimiento/concurrencia:** dos workers sobre mismo job, lease expirado con respuesta tardía, diez runs del mismo snapshot, ráfaga de 1.000 observaciones por capa mientras se escanean CSV, cola saturada, integración-modelos/proveedor lento, query DuckDB infinita y API expediente con 100 refs. Criterio: cero doble release, cero pérdida de lote/job, lag y p95 dentro de presupuesto configurado en hardware declarado o capacity/config ajustados antes de afirmar cumplimiento.

## 9. Observabilidad de producto y de plataforma

La observabilidad tiene **dos roles**: (1) operar nuestro motor y (2) alimentar la detección con evidencia de lo que las cuatro capas de la plataforma intentaron, omitieron o no pudieron resolver. Instrumentamos API/worker/Core-bridge/PG/sandbox con OpenTelemetry; Los contratos, proyecciones y filtros llevan target_system=attention|evolution y world/environment/purpose; fallos del motor nunca se suman a atención bancaria. `trace_id` y span links unen `source→job→query→signal→proposal→evaluation→release→memory`. La plataforma externa emite eventos estructurados de atención como fuente durable y, opcionalmente, trazas OTel como detalle diagnóstico. El motor ingiere ambos por adapter y los normaliza en `InteractionObservation` con cobertura/clock/fuente; **un span muestreado jamás sirve como denominador poblacional**. `run_id`, `episode_id`, `artifact_id` viven en logs/spans, no como labels de alta cardinalidad. IDs de cliente, texto, SQL literal, argumentos bancarios y secretos no entran en atributos OTel.

| Señal | Ejemplos y dimensiones de baja cardinalidad | Pregunta operativa |
|---|---|---|
| Logs JSON | timestamp, service_role, severity, trace_id, run/episode ref, event_code, policy/config ref, error_code | ¿qué ocurrió y por qué se bloqueó? |
| Eventos de plataforma por capa — **fuente de detección** | `episode/goal`, versión/ruta, clasificador/árbol/IA1/IA2/humano, intentos, checks omitidos, herramientas, motivo de escalamiento, outcome y coverage | ¿qué problema se repite, en qué capa se queda y qué patrón humano podría automatizarse? |
| Trazas de plataforma — evidencia auxiliar | spans de nodo/decisión/model/tool/handoff, error codes, latencia y parent/links | ¿qué hizo o no hizo la capa antes del fracaso?; muestreo y huecos explícitos |
| Métricas USE/cola | CPU/RAM/IO, PG pool/wait, jobs queued/dead/age, lease expiry, SQL concurrency, tokens/USD, cache hit | ¿qué limita throughput/costo? |
| Embudo automejora | signals examinadas/corroboradas/refutadas, oportunidades, propuestas, tests pass/fail/unknown, releases, outcomes maduros, memoria reused/stale | ¿evoluciona el sistema o produce ruido? |
| Trazas del motor | spans `model_call`, `job_claim`, `sandbox_query`, `oracle`, `head_cas`, `release_ack` | ¿dónde se gastó tiempo y dónde falló la automejora? |

Cada métrica de negocio lleva **denominador y cobertura definidos**: `safe_resolution_rate` sólo goals elegibles con outcome observado en eventos durables de plataforma; CSAT/NPS sólo encuestas respondidas con tasa de respuesta; `evaluation_pass_rate` cuenta unknown por separado; `time_to_signal` usa event/observed/processed clocks. Si faltan eventos de una capa o trazas por sampling, la señal se marca `coverage_gap`, no «la capa no hizo nada». Inferir **omisión** exige contrato que declare qué evento se debía emitir y un cierre/timeout durable; ausencia de span aislado no basta. La vista del motor no suma CSV, sandbox y valor USD supuesto en un KPI. Alertas: evento de plataforma atrasado, gaps de correlación, job dead, release ack unknown, memoria revocada recuperada, latencia/costo y telemetría caída; owner/runbook/receipts por alerta.

**Stack local:** [Grafana `otel-lgtm`](https://grafana.com/docs/opentelemetry/docker-lgtm/) recibe logs/métricas/trazas; no montamos Loki/Tempo/Mimir separados. **Stack AWS:** Collector/ADOT exporta a [CloudWatch/X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/xray-instrumenting-your-app.html) con IAM/retención acotados. El motor usa OTLP en ambos. Sampling prioriza errores, pero **OTel es best effort**: `pulso_run_events`, `pulso_audit_events`, lotes de eventos de plataforma con cursor y `pulso_external_commands` son la verdad durable. Un trace ausente deja el detalle diagnóstico `unavailable`, no borra la transición ni altera cobertura de eventos durables. Test apaga collector e inyecta secreto falso: la detección sigue usando eventos durables, reporta falta de trazas auxiliares y no filtra secretos a logs/spans/labels.

## 10. Stacks local, demo pública y despliegue de producto

```mermaid
flowchart TB
  subgraph Local[Podman local]
    CSV[CSV readonly] --> W[Worker automejora]
    SIM[Simulador plataforma] --> W
    W --> PG[(PostgreSQL Pulso)]
    W --> LS[(LocalStack S3)]
    W --> CORE[pulso-core-runtime: Core y bridge, imagen propia]
    CORE --> PGC[(postgres-core PG16)]
    CORE --> GW[Proveedor externo autorizado]
    CORE --> JEV[Jev TLS allowlisted]
    W --> SQL[DuckDB efímera]
    API[Control API/feed] --> PG
    DEBUG[Consola técnica interna] --> API
    W --> LGTM[otel-lgtm]
  end
  subgraph AWS[AWS producto]
    PLAT[Plataforma de atención externa] --> ECS[ECS: API / worker]
    ECS --> RDS[(RDS PostgreSQL)]
    ECS --> S3[(S3)]
    ECS --> CORE2[ECS: pulso-core-runtime, Core y bridge, imagen propia]
    CORE2 --> PGC2[(RDS PG16 de Core: core_runtime/core_eval)]
    ECS --> EXP[pulso-core-exporter]
    EXP --> PGC2
    CORE2 --> GW2[Proveedor externo autorizado]
    CORE2 --> JEV2[Jev TLS allowlisted]
    ECS --> TASK[ECS RunTask: sandbox efímero]
    ECS --> OTel[ADOT → CloudWatch / X-Ray]
    ECS --> PLAT
  end
```

**Local:** `improvement-engine/local` usa `podman compose` para PostgreSQL real, LocalStack **sólo S3**, `control-api`, `worker`, `pulso-core-runtime` (Python: runtime de Core y bridge, imagen propia; código en `core-bridge/`), `core-exporter` y `postgres-core` (PG16, bases `core_runtime`/`core_eval`), con red `core-egress` sólo para `pulso-core-runtime` (la red `pulso-internal` es `internal: true`), `platform-sim`, `debug-console` y `otel-lgtm`. Launcher rootless crea DuckDB efímera sin red/socket Podman, con CPU/RAM/disco/tiempo y mount tratado readonly por run. `scripts/dev.ps1 up`: preflight Podman/dataset/secrets → bucket LocalStack → migraciones separadas de pulso_control/core_runtime/core_eval → `pulso-bootstrap core` (bases, `migrate`, claves, semilla y verificación, §31.9.3) → seed del simulador → SourceContracts/manifest → smoke de modelos externos **reales** Jev/LLM vía Core y detección → feed/consola técnica. Credenciales sólo en secret local ignorado por Git, nunca en compose/config. `doctor` reporta digest/cobertura/config/commit, PG/S3/integración-modelos/proveedor/launcher/OTLP y, con `--with-core`, los checks de Core de §31.11.2; `down` no borra datos por defecto. Recorded responses sólo en tests deterministas/fallos y etiquetadas, no sustituyen el smoke de modelo real.

**Demo de hackathon:** `prod` es el entorno de demo y `staging` es la verificación previa; no existe un tercer entorno `demo`. Si se expone una demo, muestra feed tratado y simulación, no un chat de atención propio ni dataset/credenciales. La consola técnica completa queda en local/staging por VPN/SSM, nunca en la superficie pública; replay público no expone prompts, SQL, trazas internas ni holdout. Si el launcher seguro no pasa preflight, se permite replay inmutable precalculado con receipts y etiqueta explícita; la automejora respaldada por datos se reproduce localmente. Dominio, coste y publicación requieren autorización separada.

**Infraestructura AWS objetivo, entregada de forma incremental:** `infra` define contratos Terraform para `staging` y `prod`, con interfaces de red (VPC, subredes privadas y decisión NAT/endpoints), security groups, IAM, cómputo, storage, base de datos, secretos, API y observabilidad. I06 valida actualmente esos contratos sin provider resources, state remoto, credenciales, OIDC, `plan`, `apply` ni despliegue automático; por tanto no afirma que VPC, ECS/Fargate, RDS, S3, ALB, VPN o alarmas ya existan. Las elecciones concretas se materializan por módulos, ADR, tests Terraform y aprobación humana antes de su primer `apply`. El objetivo técnico conserva: servicios `api`/`worker` y bridge Core con identidad por workload; datos fuente readonly separados de artifacts/extractos; secretos por referencia; telemetría tratada; sandbox efímero sin acceso al bucket fuente; y red privada/autenticación de servicio para la plataforma externa. El proceso autorizado fuera del motor carga el dataset; Terraform nunca lo altera. Core externo maneja su egreso de modelos por perfil y el worker no conoce keys. LocalStack no acredita IAM/VPC/RDS/ECS; los smoke AWS sólo se agregan después de que una topología aprobada exista en `staging`. Nada en AWS muta el dataset original.

**Seguridad del launcher:** API firma grants de vida corta y scope `(tenant,run,source_snapshot,purpose,image_digest,budget)`; launcher local o dispatcher AWS verifica firma, nonce, revocación y mounts, falla cerrado. Sandbox no tiene socket/clave firmante ni acceso a otros tenants; en AWS sólo red/endpoints requeridos para extracto/resultado. ECS/Fargate aporta aislamiento de task/ENI, **no** convierte código/SQL arbitrario en sandbox multi-tenant probado por sí solo: threat model, permisos IAM, test de egress/escape y revisión del runtime son gates antes de dato bancario real. Test de cross-tenant, `final_locked`, revocación y limpieza tras crash es gate. `platform-sim` mantiene estado/DB independientes y falla de manera programable; no es un stub que siempre retorna success.

**CI/CD de dos repos:** cada PR de engine ejecuta en su propio workflow `cargo fmt/clippy/test`, contratos, migraciones sobre PostgreSQL efímero y sus pruebas de integración; no reutiliza un workflow desde `infra`. La suite live de Jev/proveedor externo con cuota y credenciales secretas queda separada de los PRs de forks. Cada PR de infra ejecuta `fmt` y `validate` de Terraform más contratos estáticos en Windows y Ubuntu. Aún no se configura `plan`, `apply`, despliegue, rollback automático, OIDC, state remoto ni alarmas de producción: se incorporan después de definir recursos concretos, secretos y aprobación de entorno. Cuando se habilite CD, el artefacto por digest y su manifest incluirán versiones de engine/Core/schema/migraciones; el despliegue será explícitamente aprobado, con smoke y rollback documentado. El dataset no va a Git ni a imágenes; reports agregados obedecen la política PII. `doctor` falla con explicación cuando falta una dependencia.

## 11. Casos de uso y TDD vertical: qué debe poder construir el equipo

Cada corte arranca con **test observable rojo**, implementación verde, refactor y regresión; se prueba vía API/CLI pública. PG, LocalStack S3, DuckDB y simulador de plataforma con estado/fallos corren reales en integración. Proveedor externo grabado sólo para determinismo/fallos; suite live separada prueba Jev/LLM reales con presupuesto. Cada fase deja demo verificable y recibe revisión adversarial independiente.

| Corte/owner | Historia y comportamiento de aceptación | Test rojo inicial → integración/regresión obligatoria |
|---|---|---|
| S0 data/backend/docs | Como motor, abro un snapshot reproducible de 13 fuentes sin modificar un byte original; como equipo, documento el contrato ejecutable | Fuente mínima→manifest/hash y vista readonly; duplicado, header roto, FK nula, PII oculta, corrección como nuevo snapshot; verificar bytes originales antes/después. Índice/bitácora en Git, primera página de flujo, ADRs de fronteras, PR template y check documental (§26) |
| S1 backend/infra | Como scheduler, nueva fuente o agenda despierta un run una vez | Dos triggers→un logical_key; 2 workers SKIP LOCKED/fencing, PG restart, NOTIFY perdido, lease vencido, DLQ/dead |
| S2 AI/data/modelos externos | Como investigador, consulto SQL/wiki libremente y llamo Jev/LLM reales mediante primitivas Core y egreso gobernado | DuckDB real y wiki montada, QueryReceipt; DecisionModelDef/decide con Jev Choice/Score, agent/LLMAgentPort schema/usage, live smoke, timeout/PII/egress/otro tenant denegados |
| S3 data/AI | Como banco, obtengo hallazgo sustentado o refutado en varios frentes | Métrica→señal con n/denominador/CI; dos familias positivas/negativas, mezcla, rareza, missing, ablation, multiplicidad, `Queja` no hardcoded |
| S4 AI/backend | Como motor, convierto oportunidad en alternativas y bundle compatible | Oportunidad→`do_nothing`+cambios; link correcto/incorrecto, skill/tool ausente, CAS concurrente, agente explora wiki y publica diff |
| S5 AI/eval | Como evaluador, pruebo candidato vs baseline en simulador sin construir atención | Caso normal→oracle; ambiguo/humano ES/PT emitidos por simulador, banco aislado, holdout leak, unsafe, tool unknown, adversarial client, CI/potencia |
| S6 integración/plataforma/frontend | Como motor, observo las cuatro capas y solicito release por contrato; como ingeniero, inspecciono una corrida sin shell | Simulador emite eventos y fallos por capa, ack de release y resultados; API/feed y consola técnica muestran investigación, jobs, eval y bloqueos sin construir runtime/UI de atención (§25) |
| S7 memoria/registry | Como motor, aprendo sin perder lecciones ni activar algo peor | evaluated→espera humana→approve/publish staging→eventos sandbox→wiki→nuevo run; ausencia humana, hashes stale, contradicción/purga/restore |
| S8 infra/producto | Como tercero, reproduzco local y despliego topología real del motor | `doctor`, load/chaos, dos repos, Terraform plan/apply aprobado en staging, Core/provider smoke, rollback de imagen y release externo |

**Escenarios de dominio que no se pueden omitir:** cliente activo/inactivo y producto en mora son estados snapshot, no motivo probado de impago; transacción rechazada por regla legítima ≠ error técnico; contacto/PQR sin join exacto no genera episodio causal; evento digital cercano no prueba motivo; encuesta ausente no equivale a CSAT malo; reclamo templático no aporta descripción individual; una PQR abierta con `sla_breached` no habilita inferir plazo legal; PT generado se etiqueta; fallback manual y no hallazgo son visibles. El benchmark positivo debe usar una misma entidad/objetivo entre señal, escenario y ChangeSpec, no sólo similaridad textual.

**Escenarios técnicos adicionales identificados en esta revisión:**

| ID | Perturbación | Estado/receipt esperado y nivel de prueba |
|---|---|---|
| C01 | Worker A pierde lease mientras B termina | Un solo head/efecto; A recibe `stale_lease`; integración con PG real |
| C02 | PG cae tras escribir blob S3 pero antes de artifact commit | Blob huérfano GC; run se reintenta, sin claim publicado; fault injection |
| C03 | PG cae tras commit pero antes de notificación | polling ve job/artefacto; no duplicado; integración restart |
| C04 | Core/proveedor Jev/LLM tarda o devuelve salida inválida durante investigación | job `waiting_dependency`/error tipado, cuota/receipt, sin oportunidad corroborada ficticia; integración + smoke live |
| C05 | Tool mutante confirma pero red se corta antes del receipt | `unknown`, reconciliar por key; jamás reejecutar a ciegas; contract banco |
| C06 | Kill-switch concurrente con aprobación/publicación | detiene nuevos comandos locales; si publish ya enviado reconcilia antes de declarar cancelación; humano promueve versión segura; E2E registry |
| C07 | Fuente o grant revocado durante SQL/LLM | fence de publicación/efecto y memoria, incidente; security/fault |
| C08 | Final holdout aparece en memoria/SQL/primer prompt | test canario detecta fuga y bloquea release; integración |
| C09 | Dos propuestas compiten por mismo bundle/portafolio | CAS una gana, otra rebase/retest; no doble valor; integración |
| C10 | Dataset completo, burst de 1.000 observaciones y scan pesado | atención no comparte pool; p95/costo/queue lag medidos; performance |
| C11 | Sin cobertura/split apto para discovery | `not_evaluable`/hallazgo negativo visible, sin inventar mejora; E2E |
| C12 | Restore desde backup con tombstone posterior | wiki/fuente bloqueada antes de servir workspace o enviar datos a modelos; restore test |
| C13 | Misma plantilla PQR/transcript en clientes distintos | familia completa en un split o benchmark semántico `not_evaluable`; eval |
| C14 | Cliente API `viewer` intenta aprobar release | 403, sin datos sensibles, audit event; contract API |

**Pruebas por nivel:** unit para reducers, MetricSpec, ranking, ValueModel, wiki validator, oracle y CAS; contract para schemas/SourceContracts, `PlatformObservationPort`, adaptador registry Core, decisiones Jev externas/OpenRouter y N/N−1 interno y snapshot exacto upstream; integración PG/S3/DuckDB/Podman/simulador reales; E2E snapshot→segunda mejora con observaciones externas; regresión joins/PII/holdout/rollback; load del consumidor de modelos/jobs y chaos C01–C12. Cada PR cita historia, input, salida y rojo→verde. Mocks son correctos **en la frontera de plataforma**; no sustituyen las dependencias reales del motor.

## 12. Plan de decisiones, riesgos y Definition of Done

Decisiones del usuario: (1) éxito = descubrimiento autónomo + propuesta/automejora relevante; (2) envío de datos a modelos permitido cuidando PII; (3) política/autoridad del banco se simulan en frontera de plataforma, no se fingen reales; (4) límites/settings configurables/versionados; (5) EC2 permitido para demo; (6) presentación fuera; (7) **F7/F8 son responsabilidad de la plataforma y no se construyen aquí**; (8) Jev/LLM reales a través de integración externa Core; (9) o11y de cuatro capas es fuente de detección; (10) infra en repositorio propio con Terraform y CI/CD. El motor debe funcionar solo, pero hacer visible todo su razonamiento operativo y pedir ayuda humana excepcional.

**Riesgos/validaciones que no se deciden por prosa:** la copia sintética podría no soportar un bridge histórico→solución concreto; un resultado `no_supported` sería técnicamente correcto pero no cumple la demo de éxito. El sistema debe investigar varias familias sin hardcode, y el equipo sólo itera detectores/gates mediante versiones y tests independientes, nunca reetiqueta salida para conseguir «quejas». El costo/latencia de Jev/LLM, capacidad EC2, pureza del holdout, privacidad de texto enviado y aislamiento de sandbox se miden/proban. Para producción real siguen faltando autoridad bancaria, objetivos regulatorios/retención, RPO/RTO, recursos y SLO medidos; sus **contratos existen**, pero no se afirma que estén satisfechos.

**Definition of Done del spec (antes de TDD):** equipo confirma fronteras, schemas de observación/release/integración externa de modelos, métrica de éxito, stack local/AWS, PII y presupuesto. **DoD de cada corte:** historia observable, RED→GREEN por interfaz pública, tests unit/contract/integración/E2E pertinentes, config/contratos en Git, documentación técnica que corresponda al código actual, entrada de bitácora con pruebas/pendientes, ADR si cambió una decisión, receipts, recuperación/rollback y revisión adversarial (§26). **DoD del motor demo:** tercero clona engine+infra limpios, monta dataset aprobado local, ejecuta `doctor`, reproduce detección no hardcodeada con Jev/LLM reales, inspecciona expediente/wiki/feed **y consola técnica sin shell**, ve propuesta y evaluación baseline/candidato, release/rollback confirmados por simulador y segunda iteración. El simulador cubre cuatro capas en ES/PT sin construir atención real. URL pública sin CSV muestra replay/fixtures generados **etiquetados**, nunca se confunde con run privado.

El spec fue aprobado por el usuario para implementación incremental. Los repos `improvement-engine` e `infra` existen; ejecutar cortes TDD con PRs y revisión independiente. La aprobación no acredita dependencias externas listas ni software construido. V1 conserva historial de diseño.

## 13. Fuentes técnicas y límites de interpretación

- PDFs de Factored suministrados: entregables/criterios de hackathon; no son autorización para publicar secretos ni prueba de datos bancarios reales.
- Dataset Summary/Data Dictionary suministrados y CSV locales: esquema y datos sintéticos; el manifest físico recalculado manda para conteos, nulls y cobertura. Credenciales del diccionario no se copian al repositorio/documento.
- [Karpathy, LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) y [MemPalace](https://github.com/MemPalace/mempalace): inspiración para fuente→síntesis→recuperación; no dependencia obligatoria ni benchmark bancario.
- [Jev](https://docs.typesafe.ai/introduction): juicios estrechos tipados; razonamiento abierto y diseño de cambios usa LLM/validador externo.
- [OpenRouter API](https://openrouter.ai/docs/api_reference/overview): chat completions, structured outputs y usage; el consumidor verifica capacidades/route del modelo concreto y no da por garantizado un parámetro que el proveedor ignore.
- [PostgreSQL `SKIP LOCKED`](https://www.postgresql.org/docs/current/sql-select.html) y [`NOTIFY`](https://www.postgresql.org/docs/current/sql-notify.html): base de cola durable + wakeup no durable; la elección de no usar SQS es decisión de diseño que debe validarse con carga.
- [Grafana otel-lgtm](https://grafana.com/docs/opentelemetry/docker-lgtm/) para desarrollo y [AWS OpenTelemetry/X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/xray-instrumenting-your-app.html) para exportar en AWS; la paridad de instrumentación no implica paridad de backend.
- [Podman Compose](https://docs.podman.io/en/latest/markdown/podman-compose.1.html), [LocalStack/Podman](https://docs.localstack.cloud/aws/customization/other-installations/podman/) y [LocalStack/Terraform](https://docs.localstack.cloud/aws/connecting/infrastructure-as-code/terraform/): herramientas de emulación; LocalStack no prueba IAM/VPC/RDS/ECS.
- [ECS RunTask e idempotencia](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_Idempotency.html), [red Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-task-networking.html) y [endpoints ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/vpc-endpoints.html): el `clientToken` tiene TTL, la subred privada necesita rutas/endpoints para arrancar, y el task aislado requiere validación de seguridad propia.

## 14. Contrato inicial ejecutable que acompaña este spec

Para que V2 se pueda leer **sin** tomar la V1 como contrato oculto, estos son los campos y reglas de los primeros adapters. Cada tabla original conserva sus columnas y su orden; el adapter selecciona campos en una vista readonly y conserva `raw_file_digest`. `!` significa requerido para esa vista, `?` nulo permitido. Timestamp de CSV sin zona se interpreta como UTC **por convención de replay, no por hecho del banco**; se guarda raw y la asunción. Vacío→null, no cero/false; PK duplicada idéntica se deduplica con quality receipt, divergente bloquea la vista del slice; FK huérfana no borra la fila y reduce cobertura del join. Test golden físico define parse/hash/normalización y comprueba bytes originales idénticos antes/después.

| Vista SourceContract inicial | PK y campos consumidos (no cambio de schema original) | Regla temporal/semántica |
|---|---|---|
| `customers@1` | `customer_id:text!`, `country:text?`, `segment:text?`, `customer_status:text?`, `registration_date:date?`, `last_updated:timestamp?` | snapshot; país/status no se retroproyectan a contactos pasados |
| `products@1` | `product_id:text!`, `customer_id:text!`, `product_type:text?`, `product_status:text?`, `opening_date:date?`, `days_past_due:int?`, `last_updated:timestamp?` | mora/status sólo snapshot; valor negativo de days_past_due no entra en métrica |
| `call_center_interactions@1` | `interaction_id:text!`, `customer_id:text!`, `interaction_date:timestamp!`, `contact_reason:text?`, `channel:text?`, `was_resolved:bool?`, `requires_followup:bool?`, `agent_id:text?`, `duration_seconds:decimal?`, `wait_time_seconds:decimal?` | razón gruesa; `was_resolved` operacional, no resolución verificada |
| `complaints@1` | `complaint_id:text!`, `customer_id:text!`, `creation_date:timestamp!`, `category:text?`, `subcategory:text?`, `reception_channel:text?`, `priority:text?`, `status:text?`, `sla_breached:bool?`, `resolution_date:timestamp?`, `first_response_date:timestamp?` | flag SLA suministrado, no cálculo legal; resolution_date no feature previo |
| `transactions@1` | `transaction_id:text!`, `customer_id:text!`, `transaction_date:timestamp!`, `transaction_status:text?`, `response_code:text?`, `amount_usd:decimal?` | rechazo legítimo ≠ bug; USD nulo ≠ cero |
| `digital_events@1` | `event_id:text!`, `customer_id:text?`, `session_id:text?`, `event_date:timestamp!`, `event_type:text?`, `event_category:text?` | no FK a transacción/contacto |
| `satisfaction_surveys@1` | `survey_id:text!`, `interaction_id:text?`, `survey_date:timestamp!`, `survey_type:text!`, `main_score:int?` | CSAT 1–5, NPS 0–10; reportar cobertura de respuestas |

Las otras seis fuentes tienen contrato mínimo abajo. S0 verifica golden test físico, tipos, nulabilidad y fechas antes de habilitar cada sensor. No se modifica una tabla original para cumplir contrato. Campos sensibles no seleccionados jamás entran al lab por `SELECT *`.

| Vista SourceContract inicial | PK y campos consumidos | Semántica/guard |
|---|---|---|
| `branches@1` | `branch_id:text!`, `country:text?`, `branch_type:text?`, `branch_status:text?` | snapshot; dirección/teléfono no entran al lab |
| `service_agents@1` | `agent_id:text!`, `assigned_branch_id:text?`, `agent_type:text?`, `experience_level:text?`, `specialty:text?`, `agent_status:text?` | snapshot; nombre/email/teléfono no entran; `avg_csat` no sustituye encuestas enlazadas |
| `marketing_campaigns@1` | `campaign_id:text!`, `campaign_type:text?`, `campaign_objective:text?`, `promoted_product:text?`, `start_date:date?`, `end_date:date?`, `budget:decimal?` | presupuesto sin moneda no se convierte a USD por inferencia |
| `daily_exchange_rates@1` | PK compuesta `(date,source_currency,target_currency)`, `exchange_rate:decimal!`, `source:text?` | guardar par/fecha/fuente; sin par o tasa válida → `conversion_unavailable` |
| `call_transcripts@1` | `transcript_id:text!`, `interaction_id:text!`, `process_date:timestamp?`, `detected_language:text?`, `full_text:text?` | texto sensible y posiblemente plantilla: excluido de lab general; acceso sólo a purpose `semantic_review` con máscara y audit |
| `campaign_sends@1` | `send_id:text!`, `send_date:timestamp!`, `campaign_id:text!`, `customer_id:text!`, `was_delivered:bool?`, `was_opened:bool?`, `was_clicked:bool?`, `had_conversion:bool?`, `conversion_value:decimal?`, `send_cost:decimal?` | aperturas/conversión son flags sintéticos; valor/costo sin moneda explícita no se expresa en USD |

**Primeras dos `MetricSpec`, no los únicos sensores futuros:** `contact_unresolved@1` mide `COUNT(DISTINCT interaction_id)` con `was_resolved=False` / contactos con flag conocido, por `(contact_reason,channel)` y compara resto del mismo canal; `pqr_sla@1` mide PQR con `sla_breached=True` / PQR con flag conocido, por `(category,subcategory,reception_channel)` y compara resto de la misma categoría/canal. Guardan total, conocido, missing, source refs, intervalo y calidad. No se suman sus burdens ni se usan como casos evitables. `SourceContract` y configuración versionada agregan las demás familias con el mismo interface sin cambiar código de dominio por `Queja`.

`DiscoveryConfig@1` usa perfiles separados, fijados antes de evaluar resultados. Perfil histórico: cutoff `T` = medianoche UTC posterior a última fecha completa disponible para fuentes requeridas; discovery `[T−60d,T−30d)`, confirmación `[T−30d,T)`; si no hay 60 días completos → `insufficient_temporal_coverage`, no acortar después de mirar. En discovery se seleccionan hasta 3 celdas por familia por diferencia descriptiva ponderada, luego tamaño e ID para empate. Confirmación sólo de esas celdas, con cobertura de flag ≥80%, `n_known≥500` en celda y referencia en ambos periodos, bootstrap 2.000 remuestreos por cliente con seed derivada del manifest/config y límite inferior de diferencia >0 con α=0.05/K Bonferroni por familia; estratificar por canal y excluir clientes p99 para sensibilidad. Si falta cobertura → `insufficient_evidence`; diferencia no persiste → `refuted_or_unconfirmed`; gates pasan → `corroborated_descriptive`, **no causa ni ahorro**. Perfil E0: usa casos disponibles al training_as_of, mínimo descriptivo inicial de 20 casos distintos por patrón y cobertura conocida ≥80%; sin dos ventanas comparables no declara corroboración estadística, sino `candidate_descriptive`, que puede investigarse y generar propuestas cuya mejora se prueba después en escenarios. Confirmación posterior respeta reloj replay y splits; no exige artificialmente 500 casos a un arranque de 200 ni garantiza encontrar tres oportunidades. Ambos perfiles registran universo, grano, soporte, faltantes y madurez por separado. Son defaults de ingeniería configurables/versionados, no evidencia bancaria. Tests golden cubren bordes temporales, población pequeña, semilla, ranking y ausencia de hallazgo forzado.

`WorkflowCatalog@1` contiene rutas candidatas `transaction_status_lookup`, `pqr_status_lookup`, `product_information_lookup`. `pqr_followup_triage` es **subruta del árbol `pqr_status_lookup`**, no clase nueva del clasificador: con PQR propia/abierta y política sandbox, explica estado y escala; `sla_breached` posterior no es input de decisión. Cualquier ruta requiere llave verificada, población elegible, tool/registro confiable, política sandbox, oracle y casos normal/ambiguo/humano; si falta, `unlinked`. La selección recorre oportunidades elegibles según §29.8 por ranking sellado y elige primera ruta viable **sin fijar categoría ganadora**. E2E original-only del dataset entregado debe producir al menos una oportunidad corroborada y un candidato relevante evaluado sobre el mismo mecanismo/flujo; fixtures prueban positivo/negativo pero **no sustituyen** la detección histórica. `linked` se subdivide en `same_outcome_linked` y `mechanism_proxy` (§16): no se afirma mejora del outcome histórico con sólo este último. Si el dataset no permite ni un bridge de mecanismo, se informa fallo del objetivo y se revisa detector/alcance con nueva config y holdout independiente, no se inventa atribución.

## 15. Revisión adversarial propia: contratos que aún podían quedar implícitos

La simplificación elimina tablas/servicios, **no** invariantes. Esta tabla fija el reducer de jobs y la separación de efectos; evita que dos implementadores inventen comportamientos distintos.

| Estado de `pulso_jobs` | Transición admitida / guard | Efecto durable |
|---|---|---|
| `queued` | `claim` con cuota/lease → `running`; presupuesto/fuente no lista → `deferred` | `lease_version+1` al claim; razón/`due_at` al defer |
| `running` | `success` con lease vigente → `complete`; dependencia externa → `waiting_dependency`; error transitorio → `retry_wait`; error definitivo/límite → `dead` | resultado+artefactos+head CAS en transacción PG; no se declara success antes |
| `deferred`, `waiting_dependency`, `retry_wait` | evento/cadencia y misma config/snapshot → `queued`; config/snapshot distinta → `superseded` y nuevo job | razón y próximo wakeup visibles; no se reabre input sellado |
| `complete`, `dead`, `superseded`, `cancelled` | terminal | nuevo intento lógico crea job sucesor, no cambia pasado |

Revocación autorizada fencea lease local y evita nuevos efectos. El job queda cancelled sólo cuando no existe efecto externo pendiente; si pudo enviarse conserva unknown y el run permanece cancel_requested hasta reconciliar (§29.8). `complete` significa receipt durable, no publicación. Ledger `prepared→sent→confirmed|rejected|unknown→reconciled` es Pulso. Reconciliación usa protocolo específico §27: GET proposal para draft/freeze por HTTP; publish misma key; create/promote HTTP sin lookup idempotente quedan unknown/manual_reconcile si no se puede probar. Métodos locales de BuilderToolExecutor sí usan key/get_write cuando disponibles. Core es autoridad de Release y staging/prod; nuestro artifact refleja propuesta/receipt, no shadow/canary. No extrapolar CAS local a exclusión de otros writers upstream.

**API mínima del motor:** `POST /api/v1/evolution/runs` sólo para disparo explícito opcional (idempotente), `GET /api/v1/evolution/runs/{id}`/`discovery-report`, `GET /api/v1/evolution/opportunities`/`{id}`/`lineage`, `GET /api/v1/evolution/proposals/{id}`/`diff`, `GET /api/v1/evolution/candidates/{id}/evaluation`, `GET /api/v1/evolution/releases/{id}`, `POST /api/v1/evolution/releases/{id}/rollback` autorizado, `GET /api/v1/evolution/memory/wiki/{scope}`/`revisions`, `GET /api/v1/evolution/activity`/`stream`, `GET /api/v1/evolution/platform-observations/{id}` tratado y `POST /api/v1/evolution/decisions/{id}/responses` (§20.1, ruta canónica; no alias respond). Integración privada: `POST /internal/v1/platform/observations` (§24), adaptador saliente Core §§17/27; PlatformReleasePort futuro no es API upstream. **No** hay endpoints de chat con cliente, oficina de agentes, constructor conversacional ni CRUD de capacidades de la plataforma. Colecciones con cursor/limit ≤100; negativos son status explícitos, no 404. `viewer` lee redacted; `operator` puede detener o solicitar rollback; acciones registry de approve/reject/publish/promote requieren builder humano step_up con aprobador; revoke requiere admin; nadie amplía autoridad por prompt. `expected_revision` en mutaciones Pulso; PUT Core usa expected_rev y promote carece de CAS upstream; 409 entrega head/diff seguro. Cualquier aporte experto entra como evidencia/decisión, no como edición directa del outcome histórico. Las rutas de producto y DTO de §§20.1/20.2 son canónicos; este resumen no crea aliases /v1 ni otra superficie pública.

**Prueba de autoconsistencia:** generar OpenAPI/JSON Schema desde Rust, validar wire fixtures, y recorrer `source_snapshot→signal→opportunity→ChangeSpec→EntityDraft→Proposal/Candidate→EvalReport+ImprovementEvidence→human_approval→ReleaseDetail staging→EngineEvent→memory_wiki` usando **sólo las diez tablas del motor y sus puertos**. Otra tabla exige ADR, consumer, migración y test. `SourceRef` rota falla `source_unavailable`; final_locked no entra a prompt/SQL/wiki de desarrollo. Contract test debe poder reemplazar simulador por adapter de plataforma sin tocar `core/app`.

## 16. Contrato de evidencia → cambio → resultado (normativo)

El problema central no es generar JSON de una propuesta: es impedir que un hallazgo histórico y una mejora sandbox inconexa se presenten como el mismo resultado. El `WorkflowBridge` se construye **antes** del `ChangeSpec` y del set final. Requiere `target_outcome`, `unit_of_analysis`, `eligible_population_query_digest`, `entity_key`, `as_of_cutoff`, `candidate_route`, `mechanism`, `intervention_point`, `observable_effect`, `oracle_measure`, `link_grade`, `missing_links[]` y `support_refs[]`. El validador, no el builder LLM, asigna `link_grade`:

| Grado | Predicado comprobable | Afirmación permitida |
|---|---|---|
| `same_outcome_linked` | Clave estable entre observación y ejecución, mismo outcome definido antes de intervenir, cambio capaz de alterarlo, estado inicial disponible antes del outcome y oracle independiente | «En sandbox, el candidato mejora el mismo outcome definido para la población elegible». Nunca se extrapola automáticamente al banco real |
| `mechanism_proxy` | Ruta/población plausibles y mecanismo probado, pero falta join, estado contrafactual u outcome histórico comparable | «El CSV indica carga; este mecanismo funcionó en escenarios sandbox». Beneficio monetario sólo como rango de supuesto |
| `unlinked` | Cambio no puede afectar la métrica o no se identifica población/ruta | No se promueve bajo esa oportunidad; puede abrir investigación independiente |
| `not_evaluable` | Faltan fuente, estado, oracle o muestra válida | No hay gate de mejora ni claim de valor |

Ejemplo prohibido: detectar `contact_unresolved` en `Queja`, observar muchas PQR con `sla_breached` y probar un árbol `pqr_status_lookup`; `origin_interaction_id` está vacío en la copia auditada, y un status lookup no cambia por sí mismo resolución del contacto ni SLA. Son **dos hechos** y una posible intervención de información, no una cadena causal. Ejemplo permitido como `mechanism_proxy`: ese mismo contacto motiva explorar un árbol de identificación de PQR que reduce escalamiento innecesario en episodios sandbox donde identidad/PQR/handoff son verificables; se informa la tasa de handoff sandbox y la cobertura elegible, **no** «PQR evitadas». Para llegar a `same_outcome_linked` en una fuente futura harían falta llave/tiempo del episodio, definición de resolución y oracle del mismo objetivo; el spec no presupone que el CSV actual lo tenga.

El primer perfil medido del dataset se incorpora como **evidencia de diseño, no regla de selección**: en la ventana 2026-04-18 a 2026-06-17 (fin exclusivo), `Phone/Queja` tiene 5.339 contactos y `was_resolved=False` ≈56,3%; `Phone/Transaccional` 11.167 y ≈8,1%. La espera telefónica media de esos dos grupos ronda 119 s en ambos: no respalda una tesis de espera específica de quejas. Recalcular con snapshot/contratos y reportar cobertura antes de citar; no se pinnea este resultado en `DiscoveryConfig`. En PQR de la misma ventana, `first_response_date` sólo está poblado en alrededor de 59–62% de varias categorías principales, así que «demora hasta primera respuesta» no puede usar todas las PQR como denominador ni equipararse a `sla_breached`. Ningún motor usa campos posteriores (`resolution_date`, `sla_breached`, `was_resolved` de un contacto recién iniciado) como feature predictiva anterior. El gate de temporalidad verifica `available_at ≤ decision_at`, no sólo `event_date ≤ decision_at`.

**ValueModel@1** separa `observed_burden`, `eligible_fraction`, `effect_if_exposed`, `adoption`, `unit_value_usd`, `implementation_cost_usd`, `operating_cost_usd` y `confidence`. `gross_scenario_usd = volume × eligible_fraction × effect_if_exposed × adoption × unit_value_usd`; `net_scenario_usd = gross − implementation − operating`. Cada factor tiene `evidence_kind` y rango bajo/base/alto; sin USD respaldado se deja `unknown`, no cero. Portfolio calcula valor **marginal**: si dos propuestas cubren la misma población/episodio, la segunda usa sólo casos adicionales o incremento sobre primera; jamás suma dos veces el total. Ranking predeclarado usa primero seguridad/evaluabilidad, después `expected_net_scenario_range`, esfuerzo, incertidumbre y alcance; los pesos/versiones viven en config, no se ajustan tras ver ganador. Publicar un rango no prueba causalidad bancaria.

## 17. Contratos de capacidades hacia la plataforma: lo que el builder produce

El objetivo del builder es producir **artefactos ejecutables por Agent Core**, no un formato alternativo de agente. El baseline de compatibilidad es el checkout `references/agent-core` en SHA `86a767474042a566a0dbd6ed23588959f27ebdb3`, `contracts/VERSION = 1.3.0` (reemplaza el pin previo `53e729d624c8284e906249df84c1a1df84cc8d40` / `0.5.0`; 72 commits de diferencia, ver nota de corrección 03-10-2026). `crates/core` conserva nuestros contratos de investigación, evidencia y operación; el módulo `core/agent_core_wire` (ruta física `crates/core/wire/agent_core@<sha7>/`, §31.4.1) reproduce los schemas upstream fijados (`contracts/schemas/*.json`, generados vía `uv run agentcore contracts`, no editables a mano; `EvalSuite`, `EntityDraft`, `VersionDocs` y las respuestas del registry no existen allí y se derivan, §31.4.1) y un adaptador exporta los objetos sin renombrar sus campos. Los schemas y fixtures de ese SHA son la autoridad de forma; M0/M1/M2/M3/M4 y ADR0019 explican semántica y restricciones. Una actualización upstream requiere revisión de diff, fixtures y prueba de compatibilidad, no cambiar automáticamente el pin.

Hay **dos espacios de referencias**. Pulso identifica evidencia y snapshots con `(tenant_id,id,revision,digest)`; Core identifica entidades con `(EntityKind,id,version)` semver. `RefSpec{id,spec}` puede admitir rangos durante autoría; una release ejecutable lleva `EntityRef{id,version}` exacta `X.Y.Z`, sin prerelease/build. El hash de contenido verifica integridad y no reemplaza semver. El envelope Pulso no se inserta dentro de una entidad Core (`extra=forbid`). El adaptador conserva metadata/PII/tenant fuera del body upstream y mantiene un mapa verificable entre ambas referencias.

| Tipo | Campos obligatorios y validación | Consumidor/fallo |
|---|---|---|
| `ChangeSpec` | `base_bundle_ref`, `opportunity_ref`, `workflow_bridge_ref`, `operations[]` (`add\|replace\|disable`, `target_kind`, `target_ref`, `new_ref`, `precondition_digest`), `expected_mechanism`, `affected_routes[]`, `rollback_ref` | Builder emite; `prepare_bundle` rechaza operación sin ruta/precondición, cambio fuera de bridge o referencia mutable |
| `CapabilityBundle` — Pulso | Siempre: `state=draft\|frozen\|evaluated`, `core_baseline_sha`, `core_schema_version`, `agent_id`, `change_spec_ref`, `entity_artifact_refs[]`, `workflow_bridge_ref`, `base_ref` nullable para agente nuevo. Draft permite `authoring_release_ref?`; frozen requiere `authoring_release_ref,pinned_release_ref,registry_proposal_id,candidate_hash,compatibility_digest`; evaluated añade `evaluation_ref` con ambos gates y suite ref/digest | Envelope Pulso, no body Core; refs apuntan snapshots inmutables. Estado evaluated del envelope no reemplaza Proposal.state. Rutas/capas son metadata externa |
| `Agent` — Core | `id`, `version`, `mode=conversational\|task`, `entry_flow`, `invocable_by`, `min_auth_level`, `subject_kinds`, `supported_locales`, `default_locale`, `tools_allowed`, `budgets`, `templates`, `max_clarifications`, `on_clarify_exhausted`, `default_target_queue`; opcionales/defaults conforme schema: `understand`, `slots_model`, `inactivity_ttl`, `max_repair_turns_per_run`, `metrics`. **Nuevos en este pin, no presentes en el spec previo:** `accepts` (`TransferContract` opcional, nullable) y `routing` (`RoutingCard` opcional, nullable) — ambos ligados al subsistema de transferencia entre agentes (ADR0021, ver fila nueva más abajo) | Sustituye wire `AgentSpec`. La capa IA1/IA2 es metadata de plataforma; Jev es proveedor de `DecisionModelDef`, no tipo de agente. Un agente es un descriptor cuyo `entry_flow` gobierna su ejecución. `accepts`/`routing` describen capacidad de recepción de transferencia de la plataforma; el builder no los emite en el primer corte (ver más abajo), sujeto a verificación si/cuando el subsistema quede aprobado |
| `Flow` — Core | `id`, `version`, `priority`, `nodes[]` no vacío; cada nodo tiene `id`, `type`, `config`, `next` | Sustituye wire `TreeSpec`; entrada = primer nodo. Config y ramas obedecen la unión discriminada upstream, no `check\|ask\|effect`. El simulador conserva recibos propios que referencian `(flow@version,node_id)` |
| `DecisionModelDef` — Core | `id`, `version`, `output_schema`, `calibrated_fields`, `input_view`, `providers[]`, `calibration`, `thresholds_from?` | Proveedores `jev\|classifier\|llm_structured\|rule`; `decide.branch_on` es propiedad enum string de primer nivel y campo calibrado, con rama `low_confidence`. No equiparar confianza del proveedor a calibración validada |
| `Prompt` / `Template` — Core | Ambos: `id`, `version`, `locales`, `reads`; Prompt añade `model_profile` | Prompt sin interpolación `{{ }}`; Template permite rutas y el loader deriva `reads`. Locales cubren los soportados por cada Agent. Contenido de skill puede compilarse a estos artefactos o Flow, pero `SkillSpec` no es entidad Core |
| `ModelProfile` — Core | `id`, `version`, `endpoint_alias`, `model`, `temperature`, `max_tokens`, `price{input_per_mtok,output_per_mtok,source,as_of}`; `timeout_s`, `structured` con defaults upstream | Alias de endpoint sin credenciales; números/precios Decimal finitos. El adaptador consumidor debe mapear el perfil sin sustituirlo por su propio `ModelPolicy` |
| `ToolDef` — Core | `id`, `version`, `risk_class=read\|compute\|write_draft\|write_reversible\|write_irreversible\|money_movement`, `min_auth_level`, `idempotent`; `readback_by=idempotency_key` obligatorio para escritura; campos opcionales/defaults: `max_auth_age`, `untrusted_fields`, `source`, `confirmation_ttl`, `description`, `args_schema` | Definición no crea executor: referencia tool realmente disponible en plataforma/sandbox. Nodo `agent` exige `description` y `args_schema` cerrado. `ToolSpec` interno conserva receiver/timeout/reconcile, sin inventarlos como campos wire |
| `Policy` / guards — Core | Policy: `id`, `version`, `owner`, `expr`, `rationale`; `LanguageDetection` (`id`, `version`, `detector`, `candidates`, `thresholds_from`, `unsupported`, `min_letters`, `min_letters_unsupported`) e `InjectionRuleset` (`id`, `version`, `rules`) conforme schemas | Versionar reglas/guardas usadas por release; autoridad protegida no se modifica desde una hipótesis. Mock de política se etiqueta como tal. `InjectionGuard`/`InjectionRule(set)` y `LanguageDetection`/`LangGuard`/`LangScore` mantienen la forma descrita en el pin previo (ADR0012); no se detectó cambio de forma en este pin, pero queda sujeto a verificación en cada actualización |
| `KnowledgeSnapshot` — Core | `id`, `version`, `pages[]`; página (`KnowledgePage`): `path`, `hash`, `audience`, `status`, `lang` obligatorios; `approved_by`, `translation_of?`, `valid_from?`, `valid_to?`, `source_refs[]` opcionales | Exportación de conocimiento aprobado de atención, separada de wiki analítica Pulso. Texto reside en blob store por hash; estado approved exige approved_by. No habilita automáticamente nodos de conocimiento aún no disponibles |
| `Release` — Core | Resultado de publicación (M0): `id`, `status=active\|revoked`, `entities` (mapa `EntityKind → {id: version}}`), `language_detection` obligatorios; `interrupts[]`, `injection_ruleset?`, `knowledge_snapshot?`, `max_input_chars` (default 4000) opcionales. **El tipo se llama `Release`, no `ReleaseDecl`** — `ReleaseDecl` sigue existiendo en este pin (`agent_core/flows/registry.py`) pero es exclusivamente el insumo de autoría previo a publicar (`id`, `agents[{agent,aliases}]`, `flows`, `interrupts`, `language_detection`, `injection_ruleset?`, `knowledge?`, `max_input_chars`); `pin_release` lo convierte en `Release` exacta | No confundir release Core con campaña canary Pulso. Publicación fija refs y clausura; runtime nunca resuelve rangos. Identidad, permisos y lifecycle del registry siguen gobernados por upstream |
| `Goal` | `goal_id`, `intent`, `subject_ref`, `requested_outcome`, `eligibility`, `state=pending\|clarifying\|in_progress\|verified\|failed\|handoff` | Schema de evento externo; plataforma decide outcome y emite proof, motor sólo observa/evalúa |
| `RouteDecision` / `LayerAttempt` | `input_event_ref`, `classifier_ref`, `intent_candidates`, `confidence_or_abstain`, `route_ref`, `reason_codes`; attempt añade `layer`, `started_at`, `ended_at`, `result`, `receipt_refs[]` | Contrato de observación externa para replay/evaluación; output inválido/timeout/denied no equivale a resuelto |
| `EffectReceipt` | `command_key`, `receiver`, `request_digest`, `status=confirmed\|rejected\|unknown`, `receiver_receipt_ref?`, `observed_at`, `reconcile_after?` | Emitido por plataforma/simulador; única base para afirmar efecto observado |
| **Tipos nuevos del pin (capacidad de plataforma, no contrato que el builder deba emitir en el primer corte)** | `TransferContract`, `TransferPacket`/`TransferPacketSpec`, `TransferNode`/`TransferConfig`, `TransferReceived`/`TransferRejected` (+ sus `*Payload`), `RunTransferred`/`RunTransferredPayload` (ADR0021, subsistema de transferencia entre agentes); `AwaitApprovalNode`/`AwaitApprovalConfig` (ADR0014); `StepUpPrompt`, `StepUpRequested`/`StepUpRequestedPayload` (ADR0010); `EncryptedBlob` (`kid`,`nonce`,`ciphertext`), `Fingerprint` (`alg`,`kid`,`value`), `OutboxMessage` (`message_id`,`type`,`run_id`,`payload`,`created_at`); `MetricDef`/`MetricExpr` (DSL de métricas por agente, ADR0020, `SCHEMA_VERSION` propio `1.2.0`, separado del `contracts/VERSION` general) | Ninguno es objeto que Pulso deba producir hoy. Transferencia entre agentes (ADR0021) es ruteo interno de agent-core entre runs/agentes, documentado como **implementado en rama de desarrollo `feat/transferencia-entre-agentes` pero pendiente de aprobación** en el repo verificado — tratarlo como capacidad futura de la plataforma, no requisito del mock inicial. `AwaitApprovalNode`/`subflow` ya aparecían deshabilitados en el baseline previo (§17 tabla de compilación) y siguen igual, sujeto a verificación en cada pin. `StepUp*` gobierna reautenticación de operaciones sensibles (aprobación/publicación/promoción, §498) y Pulso sólo la solicita, no la implementa. `MetricDef`/`MetricExpr` alimenta `Agent.metrics`/`eval_suite` de evaluación por agente (ADR0020); su relación con `EvaluationPlan`/gate de Pulso (§18) queda pendiente de confirmar caso a caso, no se asume equivalencia automática |

**Compilación `ChangeSpec → paquete Core`.** (1) Resolver base fijada (`ReadBase`, §31.3.1) y operaciones autorizadas, con precondition digest (= `content_hash` Core, §31.4.2; Core no valida precondiciones por entidad: se cierra por doble lectura, §31.4.10); (2) producir entidades nuevas/versionadas con formato upstream; (3) no se construye `ReleaseDecl` por la vía registry: el servicio la deriva de la base y las entidades (`candidate._decl`); un cambio a nivel release es `dependency_blocked(release_level_change)` (§31.4.4); (4) validar schemas, referencias, G0/AG, permisos/locales y disponibilidad de executors; (5) calcular clausura transitiva y fijar refs; (6) la `Release` la produce `publish` (vía `pin_release` dentro de Core); Pulso la lee y guarda digests y reporte de validación, no la construye; (7) evaluar el mismo paquete que se propone publicar. Cualquier fallo devuelve violaciones con entidad/nodo/JSON Pointer; ningún fallback fabrica una release compatible. `pin_release` no valida por sí solo: validación ocurre antes. Dos referencias a un mismo `(kind,id)` que resuelven versiones distintas son conflicto. Clausura incluye entry flows, Understand/slots, templates, tools, refs de nodos, interrupciones/policies, guardas, snapshot y perfil de cada prompt. Una variación posterior invalida el digest evaluado.

| Intención de mejora | Compilación válida | Restricción que se prueba |
|---|---|---|
| Árbol determinista | `Flow`: check→`rule`, ask→`collect`, read→`tool`, effect→`confirm → tool(action_from) → verify`, handoff→`escalate`, terminal→`end`; añadir `respond` para mensajes | IDs únicos, destinos/ramas completos, alcanzabilidad, sin ciclos sin espera, fallo con salida segura; políticas JSON Logic del subconjunto Core |
| Clasificación o decisión Jev | `DecisionModelDef` + nodo `decide`; Agent `understand`/`slots_model` según caso | No lectura `decisions.*` desde rule/escritura; ausencia/calibración baja termina en rama explícita, no acción autorizada |
| Agente LLM de lectura/cálculo | `Agent` con Flow y nodo `agent`, `Prompt`, `ModelProfile`, tools permitidas, max_steps/output_schema | G0-07 solo read/compute; G0-24 catálogo documentado. Salida en facts de origen agent, G0-22: respond/input_view de decide o agent; excepción exacta DRAFT_OUTPUT_SCHEMA→write_draft args.changes. No rule, verify, escritura bancaria o end.output_map |
| Combinación de agentes/flows | Varias entidades Agent/Flow en paquete; plataforma coordina runs y recibe escalamiento | No hay `call_agent` ni grupo nativo. Escalamiento cierra run; episodio enlaza próximo run. `subflow`/`await_approval` existen en schema pero están deshabilitados en baseline; no simularlos como soporte actual. La transferencia entre agentes (`Transfer*`/`RunTransferred`, fila nueva arriba) tampoco se simula como soporte actual: está en rama separada, no en el pin publicado como aprobado |

**Constructor y límites actuales.** El bot constructor es `PrincipalType.builder` sin subject, campos ni bound params de cliente; existe excepción explícita del administrador humano (§27.5), nunca del bot; constructor recibe evidencia agregada/desidentificada. Scouts SQL del motor conservan su lab seguro y no obtienen esos accesos usando identidad builder. Constructor chat y automático requieren Agents distintos (`conversational`/`task`) si se ejecutan en Core. Un flow task no contiene `collect`, `confirm` ni `respond(await:true)`. ADR0019 diseña `write_draft` con `act→verify` sin confirmación y rol constructor exclusivo, pero RiskClass.write_draft, M3, G0-23, AG-02 y BuilderToolExecutor ya existen. Usar act→verify para borradores (§29); constructor task publicado/cableado no viene listo en serve. El transporte simulado respeta estas primitivas/readback y no finge constructor upstream desplegado. La credencial del constructor no hereda rol aprobador del humano. Aprobación/publicación/promoción requieren builder humano aprobador+step_up (`StepUpPrompt`/`StepUpRequested`, fila nueva arriba) y revocación requiere admin+step_up; nuestra automatización prepara, prueba y solicita esas operaciones, sin asumir autopublicación upstream.

**Conformidad del simulador.** `platform-sim` acepta los mismos cuerpos Core fijados, errores de referencias, catálogo de nodos, outcomes y protocolo de escritura. Capacidades pendientes devuelven `unsupported_capability`; no éxito ficticio. `collect.validator(kind=decide)` figura en el tipo pero G0-01 lo rechaza antes de publicar; knowledge_refs de generate no vacío tampoco se exporta como habilitado. Tests de contrato cubren refs no exactas runtime, conflicto de versiones, ramas faltantes, task esperando, tool sin executor, agent intentando escribir, builder con subject, salida agent usada en escritura, readback unavailable y cambios de paquete después de evaluación. `AgentSpec`/`TreeSpec`, si aparecen en una explicación o representación visual, son nombres conceptuales internos y jamás payloads wire.

Cambios en tool/prompt/knowledge producen paquete candidato y reevalúan escenarios afectados. Dataset no ofrece gold semántico de mensajes; casos ES/PT son generados/adjudicados y se etiquetan. Core y proveedores reales Jev/LLM sirven razonamiento del motor; si simulador invoca un modelo, usa purpose/presupuesto separados. Objetos de ejecución, prompts, condiciones y decisiones visibles se registran; no se pretende observar razonamiento privado del modelo.

## 18. Orquestación autónoma y evaluación: algoritmo implementable

```mermaid
flowchart TD
  A[Snapshot o eventos/agenda] --> B[Coalescer + job detect]
  B --> C[Extracto tratado / MetricSpecs]
  C --> D{Calidad y anomalía}
  D -->|no| N[Finding negativo + próxima condición]
  D -->|sí| E[Scout SQL libre + Verifier independiente]
  E --> F{eligible_for_proposal?}
  F -->|no| N
  F -->|sí| G[WorkflowBridge + ValueModel marginal]
  G --> H{Viable?}
  H -->|no| N
  H -->|sí| I[Builder: alternativas + ChangeSpec]
  I --> J[Compile bundle + ScenarioFactory]
  J --> K[Dev tests y adversariales]
  K -->|fallo| L[Revisión nueva, presupuesto/intententos acotados]
  L --> J
  K -->|pasa| CE[Core evaluate con suite exacta]
  CE -->|fail| L
  CE -->|failed_infra| RI[Retry acotado mismo hash y suite]
  RI --> CE
  CE -->|pass no implica mejora| M[Final Pulso sellado una vez por familia]
  M -->|mejora pasa| O[Ambos gates pasan → espera humana → publicar staging]
  M -->|falla o inconcluso| RT[Retirar final y detener familia]
  RT --> N
  O --> P[Outcomes maduros → memoria y nuevos triggers]
  P --> B
```

**Programación y sensores.** `scheduler_tick` compara `SourceSnapshot`/offset, config y `last_complete_window` por sensor. `trigger_key = SHA256(tenant,mission,source_snapshot,config,window,trigger_kind)` deduplica. Un trigger manual usa igual pipeline y sólo añade `requested_by`; no fuerza outcome. Los sensores son MetricSpecs declarativas con `grain, event_time, available_time, numerator_sql, denominator_sql, dimensions, allowed_strata, min_coverage, window, comparator, unit, source_contract_refs`. El scanner ejecuta cada sensor habilitado en las familias de la tabla siguiente; mantiene resultados por celdas en artifact de run y aplica presupuesto por familia. `signal` lleva query digest, conteos, missing y selección de celdas. La detección no es un LLM que «ve» un dashboard: cálculo determinista identifica candidatos; scout LLM investiga libremente el extracto; verifier independiente intenta refutar con ventanas, estratos, negativos y leakage. Un detector propuesto por LLM vive en `candidate`, después `shadow` en ventanas nuevas, y jamás justifica su propia activación.

El catálogo inicial de sensores **cubre todos los frentes sin afirmar que todos sean oportunidades**. Cada métrica exacta es config/schema versionado; si la columna no existe o cobertura falla, publica `unsupported/insufficient_evidence` por familia, no inventa indicador:

| Familia / fuente | Numerador / denominador y comparación inicial | Límite causal y ruta potencial |
|---|---|---|
| Contacto (`call_center_interactions`) | `was_resolved=False` / flag conocido por motivo/canal; espera y duración sólo sobre contactos con valor, mediana/p95 vs mismo canal | No resolución operacional, no fallo probado de IA; routing/árbol sólo si bridge y oracle lo sostienen |
| PQR (`complaints`) | `sla_breached=True` / flag conocido; `first_response_date` presente / PQR creadas; tiempo a primera respuesta sólo entre pobladas | Flag SLA provisto, no plazo legal ni causalidad de contacto; status/triage no promete reducir SLA |
| Transacciones (`transactions`) | status no aprobado / status conocido por tipo/canal/response_code; volumen USD aprobado con `amount_usd` válido | Rechazo puede ser control legítimo; status lookup/explicación no revierte transacción automáticamente |
| Digital (`digital_events`) | frecuencia y secuencias `event_type/action` por sesión/canal/versión, abandono sólo si definición de sesión/cierre válida | No hay flag explícito de error: `event_type` no se llama «fallo técnico» sin taxonomía validada |
| Productos/cartera (`products`,`customers`) | proporción `days_past_due>0` / productos con dato; estados activos por producto/cliente al snapshot | Sin historia de pagos ni causalidad de impago; rutas informativas, no recuperación monetaria afirmada |
| Marketing (`campaign_sends`,`marketing_campaigns`) | delivered/opened/clicked/conversion / flags conocidos, por campaña/canal; costo/valor sólo en moneda respaldada | Conversión sintética descriptiva, no incrementalidad; no USD si moneda no consta |
| Experiencia/operación (`satisfaction_surveys`,`service_agents`,`branches`) | CSAT/NPS sólo respondentes enlazados y tasa de respuesta; carga/duración por agente con contactos enlazados | Comparar agentes ajusta mix/canal/volumen; `avg_csat` snapshot no es gold de cada episodio |
| Plataforma observada (eventos durables + OTel auxiliar) | handoff/unsafe/tool unknown/latencia por capa, recontacto y patrón de resolución humana con denominadores y cobertura | Eventos tardíos/sampled traces no son ausencia de acción; sólo claims de capas observadas; fuente independiente del detector |

El orden en esta tabla no prioriza ganador. En discovery todos los sensores habilitados compiten bajo presupuesto de scan; su orden de ejecución se registra y varía por fairness. `SourceContract` documenta para cada flag su disponibilidad temporal: los resultados posteriores sólo sirven como label retrospectiva y nunca se filtran a decisión previa. La evaluación independiente de un cambio siempre usa oracle de la capacidad afectada, no una correlación visual entre dos tablas.

**Construcción de propuestas.** Para cada oportunidad elegible según el predicado de §29.8, `BridgeBuilder` consulta WorkflowCatalog/capabilities y §16; si falla, conserva `blocking_reasons`. `PortfolioRanker` agrupa por población/objetivo, deduplica lineage, estima valor marginal y toma top-k bajo presupuesto. Builder LLM usa Core externo real, navega libremente SQL/wiki autorizados y devuelve `do_nothing` y alternativas disponibles, `ChangeSpec` tipado y predicciones falsables. Compilador verifica schema/G0/refs/Core capabilities fijadas y policy sandbox; no ofrece nueva autoridad ni knowledge no soportado. Si ninguna alternativa es construible, publica `no_safe_change`. Dos propuestas con mismo base head: perdedora rebase+reevalúa.

**ScenarioFactory y firewall.** `ScenarioCase` fija `{case_id,family_id,origin=source_derived|platform_failure|generated|adversarial,source_refs,decision_cutoff,language,initial_bank_state_ref,customer_messages_ref,allowed_actions,forbidden_actions,expected_goal,oracle_ref,split,seed,sensitivity}`. `OracleSpec` se versiona **antes** de ejecutar candidatos: predicados sobre estado final del simulador/plataforma, receipts, permiso, información comunicada y handoff; define `pass|fail|unsafe|unknown`, no texto libre evaluado por builder. Estado inicial/policy son privados y provienen de fixture generado o fuente válida anterior a cutoff; no se inventa sesión/saldo/autorización del CSV. Agente adversarial interactúa por la misma API de plataforma/simulador, varía idioma/ambigüedad/errores y no ve oracle. Casos/oracles son artefactos cifrados por split; reviewer distinto adjudica gold donde no hay receptor verificable.

El split se sella **por campaña/familia de propuesta**, no por revisión: grupos de cliente, episodio, plantilla y fuente relacionada se asignan enteros a `development`, `validation` o `final_locked` con hash de seed/manifest antes de construir. Variantes adversariales de un caso heredan su split. Builder, scout, memoria recuperable, SQL de desarrollo y feedback granular nunca ven `final_locked`. Una familia que falla final recibe sólo gate agregado (`pass/fail`, métricas agregadas y error de seguridad genérico), no casos ni trazas; la siguiente familia necesita un final independiente sellado antes de iterar. Casos finales gastados quedan `retired`, no vuelven a ser holdout. Gate de acceso se ejecuta en extractor, artifact reader, memory retrieval y API, no sólo en prompt. Un canario sintético de fuga en final debe bloquear release si aparece en output de desarrollo.

**Comparación y gate.** Baseline Pulso seleccionado y candidato (registrar release exacta; base habilitante Core es staging, no necesariamente prod) corren emparejados con mismo caso/seed/policy/banco, pero namespaces físicos separados y reset verificado por digest antes/después. Se randomiza orden de brazos para no confundir calentamiento. `EvaluationPlan` predeclara métrica primaria **por objetivo del bridge**, secundarios, no-inferioridad de seguridad, mínimo de casos por estrato ES/PT/riesgo, presupuesto, CI y umbral; si el set es pequeño, resultado es `insufficient_power`, no «pasa». `unknown` por caída de banco/modelo/oracle se reporta aparte, excluye claim de mejora y dispara retry limitado con mismas versiones. Un solo unsafe confirmado bloquea release; ninguna reducción de costo compensa unsafe. Cada iteración es nuevo `ChangeSpec`/bundle/evaluation; el historial conserva fallos. Tras máximo configurable de intentos o presupuesto, se publica `stopped_no_improvement` con siguiente condición automática, no loop infinito. La tasa de éxito se expresa sobre casos evaluables **y** cobertura evaluable.

BaselineSelectionReceipt se sella antes de construir/evaluar el candidato: regla, capacidad activa anterior a la propuesta o política do_nothing explícita, release/digests, mundo, objetivo y oracle. No elegir después una baseline peor para fabricar mejora. Acciones humanas históricas sin ejecutor reproducible y oracle compartido sólo constituyen comparación descriptiva, no delta emparejado; agente nuevo con floor Core tampoco acredita por sí solo mejora Pulso. Cambio de baseline/release durante campaña invalida el plan y exige nueva campaña, no mezcla resultados.

La diferencia primaria usa un universo predeclarado y el conjunto común de pares evaluables, nunca denominadores independientes por brazo. Se reportan unknown por brazo/estrato, cobertura común y diferencial de missing; EvaluationPlan fija cobertura mínima y tolerancia diferencial antes del run. Rechazo incorrecto del candidato sobre contexto válido es fail, no unknown. Casos desconocidos pueden suspender el claim de mejora aunque la tasa condicional suba; no se imputan como éxito. Abandono legítimo se clasifica mediante oracle predefinido. Tests: candidato falla en casos difíciles y no mejora por excluirlos; selección post hoc de baseline rechazada; reintento de infraestructura conserva caso/versiones sin doble puntuación.

EvaluationPlan exige metric_ref/unidad/dirección, efecto mínimo, método/α/seed/CI, mínimos de pares y grupos/estratos, cobertura mínima común, tolerancia diferencial de unknown, guardrails, split/manifest, baseline receipt y presupuesto. Campos ausentes, denominador cero no contemplado, umbral fuera de rango o unidad incompatible invalidan el plan antes de llamar modelos. No se aplican defaults permisivos de aprobación. Son parámetros configurables/versionados del entorno, no estimaciones de rentabilidad bancaria; S0 materializa fixtures de planes completos e incompletos y su validador.

**Publicación actual, rollout futuro y aprendizaje.** Tras los gates de Pulso y `EvalReport.verdict=pass` del registry, el motor queda `waiting_human_approval` ligado al hash exacto. Un humano autorizado aprueba y publica: publish mueve staging, no prod; promover prod requiere otra acción humana. `PlatformReleasePort` para shadow/canary/cohortes es una extensión futura **no soportada** por registry rev2. El mock actual no inventa sus endpoints ni confirma exposición inexistente. Un experimento opcional de cohortes en banco sandbox se etiqueta `pulso_extension_simulation`, independiente de publicar una release core. Rollback actual exige promover una release anterior activa con humano; luego puede revocarse la defectuosa, nunca mientras prod apunte a ella. El sandbox no prueba impacto live. Detector consume eventos externos y puede contradecir wiki; no usa su propio texto como evidencia de éxito.

## 19. Persistencia, aislamiento, recuperación y operación entre servicios

**Publicación inmutable.** Writer valida schema y refs, canonicaliza JSON, calcula SHA-256 y sube blob cifrado temporal a S3 si aplica. Lee HEAD/hash del objeto; en transacción PG inserta nueva revisión/edges, comprueba lease + tenant + source/config/policy vigentes, mueve `pulso_artifact_heads` con `WHERE head_version=expected`, inserta auditoría y job result; sólo entonces la revisión es visible. Un blob sin referencia PG es huérfano y GC lo elimina tras ventana de seguridad; un blob referenciado sin digest válido bloquea lectura/promotion y alerta. GC enumera refs alcanzables de heads **y** auditoría/retención legal, marca candidatos, espera grace period, vuelve a verificar y borra sólo huérfanos. Restore desde backup restaura PG/S3 coherentes o deja artefacto `unavailable`; aplica tombstones/revocaciones antes de servir.

**Claim, cuota y fallo.** `claim_next` corre en transacción corta: obtiene advisory transaction lock de `(tenant,lane,resource)`, valida cupos activos, selecciona un job `queued` vencido con `FOR UPDATE SKIP LOCKED`, hace reserva condicional en `pulso_quotas`, incrementa `lease_version`, pone `running`/lease/costo reservado y commitea. Scheduler pasa `retry_wait→queued` antes del claim. No mantiene lock durante SQL/modelo. `finish_job` exige lease/head esperados; en la misma transacción persiste artifacts/edges/audit, costo real y `complete`; la reserva de presupuesto permanece como cota conservadora de la ventana. Para cada transición, `append_run_event` bloquea la fila del **job raíz** `run_ref`, incrementa allí `last_event_sequence` e inserta `(run_ref,sequence)` antes del commit; el lock serializa writers del mismo run, no todos los tenants. El evento es durable junto al cambio de estado. Sweeper sólo requeue jobs con lease vencida y no-effect confirmado; si pudo haber efecto externo, deja `waiting_dependency` hasta reconciliación específica por operación (§27), no command-key lookup universal. Índices parciales `(tenant_id,lane,priority DESC,due_at,id) WHERE status='queued'` y `(lease_until) WHERE status='running'`; medir `EXPLAIN ANALYZE`, vacuum/bloat y pool wait. Para fairness scheduler rota lanes por pesos configurados, no confía en ORDER BY global. `dead` requiere razón; retry autorizado como generación nueva no duplica efecto.

**SQL sandbox.** Local: extractor crea derivados tratados con archivos de sólo lectura y manifest; helper launcher rootless del host, iniciado por just dev y único poseedor del socket Podman, recibe grants por transporte privado autenticado e inicia contenedor efímero por run, imagen fijada por digest, red `none`, usuario no-root, fs root readonly, `/tmp` tmpfs limitado, cgroups CPU/RAM/PIDs, seccomp, deadline y output pipe limitado. El broker admite consultas sobre views allowlisted y `CREATE TEMP TABLE/VIEW AS SELECT`; DML sólo sobre objetos scratch creados en esta invocación. Cada petición contiene un único AST; las fuentes originales y sus views no admiten escritura. Deniega `read_csv/read_parquet` a rutas arbitrarias, `ATTACH`, `COPY`, `INSTALL/LOAD`, UDF externas y múltiples sentencias. El contenedor recibe digest/manifest, no path del dataset original ni secret. El broker revalida filas/columnas de salida y agregación mínima antes de enviar al modelo. Cada query deja receipt con digest de SQL tratado, dataset extract digest, costo/bytes/filas, cutoff y truncación. Revocación cancela container y fencea publicación; cleanup borra directorio por run validando path exacto. Tests positivos de CTAS y negativos de modificación de fuente, lectura externa y escape de namespace son obligatorios. Un SQL malicioso no se convierte en escalamiento de host aunque el parser falle: el aislamiento OS es segunda barrera.

AWS: `worker` envía `SandboxRequest{run_id,image_digest,extract_blob_ref,manifest_digest,grant_ref,budget,deadline,callback_ref}` a dispatcher autenticado. Dispatcher lanza **un ECS/Fargate RunTask por run**, no SQL dentro del service worker; pasa `clientToken` estable para idempotencia de lanzamiento y reconcilia por task ARN/`DescribeTasks` si el ack se pierde. La idempotencia de `RunTask` tiene TTL limitado: el ledger `pulso_external_commands` conserva el efecto y evita reemitir a ciegas fuera de esa ventana. El task descarga sólo extracto cifrado con grant S3 acotado, mantiene sesión DuckDB adaptativa mediante mailbox S3 (§29.8), sin egreso general; al cerrar devuelve `SandboxResult{run_id,query_receipts,output_blob_ref,digest,status,usage}` firmado. Worker verifica firma/digest, lease/grant vigentes antes de publicar. Timeout/callback tardío se deduplica por `(run_id,attempt,lease_version)`; limpieza revoca grant y elimina scratch. `infra/terraform/modules/sandbox` define task definition, red, IAM y límites. EC2 demo usa launcher local pero no se toma como prueba de aislamiento AWS.

**Dependencias y deploy.** `control-api/worker` se despliegan por digests separados y leen config por ref; migración expand/contract precede binarios nuevos. Release de capacidad en plataforma es distinto de release de código del motor: ambos tienen receipts/rollback. LocalStack sólo S3; PG y simulador de plataforma son contenedores reales; Jev/LLM externos se usan con permiso/presupuesto, recorded sólo en tests etiquetados. EC2 demo es disposable: Terraform recrea infra; evidencia proviene de blobs/backup etiquetados, no del disco de VM como única copia. Runbook prueba crash/restart/restore y declara RPO/RTO medidos antes de producción. Terraform `plan` no implica `apply`; Git nunca almacena dataset, PII, secrets ni state.

**Divulgación acumulada SQL (U05/U08).** El perfil versionado del extracto distingue `synthetic_authorized`, observaciones individuales autorizadas por propósito y agregados sensibles. Un mínimo de grupo aislado no demuestra privacidad: el broker mantiene presupuesto de consultas/resultados por principal, propósito y extracto, compartido entre sesiones, y rechaza selectores individualizantes y diferencias/solapamientos que puedan revelar grupos pequeños. Si no puede evaluar conservadoramente esa divulgación, sólo admite vistas agregadas previamente aprobadas o bloquea el perfil; no promete privacidad diferencial. Cada rechazo deja reason/receipt sin revelar filas. Tests obligatorios: dos agregados aceptables aisladamente cuya diferencia revela una persona, filtros repetidos, ORDER/LIMIT/proyección y nueva sesión que intenta resetear presupuesto. Este gate precede datos bancarios reales, no impide fixtures sintéticos autorizados.

**Recuperación medible (U25/U28, gate P5).** DeploymentProfile versionado fija objetivos RPO/RTO por entorno, estrategia de backup PG/S3, responsable y runbook. No son garantías hasta medirlos. Antes de aceptar AWS, un restore drill aislado registra objetivo y pérdida/tiempo observados, digests y limitaciones; reconcilia tombstones/revocaciones posteriores al backup antes de habilitar acceso. Prueba blob faltante, snapshots desalineados, leases vencidos y operación enviada sin ACK: unknown reconcilia, nunca se reenvía automáticamente por restaurar. Un drill que exceda objetivo no pasa el gate y requiere corregir estrategia o aprobar una nueva versión explícita del objetivo.

## 20. Visibilidad del motor, API y pruebas de aceptación

**Read model común.** Toda vista/API del motor incluye `tenant_id,projection_revision,as_of,environment,source_kind,validation,status,blocking_reasons[],next_automatic_action,available_commands[]`. `source_kind` distingue `historical_csv`, `enriched_history`, `platform_observed`, `sandbox_evaluated` y `assumption`; ningún consumidor los suma como una misma métrica. Comandos excepcionales llevan `idempotency_key,expected_revision,reason` y rol/grant; 202 = encolado, no completado; 409 trae head/diff tratado; 403 no filtra existencia ajena. SSE `{event_id,entity_ref,projection_revision,kind}` puede duplicarse o llegar fuera de orden; consumidor reconsulta y descarta revisiones viejas. `GET` no mueve heads ni crea memoria. El motor proporciona contratos/read models para la plataforma y una consola **interna de ingeniería** (§25); no construye la consola integral de atención.

| Superficie expuesta a la plataforma | Read model y estado visible | Intervención excepcional | Prueba de contrato |
|---|---|---|---|
| Centro de mando | Jobs/lag, embudo con denominadores, releases, costos observados vs supuestos, incidentes, fuente/config activos | `schedule_run`, pausar reintentos o kill-switch según rol; todo con razón/version | Run vacío y run activo visibles; una métrica sin datos dice `unknown`, no 0 |
| Expediente de oportunidad | Fuente/ventana/población, consultas reproducibles, soporte/contraevidencia, `WorkflowBridge`, rango de valor y grado de enlace | Objetar evidencia, pedir nueva investigación o congelar; no editar resultado histórico | Navegar del hallazgo al CSV agregado, bridge y candidato; `mechanism_proxy` no aparece como ahorro comprobado |
| Cambio propuesto | `ChangeSpec`, diff de bundle, ruta/capa afectada, contrato de skills/tools/knowledge, compatibilidad y fallos de compilación | Experto puede objetar o aportar conocimiento; no construye el cambio paso a paso | Prompt malicioso no concede autoridad; stale head da 409 y nueva evaluación |
| Laboratorio de evaluación | Baseline vs candidato emparejados, cohortes/estratos, oracle receipts, `unknown`, CI/potencia, casos adversariales permitidos | Iniciar dev eval, detener, revisar gate; final sólo por servicio autorizado | No se muestran trazas final locked al builder; caída de oracle nunca cuenta como pass |
| Release y memoria | Estados core draft/candidate/evaluated/approved/published, candidate_hash, base/staging/prod y wiki independiente | Humano requerido para approve/reject/publish/promote/revoke | Hash cambiado invalida aprobación; Core pass no implica mejora; canary unsupported |
| Observabilidad como evidencia | Por run/episodio externo, eventos durables por capa + spans best effort, coverage y correlación | Experto puede señalar interpretación errónea | Collector apagado mantiene eventos; `traces_unavailable`/gap visibles |

**Interacción normal:** el motor corre solo y publica actividad a medida que investiga, escribe memoria, construye/evalúa propuestas y decide continuar o detenerse. La plataforma presenta su expediente; el usuario sólo entra si quiere inspeccionar o recibe `DecisionRequest` por autoridad, contradicción, policy o veto. Aceptar grant no salta gates automáticos. La plataforma es responsable de UX, scroll, accesibilidad y oficina de agentes; nuestro contract test verifica que dispone de estados/razones/diffs/acción siguiente para renderizarlos. Monitor mínimo de demo consume la misma API, sin wizard ni edición de agentes.

**Modelos de error de la API.** `Problem{code,message,correlation_id,retryable,current_ref?,blocking_refs?}` con códigos `source_unavailable`, `quality_gate_failed`, `policy_denied`, `stale_head`, `lease_lost`, `budget_exhausted`, `dependency_unknown`, `oracle_unavailable`, `holdout_forbidden`, `not_evaluable`, `artifact_revoked`. No se devuelve stack/SQL/PII. Eventos de background usan el mismo `code`. Solicitud de rollback es idempotente sólo en Pulso; exige evidencia del alias y humano para promote. Core no ofrece expected_active CAS: sin lector/garantía de alias o ante writer externo concurrente no se promete 409 ni rollback exclusivo; resultado unknown se reconcilia (§27). Los read models se reconstruyen desde tablas/artefactos; cache UI no es verdad.

**Matriz de aceptación del flujo completo.** Los tests aquí son bloqueantes; se escriben rojo antes de implementar su corte y corren con PG/LocalStack/DuckDB/banco sandbox reales, salvo provider grabado en suite determinista. Cada fila define input, salida observable y nivel mínimo, por lo que el equipo no debe inventar éxito por mocks.

| ID / owner | Input y decisión observable | Gate de aceptación y pruebas |
|---|---|---|
| E01 Data | Dataset original + manifest versionado | 13 SourceContracts/golden headers y types, hash original idéntico, quality report de cobertura/completitud diaria/PK/FK, extracto sin PII directa; unit+integración |
| E02 Backend | Dos triggers y worker concurrente | Una generación lógica, nuevo ciclo sucesor con parent, claim/fence/cupo atómico, poll tras NOTIFY perdido, no double effect; integración PG+fault |
| E03 Security/Data | Scout SQL intenta leer raw, otro tenant, final o egress | Denegación por broker **y** contenedor; no mount raw, no red/socket, result disclosure guard, kill/revocación, cleanup; integración Podman+security |
| E04 AI/Data | Métricas en familias múltiples y anomalía inyectada sin nombre `Queja` | Selección por ranking predeclarado, confirmación/refutación independiente, query receipts, temporal availability y quality gates; regresión CSV+property tests |
| E05 Product/AI | Señal contact-unresolved + PQR sin join | Bridge `mechanism_proxy` o `unlinked`, nunca `same_outcome_linked`; ninguna cifra de SLA evitado; golden dataset E2E |
| E06 AI/Backend | Oportunidad viable + dos builders concurrentes | Do-nothing+alternativas, ChangeSpec schema, bundle compilable, CAS único y rebase del perdedor; contract+integración |
| E07 Eval | Mismo caso baseline/candidato con banco real sandbox | Namespace reset comprobado, oracle independiente, pass/fail/unsafe/unknown, split familiar y final sellado; integración+adversarial E2E |
| E08 Eval/Security | Fuga de canario final a memoria/SQL/prompt | Release bloqueado, incidente y fuente del leak auditada; la familia final se retira sin feedback granular; security regression |
| E09 Integración plataforma | Simulador emite normal/ambiguo/ajeno/multi-goal ES/PT y fallos de cada capa | Motor ingiere eventos/trazas con cobertura, detecta patrón y evalúa cambio por contrato; no implementa atención; contract+E2E |
| E10 Backend | Respuesta perdida de create/PUT/evaluate/publish/promote | Reconciliación según operación §27; publish misma key, create/promote sin query_key ficticio; unknown/manual_reconcile visible; crash+fault injection |
| E11 Release | Core pass + Pulso improvement pass, humano ausente, staging concurrente o respuesta perdida | Sin humano no publish; candidate_changed/proposal_stale obliga rebase+reevaluación+aprobación nueva; publish idempotente; promover prod no es canary; chaos+contract (§27) |
| E12 Memory | Segunda corrida tras éxito y luego revocación | Agente explora/reorganiza wiki, publica diff con CAS; tras revocación no se monta en workspace/modelo/release ni tras restore; integración+restore |
| E13 API/visibilidad | Plataforma/simulador consume feed durante tarea en progreso | Read models 403/409/diff, SSE duplicado/stale, estados unknown/coverage gap y redacción; contract API |
| E19 Frontend/Backend debug | Ingeniero abre run atascado sin acceso a shell | Grafo, cronología durable, consultas/model receipts, último error y siguiente wakeup; replay fork no muta original; OTel caído deja eventos; redacción/holdout/tenant; browser E2E + PG fault + load (§25) |
| E14 Infra | Local limpio y AWS plan | `doctor`, stack Podman/LocalStack S3, Terraform fmt/validate/plan, launcher aislado, deploy demo recreable, restore y runbook; CI+smoke |
| E15 Performance | Perfil de carga declarado: hardware, dataset manifest, provider/latency, 1×/3×/10× + scan | Reporte p50/p95/p99, queue lag, PG waits/bloat, slots, costo/1.000 casos; ninguna promesa SLO sin medición; load+chaos |
| E16 O11y/Data | Mismo episodio pasa árbol→IA1→IA2→humano; un span falta y un evento llega tarde | Detección de cuello por capa usa eventos completos; span faltante produce cobertura desconocida, no omisión; late event revisa signal sin mutar pasado; contract+E2E |
| E17 Integración modelos externos | DecisionModelDef/decide con Jev Choice/Score y LLM estructurado reales, provider lento y fallback prohibido | Receipts con modelo/ruta/costo, schema validado, presupuesto atómico; no fallback cross-policy; smoke live + contract recorded |
| E18 Infra/CD | Engine publica manifest, infra plan/apply staging aprobado | Imágenes API/worker/Core separadas, OIDC sin keys, migración/smoke/rollback; simulado local + smoke AWS staging |

**Fuente completa no equivale a día completo.** `SourceSnapshot` contiene por tabla/partición `row_count,first_event_at,last_event_at,file_digest,header_digest,ingested_at,quality_status` y calendario esperado de archivos; una fecha del nombre del path no valida todos los eventos dentro. El cutoff de `DiscoveryConfig` usa sólo días completos según `SourceContract` y disponibilidad de fuente requerida, con lag permitido versionado. Duplicado de PK divergente bloquea sólo el slice dependiente y conserva finding; `campaign_sends` y encuestas pueden ser parciales sin bloquear métricas de contactos. El manifest y sus transforms quedan fijados por digest en cada run; un query receipt que no los cite es inválido.

**Criterio de salida honesto.** E2E requiere `snapshot/eventos→detección no dirigida→verificación→bridge→ChangeSpec→EntityDraft[]→draft/freeze→EvalSuite y gate Pulso→evaluated→espera humana visible→approve/publish mock→ReleaseDetail staging→eventos independientes→wiki→segunda corrida`. Incluye negativos y fallos. Jev/LLM reales en smoke controlado; recorded sólo prueba determinismo. Sin humano el éxito autónomo es candidato evaluado listo para decisión, no release publicada. Canary ficticio o UI no acreditan compatibilidad.

### 20.1 API de producto implementable: panorama, expediente, prueba y decisión

Estas rutas son de **Pulso**, bajo `/api/v1/evolution`, no endpoints Core ni atención bancaria. Se implementan en Control API existente; plataforma consume sus contratos y construye las pantallas de `design`. Debug usa proyecciones más técnicas bajo su propio scope, no un permiso universal para raw. DTOs y fixtures viven en `contracts/product/`, OpenAPI generado y pruebas N/N−1 en U07/U24; comandos e integración Registry en U21. No hay tabla durable por pantalla.

**Envelope de lectura:** campos comunes de §20 más `schema_version`, `entity_ref`, `links` autorizados y `coverage`. Colecciones usan `items,next_cursor` opaco y máximo 100 configurable; filtros `environment,source_kind,status,from,to` y dominio/idioma sólo cuando el contrato los soporta. Query desconocida falla 400, no filtro silencioso. `as_of` es freshness de la proyección, no disponibilidad universal; 404 no revela objetos de otro tenant. El catálogo disponible permite deshabilitar controles sin inventar éxito.

| Método/ruta relativa | DTO y consumer de producto | Contrato de comportamiento |
|---|---|---|
| `GET /capabilities` | `CapabilityAvailability`: operación/kinds/entornos admitidos, provider/version, estado/reason | `available\|simulated\|unsupported\|dependency_blocked`; autoría ToolDef no demuestra executor; canary upstream unsupported se muestra explícito |
| `GET /overview` | `OverviewProjection`: actividad, métricas, oportunidades priorizadas y dependencias | Panorama muestra investigación/iteración en curso, no sólo resultados terminados; fuentes y periodos no mezclados |
| `GET /opportunities` y `/opportunities/{id}` | `OpportunityProjection`: problema, population/window, soporte/contraevidencia, bridge, alternativas, supuestos, rango valor y refs a candidatos | Abrir tema no dispara investigación ni cambia prioridad; refs sólo a evidencia permitida |
| `GET /proposals/{id}` | `ProposalProjection`: ChangeSpec, candidate/hash, diff, artefactos, affected_consumers, estado/gates y paso siguiente | «Agentes» puede agrupar Flow/Agent/DecisionModel/Tool/context sin convertir todo a Agent. Refs de consumers derivadas de closure/digest; stale/incompleta impide declarar cambio seguro |
| `GET /proposals/{id}/comparison` | `ComparisonProjection`: base/candidato, muestras dev autorizadas, outcomes/efectos/tiempos y aggregates independientes | No incluye detalle de final_locked para builder/expert genérico; 5 ejemplos no son toda la suite. Otra policy o denominador marca no comparable |
| `GET /proposals/{id}/readiness` | `ReleaseReadiness`: compilation, policy, evaluation, improvement, authority, published_alias, activation_ack, exposure | Gates, aprobación, publicación y activación separados. `exposure` sólo si plataforma lo soporta y receipt confirma; nunca derivado del selector 10/50/100 |
| `GET /runs/{id}/activity` | `ActivityProjection`: sequence, stage, estado, reason, evidencia refs y next wakeup/action | Progreso de detección/verificación/builder/trials/memoria visible con reasoning summary sustentado, no chain-of-thought privada; SSE existente notifica refs y consumidor reconsulta. Evidencia originada en Agent Core anota su nivel (`engine_event`\|`outbound_event`, §24) junto al ref, nunca mezclada sin distinguir |
| `POST /opportunities/{id}/feedback` | `ExpertFeedbackRequest`: expected_revision, type `support\|challenge\|knowledge\|request_review`, texto tratado y evidence_refs autorizadas | Artefacto append-only con actor/config/ref; no edita el finding. Contradicción agenda reverify sucesor con ref; conocimiento nuevo pasa seguridad/provenance y no se promueve a policy por opinión |
| `POST /proposals/{id}/trials` | `TrialRequest`: candidate_hash, dev scenario/fixture_ref o input tratado, config_ref y budget_ref | Dev sandbox independiente, nunca final_locked. Agente adversarial real sólo dentro de grants; input no confiable no da permisos. Trial es job async con receipts de resultado |
| `GET /decisions` y `/decisions/{id}` | `DecisionRequestProjection`: type, target hash/revision, actor roles permitidos, opciones, rationale/evidence refs, deadline y estado | Lista de excepciones, no wizard; distinguir approval de release de ayuda por evidencia/dependencia. No contiene autoridad de aprobar dinero |
| `POST /decisions/{id}/responses` | `DecisionResponseRequest`: expected_revision, option, reason, evidence_refs | Validar rol/grant, vencimiento, candidate/config actuales y policy; approve/reject sólo para esa propuesta/hash. Cumplir Core JWS y G1 local de separación autor/aprobador cuando policy lo requiere; Core no lo garantiza por sí solo |
| `GET /commands/{kind}/{id}` | `CommandStatus`: accepted/running/succeeded/failed/unknown, receipt_ref, resulting_ref, error y próximo reconcile | Recargar tras timeout consulta status; unknown conserva efecto potencial. Aceptación no acredita publicación |

**Comandos:** header `Idempotency-Key` y body `expected_revision,reason` donde muta; actor/tenant se obtienen del principal verificado, no del body. Tx PG valida/persiste artefacto y encola job antes de 202 `{command_ref,status_url,entity_ref}`; `pulso_external_commands` representa operaciones externas y jobs/artifacts los trabajos internos, no tabla adicional commands. Clave repetida misma intención retorna status existente; payload distinto 409. Para una respuesta de decisión, consumir mediante CAS y probar dos respuestas concurrentes; una sola transición local, efecto externo unknown reconciliado según §27. 401 no autenticado, 403 scope, 409 stale/conflicto, 422 input/operation inválida, 429 quota con retry, 503 dependencia. No garantizar atomicidad distribuida con Registry.

**DecisionRequest:** `type=release_authorization|evidence_help|dependency_authorization`; las dos últimas sólo `provide_feedback|decline`, no pueden activar permisos/policy. La primera ofrece opciones permitidas por operación upstream (`approve|approve_with_loosening|reject|publish|promote|revoke` cuando disponibles; `approve_with_loosening` sólo si el reporte nativo trae `yardstick_changes` y fija `accept_yardstick_loosened=true`, §31.7.2), cada solicitud fija operación/target y nunca presenta approve como publish implícito. Estado `pending|responded|expired|superseded`, deadline configurable, reviewer y respuesta con digest. Vencimiento no aprueba por silencio: detiene únicamente la acción dependiente y agenda reminder con dedup, sin frenar otros runs. «Ahora no»/cerrar panel es estado local de UI; snooze personal opcional de plataforma cambia notificaciones, no el motor. Pausa/cancelación exigen comandos técnicos autorizados distintos. Prueba humana del sandbox es ayuda opcional, no requisito universal para toda evolución.

**Identidad de consumidor:** JWT de plataforma validado en API con issuer/audience allowlisted, JWKS/algoritmos fijados, exp/nbf, subject y tenant/grants verificados; mapping de roles→scopes versionado, no confiar en selector de rol. Cliente bancario no tiene scopes evolution. Scopes mínimos `evolution:read`, `evolution:feedback`, `evolution:trial`, `evolution:decision`, `evolution:operate`, `evolution:debug`; autorización por objeto/purpose y partición también en links/export/blob/download. Token de sesión plataforma no es firma Core: el worker Rust obtiene por `HumanAuthorizationPort` el JWS del humano autorizado para el target/operación exactos, no fabrica identidad humana (el bridge sólo emite la credencial del bot, CAP-33). Login/SSO/MFA son externos, fixtures locales simulan claims verificados y prueban issuer/aud/expiry/tenant incorrectos y revocación. No construir otro IdP ni almacenar password/OTP.

**Métricas:** `MetricProjection{metric_ref,value,unit,numerator,denominator,population,window,source_kind,quality,formula_ref,assumption_refs,fx_ref?,uncertainty?,comparison_ref?}`; desconocido es null+reason, nunca cero. Grouping árbol/AI/humano es presentación declarada; conservar clasificador fuera de cierres y AI1/AI2 diferenciados en detalle, sin double-count de mitigación+handoff. Resultado correcto puede ser handoff según policy. Costos/valor comparativo USD con FX/fecha/fuente; límites bancarios mantienen moneda nativa/policy exacta. Readiness «0 fallos/n» no promete seguridad absoluta. Trial datasets/status no entran a KPI observado.

**Tests bloqueantes de este corte:** U07 contrato/routing/paginación, issuer/audience/tenant, 202/status/retry/revision; U24 flujo panorama→tema→propuesta→comparison→trial→decisión con estados activos/unknown/unsupported; U21 respuesta concurrente/expiry/hash changed/four-eyes y fallo Registry; U20/U27 trial muta sólo sandbox, adversarial input no filtra datos, no fuga de final y no contaminación KPI; U29/U30 requested_reply/cierre/mitigación/métricas denominadas; U33 feedback contradice memoria y reverify sin reescribirla. Fixtures sólo acreditan representación; integración exige API/PG/worker/Core/sandbox reales y lectura del receipt. UI scroll/keyboard son responsabilidad plataforma y pruebas contractuales habilitan los estados necesarios; consola debug verifica su propio E2E.

### 20.2 Precisiones wire y seguridad de la ejecución asíncrona

**Integridad de presentación y evidencia (U07/U24/U32).** Una nota es texto UTF-8 tratado con límite versionado, no objeto serializado implícitamente; schema rechaza tipos incorrectos y UI no muestra `[object Object]`, HTML ejecutable ni payload raw. El expediente conserva la evidencia conocida al solicitar la decisión; verificaciones posteriores aparecen como nuevos eventos con timestamp/provenance, nunca se hacen pasar por evidencia anterior. El dispatch revalida la condición vigente aunque la proyección muestre evidencia histórica. Tests contract-consumer y UI: nota vacía/texto/objeto inválido/XSS; evidencia posterior a solicitud claramente identificada, reloj/orden discrepante visible, sin atribuir identidad ya verificada al instante anterior. La cronología inconsistente de un fixture no modifica clocks de producción.

**Continuidad de reautenticación (U07/U21).** El challenge externo se vincula a CommandRef, decision_ref, actor_ref, target/revision y operation; CommandStatus sólo expone esa referencia autorizada y expiry, nunca credenciales. Reanudar el comando es idempotente por CAS de su revisión, sin crear otra DecisionResponse. Se rechazan callbacks duplicados, challenges consumidos/expirados, comandos desconocidos/terminales, actor distinto, target stale o permiso revocado; un callback duplicado puede devolver el recibo previo, pero nunca adquirir otra firma ni repetir dispatch. Se revalidan todas las condiciones justo antes de enviar. Unknown obliga a reconciliar antes de cualquier reenvío. Tests: expiración en cola→espera→step-up→un dispatch; replay/cross-actor, cambio de target, revocación durante step-up y crash entre acquire/dispatch sin token durable. Sin puerto externo compatible se conserva dependency_blocked.

Rutas adicionales de trials: `POST /trials/{id}/turns` recibe input tratado, expected_revision y header idempotente; sólo permite trial dev conversacional abierto y acceso del actor al sandbox. Devuelve CommandRef de turno y status_url; reducer actualiza TrialProjection con secuencia, resultados y receipts sin convertir el trial en fuente de producción. Trial cerrado, vencido o revocado rechaza nuevo turno; POST concurrente con misma revisión deja un turno aceptado y otro 409, retry mismo key devuelve el anterior. `GET /trials/{id}` es readback del conjunto.

Esta sección fija las precisiones de §20.1; fixtures/schemas ejecutables se construyen por TDD en U07/U21, no se afirman existentes en este workspace de planificación. `Idempotency-Key` es autoridad wire en API producto; `idempotency_key` se deriva internamente, el body no acepta una segunda clave. `expected_revision` siempre es revisión de dominio de la entidad mutable indicada por ruta, nunca projection_revision ni timestamp. OpenAPI distingue opportunity revision para feedback, candidate revision/hash para trial y decision revision para respuesta. Una proyección atrasada con dominio vigente no causa 409 artificial.

**CommandRef y lookup:** `{kind:job|external_command,id}` referencia owner existente. URL `GET /commands/{kind}/{id}` es la forma canónica del status_url de §20.1; rechazar kind desconocido y validar tenant/actor. Job queued/deferred/retry_wait/waiting_dependency → accepted con substatus/reason/next wakeup; running → running; complete → succeeded sólo con result receipt; dead/failed/superseded → failed; efecto externo desconocido → unknown con reconcile_ref, aunque el job termine. Cancelled es failed con code cancelled, no success. Ledger normativo §15: prepared→accepted, sent→running, confirmed→succeeded, rejected→failed, unknown→unknown; reconciled deriva succeeded/failed sólo de receipt terminal comprobado, sin él permanece unknown. El comando termina por su operación, no por todo el árbol de jobs; reverify devuelve resulting_ref al sucesor de investigación. No añadir tabla commands ni reconstruir resultado desde mensaje de log.

**Trials y lectura de resultados:** `TrialRequest` tiene exactamente uno entre fixture_ref dev autorizado o input tratado, y fija candidate_hash, candidate revision, config_ref, provider_profile_ref y presupuesto. Harness crea TrialPlan inmutable con oracle/grant/source/seed cuando aplicable; no accede final_locked. `GET /trials/{id}` devuelve `TrialProjection{trial_ref,plan_ref,candidate_hash,environment,stage,status,scenario_ref,conversation_ref?,action_receipts[],effects[],oracle_result?,cost_receipt?,limitations[],result_links}` más envelope. GET de conversación/evidencia usa los links autorizados de detalle, jamás raw público. Estado sin oracle es pending/unknown/failure, no pass. Continuar chat crea turno/job referenciado al mismo trial sandbox y CAS revision; no reutiliza sesión de otro usuario ni escribe historia productiva. E2E headless de U24 verifica enviar→status→resultado y permisos; no construye la UI F8.

**Target de decisión discriminado:** approve/reject/publish → `{kind:proposal,proposal_ref,proposal_rev,candidate_hash,base_release_ref}`; promote/revoke → `{kind:release,release_ref,agent_ref,release_digest,alias?,alias_observed_ref?}`. Operación fija opciones válidas; publish exige aprobación vigente. agent_ref se verifica contra ReleaseDetail.agent_id para la ruta de alias; release_digest es digest interno Pulso del manifest/closure/receipt fijados, no un release_hash del wire Core. Alias observado es evidencia/precondición Pulso, no CAS inexistente Core. Writer externo o ACK perdido mantiene unknown hasta reconciliar. `responded` significa respuesta durable, no éxito externo; linked command conserva su estado. Expiry sólo cambia pending por CAS; no expira/reabre responded para duplicar operación. Test sweeper+respuesta concurrente/timeout/dobleclick conserva una decisión y un comando lógico.

**HumanAuthorizationPort — externo, no nuevo IdP:** firma única (idéntica en §31.8.1): `prepare(actor_ref, target, operation, decision_ref) → AuthorizationTicket{challenge_ref, expiry, authority_ref}` sin credenciales (`target` es el target discriminado de arriba: para approve/reject/publish `{proposal_ref, proposal_rev, candidate_hash, base_release_ref}`); `acquire(challenge_ref, verified_step_up) → JWS` en memoria, válido para el método Core concreto (`challenge_ref` = `AuthorizationTicket.challenge_ref`). El worker Rust despacha approve/publish/promote con ese JWS en memoria. El emisor/firma humana es de plataforma autorizada; Pulso no suplanta sub ni firma por un actor que sólo hizo click. DecisionResponse se guarda como intención auditada y job; inmediatamente antes del dispatch se verifican grant/revocación, target/rev, expiry, operación y firma. JWS/OTP/tokens jamás en PG/S3/artefactos/logs/colas; sólo refs/digests no reversibles de recibos y expiry. Si emisor permite referencia delegada, ésta debe ser acotada/revocable y verificada por puerto externo, no asumir soporte. Si no puede reemitir sin presencia humana o expiró step-up antes de dispatch, comando espera `waiting_human_reauthentication` y pide nueva autenticación para la misma intención; no repite efecto ni inventa aprobación nueva. Caída tras envío conserva unknown y reconcilia antes de solicitar reenvío. El doble de identidad local prueba TTL, actor cambiado, clave rotada, revocación y cero persistencia de token; integración real queda dependency_blocked hasta puerto disponible.

**Scopes y admission:** debug_viewer requiere `evolution:debug`+grant de lectura técnica por objeto; debug_operator exige además `evolution:operate` y grant específico de comando; ninguno implica builder/admin de Registry. JWT válido no prueba ausencia de revocación: overlay/grant store se consulta en fronteras; estado indisponible falla cerrado para mutaciones/egreso, lecturas sensibles y export. Feedback/input de trial se limita por tamaño, valida refs/tenant/partition, trata PII y rechaza final refs antes de persistir/encolar; payload malicioso sigue siendo dato, audit sólo conserva código/ref tratado. Umbral de retención local no puede ampliar política externa ni ser modificado por feedback.

**Disponibilidad temporal y procedencia:** plataforma discovery usa occurred_at y received_at/availability_at≤cutoff, no sólo fecha ocurrida; evento tardío se conserva como nueva evidencia sin reescribir snapshot anterior. E0 sin recepción sigue el reloj de replay y disponibilidad por evento/campo de §§28.2/29.8 con supuesto de lag etiquetado; snapshot de bytes completo no habilita datos futuros ni simula received_at real. MetricProjection añade factor_provenance por factor de fórmula para separar población observada, tiempo medido, costo supuesto y FX; source_kind agregado no implica que todos factores sean observados. Hold de retención necesita authority receipt/target/expiry verificados; flag del administrador o texto fixture no prolonga datos por sí solo.

**Pruebas añadidas:** U07 mapping de estados/domain revision/admission/cross-tenant; U21 autorización expira mientras espera/reautenticación/reconciliación y token no persistido; U20/U27 TrialPlan oneOf/turn concurrente/resultado sin oracle; U29 cutoff recibido tarde/sequence ausente; U30 factor provenance; U33 purge/hold inválido. Las pruebas de UI producto son contract-consumer/headless, distintas del browser E2E de la consola debug.

## 21. Memoria operativa: wiki libre dentro de un perímetro gobernado

Adoptamos la idea central de [Karpathy, LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): fuentes originales inmutables, una wiki interconectada que el agente mantiene, y convenciones para ingesta/consulta/lint. **Nuestra adaptación**, no una prescripción del autor, añade tenant, propósito, retención, PII, particiones de evaluación, aprobación de publicación y versionado inmutable. No reducimos memoria a una fila por claim ni a un packet top-k que decide de antemano qué puede leer el agente.

```text
workspace de un run (desechable)
  sources/             # extractos/evidencia autorizados, readonly, con manifest
  wiki/                # copia writable del head de memoria fijado al iniciar
    index.md           # mapa temático mantenido por el agente
    topics/...         # síntesis, conexiones, hipótesis, procedimientos, fallos
    entities/...       # rutas, capas, herramientas, oportunidades, patrones
    log.md             # qué cambió y por qué, append-only dentro del snapshot
  scratch/             # SQL, notas y borradores, nunca servidos como memoria
```

**Lectura libre:** tras aplicar el perímetro `(tenant,purpose,cutoff,policy,information_partition)` al montar `sources/` y `wiki/`, el agente decide qué leer, cruzar y buscar, en cualquier orden, sin un catálogo de preguntas predefinidas ni top-k obligatorio. Libertad semántica no implica acceso directo del proceso LLM al filesystem: en Agent Core el executor general `lab_read`/`lab_query`/`lab_write_scratch` (§29.4) transporta navegación/SQL/scratch bajo la sesión autorizada; no creamos una tool de negocio por cada lectura o tabla. El broker aplica permisos y límites, no selecciona la hipótesis. FTS es ayuda, no filtro obligatorio. Páginas pueden contener resultados apoyados, hipótesis, preguntas, contradicciones y lecciones; citas usan SourceRef/artifact refs. Enlaces rotos y afirmaciones sin soporte son findings de lint, no motivo para impedir creatividad en scratch.

**Escritura libre, publicación controlada:** el agente edita, crea y reorganiza páginas en `wiki/` durante investigación, evaluación o mantenimiento. Esas ediciones no afectan a otros runs. `publish_memory(base_head,diff_digest,manifest)` valida rutas/symlinks, tamaño, PII/secretos, final holdout, referencias existentes y vigentes, tenant/purpose, links/índice/log y la distinción `observado|inferido|hipótesis|sandbox`; un reviewer automático puede señalar contradicciones y pedir otra iteración. Si pasa, se guarda snapshot/diff cifrado por digest en S3 y `pulso_artifacts(kind=memory_wiki)` más `pulso_artifact_heads(scope=memory_index/<tenant>/<purpose>/<world>/<campaign>/<protocol>/<partition>)` cambian por CAS. Dos agentes con el mismo head: uno publica; otro rebasea su diff en una copia nueva, vuelve a lint y publica revisión sucesora. No se modifica una revisión ya publicada. `MemoryUseReceipt` registra head fijado, páginas leídas, páginas cambiadas y decisiones que las citaron; no presupone que leer una página causó mejora.

**Olvido deliberado:** no bajamos la verdad de una página sólo por desuso. Un `memory_maintenance` espontáneo/periodico hace lint de contradicciones, fuentes corregidas, capacidades/release reemplazados, páginas huérfanas y enlaces rotos; reescribe síntesis, archiva hipótesis refutadas o retira páginas obsoletas, conservando su revisión anterior mientras retención lo permita. Revocación de fuente/permiso pone tombstone en control **antes** de permitir lecturas nuevas, bloquea heads afectados y dispara nueva wiki depurada; restauración de backup aplica tombstones antes de servir. Purga física sigue política de retención/privacidad; log/auditoría lícita puede conservar el hecho de la revisión sin payload sensible. Resultado sandbox nunca se eleva a outcome bancario live al reescribir una página.

**Pruebas de memoria:** un agente crea una conexión no prevista entre dos fuentes permitidas y la conserva en segunda corrida; otra fuente contradice esa síntesis y el lint exige revisión; dos writers concurrentes rebasean sin perder páginas; fuente revocada desaparece de wiki montada, prompt, búsqueda, snapshots nuevos y restore; final locked no se monta; página con PII o enlace a otro tenant no publica; wiki inaccesible deja run `degraded_without_memory` visible, no «sin problemas»; ablation evalúa si usar una wiki anterior cambia la propuesta, sin convertir ese resultado en verdad por sí mismo.

## 22. Recorrido de referencia y fronteras de ownership para implementar

Este recorrido es un **test de contrato**, no un guion hardcodeado de producción ni promesa de que la primera corrida elegirá quejas. La suite de fixture inyecta un aumento genérico de no resolución en una categoría renombrable; la corrida con CSV original selecciona por ranking sellado y puede elegir otro frente. Los mismos puertos, schemas y gates se usan en ambos:

| Paso | Entrada → salida durable | Owner y fallo que no se disfraza |
|---|---|---|
| 1. Ingesta | `SourceSnapshot{manifest_digest,source_contract_refs,cutoff,quality_ref}` → artifact y trigger key | `adapters/source` lee CSV; header/PK/tiempo inválido publica finding y no modifica origen |
| 2. Agenda | `schedule_run(snapshot_ref,config_ref,trigger_key)` → `pulso_jobs detect` | `app/scheduler` deduplica; mismo key retorna job existente, nueva ventana crea generación sucesora |
| 3. Scan | MetricSpecs → `signal{cell,numerator,denominator,comparison,query_receipts,validation}` | `app/detection` calcula; cobertura insuficiente produce `insufficient_evidence`, no número inventado |
| 4. Investigación | Signal + extracto tratado + wiki montada → `opportunity{support,counter,claim,status}` | `app/investigation` y verifier separado; LLM real vía Core externo explora, SQL/quality/ablation deciden corroboración |
| 5. Bridge/valor | Opportunity + WorkflowCatalog → `WorkflowBridge{target_outcome,mechanism,link_grade}` + ValueModel rango | `app/portfolio`; no join contacto–PQR implica proxy/unlinked, nunca same-outcome por texto parecido |
| 6. Construcción | Evidencia + wiki + bundle externo activo → propuesta, `ChangeSpec`, bundle candidato | `app/builder` usa Core externo; compiler rechaza refs/policy rotas, CAS protege candidato |
| 7. Escenarios | Bridge + fuente válida + observaciones externas + simulador → `ScenarioSet`/`OracleSpec` sellados | `app/eval_factory`; no sesión/saldo inventado como histórico; gold inaccesible para el builder |
| 8. Evaluación | Baseline/candidato emparejados → `Evaluation{results,unknown,unsafe,gate}` | `app/evaluator`; final_locked una vez por familia, unsafe/unknown no pasa |
| 9. Registry/publicación | Proposal congelada + EvalReport pass + gate Pulso → waiting_human_approval → approve/publish firmados → ReleaseDetail staging | `app/registry_adapter`; sólo publish HTTP tiene key; servicio/BuilderToolExecutor tienen keys de borrador; respuesta perdida aplica matriz §27, no get_by_command_key ficticio |
| 10. Observación | Plataforma/simulador emite attempts por capa, efectos y outcomes | `app/ingest`; dedup/cobertura/correlación; unknown se reconcilia, no se afirma resolución |
| 11. Aprendizaje | Outcomes maduros + eval/release → wiki nueva y trigger | `app/memory`; contradicción/revocación revisa u olvida, no autojustifica detector |

`core` posee tipos/validadores/reducers; `app` casos de uso/transacciones; `adapters` PG/S3/DuckDB/plataforma; `control-api` y `worker` cablean procesos; Core externo posee ejecución y credenciales de modelos. Control API no escribe artifacts saltando app; worker no activa capacidades saltando adaptador registry/comandos externos (§27). La consola de plataforma consume HTTP/SSE, no PG/JSONB interno. Eventos durables externos son contrato de entrada; pérdida de OTel reduce diagnóstico, no borra hechos de atención.

**Fixtures wire mínimos que deberán vivir en Git antes de S2:** `source_snapshot_valid/invalid`, `platform_observation_complete/gap/late`, `signal_corroborated/refuted`, `workflow_bridge_same_outcome/proxy/unlinked`, `change_spec_valid/stale`, `tree_valid/cycle`, `scenario_normal/ambiguous/unsafe/unknown`, `evaluation_pass/fail/insufficient_power`, `release_ack_confirmed/unknown`, `memory_wiki_valid/contradicted/revoked`, `read_model_running/stale/restricted`. Cada fixture valida JSON Schema desde Rust, `serde` round-trip y N/N−1; unknown enum/version falla cerrado si cambia decisión. Esto es trabajo S0–S2, no licencia para inventar campos ad hoc.

## 23. Integración de modelos externos: Jev y LLM reales bajo una política

Core ejecuta Jev y LLM como dos puertos de dominio distintos, no como un servicio único nombrado "DecisionService". Jev vive en el módulo interno `agent_core.decision` ("M5"): un `DecisionProvider` (Protocol, definido en `agent_core/decision/types.py`) con implementaciones concretas en `agent_core/decision/providers/` — `jev.py`, `jev_http.py` (Jev como proceso/HTTP externo), `classifier.py`, `llm_structured.py` y `rule.py`. No existe un tipo "JevProvider" ni un servicio llamado "DecisionService"; el nombre correcto a citar en diseño e integración es decision (M5) + `DecisionProvider`, con la implementación concreta (`jev`, `jev_http`, etc.) declarada explícitamente en cada punto donde se invoca. LLM real se ejecuta por `LLMAgentPort`/`OpenAICompatGateway`, confirmados tal cual en `agent_core/adapters/llm/` (ADR 0016): `AgentPort` es el puerto de dominio ("M0") que `LLMAgentPort` entrega; esta parte no cambia respecto al diseño previo. No construimos gateway ni proxy propio para ninguno de los dos.

`ModelInvocation`/`ModelReceipt` son DTO **internos de Pulso**, no nombres ni endpoints que agent-core exponga. agent-core modela gasto y telemetría de uso con sus propios tipos de dominio — `LlmUsage` (evento, `agent_core/domain/events.py`), `Budgets`/`BudgetsUsed` (`agent_core/domain/entities.py` y `agent_core/domain/state.py`) y el puerto `CostCounters` (`agent_core/ports/costs.py`) —, y el costo exacto se calcula en `agent_core/adapters/llm/cost.py` con `Decimal` y tarifa de `ModelProfile`. Pulso debe mapear su propio `ModelInvocation`/`ModelReceipt` contra esos tipos de agent-core al consumirlos, nunca asumir que agent-core habla en términos de "ModelInvocation" o "ModelReceipt"; el mapeo es responsabilidad del adaptador de Pulso, documentado donde se traduzca transporte (ver §27.1). PulsoModelProfile se mapea al perfil Core y fija tratamiento, modelos, presupuesto y deadline. La capacidad externa faltante o sin enforcement verificable bloquea la ejecución, no autoriza construir otro servicio.

| Contrato interno (Pulso) | Campos mínimos | Comportamiento/fallo |
|---|---|---|
| `ModelInvocation` | `request_id,tenant_id,run_ref,purpose,model_profile_ref,sensitivity,information_partition,policy_ref,input_digest,treated_payload_or_ref,output_schema_ref?,typed_question?,max_tokens,deadline,idempotency_key,trace_id` | `kind=llm_generate`; Jev se invoca por `decision` (M5) vía el `DecisionProvider` configurado (`jev`/`jev_http`/`classifier`/`llm_structured`/`rule`) en Core, no mediante esta invocación; rechazo previo si purpose/modelo/región/retención no autorizados o presupuesto no reservado |
| `ModelReceipt` | `request_id,provider,model_id,model_version_or_alias,resolved_route,provider_request_id,tenant_id,job_id,grant_ref,attempt,input_commitment,policy_ref,capability_ref,evidence_commitment,output_digest,usage_tokens,estimated_and_reported_usd,latency_ms,output_validation,status,trace_id` | `input_commitment` hashea el input tratado y sus refs autorizadas; el receipt se valida contra ese binding, no sólo por scope. Al reconciliar, `usage_tokens`/`estimated_and_reported_usd` se derivan mapeando el `LlmUsage`/`CostCounters` reportado por Core, no se inventan campos nuevos en Core. `status=ok\|invalid_output\|timeout\|rate_limited\|provider_error\|policy_denied\|budget_exhausted\|unknown`; jamás registra prompt/texto en logs |
| `PulsoModelProfile` versionado | proveedor/modelo permitidos, región/retención, capacidades verificadas (`typed_question`,`json_schema`,`stream`), deadline, retries, fallback allowlist, costo límite | fallback a otro proveedor sólo si mismo propósito/tratamiento/región y nueva reserva de presupuesto; ruta real queda en receipt |

El consumidor valida grant vigente y payload tratado, reserva cuota conservadora antes de dispatch vía Core y persiste `ModelReceipt` tratado al reconciliar, mapeando desde `LlmUsage`/`Budgets`/`BudgetsUsed`/`CostCounters` de agent-core. Core configura credenciales fuera de Git. Timeout posterior al envío conserva unknown/reserva hasta readback; no se asume idempotencia del proveedor. Retries/fallback requieren política explícita y presupuesto. Tests deterministas de consumidor cubren schema/uso/costo desconocido y errores; smoke live separado con datos permitidos. No hay endpoint proxy propio.

La frontera de modelos pertenece al ecosistema externo. U10 verifica endpoint/perfil/capacidades y observa receipts vía Core; no despliega otro servicio. Si existe gateway externo se acuerda contrato antes de integrarlo; su ausencia no autoriza construirlo.

## 24. Plataforma observada como fuente de detección y visibilidad del motor

**Contrato upstream fijado.** Esta sección distingue contratos publicados en `agent-core` SHA `86a767474042a566a0dbd6ed23588959f27ebdb3` de adaptadores de Pulso que todavía debemos construir/acordar. `EngineEvent` sigue siendo la fuente durable nativa de auditoría: `{event_id,run_id,turn_id?,session_id?,release,ts,seq?,prev_hash?,hash?,type,payload}` (`contracts/schemas/EngineEvent.json`). El evento encadenado tiene `seq` contiguo **por run, empezando en 0**, no un cursor global. Verificamos original con canonicalización/schema fijados dentro del adaptador confiable; sólo conservamos bytes originales si policy autoriza almacenamiento cifrado/restringido; normalizar o agregar campos sobre el objeto firmado alteraría su hash. Guardamos el evento upstream separado de su proyección `InteractionObservation` y de la metadata de transporte Pulso.

**Novedad central: catálogo cerrado de eventos salientes públicos (`agent_core.outbound`).** Desde el 2026-10-02 el motor publica su propio subsistema de proyección pública — ADR nuevo, explícitamente **fuera de la numeración M0–M12**, descrito en `docs/specs/2026-10-02-eventos-salientes-design.md` (repo `agent-core`, estado "borrador implementado, pendiente de revisión"). Define un sobre estable `OutboundEvent` con una lista **cerrada** de ocho tipos v1: `run.started`, `run.closed`, `run.transferred`, `handoff.created`, `handoff.resolved`, `release.published`, `release.promoted`, `release.revoked`; el catálogo compilado vive en `contracts/events/catalog.json` (generado por `uv run agentcore contracts`, no editable a mano). Esto cambia la premisa de esta sección: **el transporte ya no es enteramente "por acordar" ni algo que Pulso deba inventar desde cero** — agent-core ya decide qué publica y con qué forma; lo que falta acordar es quién entrega esos eventos y por qué canal (ver "Transporte" abajo), no el contenido del evento en sí.

Confirmamos leyendo `agent_core/outbound/models.py` y `agent_core/outbound/project.py` que `OutboundEvent` es un tipo **distinto** de `EngineEvent`, no un alias ni un simple passthrough: es una unión discriminada por `type` (`RunStartedEvent | RunClosedEvent | RunTransferredEvent | HandoffCreatedEvent | HandoffResolvedEvent | ReleasePublishedEvent | ReleasePromotedEvent | ReleaseRevokedEvent`), con un sobre propio (`spec_version`, `event_id`, `occurred_at`, `source: "engine"|"registry"`, `run_id?`, `session_id?`, `turn_id?`, `release_id?`, `data`). El proyector (`project_engine_event`, `project_outbox_message`) construye `data` **campo a campo** desde el `EngineEvent`/`OutboxMessage` de origen — nunca un volcado del payload interno — precisamente para que un campo nuevo en la cadena de auditoría no se filtre solo al canal público. El propio diseño documenta qué queda fuera a propósito: `reportable_attrs`, `reason` de `run_transferred`, `resolution_code` de `handoff_resolved`, y además `notes`, `origin`, `packet_fp`, `directory`, `directory_hash` y `candidates` — es decir, no hay `candidate_hash` ni actor/motivo en los eventos de `release.*`, y no hay referencia de cliente/subject (solo `subject_kind` dentro de `run.started`). Esto es consistente con la lectura de que `OutboundEvent` es la proyección sin PII/sin detalle de auditoría, y `EngineEvent` sigue siendo la fuente interna más detallada. `contracts/events/OutboundEvent.json` y `contracts/events/catalog.json` existen en el SHA fijado (verificado; no están en `contracts/schemas/`). Se fijan con el MANIFEST de §31.4.1 y `agentcore contracts --check` detecta su deriva. Agent-core no entrega estos eventos: sólo los proyecta; el productor es el exporter de §31.6.

El propio documento de diseño deja explícitamente abierto: (a) que agente y alias no están en `release.*` porque `RegistryEvent` no los guarda hoy; (b) "quién consume esto y desde dónde" — es decir, **la entrega real (outbox transaccional, relay con cursor, webhook, cola, tabla) sigue sin definir upstream**, es responsabilidad de "la unidad 4"; (c) si `contracts/VERSION` debe moverse con este contrato (hoy no lo hace: `catalog.json` lleva versión propia). Garantías que el contrato promete: entrega al menos una vez (dedup por `event_id`), orden garantizado solo dentro de un run (sin orden global entre runs), sin promesa de latencia ni de transporte, y proyección determinista (mismos eventos → mismos bytes canónicos).

**Qué simplifica esto para el adaptador `PlatformObservationBatch` de Pulso.** Con un catálogo cerrado y tipado ya publicado por agent-core, el adaptador de Pulso deja de tener que decidir qué forma le da a "un evento del motor" — ya no inventa su propio `EngineEvent`/`PlatformObservationBatch` genérico desde cero para la parte que cubre `agent_core.outbound`; en su lugar **consume el catálogo de ocho tipos tal cual lo define el sobre `OutboundEvent`** y lo envuelve en su propio transporte (`PlatformObservationBatch{source_id,tenant_id,partition,from_seq,to_seq,events[],batch_digest,contract_version}`) solo para la parte de entrega/ack/cursor que agent-core no resuelve. Dicho de otro modo: el discriminador `kind=core_event|platform_event` de §24.2 debería ahora distinguir, dentro de `core_event`, entre el `EngineEvent` de auditoría completo (cuando Pulso tiene acceso autorizado a la cadena vía M11) y el `OutboundEvent` público (cuando Pulso consume el catálogo cerrado) — son dos niveles de detalle del mismo origen, no el mismo objeto. Esto no elimina la necesidad de negociar transporte: agent-core mismo dice que "quién consume esto y desde dónde" sigue abierto, así que Pulso sigue siendo quien decide/construye el mecanismo de entrega (outbox, polling, relay), pero ya no decide la forma del evento. `from_seq/to_seq` siguen siendo posiciones del transporte de Pulso, distintas de `EngineEvent.seq`; no se infieren de la secuencia de un solo run, y el catálogo de `agent_core.outbound` tampoco expone un cursor global entre runs (solo orden garantizado dentro de un run).

**M11 export_events — sin cambios de fondo.** Confirmado literal en `agent_core/audit/export.py`: `export_events(sink, run_ids, release=None)` sigue siendo un iterador Python que requiere que otra unidad suministre los run IDs; no existe un endpoint upstream para listar todos los runs o exportar auditoría masiva. El adaptador que construiremos obtiene ese listado/export con un exporter Python propio (`pulso-core-exporter`, §31.6) que lee Postgres de Core con rol de sólo lectura; Rust no accede a esa base y `PostgresOutbox.pending/mark_delivered` no se usan desde Pulso, y entrega a nuestra API `POST /internal/v1/platform/observations` el mismo `PlatformObservationBatch` descrito arriba. Esta ruta de auditoría completa (vía `EngineEvent`) y la ruta pública nueva (vía `OutboundEvent`/`agent_core.outbound`) son complementarias, no sustitutas: la primera sirve para reconstrucción/forense con más detalle y PII controlada bajo policy; la segunda sirve para que Pulso se entere de "qué pasó" sin negociar acceso a la cadena completa. Envelope de transporte por evento: `{kind,source_event,source_schema_ref,source_run_ref?,episode_ref?,goal_ref?,layer_mapping_ref?,observed_at,trace_refs[],coverage_marker}`, donde `source_event` es `EngineEvent` u `OutboundEvent`/`PlatformEvent` según discriminador de §24.2. `from_seq/to_seq` y `source_sequence` son nullable cuando la fuente no ofrece cursor secuencial; en ese caso manifest/cursor opaco y cobertura limitada no permiten acreditar ausencia de gaps. Correlaciones ausentes quedan `unknown`, nunca IDs fabricados.

El adaptador reintenta hasta ack durable. Pulso valida digest/schema/tenant, verifica la cadena sobre el original dentro del adaptador confiable (cuando el evento viene de la ruta `EngineEvent`/M11) y guarda proyección tratada separada en S3, registrando artifact + cursor en una transacción PG; S3 no participa en la transacción, por lo que el blob debe existir y verificarse antes del commit y un blob huérfano no implica lote aceptado. Duplicado mismo digest retorna ack (coherente con la garantía "al menos una vez" que promete `agent_core.outbound`); digest distinto es conflicto. Un gap del transporte exige backfill al exportador; un gap de `EngineEvent.seq` exige recuperación/verificación del run; un gap dentro de un solo tipo del catálogo `OutboundEvent` no tiene cursor global que lo acredite — sólo orden dentro de un run — así que no se puede afirmar ausencia de huecos entre runs usando solo ese canal. No confundir ese backfill con ejecutar `agentcore replay`. Evento tardío genera revisión de ventana y revalida señales dependientes. El original sólo se conserva cifrado/restringido si policy lo permite; si no se conserva, guardar receipt de verificación, no afirmar que puede revalidarse la cadena sobre payload redactado. El mock de transporte preserva schemas upstream (`EngineEvent` y, donde aplique, `OutboundEvent`) y representa explícitamente el adaptador adicional.

**Qué podemos observar y qué falta.** `node_entered`, `decision_made`, `rule_evaluated`, `tool_called`, `agent_step`, acciones dispatched/verified, respuestas/validación/fallback, `turn_completed`, escalamiento y cierre (vía `EngineEvent`/M11) permiten reconstruir decisiones y resultados del motor con el mayor detalle disponible. En paralelo, el catálogo público de `agent_core.outbound` cubre un subconjunto orientado a ciclo de vida: inicio/cierre/transferencia de run, creación/resolución de handoff y publicación/promoción/revocación de release — sin tokens, sin probabilidades/umbrales, sin motivo en texto libre. `decision_made` (solo disponible vía la ruta de auditoría completa) contiene proveedor, versión, probabilidades/umbrales, tokens, USD y latencia; `turn_completed` contiene duración y stages. `response_emitted/failed.llm.cost_known=false` significa costo desconocido, nunca cero. El upstream no declara `layer=classifier|tree|ai1|ai2|human`: el adaptador aplica un mapping versionado de agente/flow/nodo/release a capa. Una ejecución puede cruzar varios runs; `episode_ref`, ventanas de recontacto y vínculos dataset↔run requieren procedencia externa explícita.

M9 ("Acceso y API") es más amplio que "solo runs": confirmado en `contracts/openapi.json`, el módulo cubre `POST /v1/runs` (no existe un `GET /v1/runs` de listado), `GET /v1/runs/{run_id}`, `/v1/runs/{run_id}/transcript`, `/v1/handoffs/{handoff_ref}`, `POST /v1/handoffs/{handoff_ref}/resolution` y `/v1/sessions/{session_id}/lineage|turns` — es decir, todo el acceso/API del motor (runs, transcript, handoffs y linaje/turnos de sesión), no una superficie limitada a consulta de runs individuales. `serve` ya compone estos servicios; adapters productivos de transcript/authz/tools siguen pendientes. Transcript devuelve entradas renderizadas según permisos, no razonamiento intermedio ni acceso libre a datos `full`. `handoff_resolved` informa `resolution_code`, `handoff_quality` y `reader_type` en la ruta de auditoría completa (nota: `resolution_code` queda excluido a propósito del evento público `handoff.resolved` de `agent_core.outbound`, que solo expone `handoff_quality` y `reader_type`); ninguna de las dos rutas registra acciones/tools humanas, tiempo humano, CSAT/NPS ni recontacto. `run_closed.outcome=escalated` no demuestra resolución del cliente. Esas señales necesitan fuente de plataforma adicional; mientras falta, el detector marca la hipótesis `insufficient_human_evidence` y continúa con frentes sustentados.

**Detalle OTel y replay.** `TraceLookupPort(trace_id,time_range,purpose)` es adaptador Pulso a spans/logs autorizados, con sampling/cobertura/digest. Eventos audit completos sirven denominadores; spans muestreados sirven diagnóstico. Un span ausente no prueba una acción omitida. `agentcore replay --mode fixture` reproduce la misma release con modelos/tools grabados y compara eventos; comprueba reproducibilidad, no beneficio de una candidata. El modo `audit` todavía tiene integración/riesgos pendientes en upstream y no es requisito asumido disponible. La consola distingue replay registrado, fork de investigación y evaluación candidata con modelos reales en sandbox.

**Registro y entrega reales.** `RegistryPort` del motor upstream es lectura de releases publicadas (`resolve_release`, `release_status`, `get`); no es el API de autoría. Nuestro adaptador de construcción usa `RegistryService`/extensión HTTP `/v1/registry`: crear propuesta, actualizar drafts con `expected_rev`, validar, freeze, evaluate, approve y publish; promoción/revocación son operaciones distintas. Los eventos `release.published`, `release.promoted` y `release.revoked` del catálogo `agent_core.outbound` (`source: "registry"`, proyectados por `agent_core.registry.outbound.project_registry_event`, `event_id = reg-<seq>` sobre `reg_events`) son ahora la forma pública más directa de enterarse de estas transiciones, pero no llevan actor, motivo, origen, hash del candidato, agente ni alias — ampliar eso es un cambio de registry aparte, todavía no hecho. `CapabilityBundle` de Pulso contiene drafts/refs nativos y metadata de oportunidad; no reemplaza la `Release` upstream ni inventa schemas Tree/Skill que el registry no ofrece. El ciclo actual es `draft→candidate→evaluated→approved→published`; `fail` devuelve a draft y `failed_infra` conserva candidate. Reopen invalida hash/evaluación/aprobación. Builder bot autentica con credencial staff propia, tipo builder y constructor; aprobación/publicación/promoción requieren builder humano aprobador+step_up, revocación/importación admin+step_up. La investigación, construcción e iteración siguen automáticas hasta ese gate: no prometemos autopublish upstream ni trasladamos permisos humanos a un agente.

**Evaluación nativa y complementaria.** Compilamos escenarios ejecutables a `EvalSuite{id,version,agent_id,repetitions,scenarios,thresholds{metric_id→{noise_margin,floor?}}}` (los umbrales viven por métrica, no a nivel suite; cada métrica `gate`/`guardrail` de `Agent.metrics` exige uno, ver §31.4.11); cada `Scenario` contiene principal, pasos start/turn/confirm, `SandboxSeed.tools`, `sensitive_values` y `Expect{outcome?,actions_verified[],escalated?}`. Campos richer de campañas Pulso quedan fuera del JSON upstream (`extra=forbid`). `ScenarioHarness` usa `EvalTarget{label,release,registry}` y `SandboxPort.provision/tools/teardown` por corrida; tools requieren `is_sandbox=true`. `LocalSandbox` upstream sirve respuestas de tools en memoria, no un banco sandbox real. Nuestra implementación stateful debe respetar ese puerto y acordar cualquier seed extendido. `EvalReport` guarda checks/métricas/resultados/notas/verdict; candidate hash/base/suite y `eval_run_id` se recuperan de `GET /proposals/{id}` → `last_eval: EvalRun | null`, no se inventan dentro del `EvalReport` ni requieren acceso directo a tablas Core. Tras un `fail` la propuesta vuelve a `draft` sin hash y `last_eval` es `null`: el reporte sólo viaja en el cuerpo 409 `gate_failed` (`payload`), sin `eval_run_id`, y Pulso lo persiste antes de releer (§31.7.1).

El gate nativo comprueba los cuatro guardarraíles `platform_*` (`platform_pii_leak`, `platform_unverified_success_claim`, `platform_unverified_write`, `platform_unapproved_knowledge_citation`, §31.7.1) con piso 0 absoluto (no «no peores que base»; la ausencia de medición de cualquiera de ellos es fallo) y primary ≥ base−noise_margin; sin base usa floor y guardrails cero. Primary es cumplimiento de `Expect`, y margen default 0.05 permite regresión: `pass` **no demuestra mejora**. Pulso añade evaluación independiente de mejora/valor, holdout, oracle de estado bancario y costo/latencia donde haya datos; exige ambos gates antes de recomendar publicación. Sensitive leaks nativo cuenta coincidencias literales de `sensitive_values` en eventos audit, no certifica ausencia universal de PII. El gate complementario no sustituye ni elude el upstream. Un failure de LLM/sandbox/tiempo es `failed_infra`, sin pase parcial.

**Capacidades todavía pendientes.** Registry actual puede promover un alias completo o revocar una release; no implementa shadow/canary/cohortes ni API de exposure. `PlatformReleasePort` y `ExposureObservation` son adaptadores futuros/simulados identificados como tales, con idempotencia y ack/exposición separados; nunca se atribuye esa semántica a `promote`. Releases nuevas pueden crearse/promoverse mediante operaciones disponibles una vez aprobadas.

El estado del módulo de conocimiento (M12) sigue **pendiente de verificación directa y queda marcado aquí, no resuelto**: hay señales contradictorias en la propia documentación de `agent-core` entre `README.md` (§"Conocimiento": "solo hay propuesta de spec", y en el árbol de directorios `knowledge/ pendiente: solo spec (M12)`) y `docs/specs/motor/00-indice.md`, que en su tabla de módulos describe M12 como "2 (`read` implementado 2026-09-30; `navigate` fuera)" y en su matriz de temas resueltos afirma "**resuelto** (diseño 2026-09-30) y **`read` construido** (2026-09-30, `SCHEMA_VERSION` 1.0.0); `navigate` y `search` siguen fuera". No intentamos resolver esta contradicción por inferencia: el README parece describir un estado más antiguo o más conservador que el índice de specs, pero no tenemos forma de confirmar cuál refleja el `HEAD` real sin correr las pruebas del módulo (`uv run pytest tests/m12`) o leer el changelog del repo con más detalle del que esta verificación cubrió. Lo que sí confirmamos con certeza, independiente de ese desacuerdo: `KnowledgeSnapshot` existe como schema/tipo (`contracts/schemas/KnowledgeSnapshot.json`) y como `EntityKind` en M0 (`EntityKind.knowledge_snapshot`, `Release.knowledge_snapshot`), de modo que el snapshot puede sembrarse por import con independencia de si el modo `navigate` del módulo de navegación está implementado. Propuestas actuales no modifican ese snapshot. Wiki del investigador sigue usable; una mejora de conocimiento para atención queda bloqueada hasta soporte y aprobación upstream de `navigate`/`search`.

**Integración nativa de modelos en Core.** Upstream tiene `OpenAICompatGateway` Python stateless detrás de `LLMGateway` y `LLMAgentPort`; no es un servicio nuestro. `endpoint_alias` apunta al proveedor/servicio externo autorizado; no se construye proxy Pulso. `LLMAgentPort` actual requiere perfil `structured: prompted`; no compilarlo con native. Jev se invoca mediante el `DecisionProvider` concreto `jev`/`jev_http` (§23), separado del resto de proveedores de `decision` (M5). Contratos verifican estas diferencias, perfil, usage y errores sin inventar una interfaz común externa.

| Señal transversal calculable | Dato requerido | Posible propuesta, sujeta a bridge/eval |
|---|---|---|
| Flow escala repetidamente por un motivo | `node_entered`, `escalated`, `run_closed` (auditoría) o `run.closed`/`run.transferred` (catálogo público), release/flow refs y mapping válido | modificar Flow/Agent/DecisionModel con escenarios nativos y oracle complementario |
| Agente repite lectura y escala | `agent_step`, `tool_called`, `escalated`; capacidades/permisos de release | cambiar prompt/flow/tool refs; no atribuir omisión sin cobertura completa y autorización |
| Humano resuelve con patrón estable | fuente externa de acciones humanas + outcome maduro; `handoff.resolved`/`handoff_resolved` solo no basta (ninguna de las dos rutas trae `resolution_code` combinado con acción humana verificada) | proponer flow/agente cuando bridge/oracle sostienen mecanismo |
| Tool error precede escalamiento/recontacto | `tool_called`/acciones, timestamp, release; vínculo externo de episodios para recontacto | evaluar timeout/fallback/cambio de integración sin afirmar causalidad por secuencia |
| Costo/latencia sube por ruta | usage conocido, `turn_completed`, población y cobertura; outcome comparable | simplificar flow/cambiar perfil bajo gate nativo y gate de mejora Pulso |
| Release publicada/promovida/revocada afecta comportamiento | `release.published`/`release.promoted`/`release.revoked` del catálogo público (sin actor/motivo/hash candidato) correlacionado con `GET /proposals/{id}` para el detalle de autoría | correlacionar causalmente con cambios de outcome/costo antes de atribuir efecto a la release |

**Visibilidad y aceptación de integración.** Cada transición Pulso escribe `pulso_run_events` con progreso/evidencia/causa/next_automatic_action; el feed distingue evaluación upstream, gate de mejora Pulso, espera de aprobación humana, publicación y promoción confirmada. El usuario aporta autoridad/conocimiento puntualmente; los runs restantes siguen trabajando. Contract tests deben probar: parse/schema/Decimal upstream; raw preservado al normalizar; secuencia por run y transporte; discriminación correcta entre `EngineEvent` (auditoría, con PII potencial bajo policy) y `OutboundEvent` (público, sin PII, campos excluidos a propósito listados arriba); export incompleto no prueba ausencia; mapping/correlación faltante→unknown; gate pass con regresión dentro margen no declara mejora; failed_infra no habilita approve; executor no sandbox rechazado; teardown tras fallo; transcript prohibido no filtrado; handoff escalated no equivale a resolución; knowledge/canary no soportados visibles como dependencia, con el estado de M12 marcado explícitamente como contradictorio en la fuente (README vs. 00-indice) hasta verificación directa. UI técnica enlaza evento upstream→job→draft→hash candidato→EvalReport→decisión humana→release sin inventar endpoints o efectos. La plataforma renderiza el centro de mando; §25 detalla nuestra consola de debugging.

### 24.1 Integración con producto: journey, permisos y tres autoridades separadas

Fuente de producto local: `design/` y [análisis trazable](ANALISIS_PRODUCTO_DESIGN.md). Los archivos son experiencias complementarias, no versiones ordenadas por sufijo. La plataforma integral posee app/web cliente, backoffice de atención, supervisión y administración; Agent Core posee sus primitivas/registry/runtime y el motor posee detección/evidencia/propuestas/evaluación/memoria. El motor no sustituye ninguna de esas experiencias: sus read models y comandos se integran en ellas. La consola de §25 sigue siendo para desarrollo. Los valores/reglas ilustrativos del diseño no reemplazan dataset, políticas E0 ni contratos upstream.

**Tres autoridades distintas:** (a) aprobación financiera de una acción en un caso — plataforma bancaria/sandbox; (b) aprobación de cambio de permiso/policy — gobierno de plataforma; (c) aprobación/publicación de candidato — Registry Core. Un rol visible, badge de identidad, consentimiento del cliente o aprobación de (a)/(b) no autoriza (c). El motor conserva refs y estados tratados, nunca ejecuta abonos ni administra usuarios. Un candidato no puede autoexpandir sus grants/tools; cambios de autoridad quedan `waiting_dependency` hasta recibo válido de la frontera externa. Separar autor/aprobador cuando lo requiera la policy, incluso si la UI permite cambiar de rol localmente.

**Journey observado, no una tabla nueva por pantalla.** `InteractionObservation` conserva refs autorizadas a contacto/caso/transacción/producto y origen contextual app-detail/app-support/web/email/phone, dirección entrante/saliente, motivo elegido y motivo inferido, policy/config vigentes, tipo de actividad `new_issue|status_request|requested_reply|follow_up|unknown` y linkage explícito. Son extensiones del contrato de plataforma con fuente/cobertura, no campos inventados del CSV. `requested_reply` no cuenta como recontacto de fracaso por defecto. Deduplicar sólo por identificador externo/relationship acreditado; semejanza textual/temporal sigue siendo candidato, no join exacto. Ante falta de un atributo, marcar unknown y excluir la métrica dependiente con denominador visible.

| Evidencia de la experiencia | Representación/consumer del motor | Comportamiento y prueba |
|---|---|---|
| Copiloto sugiere/borrador humano revisa/envía | Intento de asistencia con actor, versión, estado y refs tratadas; detector de secuencias efectivas | Rechazo/edición/aceptación ≠ ejecución; no evaluar un borrador como mensaje enviado |
| Árbol mitiga, abre reclamo y escala | LayerAttempt y ToolReceipt por paso, GoalOutcome por objetivo | Bloqueo confirmado no acredita resolución de disputa; comprobar continuidad del contexto y efectos parciales |
| Pregunta/consulta recurrente convertida en herramienta | Evidencia de uso y propuesta de artefacto tool/flow/context, con cobertura y scope | Frecuencia sólo dispara investigación; validar utilidad, idempotencia y permisos con otro cliente/test de aislamiento |
| Solicitud/respuesta/espera por aprobación | Eventos de solicitud, vencimiento, decisión y efecto externos | Aprobado sin receipt del efecto permanece pendiente/unknown; rechazo no implica mala atención automáticamente |
| Notificación fallida, retry o canal alternativo | Intento, outcome de entrega, correlation/idempotency refs | Mensaje enviado no implica entregado/leído; fallos y delivery se cuentan separadamente, sin doble efecto al retry |
| Cierre y encuesta/seguimiento | Estado operativo, outcome declarado y comprobado, survey requested/responded | Cierre sin resolver no es success; texto de cierre no es oracle; sin respuesta no inventar CSAT/NPS |
| Llamada/hold/transcripción y correo sin sesión | Turnos parciales/finales y tiempos por estado, proof de identidad tratado | Excluir parciales del gold; separar cola/hold/activo/espera cliente; teléfono/correo no acredita identidad |

**Acceso interno versus divulgación:** la pantalla puede mostrar contexto al asesor antes de verificar al cliente; esto requiere grant interno explícito, no autoriza que copiloto/cliente reciban lo mismo. Views de investigación usan datos anonimizados; la atención aplica scopes separados por actor/purpose y proof vigente en cada frontera mutable/de divulgación. No copiar respuestas correctas de identidad a logs, prompt, wiki o debug; preguntas de aclaración de una disputa no son verificación de identidad. El mock debe rechazar una consulta/divulgación indebida aunque el diseño muestre datos; nunca usar el prototipo como política de seguridad.

**SLA y valor:** el diseño ilustra plazo de respuesta de reclamo y deadline de supervisión; el motor usa un reloj por policy/country/calendar con inicio, pausas y cobertura, no constantes universales de UI. Sin calendario/policy sustentados sólo duración transcurrida y supuesto etiquetado, no «violación regulatoria». Separar atención humana activa, espera interna y espera del cliente. Un ahorro proyectado especifica población, periodo, tiempo sustituible y costo supuesto; no multiplicar mitigaciones por duración de resolución ni reutilizar satisfacción 1–4 como CSAT de otra escala.

**Cambio de permisos, policy o retención:** versiones externas se fijan en snapshot/config del run y recibos; cambio posterior invalida eligibility/release si afecta seguridad/outcome, incluso con evaluación previa exitosa. Revocaciones se aplican en frontera al invocar y antes de publicar; trabajos in-flight se detienen/reconcilian sin deshacer hechos. Retención administrativa propuesta no es norma validada: overlay de revocación/redacción y propagación a derivados/memoria (§21) con audit mínimo autorizado; no retener PII por «blobs inmutables». Nombres de tablas/versiones del diseño no son autoridad del SourceContract.

**Aceptación incremental:** U29 ingiere estos estados en fixtures de plataforma y U30 detecta familias con denominadores/cobertura; U04 mapea sólo atributos presentes de E0; U20/U20-E/U26/U36 prueban autorización/identidad/efectos, U17/U18 preservan outputs tool/flow/agent/context y autoridad Core, U24 muestra estados veraces. Pruebas obligatorias: respuesta tardía/doble/cross-session, dos canales mismo caso, policy stale tras freeze, proponente=aprobador denegado, aprobación expirada, notificación unknown, cierre falso, consulta antes de identidad con scopes distintos y revocación en trabajo en vuelo. Estas pruebas se adscriben a unidades existentes, no autorizan implementar F7/F8.

### 24.2 Eventos complementarios, políticas y outputs sin inventar capacidades Core

`PlatformObservationBatch.events` es una unión discriminada del adaptador Pulso: `kind=core_event|platform_event`. Dentro de `core_event` distinguimos ahora dos niveles, confirmados como tipos distintos contra el código real: el evento de auditoría completo (`EngineEvent`, con su verificación nativa de cadena, sin cambiar payload/hash para encajar pantallas) y el evento público proyectado (`OutboundEvent` del catálogo cerrado de `agent_core.outbound`, construido campo a campo, sin PII, sin `candidate_hash`, sin actor/motivo en los tipos `release.*`). Ambos conservan su forma de origen sin normalizarla para la pantalla. `platform_event` sigue siendo el tipo complementario de la unidad de datos/plataforma — fuera de `agent-core` — y contiene `PlatformEvent{event_id,source_contract_ref,source_sequence?,occurred_at,received_at,entity_refs,actor_ref,event_type,payload_ref,digest}` con schema tipado por evento, permisos y payload tratado. Cursor de transporte permanece externo; si la fuente no da secuencia/cobertura, el contract lo declara y se conserva uncertainty — ni `agent_core.outbound` (orden garantizado solo dentro de un run) ni una fuente de plataforma sin cursor permiten inventar integridad hash upstream. Se soportan inicialmente `assistance_suggested`, `assistance_sent`, `human_action_recorded`, `case_state_changed`, `response_requested`, `response_received`, `delivery_state_changed`, `case_authority_decided`, `platform_policy_changed`, `access_revoked`; presencia/cola sólo si el SourceContract las entrega. `response_received` referencia solicitud y choice tipado `yes|no|other`, sin almacenar respuestas de identidad; el prototipo que usa sólo `answered=true` no suministra dicho choice.

Validación U29: discriminador/schema/tenant/refs/digest y dedup por source/event_id (para `OutboundEvent`, el `event_id` es el del evento de cadena que lo origina — o el `message_id` del outbox para `handoff.created` — y es la clave de deduplicación que el propio contrato promete: entrega al menos una vez); conflicto mismo ID diferente digest genera finding y bloquea slice; event-time tardío no altera manifests históricos y crea proyección/sucesor nuevos. Cualquier denominador de cobertura se liga al mismo `tenant_id`, `source_id`, `contract_ref` y `batch_digest` de los eventos que pretende describir; una fuente sampled, parcial o `evolution` no puede disfrazarse de cobertura completa — el catálogo público tampoco ofrece cursor global entre runs, así que no sustituye un denominador de cobertura completo por sí solo. El almacenamiento PostgreSQL aplica `FORCE ROW LEVEL SECURITY`; una concesión de rol→tenant→purpose sólo la emite la frontera confiable por transacción y el rol runtime no puede alterar la tabla de concesiones. Esto bloquea lectura/escritura cross-tenant y grants/purpose erróneos, pero no afirma que RLS sustituya la integridad del dominio para una escritura autorizada del propio tenant: CAS, fences, receipts y schemas siguen siendo obligatorios. Reducer mapea eventos a InteractionObservation existente; humano/cliente/plataforma no se convierten artificialmente en node de Flow. Chain Core incompleta se reporta para ese run; la otra fuente no «rellena» sus seq/hash. E0 no tiene todos estos eventos: mapping explicita present/derived/unsupported, fixtures sandbox prueban los ausentes con evidence_kind separado. Cambiar source contract exige versión/compatibilidad, no editar CSV ni EngineEvent; para el catálogo público, el propio diseño ya fija la regla de compatibilidad: un campo opcional o tipo nuevo es cambio compatible (sube versión menor de `catalog.json`), quitar o cambiar un campo exige tipo nuevo o `spec_version` 2, y una copia congelada de schemas v1 (`tests/outbound/frozen_v1/` en agent-core) hace fallar la prueba si un campo obligatorio desaparece o cambia de tipo — Pulso puede apoyarse en esa garantía en vez de construir su propia prueba de congelamiento para esta parte.

**Política reproducible y permiso vigente:** policy_ref del run fija interpretación histórica y replay; autoridad efectiva se revalida en cada lectura/divulgación/tool/model-egress/publicación. Un cambio ordinario produce nueva config y reevaluación según affected consumers; revocación urgente impide nuevos usos desde su recepción, fencea resultados en vuelo y bloquea publish aunque policy pin antigua permitía. Retención efectiva no excede autorización externa: config local puede acortar, nunca ampliar; legal hold sólo mediante autoridad/documentación externa explícita, no flag del agente. Purga/redacción se propaga a extracts/cache/wiki/details/export y el estado mínimo de auditoría se conserva sólo cuando autorizado. Tests cubren fuente revocada entre draft/freeze/evaluate, export/URL de detalle cross-tenant y resultado tardío sin permiso.

**Nuevas tools:** el output compatible puede proponer ToolDef/schema/refs y flujo que la utiliza, pero no genera/executa código arbitrario. la tool debe existir en el catálogo de capacidades Pulso (`capability-catalog.json`, §31.9.4) con handler registrado y versión fija; Core no tiene `executor_ref`: el vínculo tool→ejecución es el `ToolExecutor` único del runtime (§31.5.6); una nueva operación requiere implementación/revisión fuera del builder, contrato, pruebas sandbox y grant antes de readiness. Si executor falta, `dependency_blocked` conserva la propuesta/evidencia útil; no simular éxito como interoperabilidad real. Tool de lectura parametrizable sobre datos autorizados puede reutilizar executor general con limits y query template validado; no añadir permisos cross-customer ni SQL crudo en producción de atención. Wiki interna no equivale KnowledgeSource publicable: su cambio de atención sigue restricciones Core de §27/§29, y el estado de implementación del módulo de conocimiento (M12) sigue marcado arriba como contradictorio entre fuentes upstream, no resuelto.

**Cobertura bottom-up:** U29 agrega union/late/dedup/request-response; U30 métricas con scopes/denominadores y no contar requested_reply como fracaso; U05/U10 revocación de grants/egreso; U17 capabilities/executor/affected consumers; U20/U20-E identidad y efectos; U21 autoridad/expiry; U33 propagación a memoria. Revisor integra estas pruebas en matriz UC→test→contract antes de cerrar cada corte. El DAG por sí solo no acredita estos escenarios.

## 25. Backoffice interno del motor: operación autónoma, observabilidad y debugging

**Objetivo y frontera.** Una corrida autónoma debe ser inspeccionable sin entrar por SSH ni leer JSONB manualmente: qué trigger la creó, qué ejecuta ahora, qué leyó/invocó, qué decidió, qué quedó en espera, qué falló, qué evidencia y configuración usó, y qué efecto externo está confirmado o `unknown`. `debug-console/` es el **backoffice interno de operación del motor**, una UI real incluida en el primer corte (no un mock ni la consola de agentes que atienden clientes). Está dirigida al equipo que construye y gobierna Pulso para entender la actividad autónoma y actuar sólo mediante comandos acotados. Consume la API privada `/internal/v1/debug` del `control-api` y links a OTel; no consulta PG/S3 directamente ni ejecuta SQL arbitrario sobre el dataset. Es de **solo lectura por defecto**. El motor funciona idéntico cuando la consola está apagada; eventos de transición se registran por las transacciones del dominio, no por “clicks” de UI.

```mermaid
flowchart LR
  TR[Trigger: snapshot, evento, agenda, manual] --> RUN[Run y jobs: estado durable]
  RUN --> EV[pulso_run_events: secuencia por run]
  RUN --> AR[Artefactos, edges, receipts, wiki]
  RUN --> OT[Logs, métricas y trazas OTel]
  EV --> API[Control API: proyección debug]
  AR --> API
  OT --> API
  API --> UI[Consola técnica interna]
  UI -->|comando versionado y auditado| API
  UI -. no accede directamente .-> STORE[PG/S3 o plataforma]
```

**Pantallas y navegación obligatorias.** La portada muestra runs activos/recientes, cola por lane, jobs `dead`, dependencias `waiting_dependency`, lag de ingesta, cuota/costo, salud observable de Core/proveedor externo/sandbox/OTel (dependencia externa desconocida si no ofrece health verificable) y release `unknown`; filtros por tenant, entorno, estado, trigger, fuente/config y rango de tiempo, con cursor y URL compartible. Entrar en un run abre un **grafo de trabajos y etapas** (`trigger→scan→investigación→bridge→propuesta→escenarios→evaluación→release→observación→memoria`), no un wizard: nodos pendientes/activos/completos/fallidos, duración, intento, worker/lease, bloqueo y próxima reanudación; selección de nodo preserva scroll/filtro y abre panel lateral. Línea de tiempo ordenada por `sequence` muestra eventos, artefactos producidos, decisiones, reconciliaciones y cambios de head; se puede comparar dos runs o revisiones con mismo snapshot/config y ver qué cambió. Cada card enlaza al `trace_id` cuando existe; si OTel no está disponible se conserva el hecho durable y aparece `trace_unavailable`, no un hueco silencioso.

| Panel de detalle | Qué muestra para responder “¿qué hizo?” | Fuente y límite |
|---|---|---|
| Origen/plan | trigger e idempotency key tratados, snapshot y contratos, cutoff, config/model profiles, pasos planeados vs ejecutados, responsable y presupuesto | jobs/config/source refs; un plan no se declara ejecución |
| Datos/SQL | manifest del extracto, tablas/columnas permitidas, filtros, SQL **tratado o digest**, QueryReceipts, filas/bytes/duración/truncación, intentos bloqueados y quality findings | receipts + spans; no vista raw de CSV/PII ni botón para consultar fuente directamente |
| Agentes/modelos | invocaciones Jev/LLM en orden, purpose, perfil/ruta real, tipo de juicio/schema, input/output tratados o digest, validación, tokens/USD, latencia, retry/fallback/error y refs de decisión | ModelReceipts + trazas; sin claves, chain-of-thought privado ni promesa de registrar cada token |
| Investigación | candidatos examinados y descartados, hipótesis, contraevidencia, comparadores, ablation, grado de enlace y valor como escenario vs observado | signal/opportunity/bridge/ValueModel; refutado no desaparece del historial |
| Evaluación | Dos gates separados: Core pass/fail/failed_infra y Pulso improvement/unsafe/unknown/insufficient_power; candidate_hash, suite/version/digest, base staging y baseline runtime | Dos cards independientes, nunca un verde único; final sólo agregado; resultados Core no sustituyen efecto medido |
| Memoria | head montado, páginas/digests leídos, diff propuesto/publicado, lint, CAS perdido, revocaciones y rebase | MemoryUseReceipt/wiki tratada; páginas sensibles requieren grant |
| Plataforma externa | observaciones por clasificador/árbol/IA1/IA2/humano, cobertura, spans auxiliares, comandos/acks, exposición, outcome maduro y `unknown` | eventos durables y recibos; ausencia de span no demuestra ausencia de acción |
| Operación | job/worker heartbeat, lease, retries, queue age, cuotas, circuit breaker, sandbox task/container, dependencia y próximo wakeup | jobs/run events/health/OTel; dashboard no sustituye alertas |

**Contrato de instrumentación, no “guardar todo”.** Cada operación relevante emite evento tipado `RunEvent` con `sequence` monotónica asignada en PG por run mediante el job raíz (§19), `run_ref`, `job_ref?`, `stage`, `event_code`, `status`, `reason_code?`, `artifact_ref?`, `trace_id?`, `details_ref?` y tiempo; se graba en la **misma transacción** que cambia estado. `schedule_run` crea primero el job raíz y su evento `trigger_accepted`; hijos heredan `run_ref`. Eventos mínimos: `trigger_accepted`, `job_queued/claimed/heartbeat_lost/completed/deferred/dead`, `extract_started/completed/rejected`, `query_submitted/completed/denied`, `model_invoked/completed/invalid/unknown`, `signal_selected/refuted/corroborated`, `proposal_revised`, `evaluation_started/completed/gate_blocked`, `release_sent/ack_unknown/confirmed/rejected`, `observation_ingested/gap`, `memory_mounted/publish_rejected/published`, `dependency_waiting/resumed`, `run_completed/cancelled`. Heartbeats se agregan por cambio de estado/intervalo, no se inserta uno por segundo. Receipts/artifacts guardan payload versionado; logs/traces detallan waterfall y latencia. Un `GET` de debug nunca crea eventos de dominio; acceso a dato sensible sí genera `pulso_audit_events`. Se define retención separada: eventos y auditoría por política versionada, OTel más corta, blobs sensibles por propósito/consentimiento. No se promete “absolutamente todo” literal: no se retienen secretos, PII directa, chain-of-thought privado ni tokens individuales; se garantiza **toda transición material y su evidencia/razón recuperable**.

**API privada y comportamiento.** Bajo `/internal/v1/debug`, autenticación humana SSO/OIDC y rol `debug_viewer` (lectura tratada) o `debug_operator` (comandos acotados); **no** basta el JWT de servicio dla integración externa de modelos. `GET /runs?cursor&filters`, `/runs/{id}/graph`, `/runs/{id}/events?after_sequence`, `/runs/{id}/artifacts/{ref}`, `/runs/{id}/model-calls`, `/runs/{id}/queries`, `/runs/{id}/evals`, `/runs/{id}/memory-diff`, `/runs/{id}/external-commands`, `/health/dependencies` devuelven proyecciones paginadas, `as_of` y `projection_revision`. `GET /runs/{id}/stream?after_sequence` reanuda con secuencia; ante gap el cliente repide página, deduplica por `(run,sequence)` y no interpreta silencio como final. `POST /runs/{id}/diagnostic-bundles` (rol autorizado y motivo) crea export tratado con TTL y audit; `GET /diagnostic-bundles/{id}` descarga manifest + receipts/logs **tratados**, digests, config/commit y tiempos, sin PII/secretos/final_locked. Un GET jamás crea artifact de export. No hay endpoint que exponga SQL raw del agente si contiene literales sensibles: se muestra AST/SQL saneado, digest y parámetros por clase. Links a Grafana/CloudWatch se firman o construyen con refs, no incluyen payloads.

**Comandos de depuración autorizados.** `POST /runs/{id}/pause`, `/resume`, `/cancel` y `POST /jobs/{id}/retry` requieren `expected_revision`, idempotency key, motivo y `debug_operator`; pausa detiene nuevos claims, no interrumpe efecto externo ya enviado. Retry crea generación sucesora y sólo si el efecto está confirmado como no ocurrido o reconciliado. `POST /runs/{id}/fork-replay` crea **otro run** fijando snapshot/config/simulator seed y `replay_of`, sin mutar el original; deniega fuente/config revocada, final_locked o datos ya no disponibles. Su salida se etiqueta `team_generated`/sandbox. No hay botón “promover aunque falle”, editar artifact, desbloquear holdout ni ampliar policy. Rollback/release conservan los gates/roles del dominio, nunca se saltan desde debug. Todas las mutaciones registran actor/grant/razón en auditoría; la UI siempre presenta “solicitado” separado de “confirmado”.

**Seguridad y despliegue.** Consola habilitada local y staging; en AWS va tras ALB interno + acceso VPN/SSM/identity proxy, sin ruta en demo pública ni cliente bancario. `debug_viewer` ve ids pseudónimos y payload tratado; acceso excepcional a blob sensible es grant de propósito, tiempo, tenant y auditoría, y sigue prohibido para final_locked de una campaña activa. `debug_operator` no hereda `approver` ni permisos de plataforma. CSRF para sesión browser, CSP, expiración, rate limit, no cache de respuesta sensible, redacción previa al índice/búsqueda/export, y prueba cross-tenant. Si el backend OTel cae, la consola marca panel de traza degradado; si PG cae, muestra “estado no disponible” y no inventa último estado. El integración-modelos/proveedor puede ocultar prompts completos por política; la consola indica `payload_redacted` y digest. Ninguna capacidad de debug debe ampliar el perímetro del agente/SQL sandbox.

**Rendimiento y pruebas de aceptación.** Proyección desde índices `(tenant,run,sequence)` y `jobs(run_ref,status)`, carga diferida de detalle/artefactos y cursor máximo 100; p95 objetivo ≤500 ms para lista/timeline de 100 en hardware de referencia, waterfall OTel en llamada separada con timeout. La UI usa virtualización para >1.000 eventos, reconexión SSE/backoff, filtros persistidos en URL, estados vacío/cargando/error/gap y accesibilidad teclado/lector de pantalla. Pruebas unitarias cubren reducers de cronología/grafo, redacción y permisos; integración PG prueba que transición y evento son atómicos, orden concurrente, retry y lease; contract prueba endpoint/403/404 sin filtrar tenant, SSE duplicate/gap y esquema N/N−1; E2E browser sigue corrida positiva, refutada, `waiting_dependency`, release `unknown`, memoria revocada y collector caído. Fault test reinicia API durante stream, recupera por `after_sequence` sin perder/doblar hechos. Seguridad intenta ver PII, secreto, holdout y otro tenant por UI/API/export. Carga prueba 100 runs × 1.000 eventos sin N+1, lag de proyección y presupuesto PG. **DoD:** un ingeniero sin acceso a shell identifica desde la consola qué run está detenido, el último paso verdadero, error/owner/next wakeup, las consultas/model calls relevantes, evaluación y estado externo; reproduce un run como fork sin alterar su evidencia histórica.

**Cursor y accesibilidad de la consola (U07/U24/U32).** El contrato browser de §29 también aplica a `after_sequence` de §25: si la secuencia quedó purgada, HTTP 410 `cursor_expired` incluye ref de snapshot autorizado y cursor de recuperación; el cliente sustituye su proyección con ese snapshot y reanuda, sin inventar eventos perdidos ni declarar finalización. Cursor de otro tenant/run no devuelve piso/secuencia/refs ajenos. Tests cubren pérdida entre snapshot y stream, duplicados y revocación durante recuperación. Aceptación de accesibilidad: todas las acciones por teclado; drawer/dialog con nombre accesible, foco inicial dentro, Escape cierra y devuelve foco al disparador; reconexión/progreso no roba foco y usa anuncio de estado moderado; grafo tiene lista textual equivalente con estados, errores y dependencias; estados no dependen sólo del color. Testing Library verifica roles/foco, Playwright recorre teclado y una revisión independiente con lector verifica el camino crítico. No afirmar cumplimiento WCAG sólo por tests automáticos.

### 25.1 Backoffice de la plataforma de atención (diferido; distinto del backoffice interno de Pulso)

El backoffice de atención/supervisión de la plataforma y cualquier UI/API de producto dirigida a usuarios de esa plataforma quedan **fuera del alcance de implementación de Pulso** (F7/F8). Esta exclusión no elimina ni reduce el backoffice interno del motor descrito en §25: `debug-console/` es la superficie de operación/observabilidad para el equipo responsable de detección y automejora, con API privada, autenticación y comandos limitados allí especificados. Las rutas privadas de debugging no se convierten por ello en `/api/v1/evolution` ni en contratos de la plataforma. La consola puede usar fixtures/stand-ins etiquetados para componentes externos aún no integrados, sin presentar esos resultados como efectos reales. Una futura experiencia de producto de la plataforma requeriría decisión explícita y reconciliación de alcance.

## 26. Documentación técnica viva y bitácora de construcción

La documentación es parte del producto: un ingeniero nuevo debe poder reconstruir **qué hace el motor, cómo está implementado, por qué se eligió ese diseño, cómo se opera y qué se comprobó realmente** sin depender de la memoria del equipo ni de una conversación. Hay dos ritmos complementarios. La **documentación técnica viva** representa el estado actual del código y se corrige en el mismo PR que lo cambia; la **bitácora cronológica** conserva lo que ocurrió, incluso intentos fallidos y decisiones luego sustituidas. No se duplica un spec entero en cada avance ni se usa la bitácora como sustituto de contratos/arquitectura actualizados.

| Artefacto y ubicación al crear los repos | Contenido obligatorio y dueño | Momento de actualización |
|---|---|---|
| `improvement-engine/docs/architecture/` | Contexto/C4 ligero, límites de procesos, ownership, diagramas de componentes y despliegue, estados e invariantes, modelo de datos/lineage, privacidad; dueño backend/AI/data según módulo | Cambio de flujo, entidad, frontera, store o autorización |
| `improvement-engine/docs/flows/<flujo>.md` | Para F1–F6 y flujos transversales (integración de modelos externos, observaciones de plataforma, consola debug): trigger, input/output, secuencia E2E, algoritmo y gates, entidades/contratos concretos, transacciones, idempotencia, errores/recovery, OTel, pruebas y rutas de código | Mismo PR que implementa o modifica comportamiento |
| `improvement-engine/contracts/` y `docs/api/` | JSON Schema/OpenAPI/eventos/model profiles/config generados o verificados desde tipos Rust; ejemplos wire válidos e inválidos, compatibilidad N/N−1 | Cada cambio de contrato; CI falla por drift |
| `infra/docs/architecture/` y `docs/runbooks/` | Topología local/AWS, Terraform modules/outputs, identidad/IAM/red, deploy/rollback, backup/restore, costos/límites, incidentes y comandos comprobados | Mismo PR de infraestructura y tras cada drill |
| `docs/decisions/NNNN-titulo.md` de repo dueño | ADR: contexto, alternativas, decisión, consecuencias, riesgos, evidencia, condiciones de revisión y `supersedes` | Al elegir o sustituir una decisión material, **antes** de codificar lo irreversible |
| `docs/journal/YYYY-MM.md` de repo dueño | Bitácora append-only con entradas fechadas y enlaces a PR/commit, spec/ADR/tests/runs; hecho vs hipótesis y pendientes | Cada sesión material, corte cerrado, hallazgo/fracaso o decisión; no cada comando rutinario |

**Mientras no existan los repos**, `docs/README.md` identifica el spec vigente y `docs/BITACORA_PULSO.md` inicia el registro verificable. Al ejecutar S0, se importan ambos a Git preservando historial y se fija un enlace canónico por repo; no se mantienen copias editables paralelas en el directorio de planificación. `REVISIONES_SPEC_PULSO.md` es evidencia histórica de revisiones adversariales anteriores, **no** la bitácora diaria. V1 y specs previos son antecedentes, no contratos actuales si discrepan de V2. Cuando V2 se apruebe y el código exista, cada documento técnico declarará `Estado: propuesto|implementado|verificado|obsoleto`, owner, última revisión, commit/versión de contrato aplicable y prueba que respalda su afirmación. El spec describe intención hasta que una prueba y código la conviertan en comportamiento verificado.

**Plantilla mínima de una página de flujo técnico:** propósito y límite; diagrama de secuencia; precondiciones y fuente de datos; pasos exactos con módulo/función y contrato; estados/transacciones/locks; idempotencia y recuperación; autorización/PII; logs-métricas-trazas y panel debug; fallos/unknown; pruebas unitarias, integración, E2E y regresión con comandos reproducibles; cambios de versión/migración; cuestiones abiertas. Usar ejemplos cortos con `evidence_kind` y refs sintéticas, nunca payloads bancarios crudos. Un diagrama debe corresponder a los contratos/código, no sólo representar la visión de producto.

**Entrada mínima de bitácora:** fecha/hora y fase; objetivo; observación y evidencia (ruta/commit/test/run); cambio realizado o no realizado; decisión/trade-offs y ADR si aplica; validación realmente ejecutada y resultado (`pass|fail|not_run`); riesgos/preguntas; siguiente paso/owner. Distingue `propuesto`, `implementado`, `verificado` y `desplegado`. Una prueba fallida o hipótesis refutada queda registrada, no se reescribe para parecer progreso. Se pueden añadir correcciones posteriores enlazadas, no borrar entradas históricas salvo redacción necesaria por PII/secretos.

**Regla de fuente de verdad y resolución de discrepancias.** Contratos wire/versionados gobiernan interoperabilidad; migraciones y código con tests demuestran comportamiento implementado; docs técnicos explican el diseño actual; ADR registra por qué; bitácora explica cuándo y qué se intentó; spec aprobado fija alcance esperado. Si código y doc discrepan, no se declara que uno sea “verdad” sin inspeccionar comportamiento: se abre finding, se corrige código/test o doc en el mismo PR y se deja rastro. Una actualización de decisión sustituye texto vigente y crea ADR `supersedes`; **no** apila párrafos contradictorios en docs vivas. Runbooks sólo afirman comandos probados en el entorno indicado. Nexus puede conservar receipts de contexto, pero **no reemplaza** docs versionadas en Git ni recibe secretos/PII.

**Gate de calidad documental.** PR de feature no cierra si contrato/diagrama/flujo afectado o bitácora no están actualizados; el template de PR pregunta “¿qué docs cambian y cuáles quedan obsoletas?”. CI valida links internos, fences/Mermaid renderizables, schemas/examples, OpenAPI generado sin drift y referencias a módulos/archivos existentes; una revisión humana recorre al menos un escenario desde documento→API/código→test→consola debug. Tras cada fase, un revisor distinto intenta reproducirla **sólo con docs y comandos declarados**. Un fallo de reproducibilidad vuelve a abrir la fase. DoD documental de S0: índice canónico, primera página de arquitectura/flujo, ADRs de fronteras ya acordadas, bitácora en Git y PR template/CI; no esperar al final de la hackathon.

### 26.1 Contrato de ingeniería y documentación para agentes

Este contrato complementa §30.5; es obligatorio por corte, no una fase de hardening final. Spec-driven significa que se aprueba el comportamiento/contrato antes de implementar, pero se construye en cortes verticales RED→GREEN→refactor. Un cambio de alcance vuelve al spec/ADR antes de continuar. No basta generar documentación abundante: debe permitir reproducir y evaluar el comportamiento.

| Entregable versionado | Contenido y criterio de aceptación | Owner |
|---|---|---|
| `AGENTS.md` raíz y, sólo si es necesario, por módulo | Mapa del repo, límites de ownership, comandos comprobados de build/test, TDD, revisión independiente, worktrees, contratos, PII, permisos y DoD. Los archivos subordinados sólo añaden reglas locales; CI comprueba enlaces/comandos y no tolera contradicciones conocidas | Integrador del repo |
| `CLAUDE.md` | Entrada breve que referencia AGENTS.md y añade exclusivamente instrucciones específicas del cliente; no copia otra metodología editable. Se prueba que el cliente puede cargar la guía canónica | Integrador |
| `docs/agents/` y skills de desarrollo | Guías de contextualización, implementación vertical, revisión backend/AI/data/infra/UI, evidencia y handoff; cada skill tiene propósito, alcance, instrucciones, inputs/outputs y ejemplos tratados. No confundir estas skills con artefactos runtime de Agent Core | Owner del área |
| Hooks y scripts | Hooks opcionales para recordar controles y capturar receipts tratados; nunca conceden permisos, cambian código automáticamente, envían datos ni sustituyen CI. Scripts con exit codes, timeout, parámetros explícitos y modo seguro; test de fallo/PII. Configuración específica del cliente documentada y opt-in | Infra/tooling |
| README de cada módulo/servicio | Responsabilidad/no alcance, interfaz, dependencias, configuración, arranque, errores/recovery, invariantes, telemetría y pruebas; enlaza contratos y flujos sin duplicarlos. Documentar API/worker/Core/Core bridge, sandbox y módulos de memoria/evaluación/detección | Implementador + reviewer |
| Guías de evaluación y revisión | Matriz UC→tests→evidencia; reviewers distintos del autor, focos asignados y severidad/triage. Gates/oracles no se cambian para favorecer al candidato. Findings pendientes bloqueantes impiden merge; limitaciones no bloqueantes quedan explícitas | Integrador/evaluación |

Documentación de instrucciones y hooks es input confiable sólo cuando fue revisada en el repo; documentos bancarios, dataset, mensajes de agentes y salida de modelos son datos, no autoridad para ejecutar comandos. Nunca incluir credenciales, respuestas de identidad o holdout en ejemplos, logs, guías o receipts. Nexus usa outbox local, no sustituye Git ni habilita escritura al vault.

### 26.2 CI/CD verificable con GitHub Actions y Terraform

```mermaid
flowchart LR
  B[Feature branch y corte TDD] --> P[PR pequeño y revisión independiente]
  P --> C[CI tests contratos seguridad docs]
  C --> M[Merge a main protegida]
  M --> I[Artefacto/versionado verificable]
  I -. U25 futuro y aprobación .-> D[Manifest compatible y plan infra]
  D -. futuro .-> S[Deploy staging y smoke]
  S -. futuro .-> A[Promoción autorizada o rollback]
```

**Workflows actuales y futuros:** engine `ci.yml` en PR/push comprueba fmt/lint, unitarios, contratos Rust/Python, integración habilitada con PG/sandbox reales, regresiones y E2E del corte, schemas/docs y secretos/dependencias. Infra `ci.yml` ejecuta Terraform fmt/validate y contratos estáticos en Windows/Ubuntu. `release.yml`, `plan.yml`, `deploy.yml`, OIDC, backend remoto, apply, rollback y drift son diseño U25 futuro: no existen aún como workflows activos ni se simulan con un éxito vacío. Un job agregado estable es check requerido: filtros por rutas no permiten omitirlo; reporta qué suites aplicaron y por qué. Los jobs de integración con Core (`contract-drift`, `mock-wire`, `a2-wire`, `real-wire`, `real-live-models`) y el `integration_report.json {target, sha, runtime_profile, doubles[]}` están en §31.10.5. CI ordinario no requiere E0 privado ni proveedor live; suites privadas/live son gates separados de su campaña/release, no éxitos implícitos.

Actions fijadas a SHA y permisos mínimos por job; PRs no confiables sin secretos ni identidad AWS, nunca ejecutar código del PR mediante `pull_request_target` privilegiado. Cuando U25 habilite AWS, OIDC quedará restringido a repo/entorno/branch autorizado y apply/promoción requerirán aprobación de entorno. La concurrencia serializará deploys por entorno; no cancelará un apply en curso. Timeouts y cleanup aíslan contenedores/namespaces; no se usarán runners compartidos con datos bancarios. Ver [guía oficial de seguridad de Actions](https://docs.github.com/en/actions/reference/security/secure-use).

Terraform es autoridad de recursos/IAM/red/retención/alarmas, no de datos de negocio ni decisiones del motor. State remoto cifrado, versionado y con locking; bootstrap del backend separado y documentado. Plan y state pueden contener secretos: artifacts restringidos y retención limitada, no comentarios públicos ni Git. Un plan se invalida si cambia head/config/state; no aplicar un plan anterior. LocalStack valida sólo servicios emulados, no acredita IAM/red AWS. No usar workspaces como única barrera entre entornos: backend/config/IAM separados. Drift se detecta periódicamente y se revisa, no se autocorrige con apply sin autoridad.

Construir una vez y promover el mismo digest; rollback de binarios/config compatibles no equivale a deshacer migraciones destructivas. Prohibidas migraciones destructivas sin estrategia y prueba de recuperación. Release notes vinculan versión, SHAs engine/infra, contratos, digests, validación y limitaciones; despliegue registra receipt. Un tag no prueba deploy y deploy no prueba éxito funcional. Pruebas: CI falla correctamente por schema drift/test rojo, rechazo de identidad desde PR no autorizado, deploy concurrente serializado, plan stale rechazado, smoke fallido impide promoción y rollback restaura servicio sin perder evidencia.

### 26.3 Observabilidad, reliability y aceptación operativa por corte

Mantener el stack de §8: OTLP y un LGTM local; Collector hacia CloudWatch/X-Ray en AWS. No agregar otro backend por cada servicio. [OpenTelemetry](https://opentelemetry.io/docs/concepts/signals/) separa logs, métricas y trazas; ninguna sustituye el journal/audit durable. Logs estructurados llevan servicio/versión/entorno, severidad, evento, outcome y correlación tratada; propagar trace context API→cola→worker→Core/proveedor mediante span links para trabajos asíncronos. Métricas usan labels acotados, nunca IDs de cliente/run ni prompts. Retención, sampling, redacción y límites son config versionada. E2E prueba correlación y ausencia de PII; caída del collector no detiene ni falsea el motor.

| Riesgo y señal mínima | Acción y prueba requerida |
|---|---|
| API: errores, disponibilidad y p95/p99 | Readiness separada de liveness; dependencia indisponible no causa restart storm. Smoke y prueba de timeout/fallo bajo carga |
| Trabajo autónomo detenido: queue age, último heartbeat/progreso, jobs vencidos y retries | Alarma aun con API saludable; recuperar lease y reanudar idempotentemente. Matar worker durante un paso y comprobar ausencia de efectos duplicados |
| Modelos: timeout/error, cuotas, costo, slots y circuit breaker | Backpressure y presupuesto antes de invocar; retry con jitter/deadline sólo cuando seguro. Resultado mutable desconocido se reconcilia, no se repite ciegamente |
| Persistencia/sandbox: espacio, pool/locks, backup age y cleanup | Límite de concurrencia/memoria/disco; fallo controlado y limpieza de namespace; restore comprobado sin borrar hechos |
| Evidencia: gaps/freshness de ingesta, collector/exporter y drift | Gap visible, alerta con fuente/cursor; no aprender de ausencia de spans como ausencia de acciones. Distinguir monitoreo del motor de señales de atención |

Cada alarma declara nombre, métrica/query, ventana, umbral versionado, severidad, owner, destino configurado, deduplicación, runbook y condición de recuperación. Warning informativa frente a critical accionable; mantenimiento silencia temporalmente con vencimiento, no deshabilita permanentemente. El gate local verifica firing y resolved en el backend local; el gate AWS comprueba entrega y recuperación del destino real. Antes de habilitar operación continua se prueban alarma de progreso estancado y presupuesto, restore y rollback. No llamar «monitoreado» a un dashboard sin alertas probadas.

SLOs de API, tiempo de espera/progreso de jobs y frescura se definen por separado, con denominador, exclusiones, ventana y hardware/carga; los valores de §8 siguen siendo objetivos propuestos hasta medirlos. Alertas iniciales de umbral sirven al laboratorio; burn-rate sólo cuando existe SLO medido. No prometer alta disponibilidad multi-AZ para la demo EC2. Runbooks indican RPO/RTO medidos, quién actúa, comandos seguros y evidencia; pruebas de saturación, crash/restart, pérdida de collector/dependencia y backup/restore forman parte de los cortes correspondientes, no sólo del último hito.

**DoD transversal:** aceptación funcional y regresiones verdes; revisión independiente cerrada; CI/head comprobados; docs/ADR/bitácora e instrucciones actualizadas; telemetría tratada observable; fallos y recuperación probados; alarmas/runbook según riesgo; infraestructura reproducible. Los nuevos entregables se adscriben a U01/U05/U06/U07/U10/U24/U25/U28 y a cada servicio afectado; no crean una fase horizontal que bloquee todo el DAG ni afirman infraestructura ya construida.

### 26.4 Selección de prácticas simples y de alto valor, contrastada con fuentes

Investigación oficial revisada el 01-10-2026. Las recomendaciones externas justifican principios; las elecciones siguientes son adaptación de Pulso, no requisitos universales ni funciones ya implementadas. No añadir plataformas nuevas cuando scripts, CI o servicios existentes cubren la necesidad.

| Práctica y fuente | Aplicación mínima en Pulso | Evidencia de aceptación |
|---|---|---|
| [Control de deployments de GitHub](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments) | Un deployment por entorno, promoción con manifest y gates; comprobar en S0 disponibilidad de protecciones para plan/visibilidad del repo. Si no existe aprobación nativa, usar promoción manual auditada desde rama protegida con IAM restringido, no fingir protección | Segundo deploy no solapa apply; PR no autorizado no obtiene credenciales; aprobación/actor quedan registrados |
| [Actualizaciones Dependabot](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference) | Actualizaciones semanales agrupadas por ecosistema compatible, major separadas y sin auto-merge inicialmente; Actions incluidas. Un mecanismo de auditoría por ecosistema, no tres escáneres equivalentes; excepciones con owner/motivo/vencimiento | PR de actualización ejecuta regresiones; vulnerabilidad nueva relevante se triagea sin esconderla en una excepción permanente |
| [Cargo.lock y reproducibilidad](https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html) | Lockfiles versionados, toolchains/pins declarados y builds Rust con `--locked`; cache por OS/toolchain/lock digest, nunca datos/prompts/credenciales. Igual disciplina para Python/frontend e imágenes | Clone limpio resuelve dependencias fijadas; lock inconsistente falla, cache stale no cambia contrato |
| [Estilo Terraform](https://developer.hashicorp.com/terraform/language/style) | Variables tipadas/documentadas y validación de restricciones; módulos por frontera real, no un wrapper por recurso. Exponer settings que cambian, no cada atributo de AWS. `sensitive` oculta salida, no elimina secretos del state | fmt/validate y negativos de variables; inspección tratada de plan/state bajo acceso restringido |
| [Monitoreo SRE](https://sre.google/workbook/monitoring/) | Priorizar síntomas accionables: run sin progreso, queue age, error/latencia y presupuesto; CPU alta sola es diagnóstico, no página automática. Dashboard inicial único con enlaces al runbook y detalle | Inyectar un job bloqueado con API saludable dispara alerta útil y recuperación; ruido repetido se deduplica |
| [Contexto para Claude](https://support.claude.com/en/articles/14553240-give-claude-context-claude-md-and-better-prompts) | Instrucciones breves con comandos y gotchas propios del repo; detalles en guías enlazadas. Un agente nuevo debe verificar estado, leer spec relevante, elegir un UC y ejecutar tests, no consumir toda la bitácora indiscriminadamente | Ejercicio de onboarding desde clone limpio por revisor distinto; no instrucciones duplicadas ni comandos imaginarios |
| [Evaluación de agentes](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Combinar assertions determinísticas de seguridad/outcome con juicio de modelo sólo donde es necesario; guardar resultado, trayectoria tratada y estado final. Repetir trials en suites live no deterministas con presupuesto/versiones fijados, informar dispersión y fallos de harness separados | Candidato aparentemente exitoso pero con efecto indebido falla; repetición no descarta trials malos; fixture perfecto no se anuncia como éxito live |

**Interfaz de desarrollo sencilla:** al implementar U01, un único launcher versionado `scripts/dev` (ejecutado inicialmente desde PowerShell/Windows; backend de contenedores Linux verificado, sin nueva dependencia de task runner) ofrece `doctor`, `up`, `test --suite`, `check`, `down` y `reset --namespace`. Cada comando declara prerequisitos/exit codes; reset valida targets, requiere confirmación explícita y sólo afecta namespaces desechables. Los mismos scripts alimentan CI; un hook opcional usa `check --fast`, no ejecuta todo el E2E tras cada edición. Test rápido por UC y regresiones pertinentes durante TDD; integración/E2E del recorrido antes de merge, live privado en su gate separado. Un test flaky no se «arregla» con retry hasta verde: conservar primer fallo, diagnóstico y owner; cuarentena explícita con vencimiento no acredita gate de una capacidad crítica.

**Orden práctico:** U01/S0 introduce comandos reproducibles, instrucciones, template y CI básico con protecciones; cada servicio añade telemetría y pruebas de recuperación al nacer; U25/U28 cierran publicación/deploy/Terraform/alertas AWS. Dependabot y docs checks arrancan temprano sin un sistema nuevo. Diferir registry privado de módulos, plataforma de docs, merge queue y automatización compleja de releases hasta que un problema medido lo requiera. Los tags manuales revisados y una checklist reproducible bastan inicialmente. Estas decisiones mantienen las 46 unidades del DAG y la disciplina de revisión independiente.

## 27. Implementación del adaptador compatible con Agent Core

### 27.1 Dos autoridades, una relación explícita

Fuente fijada: Agent Core en SHA `86a767474042a566a0dbd6ed23588959f27ebdb3` (`D:\.codex\factored\references\agent-core`). Ver [contratos HTTP, hashes, errores y discrepancias](AGENT_CORE_CONTRATOS_Y_ALINEACION.md). M0–M11, registry rev2 y gateway fueron contrastados con modelos/código; M12 read está implementado e inyectable; navigate y publicación por propuesta no están disponibles. Las cifras de tests upstream no son resultados ejecutados por Pulso. Leer docs/código no acredita servidor desplegado: `agentcore serve` y registry opt-in existen; adapters externos y cableado del constructor/lab siguen pendientes.

La API HTTP del registry está implementada en `agent_core/registry/http.py`, montada bajo el prefijo `/v1/registry` como extensión separada (`registry_extension(service, verifier)`; el `agentcore serve --registry-api` stock la compone y exige `--staff-keys` fuera de demo; en Pulso la compone `pulso-core-runtime`, §31.5.0, y el `serve` stock queda sólo como degradación documentada, §31.5.1). **Esta API no aparece en `contracts/openapi.json`**: ese documento autogenerado sólo cubre `/v1/runs*`, `/transcript`, `/v1/handoffs/*` y `/v1/sessions/*`. Pulso no puede confiar en el OpenAPI generado para el registry; el contrato de esta sección se lee directamente de `agent_core/registry/http.py` (o se acuerda que el generador lo incluya). Rutas confirmadas en el HEAD fijado:

| Método y ruta | Uso | Nota |
|---|---|---|
| `POST /v1/registry/proposals` | Crear propuesta: `{agent_id,origin,title}` | 201; persistir resultado antes de avanzar |
| `GET /v1/registry/proposals/{pid}` | Leer propuesta/estado/rev | |
| `PUT /v1/registry/proposals/{pid}/draft` | `{expected_rev,changes}`: reemplaza **todos** los cambios | nunca tratar como patch |
| `POST /v1/registry/proposals/{pid}/validate` | Valida sin congelar | 200 con `violations`; no inferir éxito por HTTP200 |
| `POST /v1/registry/proposals/{pid}/freeze` | Congela a candidate | falla si hay violations |
| `POST /v1/registry/proposals/{pid}/reopen` | Reabre a draft | invalida hash/aprobación previos |
| `POST /v1/registry/proposals/{pid}/evaluate` | Dispara evaluación | síncrono en Core, representado como job async local |
| `POST /v1/registry/proposals/{pid}/approve` | `{candidate_hash, accept_yardstick_loosened?: bool = false}` | exige rol aprobador + step_up; `409 loosening_not_accepted` si el reporte afloja la vara y no se acepta (§31.7.2) |
| `POST /v1/registry/proposals/{pid}/reject` | Rechaza | |
| `POST /v1/registry/proposals/{pid}/publish` | Publica release | **header `Idempotency-Key` obligatorio**; su ausencia es error de contrato, no reintento válido |
| `POST /v1/registry/aliases/{agent_id}/{alias}` | `{release_id,reason}`: esto es "promote" | separado de publish, humano |
| `POST /v1/registry/releases/{rid}/revoke` | Revoca release | exige rol admin |
| `GET /v1/registry/releases/{rid}` | Detalle de release | no prueba alias activo |
| `GET /v1/registry/releases/{a}/diff/{b}` | Diff entre releases | |
| `GET /v1/registry/entities/{kind}/{eid:path}` | Lee entidad (`?version=`) | |
| `GET /v1/registry/runs/{run_id}/lineage` | Lineage de un run | exige rol constructor |

Errores del registry llegan como `application/problem+json` con `type: urn:agentcore:registry:<code>`; ese namespace no equivale al del runtime (`urn:agentcore:*` fuera de registry). El ciclo real de vida de una propuesta —confirmado sin cambios en `agent_core/registry/models.py` líneas 41-45— sigue siendo `draft→candidate→evaluated→approved→published`, y el flujo de API que lo recorre es `create_proposal` → `put_draft`/`validate` → `freeze` (candidate) → `evaluate` (evaluated) → `approve`/`reject` (approved) → `publish`. No existen rutas de lectura de alias, de versiones ni de listado de propuestas; `GET /entities/{kind}/{id}` sin `?version=` devuelve la última versión, no la de una release (§31.3). Todo 401 es `application/problem+json` `urn:agentcore:problem:credentials_invalid` con `title`, `code`, `trace_id` (§31.2.3).

Pulso conserva Opportunity, ChangeSpec, Campaign, wiki y ImprovementEvidence. Registry conserva Proposal, versiones, Candidate, EvalRun, Approval, Release y aliases. `pulso_artifacts(kind=registry_receipt)` almacena respuesta tratada, operación, proposal_id, rev, candidate_hash, suite exacta/digest, base_release_id, release_id cuando conocido, request_digest, outcome y upstream_commit. Foreign IDs no sustituyen nuestro tenant/revisión. `pulso_artifact_edges` enlaza esos recibos con oportunidad/campaña/cambio; no duplicamos tablas reg_* como autoridad de producción ni alteramos CSV. El mock tiene almacenamiento aislado propio para reproducir estados, nunca recibe SQL arbitrario del scout.

**Código propuesto:** `core/agent_core_wire` (ruta física `crates/core/wire/agent_core@<sha7>/`, §31.4.1) contiene DTOs/nodos/refs conformes al snapshot; `app/artifact_compiler`, `app/registry_workflow`, `app/eval_campaign` los casos de uso; `adapters/agent_core_http` traduce sólo transporte/respuestas (incluido el mapeo `ModelInvocation`/`ModelReceipt` de Pulso contra `LlmUsage`/`Budgets`/`CostCounters` de Core, ver §23); el doble wire y reducer del registry es `platform-sim/registry` (el nombre difiere del simulador de cuatro capas `crates/platform-sim` de §4; ver §31.10.1). Core corre en un único proceso Python propio (`pulso-core-runtime`, §31.5) que monta `/v1/runs` y `/v1/registry` de Core y `/internal/v1/*` de Pulso; Rust usa `adapters/agent_core_http` (registry) y `adapters/core_bridge_http` (`CoreTaskPort`) contra la misma URL base con credenciales distintas. CI prueba ambos procesos y sus contratos. No crear un puerto HTTP por cada idea del producto: sólo operaciones observadas. Endpoints/capabilities futuros quedan separados.

### 27.2 Construir y entregar una mejora, paso a paso

```mermaid
sequenceDiagram
  participant D as Detección e investigación Pulso
  participant B as Builder y compiler Pulso
  participant R as Registry mock compatible o real (ver 27.6)
  participant E as Evaluación Pulso y suite Core
  participant H as Humano autorizado
  D->>B: Opportunity elegible y evidencia tratada
  B->>R: POST /v1/registry/proposals {agent_id, origin:auto_detect, title}
  R-->>B: Proposal con base staging y rev
  B->>R: PUT /v1/registry/proposals/{pid}/draft {expected_rev, changes}
  B->>R: POST .../validate y POST .../freeze
  R-->>E: candidate_hash y release_id_preview
  E->>R: POST .../evaluate {suite_id, suite_version exacta}
  R-->>E: EvalReport
  E->>E: Gate mejora Pulso y final independiente
  E-->>H: Espera aprobación ligada al hash y evidencia
  H->>R: POST .../approve {candidate_hash, accept_yardstick_loosened?}
  H->>R: POST .../publish con header Idempotency-Key
  R-->>H: ReleaseDetail y staging actualizado
  H->>R: POST /v1/registry/aliases/{agent_id}/{alias} (promote) prod si corresponde
  E->>D: Memoria revisada y eventos sandbox independientes
```

1. Obtener manifest de catálogo **Pulso**, con origen explícito (seed/mock o lectura Core), versiones de baseline y capabilities soportadas. No existe GET PlatformCapabilityCatalog nativo ni lectura HTTP de alias: la base se lee con `ReadBase` (§31.3.1) y el catálogo se genera como `capability-catalog.json` (§31.9.4). Propuesta registry toma base de staging; baseline productivo puede ser distinto: registrar ambos. La evaluación habilitante compara base staging; campaña Pulso compara además release runtime seleccionada por objetivo. No llamar a ambas «baseline activo» sin identificarlas.
2. El builder razona libremente en lab autorizado. Exporta únicamente entidades permitidas y evidencia agregada al constructor; no utiliza principal builder Core para leer clientes. Compiler traduce árbol a Flow, clasificación a DecisionModelDef, agente a Agent + prompts/templates/perfiles/flows. Una tool nueva sin executor existente es `dependency_blocked`, no éxito por publicar ToolDef. Output fuera del subset o composición multiagente sin soporte se conserva como alternativa bloqueada.

   `ChangeSpec.disable` es intención Pulso, no operación DELETE nativa: compilar una nueva versión del Flow/Agent que quite la ruta o referencia correspondiente, conservando las entidades publicadas y sus consumidores. El compiler calcula consumidores afectados y exige evaluación de regresión; si no puede expresar la desactivación con entidades soportadas, devuelve dependency_blocked. No revocar una release compartida como sustituto de deshabilitar un comportamiento.
3. `POST /v1/registry/proposals` con `{agent_id,origin:"auto_detect",title}`. Persistir resultado antes de avanzar. `PUT /v1/registry/proposals/{pid}/draft` con `{expected_rev,changes:[{kind,content,docs}]}` **reemplaza todos los cambios**. El motor mantiene lista completa; jamás interpreta PUT como patch. `content.version` es semver exacta. `POST .../validate` retorna 200 con violations; no inferir éxito por HTTP200. `POST .../freeze` falla si violations y produce hash/core closure sólo si pasa.
4. Comparar `auto_bumped` con `expected_derived` (§31.4.5); el `candidate_hash` de freeze es autoritativo, porque `ReleaseDetail` no expone `interrupts`, `language_detection`, `injection_ruleset` ni `max_input_chars` y Rust no reconstruye `release_hash` (§31.4.7). CandidateView **no devuelve closure ni entidades candidatas**: el compiler calcula la clausura de referencias y el `content_hash` por entidad en Rust, y el `candidate_hash`, la cascada y las violaciones `G0-*` los obtiene del dry-run del bridge con el código del SHA, sin crear propuesta (§31.4.6); sin bridge se usa el prefiltro más `POST …/validate`. Si catálogo/base insuficientes, `dependency_blocked`, no endpoint Candidate inventado. Verificar digest/hash y diff local (`GET /v1/registry/releases/{a}/diff/{b}`) contra receipts; no atribuir hash local distinto a Core. Si auto-versiones amplían alcance fuera del bridge, reabrir/detener. Nuevo agente necesita Agent/Flow/templates/LanguageDetection y demás dependencias; bootstrap sintético no dirige discovery.
5. ScenarioCampaign posee splits/oracles/estado bancario propios. Compiler emite **EvalSuite exacto** por agente con `steps(start|turn|confirm)`, `seed.tools`, expect(outcome/actions_verified/escalated) y `thresholds` por cada métrica `gate`/`guardrail` de `Agent.metrics` (contrato de §31.4.11); el sandbox de Core responde colas FIFO por tool, no estado. Caso no expresable no se descarta silenciosamente: oracle adicional Pulso o `not_evaluable`. Suite fijada por versión/digest, no latest. Seeds son sintéticos; estado bancario realista requiere SandboxPort adicional, no sobrecargar JSON seed. Namespace por ejecución, `is_sandbox=true`, reset/teardown aun ante error. Recorded replay de misma release no evalúa candidata ni llama LLMs reales. Compiler de mérito exige Expect no vacío vinculado al bridge, eventos terminales completos y oracle independiente de estado: upstream puede aceptar Expect vacío, Pulso lo rechaza para acreditar mejora. Exploración adversarial adaptativa corre sólo en campaña dev Pulso; se graba/adjudica y convierte en pasos estáticos para EvalSuite. Evaluación adaptativa complementaria usa API sandbox, seed/trace/oracle propios, no un agente dentro de steps. Suite estática no promete conversaciones adaptativas.
6. Worker ejecuta `POST /v1/registry/proposals/{pid}/evaluate` síncrono fuera de transacción PG y lo representa como job local asíncrono. Serializar por proposal/hash y limitar evaluaciones simultáneas. `pass` Core admite primary >= base−noise_margin y los cuatro guardarraíles `platform_*` en 0 y medidos (piso 0 absoluto; ausencia de medición = fallo, §31.7.1); no prueba mejora. Pulso exige además efecto/valor sustentado, seguridad absoluta y cobertura/potencia/final conforme §18. El mock conserva estos dos resultados por separado. Si el mock produce reporte scripted, se etiqueta contract_fixture y **no demuestra automejora**: E2E de efecto necesita baseline/candidato realmente ejecutados en simulador independiente (ver §27.6 sobre el corte de integración real). Adaptador que sustituya por Core no elimina gate Pulso. `CoreEvaluationExecutionProfile` sella máximos escenarios/repeticiones/turnos/nodos/LLMsteps, `jobs_max` (fórmula de §31.7.1), deadlines de proveedor y reserva USD conservadora antes del POST; `max_workers` es 1 en Core (el harness comparte Clock e IDs) y no se sella. Core no ofrece cancel API ni deadline global; desconectar no detiene ThreadPoolExecutor. Cuotas Rust no gobiernan su gateway vecino. Si no puede verificarse enforcement runtime, `live_eval_budget_enforced=false` bloquea ejecución live fuera del presupuesto; timeout conserva reserva/unknown y prohíbe retry concurrente. Receipt adicional conserva candidate_hash, suite exacta/digest, base staging, baseline runtime Pulso, evidence_kind y eval_run_id sólo cuando recuperable.
7. Core fail retorna draft, invalida hash y aumenta rev, deja `last_eval` en `null` y entrega el reporte sólo en el cuerpo 409 `gate_failed` (sin `eval_run_id`): persistirlo, luego renovar GET/reconstruir/freeze antes de iterar (§31.7.1). failed_infra mantiene candidate: retry acotado bajo mismo hash/suite; no approve. Nuevo cambio siempre invalida evaluación/aprobación previa. Final de Pulso sellado no se envía como suite visible al builder: mantener evaluador y credencial de lectura separados. upstream lecturas registry son amplias para builders autenticados: aislamiento de holdout depende de nuestro perímetro, no de un RBAC inexistente allí. Prohibido subir casos/oracles/seeds/texto/feedback granular final_locked a EntityDraft, EvalSuite registry, receipts accesibles, audit export o OTel; GET last_eval es legible a builders autenticados. Se valida en compiler/export y prueba con canario. Credencial separada no protege final si se carga al mismo registry.
8. Ambos gates pass generan `DecisionRequest` con hash, base, diff, incertidumbre, evidencia y suite. Core requiere principal `builder` firmado identificado: `attrs.actor=human` y `auth.level=step_up`; rol `aprobador` para `approve`/`reject`/`publish`/`promote`, rol `admin` para `revoke`/`import`. El bot sólo posee `constructor`, sin actor humano ni admin. UI no firma como humano por recibir click; issuer autorizado emite credencial y Core verifica. Mock reproduce rechazo de bot no humano, emisor incorrecto, session insuficiente (`step_up_required`) y expiración. No persistir credenciales en artefactos/bitácora. Espera no ocupa slot de worker; sweeper reanuda al evento de decisión sin repetir evaluación mientras hash/base sigan vigentes. Si el reporte nativo trae `yardstick_changes`, la decisión ofrece `approve_with_loosening` como opción separada que fija `accept_yardstick_loosened=true`; el defecto no lo acepta (§31.7.2).
9. `POST /v1/registry/proposals/{pid}/publish` con `Idempotency-Key` estable ligada a propuesta/hash (header obligatorio; su ausencia es un error de contrato que el adaptador debe rechazar antes de enviar, no delegar al servidor), conserva ReleaseDetail y staging. `POST /v1/registry/aliases/{agent_id}/{alias}` (promote) a prod es un paso separado, humano; no canary. Staging movido en publish produce proposal_stale: rebase automático a draft upstream, nueva construcción/evaluación/aprobación. Promoción/revocación no tienen CAS/key nativos: el ledger local controla a nuestros writers, no otros escritores Core; registrar before/after si respuesta y no prometer exclusión global. Campaña multiagente crea propuestas separadas con dependency plan: sin transacción atómica entre ellas, bloquear activación parcial si ruta exige todas. Coordinación/grupos runtime sigue plataforma, no inventar node call_agent. `release_id` esperado = `"rel-" + candidate_hash[:16]` (`CandidateView.release_id_preview`); la confirmación de "publicado" y de "promovido" y la clave de publish (`pulso:<proposal_id>:<candidate_hash>:publish`) están en §31.8.2.

### 27.3 Reintentos sin fabricar garantías

| Operación / incertidumbre | Comportamiento requerido | Prueba |
|---|---|---|
| Create enviado, respuesta perdida | `unknown/manual_reconcile`: no query por client key ni list proposals disponible; prohibido retry ciego | Crash después del create, no segunda propuesta automática |
| PUT draft respuesta perdida | GET proposal+changes, comparar rev/request digest; rebasar si cambia, no asumir key idempotente | Igual lista confirmada vs edición concurrente |
| Freeze/approve respuesta perdida | GET proposal estado/hash; avanzar sólo si resultado verificable. Otros actores pueden reabrir: nunca reutilizar aprobación de hash anterior | Reopen concurrente bloquea publicación |
| Evaluate timeout | `unknown`; capturar last_eval.eval_run_id antes de ejecutar; GET posterior devuelve EvalRun y validar ID nuevo, hash, base y suite sellados. Si la propuesta quedó en `draft` con `rev` avanzado, el resultado de un `fail` se perdió: re-freeze y repetir cuenta una evaluación más de la cuota (§31.7.1). Ante writers concurrentes sin atribución demostrable, inconcluso; no asumir eval ID en EvalReport | Reporte previo idéntico no se cuenta como nueva corrida |
| Publish timeout | Repetir **misma** `Idempotency-Key` (header obligatorio en toda llamada a publish, incluido el retry); misma key+otra propuesta da conflicto. Guardar resultado sólo si hash/relación consistente | Retry tras commit devuelve release original |
| Promote/revoke timeout | No retry ciego ni get_by_command_key ficticio; reconciliación autorizada/operacional. GET release no prueba alias activo; lectura de alias del bridge (`AliasState`, §31.3.2) o, sin ella, `alias_unknown`; nunca "prod activo" sólo por release existente | UI no dice prod activo por sólo release existente |
| Pérdida de lease durante HTTP | Fencea publicación local, conserva comando uncertain; siguiente worker reconcilia según operación, no manda duplicado | Worker crash + dos recuperadores |
| Dependencia sin API | `unsupported_capability` **Pulso**, no atribuir ese code al registry; no ejecutar supuesto endpoint | knowledge/groups/canary bloqueados visibles |

Errores Core conservan status/code/raw body tratado además de traducción al Problem interno; el body de error real es `application/problem+json` con `type: urn:agentcore:registry:<code>` — namespace registry que no equivale al del runtime. Fixture gold del código pinneado fija ambos. Settings Pulso configurables no alteran arbitrariamente límites del mock: capacidades/límites disponibles son snapshot versionado distinto de RunConfig. Cambiar enforcement upstream exige nuevo SHA/contrato. Los doce códigos del registry (`validation_failed`, `gate_failed`, `proposal_stale`, `candidate_changed`, `illegal_transition`, `forbidden_role`, `step_up_required`, `integrity_error`, `not_found`, `loosening_not_accepted`, `idempotency_conflict`, `quota_exceeded`) y sus acciones están en §31.2.3; `integrity_error` (500) es `unknown` y nunca se reintenta a ciegas, y `quota_exceeded` (429) es incidente de presupuesto.

### 27.4 Pruebas, drift y salida del mock

Antes de implementar compiler, versionar en Git snapshot de schemas/HTTP/models permitido, `MANIFEST.json {repo, sha, contract_version, files:[{path, sha256}]}` (§31.4.1) y fixtures sintéticos válidos/negativos (§31.4.1). Los schemas de `EvalSuite`, `EntityDraft`, `VersionDocs` y las respuestas del registry no existen en `contracts/schemas/` y se derivan; `agentcore contracts --check` no cubre el registry (no está en el OpenAPI), por lo que la suite dual-run de §31.10.3 es obligatoria. CI compara Rust round-trip y rechazo con validadores Python del SHA, con entorno Python uv.lock fijado; no importa código de main flotante. JSON Schema sólo prueba forma: reglas G0, cierre/hash, lifecycle, auth y idempotencia requieren tests adicionales. Si cambian campos opcionales sin cambio contracts/VERSION, diff de file_digests detecta drift. Actualizar upstream se hace mediante revisión/ADR y contract suite, no descarga silenciosa.

| Caso bloqueante | Aceptación |
|---|---|
| Autodetección no dirigida | Selección por ranking sellado; produce Flow/Agent/DecisionModel cambios relevantes, no documentos sin artefactos |
| Formato/closure | Extra fields, refs rotas, rangos runtime, versiones conflictivas y nodos unsupported rechazados conforme Core |
| Suites/hash | Suite exacta, nueva versión si cambia contenido; candidata hash estable con JCS/Decimal upstream, docs no alteran content_hash; suite drafted sí puede alterar candidate_hash |
| Seguridad/gates | Bot builder no customer ni aprobación; administrador humano tiene excepción gobernada §27.5; Core pass con caída dentro margen no pasa mejora Pulso; Core base unsafe no habilita seguridad Pulso |
| Concurrencia | PUT CAS, staging movido, dos evaluate, pérdida de lease y key publish cruzada sin double efecto atribuido |
| Observaciones | Raw encadenado preservado; seq por run no global; evento sin mapping/humano/exposure unknown; gap bloquea denominador afectado |
| Memoria | Wiki usada y revisada en segundo ciclo; publicar wiki no modifica knowledge_snapshot runtime |
| Debug | Ingeniero recorre Opportunity→drafts→hash→ambos gates→waiting human→release; variantes unknown/unsupported no se presentan verdes |

**Ready to plug no significa ya integrado:** schemas/fixture parity + protocolo exacto permiten cambiar backend del adapter. Activación real requiere Core servidor compuesto disponible, emisor/auth roles, bootstrap/catalog y lectura de alias acordados, transporte de auditoría/run discovery, tools executors y SandboxPort reales verificados con smoke. Lo que falta se registra como dependencia específica sin bloquear detección con fuentes disponibles. No se construye F7/F8 ni se modifica Agent Core en esta tarea. La mecánica exacta de ese tránsito del mock al servicio real está normada en §27.6.

### 27.5 Perfiles, observabilidad y capacidades del contrato 1.3.0

El pin actual es `894fa65575d83420523f33ec1c6919b8965f7ebe` (estas decisiones se verificaron originalmente en `86a767474042a566a0dbd6ed23588959f27ebdb3`, historial preservado; ver la nota de estado al final del índice de §31.1). Son decisiones upstream verificadas, no permisos que un grant Pulso pueda cambiar. **Builder describe el tipo de principal, no si es persona o bot**. El worker Rust tiene identidad de proceso Pulso y, al cruzar el registry, usa una credencial staff de tipo builder/constructor que emite `pulso-core-runtime` (`POST /internal/v1/core-credentials/issue`, CAP-33; la clave privada nunca está en Rust) y que el worker mantiene sólo en memoria; la credencial humana de approve/publish/promote la obtiene por `HumanAuthorizationPort` (§20.2, §31.8.1). Nunca manda su JWT interno como si fuera un JWS Core ni cambia su tipo a service. Formato exacto del JWS (header `{"alg":"EdDSA","kid","typ":"principal+jws"}`, claims y TTL), archivos de claves separados para `--staff-keys` e `--identity-keys` y rotación: §31.2.4.

| Perfil Core | Credencial | Operaciones disponibles |
|---|---|---|
| Bot constructor | builder identificado, constructor, session, sin actor humano | Create/PUT/validate/freeze/evaluate/reopen y lineage; lectura registry. No aprobar/rechazar/publicar/promover/revocar/importar |
| Supervisor | builder humano, constructor+aprobador | Construcción con session; approve/reject/publish/promote staging/prod exige step_up. No revoke/import |
| Administrador | builder humano, `admin` (revoke/import exigen sólo `admin` + humano + step_up, no `aprobador`; el perfil constructor+aprobador+admin es válido pero no necesario) | revoke/import con step_up; import sólo servicio/CLI (`agentcore registry import`), sin endpoint HTTP nativo |
| Customer/advisor/service | Aunque tenga roles | Registry rechaza también GET por forbidden_role; no utilizar credencial del asesor para mostrar drafts |

`GET lineage` exige constructor, no basta ser builder sin rol. Los demás GET verifican builder pero no añaden ese rol; la capa Pulso debe evitar acceso de otro tenant porque esto no equivale a RBAC tenant upstream. Autoaprobación de una persona con constructor+aprobador sigue permitida en Core: nuestro autor es normalmente bot, la aprobación humana queda registrada; no afirmar four-eyes construido.

**Emisores y experiencia de aprobación.** Claves/kid staff separadas de clientes/asesores; TestStaffIssuer usa claves públicas de PRUEBA sólo en sandbox y vive en `testing/`, que no se empaqueta en el wheel: Pulso emite sus propias credenciales de prueba con las mismas reglas de formato (§31.2.4, §31.8.1). Antes de la acción, UI Pulso comprueba roles y pide step-up mediante emisor staff; `403 step_up_required` abre reautenticación, no retry automático como caída de red. Tras renovar credencial vuelve a leer propuesta/hash; si cambió requiere nueva decisión/evaluación, y si no puede usar la decisión todavía vigente. Firma/caducidad se verifican en servidor. `registry_extension(service, verifier)` admite verificador staff separado; `pulso-core-runtime` lo compone (como el `serve --registry-api` stock) y exige `--staff-keys` fuera de demo. Probar aislamiento de emisores, no reutilizar issuer cliente+asesor porque roles coincidan.

**Excepción administrativa de datos.** La prohibición de cliente aplica a bot constructor y supervisor. El diseño Core/contrato de TableAuthz admite administrador humano builder con admin+step_up y scope subject; acceso a campos requiere concesión `(campo,purpose)`. Scopes `subject:<kind>`/`subject:*` son convención del doble, no esquema bancario productivo ya implementado. El constructor automático de Pulso **no** usa admin ni obtiene datos por esta excepción. Consola debug sigue tratada por defecto; una lectura privilegiada requiere propósito, motivo y autorización, se registra en auditoría Pulso antes de servir. Core aún no emite evento de lectura admin permitida (tema18): no afirmar que su cadena la demuestra. Si no podemos auditar la lectura, el adaptador Pulso no la habilita.

**Eventos que cambian detección.** `agent_step.kind` ahora admite tool/final/failed; failed incluye `error_kind` del GatewayError que condujo a gave_up. Scanner agrega tasa de pasos fallidos y runs afectados por agent/flow/nodo/release/error_kind, con denominador de pasos observados y cobertura. Una llamada fallida no es necesariamente falla final del cliente: buscar cierre/resultado posterior. El failure event no trae coste/uso completos: la latencia del paso es observada, costo desconocido permanece desconocido. Debug muestra fallo→rama gave_up→handoff/final y no interpreta falta de tool como omisión intencional. Con un productor sin capacidad agent_step.failed no se exige este evento retrospectivamente.

**Uso conocido no equivale a precio cero.** `GenerationResult.usage_known=false` marca tokens/cost_usd cero de relleno; M8 propaga `LlmUsage.cost_known=false`, incluso en respuesta HTTP exitosa del proveedor. Ranking de ahorro/performance exige cobertura de coste conocido y tarifas versionadas; no libera reserva USD con coste desconocido ni compara unknown contra cero. Límite residual: `LLMAgentPort` convierte GenerationResult a AgentStepResult y no propaga usage_known; ese tipo no incluye la bandera. Una cifra cero de pasos agent no acredita gratuidad. Mantener known/unknown/partial por ruta de captura y evidencia de proveedor; si no se dispone de ella, no declarar reducción de coste para esa ruta. Entradas no canónicas ahora arrojan SchemaError antes de petición: tratarlas como bug de contrato/compilación, no outage o failover facturable.

**Conocimiento y contexto.** M12 read está implementado con snapshot/purpose/audiencia/citas; páginas no prueban éxito de acciones. KnowledgeSource caído devuelve not_found/source_unavailable; navigate devuelve not_found/navigate_unavailable. Publicación por propuesta y fuente en serve siguen pendientes. G0-01 ahora rechaza collect.validator decide antes de publicar, no esperar NotImplementedError en runtime. `EngineConfig.recent_turns` tiene default6 por despliegue: Understand recibe últimas entradas model del mismo run, sin rejected drafts, sin resumen ni arrastre entre runs. No es un campo Agent ni nuestra wiki de aprendizaje. Campañas fijan este config junto al SHA/runtime; no prometer misma conducta sólo por release si cambia el contexto de despliegue.

**Evolución de auditoría.** Añadir error_kind/defaults puede cambiar el hash reconstruido de eventos antiguos: upstream M11 mantiene abierto schema evolution. Export registra versión de productor/manifiesto por run. Verificación usa el codec/schema original del run, antes de añadir defaults nuevos o proyectar. Sin versión/codec suficiente se reporta `chain_verification_unknown`, no chain_broken por defecto añadido ni chain_ok por array vacío. Conservar raw del productor separado de la proyección actual cuando sea autorizado; no migrar inplace los eventos de origen. Nuestro serializer no arregla una cadena antigua Core por sí solo.

| Regresión requerida antes de activar el adapter fijado por SHA | Resultado observable |
|---|---|
| GET registry con cliente/asesor/service firmado y roles | forbidden_role; emisor cliente inválido para callback staff-only da credentials_invalid antes de roles |
| Supervisor session aprueba; bot step_up con roles falsos decide | step_up_required para humano; forbidden_role para bot, sin mutación |
| Supervisor intenta revoke/import; admin step_up lo ejecuta | Sólo admin habilitado; prod aún impide revoke; import HTTP inexistente no se fabrica |
| Admin sin actor/scope/step_up/concesión | Sin datos; constructor bot no hereda privilegios; lectura privilegiada permitida requiere audit Pulso |
| Gateway timeout en nodo agent | agent_step failed/error_kind, gave_up seguro, señal con denominador, no éxito ni coste conocido inventado |
| Gateway éxito sin usage / entrada no canónica | Coste unknown pese a0 de relleno; SchemaError no envía request; no retry como outage |
| collect validator decide y knowledge navigate no disponible | Rechazo de validator no soportado; navigate not_found con motivo explícito; read sí se prueba con fuente |
| Evento histórico verificado con codec de su SHA y proyección actual | Cadena original inalterada; si codec falta unknown; error_kind agregado sólo en proyección |

Los límites 50 cambios/propuesta,262144 bytes/entidad,200 nodos/flow ya fueron ratificados upstream. Retención Core MVP conserva todo; no asumir que nuestro GC puede borrar reg_*. Quotas de auto_detect implementadas: 10 propuestas/24 h y 20 evaluaciones/propuesta por defecto; `RegistryService(quotas=…)` las acepta pero `agentcore serve` no expone flag: se fijan en nuestra composición (§31.5.8) o se observan. Costo por propuesta y activación de constructor task en serve siguen pendientes. Pulso sí limita su loop desde RunConfig/ExecutionProfile; origen auto_detect y API de proposals no implica ejecutar el constructor task Core. Analítica Core proyectada: vistas SQL de eventos+Phoenix, todavía pendientes de construcción; no reemplaza nuestra consola de ingeniería ni ofrece nuevos endpoints. Escalas/calibración/provider smoke y adapters productivos continúan dependencias verificables; servidor arrancable sí existe.

### 27.6 Estrategia de integración: mocks fieles primero, luego servicio real en local

Decisión explícita del responsable del proyecto, normativa para todo trabajo de integración con agent-core: la construcción se hace en **dos cortes obligatorios y secuenciales**, nunca intercambiados ni fusionados. No se declara "integración con agent-core" completa habiendo corrido sólo contra el corte (a); tampoco se sustituye el corte (a) alegando que "ya se probó contra el real".

**Corte (a) — mock/simulador fiel al contrato wire, sin levantar agent-core real.** `platform-sim/registry` reproduce las rutas, métodos, bodies, cabeceras (incluido `Idempotency-Key` obligatorio en publish, que el mock debe rechazar igual que el servidor real) y errores `application/problem+json` de §27.1 y §27.3; su especificación detallada (servidor HTTP real con almacenamiento aislado, no un doble en memoria) vive en §31.10.1, no aquí. Este corte es el que corre en CI por defecto y valida compiler, closure/pinning, gates de evaluación y máquina de reintentos de §27.3 de forma determinista y rápida. Entre (a) y (b) existe el nivel (a2): el `RegistryService` real del SHA en memoria con un `EvalPort` inyectable (§31.10.2); todo reporte rotula `mock`, `a2` o `real local`. **Un mock que pasa no acredita compatibilidad con agent-core real**: sólo acredita que el adaptador de Pulso implementa correctamente el contrato wire tal como fue leído del código fuente en el SHA fijado. Si el código real diverge del snapshot (drift, ver §27.4), el mock seguirá "pasando" sin que eso signifique nada sobre el servidor real.

**Corte (b) — servicio real en local, después y sólo después de (a).** Requiere el ambiente de CAP-58 (§31.11.1): compose con `postgres-core` PG16, job `migrate` (esquema de motor, auditoría y registry sobre `--dsn`/`AGENTCORE_REGISTRY_DSN`, evaluaciones sobre `--eval-dsn`/`AGENTCORE_EVAL_DSN` aparte) y la imagen `pulso-core-runtime` (CAP-24/60), que compone Core y monta `/internal/v1/*`, pin, dry-run y `core-state`; el `agentcore serve --registry-api --staff-keys` stock no expone esas rutas y queda sólo como degradación documentada (§31.5.1). Fuera de demo exige además `--identity-keys`, `--eval-dsn` distinto de `--dsn` y las siete piezas `--tools --authz --transcript --calibration --classifier --field-classifier --grant-active` como fábricas `modulo:atributo` fuera de `testing.*` (el paquete `testing` no viaja en el wheel); sin ellas el servidor no arranca o corre con dobles y se reporta con `doubles[]`. El agente se siembra con `agentcore registry import` (admin humano step_up) antes de la primera propuesta. Procedimiento completo y reproducible: §31.9.3 y §31.11.1. Sólo con esa instancia arriba se ejecutan las pruebas de integración servicio-a-servicio: el adaptador de Pulso contra `pulso-core-runtime` real, no contra el mock. Este corte existe explícitamente para exponer lo que el mock no puede: drift de contrato no capturado en el snapshot, comportamiento real de Postgres bajo concurrencia (PUT CAS, staging movido, dos evaluate concurrentes), y huecos conocidos del propio agent-core que su README declara abiertos — por ejemplo, la demo de transferencia entre agentes advierte expresamente que con `agentcore serve` "todavía no transfiere" porque el proveedor real de selección de especialista sigue abierto. Si una ruta de Pulso toca una capacidad con un hueco conocido de ese tipo, el resultado se registra como `dependency_blocked`, igual que cualquier otro hueco de §27.2-27.4, nunca como integración exitosa.

**Regla de secuencia y de reporte.** No se avanza a (b) sin que (a) esté verde contra el snapshot fijado; no se declara integración real sin haber corrido explícitamente contra la instancia levantada en (b) con el procedimiento de §31.9.3 y §31.11.1 (migraciones de ambas bases, siembra, claves, runtime sin `AGENTCORE_ALLOW_DEMO`), en esa sesión o en CI con el mismo docker-compose. Todo reporte de estado de integración (bitácora, PR, changelog) debe decir contra cuál de los dos cortes corrió: "mock" o "real local (SHA X, migrate+serve verificados)". Un hueco descubierto sólo en (b) no autoriza retroceder silenciosamente a (a) como si bastara: se documenta como dependencia específica (`dependency_blocked` o el código que corresponda) y queda abierto hasta que agent-core lo resuelva o Pulso acuerde un contrato alternativo. Las pruebas deterministas de CI siguen siendo las del corte (a); el corte (b) es smoke/integración periódica, no reemplaza la suite determinista ni se ejecuta en cada commit salvo que así se decida aparte. El reporte incluye `sha`, `contract_version`, `runtime_profile` y `doubles[]`; con dobles de demo se declara "real local con dobles: <lista>", nunca "real".

## 28. Histórico enriquecido E0: complemento, descubrimiento y evaluación

### 28.1 Decisión y alcance

`pulso_muestra_e0` amplía el histórico disponible con detalle operacional. Dataset bancario, histórico enriquecido y nuevos eventos de plataforma alimentan **el mismo motor F1–F6**. No son productos, detectores ni pipelines de negocio separados. Dentro del entorno E0 asumimos sus conversaciones/acciones como hechos operacionales observables y sus políticas declaradas como reglas de la simulación. Su procedencia sigue explícita: un hecho generado puede sustentar una oportunidad válida en ese entorno sin demostrar frecuencia, causalidad o ahorro real del banco. Aprender aquí significa evolucionar memoria, sensores y artefactos evaluados; no implica entrenamiento de pesos.

La muestra actual contiene 2.000 casos seleccionados de disputas, 200 de arranque y 1.800 de reproducción según sus reportes. Esto habilita descubrimiento autónomo **dentro de ese ámbito**. El dataset completo habilita búsqueda de otros frentes y la plataforma amplía evidencia con nuevas interacciones. No fijar las disputas como ganador global ni hardcodear SIG-001/SIG-002 como salida del detector.

```mermaid
flowchart LR
  D[Dataset bancario readonly] --> A[Adapters y contratos de fuente]
  E[Historico enriquecido E0 readonly] --> A
  P[Eventos nuevos de plataforma] --> A
  A --> C[Extracto autorizado a fecha de corte]
  C --> M[Motor comun: descubrir e investigar]
  M --> B[Propuesta compatible Agent Core]
  B --> V[Evaluar y evolucionar]
  L[Labels aislados] --> V
  V --> W[Memoria de desarrollo gobernada]
  W --> M
```

### 28.2 Ingesta y relaciones sin modificar fuentes

Implementar `EnrichedHistoryAdapter` en `adapters/source`; lee Parquet y los contratos actuales `platform_history` 0.5.1 y `evaluation` 0.2.0. Fijar archivos/schema/transform y documentos de políticas/preguntas por digest en SourceSnapshot, declarar contratos borrador y fallar con quality finding ante incompatibilidad. No crear un servicio nuevo ni nuevas tablas de dominio: usar artifacts, cursors y manifests existentes. Los datos originales y aumentados permanecen readonly.

Manifest declara `source_kind=enriched_history`, evidence_kind team_generated para el paquete compuesto, origen de campos suministrados/inferidos/generados, `world_ref`, contratos, partitions, clocks, tablas ausentes y transform refs. Referencias nativas usan namespace de fuente: un case_id igual a un complaint_id no implica misma entidad. complaint_id permite vínculo declarado al dataset; customer_id seudonimizado requiere mapping autorizado, no join directo con customers.customer_id. Cargo candidato conserva link_method inferred, nunca exacto por tener params de tool. No repetir conteo del reclamo al unir ambas fuentes: identidad operacional del caso y registro bancario permanecen distintos, con puente explícito y denominador por grano.

Las vistas del lab exponen case/identity_check/turn/routing_step/copilot_query/tool_call/approval/case_close y timeline según corte. identity_check registra preguntas usadas y resultado, nunca respuestas; éstas tampoco se reconstruyen para prompts, wiki, logs o debugging. timeline es derivada, no otro evento: no contar sus filas más las tablas originales. suggestion/component ausentes significan capacidad no presente en E0; no completar artificialmente. Cada campo sensible conserva tratamiento antes del ModelPort. La autorización del usuario cubre procesar E0 en local y servicios locales controlados (p. ej., LocalStack/MinIO en loopback); no publicar el paquete ni transmitirlo a proveedores remotos. Por ello RunConfig bloquea egress remoto con contenido E0, sin bloquear su lectura/proyección ni el uso de servicios locales. No exportar labels bajo ningún proveedor.

`available_at` es condición de consumo, además de event_time. Como el contrato menciona ingested_at pero sus fields no lo especifican, el adapter comprueba presencia física. Si falta, usar modo replay explícito: disponibilidad asumida al timestamp de cada evento, con ingestion_lag=0 etiquetado como supuesto, no timing de producción probado. approval_request está disponible en requested_at y approval_decision en decided_at: la primera no incluye decisión futura. case_close sólo tras closed_at; señales de ventanas completas sólo tras window_end. Los resultados posteriores de labels nunca entran en lecturas de descubrimiento.

### 28.3 Descubrimiento común y expectativas independientes

El adapter publica observaciones normalizadas y conserva payload fuente; no inventa eventos Core, hashes audit ni cuatro capas donde sólo hay humano/copiloto. MetricSpecs habilitan familias según cobertura. Dataset permite detectar magnitud/segmentos; E0 permite consultas repetidas, secuencias de acciones, verificación, errores/reintentos, espera de aprobación, transferencias y abandono; telemetría futura permite fallos por capa, costo y regresiones. No todos los sensores tienen que funcionar sobre todas las fuentes.

Scout puede descubrir motivos/secuencias libremente en texto tratado y SQL del lab. Cálculo comprueba soporte por casos y asesores distintos, denominador elegible, tiempos y cobertura; verifier refuta éxito aparente, mezcla de canales y acciones no verificadas. Repetición no demuestra buena práctica: oracle de políticas del sandbox valida acciones/precondiciones independientemente del humano. El paquete actual incluye docs/policies.md y docs/security_questions.md v0.1 borrador: son especificaciones del entorno de prueba, no políticas bancarias reales ni executors ya implementados. Su interpretación se convierte en fixture/policy/oracle versionados antes de evaluar; si una regla no es ejecutable, not_evaluable, sin deducirla de labels.

`signal.parquet` es referencia precalculada de comparación, **no entrada del detector, scout, builder ni memoria inicial**. Guardarla en partición evaluator_reference igual que labels; reproducir señales desde eventos sin leerla. Evaluador compara mecanismo, población, soporte y evidencia, no igualdad textual ni IDs. Hallar oportunidades nuevas es resultado permitido: valorar reproducibilidad, seguridad y mejora con casos posteriores, sin exigir pertenecer a las tres señales preparadas. El paquete no es sólo benchmark: sus eventos autorizados sí son materia de aprendizaje.

### 28.4 Dos protocolos de evaluación explícitos

| Protocolo | Construcción | Reproducción y memoria | Qué mide |
|---|---|---|---|
| Congelado | Arranque, config y artefactos fijados | Casos posteriores en orden; no actualizar candidato, sensores o wiki usados durante la campaña | Generalización de una versión |
| Continuo prequential | Arranque inicial, mismas interfaces | Por caso: fijar estado anterior, predecir/actuar, puntuar aparte; después incorporar sólo eventos cuya disponibilidad ya venció; nuevas propuestas pasan gates | Evolución autónoma a través del tiempo |

Separar métricas, manifests y budgets: no comparar agregado continuo con congelado sin explicar versiones/exposición. Empates opened_at forman cohortes: no usar otro caso abierto al mismo instante como pasado. Para cada decisión usar sólo casos abiertos antes del evaluado y eventos disponibles hasta su instante de replay; nunca insertar un episodio completo al abrirlo. Reproducción respeta acciones/estado, no obliga a copiar diálogo humano: el simulador puede ramificar con otro siguiente paso. Un log grabado por sí solo no es banco stateful ni prueba contrafactual de una nueva tool; ScenarioFactory construye sandbox con tools reales de test y bridge verificable (§18/27), o declara mecanismo proxy/no evaluable.

Labels lo lee sólo evaluador aislado; entrada redundante allí se toma de case, nunca se monta labels en el lab. `human_actions` es baseline, human_errors no es instrucción para el builder y final_* son outcomes posteriores. Feedback permitido para desarrollo proviene de simulador/oracle y partición de desarrollo, no de casos finales sellados. Protocolos E0 son campañas distintas de final confirmatorio §18: reutilizar reproducción para ajustar el sistema la convierte en benchmark de desarrollo, no holdout virgen. Una afirmación confirmatoria requiere familia/split final separado y sellado antes de iterar. Análisis agregado de resultados no devuelve respuestas por caso al builder ni wiki.

Métricas: oportunidades corroboradas/nuevas/refutadas, tiempo hasta hallazgo en reloj replay, cobertura de descubrimiento frente a referencias, propuestas viables y mejora segura por versión; resolución/acción correcta y escalamiento con numerador/denominador explícitos, acciones inseguras, latencia y costo conocido/desconocido. Sin referencia exhaustiva no llamar precision/recall global al conteo contra tres señales. Reportar PT/casos difíciles aparte y solapamientos, sin sumar cohortes no disjuntas. R4 y otras políticas son supuestos del entorno: su distribución restringe automatización, no prueba rentabilidad bancaria real.

### 28.5 Entrega incremental y aceptación

| Slice | Objetivo y comportamiento requerido | Pruebas antes de cerrar |
|---|---|---|
| E0-A fuente | Ingerir manifests y contratos, validar entidades/refs, preservar namespace y aislar labels/signal | Unit schema/clocks; integración Parquet readonly, joins seudónimos rechazados, timeline sin doble conteo; ausencia de tabla y columnas extra |
| E0-B descubrimiento | Ejecutar F1–F3 con eventos de arranque, producir evidencia desde fuentes, no desde diagnósticos | Integración cambia/elimina signal y labels sin alterar entrada/hallazgos con mismo provider replay; evidencia alterada sí cambia soporte; E2E descubrimiento sin ID esperado hardcodeado |
| E0-C replay | Ejecutar congelado y continuo separados con cortes y decisiones registrados | Unit cohorte/reloj; integración approval futura invisible y cierre tardío excluido; regresión contra futuros eventos/labels; crash/resume no puntúa ni aprende dos veces |
| E0-D mejora | Construir artefacto Core, probar base/candidato y memoria gobernada | E2E oportunidad→EntityDraft→gates; error humano repetido no se acepta por coincidencia; oracle faltante bloquea; propuesta nueva fuera de referencias se evalúa sin rechazo automático |
| E0-E aislamiento | Evidencia, debugging y resultados con fuente/split/versión/coverage | Seguridad labels/final ausentes en prompts, logs y wiki; restricción de exportación aplicada; contrato UI muestra qué aprende y qué espera sin requerir clicks |

DoD documental y futura implementación: el mismo pipeline soporta original-only, enriched-only y fuentes combinadas con deduplicación; descubre sin respuestas precargadas, propone una mejora evaluable y sigue aprendiendo de nuevos eventos. El caso de éxito no queda limitado a cargo no reconocido ni a una tool predeterminada. Los conteos de SAMPLE/COVERAGE son referencias reportadas, pendientes de recalcular mediante E0-A; este ajuste del spec no acredita tests ni resultados ejecutados.

### 28.6 Paquete actualizado: identidad, políticas y canales

Snapshot auditado el 01-10-2026: history 0.5.1 / evaluation 0.2.0, 2.000 casos y split 200/1.800 comprobados en Parquet. Hay 845 identity_check (396 trigger abono y 449 canal_sin_identidad), todos verified; 774 usan dos preguntas y 71 tres. No hay filas huérfanas ni ended_at anterior a started_at en esos checks; ninguna llamada abono_provisional carece de check verified previo en el mismo caso en la comprobación realizada. Esto no demuestra ausencia de otros errores humanos ni auth segura en producción.

Adapter normaliza identity_check.questions: contrato VARCHAR[] pero almacenamiento VARCHAR con JSON array válido en las 845 filas. No contar caracteres como preguntas; parsear JSON y validar IDs/longitud/tipos. turn.text_source es columna física adicional de procedencia, se declara en transform/manifest y no se utiliza como predictor/oracle. suggestion/component siguen sin archivos. ingested_at sigue ausente en todas las tablas presentes; permanece el supuesto replay de disponibilidad, no se inventa timing de ingesta.

identity_requested se observa en started_at; result/correct/lista final de preguntas y duración sólo en ended_at. Si no hay tiempos por pregunta, no publicar SQ3 anticipadamente desde el registro final. expected_identity_check es objetivo evaluator-only, no condición de routing del agente. La condición de verificación se calcula desde policy/canal/acción autorizados. Los datos reales de respuestas no se materializan en prompts ni memoria; el fixture del servicio de identidad las valida por frontera determinística y devuelve sólo evidencia de resultado. No permitir que Jev/LLM decida si una respuesta es correcta.

case.channel observado: phone/email/web_chat/app_chat. Los orígenes branch (70) y regulator (22) no son canales de sucursal del sistema: se modelan como llamadas salientes; 22 casos regulator están en phone. Conservar origin y channel separados y probar A2/firma supervisora. Descriptor caller_number/phone no demuestra autenticación de voz: el sandbox declara su identidad de canal mediante fixture/evidencia, no por inferir confianza desde un número o del texto del usuario.

Políticas y preguntas son supuestos gobernados del entorno. Fixture debe cubrir identidad fallida, tercera pregunta, falta de movimientos, sesión vencida/corte y renovación; negación de acceso a otro titular; abono humano y límites por nivel; confirmación de bloqueo; disputa >90 días; regulador y portugués. Históricos positivos de identidad no cubren negativos, y R2 >90 días no aparece en los cargos muestreados (<60 días). Casos adicionales se generan en sandbox como pruebas, no se insertan en E0 ni se atribuyen al dataset original. KBA de este ejercicio no se presenta como arquitectura de autenticación bancaria aprobada.

README prohíbe publicar el paquete o enviarlo a proveedores/servicios remotos. Está autorizado usarlo en servicios **locales** controlados por el equipo (proceso local, Podman/Compose, LocalStack o MinIO en loopback); esta autorización no habilita llamadas a OpenRouter, servicios hosted de Jev/LLM ni otros endpoints externos. El runtime de descubrimiento E0 debe usar adapters/provider replay locales, sin transmitir filas, texto, prompts ni derivados identificables fuera del host/stack local. Smoke live de modelos emplea fixtures independientes permitidos, no conversaciones E0 enmascaradas. Reemplazar el directorio crea otro SourceSnapshot/digests; no reutilizar caches, baseline ni resultados sellados del snapshot anterior. La comparación histórica aquí usa el spec previo 0.4.2/0.1.0 y documentación conservada, no un diff byte a byte de una copia antigua inexistente en esta auditoría.

**Estado de implementación a no sobrestimar:** los cortes U03, U04-B, U08-E, U12-E y U13-E implementan contratos/admisión de componentes; no constituyen por sí mismos un `source-projector`, un comando local que los componga sobre los archivos reales ni una reproducción con evaluador separado. Mientras el source-projector no lea el esquema del dataset original y emita el `PreparedSource` autorizado, `original-only` debe responder `unsupported_source` con la tabla/capacidad faltante. Un contrato JSON válido o un test sobre fixture sintético no demuestra compatibilidad ejecutable con el dataset original. El source-projector E0 y su runner se aceptan sólo tras pruebas sobre las versiones/archivos locales declarados en §28.7.

### 28.7 Contrato de la vertical ejecutable: adapters → detección → salida → evaluación

Esta sección convierte la meta “probar un escenario real localmente” en un contrato comprobable. **Es requisito objetivo; no afirma que el camino ya esté integrado.** El primer escenario de aceptación usa el E0 aumentado, porque su historial operacional aporta señales observables; el adapter original se entrega como capacidad separada. Que E0 esté soportado no habilita silenciosamente el dataset original, y viceversa.

#### 28.7.1 Boundary de entrada y proyección segura

El CLI orquesta un `SourceProjector` (no pasa paths a Scout/LLM/Core). El projector identifica la fuente mediante un manifest versionado, verifica digest/versión/esquema antes de abrir las tablas, hace joins en el borde de datos y devuelve `PreparedSource`: metadatos sellados más una proyección tipada con las columnas/relaciones permitidas. No devuelve filas originales, un `DataFrame` irrestricto ni un path local a consumidores posteriores.

Para E0, el contrato de compatibilidad exacto es `platform_history` v0.5.1 y `evaluation` v0.2.0, once archivos/tablas Parquet: nueve operacionales (`case`, `identity_check`, `turn`, `routing_step`, `copilot_query`, `tool_call`, `approval`, `case_close`, `signal`) y dos de evaluación (`labels`, `timeline`). El adapter valida presencia, tipos físicos y lógicos, nullability, enum/domain, PK/FK, relaciones con case, clocks y campos extra; las discrepancias generan hallazgo tipado y nunca alias guessing ni éxito vacío. `identity_check.questions` requiere parseo y validación como JSON array cuando el almacenamiento físico sea `VARCHAR`; `turn.text_source` adicional debe quedar declarado en el transform y no se vuelve predictor por aparecer en Parquet. `timeline` es derivada y jamás se suma con sus eventos fuente. Una columna adicional no se consume hasta que un contrato/versionado la autorice.

La proyección sólo incluye hechos requeridos por el detector activo y aprobados por un allowlist (dimensiones operativas, eventos, resultados de herramienta, tiempos y estado con availability). Se excluyen respuestas KBA, contenido de evaluador, datos directos de identidad y texto original no tratado. `customer_id` ya seudonimizado puede formar un token de agrupación por run cuando un detector requiera continuidad; el valor fuente y cualquier mapping reversible se quedan en el projector y no se registran ni salen en artefactos. Los textos con marcadores ya tratados se habilitan sólo por un permiso de campo y una ejecución local explícita; no se admiten en logs, consola, memoria persistente ni llamadas a proveedor remoto. Cada join comprueba cardinalidad, parent case y namespace; huérfanos, duplicados o cruces inválidos se contabilizan como calidad y no se reparan por heurística.

`signal.parquet` conserva el tratamiento de §28.3: la presencia en el schema no autoriza su uso como detector input. Se clasifica `evaluator_reference`/excluded hasta una política aprobada que pruebe productor, semántica, ventana y disponibilidad. `labels` y `timeline` sólo se abren mediante el evaluador (§28.7.4). Para que una prueba de no fuga sea real, el comando `run` debe terminar correctamente aun si `evaluation.json` está ausente o el path del evaluador es inaccesible.

El adapter original requiere su propio source contract + `SourceProjector`, sin alterar tablas/CSV ni inferir que los nombres parecidos al E0 significan lo mismo. Hasta mergear y probar ese adapter, la matriz de capacidades anuncia `original: unsupported`; `run --source original` retorna ese estado y no intenta el sensor E0. No afirmar soporte por la existencia de `call_center_interactions.v1.json`, por validar un header fixture ni por leer directamente el CSV sin mapping seguro. Cuando el projector exista, debe consumir el contract, producir proyección/cobertura/digest, y probar lectura readonly, nullability, los joins autorizados, tratamiento PII y corte temporal contra los bytes reales locales.

#### 28.7.2 Arranque y reproducción sin fuga temporal

`Arranque` y `Reproducción` son controles de protocolo del harness confiable, no features ni labels que recibe el motor. Para la muestra versionada: arranque = 200 casos iniciales ordenados por `case.opened_at`; reproducción = 1.800 restantes en orden ascendente. El harness puede usar `labels.rank/split` para comprobar la partición documentada y construir un manifiesto opaco de miembros; no serializa esos campos, sus valores ni `labels.case_id` al `PreparedSource`, prompts o artefactos de descubrimiento.

El Arranque crea una línea base/sensor/candidato a partir sólo de casos del prefijo y eventos admisibles a su cutoff final sellado. En reproducción el harness se mueve caso por caso. Antes de evaluar el caso objetivo `i`, congela la versión activa; sensores, queries, memoria y propuestas sólo observan eventos de casos anteriores cuyo `event_time` y `available_at` sean `<= opened_at(i)`. Si la fuente aporta `ingested_at`, también se exige `ingested_at <= opened_at(i)`; E0 sin reloj físico admite únicamente el perfil `replay_at_event_time` de U04-B (lag 0 supuesto y visible). Empates de `opened_at` forman una cohorte no ordenable: ningún caso de esa cohorte informa a otro. Eventos posteriores/cierre/decisión del caso `i` se entregan sólo a su evaluador después de sellar el resultado de `i`, y pueden afectar casos futuros sólo una vez vencida su disponibilidad. En modo continuo, cualquier update de memoria/config/sensor ocurre después de puntuar y produce una nueva revisión para `i+1`, nunca muta el estado que generó la decisión actual.

Hay dos informes/campañas distintos: frozen mantiene candidate/config/sensor/memoria fijados para toda la reproducción; prequential/continuo aplica la secuencia de fijar→decidir→sellar→evaluar separado→actualizar/versionar. No mezclar sus métricas, exposición ni denominadores. La partición reproduction deja de ser holdout confirmatorio si resultados por caso o métricas se usan para tunear; registrar cada iteración como desarrollo. El stress-test (Portugués/difíciles) se reporta aparte, sin filtrar su pertenencia al detector.

El adaptador valida cortes por campo, no sólo el corte global. `approval_request` nace en `requested_at`, `approval_decision` en `decided_at`; `identity_check` no revela resultado/preguntas completas antes de `ended_at`; `case_close` no existe para el motor antes de `closed_at`; ninguna señal de ventana completa puede usarse antes de `window_end`. El fixture `replay_at_event_time` declara la suposición y no demuestra latencia de ingestión de producción.

El `run_manifest` persiste el compromiso exacto de lectura: digest del snapshot y contratos, versión de transform/allowlist, detector/config, protocolo, partición, cutoff efectivo, perfil de disponibilidad, lista de tablas/campos realmente leídos, conteos incluidos/excluidos y cursor/cohorte. No persiste identificadores fuente. Un retry/restart con la misma idempotency key debe reconstruir el mismo ámbito; si cambió cualquiera de esos inputs crea una corrida nueva, no continúa una corrida distinta. Tests alteran bytes, cutoff, allowlist y orden/cursor y comprueban rechazo o nuevo run. Con E0 `replay_at_event_time`, `available_at` y `ingested_at` derivan del perfil asumido y se reportan como tales, nunca como clocks observados.

#### 28.7.3 CLI local, corrida y salida atómica

La aceptación requiere comandos ejecutables, no sólo tests de biblioteca. La sintaxis es una interfaz estable a congelar al integrar el runner; estos nombres describen el contrato funcional:

```powershell
improvement-engine source validate --kind enriched_history --input <path> --contract-version 0.5.1
improvement-engine run --source <source-snapshot-ref> --protocol frozen --partition arranque --as-of <RFC3339-UTC> --execution-profile local-simulated --output-root <path>
improvement-engine run --source <source-snapshot-ref> --protocol frozen --partition reproduccion --as-of <RFC3339-UTC> --execution-profile local-simulated --output-root <path>
improvement-engine evaluate --run <sealed-run-dir> --evaluation-source <path> --contract-version 0.2.0
```

`source validate` hace lectura readonly y emite coverage/schema findings sin filas/IDs/texto. `run` resuelve source contract, snapshot, projector, temporal protocol, sensores/workflow local y sella una corrida; **no recibe argumento de evaluación ni abre `labels`/`timeline`**. `evaluate` es proceso/puerto separado, verifica primero hashes/manifests, hace el join interno de evaluador y publica sólo agregados. El comando indica de forma explícita modo local y qué capacidades son `simulated`, `dependency_unavailable` o nativas; el mock de Agent Core ejecuta interfaces/productos del motor para probar el flujo, pero nunca escribe `native_success`/`released` ni crea receipts con autoridad externa. El camino E0 no invoca servicios hosted y no exporta muestra o derivados.

El scope allowlisted del manifest es una lista exacta de tablas y campos consumidos por cada etapa; descubrir archivos adicionales no amplía el scope. Al validar E0 se debe auditar el schema y las relaciones de las nueve tablas operacionales aunque algunas queden excluidas del detector input (`signal`) o sólo estén disponibles post-outcome (`case_close`). Evaluación (`labels`, `timeline`) pertenece a otro scope y otro proceso. La ausencia de una tabla requerida, un campo, una relación o una regla de dominio produce un quality finding/bloqueo explícito; nunca se interpreta como cero ni se omite silenciosamente.

`original` falla cerrado: hasta que exista mapping source-contract específico verificado contra el dataset original, `run --source original` termina `unsupported_source` antes del sensor, Scout o simulador, con lista segura de capacidades faltantes y exit code 2. No basta con producir un `PreparedSource` vacío, enumerar hashes/headers o terminar `completed` sin observaciones. La tabla de capacidades y el manifest deben reflejar `original: unsupported`.

Cada corrida se escribe a `<output-root>/.staging/<run-id>` en el mismo volumen. Cada archivo usa creación exclusiva, schema versionado, `flush`/`sync_all`, length y digest; el manifest de run se escribe al final con source/schema/transform/policy/config hashes, corte, protocolo, runtime adapter, estados y lista exacta de outputs. Al confirmar la integridad, renombrar atómicamente el directorio staging al destino final único; lectores ignoran staging. Fallo antes del rename deja run `incomplete` no elegible; no sobrescribir run previo. Si filesystem no garantiza rename atómico de directorio, devolver `dependency_blocked` y documentar mecanismo alternativo seguro antes de llamarlo completo. Retry sólo reanuda si idempotency key y todos los commits inputs/config coinciden; de lo contrario crea nueva corrida. No escribir `completed` previo a publicación atómica.

Salida mínima: manifest, coverage/quality summary, run-event timeline safe, señales agregadas con numerador/denominador/missingness/cutoff, evidencia/candidate draft commits y status de cada gate. No copia archivos de fuente, path de usuario, customer/case/agent IDs de origen, texto, KBA, labels/timeline o prompts. Para explicar evidencia por caso, usar referencias opacas/run-scoped y sólo mostrarlas en debugging local protegido; los resultados que puedan exportarse son agregados. Un run `completed` significa que el pipeline declarado terminó, no que encontró oportunidad, Native/Core funcionó, el candidato calificó o el banco mejoró.

Estados terminales no colapsables: `completed`, `no_supported_signal`, `unsupported_source`, `insufficient_evidence`, `dependency_blocked`, `failed`, `incomplete`. `no_supported_signal` sólo cuando hubo población no vacía/cubierta y corrió un detector soportado. Fuente vacía/invalidada no equivale a cero. Original sin projector/mapping => `unsupported_source` con lista de tabla/capacidades faltantes, exit code documentado y ningún fallback a E0.

Exit codes: `0` para evaluación local terminada con fuente soportada (incluye `no_supported_signal` o `insufficient_evidence`); `2` para contrato/schema/fuente no soportados (`unsupported_source`); `3` para fallo operativo/dependencia al completar pipeline; `4` para violación de aislamiento o protección. Cuando se pudo escribir, el resumen y manifest preservan el status tipado aunque el proceso retorne 2/3/4; un fallo de escritura conserva únicamente staging/incomplete, jamás un resultado completed. Estos códigos se congelan con las pruebas de CLI.

**Criterio de parada/no-op para E0:** si el smoke de referencia reproduce 0 señales positivas, 13 observaciones faltantes y 3 candidatos inciertos, el resultado aceptado es terminal `no_supported_signal` o `insufficient_evidence` según cobertura efectiva, ruta formal `do_nothing`, cero candidato ejecutable/propuesta/release y resumen con numeradores, denominadores y razones de missingness/incertidumbre. Las tres candidaturas inciertas no se elevan ni se reintentan en bucle. Sólo una nueva revisión de fuente/config/detector explícitamente versionada permite otro run; resultados vistos convierten reproduction en conjunto de desarrollo, no holdout confirmatorio. Los conteos son fixture de regresión de la muestra auditada, no constante universal: si cambian los bytes debe cambiar el commitment y reportarse el resultado recalculado, sin forzar esos conteos ni una oportunidad.

#### 28.7.4 Evaluador aislado y medición

La evaluación inicia sólo con `run_manifest` ya comprometido. Un crate/binario de evaluator consume `evaluation.json`/`labels.parquet`/`timeline.parquet` readonly y un mapping opaco mantenido por el harness; no comparte `PreparedSource`, ledger de query, contexto Jev/LLM/Core o filesystem reader con `run`. Separar carga/config/permisos: el proceso `run` debe poder ejecutarse bajo una cuenta que no tenga acceso al directorio evaluator. En tests, dicho path será un sentinel que falla ante cualquier open; comprobar que el run produce el mismo digest cuando evaluation files están presentes, ausentes o alterados.

El evaluador verifica source/run/evaluation contract digests, joins caso sólo dentro del namespace/campaign sellado, aplica campos por `evaluation.json` `use` (entrada/objetivo/referencia/diagnóstico/posterior/orden) y calcula métricas de cada protocolo/cohorte con denominador y filas excluidas explícitos. Los campos `expected_*`, `human_errors`/human actions, `final_*` posteriores y timeline son visibles exclusivamente al evaluador después de sellar la salida. Ningún resultado individual vuelve al builder/sensor/memoria durante esa misma corrida. Una iteración posterior puede usar sólo un reporte agregado firmado/hasheado y explicitamente permitido para desarrollo, creando nuevas revisiones y etiquetando reproducción como conjunto de desarrollo, no holdout confirmatorio.

Los artefactos simulados mantienen valores de ejecución diferenciados en summary y timeline por etapa; no reportar tasa de nativo ni diferencia uplift si la ejecución fue el simulator. El evaluator reporta referencia E0 descriptiva y safety/oracle; B compara sólo resultado sandbox medido con tool effects/readback, nunca atribuye causalidad en la distribución bancaria sólo por labels. Unknown/missing/blocked permanecen en la base y denominadores reportados, no se eliminan silenciosamente.

#### 28.7.5 TDD, integración y Definition of Done

| Prueba | Criterio observable | Regresión obligatoria |
|---|---|---|
| Source projector unit | Acepta schema real E0 0.5.1/0.2.0 y produce proyección allowlisted; valida `VARCHAR` serializado de `questions` donde aplique | Schema/version/type drift, required table/column ausente, columna nueva no permitida, enum/null/PK/FK/cardinalidad erróneos, texto/PII/KBA/label omitidos |
| Source projector integration | Smoke local opt-in lee las nueve tablas operacionales Parquet reales readonly; evaluator files no se pasan al projector de run. El evaluador, por separado, lee `labels` y `timeline`. Ambos validan sus relaciones sin modificar bytes. CI usa fixtures sintéticos con mismo schema; ningún dato E0 se versiona | Remover/alterar `signal` no cambia el hallazgo; cambiar `labels`/`timeline` no cambia el digest de decisión del run (sí puede cambiar el digest separado de evaluación); `signal` permanece en cuarentena; corrupt parquet/relación rota falla explícito |
| Cutoff/harness unit+integration | Arranque 200 y Reproducción 1.800 por opened_at/rank esperado; empates en misma cohorte; actualiza memoria sólo entre casos | Evento/field/ingest/cierre/decisión futuro invisible; monotonic timestamps; reload/crash no aplica dos veces; split/rank no llega al motor |
| CLI arranque E2E (gate A) | `source validate` y ejecución local de Arranque sobre E0 readonly; produce manifest/salida atómica y motivo honesto aunque no detecte oportunidad | Cero señal positiva + 13 missing + 3 inciertas termina no-op/do_nothing; no candidato ejecutable ni loop; fuente alterada cambia commitment; gate no afirma replay/evaluador |
| Reproducción E2E (gate B, pendiente del gate A) | Replay 1.800 caso-a-caso conforme al cursor/cutoff sellado y protocolo; informe separado frozen/continuous | Empates, reinicio, corte de campo y cambio de inputs; cualquier consulta de outcomes/futuro bloqueada; inspección/tuning degrada explícitamente a desarrollo, nunca holdout validado |
| Evaluador aislado E2E (gate C, pendiente del gate B) | Proceso/permiso separado evalúa sólo run sellado y publica agregados; `run` termina sin acceso al path evaluator | Sentinel ante open, labels/timeline presentes/ausentes/alterados no cambian decision digest; joins/denominadores correctos y no reingreso de resultados individuales |
| Cobertura schema E0 | Validar nueve tablas operacionales y relaciones contra bytes reales readonly; validar aparte dos tablas evaluator; manifest lista campos realmente consumidos | Falta tabla/campo, drift, enum/null/PK/FK/cardinalidad o datos corruptos bloquean; `signal` no afecta detector, `case_close` sólo post-outcome |
| Source original fail-closed | Sin projector real: `unsupported_source`, exit 2 antes de invocar sensor/simulador, capacidades faltantes seguras | No `PreparedSource` vacío ni `completed`; no fallback E0; sólo declarar soporte después de mapping/joins/PII/cutoff sobre CSV real readonly |
| Evaluator isolation | `run` no puede abrir la carpeta del evaluador y produce el mismo digest de decisión independientemente de `labels`/`timeline` | Intentar serializar labels/campos finales dentro de PreparedSource, prompt, event, draft o wiki falla en compilación o en runtime |
| Atomic-output integration | Run output final sólo aparece tras manifest/hash/rename; retry exacto idempotente | Inyectar crash tras cada escritura, target preexistente, hash alterado, acceso concurrente y rename no atómico jamás crea `completed` parcial |
| Original source | Hasta que projector esté implementado: retorna `unsupported_source` sin procesar, cero candidatos | No fallback a E0, no inferencia por nombre de campos; tras implementación sólo green con source-contract-specific fixtures y Parquet/CSV real readonly |
| Release-quality | `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`, `python -m unittest discover -s tests -p "test_*_contract.py" -v`, `python contracts/validate_fixtures.py`; revisión independiente de seguridad/data, backend/runtime, test y E2E | Evidencia de comando/head/branch exacto; compose smoke se reporta separado y no se inventa si backend Podman está unavailable |

**DoD escalonado; no confundir con estado implementado:** gate A = Arranque ejecutable y no-op/detección honesta sobre E0 local con source manifest completo; gate B = Reproducción temporal completa con commitment/cursor persistidos; gate C = evaluator aislado y agregado. Sólo A permite afirmar “smoke de Arranque runnable”; sólo A+B+C y cobertura real de tablas permiten afirmar “E2E runnable y evaluable”. Ninguno permite llamar confirmatorio al holdout una vez inspeccionado/tuneado, ni afirmar causalidad/lift bancario. Dataset original permanece `unsupported` hasta que su projector real pase pruebas readonly y fail-closed. No se afirma que replay, evaluator o validación completa de tablas esté implementado por la existencia de código/fixtures parciales.

#### 28.7.6 Trazabilidad entre contratos existentes y la integración pendiente

Esta tabla separa qué demuestra hoy cada corte del repo de lo que debe probar la vertical runnable. La presencia de módulos de Core o pruebas con fixtures no equivale a leer los Parquet reales ni a ejecutar el flujo CLI completo.

| Evidencia en `improvement-engine` | Lo que sí respalda | Lo que no respalda todavía |
|---|---|---|
| `crates/core/src/enriched_history.rs`; `crates/core/tests/enriched_history.rs` | U04-B, projection in-memory E0, cutoff/availability y exclusiones de contenido no permitido | Parquet filesystem adapter, E0 SourceProjector, source-projector original o comandos CLI |
| `crates/core/src/e0_query_lab.rs`; `crates/core/tests/e0_query_lab.rs` | U08-E capability de consulta y receipt E0 opacos con source evidence ya proyectada | Importar/parsear datasets completos o separar físicamente un evaluador |
| `crates/core/src/e0_deterministic_sensor.rs`; `crates/core/tests/e0_deterministic_sensor.rs` | U12-E mide el tipo de evidencia E0 autenticada con corte/digest | Escanear Parquet, elegir split, ni garantizar que caller pasó facts reales en orden |
| `crates/core/src/autonomous_scout.rs`; `crates/core/tests/autonomous_scout.rs` | U13-E conserva proveniencia de señal/receipts en candidato Scout | Runner, caso no dirigido de E2E, CLI, o métricas de resultado del benchmark |
| `crates/runner/tests/cli_e2e.rs` y `crates/source-adapters/tests/source_adapters.rs` (si están en la rama de integración) | Contratos candidatos para ejecutar end-to-end y leer schemas de source adapters | No cuentan como main/mergeados ni como CI verde mientras branch/head/checks no lo confirmen; fixtures sintéticos no sustituyen el E0 local real |

Por tanto, al reportar avance se usarán tres marcas: **componente implementado** (módulo/test slice), **integrado runnable** (comando end-to-end sobre E0 real con outputs sellados y evaluator aislado) y **original soportado** (source-projector original + pruebas contra el dataset original readonly). Sólo la primera tiene evidencia en las filas de módulos Core; las otras dos requieren las aceptaciones de esta sección.

## 29. Pulso usa Agent Core para evolucionar artefactos Agent Core

### 29.1 Arquitectura de ejecución y ownership

**No basta exportar al final ni convertir todo en agentes.** Detección/verificación/construcción son capacidades compuestas por Flow, rule, tool read/compute, decide con DecisionModelDef/Jev y, sólo donde aporte, node agent. Agent Core describe su propio funcionamiento como un ciclo **Understand → Decide → Act → Verify → Escalate (U-D-A-V-E)**: recibe un mensaje, entiende qué quiere la persona, sigue un guion validado (un Flow), actúa con red de seguridad y deja un rastro auditable y reproducible. Es agnóstico al negocio — un agente, un flow, una política o una plantilla son datos; el motor sólo los interpreta — y contempla tanto agentes de cara al cliente como internos (copiloto del asesor, constructor de agentes). Ese ciclo público **no es un mapeo 1:1** con los módulos internos M0–M12 que organizan el código (`CLAUDE.md`, `docs/specs/motor/00-indice.md`): Understand cruza M6 (guardas de entrada) + M7 (vistas/tokenización); Decide cruza M2 (intérprete) + M5 (DecisionModel/Jev); Act es M2 + M3 (acciones de escritura); Verify es M8 (validador de respuesta); Escalate es M10 (escalamiento/handoff). M0 (dominio/puertos), M1 (flows/validación estática), M4 (ciclo del turno), M9 (acceso y API — más amplio que sólo "runs"), M11 (auditoría/transcript/replay) y M12 (conocimiento) sostienen el ciclo sin corresponder a una sola etapa U-D-A-V-E. El registry (`agent_core.registry`) es explícitamente "unidad 2", fuera de la tabla M0–M12; los eventos salientes (`agent_core.outbound`) también quedan fuera de M0, con spec propia. Agent es el descriptor de ejecución de una release, no obliga a que cada etapa tenga personalidad, ReAct o LLM. El monitor periódico no es un LLM despierto permanentemente: scheduler y sensores deterministas abren tareas cuando corresponde. La autonomía surge de su coordinación durable, no de improvisar tiempos/reintentos en un prompt.

```mermaid
flowchart TB
  H[Dataset + E0 + eventos de plataforma] --> D[Control plane Rust: cortes y sensores]
  D --> S[Core Flow: investigar con SQL y agent cuando haga falta]
  S --> V[Core Flow: verificar con reglas y Jev o LLM]
  V --> G[Gate determinista: evidencia y oportunidad]
  G --> B[Core Flow: construir con node agent cuando haga falta]
  B --> C[Compiler y validacion estatica]
  C --> W[Core Flow: write_draft y verify]
  W --> E[Evaluacion Core + gate Pulso]
  E -->|iterar en desarrollo| B
  E -->|pass| A[Aprobacion humana y registry]
  E --> M[Memoria gobernada]
  M --> S
  A --> P[Plataforma consume nueva release]
  P --> H
```

Rust no interpreta nodos Core: agenda, crea extractos, calcula métricas, controla presupuesto, prepara escenarios y guarda evidencia/estado. Core interpreta Flow, decide/agent, sus budgets, tools y auditoría. Su PostgreSQL tiene runs/reg_* propios y base separada de evaluaciones; PostgreSQL Pulso conserva diez tablas pulso_*. Pueden compartir servidor local, no ownership de tablas. Core externo gobierna ejecución y secretos de modelos; el consumidor reserva cuota y registra receipts sin otro gateway ni recalibrador de Jev.

El corte local añade servicio `pulso-core-runtime` (proceso = imagen = servicio compose; directorio `core-bridge/`; nombre único, ya no `agent-core-runtime`) con imagen/commit fijados, alongside control-api/worker/Core/PG/S3/sandbox. Terraform despliega esa misma frontera de proceso como servicio ECS Fargate del entorno demo (§4.1, CAP-62); health y versión observable por servicio. No se migra Core a Rust. Contrato de `CoreTaskPort` permite mock fiel para avanzar cuando falta composición; distinguir runtime=contract_mock de runtime=agent_core, y no llamar integración real a una simulación.

### 29.2 Qué cambió realmente en el snapshot actual

Fuente de este análisis `86a767474042a566a0dbd6ed23588959f27ebdb3` (2026-10-02; el pin vigente hoy es `894fa65575d83420523f33ec1c6919b8965f7ebe`, historial preservado), sucesora de `53e729d624c8284e906249df84c1a1df84cc8d40` citada en una revisión previa de este spec. `contracts/VERSION` y `agent_core/domain/version.py` ahora declaran **1.3.0** (frente a 0.5.0 del snapshot anterior): el salto no es un simple bump, trae ADRs y features completos que cambian supuestos de diseño de esta sección. **SHA y digests de schemas/código siguen siendo el pin**, no la versión semver sola; no asumir compatibilidad entre snapshots por coincidir el número.

Entre ambos snapshots entraron, entre otros: doble vara de evaluación con guardarraíles de plataforma y `forbidden_role` (ADR 0020, varios commits `feat(registry)`), un DSL de métricas propio (`MetricDef`/`MetricExpr`, `SCHEMA_VERSION` 1.2.0, separado del contrato general 1.3.0), la demo de transferencia entre agentes (ADR 0021, `SCHEMA_VERSION` 1.2.0 para ese contrato) con su mundo de prueba (`tests/fixtures/registry-transfer-demo/`, `tests/fixtures/runs-transfer/`) y spans OTel de transferencia, y un cliente de chat por terminal para `agentcore serve`. No se han ejecutado tests upstream en esta revisión de este spec; contract CI debe probar imports/validación/schemas/servidor antes de habilitar un feature, no sólo comparar `VERSION`.

| Primitiva | Evidencia actual | Decisión Pulso |
|---|---|---|
| agent con input_view y output_schema | LLMAgentPort + M2 existentes; sólo read/compute dentro del bucle | Usar para investigar/verificar/diseñar; inputs explícitos, no asumir que recibe automáticamente el mensaje original |
| write_draft | RiskClass, M3, G0-23/AG-02, BuilderToolExecutor y reg_draft_writes existentes | Crear/guardar/congelar/reabrir/evaluar con act→verify sin confirm; jamás aprobación/publicación por bot |
| Idempotencia del constructor | Service acepta key/get_write; API HTTP aún no la expone para esas operaciones | Usar BuilderToolExecutor local al runtime; REST externo conserva restricciones §27.3; no inventar GET /writes |
| Quotas | Quotas inyectables: 10 auto_detect/24 h, 20 evals/propuesta | Presupuesto Pulso adicional, no elevar ni esquivar origin; 429 produce espera/detención explicada |
| knowledge read | KnowledgeService/RunState.pages/validación de citas y composición EngineDeps; `read` construido (`SCHEMA_VERSION` 1.0.0), `navigate`/`search` siguen fuera | Contexto fijo del run disponible con fuente; navigate not_found; serve no aporta fuente y registry bloquea cambios snapshot |
| Métricas DSL (ADR 0020) | `MetricDef`/`MetricExpr`, `SCHEMA_VERSION` 1.2.0 propio en M0, funciones de `evaluation/metric_eval.py`, `evaluation/scoring.py`, `evaluation/yardstick.py` | Candidato a que Pulso lea métricas nativas de evaluación para sus propios gates; pendiente de evaluar en detalle, no integrado todavía — no confundir con el gate efectivo de RegistryService |
| `eval_suite` (antes "EvalSuite") | `agent_core/registry/suite.py` define literalmente `EvalSuite`, `Scenario` y `DatasetScenario` junto a `Step`, `ToolReply`, `SandboxSeed`, `Expect`, `Assertion`, `ScenarioPrincipal`; escenarios `scripted` (motor real con tools en sandbox) o `dataset` (ids/hash reales, **deshabilitado**, abierto #20). `registry/evaluation/ports.py` define los Protocols `EvalPort`, `ScenarioHarness`, `SandboxPort` y `Judge`; `composition/evaluation.py` aporta `EngineScenarioHarness` (principal fijo `customer`) y `registry/evaluation/local_sandbox.py` el sandbox local | [NUESTRA] Un solo formato; no inventar segunda `EvalSuite`. Implementar nuestro propio `ScenarioHarness` (§29.8) en vez de modificar el de Core |
| Transferencia entre agentes (ADR 0021) | Nodos, tipos, eventos, TurnEngine, `AgentSelector`/`TransferContract`, demo `registry-transfer-demo` y tests existen; el propio README confirma que con `agentcore serve` el directorio está cableado pero "el proveedor real de esa elección sigue abierto", por lo que "la demo por serve todavía no transfiere" | Capacidad futura con huecos conocidos (equivalente a `dependency_blocked` en vocabulario de este spec), no algo que Pulso deba orquestar ya; no usar transfer para coordinar tasks de evolución |
| Serve y staff | serve.py, registry opt-in, staff_verifier separado, eval-dsn, cliente de chat por terminal | Retirar afirmación de servidor inexistente; fuera de demo `serve` exige siete fábricas reales (`tools`, `authz`, `transcript`, `calibration`, `classifier`, `field-classifier`, `grant-active`) que hoy sólo existen como dobles bajo `testing/` (no empaquetado); la CLI no acepta extensiones ni `limits` (§31.5.1) |

README/TEMAS conservan afirmaciones antiguas sobre servidor/conocimiento: prevalece evidencia por símbolo y composición, no el resumen de estado.

### 29.3 Composición de flujos, decisiones y agentes

Primera composición mínima: **un Agent task descriptor `pulso-evolution`**, con entry_flow de evolución y rutas de investigación, verificación y construcción. Como referencia concreta de cómo luce una composición Agent Core real y no un ejemplo abstracto, usar la demo publicada en `tests/fixtures/registry-demo/`: el agente `agents/atencion@1.0.0.yaml` compone el flow `flows/disputa-cargo@1.0.0.yaml`, dos decision_models (`match-cargo@2.0.0`, `understand-turno@1.0.0`), una policy (`escalamiento-disputa-monto@1.0.0`), un perfil de modelo, un ruleset de inyección, un detector de idioma es/pt y cinco tools (`buscar_transacciones`, `convertir_moneda`, `obtener_pqr`, `radicar_pqr`, `seleccionar`), con una `releases/demo.yaml` que fija todo el conjunto; los caminos grabados en `tests/fixtures/runs/` (`resuelto`, `cancelado`, `escalado_por_monto`, `uncertain_verify`, `step_up`, `interrupcion`) muestran las ramas reales de éxito, escalamiento y reintento que `pulso-evolution` debe reproducir en su propio dominio (scout/verifier/builder) en vez de inventar nombres de nodo nuevos donde el patrón ya existe.

La primera tool recibe `args={}` y obtiene contexto del binding privado de la invocación, no de slots de entrada aún no validados. El bridge Python mantiene un contexto aislado por invocación (no variable global compartida), autorizado por tenant, principal builder, job, stage, grant, presupuesto y release. Al recibir el run_id generado por Core, registra su binding antes de permitir efectos. Devuelve facts booleanos `is_scout`, `is_verifier`, `is_builder`; rule compara booleanos, no literales de negocio incrustados. Stage recibido desde el cliente o prompt nunca concede permisos. No es un agente LLM monolítico: puede ejecutar una rama enteramente sin LLM. No usar subflow deshabilitado; las ramas del primer Flow son nodos explícitos y comparten entidades cuando procede. Stages se ejecutan como runs distintos para mantener leases, presupuestos y gates entre etapas; no hace falta concatenarlos con transfer — y, dado que la transferencia entre agentes (§29.2) todavía no cierra su proveedor de selección en `serve`, no es candidata a reemplazar esta separación por runs en el corto plazo.

Separar otro Agent/release sólo ante permisos distintos, presupuesto independiente, necesidad de evaluación/versionado independiente o aislamiento adversarial comprobable. Verifier tiene run/contexto/prompt y evidencia separados del scout aunque reutilice el descriptor; si eso no garantiza aislamiento requerido se extrae a Agent propio. Invocable_by builder, subject_kinds=[]; sin subject cliente ni credencial admin. Fuentes son extractos tratados autorizados por Pulso, no acceso a clientes con identidad builder. Caso bancario individual no se convierte en subject del constructor.

| Trabajo | Primitiva preferida | Cuándo escalar complejidad |
|---|---|---|
| Ventanas, conteos, joins, soporte y tiempos | SQL determinista / tool compute y rule | No LLM para recalcular ni decidir permisos |
| Categoría de señal, selección finita o juicio booleano/escala | decide + DecisionModelDef + Jev calibrado | LLM si el problema requiere explicación abierta o hipótesis nuevas |
| Investigar causas, refutar argumentos, diseñar artefactos nuevos | node agent dentro de Flow, con input_view y budgets | Agent independiente sólo si cambia frontera de permisos/contexto/release |
| Secuencia conocida de construcción/verificación | Flow tool(write_draft)→verify y ramas explícitas | No ReAct para improvisar protocolo de escritura o aprobación |
| Agenda, colas, disponibilidad, persistencia y aprobación | Control plane determinista / registry | No agentes ni Jev para leases, autoridad o idempotencia |

| Capacidad / entrada lógica Pulso | Flow y primitivas | Salida y consumidor |
|---|---|---|
| scout: snapshot/cutoff/lab/wiki/metric refs | tool read de contexto autorizado → agent con input_view, SQL/wiki read/compute → end | HypothesisSet tratado + evidence refs; TaskAdapter valida y persistencia Pulso; no opportunity corroborated directo |
| verifier: hipótesis, extracto y método sellados | rule/compute para schema/soporte/temporalidad, decide/Jev para juicios tipados y node agent sólo para refutación abierta; run separado | VerificationReport con contradicciones, queries y coverage; gate determinista calcula status |
| builder: oportunidad/bridge/capabilities/base/wiki | agent con alternativas y schema interno; segunda fase específica produce DRAFT_OUTPUT_SCHEMA exacto → write_draft/verify | ChangeSpec/evidencia por adapter y EntityDraft[] por registry; ambos enlazados por digest |

`CoreTaskInvocation` interno contiene tenant/pulso_run/job refs, agent+release pin, input_artifact_refs, lab_grant_ref, config/budget/cutoff/information_partition, deadline y logical key. TaskAdapter convierte a **CreateRunBody{agent,subject:null,input,lang}** y header Idempotency-Key de runs, autenticado con principal builder autorizado. No añade nuestro envelope al body Core. Cada input se proyecta a slots bajo nombres conocidos; Core los crea claimed, no validated. Flow usa tool read de contexto para verificar grants/digests y devolver facts tipados: referencias que aporta el modelo no autorizan montaje ni lectura.

`CoreTaskReceipt` enlaza core_run_id/release, estado/outcome, output refs/digest, audit refs y presupuesto conocido/unknown; además compromete criptográficamente el binding autorizado `{tenant_id, job_id, grant_ref, attempt, task_binding_ref, input_commitment}`. Un receipt exitoso de otro tenant, job, grant, intento o input no es reutilizable. Guarda firma/correlación externa, no token staff. Agent outputs no son hechos bancarios verificados. G0-22 impide llevar facts origin agent directo a rule, escritura bancaria o end.output_map; no diseñar Flow que lo eluda. Salida de análisis se captura desde facts del RunState por adapter autorizado dentro de composición confiable (sin endpoint público inventado); la salida de un nodo `agent` no es recuperable por HTTP (`GET /v1/runs/{id}` y `RunResult.output` no la contienen y G0-22 la excluye de `end.output_map`): sólo `UnitOfWork.load_run` in-process, con whitelist (§31.5.5), se valida fuera del modelo y se registra en Pulso. end marca tarea terminada, no demuestra verdad de hipótesis.

Identidad del runtime interno: configurar IdentityVerifier/AuthzPort para builder autorizado en este servicio de evolución separado de atención al cliente. --identity-keys valida invocación del run; --staff-keys valida registry opt-in. No asumir que una credencial válida en registry pasa automáticamente start_run. La credencial de BuilderToolExecutor es builder/constructor propia, no PrincipalType.service aunque algún texto de diseño diga "credencial de servicio". Ningún grant lab sale del modelo; los adapters verifican tenant/run/cutoff/partición en cada consulta y ligan Core run a job mediante binding previo autorizado. Tests prueban credencial de cliente rechazada en runtime interno y constructor rechazado en atención de clientes.

El bridge es el proceso `pulso-core-runtime` (§31.5.1): compone Core in-process **dentro de Python**, monta sus rutas privadas vía `ApiDeps.extensions` y lee `RunState` con el `uow_factory` de Core; no es cliente HTTP de `agentcore serve` ni se ejecuta dentro de Rust. Expone transporte privado Pulso definido abajo; no es una nueva API upstream. Priorizar prueba vertical task con inputs→agent→fact→receipt antes de implementar todos los roles. En builder sólo facts.<draft>.value.changes con esquema DRAFT_OUTPUT_SCHEMA exacto puede alimentar args de write_draft (G0-22); título, origin, propuesta/rev y grants vienen de slots/facts deterministas validados. Antes de put_draft el wrapper verifica digest del payload contra EntityDraft[] aprobados por compiler y grant ligado a job/proposal/agent. Si el modelo cambió el payload, se recompila y requiere nuevo grant; schema válido no basta. Test adversarial cambia tool/policy/ruta entre fases: denied sin write. Salida de una escritura derivada no adquiere autoridad bancaria.

### 29.4 Jev, LLM y libertad segura del lab

Toda decisión Jev pasa por DecisionModelDef con output_schema, providers/calibración y nodo decide — la misma primitiva de M5 que, en U-D-A-V-E, resuelve la parte "Decide" del ciclo (y, combinada con M6/M7, el "Understand" de la demo `atencion`: p.ej. `understand-turno@1.0.0` clasificando el turno antes de que `match-cargo@2.0.0` decida la correspondencia de un cargo). Ejemplos propios de Pulso: clasificar familia de señal, elegibilidad para investigar, tipo de intervención o suficiencia de evidencia. JevProvider traduce preguntas tipadas; confidence del proveedor no sustituye p_cal. Low-confidence tiene rama explícita de investigación/no decisión, jamás autorización por defecto. Para razonamiento abierto, causas y diseño usar agent + Prompt + ModelProfile structured:prompted y LLMAgentPort; no un SDK paralelo en worker.

El motor conserva gobierno de datos, reservas y conciliación del uso; Core conserva ejecución Jev/LLM y credenciales. U10 valida la integración externa autorizada y sus receipts, no implementa proxy. Los límites nativos de Core se verifican con pruebas; si no alcanzan el límite sellado, se bloquea la ruta live. Un usage desconocido nunca se convierte en cero ni libera automáticamente la reserva.

Libertad de lectura significa **capacidades generales**, no cien tools por query. Nodo agent requiere tools read/compute para acceder a información que no cabe en input_view: `lab/query`, `wiki/read` y `wiki/explore` tienen contratos amplios con ámbito/grant y redacción; el modelo decide SQL, navegación y métodos libremente. Implementar bajo ToolExecutor, no shell irrestricto ni acceso al filesystem host. Las tools son interfaz nativa y control de efecto, no un wizard. SQL temporal puede crear derivados efímeros dentro del lab autorizado sin efecto durable; publisher de wiki y cambios persistentes conserva gates Pulso. Knowledge read fijo (M12, `read` construido con `SCHEMA_VERSION` 1.0.0; `navigate`/`search` siguen fuera) no reemplaza esa wiki libre ni su publicación gobernada.

### 29.5 Lo que E0 enseña sobre el output

No entregar sólo insight o texto: producir **unidad de mejora versionada y verificable**, compuesta de artefactos Core, dependencias, mecanismo, ámbito, pruebas y límites. Output de dominio `ImprovementPackage` usa CapabilityBundle/ChangeSpec existentes; no nueva tabla ni EntityKind inventado. Distinguir paquete para atención de paquete para mejorar propio sistema, target_system=attention/evolution, en metadata Pulso fuera del JSON Core.

| Evidencia enriquecida descubierta, no precargada | Output candidato nativo | Requisito que debe acompañarlo |
|---|---|---|
| Consulta recurrente del asesor con mismas lecturas | ToolDef read/compute + Flow que la usa + Agent tools_allowed | Executor y permisos/data contract, paridad con lecturas originales, cobertura; ToolDef sin implementación no resuelve nada |
| Secuencia estable y segura de acciones | Flow rule/tool/confirm/verify + Agent actualizado | Precondiciones, ramas error/handoff, confirmación cuando corresponda, oracle de estado; no copiar error frecuente |
| Regla de siguiente paso o sugerencia | DecisionModelDef/Policy/Template/Flow y Agent de copiloto | Adapter que muestra recomendación, público asesor y permisos; suggestion_rule no es EntityKind Core |
| Motivo no cubierto que exige razonamiento | Agent + Flow agent + Prompt/ModelProfile + tools permitidas | Input_view explícito, budgets, fallback, pruebas e integración externa de modelos; límites de autonomía claros |
| Varios subtemas requieren composición | Varios Agents/Flows con plan de dependencias | TaskCoordinator para tareas de evolución; transferencia conversacional (ADR 0021) sólo tras resolver el proveedor de selección pendiente en `serve` y las incompatibilidades conocidas; no node call_agent |
| Falta conocimiento o instrucciones útiles | Prompt/Template/Flow con contexto autorizado; propuesta de KnowledgeSnapshot si soporte futuro | snapshot importado/approved según canal actual; publicación por propuesta bloqueada; skill = composición de entidades, no schema nuevo |
| Sensor/hipótesis de automejora deficientes | Nueva versión de Agents/Flows/DecisionModelDef/Prompt del sistema + MetricSpec Pulso si requiere SQL | Tests no dirigidos, detección negativa, seguridad y mejora contra versión anterior; mismas barreras, no autoactivación |

Cada paquete incluye EntityDraft[] y refs exactas, executor_dependency_refs, evaluación nativa vigente, evidencia de mejora Pulso, policies aprobadas del entorno, fuentes/cutoff, consumidores afectados, config y rollback a release previa. `eval_suite` **vigente** (formato de `agent_core/registry/suite.py`: `EvalSuite`/`Scenario`/`DatasetScenario`) es kind del registry fuera de EntityKind runtime. Agent.metrics usa sólo catálogo actual; discovery con joins/SQL, tiempos de disponibilidad y calidad E0 sigue MetricSpec Pulso, no el DSL de métricas de Core (`MetricDef`/`MetricExpr`, `SCHEMA_VERSION` 1.2.0) extendido clandestinamente — ese DSL es, como mucho, una fuente futura de señales nativas para los gates propios de Pulso, pendiente de evaluar en detalle antes de integrarse. No endurecer/aprobar policies bancarias sólo porque patrón humano se repite.

### 29.6 Ciclo autónomo, concurrencia y automejora del propio motor

1. Scheduler/coalescer reclama job con lease y prepara snapshot/lab tratado; fijar Agent/release/Flow y stage autorizado antes de dispatch. Agenda o señal dispara, usuario sólo excepcional; algunos jobs son enteramente SQL/reglas sin modelo.
2. CoreTaskPort invoca scout con key estable; lee receipt antes de repetir. Timeout no cancela run ni demuestra que no gastó: unknown, no duplicar trabajo hasta reconciliar estado.
3. Worker calcula soporte desde receipts y dispara verifier como task independiente; puede paralelizar investigaciones distintas con lanes/budgets §8, no dos jobs del mismo logical key. Core transfer (ADR 0021) no es fan-out, llamada de retorno ni DAG de tareas — y, mientras su proveedor de selección siga abierto en `serve`, tampoco es un mecanismo disponible para coordinar stages.
4. Gate determinista registra oportunidad/bridge o refutación; builder propone alternativas y compiler valida refs. Emitir diagnóstico de dependencia faltante, no artefacto verde ficticio.
5. Flow constructor autorizado usa BuilderToolExecutor con credencial builder/constructor propia: create_proposal→verify, put_draft→verify, validate, freeze→verify y evaluate→verify. El readback del executor no contiene por sí solo todos los bindings: para pass o failed_infra recuperable, el coordinador consulta el EvalRun completo del RegistryService y verifica eval_id nuevo, hash del candidato, base y suite contra el manifest esperado. Para fail se aplica la recuperación de §29.8 aunque last_eval haya desaparecido; no se habilita publicación. El recibo de write también se liga a operation/key/request_digest. Un verdict favorable o HTTP200 aislado no constituye ese gate. Fail/inconcluso vuelve al job de desarrollo con nueva revisión y consumo de cuota.
6. Gates Core + Pulso y final separado cuando procede; aprobación humana, publish y promote siguen registry, no herramientas del nodo agent. No await_approval task; PendienteHumano es decisión durable Pulso sin slot ocupado.
7. Memoria publica aprendizajes autorizados; nuevos eventos generan nueva detección. Candidato del sistema evolutivo sólo corre en sandbox sobre snapshots sellados; la release activa de scout/verifier/builder no cambia durante la investigación.
8. Si se propone modificar el detector o juez, **no puede aprobarse a sí mismo**: baseline de evaluación, oracle y guardrails fijados por control plane fuera del candidato. Promoción humana de nueva release evolutiva; activar siguiente job usa nuevo pin, runs antiguos mantienen el anterior. Se protege el circuito contra aprender a fabricar hallazgos o aflojar el gate — el propio ADR 0020 (doble vara, `forbidden_role` cuando una propuesta toca guardarraíles de plataforma) es la versión que Core ya aplica a sí mismo para este problema; Pulso reutiliza ese patrón, no inventa uno paralelo.

Idempotencia de writes nativa existe sólo en métodos/BuilderToolExecutor, no como header de draft REST. Pulso ledger sigue necesario para ownership, presupuesto, cancelación y recovery. API REST evaluate sigue síncrona; serve eval max_workers=1 por Clock/IDs compartidos. Backpressure local no cancela petición en curso; límite global de evaluaciones por servicio y deadline/fallo de infra explícitos. No prometer exactly-once de llamadas LLM ni bloqueo global ante writers ajenos. Quotas upstream se verifican también en carreras con tests reales antes de usar al máximo; valor configurable Pulso no sobreescribe permiso ni límite Core implícitamente.

### 29.7 Implementación y pruebas contractuales

| Slice | Construcción concreta | Criterio verificable |
|---|---|---|
| AC-A pin/compose | Imagen Python Core por SHA, adapters de tools/authz/knowledge y artefactos mínimos publicados de prueba | Core validate/import, task start, staff separado; schemas regenerados en CI y divergencias explícitas, no comparar sólo VERSION |
| AC-B scout | Agent task/Flow agent/input_view + SQL/wiki generales sobre DuckDB por job | Descubre de E0 sin labels/signal y de dataset con cobertura; input faltante falla seguro; consulta libre no escapa tenant/grant |
| AC-C verifier/Jev | Agent task independiente + DecisionModelDef/decide calibrado | Refuta evidencia alterada; low-confidence no corrobora; no salida agent directa a rule/end/escritura bancaria |
| AC-D builder | DRAFT_OUTPUT_SCHEMA, BuilderToolExecutor, write_draft/verify y cuotas | Crash tras write se recupera por key/readback, misma key distinto payload conflicto, retries no duplican propuesta ni evaluate confirmado; ninguna tool approve/publicar |
| AC-E evaluación | `eval_suite` vigente (`agent_core/registry/suite.py`) + ImprovementEvidence Pulso; DSL de métricas (ADR 0020, `SCHEMA_VERSION` 1.2.0) sólo tras adapter/gate probado | No mezclar dos formatos `eval_suite` ni dos Verdict; pass nativo sin mejora no libera; outcome inseguro falla; cambios métricas no eluden baseline |
| AC-F reflexividad | Proposal target_system evolution, baseline externa y siguiente-job release pin | Candidato no cambia su juez/guardrails; rollback humano funciona; cambio prompt afecta próximo job, no run actual |

Unit: inputs/namespace/cost reconciliation, métricas y gates. Contract: schemas/código/fixtures por SHA, JevProvider y gateway nativos, nuevos nodos y clases de riesgo. Integration: Core/PG/Pulso/DuckDB reales en Podman con fallos y claves de prueba. E2E: descubrir→refutar/corroborar→generar drafts→evaluar→decisión→segunda corrida, usando como referencia de forma (no de contenido) la demo `atencion`/`disputa-cargo` y sus caminos grabados en `tests/fixtures/runs/`. Live smoke separado con payload permitido y presupuesto; pruebas deterministas usan providers grabados por puertos Core. No basta fixture que simula "un agente dijo pass": validar ejecutor real y receipts. No modificar Agent Core en esta tarea documental ni afirmar completado el cableado faltante (incluida la transferencia entre agentes, que a la fecha del snapshot sigue sin proveedor real de selección en `serve`).

### 29.8 Contratos de integración que debe construir el equipo

**Regla de alcance.** Esta subsección contiene sólo contratos de responsabilidad nuestra (Pulso, improvement-engine, infra, CI, mocks, scripts de bootstrap/seed que operamos). Etiquetas: **[NUESTRA]** la construimos y operamos nosotros; **[AGENT-CORE]** debe proveerla agent-core (endpoint, flag, fábrica de su composición, cambio en su registry/API) y vive en §29.9 con su workaround; **[FRONTERA]** módulo que toca ambos lados, con dueño argumentado. Ningún contrato siguiente asume que agent-core lo implementará.

| Capacidad | Etiqueta | Dueño y razón |
|---|---|---|
| Elegibilidad, ranker, bridge builder, memoria/wiki, disponibilidad temporal, E0 por batches, run_control | [NUESTRA] | Dominio Pulso; Core no lo conoce |
| Sandbox de exploración, broker, mailbox S3, bootstrap Terraform/Podman, browser, CI, observabilidad | [NUESTRA] | Infra y consola propias |
| `pulso-core-runtime` (proceso Python que compone Core in-process; código en el directorio `core-bridge/`) | [FRONTERA] → NUESTRA | Se despliega, versiona y opera con nuestra imagen; usa sólo puertos públicos de Core (`ToolExecutor`, `AuthzPort`, `IdentityVerifier`, `RegistryPort`, `EngineDeps`/`build_turn_engine`). `.importlinter` prohíbe que módulos de Core importen `agent_core.composition`, no que lo haga un consumidor externo; a Core le pedimos estabilidad de esa superficie (§29.9 #6), no que la escriba. Es el proceso `pulso-core-runtime` (composición de Core, siete fábricas, `/internal/v1/*`) más `pulso-core-exporter`; la imagen y su Dockerfile son nuestros (§31.11.3). |
| `PulsoScenarioHarness` y `--verifier`/`--harness` de `agentcore registry` | [FRONTERA] → NUESTRA | Core define el Protocol `ScenarioHarness` (`registry/evaluation/ports.py`) y carga el harness por ruta `modulo:atributo`; la implementación con principal builder es nuestra |
| `PinnedRegistryPort` | [NUESTRA] workaround | Implementa `RegistryPort`; el `release_id` en `CreateRunBody` es [AGENT-CORE] (§29.9 #1) |
| `release_id` en HTTP, readback de EvalRun/writes, transferencia real, escenarios `dataset` | [AGENT-CORE] | Ver §29.9 |

**[NUESTRA] Elegibilidad única de construcción.** `eligible_for_proposal` requiere fuente/grano/cutoff válidos, verificación independiente, bridge construible, policy/oracle disponibles y ausencia de bloqueo de seguridad. Además exige histórico `corroborated_descriptive`, o perfil E0 `candidate_descriptive` con soporte/calidad mínimos de su config. El segundo conserva evidencia descriptiva y no se renombra corroboración estadística; sólo autoriza construir y probar una hipótesis, nunca publicarla sin los dos gates. F3, PortfolioRanker, BridgeBuilder y diagramas usan este mismo predicado. La demo puede descubrir una oportunidad E0 legítima sin fingir potencia estadística del histórico.

**[NUESTRA] Sesión de exploración adaptativa.** `SandboxSessionPort` expone start(manifest,grant)→session_ref; query(session_ref,query_key,sql,expected_lease)→QueryResult; status y close. QueryResult contiene receipt_ref, schema de columnas, filas tratadas limitadas, truncated y result_ref/digest para resultado paginado autorizado; QueryReceipt registra costos/metadatos y no reemplaza los datos que necesita razonar el agente. Una sesión conserva DuckDB y scratch durante una etapa, admite una query activa y cola limitada, y permite que una segunda consulta dependa de la primera sin recrear la base. Core ToolExecutor llama al broker autorizado; no habla con filesystem/Podman. Local, el launcher mantiene el contenedor sin red y comunica solicitudes/resultados por pipes limitados. AWS usa mailbox S3 de comandos/resultados por sesión con prefijos IAM exactos; el task privado sondea comandos versionados y publica receipts. Es transporte de la misma sesión, no nuevo servicio por consulta. Identidad/key/digest de query evita ejecutar dos veces CTAS/DML por retry; clave repetida con SQL distinto falla. Manifest de sesión y receipts son artefactos; lease, deadline, límites y secuencia pertenecen al job/launcher. Si se pierde la sesión, no se finge continuidad: nuevo intento reconstruye desde manifest y queries deterministas confirmadas, o reinicia etapa dejando evidencia previa inmutable. Cleanup y revocación cierran la sesión y fencean resultados. AWS polling añade latencia configurable que se mide aparte, no hereda p95 de la API. Test real ejecuta dos queries dependientes, conflicto de key, crash entre comando/receipt, revocación y cierre por presupuesto.

**[NUESTRA] Revocación durante una etapa.** El wrapper de ToolExecutor revalida grant, lease y estado run_control antes de cada acción write_draft y antes de emitir una llamada de proveedor o query nueva; facts de bootstrap no conceden autorización perpetua. Resultado tardío de una operación ya enviada se reconcilia, pero no habilita nuevas acciones ni publicación después de revocación. Test cancela después de validar contexto y antes de put_draft: cero escrituras; timeout Core conserva unknown, no cancelled ficticio.

**[NUESTRA + FRONTERA] Transporte Rust↔Python.** `CoreTaskPort` usa un servicio privado Python propio (`pulso-core-runtime`), autenticado por JWT de servicio aud=core-bridge con tenant/purpose/job y expiración; no se publican estas rutas como endpoints de Agent Core. `POST /internal/v1/core-tasks/invoke` recibe CoreTaskInvocation, schema_version y request_digest, con Idempotency-Key estable; ejecuta sincrónicamente una etapa Core y devuelve CoreTaskReceipt. El worker es asíncrono frente al usuario y limita concurrencia/deadline; no mantiene una transacción PG abierta durante la llamada. Un timeout de transporte deja unknown, no permiso de reejecutar.

Antes de dispatch, Rust persiste comando prepared/sent en pulso_external_commands. El bridge vincula el core_run_id mediante callback autenticado `POST /internal/v1/core-task-bindings` del control-api antes de cualquier efecto; callback hace CAS sobre el comando, valida tenant/job/key/request_digest y guarda binding como receipt. Si el binding no puede persistirse se deniegan efectos. `GET /internal/v1/core-tasks/{core_run_id}` del bridge consulta almacenamiento mediante los puertos Core y devuelve receipt/resultados tratados del run confirmado; no consulta tablas Pulso ni inventa un endpoint upstream. Comando desconocido antes del binding queda manual_reconcile si no puede probarse ausencia de efecto. Reintento sólo tras readback terminal o prueba de no envío; misma key con payload distinto es 409. Rust no accede directamente a PG Core. Resultados/facts pasan por whitelist de schema del stage, límites/PII y digest antes de publicarse en Pulso; no se exporta RunState raw. Tests: respuesta perdida antes/después del binding, callback fallido, restart bridge, clave conflictiva y revocación durante ejecución.

**[NUESTRA] Contrato browser.** Consola mínima React + TypeScript + Vite, lockfile versionado; Vitest/Testing Library para componentes y Playwright para E2E. API y stream son same-origin mediante sesión Secure/HttpOnly/SameSite; mutaciones validan CSRF. SSE no lleva JWT en URL, valida tenant/run y sesión vigente, cierra al expirar permisos. Cursor purgado devuelve 410 cursor_expired con ruta de snapshot y cursor de recuperación autorizado; cliente recarga snapshot y reconecta, no declara completion por silencio. Local usa emisor de identidad exclusivamente test/sandbox con roles y step-up simulado visible; AWS requiere proveedor OIDC configurado, no se afirma que exista ya. Tests: reconexión, cursor ajeno/purgado, logout, revocación y rol cruzado.

**[NUESTRA + AGENT-CORE] Ruta externa de modelos.** Core usa su integración OpenAI-compatible o Jev nativa según perfil. El equipo dueño suministra endpoint, credenciales y capacidades verificadas; no imponemos headers privados, `/internal/v1/invoke` ni un proxy Pulso. Si la integración no permite hacer cumplir tratamiento, cuota o deadline requerido, el motor declara dependency_blocked y no envía datos.

**[NUESTRA + AGENT-CORE] Pin de ejecución.** El HTTP CreateRunBody actual no acepta release_id. El bridge utiliza un `PinnedRegistryPort` por invocación: resuelve exclusivamente la release autorizada y su cierre de dependencias, verifica Agent/version/status y rechaza cualquier fallback a latest. Se comprueba revocación antes de acciones sensibles. No basta comprobar el pin después de ejecutar. La release se resuelve dos veces por invocación (`RunAuthorizer` y `TurnEngine.start_run`) y un selector por versión resuelve la release **más reciente** de esa versión de Agent, no la autorizada: el pin cubre ambos puntos y se verifica `RunResult.release` (§31.5.3). Tests: dos releases de la misma versión de Agent, alias movido durante la ejecución y release revocada; ninguna debe cambiar silenciosamente el código ejecutado.

**[NUESTRA] Single-flight de invocación.** Idempotency-Key de start_run no serializa por sí sola solicitudes simultáneas antes del commit final. Rust permite un dispatcher propietario por comando/lease; bridge aplica single-flight `(tenant,principal,key)` antes de entrar al engine. El callback durable admite transición sin binding→un core_run_id, repetición del mismo binding→ack y otro core_run_id para la misma key→409. Un bootstrap cuyo binding pierde CAS deniega toda query/modelo/write antes de generar efectos. Tras crash no se libera una key con binding incierto sólo por expirar lease: se reconcilia o bloquea explícitamente. Tests ejecutan POST concurrentes, run IDs distintos y crash después de write antes del commit Core; ningún segundo run puede producir efectos nuevos.

Readback distingue in_progress, unknown y terminal. RunState ausente mientras exista binding o comando sent no prueba que nada se ejecutó: la transacción inicial puede no haber cometido aunque un write del registry sí lo hizo. Se reconcilian writes por key/get_write y presupuesto antes de permitir un sucesor; jamás se interpreta load_run=None como autorización para repetir. Tests matan el proceso entre write y commit y exigen una sola propuesta, estado unknown visible y recuperación sin falso éxito.

**[NUESTRA] Acceso real al mailbox AWS.** Un task role compartido no garantiza prefijos por sesión. El sandbox task no recibe permiso S3 general: el dispatcher/broker, ya existente, entrega URLs prefirmadas por objeto exacto tras validar grant/session/tenant/attempt/sequence y revocación; el task consulta el broker privado para obtener sólo el siguiente command y el objeto result autorizado. No recibe capacidad ListBucket ni puede escoger una key de otro run. Roles del broker separan lectura de sources/extracts y escritura de resultados; URLs tienen TTL limitado al grant/deadline y son material sensible que no se registra en eventos/logs. Digest del comando/resultado se verifica además de autenticación; URL expirada exige grant vigente, no renovación ilimitada. Un resultado publicado tarde no activa nada si el grant fue revocado. Tests task A contra prefijo B, reutilización de URL/key ajena, expiración y revocación. La política IAM exacta es del broker; el acceso del task queda acotado por objeto firmado, no por una session policy inexistente.

Revocar el grant bloquea nuevas URLs/acciones y uso de resultados, pero una URL ya emitida puede permanecer utilizable hasta su expiración. No prometer revocación instantánea de esa capacidad; TTL máximo y exposición residual se fijan en config/policy y se prueban. Source objects sensibles no se borran para simular revocación ni se incluyen en URLs públicas.

**[NUESTRA] Bootstrap de infraestructura.** Entorno local inicial Windows/PowerShell con backend Linux de Podman; launcher/seccomp/cgroups se verifican dentro del contenedor. WSL sólo se evalúa ante incompatibilidad importante documentada. doctor valida plataforma/cgroup/preflight y falla antes de iniciar investigación insegura. `infra/terraform/bootstrap` crea una vez backend de state cifrado/versionado con locking y trust role GitHub OIDC, usando identidad administrativa autorizada; runbook registra prerequisitos, outputs no sensibles y migración del state al backend remoto. Los roots normales y CI usan OIDC, no claves persistentes ni el administrador de bootstrap. fmt/validate no crean backend. Tests: segundo bootstrap sin cambios, workspace limpio identifica backend/rol faltantes, rechazo de repo/ref OIDC no permitido y plan normal usando backend remoto.

**[NUESTRA + FRONTERA] Evaluación de tasks.** El `EngineScenarioHarness` de Core (`composition/evaluation.py`) fija principal `customer` y no proporciona el contexto privado que necesita este constructor. Implementamos `PulsoScenarioHarness` cumpliendo el Protocol `ScenarioHarness` vigente (`run(target, agent_id, scenario, tools) -> list[EngineEvent]`, con `HarnessUnavailable` para fallos de infraestructura) y lo inyectamos por la ruta `modulo:atributo` que acepta `agentcore registry --harness` (junto con `--verifier`). No añade campos al wire `eval_suite` (`EvalSuite`, `Scenario`, `Step`, `ToolReply`, `SandboxSeed`, `Expect`, `Assertion`, `ScenarioPrincipal`). Sólo escenarios `scripted` son ejecutables; `dataset` está deshabilitado (abierto #20) y la primera versión no depende de él. El manifest externo sellado resuelve scenario.id a fixture, identidad builder, stage, grant y contexto. Cada brazo/repetición recibe registro, almacenamiento y ejecutores sandbox aislados vía `SandboxPort` (`is_sandbox = True`; `LocalSandbox` de `evaluation/local_sandbox.py` como referencia); BuilderToolExecutor jamás escribe en el registry operativo durante estas pruebas. Ejecuta el engine real con el target congelado y devuelve sus EngineEvents al evaluator nativo. Una evaluación del constructor usa una fixture acotada independiente. Error de proveedor, fixture ausente o contexto inválido lanza `HarnessUnavailable` = failed_infra, no pass ni error del cliente. El seed inicial se importa por canal administrativo autorizado; las versiones siguientes pasan por propuesta y evaluación normales. Es [FRONTERA] porque el Protocol y el cargador son de Core; se asigna a nosotros porque la identidad builder y los grants son nuestros.

**[NUESTRA] Escala E0.** La evaluación completa del corpus se divide en batches externos con cobertura explícita. El gate Core vigente admite como máximo 200 escenarios, 50 pasos por escenario y 10 repeticiones (límites declarados en `agent_core/registry/suite.py`): no fingir que contiene las 1.800 reproducciones ni truncar conversaciones sin reportarlo. La suite nativa se fija antes de mirar final; el manifest une su EvalRun y la evidencia externa completa. Múltiples evaluaciones nativas no se convierten automáticamente en un único gate de aprobación.

El plan sellado identifica exactamente la suite nativa que respalda la aprobación y su digest; los batches complementarios no sustituyen el last_eval requerido por Core. Casos de más de 50 pasos quedan `not_evaluable_native`, no se truncan ni se cuentan como pass; se conservan en la evaluación complementaria con su elegibilidad y cobertura. Una suite nativa vacía o inválida bloquea publicación aunque el agregado externo sea favorable.

**[NUESTRA] Routing Jev.** Cuando decide alimenta branch_on, su contrato contiene un enum string calibrado explícito para routing. Booleanos y scores son resultados auxiliares o facts derivados para reglas; no se pasan directamente como branch_on si el contrato Core exige enum. Schema, etiquetas y calibración se versionan juntos.

**[NUESTRA + AGENT-CORE] Evaluación fallida.** La verificación completa del candidato/suite es obligatoria para aceptar pass. Si evaluate invalida el candidato y el readback ya no conserva last_eval, se registra fail con el cuerpo 409 `gate_failed` (que trae el `EvalReport` completo, sin `eval_run_id`) y, sólo si esa respuesta se perdió, con el write receipt disponible y detalle `unavailable`; no se convierte esa ausencia en éxito ni se inventa un endpoint EvalRun. El adapter preserva el error gate_failed cuando esté disponible. Nueva evaluación requiere candidato congelado válido y nueva identidad de intento.

El harness distingue setup inválido (fixture ausente, grant incorrectamente preparado, proveedor caído: failed_infra) de regresión del candidato sobre contexto válido (rechazo o comportamiento incorrecto: fail). No etiquetar como infraestructura todo rechazo de contexto: ocultaría fallos funcionales.

**[NUESTRA] Control durable de runs.** `run_control` es artefacto versionado y head CAS, no tabla adicional. Guarda running/pause_requested/paused/cancel_requested/cancelled/completed, revision y command receipts. Comando exige expected_revision y key: misma key/payload devuelve recibo previo; payload distinto o revisión obsoleta devuelve 409. Claim de hijos y cambio del head toman el mismo lock del run raíz y revalidan estado en transacción. paused requiere cero hijos activos y ninguna ejecución Core/comando incierto capaz de continuar; waiting_dependency no prueba quiescencia; cancel_requested revoca nuevos grants y espera reconciliación de efectos en vuelo antes de cancelled. Resume sólo admite paused no terminal. Tests cubren pausa concurrente con claim, comandos repetidos, reinicio, resume terminal y proveedor con outcome unknown.

**[NUESTRA] Conformidad del consumidor de modelos.** Core recibe contexto privado de ejecución, perfil y límites, no autorizaciones derivadas del prompt. El adaptador revalida tenant/job/propósito/partición/lease y reserva antes de dispatch. La integración externa informa usage/errores cuando disponible; costo desconocido queda unknown. No se implementa middleware de proxy ni se promete que proveedores entiendan grants Pulso. Tests: contextos paralelos cruzados, grant expirado, timeout, capacidades ausentes y costo desconocido.

**[NUESTRA] Memoria editable sin efectos durables.** `wiki/transform` es compute sobre una copia efímera del run. Recibe base_digest y operaciones tipadas create/replace/move/remove sobre rutas relativas autorizadas; devuelve diff y manifest, aplica límites de tamaño y revisión de PII. No cambia el head compartido. El publicador Rust verifica procedencia y reglas de memoria antes de crear la revisión durable. Los heads se separan por mundo/campaña/protocolo/partición; replay monta la revisión disponible a su reloj, no la wiki más reciente. Frozen conserva memoria de entrenamiento; continuous aprende sólo después de observar el resultado disponible del caso. Pruebas de conflicto de base, path traversal, contaminación final y ejecución concurrente son obligatorias.

**[NUESTRA] Disponibilidad temporal por campo.** Un opened_at no autoriza todo el registro: topic inferido, analista asignado, resolución, SLA final y complaint_id pueden conocerse después. El contrato de extracción registra available_at por campo o grupo con igual procedencia; valor sin timestamp fiable sólo se usa retrospectivamente o bajo supuesto explícito versionado, nunca como predictor histórico confirmado. Los joins con snapshots originales tampoco vuelven históricos sus estados finales. `training_as_of` precede al primer caso de reproducción; cierres posteriores de casos de arranque se excluyen hasta estar disponibles. CSAT conserva valor, escala declarada por contrato validado y fuente; E0 declara 1–4. No inferir la escala original del rango observado ni mezclar escalas sin mapping versionado.

**[NUESTRA] Operación y observabilidad.** Local y AWS incluyen el proceso Python Core/bridge, además de los servicios Rust; Core usa su propio servicio PG16 (la versión que valida su CI) con bases `core_runtime` y `core_eval` y roles distintos; compartir servidor con Pulso (PG de `pulso_control`) sólo tras pasar el contract test sobre la versión compartida. CI valida contratos Python, fixtures, schemas y migrations por owner, fija SHA e imagen de Core y prueba compose completo. Trazas llevan metadatos externos target_system=attention|evolution y world/environment/purpose sin alterar hashes de artefactos Core: un fallo del investigador no cuenta como fallo de atención bancaria. El grafo de debugging enlaza job→CoreRun→FlowNode→decide/tool/agent y receipts. Pausa impide nuevas etapas, no promete cancelar una llamada Core en vuelo; cancelación queda pendiente hasta reconciliar efectos y presupuesto desconocidos. Debe probarse carrera pausa/claim, reinicio y timeout después de una escritura. El runtime Core se construye como imagen propia (`pulso-core-runtime`, §31.11.3), con el SHA y el `uv.lock` fijados; `agentcore migrate` se prueba sobre la base del SHA anterior en cada bump (§31.10.5).

### 29.9 Dependencias y solicitudes a agent-core

Lista corta de lo que **no** podemos construir nosotros. Cada fila deja una ruta explícita `dependency_blocked` o un workaround nuestro, nunca una simulación presentada como integración. Ninguna bloquea AC-A.

| # | Necesitamos [AGENT-CORE] | Por qué | Evidencia (snapshot 86a7674) | Mientras tanto (nuestro lado) |
|---|---|---|---|---|
| 1 | `release_id` (o pin equivalente) aceptado por `CreateRunBody` | Pin exacto de release por invocación sin depender de alias | `agent_core/api/schemas.py`: `CreateRunBody` sólo trae `agent`, `subject`, `input`, `lang` | `PinnedRegistryPort` por invocación en `core-bridge`; tests de alias movido y release revocada. El selector por versión (`id@X.Y.Z`) es sólo transporte: resuelve la release más reciente de esa versión, por lo que la identidad de ejecución es el `release_id` verificado (§31.5.3). |
| 2 | Lectura de EvalRun completo y de un write por key (`get_write`) vía API estable | Verificar eval_id/hash/base/suite y recuperar tras crash sin inferir de `last_eval` | `get_write`/idempotencia existen en `registry/service.py` y `composition/builder_tools.py`; `api/app.py` no los expone para drafts ni evaluate | BuilderToolExecutor local al runtime; fallo registrado con `unavailable`; no inventar endpoint |
| 3 | (Opcional) `EngineScenarioHarness` parametrizable en principal/contexto | Evitar duplicar el armado del motor en nuestro harness | `composition/evaluation.py`: `_principal` fija `"type": "customer"` | Harness propio vía `--harness`; paridad con el de Core por test de contrato por SHA |
| 4 | Proveedor real de selección de especialista en `agentcore serve` | Sólo si se adopta transferencia conversacional (ADR 0021) | README: la demo `registry-transfer-demo` "todavía no transfiere" por `serve` | `dependency_blocked`: no usamos transfer; stages = runs distintos |
| 5 | Habilitar escenarios `dataset` (abierto #20) | Evaluar con casos reales por id/hash sin copiar datos al registry | `suite.py`: `DatasetScenario` deshabilitado (`dataset_source_disabled`) | Batches externos E0 (§29.8) como evidencia complementaria; no sustituyen `last_eval` |
| 6 | [FRONTERA] Estabilidad declarada de la superficie de composición (`EngineDeps`, `build_turn_engine`, `EngineScenarioHarness`) | `core-bridge` depende de ella; un cambio silencioso rompe el pin | `agent_core/composition/__init__.py` la exporta; `CLAUDE.md` sólo regula importaciones entre módulos | Pin por SHA + contract CI que construye el motor; cambio de firma falla CI antes de promover |
| 7 | Evaluación concurrente en `serve`/`registry` (hoy `max_workers=1`) | Throughput de evaluaciones | `composition/registry.py` y `serve_registry.py`: `ScenarioEvaluator(..., max_workers=1)` | Cola y límite global por servicio de nuestro lado (§29.6) |
| 8 | DSL de métricas (`MetricDef`/`MetricExpr`, 1.2.0) como fuente de gates Pulso | Reducir duplicación de métricas | `docs/specs/motor/00-indice.md`, ADR 0020 | Pendiente de evaluar en detalle; hoy MetricSpec Pulso propio, sin asumir integración |

Solicitudes adicionales N-01 a N-11 en §31.12. La fila 2 se extiende con N-10 (`eval_run_id` en el `payload` de `gate_failed`) y la fila 6 con N-06 (superficie de composición: `resolve_ports`, `ServePorts`, `build_api_deps`, `ApiDeps`, `registry_extension`, `RegistryService(quotas=)`, `ScenarioEvaluator`, `PgRegistryStore`, `registry/memory.py`).

## 30. Plan de construcción paralela: cortes verticales, TDD e integración

### 30.1 Objetivo y reglas de ejecución

Este plan convierte el spec en unidades asignables sin construir primero todas las capas y descubrir incompatibilidades al final. **No autoriza implementación, creación de repos/tickets ni despliegue por sí mismo:** requiere visto bueno del usuario. Los cortes S0–S8, AC-A–F y E0-A–E siguen siendo cobertura funcional; las fases P0–P5 siguientes organizan su ejecución y no los reemplazan ni reducen el alcance. Una fase agrupa varios casos independientes, no un gran ticket horizontal.

Cada paquete tiene un agente implementador; otro agente integrador reúne el grupo y verifica el recorrido conjunto. Revisores adversariales independientes no son el autor ni el integrador de ese grupo. El coordinador mantiene dependencias, asignaciones y contratos, no acepta un “verde” basado sólo en un mock que devuelve pass.

**Ciclo obligatorio por comportamiento:** contextualizar spec/código/ADRs y consumidores → escribir un test observable → ejecutar y demostrar RED por el comportamiento faltante, no setup → implementar lo mínimo → GREEN → refactor con tests verdes → siguiente comportamiento. Se diseñan escenarios primero, pero no se escribe de golpe toda la suite seguida de toda la implementación. Tests por interfaces públicas sobreviven refactors; pruebas de migración/constraints sí inspeccionan invariantes DB cuando ése es su objeto. Dependencias internas y bases reales, no mocks de nuestras clases. Providers externos grabados sólo en límites y para determinismo/fallos; live smoke separado verifica Jev/LLM reales.

```mermaid
flowchart LR
  DAG[DAG de features Uxx] --> P0[P0 Base]
  DAG --> P1[P1 Tracer]
  DAG --> P2[P2 Descubrimiento]
  DAG --> P3[P3 Cambio seguro]
  DAG --> P4[P4 Automejora]
  DAG --> P5[P5 Operacion]
```

Las ramas laterales avanzan por capacidades disponibles: no bloquean esperando “todo backend”, pero tampoco integran sobre contratos imaginarios. P0 no define todos los schemas futuros: fija sólo los que necesita el primer recorrido; cada contrato adicional se congela antes de despachar sus consumidores. Autorización, aislamiento, presupuesto y eventos materiales no se posponen a P5.

Este primer dibujo es una vista de hitos, no dependencias de implementación. §§30.8/30.9 sustituyen el despacho por familias/fases: tabla Uxx normativa y grafo funcional, sin UI→detector ni fase completa→todas las features siguientes.

### 30.2 Organización de agentes y trabajo aislado

| Rol | Responsabilidad | No puede hacer |
|---|---|---|
| Coordinador | Inventario, DAG, contratos vigentes, asignaciones, evidencias y blockers | Cambiar alcance silenciosamente o dar por terminada una dependencia por intención |
| Implementador de paquete | TDD vertical, código/tests/docs en su área y entrega contra commit concreto | Modificar contratos compartidos sin acordar consumidores o editar otro worktree |
| Integrador de fase | Reunir commits compatibles, ejecutar integración/E2E/chaos del grupo, resolver fronteras mediante paquetes sucesores | Autorevisar adversarialmente sus cambios ni reemplazar suites por mocks |
| Revisor independiente | Intentar romper comportamiento, seguridad, datos, performance o UX; emitir hallazgo reproducible | Aprobar por leer un resumen del autor sin inspeccionar diff/contratos/tests |

Con cuatro slots, operar normalmente con coordinador/integrador + dos implementadores + un revisor; el rol coordinador puede recaer en el integrador para ese grupo, nunca en sus implementadores. Si se usan tres implementadores, la revisión corre después liberando slots. No multiplicar agentes esperando la misma dependencia; suspender paquetes bloqueados y avanzar otra rama lista.

Cada paquete usa branch/worktree Git propio y scope de archivos declarado. Shared schemas, migrations y lockfiles tienen un owner a la vez; los demás solicitan cambio de contrato, no resuelven conflictos a ciegas. DBs/schema de test, buckets/prefijos, puertos y Compose project se aíslan por worktree/run de test. No se comparten datos mutables ni una DuckDB entre agentes. Snapshot original sólo readonly; secretos fuera de Git. PRs/revisiones se fijan a head SHA; cualquier corrección posterior invalida aprobación del diff anterior y requiere recheck pertinente.

El test_namespace identifica Compose project, databases Pulso/Core/eval, prefijos/buckets, labels y scratch; preferir DBs Core separadas a asumir soporte de search_path custom. Cleanup opera sólo sobre allowlist de recursos etiquetados y paths absolutos verificados del paquete: nunca reset de DB ni eliminación de volúmenes compartidos. Tests de concurrencia/cuota comparten deliberadamente un scope dentro de su grupo aislado para probar contención, no entre paquetes ajenos.

### 30.3 Vista resumida de familias y cobertura, no unidades de despacho

| Hito | Familias de trabajo y especialidad | Recorrido de aceptación; dependencias funcionales en §30.8 |
|---|---|---|
| **P0 Base mínima** | P0-A backend: artifact/ref/head + primer snapshot consultable. P0-B engine-local: Compose PG/S3, doctor y CI mínima autocontenida. P0-C contratos/docs: fixtures iniciales, pin Core y glosario/owners | Contratos mínimos primero; A/B después en paralelo. Gate: clone limpio del motor → doctor → crear/leer snapshot readonly y evidencia durable. Cubre inicio S0/AC-A; no crear todos los módulos antes del primer test |
| **P1 Tracer técnico** | P1-A backend: trigger/job/event/quota/claim y comandos. P1-B AI: bridge/Core task bootstrap/pin + integración externa y Jev. P1-C data/sandbox: extracto DuckDB, sesiones y QueryResult. P1-D front/o11y: lista/timeline por API | A usa P0; B/C pueden trabajar con fixtures del contrato, después se conectan al job real. D arranca sobre API fijada, valida luego backend real. Gate: snapshot → trigger automático → task Core → query adaptativa → receipt → timeline, con permisos y presupuesto. Inicia S1/S2/S6 y AC-A/B/C; parte contractual/local de E18, cierre AWS/CD en P5 |
| **P2 Hallazgo explicable** | P2-A data: sensores multi-familia/perfiles original/E0 y cortes. P2-B AI: scout/verifier y fuerza de evidencia; eligibility final en P3. P2-C memoria: wiki efímera, publicación CAS y revocación. P2-D front: expediente/evidencia/unknown | El hito reúne el tracer y las features de descubrimiento listas. A alimenta B; C se desarrolla con fixtures y se integra sin final leakage. Gate: entrada alterada cambia soporte; hallazgo/refutación y memoria trazables, sin Queja/signal esperado hardcodeado. Cubre S3/F6, E0-A/B/E y comienzo AC-F |
| **P3 Cambio evaluable** | P3-A AI/backend: alternativas/bridge/compiler + writer registry. P3-B eval/data: ScenarioFactory/oracle/baseline/pares y harness. P3-C engine-local: aislamiento real del simulador/broker y CI contract; AWS autorizado anticipado o en P5. P3-D front: diff y dos gates | Baseline/oracles B se sellan antes de candidatos A; B puede comenzar desde P1 con fixtures, sin ver resultados del candidato. Gate: oportunidad elegible → draft autorizado → candidate congelado → native + ImprovementEvidence, incluida prueba fail/unsafe/infra. Cubre S4/S5, AC-D/E y E0-D |
| **P4 Automejora E2E** | P4-A integración backend: scheduler/registry/humano/simulador. P4-B data/eval: frozen/continuous y feedback temporal. P4-C AI/memoria: aprender/refutar y candidato evolutivo sin cambiar juez. P4-D front: ciclo completo y controles debug | El hito reúne features de descubrimiento/cambio integradas. Gate: detección autónoma → propuesta → evaluación → espera humana → publicación staging/ack simulado → nuevo evento → segunda iteración con memoria, sin intervención para forzar hallazgo. Cubre S6/S7, AC-F y E0-C/E |
| **P5 Entrega robusta** | P5-A infra: Terraform/CD/staging/rollback. P5-B performance/security: carga, fairness, fallos y retención. P5-C docs/UX: runbooks, accesibilidad, onboarding y checklist de entrega | Terraform empieza con su esqueleto independiente en P0 y se completa aquí; el stack de integración del motor ya vive en `improvement-engine`. Gate: tercero reproduce stack; chaos/carga con límites medidos; plan/smoke AWS y deploy sólo autorizados; documentación concordante. Cubre S8 y todas las regresiones críticas |

Los paquetes D de frontend son pequeños incrementos del mismo producto interno, no equipos esperando UI completa. No se implementan F7/F8 ni canary real para completar P4. Core registry mock fiel sirve cuando falta conexión, pero integración real y mock se etiquetan y verifican por separado; un mock no acredita smoke Core.

**Subgates P3 sin circularidad:** A1 entrega bridge, alternativas y objetivo/outcome propuesto, todavía sin candidato; B1 fija baseline/oracle/EvaluationPlan independiente; A2 construye y escribe el candidato; B2 ejecuta y compara. Queda permitido investigar alternativas antes de B1, no seleccionar baseline después de ver resultados. P3-C exige primero simulador stateful/aislamiento local y contrato broker; mailbox/IAM AWS reales se verifican en P5 o anticipadamente sólo con autorización. AWS no bloquea el tracer local P1 ni el gate local P3, y LocalStack no acredita seguridad IAM.

La cobertura S/AC/E0/E citada en fases es incremental: matriz por requisito registra planned/partial/passed con test/head/entorno. P1 inicia AC-B/C y la parte contractual/local de E18; detección/verificación completa se cierra en P2 y E18 AWS/CD en P5. Un primer uso de la capacidad no marca toda su suite como pasada.

**Adiciones transversales desde el inicio:** P0 fija scope/lineage/cutoff de memoria y fixtures mínimos de permisos; P1 incorpora un caso replay con reloj/corte y tests que deniegan labels/final/eventos futuros, además de cerrar E0-A incrementalmente. El replay no aparece por primera vez en P4: allí se completan ambos protocolos y corpus. P3 comienza con un escenario y un cambio ejecutables antes de ampliar suites/batches. El implementador P3-A no modifica los oracles ni gates de P3-B para conseguir aprobación; baseline y juez se mantienen externos al candidato.

### 30.4 Ejemplos de primer RED por familia; catálogo asignable en §30.8

| Paquete | Caso independiente / primer test RED | Negativo o regresión obligatoria |
|---|---|---|
| P0-A | Crear snapshot y recuperarlo con los mismos digests | Bytes originales iguales; revisión/tenant inválidos rechazados |
| P0-B | doctor identifica dependencia ausente y arranque la recupera | Segundo arranque idempotente; sin secretos en imagen/logs |
| P1-A | Dos triggers equivalentes crean un solo trabajo lógico | Dos configs no duplican presupuesto; claim/pausa y lease perdido |
| P1-B | Invocar etapa fijada devuelve receipt ligado al CoreRun | POST simultáneo y crash antes de commit no duplican efectos; pin/rol inválido |
| P1-C | Segunda query usa scratch creado por primera en la misma sesión | IO externo/source write/cross-session denegados; replay key conflictiva |
| P1-D | Un evento durable aparece tras refrescar/reconectar | SSE duplicado/purgado, OTel caído y acceso tenant ajeno |
| P2-A/B | Detectar/refutar patrón desde evidencia y config sellada | Labels/final invisibles; missing/mezcla/temporalidad no se llaman causa |
| P2-C | Dos diffs del mismo head no sobrescriben aprendizaje | Rebase, tombstone tras restore, memoria futura invisible en replay |
| P3-A | Cambios aprobados por compiler crean draft compatible | Modelo cambia payload después del compiler: denied sin write |
| P3-B | Comparar ambos brazos con mismo universo/oracle y banco separado | Unknown desigual no fabrica mejora; baseline post hoc y unsafe bloquean |
| P3-C | Acción real en sandbox se verifica por estado/receipt | Task A no lee B; revocación y URL residual se distinguen |
| P4-A | Sin humano queda evaluated; humano autorizado publica staging | Timeout no significa publish; staging stale exige reevaluación |
| P4-B/C | Evento posterior disponible genera aprendizaje y nuevo run | Frozen no aprende; candidato no cambia juez ni final; no se aprende dos veces |
| P5-A/B/C | Clone limpio reproduce caso y rollback autorizado | Fallo de migración/collector/provider, carga/fairness, permisos y teclado |

Éstos son puntos de arranque, no suites completas escritas anticipadamente. Cada paquete añade uno a uno los escenarios del spec aplicables y mantiene un índice de cobertura a S/AC/E0/E/C. No se inventa un “agente pass” para sustituir el oracle ni una demo guionada para acreditar descubrimiento autónomo.

### 30.5 Contrato de entrega e integración de un paquete

**Disciplina GitHub obligatoria (engine e infra).** Cada corte implementable se trabaja en una feature branch (`feat/Uxx-descripcion`, `fix/Uxx-descripcion` o `docs/descripcion`), nunca directamente en `main`; agentes concurrentes usan worktrees aislados. `main` se protege con PR obligatorio, checks de CI requeridos y aprobación independiente; sin force-push ni bypass rutinario. TDD y revisión adversarial siguen siendo gates, no se sustituyen por una aprobación superficial del PR.

Los PRs son pequeños, frecuentes y cohesionados alrededor de un comportamiento verificable: objetivo/Uxx, alcance, dependencias, evidencia RED→GREEN, regresiones y documentación aplicable. No acumular una fase completa para un único merge; no fragmentar arbitrariamente un cambio inseparable. El integrador verifica el head vigente y sus checks antes de cada merge; cambios incompatibles se entregan con estrategia expand/contract o permanecen sin integrar hasta ser seguros. `main` debe quedar verificable tras cada merge.

Commits claros y trazables: `feat(scope): comportamiento`, `fix(scope): causa resuelta`, `test(scope): escenario` o `docs(scope): decisión`, vinculados a la unidad de trabajo. Versiones de código con tags SemVer por repositorio (`v0.x.y` durante desarrollo), inmutables, sobre commits integrados y validados; cada hito entregable incluye release notes, SHA y estado de validación. No crear un tag por commit ni confundir tags de código con versiones de contratos, configuración o artefactos de automejora. Engine e infra pueden versionarse independientemente; el manifest de despliegue fija sus SHAs/tags y digests compatibles. Antes de implementar S0 se añaden las protecciones, CI y plantilla de PR; esta sección no autoriza crear repos, publicar tags o hacer merges ahora.

Antes de asignar: ID, objetivo/caso de uso, entradas/salidas/versiones, prerequisitos con SHA, área exclusiva, tests prioritarios, presupuesto/fixtures y reviewer. Si un contrato no existe, su pequeño corte de definición/round-trip es dependencia, no libertad de inventarlo en dos ramas.

Entrega: commits/PR head, interfaces afectadas, para toda unidad que toque Agent Core `target` (mock/a2/real), `sha` del pin y `doubles[]`, comando y evidencia RED del primer comportamiento, comandos y resultados GREEN/unit/contract/integration/regression pertinentes, fixtures/digests, migraciones/compatibilidad, limitaciones, docs/ADR/bitácora y riesgos. “Tests pasan” sin comando/head/entorno no es evidencia. Logs adjuntos tratados, nunca CSV/PII/secretos. Test skipped/recorded/live se distinguen explícitamente.

Los IDs P*-* son familias asignables, no autorización para un ticket gigante: si una familia cambia varios contratos o requiere más de un recorrido independiente, se divide en hijos con IDs estables y gate propio (por ejemplo, integración externa de modelos, bootstrap task y decisión Jev dentro de P1-B). Cada hijo conserva test RED y entrega verificable; comparte el integrador de fase. El backlog se concreta progresivamente desde estas familias, sin abrir issues externos por editar este plan.

Integrador incorpora una rama a la vez, corre pruebas de fronteras y el recorrido del grupo contra dependencias reales. Crea paquetes correctivos pequeños para fallos, no reescribe todo el trabajo ajeno. Escribir el siguiente test de integración rojo forma parte del TDD del integrador: no esconder errores de acoplamiento cambiando expectativas. Merge de código y aprobación de una release bancaria son autoridades distintas.

### 30.6 Revisión adversarial y gate de fase

Al cerrar cada fase, asignar al menos dos focos independientes según riesgo; antes de P4/P5 cubrir todos: backend/concurrencia, AI/primitivas Core, data/leakage/oracles, infra/seguridad/egreso, performance/índices/N×M, testing/regresión y frontend/UX/accesibilidad. P0 revisa contratos/privacidad/bootstrap; P1 efectos/presupuesto/sandbox; P2 evidencia/memoria; P3 evaluación/authoring; P4 autonomía/integración; P5 operación/entrega. Los revisores inspeccionan implementación/tests y reproducción, no sólo el spec.

Triage: P0/P1 de seguridad/datos/efectos o correctness bloquean cierre; otros se resuelven o se difieren sólo con riesgo/owner/justificación explícitos sin violar aceptación. Autor corrige mediante nuevo ciclo RED→GREEN; revisor independiente revalida el head nuevo. Integrador repite suite del grupo tras cada corrección de frontera. No cerrar con un blocker conocido o un test crítico skipped.

Gate de fase: paquetes integrados contra contratos vigentes + prueba observable conjunta + regresiones pertinentes verdes + revisión independiente resuelta + documentación/bitácora actualizadas. Una feature puede estar verde aislada y el grupo rojo integrado; no declarar ese hito entregado. Otra feature puede avanzar si sus propias dependencias están verificadas: no exigir cierre global de una fase lateral. Nunca ejecutar sobre dependencia insegura sólo porque existe fixture/diseño.

### 30.7 Secuencia práctica y criterios de eficiencia

1. Tras aprobación, S0 confirma repos/tracker/labels/domain docs y configura instrucciones de agentes; no crear esas convenciones sin decisión del usuario. Primer backlog son los paquetes P0 y el tracer P1, no cientos de tickets especulativos.
2. Mantener máximo dos o tres implementaciones activas por integrador; despachar por dependencias y área exclusiva, no por cantidad de agentes disponible. Infra/test fixtures/oracles/UI contract permiten trabajo paralelo real.
3. Integrar temprano cada comportamiento probado; contratos mínimos y fixtures compartidos aceleran sin aprobar capacidades simuladas como reales. Construir first-pass Core determinístico antes del smoke Jev/LLM; budget/privacidad deben estar verdes antes de llamadas live.
4. Tras cada fase, actualizar matriz de cobertura y bitácora con tiempos observados, blockers y revisiones. Ajustar tamaño de paquetes por aprendizaje, manteniendo aceptación/alcance. No prometer calendario o speedup sin medir.
5. Detener paquete ante contrato incompatible, fuente/permiso faltante, riesgo de fuga, efecto unknown o presupuesto agotado. Registrar estado y condición de reanudación; seguir otra rama independiente, no aflojar el gate para mantener agentes ocupados.

**Definition of Done del plan:** el equipo puede asignar cada paquete, conocer su dependencia y primer RED, integrar el grupo con otro agente y verificar su cierre sin reconstruir la conversación. **Definition of Done del producto** sigue §§11/12/26: descubrimiento y mejora autónomos observables, con seguridad, datos y evidencias; esta sección no los rebaja a scaffolding o mocks verdes.

### 30.8 Catálogo bottom-up: features, historias y casos independientes

**Unidad de asignación vigente = Uxx, no una fase ni una familia P*-*.** Las familias de §§30.3/30.4 son vistas resumidas de cobertura; este catálogo y sus dependencias determinan el despacho. Independiente significa que tiene comportamiento, entrada/salida y aceptación propios después de sus prerequisitos, no que carezca de dependencias. Cada unidad empieza por el UC positivo de la tabla, luego negativos/regresiones uno a uno. Ampliaciones a nuevos sensores, paneles o rutas se asignan como sucesores con ID, contrato y gate, no crecen silenciosamente dentro de un paquete.

**Aceptación real vs. mock (§27.6) para las unidades que tocan Agent Core.** U09-A, U09-B, U10, U11, U17, U18, U19, U21, U25, U31 y las nuevas U37, U38, U40, U42, U45, U46, U47, U48, U53 y U54 corren en CI y en su primer ciclo RED→GREEN contra el corte (a) de §27.6 (mock fiel al contrato wire) y, cuando se indique, el nivel (a2) de §31.10.2; eso basta para cerrar su unit/contract test, pero no acredita integración real. Su aceptación como "real" — la que puede citarse en bitácora/PR como evidencia de que Pulso funciona contra Agent Core, no contra su propio doble — exige además una corrida verificada contra el corte (b) (servicio real levantado en local con el ambiente de CAP-58: compose + `migrate` + imagen `pulso-core-runtime`, §31.11.1). No declarar una de estas unidades "integrada con Agent Core" citando sólo corridas contra el mock.

| ID / feature | HU y primer UC/RED observable | Dependencias duras | Handoff y negativo requerido |
|---|---|---|---|
| U01 Entorno mínimo — habilitador | Como desarrollador, levanto PG/S3 y doctor identifica setup inválido | — | CI/Compose/pin/contratos mínimos; segundo arranque y secretos seguros; `dev.ps1 up --with-core`, `reset-core` y checks de Core del `doctor` (U52); SHA incorrecto o `/readyz` caído ⇒ `doctor` falla con explicación |
| U02 Revisiones durables | Como motor, publico/leo un artefacto y avanzo head por CAS | U01 | ArtifactRef/head/digest; cross-tenant y revisión stale rechazados |
| U03 Snapshot original | Como motor, registro una fuente original y reproduzco su manifest | U02 | SourceSnapshot/quality; bytes originales intactos |
| U04 Adapter E0 | Como motor, registro E0 conservando namespace y procedencia | U02 | Manifest/clocks/vistas; signal/labels no disponibles al investigador |
| U05 Cuota y grant | Como motor, reservo presupuesto autorizado en una ventana global | U02 | QuotaReceipt/grant; config nueva no reinicia saldo |
| U06 Trabajo durable | Como motor, dos triggers equivalentes producen un job ejecutable | U02, U05 | JobRef/lease/reducer; restart y fencing no duplican efectos |
| U07 Actividad por API | Como ingeniero, consulto eventos de un run y recupero cursor | U06 | Read model/SSE; cursor purgado y tenant ajeno |
| U08 Lab local adaptativo | Como investigador, hago dos queries dependientes con scratch aislado | U03, U05, U06 | QueryResult/Receipt/session; IO externo y source write denegados |
| U09-A Core task: invocación y facts | Como motor, ejecuto una etapa fijada y leo sus facts por whitelist (CAP-25/28/33) | U42 | Contratos del bridge; invocación y lectura de facts por whitelist |
| U09-B Core task: pin, binding y reconciliación | Como motor, recupero el receipt de una etapa fijada (CAP-26/27/30/31) | U09-A, U05, U06 | Binding/receipt/pin; pin movido, binding perdido, 429, concurrente/crash⇒unknown sin segundo efecto |
| U10 Integración modelos externos | Como consumidor autorizado, genero una respuesta con receipt y presupuesto | U05, U06, U42 (para el corte (b): `llm-smoke`) | ModelReceipt/usage/schema; grant inválido y costo unknown; no requiere scout |
| U11 Decisión Jev | Como motor, ejecuto decide tipado y ruta de baja confianza | U05, U09-A, U42 (para el corte (b): decisión Jev por el runtime real) | DecisionReceipt/Flow/calibración; enum/schema inválidos |
| U12 Sensor determinista | Como analista, calculo señal reproducible con denominador y faltantes | U03, U06, U08 | Signal/QueryReceipts; evidencia alterada cambia resultado |
| U13 Investigación scout | Como motor, exploro una señal sellada y produzco hipótesis no autoritativas | U08, U09-A, U10, U12 | `DeterministicSignal` valida su digest y cada campo de fuente/métrica/numerador/denominador/contract/transform/cutoff contra QueryReceipts. Core y modelo presentan receipts verificados, ligados al mismo tenant/job/grant/attempt/input/policy/capability/evidencia. Cualquier tamper, replay cross-scope, input/policy distinto o outcome no exitoso bloquea drafts. HypothesisSet conserva commitments de señal/fuente/recibos; lectura/grant fuera de scope rechazada |
| U14 Verificación independiente | Como motor, refuto o sostengo hipótesis con checks y Jev | U11, U13 | VerificationReport/strength; correlación no se etiqueta causa |
| U15 Wiki montada | Como investigador, leo/transformo una wiki autorizada en scratch | U02, U05 | Snapshot/diff; path traversal y memoria futura denegados |
| U16 Mecanismo y alternativas | Como motor, convierto sólo evidencia U14 en un bridge provisional y alternativas | U14 | `VerificationReport` + input validado → `WorkflowBridge`; `do_nothing` siempre existe; `supported` llega como máximo a `mechanism_proxy`, `refuted` queda `unlinked`, `uncertain` queda `not_evaluable`. No `ChangeSpec`, runtime Core, persistencia ni eligibility final |
| U17 Compiler | Como constructor, convierto un cambio autorizado en `EntityDraft[]` válido con JCS real, `replace` y los kinds `policy` y `eval_suite` | U16, U35, U39, U46 | Drafts/closure/digests; hash == Core; `REG-UNREFERENCED` y `REG-VERSION` antes del PUT; entidad o permiso incompatible rechazados |
| U18 Writer registry | Como constructor, guardo/congelo exactamente el payload autorizado | U09-B, U17, U45, U48 | Proposal/Candidate receipts; PUT con lista completa, precondición por doble lectura, mapa de referencias; `proposal_stale` ⇒ rebase; diff de la release ⊆ `ChangeSpec` ∪ `auto_bumped`; cambio LLM después de compiler denegado |
| U19 Evaluación nativa | Como evaluador, ejecuto un escenario Core real en sandbox | U09-B, U18, U20, U26, U47, U48, U55 | EvalRun/hash/suite; seis resultados de `evaluate` capturados; `fail` sin `last_eval` conserva el 409; fail/infra diferenciados y registry operativo intacto |
| U20 Plan sellado | Como evaluador, fijo baseline/oracle/métrica antes del candidato | U16, U26 | BaselineSelectionReceipt/EvaluationPlan/OracleRef y NativeSuiteSpec o ref publicada exacta; post hoc bloqueado |
| U21 Autoridad/publicación | Como aprobador, publico staging sólo con ambos gates y step-up (CAP-45; el gate combinado es CAP-39, U27) | U19, U27, U38 | Decision/Release receipt; approve con `accept_yardstick_loosened` explícito y `ApprovalReview`; `step_up_required` ≠ `forbidden_role`; publish con clave estable y confirmación por release esperada y diff; sin humano o timeout no confirma éxito |
| U22 Segunda iteración | Como motor, evento de plataforma ingerido dispara otra investigación usando aprendizaje | U13, U14, U21, U29, U33 | Run sucesor/MemoryUseReceipt; no autovalidación ni doble aprendizaje |
| U23 Replay E0 | Como evaluador, reproduzco frozen/prequential con versiones preaprobadas | U04, U09-B, U20-E, U27, U33 | CampaignManifest/coverage; futuro invisible y resume sin doble puntuación |
| U24 Consola de lectura | Como ingeniero, veo lista/timeline y estado real sin shell | U07 | UI conectada/API; fixtures sólo acreditan componentes, no integración |
| U25 Despliegue por manifest | Como operador, despliego una imagen aprobada y recupero la anterior | U01, U09-B, U41 (precondición: imagen del runtime Core por digest (D-3) y ADR 0003 de `infra` aceptada; CAP-62 permanece `dependency_blocked` hasta entonces) | Terraform/bootstrap/CD/smoke; OIDC y rollback; autorización AWS externa; manifest con digests incompatibles rechazado; rollback conjunto restaura servicio y smoke |
| U26 Banco sandbox stateful | Como evaluador, una acción cambia estado y se verifica por readback | U01, U02 | SandboxPort/executor/reset; namespace ajeno y estado entre brazos; declara que alimenta `PulsoScenarioHarness` y las colas de respuestas de U47; sólo alimenta el gate nativo si D-7 lo decide (CAP-41) |
| U27 Comparación Pulso | Como evaluador, comparo pares comunes sin fabricar mejora | U09-B, U18, U20, U26 | ImprovementEvidence; unsafe y unknown desigual bloquean; recibe `GateItem` y los cuatro guardarraíles `platform_*`; produce `CombinedGate` (CAP-39) |
| U28 Sesión AWS | Como investigador, ejecuto lab remoto con grants por objeto | U08, U25 | Session/mailbox/QueryResult; IAM/TTL/escape reales, no LocalStack como prueba |
| U29 Observaciones de plataforma | Como motor, ingiero evento durable de atención una vez | U02, U06 | Observation/cursor/coverage; sampled OTel no es denominador; distingue particiones `audit`, `registry` y `outbox`; el productor es U49 |
| U30 Sensor de plataforma | Como motor, detecto patrón por capa desde observaciones disponibles | U12, U29 | Signal por capa; evolution no se mezcla con fallos de clientes |
| U31 Evolución del detector | Como motor, propongo mejorar mis propios artefactos con juez externo | U19, U20, U22, U27 | Proposal target_system=evolution; guardrails/juez no alterados |
| U32 Diagnóstico SQL | Como ingeniero, inspecciono resultado tratado de una query | U24, U08 | Panel query por contrato/refs; redacción y dependencias degradadas |
| U33 Memoria publicada | Como motor, publico un diff por CAS y luego lo revoco | U02, U15 | MemorySnapshot/receipt/tombstone; rebase/restore sin fuga |
| U34 Control de run | Como operador, solicito pausa/cancel y veo estado verdadero | U06, U07 | El comando usa el mismo estado durable, versión esperada y fence de U06; no mantiene un registro paralelo reescribible. Receipt incluye target, estado solicitado/confirmado, revisión y tiempo. Efecto incierto nunca se llama cancelled; carreras unknown-after-read, re-registro y colisión cross-tenant se rechazan |
| U35 Elegibilidad final | Como motor, autorizo construir sólo con evidencia, bridge y plan listos | U14, U16, U20 | eligible_for_proposal/razones; oracle ausente bloquea aunque bridge provisional exista |
| U36 Identidad sandbox | Como evaluador, verifico identidad y deniego acción sensible sin evidencia vigente | U04, U26 | Fixture/executor boundary, policy/question digests; nunca respuestas en ModelPort; sin servicio bancario nuevo |
| U37 Perfil de endpoint, cliente HTTP y clasificador | Como adaptador, hablo con un Core identificado y clasifico toda respuesta (CAP-01/02/03/06); primer RED: servidor de prueba que corta la conexión tras el commit deja `unknown`, no un reintento | U01 | Crate `adapters/agent_core_http`, `AgentCoreEndpointProfile`, `EndpointProbeReceipt`, tabla de clasificación; 2xx no JSON, `code` desconocido ⇒ `unknown_upstream_shape`, publish sin `Idempotency-Key` rechazado localmente, todo 401 clasificado `runtime:credentials_invalid` |
| U38 Credenciales Core y relevo step-up | Como adaptador, firmo la credencial del bot constructor y releyo la humana sin fabricarla (CAP-04/05/43); primer RED: JWS con header exacto aceptado por el verificador del SHA | U01 | Emisor Ed25519, archivos `staff-keys`/`identity-keys`, JWT internos de servicio, `HumanAuthorizationPort` local; header con clave extra, `kid` retirado, `actor=human` en el bot, bot y humano con la misma clave, audiencia cruzada y `exp` vencido rechazados |
| U39 Wire fijado, hash de contenido y `wire-drift` | Como mantenedor, fijo los schemas del SHA y el `content_hash` coincide con el de Core (CAP-11/12); primer RED: hash Rust de cada fixture de `registry-demo` igual al de `registry.entities.content_hash` | U01 | `crates/core/wire/agent_core@<sha7>/` con MANIFEST, schemas derivados `derived_by_pulso`, función `core_content_bytes`; MANIFEST ≠ árbol falla, `serde_json` con claves ordenadas no pasa por JCS, `exclude_none` produce otro hash y se rechaza |
| U40 Mocks fieles del registry y del bridge | Como integrador, ejecuto el adaptador contra servidores HTTP que hablan el wire real (CAP-52/53); primer RED: publish sin `Idempotency-Key` rechazado como lo haría Core | U38, U39 | Binario `platform-sim/registry`, mock del bridge, `/_sim/info`, fixtures; mock que acepta lo que el real rechaza, que decide con código del adaptador o que simula mejora en el reporte de evaluación queda rechazado por la suite (U41) |
| U41 Suite dual-run, pin y bump | Como integrador, corro la misma suite contra mock, a2 y real y detecto deriva (CAP-55/56/57); primer RED: alterar un campo del mock hace fallar la suite | U40, U51 | `contracts/agent_core/pin.json`, `record-wire`, `integration_report.json {target, sha, runtime_profile, doubles[]}`; SHA con ruta modificada ⇒ `wire_drift_detected`; bump sin ADR o aprobado por su autor rechazado |
| U42 `pulso-core-runtime`: composición, fábricas e imagen | Como motor, arranco el runtime Core con las siete piezas Pulso y sin dobles de demo (CAP-24/60); primer RED: omitir una fábrica termina con exit 2 que nombra la pieza | U01, U38 | Imagen por SHA, `/healthz`, `/readyz` extendido, `GET /internal/v1/version`; ruta `testing.*` rechazada, `AGENTCORE_ALLOW_DEMO` ⇒ `runtime_profile≠agent_core_real`, Postgres caído ⇒ 503 |
| U43 Executors y ToolDefs generales del lab | Como investigador, uso `lab_query`, `wiki_*` y `lab_write_scratch` como tools de Core (CAP-29); primer RED: un nodo agent ejecuta dos `lab_query` dependientes | U08, U42 | Catálogo `pulso/*` con ToolDef↔handler verificados por CI y `FieldClassifier` con catálogo de columnas; columna no catalogada ⇒ `unclassified_column`, tool sin handler ⇒ `unregistered_tool`, ToolDef sin handler falla CI |
| U44 `agent-core-assets`, seed y bootstrap | Como operador, llevo una instancia vacía al mundo mínimo de forma idempotente (CAP-46..51); primer RED: segundo `pulso-bootstrap core` no escribe en Core | U38, U39, U42 | Mundos, `manifest.yaml`, `expected-state.json`, `bootstrap-report.json`; re-import ⇒ `already_seeded`, credencial bot ⇒ `forbidden_role`, admin `session` ⇒ `step_up_required`, alias de LLM ausente ⇒ `bootstrap_failed`, colisión `kind/id@version` entre mundos |
| U45 Lector de estado Core | Como constructor, leo la release staging/prod y sus entidades verificadas por hash (CAP-07/08/09/10); primer RED: `GET entities` sin `?version=` no se usa para leer una release | U37, U39 | `BaseSnapshot`, `AliasState`/`ObservedAlias`, `core_ref_map`; `base_hash_mismatch`, prod nunca inferido de staging, sondeo por `POST proposals` consume cuota y sólo se permite si la propuesta se usa |
| U46 Compiler Core: plan de drafts, cascada y dry-run | Como constructor, convierto un `ChangeSpec` en la lista completa `changes[]` y predigo `auto_bumped` (CAP-13..20); primer RED: el caso dorado de `disputa-cargo@1.1.0` reproduce `candidate_hash` y `atencion@1.0.1` | U17, U42, U45 | `DraftPlan`, `expected_derived`, dry-run del bridge; `REG-UNREFERENCED`, `REG-VERSION`, `G0-12`, `cascade_mismatch`, `candidate_hash_mismatch`, límites ±1 y precondición vieja rechazados |
| U47 `CoreEvalPackage`: suite, métricas y colas | Como compiler, emito `eval_suite` con `thresholds`, `steps` y colas de respuestas (CAP-21/22); primer RED: suite de `registry-demo` aceptada por `validate` y `evaluate` | U17, U20, U26 | Suite aceptada por Core; los ocho `SuiteProblemCode`, `final_locked` ausente de `changes`/`docs`/`GET proposal`, `queue_order_sensitive`, `suite_missing_seed`, `Expect` vacío rechazado por Pulso |
| U48 Captura de resultados de `evaluate` | Como worker, persisto los seis resultados posibles de la evaluación (CAP-38/42); primer RED: un `fail` conserva el cuerpo 409 completo aunque `last_eval` sea `null` | U18, U37 | `registry_receipt` por resultado; `fail` sin `last_eval`, `failed_infra` sin approve, timeout ⇒ `evaluation_result_lost`/adopción verificada, cuota 429 sin reintento, propuesta huérfana contabilizada |
| U49 Exporter Core y mapping de capas | Como motor, ingiero auditoría, registry y handoffs de Core una vez (CAP-34/35/36); primer RED: dos runs reales aparecen como lotes con cursor y solape sin duplicados | U02, U29, U42 | `PlatformObservationBatch` válidos, `schema_digest`, `LayerMapping`; `run_chain_gap`, `schema_drift`, `eval_db_misconfigured`, evento tardío con hash distinto, run de evaluación fuera de la ingesta |
| U50 Correlación de release | Como memoria, cierro el ciclo con `release.*` y atribuyo la segunda corrida (CAP-37) | U21, U49 | `ReleaseCorrelation`/`exposure_state`; `release_mismatch`, publish sin promote ⇒ sin segunda corrida, promote a otra release, reorden `published/promoted` |
| U51 Registry en memoria con código real (a2) | Como CI, ejecuto el `RegistryService` real del SHA sin Postgres (CAP-54); primer RED: el caso dorado de §31.4.12 en memoria | U39 | Nivel a2 rotulado en el reporte; cambio de símbolos de composición rompe el job en el bump |
| U52 Ambiente local con Core real y `doctor` | Como desarrollador, levanto Pulso y Core y `doctor` lo diagnostica (CAP-58/59/63); primer RED: `doctor` falla con `core_checkout_wrong_sha` ante una imagen distinta | U01, U42 | `dev.ps1 up --with-core`, `reset-core`, redes `pulso-internal`/`core-egress`, `postgres-core`; `/readyz` 503, puerto en conflicto, cgroup `pids` no delegado, clave de prueba en configuración remota |
| U53 Primer E2E real y matriz de aceptación | Como integrador, recorro el caso dorado contra Core real con criterio de éxito y registro de huecos/trazas por SHA (CAP-61, CAP-64) | U18, U19, U21, U38, U41, U44, U52 | `E2E-REAL-01` con `runtime_profile` y `doubles[]` en el reporte; los siete negativos del escenario y la matriz por unidad |
| U54 Constructor real | Como motor, ejecuto el `BuilderToolExecutor` con credencial builder/constructor propia (CAP-32) | U05, U42, U44 | Executor sobre `RegistryService` in-process; crash tras write recupera por clave/readback, misma clave con otro payload ⇒ conflicto, ninguna tool de aprobación o publicación |
| U55 `PulsoScenarioHarness` | Como evaluador, evalúo una task con principal builder y contexto sellado (CAP-40) | U20, U26, U42 | Harness inyectado por `--harness` y en el evaluador del runtime; `failed_infra` ≠ `fail`, el candidato no escribe en el registry operativo |

**Variantes y sucesores con prerequisitos exactos:** son unidades asignables distintas, no aceptación implícita del primer corte de su familia.

| ID / feature | HU y primer UC/RED | Dependencias duras | Handoff y negativo |
|---|---|---|---|
| U08-E Lab E0 | Consulto extracto E0 disponible al reloj sin labels/futuro | U08, U04 | QueryResult E0; join posterior bloqueado |
| U12-E Sensor E0 | Calculo soporte descriptivo sobre contexto E0 real | U12, U08-E | Signal perfil E0; no exige n del histórico |
| U20-E Oracle E0 de seguridad | Como evaluador, sello reglas identidad/canal/abono/regulador antes del candidato | U04, U20, U36 | Policy/oracle/suite refs; expected_identity_check privado y fallo unsafe |
| U22-E Iteración desde E0 | Evento E0 disponible dispara aprendizaje por ingesta/replay real | U04, U12-E, U13, U14, U21, U23, U33 | Run/MemoryUseReceipt; no requiere fuente plataforma U29 |
| U23-A Continuous con activación | Propuesta E0 pasa gates y aprobación antes de usar versión nueva | U23, U19, U21, U22-E | CampaignReceipt; cambio no aprobado nunca se activa |
| U32-M Detalle modelos | Inspecciono llamadas externas LLM/Jev vía Core y sus receipts | U24, U10, U11 | Panel modelos; payload redactado/dependencia caída |
| U32-V Detalle evaluación | Inspecciono candidato y los dos gates separados | U24, U19, U27 | Panel eval; pass nativo no sustituye mejora |
| U32-W Detalle memoria | Inspecciono head/diff/CAS/revocación | U24, U33 | Panel memoria; permisos no amplían acceso |
| U34-F Fork original | Reproduzco otra corrida sin mutar evidencia histórica | U34, U03, U09-A, U15, U33 | Run nuevo/replay_of; snapshot revocado rechazado |
| U34-FE Fork E0 | Reproduzco E0 con reloj y memoria permitidos | U34-F, U04, U23 | Run nuevo E0; final/futuro inaccesibles |

Las unidades U37–U55 se despachan por capacidad (`CAP-xx` de §31); U42 y U44 abren el tracer real con Core, U39–U41 y U51 fijan el contrato y el mock del corte (a)/(a2), y U53 es el único recorrido que puede citarse como integración real local. U05 incluye vigencia/revocación de grants y U06 reducer/run_control/fencing antes de U09/U18. U34 entrega comandos públicos y estado al operador, no introduce por primera vez esos controles de seguridad. U25 acepta manifest mínimo Core determinista; un manifest con modelos externos/Jev/UI/lab añade las dependencias U10/U11/U24/U08 pertinentes. Readiness se verifica por componente seleccionado, no se marca full-stack probado por desplegar sólo Core.

U16 no consume eligible_for_proposal final ni exige que U20 exista: entrega hipótesis de mecanismo/objetivo. U20 sella oracle/baseline y suite; U35 calcula el predicado final antes de U17. El builder sólo obtiene refs/readiness y plan permitido, nunca casos/oracles final_locked. U17 compila también el draft registry kind `eval_suite` vigente cuando la suite no está publicada; U18 lo guarda/congela con el candidato y U19 consume ref/digest exactos. No agregar suite ad hoc después del freeze ni inventar que eval_suite es EntityKind runtime. Tests fijan agent_id/paridad de suite y cambio de hash ante cambio de contenido.

U23 es runner de medición sobre manifest/versions preaprobadas, no prueba publicación autónoma. U23-A acredita la integración de aprendizaje y activación autorizada. U22/U22-E usan sus adapters de entrada reales; llamar directamente al scheduler no prueba el UC evento→aprendizaje.

Para el paquete E0 0.5.1, U04 añade identity_check/timeline, parseo de questions y text_source; U08-E aplica cutoff de started/ended. U36 es capacidad del banco sandbox existente U26, no construcción de auth de la plataforma F7/F8. U20-E entrega fixtures negativos ausentes en histórico y fija políticas/preguntas por digest. U23 sólo acepta E0 bajo ese oracle; el despacho de campaña E0 añade readiness U20-E al gate U35 antes de compiler/writer/evaluación, aunque las implementaciones genéricas se desarrollen con fixtures originales; las campañas originales mantienen U20 sin requerir la muestra E0. Descubrimiento no recibe labels ni respuestas correctas, ni modifica policies para mejorar la tasa aparente.

U01 es excepción habilitadora pequeña, no feature bancaria; no exige todos los schemas ni AWS. U03/U04 son adapters hermanos. U08/U12 tienen variante E0 que añade U04 y los contratos/cutoffs de ese adapter; original-only no espera E0. El primer corte temporal de U04/U08 se prueba temprano, aunque U23 complete los protocolos al final. U15/U33 se pueden construir con fixtures autorizados sin esperar scout; sólo U22 demuestra aprendizaje integrado.

U17 depende del **plan de negocio sellado** U20 para crear el candidato de una campaña; el validador genérico del compiler puede prepararse con fixtures antes. U20 consume mecanismo U16, no resultados U17/U19/U27: no hay circularidad. U10 valida integración externa independiente; U09 arranca sin modelos y U13 reúne ambos. U25 depende de runtime mínimo por manifest, no de publicación bancaria U21; el despliegue no habilita ni elude sus gates.

**Diferenciar construcción de consumo integrado:** UI puede desarrollar componentes contra fixtures desde U01, pero U24 sólo se acepta contra U07 real. Oracle/harness puede desarrollar fixtures desde U26, pero U20 debe sellar objetivo/plan específico desde U16 y U19 debe ejecutar candidato real. Preparación paralela no equivale a dependencia cumplida ni a feature entregada.

### 30.9 Grafo funcional y agrupaciones de aceptación

Las aristas de este DAG son funcionales; la tabla de dependencias completa es normativa. El dibujo muestra el camino principal y ramas para lectura, sin afirmar que una UI habilita detección.

```mermaid
flowchart LR
  U01[U01 Entorno] --> U02[U02 Artefactos]
  U02 --> U03[U03 Original]
  U02 --> U04[U04 E0]
  U02 --> U05[U05 Cuota]
  U05 --> U06[U06 Jobs]
  U06 --> U07[U07 API eventos]
  U07 --> U24[U24 UI lectura]
  U03 --> U08[U08 Lab local]
  U06 --> U08
  U06 --> U09[U09 Core task]
  U06 --> U10[U10 Modelos externos]
  U09 --> U11[U11 Jev]
  U08 --> U12[U12 Sensor]
  U12 --> U13[U13 Scout]
  U09 --> U13
  U10 --> U13
  U13 --> U14[U14 Verifier]
  U11 --> U14
  U14 --> U16[U16 Mecanismo]
  U02 --> U26[U26 Banco sandbox]
  U26 --> U20[U20 Plan sellado]
  U16 --> U20
  U20 --> U35[U35 Elegibilidad final]
  U35 --> U17[U17 Compiler]
  U17 --> U18[U18 Writer]
  U18 --> U19[U19 Core eval]
  U18 --> U27[U27 Comparacion]
  U20 --> U27
  U19 --> U21[U21 Publicacion humana]
  U27 --> U21
  U02 --> U15[U15 Wiki scratch]
  U15 --> U33[U33 Memoria CAS]
  U33 --> U22[U22 Segunda iteracion]
  U21 --> U22
  U04 --> U23[U23 Replay E0]
  U27 --> U23
  U33 --> U23
  U09 --> U25[U25 Deploy autorizado]
  U25 --> U28[U28 Lab AWS]
  U08 --> U28
```

**Despacho:** unidad lista cuando sus prerequisitos concretos están integrados/revisados, contrato fijado y scope libre. No exigir “toda P1” para iniciar una unidad de P2 ni detener el motor por UI/AWS pendientes. Seguridad/permiso/cuota siguen siendo prerequisitos duros de la operación correspondiente. Las fases son hitos de aceptación del conjunto, no aristas adicionales al DAG.

| Hito/fase | Features que reúne el integrador | Recorrido de aceptación y paralelismo |
|---|---|---|
| P0 Base | U01, U02 y primer corte U03 | Clone→doctor→snapshot durable; U04/U05/U15/U26 pueden avanzar al tener U02, sin esperar fuentes completas |
| P1 Tracer | U03, U05–U11, U07/U24 mínimo y primer corte U04 | Source→job→Core→lab→receipt→UI; U08/U09/U10 hermanos tras sus prerequisitos, no un único paquete runtime |
| P2 Descubrimiento | U12–U16, U15/U33, U29/U30; U08-E/U12-E para E0 y UI de evidencia | Señal→investigación→verificación→bridge; memoria/banco/oracles avanzan lateralmente; detector funciona sin UI |
| P3 Cambio seguro | U16–U20, U26/U27/U35 y U32-V para UI de gates; U36/U20-E para E0 | Mecanismo→plan sellado→candidate→dos gates; integra A1/B1/A2/B2, no asigna builder y juez al mismo autor |
| P4 Automejora | U21–U23, U31/U33/U34, U32/U32-M/U32-V/U32-W; U22-E/U23-A para automejora E0 | Espera humana→staging→evento→memoria→nuevo run, reflexividad y replay temporal; publicación no se finge exposición real |
| P5 Operación | U25/U28, U32/U32-M/U32-V/U32-W, U34/U34-F y U34-FE para E0; carga/chaos/restore/a11y | Stack reproducible, permisos/smoke AWS autorizados y rollback; trabajo infra comienza antes, no bloquea la demostración local |

Validaciones de carga, seguridad, accesibilidad, retención y restore son paquetes de calidad transversales con owner/test/gate propios, no features que se inventan para rellenar una fase. U32 comienza por un tipo de detalle y añade los demás como sucesores; U34 primero pausa y después cancel/fork-replay como hijos con tests separados. Los grupos de frontend no convierten todas las capacidades de un panel en una única historia.

Cada integrador publica matriz Uxx→UC→test→head/entorno→resultado y cobertura S/AC/E0/E/C. Sólo declare passed para la aceptación realmente ejecutada. Revisores independientes comprueban tanto unidades como recorrido del grupo; los hallazgos de acoplamiento generan otro RED de integración. Las agrupaciones no sustituyen contrato de entrega ni disciplina de §§30.1/30.2/30.5/30.6.

**Ownership para asignación:** `improvement-engine` posee U01 (bootstrap, Compose, PG CI y doctor locales), además de backend U02/U05/U06/U07/U29/U34; data U03/U04/U08/U12/U30 y variantes E0; AI/runtime U09/U10/U11/U13/U14/U16/U17/U18/U31; memoria U15/U33; evaluación independiente U19/U20/U20-E/U23/U26/U27/U35/U36 y U23-A; integración funcional U21/U22/U22-E; frontend U24/U32 y paneles sucesores. `infra` posee U25/U28: Terraform y los contratos AWS, sin fixtures, Compose ni CI local del motor. Son roles, no personas permanentes: cada despacho fija un implementador, integrador y reviewers distintos, con área exclusiva. Backend conserva owner de migrations incluso si una feature data/AI las necesita. Builder U17/U18 nunca es autor de U20/U27/U35 ni altera su gate para cerrar un test.

No aceptar implícitamente variantes: “original-only” puede cerrar sus recorridos, pero el DoD del producto con E0 exige las unidades E0 enumeradas. Una entrega local puede estar aceptada mientras AWS sigue blocked por autoridad, sin llamarse desplegada. El script `docs/validation/Test-ImplementationDag.ps1` comprueba IDs/dependencias/ciclos del catálogo, no semántica, implementación, cobertura ni seguridad; las revisiones y pruebas de cada grupo siguen obligatorias.

## 31. Capacidades de integración con Agent Core: lo que Pulso debe poder hacer

### 31.1 Alcance, reglas, ownership e índice de capacidades

Esta sección enumera **lo que Pulso tiene que poder hacer contra Agent Core** (SHA `86a767474042a566a0dbd6ed23588959f27ebdb3`, contrato 1.3.0) y que §§17, 24, 27 y 29 daban por supuesto o describían sin contrato construible. No es un backlog: cada capacidad (`CAP-xx`) es un contrato de entrada, salida, precondiciones, errores tipados y verificación en mock y real. Las unidades asignables viven en §30.8 (U37–U55, ver el catálogo). Sólo contiene responsabilidad **nuestra** (Pulso, `improvement-engine`, `infra`, CI, mocks, scripts de bootstrap que operamos); lo que debe proveer agent-core vive en §31.12 y §29.9, cada fila con su workaround nuestro. No duplica §29.8/§29.9: las enlaza.

**Método de verificación de lo escrito aquí.** Lo marcado *observado* se obtuvo leyendo el código del SHA y ejecutando, en un entorno `uv` aislado del checkout, `build_candidate`/`validate_candidate` y un `RegistryService` en memoria (`InMemoryRegistryStore`, `testing.registry_demo.build_harness`) con el flujo completo de §31.4.12. No son respuestas de `agentcore serve`, no son tests upstream ejecutados por Pulso y no acreditan integración real (§27.6). Lo no verificado lleva "sujeto a verificación".

**Reglas normativas de la sección.**

| # | Regla |
|---|---|
| R1 | Ninguna capacidad se da por integrada citando el mock. Todo reporte de integración lleva `target ∈ {mock, a2, real_local, real_aws}`, `sha`, `contract_version` y `doubles[]` (piezas que son dobles de demo; vacío = ninguna). §27.6 sigue rigiendo la secuencia (a)→(b); aquí se añade el nivel (a2) de §31.10.2. |
| R2 | No se inventan endpoints, campos ni códigos de agent-core. Si falta una lectura, el estado es `unknown`/`alias_unknown`/`dependency_blocked` y la UI no afirma lo que no puede probar. |
| R3 | Respuesta con `type`, `code`, campo o forma desconocida ⇒ `unknown_upstream_shape`: se bloquea la operación y se abre hallazgo de drift; no se reintenta ni se interpreta por parecido. |
| R4 | Códigos de error: `registry:<code>` = `urn:agentcore:registry:<code>` upstream; `runtime:<code>` = `urn:agentcore:problem:<code>` upstream; todo 401 es `urn:agentcore:problem:credentials_invalid` (o `principal_expired`) ⇒ `runtime:credentials_invalid`; `pulso:<code>` = error nuestro, nunca atribuido a Core. |
| R5 | Ninguna credencial (JWS, JWT de servicio, claves) se persiste en artefactos, bitácora, eventos, OTel ni receipts; se guarda `kid`, digest y expiración. |
| R6 | Toda evaluación, receipt o evidencia conserva `target`, `sha` y `doubles[]`. Evidencia `contract_fixture` no se promueve a "real". |
| R7 | Los estados `especificada` asumen la **recomendación** de cada decisión abierta listada en `DECISIONES_ABIERTAS_V3_AGENT_CORE.md` (D-1..D-12; resumen en el encabezado «Decisiones provisionales de integración» de este documento). Si la revisión con el equipo de agent-core elige otra opción, los CAP listados en "bloquea" de esa decisión se replantean; no se construyen sobre la opción no elegida. Las decisiones se adoptaron como **DECISIÓN PROVISIONAL D-n (adoptada, revisar con equipo agent-core)** el 03-10-2026 y así se marcan donde aparecen. |

**Ownership decidido (qué es nuestro, de agent-core o frontera).**

| Pieza | Dueño | Razón y límite |
|---|---|---|
| Cliente HTTP Rust, clasificador de errores, perfil de endpoint, sonda | NUESTRA | §31.2 |
| Emisor de credencial bot (JWS EdDSA), claves staff/identity, rotación | NUESTRA | Core sólo verifica claves públicas (`jws_identity.py`) |
| Emisor de credencial humana step_up en AWS/producción | FRONTERA → plataforma/IdP de la organización | Pulso consume; local usa emisor de prueba nuestro (CAP-43/44) |
| Proceso `pulso-core-runtime` (composición de Core, bridge, siete fábricas, imagen) | NUESTRA | Tradicionalmente "frontera"; se decide nuestra porque contiene identidad builder, grants y executors Pulso (§29.8) |
| Fábricas `tools/authz/transcript/calibration/classifier/field-classifier/grant-active` para `pulso-evolution` | NUESTRA | Las del mundo de atención bancaria real son de la plataforma; en nuestro mundo de prueba son dobles etiquetados (CAP-49) |
| Derivación de schemas wire faltantes, hash de contenido, compiler, dry-run | NUESTRA | Publicación upstream de esos schemas: solicitud §31.12 |
| Relay/exporter de eventos de Core | NUESTRA | Core no empuja eventos (§31.6) |
| Mock fiel, nivel a2, dual-run, CI, `doctor`, compose, Terraform, ADR 0003 de `infra` | NUESTRA | — |
| `agentcore registry import`, `migrate`, `contracts`, `validate` | AGENT-CORE (existen) | Los ejecutamos con nuestras credenciales/fábricas |
| Endpoint de versión de instancia, lectura de alias nativa, schemas de registry en `contracts/`, cambios a nivel release, garantía expand/contract | AGENT-CORE | §31.12; workaround nuestro vigente |
| Protocol `ScenarioHarness` y su cargador `--harness` | FRONTERA → NUESTRA | Core define el puerto; la implementación con identidad builder es nuestra (§29.8) |

**Hechos del SHA que condicionan el diseño (verificados leyendo código).**

| # | Hecho | Evidencia |
|---|---|---|
| H1 | `agentcore serve` fuera de demo exige `--tools --authz --transcript --calibration --classifier --field-classifier --grant-active` como `modulo:atributo`, rechaza rutas bajo `testing.*`, exige `--identity-keys`, y con `--registry-api` exige `--eval-dsn` ≠ `--dsn` y `--staff-keys`. Las fábricas reciben sólo `DemoContext{clock, ids, registry}` | `composition/serve_ports.py::resolve_ports` |
| H2 | La CLI `serve` no acepta extensiones ni `limits`; pero `build_api_deps(ports, registry_service=…)`, `ApiDeps.extensions`/`limits`/`readiness` y `registry_extension` permiten componer un proceso propio | `composition/serve.py`, `api/app.py::ApiDeps` |
| H3 | El paquete `testing` (dobles, `TestStaffIssuer`, semillas) no se empaqueta en el wheel (`packages = ["agent_core","agent_telemetry"]`) y el repo no trae Dockerfile; su compose sólo define `postgres:16` | `pyproject.toml`, `docker-compose.yml` |
| H4 | `POST /v1/runs` es síncrono y devuelve `run_id` sólo al terminar; `GET /v1/runs/{id}` y `RunResult.output` no incluyen facts; la salida de un nodo `agent` no puede llegar a `end.output_map` (G0-22); no hay `GET /v1/runs` ni cancelación | `api/schemas.py::run_summary`, `contracts/openapi.json` (7 rutas) |
| H5 | El registry HTTP expone 16 rutas; no hay lectura de alias, de versiones ni listado de propuestas; `GET /entities/{kind}/{id}` sin `?version=` devuelve la última versión, no la de una release | `registry/http.py`, `service.get_entity` |
| H6 | `evaluate` síncrono: `pass`→200 y `evaluated`; `failed_infra`→200 y sigue `candidate`; `fail`→409 `gate_failed` con `payload=EvalReport`, la propuesta vuelve a `draft` con `candidate_hash=None` y `GET proposal` devuelve `last_eval=null`; el reporte no trae `eval_run_id` | `registry/service.py::evaluate/get_proposal` |
| H7 | `import_seed` no es idempotente (agente con `staging` ⇒ `illegal_transition`), exige admin humano step_up, una release y a lo sumo una suite por agente, y deja `staging` **y** `prod` en la release importada aunque el YAML declare sólo `prod`. Se invoca por `agentcore registry import <root>` (con `--verifier` y `--harness` fuera de demo) | `registry/service.py::import_seed`, `composition/registry.py` |
| H8 | `content_hash = sha256(JCS(model_dump(mode="json", by_alias=True)))` sobre el modelo normalizado (con defaults y `null`); la forma `exclude_none` de los YAML da otro hash (`6b5b5794…` vs `5876e2f4…` para `disputa-cargo@1.0.0`, observado) | `registry/entities.py`, `domain/json.py` |
| H9 | `EvalSuite` lleva `thresholds{metric_id→{noise_margin, floor?}}`; cada métrica `gate`/`guardrail` de `Agent.metrics` exige umbral; `missing_suite` si el agente no tiene suite al evaluar | `registry/suite.py::suite_problems` |
| H10 | `Quotas` (10 propuestas/24 h y 20 evaluaciones por propuesta, sólo `origin=auto_detect`) y `RateLimitConfig` (30 turnos con uso registrado por ventana de 60 s y 5 USD/día por principal; cuenta filas de `usage` vía `add_usage`, un rechazo no consume cuota) usan defaults sin flag en `serve`; son inyectables en composición propia | `registry/quotas.py`, `api/limits.py`, `composition/serve_registry.py` |
| H11 | Tres bases/DSN distintos: `--dsn` (motor+auditoría+registry), `--eval-dsn` (runs de evaluación), y ninguno es el de Pulso. `migrate` es idempotente y sin migraciones versionadas | `composition/migrate.py` |
| H12 | `contracts/events/OutboundEvent.json` y `catalog.json` existen; agent-core no entrega eventos (sólo proyectores puros); `audit_events` tiene `PRIMARY KEY (run_id, seq)`, `event_id UNIQUE`, `ts timestamptz`, sin secuencia global; `reg_events.seq` y `outbox.seq` son `bigserial` | `contracts/events/`, `adapters/sql/audit_events.sql` |

**Índice de capacidades.** Estado: `especificada` (contrato escrito y construible por nosotros), `especificada (condicionada a D-n)` (contrato escrito asumiendo la opción recomendada de la decisión D-n, adoptada provisionalmente; se replantea si la revisión con el equipo agent-core elige otra opción) o `dependency_blocked` (bloqueada por una decisión del dueño o por agent-core; el bloqueo está en la última columna).

| ID | Poder… | § | Estado | Bloqueo / decisión |
|---|---|---|---|---|
| CAP-01 | alcanzar una instancia identificada (perfil, red, timeouts) | 31.2.1 | especificada | — |
| CAP-02 | hablar HTTP desde Rust con política de transporte definida | 31.2.2 | especificada | — |
| CAP-03 | clasificar toda respuesta y todo error de Core | 31.2.3 | especificada | — |
| CAP-04 | presentar credencial builder/constructor que Core acepte | 31.2.4 | especificada (condicionada a D-12) | D-12 (principal de run) |
| CAP-05 | autenticar Rust↔bridge↔control-api con JWT de servicio | 31.2.5 | especificada | — |
| CAP-06 | saber con qué versión de Core hablamos | 31.2.6 | especificada | endpoint nativo: N-04 |
| CAP-07 | leer la release staging vigente y sus entidades | 31.3.1 | especificada (condicionada a D-1, D-8) | D-1, D-8 |
| CAP-08 | leer el alias vigente (staging/prod) | 31.3.2 | especificada (condicionada a D-1, D-8) | D-1, D-8 |
| CAP-09 | resolver release→agente y run→release | 31.3.3 | especificada | — |
| CAP-10 | verificar lo creado: diff, lineage y mapa de referencias | 31.3.4 | especificada | — |
| CAP-11 | fijar schemas wire y derivar los que faltan | 31.4.1 | especificada | N-01 (publicación upstream) |
| CAP-12 | serializar `content` y calcular `content_hash` como Core | 31.4.2 | especificada | — |
| CAP-13 | traducir `ChangeSpec` a la lista completa `changes[]` | 31.4.3 | especificada | — |
| CAP-14 | producir cada `EntityKind` permitido (catálogo del primer corte) | 31.4.4 | especificada (condicionada a D-10) | D-10 |
| CAP-15 | asignar versiones y predecir la cascada `auto_bumped` | 31.4.5 | especificada | — |
| CAP-16 | validar antes del round-trip (prefiltro, dry-run, `/validate`) | 31.4.6 | especificada (condicionada a D-1, D-9) | D-1, D-9 |
| CAP-17 | reconstruir clausura y comparar `candidate_hash` | 31.4.7 | especificada (condicionada a D-9) | D-9 |
| CAP-18 | redactar `docs` de versión sin contaminar hashes ni filtrar datos | 31.4.8 | especificada | — |
| CAP-19 | presupuestar límites y cuotas al compilar | 31.4.9 | especificada | — |
| CAP-20 | fijar y comprobar la precondición de base de cada operación | 31.4.10 | especificada | — |
| CAP-21 | generar la `eval_suite` desde `ScenarioCase` con métricas y umbrales | 31.4.11 | especificada | — |
| CAP-22 | sembrar respuestas de tools deterministas para el sandbox de Core | 31.4.11 | especificada | — |
| CAP-23 | cambiar elementos a nivel release (interrupciones, idioma, ruleset) | 31.4.4 | dependency_blocked | N-07 |
| CAP-24 | componer y arrancar el runtime Core de Pulso (`pulso-core-runtime`) | 31.5.1 | especificada (condicionada a D-1, D-2, D-3) | D-1, D-2, D-3 |
| CAP-25 | invocar una task con el cuerpo y la idempotencia que Core acepta | 31.5.2 | especificada (condicionada a D-1) | D-1 |
| CAP-26 | fijar la release exacta que ejecuta una task | 31.5.3 | especificada (condicionada a D-1) | D-1 |
| CAP-27 | ligar contexto privado y binding antes de efectos | 31.5.4 | especificada (condicionada a D-1) | D-1 |
| CAP-28 | leer resultado y facts de un run | 31.5.5 | especificada (condicionada a D-1) | D-1 |
| CAP-29 | registrar executors y ToolDefs generales (lab, wiki) | 31.5.6 | especificada (condicionada a D-1, D-2) | D-1, D-2 |
| CAP-30 | reconciliar una invocación incierta | 31.5.7 | especificada (condicionada a D-1) | D-1 |
| CAP-31 | acotar tiempo, tamaño, concurrencia, cancelación y tasa | 31.5.8 | especificada (condicionada a D-1, D-12) | D-1, D-12 |
| CAP-32 | correr el constructor real (`BuilderToolExecutor`) con credencial propia | 31.5.9 | especificada (condicionada a D-1) | D-1 |
| CAP-33 | versionar y autenticar los contratos del bridge | 31.5.10 | especificada (condicionada a D-1) | D-1 |
| CAP-34 | extraer observaciones de Core (auditoría, registry, handoffs) | 31.6.1 | especificada (condicionada a D-4) | D-4 |
| CAP-35 | mantener cursor, dedupe, gaps y lote hacia Pulso | 31.6.2 | especificada (condicionada a D-4) | D-4 |
| CAP-36 | aplicar el mapping versionado agente/flow/nodo/release→capa | 31.6.3 | especificada | — |
| CAP-37 | cerrar el ciclo: correlacionar release y exposición | 31.6.4 | especificada | — |
| CAP-38 | ejecutar `evaluate` y capturar todo resultado posible | 31.7.1 | especificada | — |
| CAP-39 | combinar el gate nativo con el gate de mejora y la revisión | 31.7.2 | especificada | — |
| CAP-40 | evaluar tasks con `PulsoScenarioHarness` | 31.7.3 | especificada (condicionada a D-1) | D-1 |
| CAP-41 | usar el banco sandbox stateful en el gate nativo | 31.7.4 | dependency_blocked | D-7 |
| CAP-42 | reconciliar tras respuesta perdida y gestionar cuota | 31.7.5 | especificada | — |
| CAP-43 | obtener y relevar identidad humana step_up (emisor local) | 31.8.1 | especificada (condicionada a D-5) | D-5 |
| CAP-44 | obtener identidad humana step_up en AWS/producción | 31.8.1 | dependency_blocked | D-5 |
| CAP-45 | recorrer approve→publish→promote con claves y confirmación | 31.8.2 | especificada | — |
| CAP-46 | publicar y versionar `agent-core-assets` (layout y mundos) | 31.9.1 | especificada (condicionada a D-10) | D-10 |
| CAP-47 | sembrar un registry vacío (import) y reconocer `already_seeded` | 31.9.2 | especificada | — |
| CAP-48 | reproducir el mundo desde cero de forma idempotente (`pulso-bootstrap core`) | 31.9.3 | especificada (condicionada a D-6) | D-6 |
| CAP-49 | declarar el mundo mínimo y su suite baseline | 31.9.4 | especificada (condicionada a D-2, D-10) | D-10, D-2 |
| CAP-50 | configurar modelos, claves y parámetros de despliegue de Core | 31.9.5 | especificada | — |
| CAP-51 | detectar deriva del mundo sembrado | 31.9.6 | especificada | — |
| CAP-52 | correr un mock fiel del registry (`platform-sim/registry`) | 31.10.1 | especificada | — |
| CAP-53 | correr un mock fiel del bridge (`contract_mock`) | 31.10.1 | especificada (condicionada a D-1) | D-1 |
| CAP-54 | ejercitar la lógica real de candidatas sin Postgres (nivel a2) | 31.10.2 | especificada | — |
| CAP-55 | demostrar paridad mock↔real con una suite dual-run y fixtures grabados | 31.10.3 | especificada | — |
| CAP-56 | reproducir y forzar errores, límites y cuotas reales (±1) | 31.10.4 | especificada | — |
| CAP-57 | verificar pin y drift en CI y gobernar el bump | 31.10.5 | especificada (condicionada a D-11) | D-11 (cadencia) |
| CAP-58 | levantar un Core real junto a Pulso en local | 31.11.1 | especificada (condicionada a D-3, D-6) | D-6, D-3 |
| CAP-59 | diagnosticar la conexión con `doctor` | 31.11.2 | especificada (condicionada a D-6) | D-6 |
| CAP-60 | construir, versionar y arrancar la imagen del runtime | 31.11.3 | especificada (condicionada a D-3) | D-3 |
| CAP-61 | ejecutar el primer E2E real con criterio de éxito | 31.11.4 | especificada (condicionada a D-1, D-9, D-10) | D-1, D-9, D-10 |
| CAP-62 | desplegar Core y Pulso en AWS por manifest con rollback conjunto | 31.11.5 | dependency_blocked | D-3, ADR 0003 aceptada |
| CAP-63 | manejar credenciales y datos de prueba sin fuga | 31.11.6 | especificada | — |
| CAP-64 | correlacionar trazas y registrar huecos conocidos por SHA | 31.11.7 | especificada | — |

**Nota de estado de implementación (2026-10-04, Team Claude, aditiva; no cambia ningún contrato ni la columna «Estado» de arriba, que describe la especificación).** Verificado con `gh api` contra `main` de improvement-engine (`83516eb`). Toda la evidencia es local (PG16 en Podman, presupuesto de GitHub Actions agotado), con `doubles[]` declarados; nada de esto es un H4 conjunto ni un resultado `real_aws`. Detalle y conteos de pruebas en [ESTADO_IMPLEMENTACION_CLAUDE_2026-10-03.md](ESTADO_IMPLEMENTACION_CLAUDE_2026-10-03.md).

| Capacidad | Estado de implementación | PR (SHA de fusión) |
|---|---|---|
| CAP-08 lectura de alias (staging/prod) | Implementada y fusionada: `GET /internal/v1/core-state/aliases/{agent_id}/{alias}` (antes 501) | improvement-engine#82 (`5ec0530`) |
| CAP-16 L2 dry-run de autoría | Implementada y fusionada: `POST /internal/v1/core-authoring/dry-run` ejecuta `build_candidate` + `validate_candidate` del SHA en transacción de sólo lectura; `candidate_hash`, `release_id_preview` y `auto_bumped` coinciden con el `freeze` real (verificado en PG16); un 200 con `valid:false` no es éxito | #82 (`5ec0530`) |
| CAP-33 contratos del bridge versionados | Implementada y fusionada como paquete `bridge-contract/` (OpenAPI 3.1, 28 JSON Schemas generados con gate de deriva, goldens grabados del runtime real, kit de conformancia, README por ruta) | #82 (`5ec0530`) |
| Alineación con el anexo D | Implementada y fusionada (ADR 0011): `sub=worker:<id>` en toda ruta `aud=core-bridge`, `job_id` del token igual al del cuerpo en invoke, `Idempotency-Key` en arms, nombres de `ArmRequest` del anexo (`execution_profile`, `sandbox_session_ref`, `deadline`; los previos quedan como alias deprecados un release), `evaluation_context_ref` derivado en servidor (`evc-` + `sha256_hex(tenant\|job_id\|binding_ref\|proposal_id\|candidate_hash\|attempt)[:40]`), `CoreVersion` con `schema_version` y `bridge_instance_id` | #86 (`83516eb`) |
| CAP-24..32, CAP-47..52, CAP-53, CAP-58..61, CAP-63 (runtime compuesto, invoke/binding/reconcile, tools, evaluación nativa, mocks, stack local, E2E, doctor, imagen) | Implementadas y fusionadas con dobles declarados; E2E sobre imagen real con 44 pruebas vivas (stand-in de Codex, no control-api real) | #76 (`6107f10`), #79 (`4a1fa7b`) |
| CAP-43 emisor humano local | Implementada y fusionada (`local-identity/`, sólo sandbox) | #76, #79 |
| CAP-57 pin y deriva | Pin `894fa65` fusionado (#82, ADR 0010, dual-pin); `pin-watch` en #76; bump a `c814c2b` en curso | #82; sin PR aún |
| CAP-62 despliegue AWS por manifest, CAP-44 identidad humana AWS | Siguen `dependency_blocked`; infra declarada y apagada por defecto (infra#17, #23, #24, #26), nada aplicado | infra#17, #23, #24, #26 |

Pendiente del lado Codex y no cubierto por lo anterior: cliente HTTP Rust contra `bridge-contract/`, superficie HTTP del control-api y mapeo del flujo E0 → Core.

### 31.2 Conectarse y autenticarse

#### 31.2.1 CAP-01 — Perfil de endpoint y alcance de red

| Campo | Contrato |
|---|---|
| Entrada | `AgentCoreEndpointProfile{target, runtime_base_url, registry_base_url, bridge_base_url, expected_image_digest?, expected_sha, expected_contract_version, connect_timeout, request_timeouts{runtime_task, registry_read, registry_write, evaluate}, max_inflight{runtime_task, evaluate=1}}` dentro de `RunConfigRevision`; nunca en prompt ni en el job. En la topología adoptada provisionalmente (D-1, revisar con equipo agent-core) las tres URLs comparten host y puerto y difieren en prefijo (`/v1/runs`, `/v1/registry`, `/internal/v1`) |
| Salida | Cliente configurado y `EndpointProbeReceipt{profile_digest, healthz, readyz, conformance_probe_digest, observed_at, doubles[]}` |
| Precondiciones | Servicio alcanzable por nombre estable. Local: mismo proyecto Compose o red nombrada, proceso con `--host 0.0.0.0` (el default `127.0.0.1` no es alcanzable desde otro contenedor), puerto 8000; la red `pulso-internal` es `internal: true`, así que el runtime Core pertenece además a una red `core-egress` (LLM/Jev) y sólo él entra en ambas. AWS: SG de origen engine→pulso-core-runtime:8000, nombre interno estable (Cloud Map, Service Connect o ALB interno: decisión de `infra`) |
| Errores tipados | `pulso:endpoint_unreachable`, `pulso:endpoint_not_ready` (`/readyz` 503 con `{"status":"unavailable","failed":[…]}` no es problem+json), `pulso:profile_mode_mismatch` (modo declarado `real_*` pero la sonda de CAP-06 devuelve forma de mock), `pulso:port_conflict` |
| Verificación mock | `platform-sim` expone `/healthz`/`/readyz` y `target=mock` fuera del wire; ningún receipt toma `upstream_commit` del servidor |
| Verificación real | `doctor` (CAP-59) y sonda de CAP-06; `target=real_*` sólo con `expected_image_digest` fijado y sonda aprobada |

Regla: `upstream_commit`, `target` y `doubles[]` de todo receipt salen del perfil validado, no de una autodeclaración del servidor.

#### 31.2.2 CAP-02 — Cliente HTTP Rust y política de transporte

Ownership: un único crate adaptador (`adapters/agent_core_http` para `/v1/registry` y, si se usa, `/v1/runs`; `adapters/core_bridge_http` para `/internal/v1`) es dueño de `reqwest`/TLS/pools; ningún otro crate abre sockets hacia Core. El crate HTTP no existe hoy en el workspace (sin `reqwest` en `Cargo.toml`); se elige librería por ADR.

| Regla | Contrato |
|---|---|
| Números | `Decimal` se lee como string/decimal exacto, nunca `f64` (Core serializa con `dumps` de M0) |
| Cabeceras | `Authorization: Bearer <JWS>` (bot: emitido por `pulso-core-runtime` vía `POST /internal/v1/core-credentials/issue`, CAP-33/CAP-04; humano: `HumanAuthorizationPort`, CAP-43; el worker Rust despacha approve/publish/promote con el JWS en memoria), `Content-Type: application/json`; `Idempotency-Key` (≤255 caracteres imprimibles) obligatorio en `POST /v1/runs` y `POST …/publish`: su ausencia se rechaza **localmente** antes de enviar (`pulso:contract_error{missing_idempotency_key}`) |
| Reintento | Ninguno automático en create, evaluate, approve, promote, revoke. Reintento acotado con backoff sólo en GET y en publish con la misma clave (§27.3). Un `GET /entities` sin `?version=` no se usa nunca para leer una release (devuelve la última versión) |
| Concurrencia | Un `evaluate` a la vez por instancia (`max_workers=1` upstream); `max_inflight` por servicio; cola local acotada |
| Timeouts | Valores iniciales propuestos, a medir en la primera corrida real: conexión 5 s, lectura de registry 10 s, escritura de registry 15 s. `evaluate` y `runtime_task` toman su timeout del `CoreEvaluationExecutionProfile`/`deadline` sellados (§27.2, §31.5.8); nunca menor que el presupuesto de pared del Agent |
| Cuerpos | `application/json` obligatorio; 2xx no JSON o truncado ⇒ `unknown_upstream_shape` |
| Trazas | `traceparent` saliente; se guarda `trace_id` de la respuesta en el receipt (CAP-64) |

Verificación: servidor de prueba que corta la conexión tras el commit, responde lento por encima del timeout, trunca el JSON o devuelve 2xx no JSON ⇒ resultado `unknown`, nunca retry ciego.

#### 31.2.3 CAP-03 — Clasificación de respuestas y errores

Clasificador único; el adaptador conserva status, `code` y cuerpo tratado además de la traducción al Problem interno.

| Observación | Clase | Acción |
|---|---|---|
| Fallo DNS/conexión/TLS antes de enviar | `transport_not_sent` | reintento permitido |
| Timeout o corte tras enviar | `transport_unknown` | `unknown/manual_reconcile` según operación (§27.3) |
| `application/problem+json` `urn:agentcore:registry:*` | `registry:<code>` | tabla siguiente |
| `application/problem+json` `urn:agentcore:problem:*` | `runtime:<code>` | tabla de runtime. Todo 401 (también el de `/v1/registry/*`, de otro verificador o `principal_expired`) es `urn:agentcore:problem:credentials_invalid`/`principal_expired` y se clasifica `runtime:credentials_invalid`/`runtime:principal_expired`: renovar credencial **una vez** y sólo si la operación es GET o publish con clave; si persiste, `pulso:auth_config_error` y alerta |
| `/readyz` 503 con `failed[]` | `not_ready` | espera con backoff, no es error de dominio |
| `code`/`type` desconocido, campos faltantes | `unknown_upstream_shape` | bloquear y abrir hallazgo (R3) |

Registry (12 códigos, `registry/errors.py`):

| Código | HTTP | Acción de Pulso |
|---|---|---|
| `validation_failed` | 422 | guardar `violations`; no avanzar; no reintentar. `POST …/validate` responde 200 con `violations`: HTTP 200 no es éxito |
| `gate_failed` | 409 | **persistir el cuerpo completo** (`payload` = `EvalReport`); la propuesta vuelve a `draft` (§31.7.1) |
| `proposal_stale` | 409 | rebase a draft, nueva construcción, evaluación y aprobación |
| `candidate_changed` | 409 | releer propuesta; invalidar aprobación previa |
| `illegal_transition` | 409 | releer estado; en publish con clave reutilizada es defecto de contrato local |
| `loosening_not_accepted` | 409 | `waiting_decision` con la lista tipada de `yardstick_changes` (§31.7.2); nunca aceptar por defecto |
| `idempotency_conflict` | 409 | defecto de contrato local: clave reutilizada con otro payload |
| `forbidden_role` | 403 | `permission_blocked`; para op humana crear `DecisionRequest`; sin reintento |
| `step_up_required` | 403 | `waiting_human_reauthentication` (§27.5); sin reintento automático |
| `quota_exceeded` | 429 | posponer hasta salir de la ventana; incidente de presupuesto, no flujo normal |
| `not_found` | 404 | releer; clasificar |
| `integrity_error` | 500 | `unknown`; reconciliación manual; sin reintento ciego |

Runtime (`api/problems.py`, `PROBLEM_STATUS`): `credentials_invalid` 401 y `principal_expired` 401 ⇒ `core_auth_failed`; `agent_forbidden`/`subject_forbidden`/`version_pin_forbidden`/`principal_mismatch`/`delegation_*` 403 ⇒ error de configuración de identidad, sin reintento; `not_found` 404 ⇒ `agent_not_found`; `idempotency_conflict` 409 ⇒ defecto de contrato local; `invalid_request` 422 ⇒ error de contrato/compilación, no reintento; `rate_limited`/`cost_budget_exceeded` 429 ⇒ espera hasta la ventana con evento explicado; `run_closed` 410, `turn_in_progress` 409, `handoff_already_resolved` 409 ⇒ no aplican a tasks y se tratan como `unknown_upstream_shape` si aparecen; `internal_error` 500 ⇒ `unknown`.

Verificación: cada fila tiene un caso en la suite dual-run (CAP-55); el 401 `urn:agentcore:problem:credentials_invalid` se prueba contra mock y real, también en `/v1/registry/*` (`install_error_handlers` se instala antes de las extensiones, `app.py:135`, y `registry/http.py:104` no registra su handler propio si ya existe).

#### 31.2.4 CAP-04 — Credencial builder/constructor — DECISIÓN PROVISIONAL D-12 (adoptada, revisar con equipo agent-core)

| Campo | Contrato |
|---|---|
| Formato | JWS compacto Ed25519: `base64url(header).base64url(payload).base64url(firma)` sin relleno, ≤ 8192 caracteres. Header **exactamente** `{"alg":"EdDSA","kid":<str>,"typ":"principal+jws"}` (cualquier clave extra o faltante se rechaza); la firma cubre `"<head>.<body>"`. Payload = `Principal` serializado con la convención de M0 (instantes UTC, `Decimal` exacto) |
| Bot constructor (perfil de §27.5) | `{type:"builder", id:"pulso-constructor:<tenant>", roles:["constructor"], scopes:[], attrs:{…sin actor…}, auth:{level:"session", at}, exp}`; nunca `attrs.actor="human"`; nunca `service`. `attrs` no lleva datos sensibles (se proyectan a eventos por `reportable_attrs`). TTL ≤ 15 minutos, renovar con margen de 20 % |
| Principal de run | `type=builder` firmado con una clave presente en `--identity-keys`; es un archivo y un `kid` **distintos** de los de `--staff-keys` (dos verificadores independientes; una credencial válida en uno no lo es en el otro) |
| Claves | Dos pares Ed25519 por entorno (staff e identity) y, aparte, el emisor humano (CAP-43/44). Archivo público `{"principal_keys":{kid:b64url(32 bytes)}}` (`delegation_keys` opcional en identity; el verificador staff no la usa). La clave privada del bot vive en el secreto del emisor de Pulso dentro de `pulso-core-runtime`, nunca en Git ni en el proceso Rust. El worker Rust obtiene el JWS del bot (TTL corto, en memoria, nunca persistido) llamando a `POST /internal/v1/core-credentials/issue` (CAP-33) y lo envía como `Authorization: Bearer` a `/v1/registry`; la credencial humana (approve/publish/promote) la obtiene por `HumanAuthorizationPort` (CAP-43) y nunca la emite el bridge |
| Rotación | Publicar `kid` nuevo, aceptar ambos, retirar el viejo. `load_identity_verifier` lee los archivos **sólo al arrancar**: rotar exige reinicio planificado del runtime (ventana declarada) hasta que exista recarga upstream (N-09). El emisor no firma con `kid` retirado |
| Errores tipados | `pulso:credential_signing_unavailable`, `auth:credentials_invalid`, `runtime:principal_expired`, `registry:forbidden_role`, `runtime:rate_limited`/`cost_budget_exceeded` (con D-12 = A hay un principal por `(tenant, rol)`, así que el contador no se comparte entre tenants ni roles: §31.5.8) |
| Verificación mock | El mock aplica las mismas reglas: header exacto, `typ`, `kid`, `exp`, roles y el 401 `urn:agentcore:problem:credentials_invalid`; rechaza otro `typ`, otro `kid`, header con clave extra y `actor=human` en el bot |
| Verificación real | Bot crea propuesta (201) y es rechazado en `approve` (`forbidden_role`); token staff en `/v1/runs` sin estar en identity ⇒ 401; token identity en `/v1/registry` ⇒ 401; `exp` vencido ⇒ `principal_expired`; rotación completa con `kid` solapado |

#### 31.2.5 CAP-05 — Autenticación interna Pulso

Estos JWT **no** son el JWS de Core (V3 §27.5: el worker nunca manda su JWT interno como JWS Core).

| Dirección | Mecanismo | Claims mínimos |
|---|---|---|
| Rust → bridge (`invoke`, lecturas, dry-run) | JWT de servicio, algoritmo y `kid` fijados por ADR | `iss=control-api`, `aud=core-bridge`, `sub=worker:<id>`, `tenant_id`, `purpose`, `job_id`, `iat`, `exp` ≤ 5 min, `jti` |
| Bridge/exporter → control-api (`core-task-bindings`, `platform/observations`) | JWT de servicio distinto | `iss=core-bridge`, `aud=control-api`, `scope ∈ {binding, observations}`, `tenant_id`, `exp`, `jti` |

Errores: `pulso:service_token_invalid`, `pulso:audience_mismatch`, `pulso:service_token_expired`. Verificación (mock y real): audiencia cruzada, `jti` repetido y token vencido rechazados.

#### 31.2.6 CAP-06 — Identidad de instancia y sonda de conformidad

Core no expone versión por red: `/healthz` devuelve `{"status":"ok"}`, `contracts/openapi.json` declara `info.version=1.0.0` con `contracts/VERSION=1.3.0` y no existe endpoint ni cabecera de SHA. Pulso fija la identidad **por perfil y por sonda**, no por declaración del servidor.

| Elemento | Contrato |
|---|---|
| Identidad | `expected_image_digest` y `expected_sha` en el perfil; con D-1, el runtime es nuestro y publica `GET /internal/v1/version → {agent_core_sha, contracts_version, pulso_sha, image_digest, runtime_profile}` (autenticado) |
| Sonda de conformidad | `GET /healthz`; `GET /readyz`; `POST /v1/runs` sin credencial ⇒ problem+json `urn:agentcore:problem:credentials_invalid`; `GET /v1/registry/proposals/x` sin credencial ⇒ 401 `application/problem+json` `urn:agentcore:problem:credentials_invalid` (observado); `POST /v1/registry/proposals` con credencial bot de prueba ⇒ acepta el cuerpo mínimo. Resultado `conformance_probe_digest` |
| Regla | Cambio de digest o de resultado de sonda exige ADR y contract suite (§27.4), no actualización silenciosa. Ante identidad inconsistente ⇒ `pulso:profile_mode_mismatch` y `real_*` no se declara |

Mock: devuelve `target=mock` y falla la sonda de `real_*` por diseño. Real: sonda contra el nombre interno; el smoke registra la versión observada.

### 31.3 Leer el estado base

Para proponer un cambio Pulso debe conocer la release de partida, sus entidades y el alias vigente **antes** de redactarlo. El registry HTTP no ofrece estas lecturas (H5); estos contratos usan lo que existe y, con D-1, lecturas de sólo lectura expuestas por nuestro bridge sobre las clases públicas del SHA.

#### 31.3.1 CAP-07 — ReadBase — DECISIÓN PROVISIONAL D-8 (adoptada, revisar con equipo agent-core)

`ReadBase(agent_id) → BaseSnapshot{release_id, source, entities:[{kind,id,version,content_hash,content}], knowledge_snapshot, eval_suite_refs, read_at}`; el snapshot se guarda como `ArtifactReference` inmutable.

Fuentes de `release_id` (se registra `source`; prioridad con D-8 = A: 2 `bridge_alias` primero, 1 `receipt` como verificación cruzada y 3 sólo si la propuesta se usará; sin bridge, el orden 1→3):

1. `receipt` — último `release_id` publicado/promovido en `pulso_artifacts(registry_receipt)`, **verificado** con `GET /v1/registry/releases/{rid}` (`status=active`, mismo `agent_id`) y consistente con la fuente 2 cuando exista.
2. `bridge_alias` — `GET /internal/v1/core-state/aliases/{agent_id}/staging` del bridge (CAP-08). Preferida con D-1/D-8 = A (adoptadas provisionalmente).
3. `proposal_probe` — `POST /proposals {origin:"auto_detect"}` y leer `Proposal.base_release_id`; **consume cuota** (10/24 h) y crea una propuesta `draft`: permitido sólo si esa propuesta se va a usar, nunca como sondeo.

Lectura de contenido: `GET /v1/registry/releases/{rid}` → `ReleaseDetail{entities[{ref,content_hash,docs,changed_vs_base}], knowledge_snapshot, base_release_id, eval_suite_refs}`; por cada entidad `GET /v1/registry/entities/{kind}/{id}?version=<exacta>` (el parámetro es obligatorio en Pulso: sin él Core devuelve la última versión). Cada `content` se verifica con CAP-12 contra su `content_hash`.

| Error | Cuándo |
|---|---|
| `pulso:base_unreadable{release_id,step}` | 404/5xx en release o entidad |
| `pulso:base_hash_mismatch{kind,id,version}` | hash local de `content` ≠ `content_hash` devuelto |
| `pulso:base_source_unavailable` | no hay receipt verificable, no hay bridge y la propuesta no se va a crear |
| `registry:not_found`, `registry:forbidden_role` | como llegan |

Mock: misma superficie y el mismo 404 sin `?version=` devolviendo la última. Real: sembrar con CAP-47 y leer.

#### 31.3.2 CAP-08 — Estado de alias — DECISIÓN PROVISIONAL D-8 (adoptada, revisar con equipo agent-core)

| Operación | Cómo | Salida | Fallo |
|---|---|---|---|
| `staging_release(agent)` / `prod_release(agent)` | Bridge `GET /internal/v1/core-state/aliases/{agent_id}/{alias}` implementado con la lectura de sólo lectura del store de Core (`RegistryTx.get_alias`; interfaz exacta sujeta a verificación en el SHA y cubierta por el contract CI de CAP-57) con lectura de sólo lectura del store que ya posee `pulso-core-runtime` (no necesita el rol Postgres del exporter, que es del exporter, CAP-34) | `AliasState{agent_id, alias, release_id, source:"core_store", observed_at}` | `pulso:alias_unknown` |
| Sin bridge (stock `serve`, D-1 no confirmada) | `ObservedAlias{release_id, observed_at, evidence_kind}` con evidencia: último `release_id` de `run.started` del agente en producción, `release.promoted` (+CAP-09 para el agente) o `AliasChange` de la respuesta de promote | Nunca autoritativo | `pulso:alias_unknown` |

Regla: "prod = staging" no se infiere nunca; el receipt conserva baseline staging y prod con `evidence_kind` distinto (§27.2 paso 1). `GET /releases/{rid}` no prueba alias activo. La lectura nativa upstream se solicita en N-02; no se fabrica un `GET /aliases`.

#### 31.3.3 CAP-09 — Resolución release→agente y run→release

`release.*` salientes no traen agente ni alias (`ReleaseData{release_id, proposal_id}`); `run.started` trae `agent{id,version}` y el sobre trae `release_id`. Resolvedor: `GET /v1/registry/releases/{rid}` → `agent_id` (inmutable, se cachea por `release_id`) y `GET /v1/registry/runs/{run_id}/lineage` (rol `constructor`) para run→release. Error: `pulso:release_agent_unresolved` ⇒ `agent=unknown`, excluido de ratios por agente.

#### 31.3.4 CAP-10 — Verificar lo creado

Tabla `core_ref_map(tenant, pulso_artifact_ref, kind, id, version, content_hash, proposal_id, candidate_hash)`: un `ChangeSpec.new_ref` ↔ exactamente un `VersionRef`. Tras `freeze`/`publish`: `GET /releases/{base}/diff/{rid}` debe producir `added ∪ changed` igual a las operaciones autorizadas ∪ `auto_bumped`; cualquier otra entrada ⇒ `pulso:diff_exceeds_change_spec`. La `eval_suite` **no** aparece en el diff de entidades de la release (se guarda como versión y entra en `eval_suite_refs`; *observado*). `lineage` sólo con credencial constructor.

### 31.4 Producir los artefactos que Core acepta

#### 31.4.1 CAP-11 — Schemas wire fijados y derivados

| Campo | Contrato |
|---|---|
| Entrada | Pin `{repo, sha, contract_version}` y árbol upstream en ese SHA, con el entorno Python fijado por el `uv.lock` del SHA |
| Salida | `crates/core/wire/agent_core@<sha7>/` con `schemas/*.json` (copia byte a byte de `contracts/schemas/`, 193 archivos generados por `uv run agentcore contracts`), `events/` (`OutboundEvent.json`, `catalog.json`), `registry_schemas/*.json` (derivados, ver abajo), `fixtures/{valid,invalid}/` y `MANIFEST.json {repo, sha, contract_version, files:[{path, sha256}]}` |
| Precondiciones | Pulso no edita archivos copiados; un cambio de pin es un PR dedicado (CAP-57) |

`contracts/schemas/` **no** contiene `EvalSuite`, `EntityDraft`, `VersionDocs` ni los modelos de respuesta del registry (`Proposal`, `ValidationReport`, `CandidateView`, `ReleaseDetail`, `EntityVersion`, `ReleaseDiff`, `EvalReport`, `ProposalDetail`): `contracts.py::_collect` sólo exporta `agent_core.domain` y `agent_core.ports`, y `contracts/openapi.json` no incluye `/v1/registry`. Pulso los **deriva** con `TypeAdapter(Model).json_schema(mode="validation", by_alias=True)` sobre `agent_core.registry.models`/`.suite`/`.service`, ejecutado en el entorno pineado (job de CI o `core-bridge`), con el orden determinista y el `$comment` de `contracts.py::_encode`; se guardan marcados `derived_by_pulso=true`. Si agent-core atiende N-01, el MANIFEST pasa a copiarlos y la generación local se elimina por cambio de pin, no en silencio.

| Error | Cuándo |
|---|---|
| `pulso:wire_drift{file,expected_sha256,actual_sha256}` | MANIFEST ≠ árbol regenerado |
| `pulso:wire_schema_missing{type}` | tipo sin schema fijado ni derivado |
| `pulso:pin_mismatch` | identidad de instancia (CAP-06) ≠ MANIFEST |

Verificación: fixtures válidos/inválidos decodificados con el validador Python del SHA y con el decodificador Rust dan el mismo resultado (mock/a); `agentcore contracts --check` contra el checkout que corre el runtime (real). El job `wire-drift` es de CAP-57.

#### 31.4.2 CAP-12 — Serialización canónica y `content_hash`

Función normativa `core_content_bytes(kind, value)`:

1. Decodificar `value` con el DTO del kind (`agent_core_wire`) con **los mismos defaults** que el modelo pydantic.
2. Volcar con **todos** los campos con default y `null`, alias de cable (`await`, no `await_`) y referencias como `{id, spec}`.
3. JCS (RFC 8785) con las reglas de `domain/json.py::canonical_bytes`: `Decimal` con escala ⇒ string; `Decimal` entero ⇒ entero; `int` fuera de ±(2^53−1) ⇒ string.

`content_hash = sha256_hex(core_content_bytes)`. Prohibido: `serde_json::Value` con claves ordenadas como sustituto de JCS (el comparador de U17 debe migrar), `exclude_none`, redondear `Decimal`, y emitir refs como `"id@spec"` aunque Core las acepte al leer.

Observado: el hash sobre el volcado completo de `disputa-cargo@1.0.0` es `6b5b579464f54370…`, y sobre el volcado `exclude_none` (forma de los YAML) `5876e2f42fca…`. El servidor re-parsea y re-serializa lo enviado (`candidate._parse_drafts`), de modo que el hash no es el de los bytes recibidos sino el del modelo normalizado, y `GET proposal` devuelve `changes[].content` **tal como se envió**, no normalizado: no es fuente de verdad del hash. Pulso envía siempre la forma normalizada. Se pide a agent-core confirmar la equivalencia de formas (N-05).

| Error | Cuándo |
|---|---|
| `pulso:content_not_canonical{kind,id,pointer}` | campo no representable (Core rechaza `Decimal` no finito o con |exponente| > 1000, `domain/json.py::_check_decimal`; un float finito se acepta; un `Decimal` con exponente ≥ 0 se canoniza como entero, `1E+2`→`100`; el comparador Rust aplica la misma regla) |
| `pulso:content_hash_mismatch{expected,actual}` | hash local ≠ hash de `GET entities` o `ReleaseDetail` |

Prueba dorada: para cada fixture de `registry-demo`, hash Rust == `content_hash` de `GET entities/{kind}/{id}?version=` tras CAP-47 (real) == `registry.entities.content_hash` (a2).

#### 31.4.3 CAP-13 — `ChangeSpec` a `changes[]`

Entrada: `ChangeSpec` autorizado + `BaseSnapshot` (CAP-07). Salida: `DraftPlan{changes:[{kind, content, docs}], expected_derived:[VersionRef], blocked:[…]}` con la lista **completa y ordenada** `(kind,id,version)`; cada `PUT …/draft` reemplaza todo, nunca es patch (§27.2 paso 3).

| Operación Pulso | Traducción exacta | Precondición | Si no cabe |
|---|---|---|---|
| `add` | un `change` con `version` inicial; además un `change` del consumidor que la **referencia** (flow o agent que la cita) | `(kind,id)` ausente en la base | sin consumidor ⇒ `pulso:compile_violation{rule:"REG-UNREFERENCED"}` previo al PUT |
| `replace` | un único `change` por `(kind,id)` con el `content` completo y `version` mayor que la de base; sin parches | `content_hash` de base == `precondition_digest` | `pulso:precondition_mismatch` |
| `disable` | nuevo `change` del **consumidor** sin la referencia/ruta; ninguna operación sobre la entidad deshabilitada, que permanece en el registry | consumidores calculados sobre la base y regresión planeada | `dependency_blocked(disable_not_expressible)` |

Reglas: una entidad de base no incluida en el draft **permanece** (no existe borrado); ≤ 50 `changes` por PUT (la suite cuenta); un kind fuera de §31.4.4 ⇒ `unsupported_capability`; `docs` según CAP-18. Pruebas: caso dorado de §31.4.12; negativos: entidad añadida sin consumidor, `replace` con digest viejo, `disable` de una tool que consume otro flow del paquete.

#### 31.4.4 CAP-14 y CAP-23 — Kinds producibles y alcance de la release — DECISIÓN PROVISIONAL D-10 (adoptada, revisar con equipo agent-core)

| Kind | Primer corte | Observación |
|---|---|---|
| `flow` | sí (`add`/`replace`) | unión discriminada upstream; `subflow` y `await_approval` fuera |
| `template` | sí | `locales` ⊇ locales del agente (G0-12) |
| `policy` | sí | JSON Logic del subconjunto Core; `owner` y `rationale` obligatorios |
| `prompt` | sí, con `model_profile` existente | sin `{{ }}` |
| `decision_model` | sí, sin cambiar calibración | `calibrated_fields`/`thresholds_from` heredados |
| `eval_suite` | sí | CAP-21 |
| `agent` | por cascada o `replace` de campos autorizados (p. ej. `tools_allowed`) | `accepts`/`routing` no se emiten |
| `model_profile` | no | precios y alias son de plataforma: `unsupported_capability` |
| `tool` | no | sin executor ⇒ `dependency_blocked(tool_without_executor)`; `executor_ref` **no existe** en Core |
| `language_detection`, `injection_ruleset` | no | protegidas; sólo heredadas |
| `knowledge_snapshot` | no | `REG-KNOWLEDGE` |

`CoreEntityKind` de U17 debe ampliarse a `Policy` y `EvalSuite`. **`ReleaseDecl` y `Release` no se autoran por la vía registry:** `candidate._decl` las deriva de la base (interrupciones, detección de idioma, ruleset, `max_input_chars` heredados y re-apuntados, `aliases:["staging"]`, todos los flows del merge) y `publish` produce la `Release`. CAP-23 (cambiar interrupciones, idioma, ruleset o `max_input_chars` por propuesta) está `dependency_blocked(release_level_change)` por N-07; sólo un humano puede editarlos por una vía de agent-core. Crear un agente nuevo (base `null`: `interrupts=[]`, `max_input_chars=4000`, `REG-PIN` si falta `language_detection`, sin vara previa) queda fuera del primer corte salvo decisión D-10.

#### 31.4.5 CAP-15 — Versionado y cascada

1. Versión de una entidad editada: patch+1 si el cambio es compatible en wire; minor si agrega nodos o ramas; major sólo con cambio de contrato de entrada/salida. Debe ser `> base` (`REG-VERSION`) y no estar publicada con otro contenido (`REG-VERSION-TAKEN`). La política es de Pulso; la regla de validez es de Core.
2. Cascada: toda entidad almacenada referencia con versión exacta, por lo que **todo consumidor transitivo no editado** de una entidad editada recibe patch+1 al primer patch no publicado (`candidate._cascade`, punto fijo). El compiler calcula `expected_derived` con el mismo punto fijo sobre el grafo de referencias de la base.
3. Tras `validate`/`freeze`: `auto_bumped` observado == `expected_derived`; si añade entidades fuera del bridge ⇒ `pulso:cascade_scope_exceeded` (reabrir/detener); si sólo difiere la versión ⇒ `pulso:cascade_mismatch`.

Observado: editar `disputa-cargo` a `1.1.0` deriva `atencion@1.0.0 → 1.0.1` sin que el draft lo declare, con `docs` autogenerados ("Versión derivada de atencion").

#### 31.4.6 CAP-16 — Validar antes del round-trip — DECISIÓN PROVISIONAL D-9 (adoptada, revisar con equipo agent-core)

Decisión (justificada y verificada; D-9 = DECISIÓN PROVISIONAL adoptada, revisar con equipo agent-core): reimplementar `G0-*`/`AG-*`/`MT-*` en Rust (~25 reglas en `flows/rules/*.py`) duplicaría la fuente de verdad; delegar siempre a `POST …/validate` obliga a un round-trip por iteración. Tres capas:

| Capa | Dónde | Qué hace | Autoritativa |
|---|---|---|---|
| L1 prefiltro | Rust (compiler) | sólo reglas independientes de otras entidades y de la base (tabla siguiente) | no |
| L2 dry-run | bridge (D-1, D-9) `POST /internal/v1/core-authoring/dry-run` | ejecuta `build_candidate` + `validate_candidate` del SHA sobre base (CAP-07) + `DraftPlan`, **sin crear propuesta ni gastar cuota**; devuelve `{violations, candidate_hash, release_id_preview, auto_bumped, new_versions, content_hashes}` | paridad: usa el mismo código que `freeze` |
| L3 | registry HTTP | `POST …/validate` (200 con `violations`, sin cambio de estado) y `freeze` | sí |

L1 (obligatorio local): forma por schema fijado sin campos extra (`REG-SCHEMA`); límites ≤50 changes, ≤262144 bytes canónicos por entidad y ≤200 nodos por flow (`REG-LIMIT`); `version` exacta y `> base` (`REG-VERSION`); id único por `(kind,id)`, kind permitido, sin `knowledge_snapshot` (`REG-DUPLICATE`, `REG-KIND`, `REG-KNOWLEDGE`); cada entidad nueva con consumidor (`REG-UNREFERENCED`); template/prompt cubre `supported_locales` del agente (`G0-12`); `next` de cada nodo apunta a nodos existentes (`G0-03`); métricas/umbrales `platform_*` no editados (`forbidden_role` en PUT).

Sin bridge (D-1 no confirmada): L1 + L3; cada iteración cuesta un PUT+validate dentro de **una** propuesta (validate no consume cuota; create sí). Las violaciones se conservan tal cual `{rule, path, flow, node_id, message}` y se mapean a `pulso:compile_violation{rule, entity, pointer}`; **HTTP 200 con `violations` no vacío no es éxito**. Observado: un template sin locale `pt` falla `G0-12` sólo en `validate_candidate`, no en el schema de `Template`.

Errores: `pulso:compile_violation`, `pulso:dry_run_unavailable`. Verificación: cada fila de L1 con un negativo; paridad Rust-vs-Python sobre las mismas fixtures inválidas; en real, `dry-run.candidate_hash == freeze.candidate_hash`.

#### 31.4.7 CAP-17 — Clausura y `candidate_hash`

Fórmulas del SHA: `release_hash = sha256(JCS(release.model_dump(mode="json", exclude={"id","status"})))`; `candidate_hash = sha256(JCS({"release_hash": r, "versions": sorted([[str(ref), content_hash], …])}))` (incluye suites del draft; **no** `docs`); `release_id_preview = "rel-" + candidate_hash[:16]`.

`GET /releases/{rid}` no devuelve `interrupts`, `language_detection`, `injection_ruleset` ni `max_input_chars`, así que Rust no puede reconstruir `release_hash`. Alcance: Rust calcula el conjunto de refs de la clausura y el `content_hash` por entidad (CAP-12); el `candidate_hash` lo calcula el dry-run del bridge con el código del SHA y se compara con el de `freeze`. Sin bridge: `pulso:candidate_hash_unverifiable` (informativo, no bloquea); el hash de `freeze` es autoritativo. Errores: `pulso:closure_mismatch{missing,extra}`, `pulso:candidate_hash_mismatch` (bloquea), `registry:candidate_changed`. Con N-03 la paridad pasaría a ser local.

#### 31.4.8 CAP-18 — `docs`

`docs = {description 1..4000, rationale ≤4000, changelog ≤8000}` por change. Contenido: qué cambia, `opportunity_ref`/`change_spec_ref` por id (no texto de evidencia), sin PII, sin `final_locked`, sin credenciales (se almacenan en la versión y los lee cualquier builder). No participa de `content_hash` ni de `candidate_hash`; los `docs` de las derivadas los genera Core y no se envían. Error: `pulso:docs_policy_violation{field}`. Prueba: escáner de PII/canario sobre `docs`, `changes` y `GET proposal`.

#### 31.4.9 CAP-19 — Límites y cuotas como precondición

`len(changes) ≤ 50` (la suite cuenta; las derivadas por cascada no); `core_content_bytes ≤ 262144`; `len(flow.nodes) ≤ 200`. Reserva de cuota `auto_detect` antes de crear: 10 propuestas por ventana móvil de 24 h y 20 evaluaciones por propuesta (H10); `registry:quota_exceeded` no se reintenta. Un draft fallido por cuota no destruye la propuesta. Error: `pulso:limit_exceeded{limit,value}`. Con composición propia (D-1) Pulso fija sus `Quotas`; con `serve` stock sólo observa los defaults.

#### 31.4.10 CAP-20 — Precondición de base

El registry **no** valida precondiciones por entidad: sólo `put_draft` hace CAS por `expected_rev` y `publish` devuelve `proposal_stale` si `staging` se movió. El `precondition_digest` es el `content_hash` de `EntityInRelease`/`EntityVersion` (CAP-12). La atomicidad "precondición + PUT" no existe en Core: se cierra con doble lectura (releer `ReleaseDetail` antes del PUT y tras `freeze`) y `proposal_stale`. Errores: `pulso:precondition_mismatch`, `registry:proposal_stale` (rebase).

#### 31.4.11 CAP-21 y CAP-22 — `eval_suite` y sandbox de respuestas

**CAP-21 — `ScenarioCase` → `Scenario`.** Salida: `change{kind:"eval_suite", content:EvalSuite, docs}`.

| `ScenarioCase` (Pulso) | `Scenario` (Core) |
|---|---|
| id estable | `id` `^[a-z0-9][a-z0-9_-]*$`, único en la suite; 1..200 escenarios |
| principal sintético | `principal{id, attrs{str→str}}` sin PII real; el harness lo ejecuta como `customer` |
| turnos | `steps[]` (1..50): único `start` inicial; `turn{text≤4000, lang?}`; `confirm{answer:yes\|no}`; `auth` fijado siempre explícito (el default de Core es `step_up`) |
| estado de tools | `seed.tools{tool_id:[ToolReply{status,result,error}]}`; sólo tools de `tools_allowed` |
| oracle ejecutable | `expect{outcome?, actions_verified[], escalated?}`; `assertions[]` ≤ 20 sobre eventos del catálogo; Pulso exige `expect` no vacío (más estricto que Core) |
| valores sensibles de prueba | `sensitive_values[]` (suman a `platform_pii_leak`) |
| fuente `dataset` | no (`dataset_source_disabled`): `not_evaluable_native`, oracle Pulso |

`repetitions` 1..10. `thresholds`: una entrada por **cada** métrica `gate`/`guardrail` de `Agent.metrics` (`missing_threshold` en otro caso), ninguna `platform_*`, y ningún umbral para métrica no declarada (`unknown_threshold_metric`); `MetricThreshold{noise_margin ≥ 0, floor?}`, `floor` obligatorio si la métrica es nueva o cambió. Un agente sin suite resoluble (ni en el draft ni publicada) ⇒ `missing_suite` **al evaluar** (`validate` y `freeze` no la exigen). La suite viaja en el draft como `EntityDraft{kind:"eval_suite"}`, cuenta contra los 50 changes y 262144 B, altera el `candidate_hash` y no entra en la release (queda en `eval_suite_refs`); versión nueva si cambia un byte (`REG-VERSION-TAKEN` si se reutiliza `id@version`). `evaluate` nombra `suite_id` + `suite_version` exacta (nunca latest). La suite es legible por cualquier builder: prohibido subir casos `final_locked` (§27.2 paso 7). `registry-demo` no trae `eval_suites/`: la primera propuesta del mundo demo debe incluir su suite y esa suite pasa a ser la "vara anterior" de la siguiente (`eval_suite_refs`).

Errores: `registry:validation_failed` con `REG-SUITE` + `SuiteProblemCode` (`missing_suite`, `agent_mismatch`, `duplicate_scenario`, `dataset_source_disabled`, `unknown_assertion_event`, `invalid_assertion_filter`, `missing_threshold`, `unknown_threshold_metric`); `registry:forbidden_role` al tocar `platform_*`; `pulso:scenario_not_expressible{case_id,reason}`; `pulso:final_locked_leak`. Verificación: mock con las mismas reglas desde el schema del SHA; real: `validate` + `evaluate` con una suite negativa por cada código; canario `final_locked` ausente en `changes`, `docs` y `GET proposal`.

**CAP-22 — Respuestas de tools deterministas.** El sandbox de Core es `LocalSandbox`: cola FIFO por `tool_id` (se consume con `popleft()` si hay >1 respuesta, la última se repite), `error "sin respuesta sembrada"` si falta, idempotencia por `(tool, key)`, sin matching por argumentos ni estado. Por tanto el compiler (1) emite `seed.tools` desde una **traza de referencia** calculada con el banco sandbox de Pulso (U26) ejecutando el guion con respuestas deterministas; (2) verifica que el orden de llamadas del candidato sea compatible con la cola (si no, genera una cola por rama o `pulso:queue_order_sensitive`); (3) valida cobertura: toda tool de `tools_allowed` referida por un escenario tiene respuesta sembrada (`pulso:suite_missing_seed`); (4) marca `not_evaluable_native` el escenario que dependa de argumentos o estado intermedio y lo evalúa sólo en la campaña Pulso. Dos brazos con el mismo seed no comparten cola (instancias de sandbox distintas). El banco stateful dentro del gate nativo es CAP-41.

#### 31.4.12 Ejemplo trabajado: `disputa-cargo@1.0.0` a `1.1.0` en `atencion`

Mundo: semilla `tests/fixtures/registry-demo` importada (CAP-47; agente `atencion@1.0.0`, entry flow `disputa-cargo@1.0.0`, 19 nodos). Los valores marcados *observado* salen del SHA ejecutado en memoria (§31.1); los identificadores de propuesta y las marcas de tiempo son ilustrativos (en memoria `FakeIds` produce `proposal-0001`).

**Oportunidad y `ChangeSpec` (ilustrativos).** Tras la regla `umbral` (monto USD sobre el umbral) el flow escala a `esc_monto` sin avisar al cliente.

```
operations:
  - {op: add,     target_kind: template, new_ref: t/aviso_monto@1.0.0, precondition: EntityAbsent}
  - {op: replace, target_kind: flow, target_ref: disputa-cargo@1.0.0, new_ref: disputa-cargo@1.1.0,
     precondition_digest: 6b5b579464f54370d2eed81b5c1a460c6a3ab270c0c8244fe17ed0a80d953b11}
  - {op: add,     target_kind: eval_suite, new_ref: disputas-suite@1.0.0, precondition: EntityAbsent}
expected_mechanism: avisar antes de escalar por monto
affected_routes: [disputa-cargo]     rollback_ref: rel-98130317a1003849
```

El `precondition_digest` es el `content_hash` completo de `disputa-cargo@1.0.0` leído con `GET /v1/registry/entities/flow/disputa-cargo?version=1.0.0` y verificado con CAP-12. `rel-98130317a1003849` es la base importada (*observado*; determinista a partir del hash de la release).

**`DraftPlan`.** `changes = [flow disputa-cargo 1.1.0, template t/aviso_monto 1.0.0, eval_suite disputas-suite 1.0.0]`; `expected_derived = [agent atencion@1.0.1]`.

**1. Crear la propuesta** (`POST /v1/registry/proposals`, `Authorization: Bearer <JWS bot>`; 201; persistir antes de avanzar):

```json
{"agent_id":"atencion","origin":"auto_detect","title":"Avisar antes de escalar por monto"}
→ {"proposal_id":"proposal-0001","agent_id":"atencion","origin":"auto_detect","state":"draft","rev":0,
   "base_release_id":"rel-98130317a1003849","title":"Avisar antes de escalar por monto",
   "created_by":"constructor-bot","candidate_hash":null,"updated_at":"…"}
```

Si `base_release_id` es `null`, el agente no está sembrado: `dependency_blocked(agent_not_seeded)`.

**2. `PUT /v1/registry/proposals/proposal-0001/draft`** con `expected_rev: 0` y la lista completa. Forma **normalizada** (CAP-12). Los 19 nodos de `disputa-cargo@1.0.0` son los devueltos por `GET entities/flow/disputa-cargo?version=1.0.0`; sólo cambian `umbral.next.true` y el nodo nuevo `aviso_monto`:

```json
{"expected_rev":0,"changes":[
 {"kind":"flow","docs":{"description":"umbral.true pasa por aviso_monto antes de escalar","rationale":"opp-demo-1","changelog":"umbral.true → aviso_monto → esc_monto"},
  "content":{"id":"disputa-cargo","version":"1.1.0","priority":50,"nodes":[
   {"id":"pedir_cargo","next":{"ok":"buscar_tx","max_attempts":"esc_sin_datos"},"type":"collect","config":{"slot":"descripcion_cargo","prompt_ref":{"id":"t/pedir_cargo","spec":"1.0.0"},"validator":null,"max_attempts":2}},
   {"id":"buscar_tx","next":{"ok":"coincide","error":"esc_tool","timeout":"esc_tool","denied":"esc_tool"},"type":"tool","config":{"tool":{"id":"buscar_transacciones","spec":"1.0.0"},"args":{"texto":"slots.descripcion_cargo"},"save_as":"candidatas","step_up_max_attempts":2}},
   {"id":"coincide","next":{"unica":"elegir","ninguna":"aclarar","varias":"aclarar","low_confidence":"aclarar"},"type":"decide","config":{"model":{"id":"match-cargo","spec":"2.0.0"},"input_view":null,"branch_on":"match","save_as":"coincide","choices_from":null}},
   {"id":"elegir","next":{"ok":"a_usd","error":"esc_tool","timeout":"esc_tool","denied":"esc_tool"},"type":"tool","config":{"tool":{"id":"seleccionar","spec":"1.0.0"},"args":{"lista":"facts.candidatas.value","id":"decisions.coincide.transaction"},"save_as":"transaccion_elegida","step_up_max_attempts":2}},
   {"id":"a_usd","next":{"ok":"umbral","error":"esc_tool","timeout":"esc_tool","denied":"esc_tool"},"type":"tool","config":{"tool":{"id":"convertir_moneda","spec":"1.0.0"},"args":{"monto":"facts.transaccion_elegida.value.amount","moneda":"facts.transaccion_elegida.value.currency","destino":"USD"},"save_as":"monto_usd","step_up_max_attempts":2}},
   {"id":"umbral","next":{"true":"aviso_monto","false":"confirmar"},"type":"rule","config":{"policy":{"id":"escalamiento-disputa-monto","spec":"1.0.0"},"expr":null}},
   {"id":"confirmar","next":{"yes":"radicar","no":"fin_cancelado","unclear":"confirmar","max_attempts":"no_confirmado"},"type":"confirm","config":{"action":{"tool":{"id":"radicar_pqr","spec":"1.0.0"},"args":{"transaction_id":"facts.transaccion_elegida.value.transaction_id","descripcion":"slots.descripcion_cargo"}},"summary_template":{"id":"t/resumen_pqr","spec":"1.0.0"},"reprompt_template":null,"max_attempts":2}},
   {"id":"radicar","next":{"ok":"verificar","uncertain":"verificar","denied":"esc_tool"},"type":"tool","config":{"action_from":"confirmar","draft":false,"tool":null,"args":{},"save_as":"pqr","step_up_max_attempts":2}},
   {"id":"verificar","next":{"verified":"responder_ok","failed":"esc_verif"},"type":"verify","config":{"readback":{"id":"obtener_pqr","spec":"1.0.0"},"by":"idempotency_key","predicate":{"==":[{"var":"readback.status"},"Open"]},"save_as":"pqr_verificada"}},
   {"id":"responder_ok","next":{"next":"fin"},"type":"respond","config":{"template_ref":null,"generate":{"prompt_ref":{"id":"p/resumen_radicado","spec":"1.0.0"},"allowed_facts":["facts.pqr_verificada"],"knowledge_from":[],"purpose":"customer_answer","fallback_template_ref":{"id":"t/pqr_radicado","spec":"1.0.0"}},"await":false,"claims":["confirmar"]}},
   {"id":"fin","next":{},"type":"end","config":{"outcome":"resolved","output_map":null}},
   {"id":"aclarar","next":{"next":"pedir_cargo"},"type":"respond","config":{"template_ref":{"id":"t/aclarar_cargo","spec":"1.0.0"},"generate":null,"await":true,"claims":[]}},
   {"id":"no_confirmado","next":{"next":"fin_abstenido"},"type":"respond","config":{"template_ref":{"id":"t/no_confirmado","spec":"1.0.0"},"generate":null,"await":false,"claims":[]}},
   {"id":"fin_abstenido","next":{},"type":"end","config":{"outcome":"abstained","output_map":null}},
   {"id":"fin_cancelado","next":{},"type":"end","config":{"outcome":"cancelled","output_map":null}},
   {"id":"esc_sin_datos","next":{},"type":"escalate","config":{"reason_code":"low_confidence","target_queue":null,"priority_expr":null}},
   {"id":"esc_tool","next":{},"type":"escalate","config":{"reason_code":"tool_failure","target_queue":null,"priority_expr":null}},
   {"id":"esc_monto","next":{},"type":"escalate","config":{"reason_code":"policy:escalamiento-disputa-monto","target_queue":"disputas","priority_expr":null}},
   {"id":"esc_verif","next":{},"type":"escalate","config":{"reason_code":"verification_failed","target_queue":null,"priority_expr":null}},
   {"id":"aviso_monto","next":{"next":"esc_monto"},"type":"respond","config":{"template_ref":{"id":"t/aviso_monto","spec":"1.0.0"},"generate":null,"await":false,"claims":[]}}]}},
 {"kind":"template","docs":{"description":"Aviso es/pt previo a escalamiento por monto","rationale":"opp-demo-1","changelog":"Nuevo template"},
  "content":{"id":"t/aviso_monto","version":"1.0.0","locales":{"es":"Por el monto, un especialista revisará tu disputa.","pt":"Pelo valor, um especialista vai revisar sua contestação."},"reads":[]}},
 {"kind":"eval_suite","docs":{"description":"Suite baseline de disputas","rationale":"suite del mundo demo","changelog":"Versión inicial"},
  "content":{"id":"disputas-suite","version":"1.0.0","agent_id":"atencion","repetitions":1,"thresholds":{},"scenarios":[
   {"id":"resuelto","source":"scripted","principal":{"id":"cust-001","attrs":{"country":"CO"}},
    "steps":[{"op":"start","text":null,"answer":null,"lang":null,"auth":"step_up"},
             {"op":"turn","text":"no reconozco un cargo de ciento veinte dólares","answer":null,"lang":null,"auth":"step_up"},
             {"op":"confirm","text":null,"answer":"yes","lang":null,"auth":"step_up"}],
    "seed":{"tools":{"buscar_transacciones":[{"status":"ok","result":[{"transaction_id":"tx-1","amount":"120.50","currency":"USD"},{"transaction_id":"tx-2","amount":"30.00","currency":"USD"}],"error":null}],
                     "seleccionar":[{"status":"ok","result":{"transaction_id":"tx-1","amount":"120.50","currency":"USD"},"error":null}],
                     "convertir_moneda":[{"status":"ok","result":"120.50","error":null}],
                     "radicar_pqr":[{"status":"ok","result":{"status":"Open","id":"pqr-demo-1"},"error":null}],
                     "obtener_pqr":[{"status":"ok","result":{"status":"Open","id":"pqr-demo-1"},"error":null}]}},
    "sensitive_values":[],"expect":{"outcome":"resolved","actions_verified":["radicar_pqr"],"escalated":false},
    "assertions":[],"repetitions":null}]}}]}
→ Proposal{state:"draft", rev:1, candidate_hash:null, …}
```

El agente `atencion` del demo no declara `metrics`: no hay umbrales que exigir; los cuatro guardarraíles `platform_*` se miden igual (§31.7.1).

**3. `POST …/validate`** (200; *observado*): `{"violations":[],"candidate_hash":"a6d50a8f209a5eccf12fd3e96fecb50dceec01123bb2004e729b3a8e78304c8e","auto_bumped":[{"kind":"agent","id":"atencion","version":"1.0.1"}]}`.

**4. `POST …/freeze`** (*observado*): `{"proposal_id":"proposal-0001","candidate_hash":"a6d50a8f…8e","release_id_preview":"rel-a6d50a8f209a5ecc","new_versions":[agent atencion@1.0.1, eval_suite disputas-suite@1.0.0, flow disputa-cargo@1.1.0, template t/aviso_monto@1.0.0],"auto_bumped":[agent atencion@1.0.1]}`. `new_versions` lista sólo lo que aún no está publicado (la base ya lo está). El `release_id_preview` es la clave de correlación del cierre del ciclo (CAP-37). Hashes de contenido observados: `flow 1.1.0 = c66fb4f5f8657fac…`, `template = a47b3653edb2…`, `agent 1.0.1 = d020772da7d59bac…`, `suite = 13a1031b0f08…`. Sin la suite en el draft el `candidate_hash` sería `32acfde12e92299d…` (la suite altera el hash; los `docs` no).

**5. `POST …/evaluate`** con `{"suite_id":"disputas-suite","suite_version":"1.0.0"}` (síncrono; *observado* con el harness demo y el escenario `resuelto`): `{"verdict":"pass","items":[{"metric_id":"scenario/resuelto","phase":"new_yardstick","role":null,"value":null,"base_value":null,"noise_margin":null,"floor":null,"passed":true,"reason":""},{"metric_id":"platform_pii_leak","phase":"platform","role":"guardrail","value":0,"base_value":null,"floor":0,"passed":true,…},{"metric_id":"platform_unverified_success_claim",…},{"metric_id":"platform_unverified_write",…},{"metric_id":"platform_unapproved_knowledge_citation",…}],"runs":{"base_on_old":null,"cand_on_old":null,"cand_on_new":{"status":"ok","metrics":{…:0},"scenarios":{"resuelto":true}}},"results":[…],"judge_notes":[],"yardstick_changes":[],"detail":null}`. `base_value` es `null` porque la base no tiene suite (no hay vara anterior): **el `pass` no prueba mejora**. `GET proposal` devuelve `state:"evaluated"`, `last_eval{eval_run_id, proposal_id, candidate_hash, base_release_id, suite, verdict, report, at}` y `review{functional_changes, suite, suite_changes, gate, yardstick_loosened:[]}`. Los guardarraíles son cuatro (`platform_pii_leak`, `platform_unverified_success_claim`, `platform_unverified_write`, `platform_unapproved_knowledge_citation`).

**6. Aprobación y publicación** (humano, CAP-43/45): `POST …/approve {"candidate_hash":"a6d50a8f…8e","accept_yardstick_loosened":false}` → `Approval{decision:"approved", actor:"ana", yardstick_loosened:[]}`; `POST …/publish` con `Idempotency-Key: pulso:proposal-0001:a6d50a8f…8e:publish` → `ReleaseDetail{release_id:"rel-a6d50a8f209a5ecc", status:"active", agent_id:"atencion", …}`; repetir con la misma clave devuelve la misma release (*observado*). `POST /v1/registry/aliases/atencion/prod {"release_id":"rel-a6d50a8f209a5ecc","reason":"dec-91"}` → `AliasChange{before:"rel-98130317a1003849", after:"rel-a6d50a8f209a5ecc"}`: publicar mueve **staging**, no prod.

**7. Verificación** (CAP-10): `GET /releases/rel-98130317a1003849/diff/rel-a6d50a8f209a5ecc` → `added=[template t/aviso_monto@1.0.0]`, `changed=[agent atencion 1.0.0→1.0.1, flow disputa-cargo 1.0.0→1.1.0]`, `removed=[]` (*observado*): igual a las operaciones autorizadas ∪ `auto_bumped`, sin la suite.

**Negativos observados** (cada uno es un caso de la suite dorada): (a) sólo el template, sin flow que lo cite ⇒ `REG-UNREFERENCED`; (b) flow con `version` `1.0.0` ⇒ `REG-VERSION: debe ser mayor que la vigente 1.0.0`; (c) campo extra `foo` ⇒ `REG-SCHEMA … Extra inputs are not permitted`; (d) template sólo `es` ⇒ `G0-12 … no tiene los locales pt del agente atencion@1.0.1`.

**Criterios de aceptación.** El mismo script corre contra mock (a), a2 y real (b) con los mismos cuerpos; cada paso persiste un `registry_receipt` con `request_digest` antes del siguiente; el hash local de cada entidad coincide con el de Core; `candidate_hash` de dry-run == `freeze`; el segundo publish con la misma clave no crea otra release; una corrida real sin agente sembrado termina en `dependency_blocked`, no en éxito.

### 31.5 Ejecutar tasks y leer sus resultados (core-bridge)

#### 31.5.0 Topología: un solo proceso Python propio — DECISIÓN PROVISIONAL D-1 (adoptada, revisar con equipo agent-core)

V3 decía a la vez que el adaptador Rust habla con `/v1/registry` y `/v1/runs` de `agentcore serve` (§27.1) y que habla con un `core-bridge` que "compone Core in-process" (§29.8, §29.3). Son compatibles sólo si se decide cuántos procesos Python existen y quién compone qué. Opciones:

| Opción | Descripción | Resultado verificado |
|---|---|---|
| S1+S2 | `agentcore serve` stock (con nuestras fábricas) más un `core-bridge` aparte con acceso a la misma base | La CLI no acepta extensiones, `limits` ni sustituir el `RegistryPort`; el pin por `release_id`, el binding previo y la inyección de `Quotas`/sandbox son inalcanzables; leer facts exige acceso SQL externo |
| **S3 (recomendada)** | Un único proceso `pulso-core-runtime`: compone las piezas públicas de Core (`resolve_ports`, `build_api_deps`, `RegistryService`, `registry_extension`, `create_app`) con extensiones propias `/internal/v1/*` | Cubre todas las capacidades de §31.5; Rust nunca importa Python ni lee Postgres de Core |
| S4 | Cliente HTTP puro de `serve` (sin bridge) | Imposible para tasks: el `run_id` sólo se conoce al terminar el run (H4), la salida de un nodo `agent` no es recuperable por HTTP y no hay pin por release |

**Recomendación S3.** Rust es cliente HTTP de **una** URL: `/v1/registry` y `/v1/runs` son las rutas de Core montadas en nuestro proceso (credenciales staff e identity), `/internal/v1/*` son las rutas Pulso (JWT de servicio, §31.2.5). Con D-1 = A (adoptada provisionalmente) todas las rebanadas, incluida la primera (propuesta gobernada, §31.11.4/CAP-61, que exige dry-run y `candidate_hash` de freeze, CAP-16 L2), corren sobre `pulso-core-runtime`; `agentcore serve --registry-api` stock con nuestras siete fábricas queda sólo como **degradación documentada** (§31.5.1) y no sirve para CAP-61. Costo de S3: acoplamiento a ~5 funciones de composición de Core (N-06) mitigado por el contract CI que arranca la app en cada cambio de pin (CAP-57). Si el dueño elige otra opción, CAP-26/27/28/30/31/16(L2)/08 degradan como indica el párrafo de degradación de §31.5.1. Equivalencia con `DECISIONES_ABIERTAS_V3_AGENT_CORE.md`: S3 = opción A, S1+S2 = opción B, S4 = opción C (en este texto "S3" y "D-1 = A" nombran la misma opción).

#### 31.5.1 CAP-24 — Componer y arrancar `pulso-core-runtime` — DECISIONES PROVISIONALES D-2 y D-3 (adoptadas, revisar con equipo agent-core)

| Campo | Contrato |
|---|---|
| Entrada | Entrypoint `pulso_core_runtime.main` en `core-bridge/`. Pasos: (1) `resolve_ports(args, env, clock, ids, tracer)` con `args` sintetizado que apunta las siete fábricas a `pulso_core_runtime.factories:*` (nunca bajo `testing.`), `--identity-keys`, `--staff-keys`, `--registry-api`, `--eval-dsn`; (2) `dataclasses.replace(ports, registry=PinnedRegistryPort(ports.registry))`; (3) `RegistryService` propio (nuestras `Quotas`, evaluador `ScenarioEvaluator(harness, sandbox, max_workers=1)`, `runs=UowRunReleases`); (4) `build_api_deps(ports, registry_service=…)` y `dataclasses.replace(deps, limits=RateLimitConfig(…), extensions=(*deps.extensions, pulso_internal_extension), readiness=(*deps.readiness, …))`; (5) `create_app` y `uvicorn.run(..., log_config=None, access_log=False)` como upstream |
| Salida | Proceso con `/healthz`, `/readyz`, `/v1/runs*`, `/v1/registry/*` de Core y `/internal/v1/*` de Pulso |
| Precondiciones | `AGENTCORE_ALLOW_DEMO` ausente en todo perfil que se reporte `agent_core_real`; `agentcore migrate` aplicado (`--dsn`, `--eval-dsn` distinto, `--app-role` de mínimos permisos); archivos `--identity-keys` y `--staff-keys`; secretos §31.11.6 |
| Errores tipados | `pulso:runtime_config_invalid` (exit 2, nombra la pieza y nunca valores), `pulso:adapter_missing`, `pulso:demo_double_in_real_mode` |
| Verificación mock | Los puertos son fakes Pulso con las firmas de `ports/tools.py` y `ports/authz.py`; no se declara pass de Core |
| Verificación real | Omitir cada flag ⇒ exit 2 con `falta <pieza>`; ruta `testing.*` ⇒ rechazada; `/readyz` 503 con Postgres caído; `GET /internal/v1/version` coincide con el perfil |

Las siete fábricas (reciben `DemoContext{clock, ids, registry}`; si necesitan DSN o configuración la leen de su propio entorno):

| Flag | Pieza Pulso | Contrato mínimo |
|---|---|---|
| `--tools` | `PulsoToolDispatcher` | despacha por `tool.id@version` a executors `pulso/*`, al `BuilderToolExecutor` y, en el mundo de prueba, al sandbox sembrado; tool desconocida ⇒ `ToolStatus.error` `unregistered_tool` y evento, nunca fallback silencioso; `definition(tool)` lee el `ToolDef` del registry |
| `--authz` | `PulsoAuthz` | `authorize_agent` admite sólo `PrincipalType.builder` con roles/atributos del stage; `authorize_subject` admite `subject=None`; `bind_params` derivado de `Principal.attrs` firmadas; `knowledge_view` vacío; `reportable_attrs` lista cerrada |
| `--transcript` | `NullTranscript` | tasks no registran transcript; conversacional rechazado |
| `--calibration` | `PulsoCalibrationSource` | calibraciones de los `DecisionModelDef` de Pulso; sin calibración ⇒ ruta live bloqueada |
| `--classifier`, `--field-classifier` | proveedor y `FieldClassifier` con catálogo de columnas lab | columna no catalogada ⇒ error explícito (por defecto Core la trata como `pii_direct` y la tokeniza silenciosamente: sujeto a verificación) |
| `--grant-active` | `lambda ref, now: False` | Pulso no usa delegación de asesores |

Nota de composición: el `authz` de `--authz` gobierna `/v1/runs`; el harness de evaluación del mundo de atención (`EngineScenarioHarness`/`PulsoScenarioHarness`) recibe su propio `authz` de evaluación con principal `customer` sintético, etiquetado como doble en `doubles[]`. Con `serve` stock ambos usan la **misma** pieza `--authz`, que entonces debe admitir builders y el principal sintético de evaluación (sujeto a verificación). Quién escribe las fábricas y cuáles son dobles en el mundo de prueba: D-2 y CAP-49. Reporte obligatorio: `runtime_profile ∈ {contract_mock, agent_core_real, agent_core_demo_doubles}` y `doubles[]` (por pieza y por mundo).

**Degradación si D-1 ≠ S3 (stock `serve` + sidecar).** CAP-26: pin sólo por selector `id@X.Y.Z` más verificación posterior de `RunResult.release`; CAP-27: binding desde la primera tool dentro de `serve` (la fábrica corre en el proceso) pero sin contrato de cancelación previa; CAP-28: lectura de facts por proceso sidecar con `PostgresStore` y el mismo DSN; CAP-31: `RateLimitConfig`/`Quotas` en defaults (observados, no fijados); CAP-16(L2) y CAP-08: no disponibles (L1+L3; `alias_unknown`).

#### 31.5.2 CAP-25 — Invocar una task

| Campo | Contrato |
|---|---|
| Entrada | `CoreTaskInvocation{schema_version, tenant_id, pulso_run_ref, job_id, stage, attempt, agent_id, agent_version, release_id, input_artifact_refs, lab_grant_ref, budget, cutoff, deadline, logical_key}` → el bridge arma `CreateRunBody{agent:"<id>@<X.Y.Z>", subject:null, input:{…}, lang}` y el header `Idempotency-Key = sha256(tenant|job|stage|attempt|logical_key)` en hex. No añade nuestro envelope al body. Sin `Idempotency-Key`, en blanco, no imprimible o de más de 255 caracteres, Core responde `422 invalid_request` |
| Reglas de `input` | objeto JSON plano con **nombres de slot declarados por el Flow** (claves desconocidas se rechazan antes de enviar); `lang ∈ Agent.supported_locales`; Core crea los slots `claimed`, no `validated`; sin tope de tamaño upstream, por lo que Pulso sella un máximo canónico (p. ej. 256 KiB) y los datos grandes viajan como `input_artifact_refs` + lectura por tool autorizada, nunca texto crudo de clientes |
| Semántica de Core (verificada) | Idempotencia por `(principal.key, key)` y hash del `RunInput`: misma clave y mismo body ⇒ mismo `RunResult`; otro body ⇒ 409 `idempotency_conflict`; el registro se guarda en la misma transacción que el run. Respuesta **síncrona** 201 `RunResult{run_id, release, output, status, outcome, handoff_ref, trace_id}`; `outcome ∈ {completed, failed}` para tasks |
| Salida | `CoreTaskReceipt{core_run_id, release_id, outcome, trace_id, idempotency_key_digest, request_digest, task_binding_ref, input_commitment, output_refs[], output_digest, audit_refs[], budget{known|unknown}}` (campos de §29.3; `binding_ref` pasa a llamarse `task_binding_ref`; `task_binding_ref` e `input_commitment` junto con `{tenant_id, job_id, grant_ref, attempt}` forman el binding comprometido) |
| Errores tipados | tabla de runtime de §31.2.3 y `pulso:unknown_input_slot`, `pulso:input_too_large` |
| Verificación | Mock: reproduce los códigos y la atomicidad del registro de idempotencia. Real: misma clave dos veces ⇒ mismo `run_id`; misma clave con otro `input` ⇒ 409; selector inexistente ⇒ 404 |

Un `agent: "id"` sin pin resuelve el alias `prod`; Pulso nunca lo usa para tasks. `subject:null` es obligatorio (el constructor no tiene sujeto cliente). La invocación entra por la ruta M9 completa (autenticación, autorización, límites e idempotencia) mediante cliente ASGI en proceso o loopback, no llamando directamente a `TurnEngine` (decisión de implementación sujeta a ADR).

#### 31.5.3 CAP-26 — Pin de la release exacta

Ver §29.8 «Pin de ejecución» y §29.9 #1 (`CreateRunBody` no acepta `release_id`). Delta de este contrato: (1) antes de despachar se verifica con `GET releases/{rid}` o el store que la release está `active`, es del agente/versión esperados y su clausura coincide con el manifest Pulso; (2) `PinnedRegistryPort` (contextvar con `release_id`) cubre los dos puntos de resolución y sin pin devuelve `release_pin_unavailable`, nunca `latest_release_for_agent_version`; (3) tras el run se exige `RunResult.release == release_id`, si no `release_drift` y se descarta el resultado.

| Error | Cuándo |
|---|---|
| `pulso:release_pin_unavailable` | el puerto no puede resolver exactamente la release autorizada |
| `pulso:release_revoked` | revocada antes de acciones sensibles: el run en curso no se cancela, el resultado no habilita publicación |
| `pulso:release_drift` | `RunResult.release` ≠ esperada |
| `runtime:version_pin_forbidden` | el principal no es builder/service (los pines `id@X.Y.Z` y alias distinto de `prod` sólo se admiten a `builder`/`service`) |

Verificación: mock con dos releases de la misma versión de Agent (la autorizada no es la más reciente) ⇒ el pin devuelve la autorizada; real: alias movido entre autorización y arranque y release revocada ⇒ `release_drift`/`release_revoked`, nunca ejecución silenciosa de otra release.

#### 31.5.4 CAP-27 — Contexto privado y binding previo a efectos

`ToolCallContext` trae `{run_id, release, principal, on_behalf_of, subject, turn_id}`: no tiene tenant, job ni grant. Canal de contexto: `Principal.attrs` (strings no sensibles) **firmada** por el emisor del bridge con `{tenant, job, stage, attempt, grant_ref, task_binding_ref}` y un contextvar in-process con el contexto completo (presupuesto, lease, cutoff). Las tools **nunca** reciben estos valores en `args`.

La primera tool del Flow (`pulso/bind_context`, `risk_class=read`, `args={}`) lee `ctx.run_id` y `ctx.principal.attrs`, llama a `POST /internal/v1/core-task-bindings` del control-api con `{schema_version, tenant_id, job_id, command_key, request_digest, attempt, core_run_id, bridge_instance_id, task_binding_ref}` y devuelve facts booleanos `is_scout`/`is_verifier`/`is_builder` (o `denied`). El `run_id` lo genera Core (`IdSource`): el binding "antes de efectos" sólo es posible dentro del proceso y desde esa primera tool; por HTTP puro sería posterior al efecto.

| Respuesta del callback | Efecto |
|---|---|
| 200 (binding nuevo o repetición idéntica) | continúa |
| 409 `binding_conflict` (otro `core_run_id` para la misma clave) o `digest_mismatch` | `denied` sin efecto |
| 404 `command_unknown` / 503 / timeout | `denied`: toda query, modelo o write se deniega; el receipt queda `manual_reconcile` si no se prueba ausencia de efecto |

Single-flight, callback de binding y revocación durante la etapa: ver §29.8 («Single-flight de invocación», «Revocación durante una etapa»); delta: sin contexto o con contexto cruzado ⇒ `denied`. Errores: `pulso:binding_cas_lost`, `pulso:context_missing`, `pulso:context_mismatch`, `pulso:grant_revoked`. Pendiente de verificación en implementación: propagación de `contextvars` al hilo síncrono de FastAPI. Verificación: mock con dispatcher y contextvar; real: dos POST concurrentes con jobs distintos no cruzan contexto; binding rechazado ⇒ cero efectos en lab y registry.

#### 31.5.5 CAP-28 — Leer resultado y facts de un run

`GET /v1/runs/{id}` devuelve `{run_id, status, outcome, locale, awaiting, handoff_ref, trace_id}` y sólo lo lee el principal dueño; `RunResult.output` sale de `end.output_map` y G0-22 prohíbe que un fact `origin=agent` llegue ahí. **El producto de un nodo `agent` no es recuperable por HTTP.** `core-bridge` expone `ReadRunResult(run_id)` con `UnitOfWork.load_run(run_id)` sobre el `uow_factory` del runtime: `{status, outcome, facts:{<save_as>:{value, source}}}` filtrado por **whitelist por stage** (nombres de facts y JSON Schema), límites de tamaño/PII y digest canónico (RFC 8785) antes de publicarse en Pulso. `RunState` crudo, slots y transcript no salen del proceso. Un fact `origin=agent` es no verificado; `outcome=completed` no prueba la hipótesis. `RunResult.output` sólo sirve para stages sin nodo agent.

Errores: `pulso:run_not_found` (≠ prueba de no ejecución), `pulso:fact_schema_violation`, `pulso:output_too_large`, `pulso:output_missing` (`save_as` ausente en un run `completed` es fallo del stage, no éxito parcial). Verificación: real con un Flow mínimo `agent`→`end` sin `output_map`: `GET /v1/runs/{id}` no contiene el fact y `ReadRunResult` sí; un flow con `end.output_map` hacia un fact agent lo rechaza `agentcore validate` (G0-22).

#### 31.5.6 CAP-29 — Executors y ToolDefs generales — DECISIÓN PROVISIONAL D-2 (adoptada, revisar con equipo agent-core)

Catálogo cerrado `pulso/*`: `bind_context`, `lab_query` (read/compute), `lab_write_scratch` (efímero; `risk_class` write con `idempotency_key` y `readback_by`), `wiki_read`, `wiki_explore`, `wiki_transform` (compute). Cada uno: (a) `ToolDef` versionado en `agent-core-assets/tools/` con `description`, `args_schema` sólo con keywords que acepta G0-24, `risk_class`, `idempotent`, `min_auth_level`; (b) handler en `PulsoToolDispatcher` por `tool.id@version`; (c) CI falla si hay ToolDef sin handler o handler sin ToolDef (`dependency_blocked(tool_without_executor)` en el compiler para tools nuevas). **`executor_ref` no existe en Core**: el vínculo tool→ejecución es el único `ToolExecutor` de `--tools`, así que el ejecutor es código Python importable por el proceso y un solo despachador sirve a todos los agentes.

Salida: `ToolResult{status ∈ ok|error|timeout|denied|step_up_required|uncertain, result_full, source, call_id}` con límites de filas/bytes. El `FieldClassifier` declara cada columna lab (`public|financial|pii_*|untrusted_text`); columna sin clasificar ⇒ `error: unclassified_column`. Canal ejecutor→lab: el ejecutor habla con el broker `SandboxSessionPort` por HTTP interno autenticado (JWT aud=`lab-broker` con tenant/purpose/job/lease tomados del contexto de CAP-27), no con DuckDB/filesystem/Podman. Verificación: `agentcore validate agent-core-assets/` ok; un run con un nodo agent que ejecuta dos `lab_query` dependientes; tool no declarada rechazada por el motor; columna no catalogada ⇒ `unclassified_column`.

#### 31.5.7 CAP-30 — Reconciliar una invocación incierta

Estados del bridge: `prepared|sent|binding_confirmed|terminal_ok|terminal_failed|unknown|manual_reconcile`. Ver §29.8 (readback `in_progress`/`unknown`/terminal; `load_run=None` no autoriza repetir). Delta: `in_progress` es estado del bridge, no de Core (el run y su registro de idempotencia se persisten en **un** commit al final de `start_run`). Reconciliación en orden: (1) `uow.get_run_idempotency(principal.key, key)` ⇒ si existe es el `RunResult` terminal; (2) binding del control-api; con binding y `load_run(core_run_id)` en `None` el commit de Core no ocurrió pero los efectos de registry pudieron ocurrir ⇒ (3) `RegistryService.get_write(idempotency_key)` por cada write esperado; sólo con todo ausente y presupuesto reconciliado se admite un sucesor con **nueva** clave de intento. Sin binding y comando `sent` ⇒ `manual_reconcile`. Repetir con la misma clave mientras `unknown` relee, nunca reejecuta. Errores: `pulso:unknown_outcome`, `pulso:registry_write_pending`, `pulso:manual_reconcile_required`. Verificación real: matar el proceso entre un write del registry y el commit del run ⇒ una sola propuesta, estado `unknown` visible y recuperación sin falso éxito.

#### 31.5.8 CAP-31 — Tiempo, tamaño, concurrencia, cancelación y tasa

| Aspecto | Contrato |
|---|---|
| Duración | La cota dura es `Agent.budgets{max_wall_ms_per_turn, max_model_calls_per_turn, max_tokens_per_run, max_cost_per_run}` del Agent publicado; la `deadline` de Pulso es ≥ pared + margen y el timeout de cliente nunca es menor; `deadline_exceeded` ⇒ `unknown` |
| Cancelación | Core **no** ofrece cancelar un run (no hay ruta ni puerto): "cancelar" = revocar grant/lease (los executors niegan acciones nuevas, §29.8) y esperar terminal o `unknown`; Pulso no registra `cancelled` mientras haya un run sin terminal |
| Concurrencia | `max_inflight` del bridge ≤ min(pool de Postgres, hilos disponibles), cola limitada y 429 propio `pulso:bridge_busy`; evaluate de registry serializado (`max_workers=1`: el harness comparte Clock e IDs) |
| Tasa | Defaults de Core: 30 turnos con uso registrado por ventana de 60 s (`LimitGuard.check`; filas de `usage` vía `add_usage`, un rechazo no consume cuota) y 5 USD/día **por principal**. Con S3 el runtime fija `RateLimitConfig` explícita; el bridge usa un principal por `(tenant, rol)` o sube el tope; se declara en `RunConfigRevision`, no se supone. `runtime:rate_limited`/`cost_budget_exceeded` ⇒ espera con evento explicado |
| Cuotas de registry | `Quotas` fijadas por nuestra composición, ≤ las que Pulso aplica antes (§31.4.9); `quota_exceeded` es incidente |
| Tamaño | §31.5.2 (Core no limita `input`) |

Verificación real (sujeta a verificación): la 31.ª invocación en 60 s con el mismo principal ⇒ 429 sólo si las 30 previas registraron uso (o config distinta declarada); task con presupuesto de pared bajo ⇒ `outcome=failed|escalated`, nunca un run colgado.

#### 31.5.9 CAP-32 — Constructor real

`BuilderToolExecutor(service: RegistryService, actor: Principal, ids)` requiere un `RegistryService` in-process (S3) y un `actor` builder/constructor por `(tenant, rol)` del bridge (D-12) (el principal del run sólo viaja como contexto de auditoría). Tools de código: `registry/create_proposal`, `put_draft`, `freeze`, `reopen`, `evaluate`, `validate`, `get_proposal`, `get_entity`, `list_versions`, `get_write` (`origin ∈ {builder_chat, auto_detect}`); **no** hay approve, publish, promote, revoke ni import. Sus `ToolDef` están en código (`BUILDER_TOOL_DEFS`) y deben sembrarse también como entidades del registry y listarse en `tools_allowed` de `pulso-evolution` (sujeto a verificación contra G0). Cada write lleva clave idempotente y readback por `get_write`; `evaluate` se reconcilia por §29.6 paso 5 y §31.7.1. Mock: executor sobre registry en memoria. Real: crash tras write recupera por clave/readback; misma clave con otro payload ⇒ conflicto; ninguna tool de aprobación o publicación es invocable.

#### 31.5.10 CAP-33 — Contratos y transporte del bridge

| Ruta (control-api/bridge) | Uso | Auth |
|---|---|---|
| `POST /internal/v1/core-tasks/invoke` | `CoreTaskInvocation` → `CoreTaskReceipt` (síncrono; `Idempotency-Key`, `request_digest`) | JWT `aud=core-bridge` |
| `GET /internal/v1/core-tasks/{core_run_id}` | `ReadRunResult` tratado (CAP-28) | idem |
| `GET /internal/v1/core-state/aliases/{agent_id}/{alias}` | `AliasState` (CAP-08) | idem |
| `POST /internal/v1/core-authoring/dry-run` | CAP-16 L2 | idem |
| `GET /internal/v1/version` | CAP-06 | idem |
| `POST /internal/v1/core-credentials/issue` | emite el JWS del bot constructor (`{tenant_id, role, purpose}` → `{jws, kid, exp}`); TTL ≤ 15 min, firmado con la clave identity/staff del bot, devuelto por TLS interno, **nunca persistido ni registrado** (R5); no emite credenciales humanas | JWT `aud=core-bridge` con `purpose=credential_issue` |
| `POST /internal/v1/core-task-bindings` (en control-api) | CAP-27 | JWT `aud=control-api` |
| `POST /internal/v1/platform/observations` (en control-api) | CAP-35 | JWT `aud=control-api` |

Cada mensaje tiene JSON Schema en `contracts/` (`CoreCredentialIssue`, `CoreTaskInvocation`, `CoreTaskReceipt`, `CoreTaskBinding`, `AliasState`, `CoreAuthoringDryRun`, `CoreVersion`), `schema_version` propio y fixtures del corte (a). Errores tipados del bridge: `pulso:bridge_busy`, `pulso:binding_failed`, `pulso:task_unknown`, `pulso:digest_conflict`, `pulso:core_unavailable`. Estas rutas no se publican como endpoints de Agent Core. Mock del bridge (CAP-53): servidor que cumple los mismos schemas y reproduce muerte antes/después del binding; etiqueta `runtime_profile=contract_mock`.

### 31.6 Ingerir observaciones de runs de Core

Agent-core no llama a nadie: `agent_core.outbound` sólo proyecta (funciones puras), no hay relay, webhook, cola ni cliente saliente, y no existe ruta HTTP que liste runs, eventos del registry ni auditoría (H4, H12). Para que `POST /internal/v1/platform/observations` reciba algo, Pulso construye el productor.

#### 31.6.1 CAP-34 — Exporter de observaciones

**DECISIÓN PROVISIONAL D-4 (adoptada, revisar con equipo agent-core):** un proceso `pulso-core-exporter` (Python, misma imagen que el runtime, `uv.lock` y SHA idénticos) lee Postgres de Core con un **rol sólo lectura** (`GRANT SELECT` en `audit_events`, `reg_events` y `outbox`) y publica lotes al control-api. Rust no accede a Postgres de Core (§29.8). El acoplamiento al esquema SQL se mitiga: usar las clases de `agent_core` (`PostgresAuditSink.read`, `EngineEvent`, `OutboundEvent`, `project_engine_event`, `project_registry_event`, `check_chain`) salvo para el listado de runs; contract test de esquema que compara columnas e índices de las tres tablas con un snapshot (`schema_digest`) y falla cerrado ante drift.

| Fuente | Qué lee | Cursor | Dedupe/orden |
|---|---|---|---|
| Auditoría completa | `audit_events` de la base de **producción** (`--dsn`), nunca la `--eval-dsn` | watermark temporal con solape (`ts >= watermark − overlap`, 10 min por defecto) más cursor por run `(run_id → último seq confirmado)`; no hay secuencia global | `event_id` único; por run `seq` contiguo desde 0 |
| Catálogo público | `project_engine_event` sobre la misma lectura (sin releer) | el de arriba | `event_id` del evento de cadena |
| `handoff.created` | `outbox` por `SELECT … ORDER BY seq`, **sin** `pending()` ni `mark_delivered` (mutaría el estado del despachador de handoffs de Core) | `outbox.seq` global | `message_id` |
| `release.*` | `reg_events` | `seq` global; `event_id = reg-<seq>` | `reg-<seq>`; un hueco de `bigserial` puede ser rollback: se marca `registry_seq_gap_unverified`, no pérdida |

Errores tipados: `pulso:core_db_unreachable`, `pulso:schema_drift` (bloquea), `pulso:eval_db_misconfigured` (el DSN coincide con `--eval-dsn` o los runs llevan `idempotency_key` con prefijo `eval-`: se rechaza; los runs de evaluación contaminarían la detección). Verificación mock: `platform-sim` genera cadenas reales con fixtures de `agent_core` y reproduce gap, tardío, duplicado y solape. Real: crear runs con `POST /v1/runs`, comprobar que el exporter los ve, que el solape no duplica y que un run de evaluación no aparece. Sujeto a verificación: semántica de `ts` frente al orden de commit bajo concurrencia (de ahí el solape).

#### 31.6.2 CAP-35 — Cursor, dedupe, gaps y lote

`PlatformObservationBatch` (§24): `source_id` = identificador lógico de la instancia Core; `partition` ∈ `audit:<yyyy-mm-dd>`, `registry`, `outbox`; `from_seq`/`to_seq` = `null` en `audit` (no hay secuencia global) y `reg_events.seq`/`outbox.seq` en las otras (nunca se infieren de la secuencia de un run); por evento `source_run_ref=run_id`, `source_sequence=seq` por run, `coverage_marker ∈ {complete_run, open_run, gap, late}`; `batch_digest` sobre bytes canónicos; `Idempotency-Key = batch_digest`. Respuestas: 202, 200 duplicado con mismo digest, 409 `digest_conflict`, 422 `schema_invalid`, 503 con `Retry-After`. Un run abierto se reexporta cuando crece; un evento tardío bajo un `seq` ya confirmado con hash distinto ⇒ `source_conflict`. Un `seq` salteado ⇒ `run_chain_gap(run_id, desde, hasta)` que bloquea el denominador de ese run, no el lote. Cursores persistidos en Pulso (`pulso_artifacts kind=observation_cursor`), uno por `(source_id, partition)`.

#### 31.6.3 CAP-36 — Mapping a capas

`LayerMapping{version, agent_id, rules:[{match:{flow?, node_id?, node_type?, provider?, principal_type?}, layer: tree|classifier|ai1|ai2|human, evidence_event}], default:"unknown"}`, inmutable por versión. Evento sin regla ⇒ `layer=unknown`; nunca se infiere por nombre. El upstream no declara capa. Agente: `run_started.payload.agent{id,version}`; sin `run_started` (gap) ⇒ `agent=unknown`, excluido de ratios por agente. Cada evento enriquecido lleva `layer_mapping_ref`; el original no se modifica.

**Grano de métricas, no sólo etiquetas.** Numerador y denominador de cada `MetricSpec` deben contar la misma entidad elegible y el mismo grano; el `population_ref` y el `source_contract_ref` fijan esa semántica de forma versionada y trusted. En la ruta `agent_core.outbound`, `source_run_ref=run_id`; no equivale a `Goal.goal_id`, y un evento sin `goal_ref` no permite contar metas. El primer sensor de handoff por capa se define como `attention_run_handoff_rate`: numerador = runs fuente distintos con ≥1 handoff mapeado a esa capa; denominador = población completa de runs elegibles declarada por el contrato de fuente bajo `population_ref=attention_source_runs`. El contrato de fuente debe atestiguar que `expected_population` cuenta esos runs distintos; una cobertura de goals, turns, handoff-events u otro grano no puede producir estado `measured` para este sensor y se trata como `insufficient_evidence`. Para una tasa por goal se requiere un `goal_ref` validado y un denominador de goals con la misma inclusión/ventana; no se infiere equivalencia run↔goal. El grano forma parte del digest de métrica/mapping y de la señal persistida.

#### 31.6.4 CAP-37 — Cierre del ciclo y segunda corrida

`ReleaseCorrelation{proposal_id, candidate_hash, release_id_expected = "rel-" + candidate_hash[:16], published_event_id?, promoted_event_id?, first_run_event_id?, exposure_state ∈ {published_not_exposed, promoted_unobserved, exposed, revoked, unknown}}`. Reglas: (1) `release.published` con `proposal_id` conocido valida `release_id == release_id_expected`, si no `pulso:release_mismatch` (no se atribuye); (2) publicar no produce tráfico (los runs de producción resuelven el alias `prod`): `exposed` sólo con ≥ 1 `run.started` cuyo sobre lleve `release_id` esperado **tras** `release.promoted`; (3) `release.promoted` no trae agente: se resuelve con CAP-09 y se compara con el de la decisión; (4) `release.revoked` ⇒ `revoked` y reabre la hipótesis; (5) la ventana "después" empieza en el `occurred_at` de `release.promoted` con tolerancia de reloj declarada; los runs abiertos que cruzan la promoción se excluyen del par antes/después; (6) la memoria (§21) lee `ReleaseCorrelation` y las métricas post-release ya mapeadas, no Core. Pruebas: publish sin promote ⇒ sin segunda corrida; promote a otra release ⇒ `release_mismatch`; reordenamiento `published/promoted` por entrega al-menos-una-vez ⇒ idempotente; revocación posterior ⇒ revisa memoria.

### 31.7 Evaluar de verdad

#### 31.7.1 CAP-38 — Ejecutar `evaluate` y capturar todo resultado posible

`POST …/evaluate` es síncrono, serializado (`max_workers=1`), corre fuera de la transacción de Postgres de Pulso y se representa como job local asíncrono (§27.2 paso 6). Cuerpo `{suite_id, suite_version}` (versión exacta, nunca latest). Matriz real de resultados:

| Resultado | Señal HTTP | Estado de la propuesta | Qué persiste Pulso antes de continuar |
|---|---|---|---|
| `pass` | 200 `EvalReport` | `evaluated` | reporte + `GET proposal` → `last_eval{eval_run_id, proposal_id, candidate_hash, base_release_id, suite, verdict, report, at}` y `review` |
| `fail` | **409 `gate_failed`** con `payload=EvalReport` | `draft`, `rev+1`, `candidate_hash=null` | el **cuerpo completo del 409**: es la única copia accesible por HTTP (`last_eval` queda `null` y el reporte no trae `eval_run_id`) |
| `failed_infra` | 200 `EvalReport(verdict="failed_infra", detail)` | `candidate` sin cambio; EvalRun persistido | reporte; retry acotado bajo el mismo hash y suite; nunca approve |
| cuota | 429 `quota_exceeded` | sin cambio | contador local `evals_used/20` |
| candidata cambiada | 409 `candidate_changed` | sin cambio o `draft` | releer propuesta |
| timeout del cliente | — | desconocida | releer `GET proposal`: si `state=evaluated` y `last_eval.at` es posterior al envío ⇒ adoptar; si `draft` con `rev` avanzado ⇒ resultado perdido (`pulso:evaluation_result_lost`): re-freeze y repetir, que cuenta una evaluación más de la cuota |

`EvalReport` real (*observado*): `{verdict, items[GateItem{metric_id, phase ∈ base_yardstick|new_yardstick|platform, role, value, base_value, noise_margin, floor, passed, reason}], runs{base_on_old, cand_on_old, cand_on_new}, results[ScenarioResult], judge_notes, yardstick_changes, detail}`. Las métricas se calculan sobre los eventos agrupados de **todas** las repeticiones; el `pass` de un escenario exige todas sus repeticiones. Los guardarraíles de plataforma son cuatro y deben valer 0 y estar medidos (ausencia de medición = fallo): `platform_pii_leak`, `platform_unverified_success_claim`, `platform_unverified_write`, `platform_unapproved_knowledge_citation`.

Costo y tiempo: `jobs = N_nueva + [hay vara anterior]·N_vieja·(1 + [suite vieja ≠ suite nueva])` con `N = Σ_escenarios repeticiones` (`evaluator._plan`: `cand_on_new`, y con vara anterior `base_on_old` y, si difiere, `cand_on_old`). `serve` los ejecuta secuencialmente con el gateway y Jev reales del runtime: consumen presupuesto LLM de Core, no el de Pulso. `CoreEvaluationExecutionProfile` fija `jobs_max`, timeout HTTP ≥ `jobs_max × p95_job` y reserva USD antes del POST. Core no cancela una evaluación en curso: desconectar no la detiene.

Errores: `pulso:evaluation_result_lost`, `pulso:evaluation_budget_unenforced` (`live_eval_budget_enforced=false` bloquea live). Verificación: mock reproduce los seis resultados y la pérdida de `last_eval` tras `fail`; real: suite con un escenario que falla a propósito y otra con `HarnessUnavailable` (gateway caído).

#### 31.7.2 CAP-39 — Gate combinado y revisión del aprobador

Entrada: `EvalReport` + `ApprovalReview` (`GET proposal.review`: `functional_changes`, `suite`, `suite_changes`, `gate`, `yardstick_loosened`) + `ImprovementEvidence` (U27). Salida: `CombinedGate{native:{verdict, items_failed[], platform_guardrails{4}, yardstick_changes[]}, pulso:{verdict, effect, power, unsafe, unknown}, decision: eligible|blocked|needs_loosening_acceptance}`.

Reglas: (1) `native=pass` y `pulso=pass` ⇒ `eligible`; cualquier otro ⇒ `blocked`, el candidato no llega al humano; (2) `yardstick_changes ≠ []` (nueve tipos: `metric_removed`, `role_degraded`, `metric_changed`, `threshold_removed`, `floor_loosened`, `noise_widened`, `scenario_removed`, `scenario_changed`, `repetitions_lowered`) ⇒ la `DecisionRequest` incluye la lista tipada y una opción separada `approve_with_loosening` que fija `accept_yardstick_loosened=true`; la opción por defecto **no** la acepta, y `registry:loosening_not_accepted` vuelve a `waiting_decision` con la lista; (3) un escenario que ya fallaba en la base no cuenta como regresión nativa pero sí aparece en el reporte Pulso; (4) `native=pass` con regresión dentro de `noise_margin` no acredita mejora; (5) un `Expect` vacío es válido upstream y Pulso lo rechaza; (6) sin vara anterior (`base_value=null`) el pass nativo no prueba mejora. Pruebas: nativo pass + Pulso fail ⇒ blocked; nativo fail ⇒ no hay `DecisionRequest`; `Expect` vacío ⇒ Pulso rechaza aunque Core acepte.

#### 31.7.3 CAP-40 — `PulsoScenarioHarness`

Ver §29.8 «Evaluación de tasks» (Protocol `ScenarioHarness`, aislamiento por brazo y repetición vía `SandboxPort`, `--harness`). Delta de este contrato: `PulsoScenarioHarness` construye `Principal(type="builder", roles=["constructor"], attrs=<manifest sellado>)` (el `EngineScenarioHarness` de Core fija `customer` y no es invocable con un task-agent `invocable_by:[builder]`); con S3 se inyecta además en nuestro `ScenarioEvaluator`. Setup inválido (fixture ausente, proveedor caído) ⇒ `HarnessUnavailable`/`failed_infra`; regresión del candidato sobre contexto válido ⇒ `fail`. Verificación: `failed_infra` vs `fail` diferenciados en mock y real; el candidato no escribe en el registry operativo.

#### 31.7.4 CAP-41 — Banco sandbox stateful en el gate nativo (dependency_blocked, D-7) — DECISIÓN PROVISIONAL D-7 (adoptada, revisar con equipo agent-core)

`serve` stock cablea `LocalSandbox(ports.ids)` y `max_workers=1` (`serve_registry.py`); el puerto `SandboxPort` existe. Con composición propia (S3) podríamos inyectar el banco stateful de U26 en `ScenarioEvaluator`, de modo que el gate nativo y el de Pulso compartan mundo de datos. Hasta decidirlo, el banco stateful sólo alimenta `PulsoScenarioHarness` y la campaña complementaria (declarada **complementaria**, no sustituto del gate nativo) y el nativo usa las colas de CAP-22. Mezclar sandboxes cambia lo que significa "pass nativo": exige decisión explícita y paridad por test de contrato por SHA.

#### 31.7.5 CAP-42 — Reconciliar tras respuesta perdida y gestionar cuota

| Operación | Respuesta perdida | Reconciliación |
|---|---|---|
| create | propuesta posible huérfana (sin clave nativa, sin listado) | registrar `orphan_candidate{title_digest, sent_at}`; verificar con `GET /proposals/{id}` sólo si el id llegó; descontar 1 de las 10/24 h hasta pasada la ventana; el `title` lleva `pulso-key:<k>` (≤ 200 caracteres) para detección manual por humano |
| put / freeze / reopen | — | `GET proposal` (rev, estado, hash) |
| evaluate | ver §31.7.1 | — |
| publish | — | repetir con la **misma** `Idempotency-Key` |
| promote / revoke | — | sin clave ni CAS nativos: `release.promoted/revoked` posterior en el exporter, `AliasState` (CAP-08) o `AliasChange` si hubo respuesta; nunca "prod activo" sólo por release existente |

Pulso mantiene presupuesto local ≤ cuota upstream menos un margen; llegar a 429 es incidente, no flujo.

### 31.8 Aprobación humana y firma

#### 31.8.1 CAP-43 y CAP-44 — Identidad humana step_up — DECISIÓN PROVISIONAL D-5 (adoptada, revisar con equipo agent-core)

Perfiles de credencial y operaciones por rol: ver §27.5 (tabla de perfiles). Core sólo **verifica** JWS; no hay endpoint de login ni emisión. Un humano necesita una credencial `Principal{type:"builder", roles ⊇ ["aprobador"], attrs.actor="human", auth.level="step_up"}` para `approve`, `reject`, `publish` y `promote` (`revoke` e `import` exigen sólo rol `admin` humano con step_up, `registry/roles.py::require_admin`); `auth.level=session` ⇒ `403 step_up_required` (distinto de `forbidden_role`). Pulso **no fabrica** esa credencial en producción: la obtiene y la releva.

`HumanAuthorizationPort` (Pulso; misma firma que §20.2): `prepare(actor_ref, target, operation, decision_ref) → AuthorizationTicket{challenge_ref, expiry, authority_ref}` (liga la decisión a `{proposal_id, candidate_hash}` del `target` en la bitácora Pulso; el JWS no lleva el hash, Core no lo exige) y `acquire(challenge_ref, verified_step_up) → JWS` en memoria, con TTL ≤ el de la decisión y un `kid` distinto del del bot (`challenge_ref` = ticket). Justo antes del dispatch el worker Rust reverifica `GET proposal` (`state`, mismo `candidate_hash`, `rev`) y envía el token como `Authorization` directamente a `/v1/registry` (no lo persiste ni lo registra; el bridge no interviene en credenciales humanas). Un JWS por operación; la autoridad de approve/publish puede ser distinta de la de promote. Si el JWS caducó entre decidir y publicar ⇒ `waiting_human_reauthentication`; al renovar se releen propuesta y hash.

| Entorno | Emisor | Estado |
|---|---|---|
| Local y CI sandbox | Emisor de prueba nuestro (JWS Ed25519 con `kid` humano propio, `auth.simulated=true` visible), claves públicas en `--staff-keys`; derivado de las mismas reglas que el verificador real; **no** se reutiliza `TestStaffIssuer` de `testing/` (no viaja en el wheel y usa semillas públicas) | CAP-43 especificada |
| Staging y prod (AWS) | Proveedor de identidad de la organización (OIDC/KMS por definir); hasta entonces el paso humano se ejecuta fuera de banda con `agentcore registry approve/publish/promote` y `--credential`, registrado como `evidence_kind=out_of_band` | CAP-44 dependency_blocked (D-5) |

Errores: `registry:step_up_required`, `registry:forbidden_role`, `auth:credentials_invalid`, `runtime:principal_expired`, `pulso:authorization_ticket_expired`. Verificación (mock y real): bot en approve ⇒ `forbidden_role` sin mutación; humano `session` ⇒ `step_up_required`; token expirado; `typ` incorrecto; `kid` desconocido; credencial cliente en `/v1/registry` ⇒ 401; bot y humano con la misma clave privada ⇒ falla el contract test (en producción la clave humana no existe en Pulso).

#### 31.8.2 CAP-45 — approve → publish → promote

Ver §27.2 paso 9 (secuencia, `release_id` esperado, promote humano separado). Delta: precondiciones de Core, errores tipados y confirmación exacta por paso.

| Paso | Precondición de Core | Error y reacción |
|---|---|---|
| approve `{candidate_hash, accept_yardstick_loosened}` | `state=evaluated`, hash vigente, `last_eval.verdict=pass` | `candidate_changed` ⇒ rehacer decisión; `gate_failed`/`illegal_transition` ⇒ bloquear; `loosening_not_accepted` ⇒ §31.7.2 |
| publish con `Idempotency-Key = "pulso:" + proposal_id + ":" + candidate_hash + ":publish"` | `state=approved`, aprobación vigente, `staging` == base | `proposal_stale` (→ `draft`, `rev+1`) ⇒ rebase, nueva evaluación y nueva decisión; misma clave y propuesta ⇒ devuelve la release original (éxito idempotente); misma clave con otra propuesta ⇒ `illegal_transition` (defecto de contrato) |
| promote `POST /aliases/{agent}/{alias}` `{release_id, reason}` | alias ∈ {staging, prod}, release activa del mismo agente | `AliasChange{before, after, actor, reason, at}` persistido; sin CAS ni clave: el ledger Pulso controla a nuestros writers, no a otros escritores |

Confirmación: "publicado" = `ReleaseDetail{release_id == release_id_preview, status=active}` más diff de CAP-10; "promovido" = `AliasChange` persistido y, cuando exista, `AliasState` (CAP-08) o el evento `release.promoted` (CAP-37). Nunca se afirma "prod activo" con menos. Publicar mueve **staging**; la promoción a prod es un paso humano separado, sin canary.

### 31.9 Sembrar y reproducir el mundo de Core

#### 31.9.1 CAP-46 — Layout y mundos de `agent-core-assets`

```text
agent-core-assets/
  manifest.yaml            # pin {repo, sha, contract_version}, mundos, digests, release_id esperados
  expected-state.json      # {agent_id: {release_id, release_hash, entities:[{kind,id,version,digest}]}}
  worlds/
    attention-demo/        # copia pinneada de registry-demo + eval_suites/
    pulso-evolution/       # agents flows decision_models model_profiles prompts templates tools policies
                           # injection_rulesets language_detection releases/ eval_suites/
  build/seed-root/         # ignorado por Git; salida de `pulso-bootstrap build-seed`
  ci/validate.sh  ci/check-digests.py
```

Reglas: (i) el formato es el de `agentcore validate <dir>`/`load_seed` (modelo: `tests/fixtures/registry-demo`; versiones exactas, `extra="forbid"`, sin aliases implícitos); cada mundo valida solo y fusionado; (ii) la fusión falla si dos mundos definen el mismo `kind/id@version` con distinto contenido; (iii) **una release por agente** (`len(aliases) == 1`) y **a lo sumo una `eval_suite` por agente** y evaluable (`_check_seed_suites`); (iv) versión inmutable: cambiar contenido exige nueva versión y nueva release por **propuesta**, nunca re-import; (v) `manifest.yaml` y `expected-state.json` cambian en el mismo PR que el asset; (vi) secretos jamás (`api_key_env` es un nombre). Dueño: repo `improvement-engine`; CODEOWNERS de Pulso.

`pulso-evolution@1.0.0` mínimo: `Agent` `mode: task`, `invocable_by:[builder]`, `subject_kinds:[]`, `min_auth_level: session`, `tools_allowed` = ToolDefs `pulso/*` (y `registry/*` cuando se componga el constructor), `budgets` explícitos, `EngineTemplates` obligatorias, `entry_flow` con ramas de investigación, verificación y construcción y rutas `gave_up`/`escalate` que reproducen los patrones de `tests/fixtures/runs/`, más una suite de humo independiente. Debe pasar `agentcore validate`.

#### 31.9.2 CAP-47 — Sembrar un registry vacío

| Campo | Contrato |
|---|---|
| Entrada | `uv run agentcore registry --dsn $AGENTCORE_REGISTRY_DSN --credential $AGENTCORE_CREDENTIAL --verifier pulso_core_runtime.staff:verifier --harness pulso_core_runtime.harness:build import build/seed-root`; credencial = JWS **admin humano** (fuera de local, la fuente de esa credencial depende de D-5, CAP-44) (`attrs.actor=human`, rol `admin` basta; `constructor`+`aprobador` son válidos pero no necesarios, `auth.level=step_up`) del emisor local/sandbox (§31.8.1); fuera de demo `--verifier` y `--harness` son obligatorios y el harness no se usa en el import |
| Salida | JSON `list[ReleaseDetail]` por agente; `release_id = "rel-" + hash[:16]` (determinista); **`staging` y `prod` apuntan a la misma release** (comportamiento upstream, no configurable, aunque el YAML declare sólo `prod`) |
| Precondiciones | `agentcore migrate` aplicado; el agente sin alias `staging`; `agentcore validate <root>` con código 0; ≤1 release y ≤1 suite evaluable por agente |
| Errores tipados | `registry:forbidden_role` (no admin/humana), `registry:step_up_required`, `registry:validation_failed` (≤50 violaciones; sin escritura parcial), `registry:illegal_transition` ⇒ se **reclasifica** `already_seeded` y pasa a verificación; otro ⇒ `pulso:bootstrap_failed` y se detiene |
| Idempotencia | `import_seed` no lo es: el reintento da `illegal_transition`; la verificación (`GET /releases/{release_id_esperado}` con `status=active` y digests de `entities[]` iguales a `expected-state.json` más `AliasState` de CAP-08) es la postcondición |
| Verificación mock | el mock expone el import sólo en el doble (`POST /v1/registry/_seed`, ausente en el wire real) con las mismas reglas: una release por agente, ambos alias, `illegal_transition` en re-import |
| Verificación real | instancia vacía → import → verificación; segundo import ⇒ `already_seeded`; credencial bot ⇒ `forbidden_role`; admin `session` ⇒ `step_up_required`; suite inevaluable ⇒ `validation_failed` sin escritura parcial |

#### 31.9.3 CAP-48 — Bootstrap normado

Herramienta `pulso-bootstrap core --env local|ci [--reset]` (Python, `core-bridge/tools/`; no toca tablas Pulso). Pasos ordenados, cada uno con salida y chequeo; falla cerrada:

| # | Paso | Idempotencia | Verificación |
|---|---|---|---|
| 0 | Preflight de pin: SHA de la imagen/checkout == pin, `contracts/VERSION == 1.3.0`, `uv sync --locked` | sí | manifest de CAP-11 coincide |
| 1 | `postgres-core` (PG16, la versión que valida el CI de Core) con `healthcheck pg_isready` | sí | healthcheck verde |
| 2 | Bases `core_runtime` y `core_eval` (y roles; `--app-role` de `migrate`) si no existen | sí | DSN distintos |
| 3 | `agentcore migrate --dsn … --eval-dsn … [--app-role …]` | sí (`IF NOT EXISTS`) | salidas `ok` de motor/auditoría/registry y evaluaciones |
| 4 | `build-seed`: fusiona `worlds/*` en `build/seed-root/` | determinista | digest == `expected-state.json` |
| 5 | `agentcore validate build/seed-root --json` | sí | código 0, cero violaciones |
| 6 | Claves: `staff-keys.yaml` e `identity-keys.yaml` (`{principal_keys:{kid:b64url32}}`, `kid` distintos) y credenciales de prueba bot/supervisor/admin | claves estables por entorno | un GET con el bot no da `credentials_invalid` |
| 7 | Sembrar (CAP-47) por agente | `already_seeded` | releases esperadas activas |
| 8 | Arrancar `pulso-core-runtime` (CAP-24) | n/a | `/healthz` y `/readyz` 200; `doubles[]` igual a lo declarado |
| 9 | Smoke: `agentcore llm-smoke --registry build/seed-root --profile <id@ver> --n 3` por perfil usado; `GET /v1/registry/entities/agent/{id}` y `GET /releases/{rid}` | sí | `bootstrap-report.json` |

`--reset` (sólo `local`/`ci`, nunca remoto, con confirmación): descarta las dos bases y repite 2–9; es la única forma de reiniciar la cuota `auto_detect` y las `rev` de propuestas (la cuota se mide con el reloj de Core sobre sus tablas). `bootstrap-report.json = {target, sha, contract_version, runtime_profile, doubles[], releases{}, agents_seeded[], staff_kids[]}`; todo reporte de integración lo cita. Aceptación: dos ejecuciones seguidas producen el mismo `expected-state` y la segunda no escribe en Core; tras `--reset` los `release_id` son idénticos. No se confunde con el "bootstrap de infraestructura" de §29.8.

#### 31.9.4 CAP-49 — Mundo mínimo del primer corte — DECISIONES PROVISIONALES D-10 y D-2 (adoptadas, revisar con equipo agent-core)

Todo en la misma instancia (D-10):

| Entidad | Detalle | Origen |
|---|---|---|
| `atencion@1.0.0` | `conversational`, `invocable_by:[customer]`, flow `disputa-cargo@1`, tools `buscar_transacciones`, `seleccionar`, `convertir_moneda`, `radicar_pqr`, `obtener_pqr` | copia pinneada de `tests/fixtures/registry-demo` con digest |
| `disputas-suite@1.0.0` | `eval_suites/…yaml` traducido de `testing/registry_demo.py::demo_suite` (escenario `resuelto`); ampliar con ≥1 escenario fallido y ≥1 de escalamiento para que la vara tenga varianza. El demo no trae suite en YAML | nuevo, en `worlds/attention-demo/eval_suites/` |
| `pulso-evolution@1.0.0` | §31.9.1 | nuevo |
| ModelProfile(s) | uno para generación de atención y uno `structured: prompted` para `pulso-evolution`; `endpoint_alias` ∈ `LLM_ENDPOINTS` | nuevo |

Reglas: la entrega declara "mundo: demo-atencion" y que su suite es `contract_fixture`/`demo_double` (no prueba mejora, §27.2 paso 6); sus tools son bancarias sin executor real, así que el mundo atiende con sandbox sembrado y dobles etiquetados en `doubles[]`. Para demostrar efecto real el mundo se **sustituye** (`registry-realflow` o uno propio con baseline realmente ejecutado), no se extiende. El catálogo de capacidades se genera como `capability-catalog.json = {tools:{id:{version, risk_class, executor:"pulso"|"sandbox"}}, builder_tools:[…], model_aliases:[…], source:"seed"|"bridge_introspection"}` desde la semilla y el despachador; no existe `GET PlatformCapabilityCatalog` en Core y el ejecutable no se consulta por HTTP.

#### 31.9.5 CAP-50 — Modelos, claves y parámetros de despliegue

| Elemento | Contrato Pulso |
|---|---|
| `LLM_ENDPOINTS` | JSON `{alias:{base_url, api_key_env}}`; cada `endpoint_alias` de un `ModelProfile` del mundo debe existir; `api_key_env` es un **nombre** de variable; el alias ausente es sólo un aviso al arrancar que Pulso eleva a `pulso:bootstrap_failed{model_alias_missing}` |
| `AGENTCORE_JEV_API_KEY` | obligatoria si algún `DecisionModelDef` usa el proveedor `jev` |
| `AGENTCORE_KEYS_FINGERPRINT`/`TOKEN_MAP` | `kid:base64` ≥32 bytes; etiquetado demo upstream; se documenta el riesgo si se usa fuera de local |
| `ModelProfile.price` | `source` y `as_of` obligatorios; sin precio ⇒ costo desconocido (§27.5) |
| `Quotas`, `RateLimitConfig` | fijadas por nuestra composición (§31.5.8); con `serve` stock sólo se observan |
| `EngineConfig` (`recent_turns=6`, `max_regenerations=1`) | `build_api_deps` no la pasa: queda en defaults; se registran en el manifest de campaña como `observed`, no `set` (cambiarlos exige replicar el armado del motor o un cambio upstream) |
| Verificación | `llm-smoke` por perfil en el bootstrap (real); en el mock `LLM_ENDPOINTS` apunta al gateway falso con `usage_known` verdadero y falso |

#### 31.9.6 CAP-51 — Deriva del mundo sembrado

`expected-state.json` fija `release_id` y digests por entidad; `release_hash` y `release_id_for` son deterministas. El job `assets-drift` compara la release en el registry con el manifest; discrepancia ⇒ `pulso:assets_drift` bloquea el job de evolución. Cambiar un asset exige nueva versión y propuesta.

### 31.10 Mock fiel, verificación dual-run, CI y política del pin

Niveles de verificación (se rotulan en todo reporte, R1): **(a)** mock wire (`platform-sim`, sin Core real); **(a2)** código real de Core en memoria (sin Postgres ni LLM reales); **(b)** servicio real local (§27.6). Un nivel no sustituye al siguiente.

#### 31.10.1 CAP-52 y CAP-53 — Mocks fieles

**CAP-52 `platform-sim/registry`.** Es un **servidor HTTP real** (proceso propio; binario Rust o, por ADR explícito, FastAPI mínimo), no un doble en memoria dentro del adaptador: un doble en memoria no ejercita serialización, cabeceras, `Idempotency-Key` ni `problem+json`. Hoy no existe crate ni directorio `platform-sim` en `origin/main`.

| Aspecto | Contrato |
|---|---|
| Alcance | las 16 rutas de la tabla de §27.1 con métodos, bodies, cabeceras y estados de éxito reales (201 en create, 200 en las demás); `POST /aliases/{agent}/{alias}` y `GET /entities/...?version=` incluidos; el mock **no** inventa lectura de alias |
| Auth | `Authorization: Bearer <JWS>`: firma, `typ`, `kid`, `exp`; fallo ⇒ 401 `application/problem+json` `urn:agentcore:problem:credentials_invalid` con `{type, title, status, code, trace_id}` (emitir un 401 sin `type` sería infiel al wire real); `require_builder` también en GET, `constructor` en `lineage`; matriz de `tests/registry/test_roles_matrix.py` |
| Errores | los 12 códigos y su estado (§31.2.3), `type: urn:agentcore:registry:<code>`, `trace_id`, `violations` en `validation_failed` y `payload` en el resto |
| Idempotencia | `Idempotency-Key` ausente en publish ⇒ `422 application/problem+json {"type":"urn:agentcore:problem:invalid_request","code":"invalid_request","detail":"header.idempotency-key: missing"}` (handler `RequestValidationError` de M9); misma clave y propuesta ⇒ release original; misma clave y otra propuesta ⇒ `illegal_transition` |
| Estados | `draft→candidate→evaluated→approved→published`; `reopen` invalida hash y aprobación; `fail` vuelve a `draft` con `rev+1` y sin `last_eval`; `failed_infra` conserva `candidate` |
| Concurrencia | `expected_rev` desactualizado y `proposal_stale` si `staging` se movió; el código exacto de rev se fija con fixture grabado |
| Límites y cuotas | 50 cambios, 262144 bytes, 200 nodos, título ≤200, 200 escenarios; 10 propuestas/24 h móviles y 20 evaluaciones/propuesta con reloj inyectable |
| Evaluación | reporte etiquetado `contract_fixture`, **nunca** simula mejora; resultado programable: pass, fail, `failed_infra`, timeout |
| Fallos programables | latencia, pérdida de respuesta tras commit, 500, corte de conexión, por un canal `/_sim/*` desactivado por defecto y ausente del wire real |
| Estado y versión | almacenamiento propio aislado, sin SQL; `GET /_sim/info → {pinned_sha, contract_version, fixtures_digest}` |
| Prohibido | aceptar por comodidad lo que el real rechaza; reutilizar código del adaptador de Pulso para decidir; reportar "integración con agent-core" por pasar el mock |

**CAP-53 mock del bridge.** Servidor que cumple los JSON Schemas de §31.5.10, reproduce muerte antes/después del binding, `bridge_busy`, receipts de otro tenant/job/intento y `run_not_found`, y etiqueta `runtime_profile=contract_mock`. La suite de contrato corre contra él y contra el runtime real.

#### 31.10.2 CAP-54 — Nivel (a2): lógica real de candidatas en memoria

`registry/memory.py` (`InMemoryRegistryStore`) y `registry/http.py::registry_extension(service, verifier, clock)` permiten levantar, en un proceso Python del SHA pineado y sin Postgres, el **mismo** `RegistryService` y router con un `EvalPort` inyectable. El job de CI importa el SHA por checkout (no por wheel: `testing/` no se empaqueta) y monta ese servicio; el `EvalPort` devuelve `EvalReport` scripted etiquetado `contract_fixture` (o, con el harness de `testing.registry_demo`, evalúa realmente el escenario `resuelto`, *observado*). Prueba con reglas reales: cascada, versiones, `G0-*`/`REG-*`, hash, límites y estados (CAP-13/15/16/17); **no** prueba concurrencia de Postgres, `evaluate` con LLM real ni cuotas con reloj real. No contradice "no importar main flotante": el código es el del SHA fijado. Si los símbolos cambian, el job falla en el bump de pin (N-06).

#### 31.10.3 CAP-55 — Suite dual-run y fixtures grabados

Suite `registry-wire-contract`, independiente del adaptador de Pulso, que recibe `REGISTRY_BASE_URL` y `TARGET ∈ {mock, a2, real}` y corre **sin cambios** contra los tres.

| Elemento | Contrato |
|---|---|
| Casos | una fila por regla de la matriz de §31.10.1 (auth, 12 errores, idempotencia, estados, CAS, roles, límites ±1, cuotas, `problem+json`); cada caso declara `applies_to: both\|mock_only` y un caso `mock_only` exige justificación |
| Comparación | estructura normalizada: método, ruta, estado, content-type, `type`, `code`, conjunto de claves del body y presencia de `trace_id`; se enmascaran ids, hashes, instantes y `trace_id` |
| Fixtures | `fixtures/agent_core_wire/<sha>/<caso>.json` con request y response normalizados producidos por el **real**; se regeneran con `record-wire` (sólo contra real, manual) |
| Drift | real ≠ fixture ⇒ `wire_drift_detected` (falla el job y bloquea el bump); mock ≠ fixture ⇒ `mock_infidelity` (falla el CI ordinario) |
| Aceptación | el mock es fiel si pasa el 100 % de los casos `both` y el real también; un caso que pasa sólo en el mock no cuenta; divergencia ⇒ se arregla el mock, no se relaja el caso |

Pruebas: alterar el mock para aceptar un publish sin clave ⇒ la suite falla; cambiar a un SHA con una ruta modificada ⇒ `wire_drift_detected`; dos corridas contra real no producen `quota_exceeded` espurio (base nueva por corrida).

#### 31.10.4 CAP-56 — Errores, límites y cuotas reales

Cada fila de §31.2.3 tiene un caso. Límites probados en −1/exacto/+1 con el mismo vector en mock y real: 50 cambios; 262144 bytes por entidad; 200 nodos por flow; 200 escenarios por suite; 50 pasos; `repetitions ≤ 10`; título ≤ 200; 20 evaluaciones por propuesta; 10 propuestas en ventana móvil de 24 h medida con el `Clock` de Core. Un caso que requiere `quota_exceeded` usa reloj inyectado (mock/a2) o base nueva por corrida (real); nunca espera reloj de pared.

#### 31.10.5 CAP-57 — CI de integración, drift y política del pin — DECISIÓN PROVISIONAL D-11 (adoptada, revisar con equipo agent-core)

Jobs en `improvement-engine/.github/workflows/ci.yml` (acciones fijadas por SHA, §26.2):

| Job | Cuándo | Qué hace | Secretos |
|---|---|---|---|
| `contract-drift` (incluye `wire-drift`) | cada PR y push | checkout del SHA del pin, `uv sync --locked`, `agentcore contracts --check` y regeneración de `registry_schemas/`; compara digest por archivo con `files` del `MANIFEST.json` referenciado por `contracts/agent_core/pin.json`; valida fixtures con los validadores Python del SHA; arranca la app `pulso-core-runtime` con fábricas fake y comprueba que las ~5 funciones de composición siguen existiendo | ninguno |
| `mock-wire` | cada PR | `platform-sim/registry` y bridge mock, suite dual-run con `TARGET=mock`, adaptador contra el mock | ninguno |
| `a2-wire` | cada PR que toque compiler/adaptador/pin | CAP-54 con `TARGET=a2` y el caso dorado de §31.4.12 | ninguno |
| `real-wire` | diario, manual y en PR que toque `adapters/agent_core_http`, `platform-sim/registry`, el manifest o el pin | `postgres-core` PG16, imagen del runtime, `migrate`, bootstrap (CAP-48), suite dual-run `TARGET=real`, E2E de §31.11.4; LLM scripted | ninguno de proveedor |
| `real-live-models` | manual o programado; **nunca** en PR de forks | smoke con Jev y LLM reales | secretos del entorno, sólo ramas del repo |
| `ci-required` | siempre | job agregado estable; informa qué suites aplicaron y por qué | — |

`contracts/agent_core/pin.json = {repo, sha, contract_version, uv_lock_sha256, manifest_sha256}`, donde `manifest_sha256` referencia el `MANIFEST.json` de §31.4.1 (los digests por archivo viven allí, bajo `files`, no se duplican en el pin); el workflow usa `ref: <sha>`, nunca una rama. Caché de `uv` por `uv.lock` del SHA, sin secretos. Timeouts iniciales (a medir): `real-wire` ≤ 20 min, `contract-drift` ≤ 5 min. `real-wire` rojo en main bloquea cualquier PR que toque el adaptador; no se declara integrado con `mock-wire` verde. Cada ejecución emite `integration_report.json {target, sha, runtime_profile, doubles[], suites, skipped}`; el contrato de entrega de §30.5 añade esos campos.

**Bump del pin (normativo).** (1) PR dedicado `chore(agent-core): bump pin <old>..<new>`; (2) corre `contract-drift` y muestra el diff de `file_digests`; (3) se regeneran fixtures con `record-wire` y se revisa el diff; (4) prueba de esquema nuevo con binario anterior y viceversa (expand/contract, N-11): si falla, se bloquea el bump; (5) un ADR resume los cambios de contrato y hallazgos; sin ADR no hay bump; (6) aprueba un revisor independiente (el integrador de Pulso aprueba, no escribe el PR); (7) se actualiza §27.5 si cambian perfiles, errores, límites o cuotas.

### 31.11 Ambiente local real, E2E y despliegue conjunto

#### 31.11.1 CAP-58 — Ambiente local real

**DECISIÓN PROVISIONAL D-6 (adoptada, revisar con equipo agent-core):** un solo proyecto Compose (`improvement-engine/local`) con Pulso y Core. Razón verificada: Core no trae Dockerfile ni servicio de aplicación y su `docker-compose.yml` sólo aporta Postgres 16 con bind `127.0.0.1:5432`; con imagen propia (CAP-60) un segundo stack sólo añadiría `host.docker.internal` y orden de arranque entre proyectos.

| Servicio | Detalle |
|---|---|
| `postgres` (Pulso) | el actual (puerto 54329) |
| `postgres-core` | PG **16** (versión que valida el CI de Core; 17 sólo tras pasar el contract test), bases `core_runtime` y `core_eval`, roles distintos; Pulso nunca recibe DSN de Core |
| `pulso-core-runtime` | imagen CAP-60; `--host 0.0.0.0`, puerto 8000, sin `AGENTCORE_ALLOW_DEMO` |
| `core-exporter` | misma imagen, rol sólo lectura |
| redes | `pulso-internal` (hoy `internal: true`) y `core-egress` (LLM/Jev); sólo `pulso-core-runtime` pertenece a ambas; el resto de servicios Pulso sólo alcanza a Core por `pulso-internal` |
| orden | `postgres-core` → job `migrate` → `pulso-core-runtime` (`/readyz`) → `core-exporter` → `control-api`/`worker` |

Runtime de contenedores: uno por máquina, registrado en `doctor`. En Podman rootless el cgroup `pids` bloquea Postgres/LocalStack sin `--cgroups=disabled` (reportado en la bitácora de `improvement-engine`; sujeto a verificación); `doctor` reporta `podman_cgroup_pids_unavailable` y **no** pasa el flag por su cuenta (decisión humana ya registrada). Comandos de nombre estable (firma sujeta a implementación): `scripts/dev.ps1 up --with-core`, `down` (no borra volúmenes), `reset-core` (único destructivo, con confirmación), `doctor --with-core`. Fallback de depuración: `uv run` del runtime en el host contra `postgres-core` publicado; se rotula `target=real_local`, `runtime_profile=host_process` y no sustituye la imagen. Reset entre corridas: bases `core_runtime_t<run>` y `core_eval_t<run>` (variantes efímeras por corrida de las bases `core_runtime`/`core_eval` de CAP-48) creadas y migradas por corrida (las cuotas y revs son acumulativas); nunca se toca la base de Pulso. Tiempos de arranque: se miden en la primera corrida real; V3 no promete valores. Fallos tipados: `pulso:core_checkout_wrong_sha`, `pulso:core_postgres_unavailable`, `pulso:core_migrate_failed`, `pulso:core_not_ready`, `pulso:runtime_cgroup_unavailable`, `pulso:port_conflict`.

#### 31.11.2 CAP-59 — `doctor` verifica la conexión

| Check | Éxito | Fallo tipado |
|---|---|---|
| Digest/SHA de la imagen | igual al pin | `pulso:core_checkout_wrong_sha` |
| Toolchain (host/CI) | Python 3.12 y `uv sync --locked` | `pulso:core_toolchain_missing` |
| `postgres-core` | `pg_isready`, DSN `core_runtime` ≠ `core_eval` | `pulso:core_postgres_unavailable` |
| Migraciones | `migrate` idempotente | `pulso:core_migrate_failed` |
| `/healthz` y `/readyz` | 200 y 200 | `pulso:core_not_ready` |
| Modo | `doubles[]` vacío o declarado por mundo | `pulso:core_demo_doubles_active` (informativo) |
| Credencial | lectura `GET /v1/registry/releases/<semilla>` con el bot ⇒ 200 | `auth:credentials_invalid` / `registry:forbidden_role` |
| Contrato | `contracts/VERSION == 1.3.0` y digests == manifest | `pulso:contracts_drift` |
| Red | el worker alcanza `pulso-core-runtime:8000` por `pulso-internal` | `pulso:core_unreachable_from_stack` |
| Seed | releases esperadas activas (CAP-47/51) | `pulso:assets_drift` |

#### 31.11.3 CAP-60 — Imagen del runtime — DECISIÓN PROVISIONAL D-3 (adoptada, revisar con equipo agent-core)

Imagen `pulso-core-runtime:<sha_agent_core7>-<sha_pulso7>`, multi-stage, Python 3.12, `uv sync --locked` con `uv.lock` propio versionado, `agent_core` por SHA (dependencia git o vendoring) y paquete `pulso_core_runtime`; entrypoints `runtime`, `exporter`, `seed` y `bootstrap`. **El Dockerfile es nuestro:** el runtime contiene nuestras fábricas e identidad builder, por lo que no depende de una imagen upstream (que no existe: H3). Orden de arranque: `migrate` (job one-shot con la imagen nueva, `--eval-dsn` distinto, `--app-role`) → runtime. `schema.sql` sin migraciones versionadas ⇒ el CI prueba `migrate` sobre la base del SHA anterior. Variables: `AGENTCORE_REGISTRY_DSN`, `AGENTCORE_EVAL_DSN`, `AGENTCORE_KEYS_FINGERPRINT`, `AGENTCORE_KEYS_TOKEN_MAP`, `AGENTCORE_JEV_API_KEY`, `LLM_ENDPOINTS` + `<api_key_env>`, `AGENTCORE_SERVE_AGENTS`, `OTEL_*`. Errores: `pulso:image_sha_mismatch`, `pulso:migrate_failed`, `pulso:contracts_drift`.

#### 31.11.4 CAP-61 — Primer E2E real

**Escenario `E2E-REAL-01` "propuesta gobernada sobre `disputa-cargo`".** Semilla: CAP-47 con el mundo de CAP-49; ejecuta los pasos de §31.4.12 (1–7) con credencial bot y supervisor step_up (CAP-43), más el segundo publish con la misma clave.

Se mide: (i) cada paso devuelve estado y forma esperados; (ii) `candidate_hash` de dry-run == `freeze`; (iii) clausura y `content_hash` locales coinciden con la release; (iv) los receipts persisten **antes** de cada avance; (v) `trace_id` correlacionado; (vi) el segundo publish no crea otra release; (vii) `runtime_profile` y `doubles[]` quedan en el reporte. Éxito: todo lo anterior y la misma secuencia con salida normalizada igual en mock (a) y a2. Fracaso tipado: `wire_drift_detected`, `pulso:content_hash_mismatch`, `pulso:receipt_not_persisted`, `pulso:duplicate_release`, `auth:credentials_invalid`, `pulso:core_not_ready`. No se concluye mejora ni efecto: el reporte de evaluación es de una suite `contract_fixture`/`demo_double`. Un `dependency_blocked` por un hueco conocido se registra y no cuenta como éxito.

Negativos: publish sin clave; approve con bot (`forbidden_role`); approve sin step_up; PUT con `expected_rev` viejo; staging movido (`proposal_stale`); crash tras create (`unknown`); cuota agotada.

| Unidad | Prueba real mínima | Negativo real |
|---|---|---|
| U09-A/U09-B task Core | invocar una etapa y leer su receipt por CAP-25/28 | crash a mitad de la llamada ⇒ `unknown` |
| U10 modelos | `llm-smoke` por perfil real | grant inválido; costo unknown |
| U11 Jev | decisión tipada por el runtime real | enum inválido; baja confianza |
| U17 compiler | hash, clausura y dry-run iguales a `freeze` | entidad fuera del subconjunto |
| U18 writer | pasos 1–4 del E2E | payload alterado tras el compiler |
| U19 evaluación | paso 5 con reporte real | `failed_infra`; timeout ⇒ `unknown` |
| U21 publicación | pasos 6–7 | bot; sin step_up; clave repetida con otra propuesta |

#### 31.11.5 CAP-62 — Despliegue conjunto en AWS por manifest (dependency_blocked) — DECISIÓN PROVISIONAL D-3 (adoptada, revisar con equipo agent-core)

Bloqueo: D-3 (quién construye la imagen) y ADR 0003 de `infra` aceptada con las correcciones de abajo; AWS requiere autorización humana separada (§26.2).

`deploy-manifest.json` (firmado, como en §4): `{environment, engine:{image_digest, git_sha, migrations_head}, agent_core:{image_digest, git_sha, contracts_version, registry_migrations_head, eval_migrations_head}, contracts:{pin_manifest_digest}, infra:{git_sha, plan_digest}, smoke:{suite, target, result}}`.

| Tema | Contrato |
|---|---|
| Topología | dos workloads ECS Fargate separados (`improvement-engine` y `pulso-core-runtime`), sin base ni rol compartidos (ADR 0003); `runtime` de §4.1 deja de decir "sin Agent Core"; el diagrama de §10 muestra `pulso-core-runtime` como servicio propio con su RDS |
| Red | `pulso-core-runtime` en subred privada; SG que admite sólo el SG del worker/exporter de Pulso en 8000; nombre interno estable (ALB interno o Service Connect: decisión de `infra`); sin ingress público; egress a `api.typesafe.ai` y a los hosts de `LLM_ENDPOINTS` (`nat_strategy` ≠ `none`) |
| Base de datos | RDS PG16; una instancia con dos bases o dos instancias queda abierta en el ADR; no se aplica hasta decidir |
| Secretos | los de §31.9.5 y el ADR; **dos archivos de claves públicas** (`--identity-keys`, `--staff-keys`) montados como secreto/archivo, no como variable; `AGENTCORE_ALLOW_DEMO` no definida (contrato estático Terraform lo rechaza) |
| Orden | (1) Terraform si hay cambio; (2) tarea one-off `migrate` con la imagen **nueva**; (3) smoke de esquema; (4) actualizar `pulso-core-runtime`; (5) esperar `/readyz`; (6) migraciones de Pulso; (7) actualizar servicios de Pulso; (8) smoke `registry-wire-contract` real y E2E acotado. Pulso nunca se actualiza antes de que Core esté listo con el contrato esperado |
| Compatibilidad | se despliega sólo si `contracts_version` y `pin_manifest_digest` coinciden con la imagen de Pulso; si no, `pulso:manifest_incompatible` |
| Rollback | se restaura el par de digests anterior como unidad; las migraciones no se revierten (expand/contract, probadas en ambas direcciones por CI); un `migrate` destructivo bloquea el despliegue sin estrategia; la evidencia y los receipts se conservan |
| Sweeper | `agentcore sweep --once` programado (EventBridge) pertenece al workload `pulso-core-runtime` y se verifica en el smoke |
| Receipt | cada despliegue registra manifest, resultado del smoke y aprobador; un deploy no prueba éxito funcional |

Correcciones a ADR 0003 de `infra` (repo nuestro, mismo PR que el manifest): `/healthz`, `/readyz` y `agentcore migrate` **sí existen** en el SHA; Dockerfile e imagen son de `improvement-engine` según la decisión provisional D-3 (revisar con equipo agent-core); añadir los dos archivos de claves, las fábricas y el SG engine→core-runtime; pasar de Proposed a Accepted. Pruebas: manifest incompatible rechazado; `migrate` fallida detiene el despliegue; rollback conjunto restaura servicio y smoke; task definition con `AGENTCORE_ALLOW_DEMO` rechazado por Terraform; SG abierto a cualquier origen rechazado.

#### 31.11.6 CAP-63 — Credenciales y datos de prueba

`dev.ps1`/`pulso-bootstrap` generan por entorno local: password de ambos Postgres, pares Ed25519 (staff, identity, humano de prueba) y `AGENTCORE_KEYS_*` aleatorios, todos en un secreto local ignorado por Git, nunca en compose/config/imagen/logs. Los valores de `.env.example` de agent-core (`demo-fp-1:REPLACE…`) y la contraseña literal de su compose son **sólo de demo** y no se usan. La credencial humana de prueba lleva `auth.simulated=true` y su `kid` no existe en configuración de staging/prod; un contract test falla si una clave de prueba aparece en la configuración de un entorno remoto. El guard `AGENTCORE_ALLOW_DEMO` (en Core) se complementa con el contrato estático de despliegue y con `doctor`. Datos de escenario: sintéticos; sin PII ni `final_locked` en suites, `docs` ni receipts.

#### 31.11.7 CAP-64 — Trazas y huecos conocidos

`traceparent` Rust→bridge; el bridge ejecuta el run dentro del span; `RunResult.trace_id` y el `trace_id` de cada `problem+json` se guardan en el receipt y se asertan en las pruebas; jamás se guarda contenido (Core excluye args y results de sus eventos). `known_gaps` versionado por SHA (`contracts/agent_core/known_gaps.json`) que las pruebas de integración consultan para clasificar `dependency_blocked` sin parecer éxito: transferencia que no opera con `serve`, publicación de knowledge por propuesta, `usage_known` no propagado por `LLMAgentPort`, escenarios `dataset`, evaluación concurrente, lectura de alias nativa, cambios a nivel release.

### 31.12 Dependencias y solicitudes a agent-core no cubiertas en §29.9

§29.9 sigue vigente (filas 1–8). Esta tabla añade lo que **no** podemos construir nosotros y no está allí; cada fila deja un workaround nuestro y una ruta `dependency_blocked`, nunca una simulación presentada como integración. Ninguna bloquea el primer corte.

| # | Necesitamos [AGENT-CORE] | Por qué | Evidencia (SHA 86a7674) | Mientras tanto (nuestro lado) |
|---|---|---|---|---|
| N-01 | Que `agentcore contracts` exporte `EvalSuite`, `EntityDraft`, `VersionDocs` y los modelos de respuesta del registry (o que `openapi.json` incluya `/v1/registry`) | El cuerpo de `PUT draft` y la suite no tienen schema publicado; `contracts --check` no detecta drift del registry | `contracts.py::_collect` sólo recorre `domain` y `ports`; `openapi.json` sin `/v1/registry` | Derivarlos con pydantic del SHA (CAP-11); suite dual-run como único detector (CAP-55) |
| N-02 | Rutas de lectura de alias (`GET /v1/registry/aliases/{agent_id}/{alias}`) y de versiones por entidad | Leer la base staging/prod sin crear propuesta ni gastar cuota; reconciliar promote/revoke | `registry/http.py` no las monta; `service.list_versions` existe sin ruta | Lectura del bridge sobre el store (CAP-08) o `ObservedAlias`; `alias_unknown` |
| N-03 | Que `ReleaseDetail` incluya `interrupts`, `language_detection`, `injection_ruleset`, `max_input_chars` | Reconstruir `release_hash` localmente | `models.py::ReleaseDetail` los omite | Dry-run del bridge (CAP-16/17) |
| N-04 | Endpoint o cabecera de versión/SHA/contrato de la instancia | `info.version` 1.0.0 vs `VERSION` 1.3.0; hoy sólo se distingue por imagen y sonda | `/healthz` → `{"status":"ok"}` | Perfil con digest + sonda + `/internal/v1/version` nuestro (CAP-06) |
| N-05 | Confirmar que `{id, spec}` e `"id@spec"` son equivalentes de contrato y que el hash se calcula sobre el modelo normalizado | Evitar depender de comportamiento observado | `candidate._parse_drafts`, `entities.encode_entity` | Emitir siempre la forma normalizada; prueba dorada de hashes (CAP-12) |
| N-06 | Declarar estable la superficie de composición que consumimos: `resolve_ports`, `ServePorts`, `build_api_deps`, `ApiDeps`, `registry_extension`, `RegistryService(quotas=)`, `ScenarioEvaluator`, `PgRegistryStore`, `registry/memory.py` | S3 y el nivel a2 dependen de ella; extiende §29.9 #6 | `composition/serve.py`, `serve_ports.py`, `api/app.py` | Pin por SHA y job `contract-drift` que arranca la app (CAP-57) |
| N-07 | Mecanismo para cambios a nivel release (interrupciones, idioma, ruleset, `max_input_chars`) por propuesta | Hoy `candidate._decl` los hereda de la base | `registry/candidate.py::_decl` | `dependency_blocked(release_level_change)` (CAP-23) |
| N-08 | Listado/exportación estable de runs y eventos (auditoría, registry, outbox) | La ingesta depende de leer Postgres de Core | no hay `GET /v1/runs` ni rutas de eventos; `export_events` exige `run_ids` | Exporter con rol sólo lectura y contract test de esquema (CAP-34) |
| N-09 | Recarga en caliente de los archivos de claves (`--identity-keys`, `--staff-keys`) | Rotar exige reiniciar el runtime | `load_identity_verifier` lee sólo al arrancar | Ventana de reinicio planificada y `kid` solapados (CAP-04) |
| N-10 | Incluir `eval_run_id` en el `payload` de `gate_failed` y exponer el EvalRun de un `fail` | `last_eval` es `null` tras `fail` y el reporte no trae id; extiende §29.9 #2 | `service.evaluate` (`candidate_hash=None` en fail) | Persistir el cuerpo 409 (CAP-38) |
| N-11 | Garantía de migraciones expand/contract entre SHAs | Rollback conjunto sin deshacer migraciones | `migrate` idempotente sin política de compatibilidad | Prueba nuestra de esquema nuevo con binario anterior en el bump (CAP-57) |

**Evaluadas y no solicitadas (con razón).** Dockerfile/imagen upstream: la imagen es nuestra (CAP-60). Empaquetar `testing/`: emisor propio de claves de prueba (CAP-43). Import de semilla por HTTP: `agentcore registry import` en nuestra imagen (CAP-47). Flags de `Quotas`/`RateLimitConfig`/`EngineConfig` en `serve`: no hacen falta con composición propia (S3); si la revisión de D-1 elige otra opción distinta de S3 se solicitan. Estas cuatro dejan de ser dependencias de agent-core y pasan a depender de D-3 y D-1.

**Bloqueos resumidos.** CAP-23 ⇐ N-07; CAP-41 ⇐ D-7; CAP-44 ⇐ D-5 y el proveedor de identidad de la plataforma (no es solicitud a agent-core); CAP-62 ⇐ D-3 y ADR 0003. Todo lo demás es construible por nosotros asumiendo las recomendaciones de las decisiones abiertas.


## 32. Plataforma de atención real, Fase 1: perfil de fuente `platform_live` (cambio aditivo)

**Origen.** El equipo de producto (la plataforma de atención y soporte en sí, distinta de Agent Core y de Pulso) publicó el modelo de datos de la plataforma real: 11 tablas, SQLite portable a Postgres. Análisis completo y trazable en [PLATFORM_DATA_MODEL_IMPACT_CLAUDE.md](PLATFORM_DATA_MODEL_IMPACT_CLAUDE.md). El plan de producto, relevado por el usuario, tiene tres fases: **Fase 1** plataforma funcional (este modelo es lo mínimo que necesita para operar y es parte de nuestro insumo); **Fase 2** árboles, flujos y agentes sobre la plataforma, junto con Agent Core y Pulso (lo que el equipo de Agent Core ya construye); **Fase 3** detección de oportunidades, análisis, evaluación y propuesta (este spec).

**Regla de no regresión.** Esta sección es **aditiva**. Nada de §§1–31 cambia de sentido: el resultado sigue siendo artefactos Agent Core evaluados, los grados `same_outcome_linked|mechanism_proxy|unlinked|not_evaluable`, los dos gates y las familias de detección de capas IA se mantienen. El modelo de la plataforma es el **perfil de Fase 1** del contrato de fuente: acota lo que puede ejecutarse hoy; a medida que la plataforma crece, el mismo motor se habilita sin reescribir detectores. `platform_history` 0.5.1 (E0) sigue siendo el mundo rico de la demo y la forma probable de los datos de Fases 2–3.

### 32.1 Qué es la fuente y en qué difiere de E0

Subconjunto real: `cases`, `turns` (append-only, `sequence` sin huecos por caso), `assignments` (append-only), `customer_case_slots`, `customers`, `event_log` (append-only, `sequence` global contiguo, `event_time` e `ingested_at`, `payload` JSON) y tablas de personal/acceso. Ausentes frente a E0: `origin`, `topic`, `complaint_id`, `identity_check`, `routing_step`, `copilot_query`, `tool_call`, `approval`, `suggestion`, `signal`, `component`; el cierre vive en `cases` (`close_reason`, `close_note`), sin `resolved`, `resolution_code` ni CSAT; canales sólo `app_chat|web_chat`. `cases`, `staff` y `customer_case_slots` son mutables (`version`).

### 32.2 Contrato aditivo de la fuente `platform_live`

1. **Fuente de lectura, nunca de escritura.** Namespace propio (`source_namespace=platform_live`); un `CASE-…` no es el `case_id` de E0 ni un `complaint_id` (regla de §28.2).
2. **Allow-list por defecto.** Se ingieren `cases`, `turns`, `assignments`, `customer_case_slots`, `event_log` y dimensiones mínimas de `staff` (roles, idiomas, equipo, activo). `login_accounts`, `mfa_challenges`, `staff_sessions`, hashes, correo y nombres **nunca** se leen. `auth.*` sólo por allow-list de tipos de evento. El texto de `turns` y los nombres siguen el tratamiento previo a `ModelPort` de §28.2 y la regla de egress local si el dato no está autorizado para modelos alojados.
3. **Evento como verdad, tabla como dimensión.** El estado se reconstruye a fecha de corte desde `event_log` (`case.status_changed`, `case.assigned`, `case.closed`), `assignments` y `turns`. Leer `cases` actual para el estado filtraría el futuro (estado final, `close_reason`) y viola «labels y cierres posteriores nunca entran en descubrimiento». Las dimensiones se leen con digest de snapshot.
4. **Transporte.** Cada fila de `event_log` es un `platform_event` de §24.2 con `source_sequence = event_log.sequence`, `available_at = ingested_at` (medido; sustituye el modo replay de §28.2 para esta fuente) y partición por tenant. La contigüidad de `sequence` y de `turns.sequence` por caso da prueba de completitud; un hueco es `gap_suspected` (puede ser un rollback de la plataforma), pide backfill y verificación con el dueño, nunca se acepta en silencio. Un evento tardío abre revisión de ventana (§24).
5. **Catálogo de eventos versionado.** Un `event_type` desconocido se cuenta y va a cuarentena con hallazgo de calidad; **no** falla el lote (`deny_unknown_fields` no aplica a tipos nuevos admitidos por allow-list versionada). Cubre la evolución anunciada por producto (`teams`, `staff.team_id`, `admin_roster`, eventos `staff.*`/`team.*`).
6. **Perfil de capacidades versionado por fase.** El manifiesto declara qué existe (`origin`, `topic`, `complaint_id`, `identity_check`, `routing_step`, `tool_call`, `approval`, `suggestion`, `case_close.resolved`, `csat`, canales). Cada detector deriva de ese perfil sus denominadores y emite `unsupported` o `insufficient_*` nombrando la capacidad faltante; no hay comprobaciones ad hoc. Un perfil superconjunto (forma 0.5.1) habilita las familias existentes sin cambiar el detector.
7. **Procedencia.** `customers.simulator=true` y los `suggestions` demo se marcan `evidence_kind=team_generated` y se excluyen de poblaciones y de cualquier afirmación de valor. `sla_due_at` (5/15/60 min por prioridad) es un valor declarado por la plataforma con procedencia, no una constante universal ni una violación regulatoria (§24.1); pausas y esperas no están modeladas, sólo disponibilidad del analista.
8. **Sin puente exacto al dataset bancario.** Sin `complaint_id`, el vínculo `CUS-…` ↔ `customers.customer_id` exige mapeo autorizado (§28.2); por defecto `unlinked`/`mechanism_proxy`. `previous_case_id` sí es relación declarada para recontacto; `close_reason=customer_unresponsive` no cuenta como recontacto de fracaso por defecto.

### 32.3 Qué detecta hoy y qué se detiene

Con datos de Fase 1: primera respuesta y SLA, espera en cola, inanición por idioma (regla H1), carga desbalanceada, rotación de reasignaciones, mezcla de motivos de cierre, cadenas de recontacto, volumen y patrón de turnos, disponibilidad. Los hallazgos operativos **no tienen aún artefacto de Core que cambiar** (no hay árboles, flujos ni agentes en Fase 1): terminan en `insufficient_*`/`waiting_dependency` en el paso de propuesta, con evidencia y denominadores completos, y se exponen sólo como insight de lectura; si alguien quisiera actuar sobre ellos, la autoridad es la (b) de §24.1. No se introduce clase de salida nueva ni camino de publicación. Las familias que requieren evidencia ausente (capas IA, herramientas, identidad, aprobaciones, resolución humana verificada) quedan `unsupported`/`insufficient_human_evidence`, como ya exige §24.

### 32.4 Reparto de ownership (igual que con Agent Core)

**Team Codex** (motor Rust, semántica de detección/evidencia/evaluación; edita el spec canónico):

| ID | Trabajo |
|---|---|
| PL-C1 | Adaptador `platform_live` en la ruta U29: catálogo cerrado con cuarentena, `source_sequence`, huecos, `available_at=ingested_at`, revisión por evento tardío, reconstrucción as-of desde eventos |
| PL-C2 | Perfil de capacidades en el contrato de fuente y su uso en detectores U30; familias operativas de §32.3 con `unsupported`/`insufficient_*` explícitos |
| PL-C4 | Allow-list de tablas/eventos, tratamiento de privacidad de texto y nombres, tablas de credenciales denegadas por construcción |
| PL-C5 | (reducido) qué evidencia basta para detenerse en insight; no se evalúa candidato en Fase 1 |
| PL-C6 | Integrar esta sección en el cuerpo del spec y en sus catálogos (§30.8) |
| PL-C3 | (diferido, opcional) superficie de sólo lectura para hallazgos sin objetivo Core |

**Team Claude** (frontera con sistemas externos; paralelizable desde ya, archivos disjuntos de Codex):

| ID | Trabajo |
|---|---|
| PL-L1 | `platform-exporter`: cursor de sólo lectura sobre `event_log` y tablas append-only, emite `PlatformObservationBatch` a `POST /internal/v1/platform/observations`; digest, reintento hasta ack durable, backfill por secuencia, tolerante a deriva de esquema |
| PL-L2 | Simulador de plataforma en `platform-sim`: las 11 tablas, `sequence`, `ingested_at`, `cases` mutables, filas demo, eventos tardíos, huecos y tipos desconocidos, más la evolución `teams`/`team_id` |
| PL-L3 | Paquete de contrato `platform-contract/`: JSON Schemas de las tablas y del catálogo de eventos, ejemplos dorados, suite de conformidad con chequeo de deriva (mismo enfoque que `bridge-contract/`) |
| PL-L4 | Consola: cobertura y perfil de capacidades por fuente (nivel de fase), feed de eventos, contadores de tardíos/huecos/cuarentena, tarjetas de insight de sólo lectura |
| PL-L5 | Infra propia: secreto de credenciales de sólo lectura, rol/SG del exporter, entrega de claves como en ADR 0009; sin duplicar infra de la plataforma |
| PL-L6 | Pruebas con dependencias reales: exporter contra SQLite y Postgres reales (Podman), E2E exporter→control-api con huecos/tardíos/tipos desconocidos |

**Nota de estado (2026-10-04, aditiva; §32 no cambia de sentido).** PL-L1 (`platform-exporter/`), PL-L2 (`platform-sim/platform_live/`), PL-L3 (`platform-contract/`) y PL-L4 (vista «Sources» de la consola) están **implementados y fusionados en improvement-engine#80** (`f4fbfa9`; fusión en `main` 03-10-2026 21:54 UTC). Evidencia local: platform-contract 26 pruebas sin deriva, `platform_live` 20, platform-exporter 51 contra postgres:16 y SQLite reales, consola 121 pruebas. La infra propia del exporter (PL-L5: secreto de sólo lectura, SG, claves como en ADR 0009) está fusionada y apagada por defecto en infra#26 (`c5ff691`). PL-L6 está cubierto contra SQLite y Postgres reales; el E2E exporter → control-api sigue pendiente de PL-C1 de Codex o de su stand-in. Los eventos meta `exporter.*` colisionan con el DTO `platform_event` de §24.2 hasta la siguiente revisión del contrato (discriminador `exporter_finding`, platform-contract 1.1.0); las formas de `payload` son supuestos del simulador hasta que Producto responda §32.6. Detalle en [ESTADO_IMPLEMENTACION_CLAUDE_2026-10-03.md](ESTADO_IMPLEMENTACION_CLAUDE_2026-10-03.md).

**Orden.** Arrancan en paralelo PL-L1, L2, L3 (y PL-C6, PL-C4). PL-C1 consume los vectores dorados de PL-L3; PL-C2 sigue a PL-C1; el E2E de PL-L6 sigue a PL-C1 o a su stand-in. No bloquea la demo mágica (que usa E0 y Core); es una segunda demostración, con datos que sí son el producto real.

### 32.5 Aceptación y pruebas de primer RED

| ID | Primer RED |
|---|---|
| PL-01 | La lectura de `login_accounts` se rechaza antes de cualquier consulta; la allow-list demuestra las tablas permitidas |
| PL-02 | Un `event_type` desconocido produce hallazgo contado y el lote se confirma |
| PL-03 | Un `sequence` saltado produce `gap_suspected` y solicitud de backfill |
| PL-04 | Un evento con `ingested_at` posterior al cierre de ventana dispara revisión |
| PL-05 | Un caso cerrado tras el corte aparece abierto en el extracto y sin `close_reason` |
| PL-06 | Un detector de herramientas contra este perfil devuelve `unsupported` nombrando `tool_call`; con perfil superconjunto 0.5.1 se habilita |
| PL-07 | Una cadena `previous_case_id` cuenta una vez; un cierre `customer_unresponsive` no cuenta como fracaso por defecto |
| PL-08 | `customers.simulator=true` queda excluido de poblaciones y marcado `team_generated` |
| PL-09 | Un incumplimiento de `sla_due_at` se mide con procedencia, sin lenguaje regulatorio |
| PL-10 | Un hallazgo de Fase 1 sin objetivo Core se detiene en `insufficient_*`/`waiting_dependency` y nunca llega a `publish` |

### 32.6 Preguntas abiertas para el equipo de producto (las releva el usuario, no el journal)

Hoja de ruta de datos de Fase 2 y si seguirá las entidades de `platform_history` 0.5.1; mecanismo de lectura (réplica, snapshot exportado o API con `after_sequence`); esquema de `payload` por `event_type`; contigüidad de `sequence` tras rollbacks y significado de `ingested_at`; futuro de `origin`/`topic`/`complaint_id` y mapeo de clientes al dataset bancario; captura prevista de hechos de capas IA, resolución y CSAT; marcador estable de filas demo; calendario y versionado de `teams` y de eventos nuevos; retención/redacción y si el dato puede llegar a modelos alojados.
