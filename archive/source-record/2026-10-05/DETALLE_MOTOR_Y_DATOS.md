# Motor híbrido, laboratorio de datos y versionado

Fecha: 2026-09-29. Estado: propuesta de implementación arquitectónica, no código ejecutado. Premisa confirmada: producto real del banco e histórico recopilado, no dataset de hackathon. Rust indicado por el usuario. Arquitectura lógica: ARQUITECTURA_PULSO.md; alcance: CONTEXTO_PULSO.md. Este documento concreta y reemplaza la restricción previa de investigación mediante consultas de negocio predefinidas.

## Motor híbrido

Un controlador Rust gobierna un workflow persistido con presupuesto, tiempo, cancelación, retries e inputs versionados. Tres carriles convergen en SignalCandidate:

1. Vigilancia recurrente: SQL/estadística para tasas, cohortes, ventanas, volumen, calidad de datos, secuencias y cobertura. Cálculo reproducible; baseline estacional y composición de casos declarados. No toda señal depende de un LLM ni toda anomalía requiere umbral rígido.
2. Descubrimiento semántico: Jev etiqueta aspectos acotados de textos y trazas con preguntas versionadas; LLM descubre temas no contemplados y propone hipótesis/taxonomías. Las nuevas categorías no se convierten automáticamente en verdad de catálogo.
3. Exploración abierta: investigador LLM formula preguntas, inspecciona esquema y ejecuta SQL libre dentro de un laboratorio autorizado; puede crear tablas temporales, joins y features derivadas. No espera siempre a que una alerta predefinida lo active: también corre por agenda y por nuevas fuentes, con presupuesto de exploración.

Investigador recibe material semántico/negocio y un snapshot, no una lista de recetas de negocio. Controlador ejecuta y registra las consultas, no deja que el LLM invente resultados. Hallazgos incluyen SQL, parámetros, hashes de entradas/resultados, universo, denominadores, contraejemplos y limitaciones.

Jev: juicios cerrados como tipo de acción, presencia de explicación, suficiencia de una evidencia acotada o elegibilidad semántica. No sintetiza SQL, procedimientos abiertos ni hace aritmética. LLM: preguntas abiertas, SQL, hipótesis, agrupaciones nuevas, análisis de contraejemplos y propuestas. Rust/SQL: joins, ventanas, cálculos, permisos, límites, gates y transiciones. Scoring semántico no sustituye verificación de éxito.

Descubrimiento exploratorio -> validación en periodo/cohorte reservada -> especificación versionada de detector. El sistema puede promover una consulta descubierta a monitor reproducible, después de pruebas de semántica, costo y estabilidad. Guardar intentos fallidos y controlar búsqueda múltiple: explorar cientos de segmentos produce aparentes hallazgos por azar. Validación independiente no consultada durante descubrimiento, tamaños mínimos y corrección estadística cuando aplique. Derivas tardías de datos disparan nueva ejecución, no reescriben el run anterior.

## Laboratorio desechable

Data broker confiable extrae snapshot autorizado del histórico, trata identificadores/textos y crea un manifiesto. Investigador nunca recibe credenciales de producción ni tabla de correspondencia. Claves pseudónimas consistentes en el ámbito autorizado permiten joins; no llamarlas anonimización irreversible. Resolver autorización de propósito y alcance antes de materializar, no después de consultar.

Contrato ExplorationWorkspace: workspace_id, purpose, access_scope, snapshot_manifest_hash, treatment_policy_version, schema/dictionary, allowed_files, resource_budget, expiry, model_egress_policy y engine_version. Permite exploration SQL genérico y lectura de esquema; no catálogo rígido de queries de negocio.

Propuesta: DuckDB para exploración analítica; SQLite posible para ledger/index local inicial. Son roles distintos y no implican usar ambos sin necesidad. Motor SQL de datos no corre incrustado en proceso privilegiado del controlador: worker en aislamiento OS/contenedor, no root, sin red/credenciales, filesystem limitado y quotas de CPU/RAM/disco/tiempo/output. Configuración de seguridad del motor fijada por launcher y extensiones solo preaprobadas. Snapshot lógico inmutable más espacio de derivación escribible; impedir modificación de base usando separación/verificación, no solo un prompt. SQL libre no significa filesystem ni carga de extensiones libres.

Se pueden materializar tablas dentro de la base de trabajo. Disabling external access exige precargar datos o configurar explícitamente rutas autorizadas; no asumir que Parquet seguirá legible con todo acceso externo deshabilitado. No aceptar filtros regex de SQL como defensa suficiente. Si hay ejecución de código en el futuro, usar un sandbox adicional, no shell del host.

El broker de modelos está fuera del worker sin red. Solo envía material autorizado según política de proveedor/país/propósito; autorización humana cuando corresponda. Minimizar/redactar resultados y controlar salida; análisis combinados y grupos pequeños pueden reidentificar incluso sin nombres. Controles de privacidad no se reducen a masking ni a un Noul. Texto y logs del banco son datos no confiables, no instrucciones para el agente.

Al finalizar o expirar: preservar solo evidencia autorizada, consultas y manifiestos necesarios; destruir copias temporales con política verificable y atender crash/recovery. Retención incluye caches, spill, logs y artefactos derivados. La privacidad puede impedir reproducir un resultado después de eliminar las fuentes; conservar trazabilidad no promete replay eterno.

## Artefactos inmutables y proyecciones

JSON canónico validado para manifiestos/contratos; YAML opcional para autoría humana y compilado a representación canónica. Parquet/blob binario para grandes datos; no serializar histórico completo como JSON. Mantener cantidades monetarias como decimales exactos/currency o unidades menores, no float ambiguo. Definir esquema, normalización, orden y timestamps antes de hashear.

ArtifactManifest: kind, schema_version, logical_id, revision, parent_refs, payload_hash, input_refs, producer_version, policy_refs, provenance. Contenido identificado por digest criptográfico (p.ej. SHA-256). Referencias construyen un grafo de dependencias verificable. Separar identidad lógica, revisión, digest y registro de ejecución/fecha: mismo payload puede pertenecer a ejecuciones distintas.

Blobs create-only para aplicación, verificación de hash en lectura, publicación atómica y ledger de eventos append-only. Hash detecta cambios; no evita borrado, no demuestra autoría ni anonimiza. Permisos, almacenamiento, backups y cuando sea necesario firmas/retención protegida dan garantías adicionales. No definir WORM eterno para evidencia personal; inmutabilidad de versión lógica coexiste con retención, revocación y eliminación controlada. Tombstones conservan razón/referencia no sensible, no el contenido eliminado.

Metadatos relacionales e índices son proyecciones mutables reconstruibles; no todo debe ser blob. ActiveReleaseChanged y decisiones de workflow se agregan al ledger; un índice current apunta al release y se actualiza con comparación de revisión para concurrencia. Revertir crea nuevo evento, no borra historia. Escribir blob y ledger no es una transacción distribuida automática: primero persistir/verificar blob, luego commit metadata/event; huérfanos se manejan mediante política de mantenimiento. No referenciar blob parcial/no disponible.

## Cache por dependencias

Key: scope de autorización/tenant/partición, policy_version, input hashes incluyendo revisión/manifiesto de derivaciones del workspace, transformación/consulta exacta y parámetros, engine/producer/model/prompt/questions versions y config. Snapshot o estado derivado nuevo produce nueva key; mutaciones no se cachean como lecturas y se ejecutan con operación idempotente o subworkspace nuevo. Revocación se aplica aun ante hit. Consultas no deterministas/desordenadas no tienen reproducibilidad garantizada: fijar semántica/orden o no cachear como equivalentes. SPEC_DETECCION_AUTOMEJORA.md concreta este comportamiento y tiene precedencia en contratos de ejecución.

Cachear snapshots autorizados, features, consultas repetidas, etiquetas Jev y llamadas LLM según política. Cache de respuesta LLM evita repetir una respuesta previa; no prueba determinismo del proveedor. Evaluación fresca tiene execution_id, cache_policy y registro de hits; no reutilizar resultado final para aparentar un nuevo ensayo. TTL y eliminación por retención. No reutilizar cache entre tenants por coincidencia de hash.

## Rust y contratos

Rust como núcleo: tipos/enums de payload, capa y estados; IDs/digests diferenciados; constructors que validan contratos; autorización necesaria en operaciones privilegiadas; procesos aislados para motor SQL y adapters. Entrada externa deserializada no equivale a dominio válido: validar timestamps, unidades, relaciones y condiciones. ValidatedCandidate no es PublishedRelease.

Rust reduce clases de fallos de memoria/tipos, no errores de dominio, SQL indebido, sesgo, fuga de datos ni fallos de dependencias FFI. Minimizar unsafe propio y probar límites de engine/bindings; compilación no sustituye revisión, tests y sandbox.

Los tres primeros contratos se amplían:

- ServiceEvent: fuente, happened_at/ingested_at, payload enum, capa/versión, clasificación de datos y refs de evidencia; faltantes explícitos.
- OutcomeObservation: dimensión y valor/unknown, método de verificación, ventana/cobertura/censura, policy/oracle refs y evidencia.
- CapabilitySnapshot: hash/versiones exactas de árbol/agentes/skills/tools, elegibilidad, contratos, permisos, dependencias y cobertura conocida/desconocida.

Fuentes oficiales de verificación técnica:

- https://duckdb.org/docs/current/operations_manual/securing_duckdb/overview
- https://duckdb.org/docs/current/operations_manual/securing_duckdb/securing_extensions
- https://www.sqlite.org/c3ref/set_authorizer.html
- https://www.rfc-editor.org/rfc/rfc8785
- https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html
- https://docs.typesafe.ai/primitives
