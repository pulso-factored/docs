# Pulso — análisis de producto desde los diseños locales

Estado: alineación documental concluida para revisión y aprobación del usuario; implementación no iniciada. Fecha: 2026-10-01. La ejecución visual local de HTML sigue limitada por frames vacíos, sin atribuir causa; la cobertura de contenido/handlers se sustenta en inspección completa de fuentes y revisión visual del PDF, no en prueba funcional del prototipo.

## Objetivo y evidencia

Comprender cada archivo, pantalla, rol y comportamiento de `design/`; contrastar después el spec vigente con el producto integral, sin convertir nuestro servicio de detección/automejora en otra plataforma aislada ni implementar las responsabilidades de atención de F7/F8.

Fuentes actuales: seis HTML de Plataforma de Contact Center (sin sufijo, 1, 2, 3, 4, 5) y un PDF de 21 páginas, 1080×675 puntos. Los sufijos no prueban cronología ni prioridad; hasta comparar contenidos no se asume cuál sustituye a cuál. Archivos originales permanecen inalterados. Texto y render PDF temporales están en `tmp/design-review/`, no constituyen contratos ni nuevos datos de negocio.

## Método y gates

1. Inventario por archivo: pantallas, identificadores, roles, navegación, estados visibles, interacciones y contenido embebido; separar contenido funcional de dependencias del bundler.
2. Revisión independiente por pares de HTML, con notas trazables; revisión principal del PDF y comparación transversal.
3. Segunda pasada: recorrer las experiencias y diferencias; identificar acciones implementadas frente a placeholders, supuestos numéricos, contradicciones y fallos/estados ausentes.
4. Mapa producto→plataforma/Agent Core/automejora→contratos y eventos→secciones y unidades del spec. Diferenciar observación del diseño, interpretación y decisión propuesta.
5. Actualización del spec por conjuntos de secciones, preservando consistencia entre dominio, datos, APIs, UX, seguridad, evaluación, operación y DAG.
6. Revisión adversarial independiente y pasada inversa spec→pantalla→contrato→UC/test. Validación estructural no acredita implementabilidad ni comportamiento.

## Primeras observaciones del PDF

Las primeras páginas muestran workspace de analista con lista de contactos priorizada, conversación, acciones verificadas y paneles Copiloto/Herramientas/Cliente; hay cambio de rol entre analista, supervisora, automatización y administración. El copiloto diferencia borrador revisable de envío al cliente; una consulta recurrente aparece como herramienta reutilizable. Esto aporta una fuente potencial de evidencia para automejora, pero frecuencia no basta para autorizar creación/publicación de tools ni acceso a datos.

Se renderizaron e inspeccionaron visualmente las 21 páginas. No se toman cifras, reglas ni etiquetas ilustrativas como resultados observados del dataset. El PDF corresponde al workspace de atención, no a todas las experiencias de automejora; no sustituye los HTML restantes.

| Páginas PDF | Pantalla/estado observado | Consecuencia para integración y evaluación |
|---|---|---|
| 1–2 | Workspace/copiloto y borrador revisable | Distinguir sugerencia, edición, envío y efecto confirmado; preservar provenance de consulta sin texto/SQL crudo en telemetría |
| 3 | Herramientas hechas/acciones/consultas; consulta recurrente convertida en herramienta | Propuesta de tool derivada de uso, no sólo nuevo agente; separar permisos de lectura y acciones mutables |
| 4–5 | Contexto cliente y recorrido clasificador→árbol→agente→humano | Recorrido real por intento/capa; mitigación no equivale a cierre; lectura auditada por componente |
| 6 | Lista colapsada | Estado de UI, sin efecto en asignación/evidencia de atención |
| 7 | Caso sin cargo reciente, mensajes repetidos y demora | Ausencia de matching no prueba inexistencia; señal potencial de frustración/demora, necesita timestamps y cobertura |
| 8–9 | Vacío y pausa de disponibilidad | Cero casos no significa ingesta completa; pausa evita nuevos contactos pero conserva existentes, responsabilidad plataforma |
| 10 | Cierre resuelto/sin resolver, motivo, seguimiento y encuesta | Cierre operativo distinto de solución y outcome bancario; encuesta solicitada no es respuesta ni satisfacción |
| 11 | Fallo de enviar estado, retry y canal alterno | Intento/error/entrega separadas, idempotencia multicanal; no contar click como notificación recibida |
| 12–13 | Identidad parcial/completa, confirmación de tenencia y siguiente paso | Resultado de identidad distinto de consentimiento/declaración sobre tarjeta; no exponer respuestas gold a modelo/analista |
| 14–15 | Solicitud de abono sobre autoridad personal y espera de supervisora | Aprobación financiera de caso es plataforma, nunca Approval de Registry; deadline/reasignación de autoridad con eventos |
| 16–17 | Aprobado y efecto confirmado versus rechazado y disputa continúa | Aprobación sola no acredita aplicación; rechazo no es necesariamente mala atención ni error |
| 18–19 | Llamada entrante, transcripción y hold | Turnos parciales/finales, tiempo en cola/hold vs tiempo activo; identidad de canal no autoriza abono |
| 20 | Llamada saliente por regulador, identidad incompleta y firma supervisora | Origen≠canal/dirección; política dependiente del canal; conservar datos mínimos de authority sin ejecutar finanzas en motor |
| 21 | Correo sin sesión, preguntas en borrador y respuesta simulada | Asincronía y no respuesta; «simular» es evidencia de test, nunca historia real |

**Ambigüedades a resolver en el contrato, no copiar como implementación:** PDF p20/p21 muestran consultas o contexto de cuenta al mismo tiempo que exigen identidad antes de hablar de cuenta; habrá que distinguir acceso interno autorizado del asesor y exposición al cliente, y validar ambos por scope. p10 ofrece texto de solución definitiva mientras selecciona sin resolver: cierre y descripción humana no son gold fiable. p14 aparece `fraud_score` y autoridad monetaria: disponibilidad real debe cotejarse con fuentes, no inferirse del mock. PDF muestra árbol y un agente, no demuestra las dos capas AI diferenciadas; se necesita representación compatible con cuatro capas sin reescribir producto por suposición.

## Registro de cobertura

| Fuente | Responsable primera pasada | Estado |
|---|---|---|
| HTML sin sufijo y (1) | design_a | 9+15 boards inspeccionados; notas A; ronda cruzada en curso |
| HTML (2) y (3) | design_b | 8+8 boards inspeccionados; notas B; ronda cruzada en curso |
| HTML (4) y (5) | design_c | 4+8 boards inspeccionados; notas C; ronda cruzada en curso |
| PDF 21 páginas y mapa transversal | principal | 21/21 inspeccionadas; cruce HTML pendiente |

## Primera adaptación técnica (parcial)

V2 §24.1 incorpora journey y distinción de estados/autoridades/scope con evidencia del PDF y notas de administración/app en [ANALISIS_DESIGN_C.md](ANALISIS_DESIGN_C.md). Permisos, política y retención son fronteras externas; los campos nuevos de observación no se agregan al dataset original. Asignación a unidades existentes y tests negativos explícitos. Pendiente cruzar automatización/supervisión/login y auditar consistencia con todos los contratos; esta adaptación no cierra la investigación.

## Segunda pasada cruzada y contrato de producto

Los tres revisores cruzaron notas ajenas y conjuntos de secciones del spec; findings en sus rondas2. V2 §20.1 materializa rutas/DTOs/comandos async de panorama, oportunidad, comparación, trial, readiness, feedback y decisión, autenticación y separación de fuentes/métricas; §24.2 separa eventos propios de plataforma de EngineEvent, revocación vigente frente a policy pin, retención y ToolDef frente a executor. §21 reconcilia lectura libre con transporte por executor general de Core. No se crean tablas/microservicios por pantalla; controles sin soporte se muestran unavailable.

Pendiente auditoría inversa de todos los conjuntos de secciones y revisión final independiente de estos nuevos contratos, además de comprobación visual de los HTML cuyos frames no renderizaron. No se presenta la especificación como aprobada ni software implementado.

## Mapa por conjuntos de secciones para auditoría inversa

Este mapa orienta la revisión, no acredita cierre por tener una fila. La evidencia específica y los findings deben quedar en notas de cada ronda.

| Secciones V2 | Producto que debe reflejar | Ajuste o invariante a comprobar |
|---|---|---|
| 1–2 | Plataforma integral, automatización y agentes/árbol | Motor parte del producto, no atención paralela; output heterogéneo; UI tres categorías no elimina AI1/AI2 |
| 3–6 | Contexto de cliente, acceso/admin y política | Dataset inmutable, fuentes separadas, ámbitos/grants, snapshot no es historia, policy pin no evita revocación |
| 7 | Detección→investigación→propuesta→evaluación→release | Autónomo aunque usuario no abra insight; pruebas humanas opcionales; feedback no impone respuesta ganadora |
| 8–10 | Progreso/colas/errores y operación | Backpressure por lane, latencia/inactividad visible, o11y durable vs spans; no construir asignación bancaria |
| 11–15 | Historias, pruebas y readiness | Los nuevos escenarios deben adscribirse a cortes y tests; acceptance no meramente screenshot |
| 16–19 | Comparación y efectos de propuestas | Bridge/outcome explícito, mitigación/handoff adecuados, ToolDef sin executor bloqueada, atomicidad y unknown |
| 20 | Panorama/expediente/propuesta/sandbox/aprobar | §20.1 contratos producto precisos; scopes, async/status, métrica/provenance y prohibición de final leakage |
| 21 | Aprendizaje y conocimiento/documentación base | Wiki interna libre vía executor general, publish gobernado y olvido; distinta de knowledge de atención |
| 22–23 | Recorrido E2E y provider real | Fronteras plataforma/Core/engine; autenticación UI no keys de proveedor; reason summaries sin chain-of-thought |
| 24 | Workspace, supervisión/audit, app/admin | §24.1/24.2 journey, fuentes tipadas y tres autoridades; no fabricar EngineEvent humano |
| 25–26 | Debug y documentación | UI producto no consola debug; access/export/raw por objeto; documentación y bitácora trazables |
| 27–29 | Crear artefactos/catálogo/versiones y uso Core | Endpoints/capacidades fijados, no convertir selector exposure en canary; JWS/roles y tareas internas compatibles |
| 30 | Trabajo realizable por equipo | API/DTOs/tests nuevos en unidades existentes sin barrera global; dependencias adicionales reales deben corregir DAG |

Rondas3–4: implementadores/revisores backend/frontend, AI/eval/Core y data/infra/security contrastaron contratos nuevos con conjuntos anteriores. Los hallazgos se resolvieron mediante §20.2 y sustituciones de rutas, estados ledger, input de ingesta, nulabilidad, lectura Core, policy y reloj E0. No fue necesario cambiar arquitectura ni añadir tablas/servicios.

## Cierre y límites de la evidencia

| Requisito de la tarea | Evidencia inspeccionada |
|---|---|
| Entender todos los archivos/pantallas | 52 boards con IDs/templates/handlers en notas A/B/C; PDF21 inspeccionado; script readonly reproduce inventario |
| Análisis durable y bitácora | Este documento, notas independientes A/B/C y entradas sucesivas BITACORA_PULSO |
| Agentes paralelos y revisiones cruzadas/adversariales | Cuatro rondas con pares de archivos, cruces de dominios, contratos nuevos y auditoría inversa por conjuntos; notas y veredictos de cada revisor |
| Integrar motor en producto integral | V2 §§1,15,20.1/20.2,21,24/24.1/24.2; tres autoridades separadas, journeys, proyecciones, eventos y outputs Core compatibles |
| Detalle implementable y pruebas | Rutas/DTOs, CommandRef/status, targets, TrialPlan/readback/turns, auth/JWS/reauth, feedback, permisos/retención, availability/provenance y tests adscritos a unidades existentes |
| Consistencia de planificación | Validadores Markdown/DAG ejecutados tras cambios; 46 unidades sin nuevas dependencias artificiales de UI/producto |

Veredicto de ronda4: los revisores no exigen rediseño y consideran implementable por cortes TDD tras fixes puntuales, ya incorporados: rutas canónicas, mapping de ledger, target agent_ref/digest interno y replay availability. No se afirma «API compilada» ni producto funcionando: schemas/fixtures y todas las pruebas de runtime son entregables de implementación, condicionados a aprobación. Upstream no aporta canary, knowledge publication ni autoridad financiera por estos diseños; dependencies permanecen visibles y fuera de éxitos ficticios.

Notas anteriores que dicen «pendiente» son el registro de pasadas previas, no el estado vigente. Limitación abierta no bloqueante del análisis: los HTML exportados no renderizaron frames en la comprobación local; no se validó accesibilidad/responsividad/interacción real ni se alteraron originales. La implementación deberá validar sus propios consumidores/UX bajo contratos; este trabajo fue de especificación, no reparación del export ni construcción de F7/F8.

Las notas de agentes son evidencia de trabajo, no contratos aprobados. La síntesis y resolución de diferencias se incorporarán aquí antes de declarar lista la alineación.

## Inventario consolidado de experiencias

52 boards HTML (estados/presets incluidos), no 52 features independientes. Base: recorrido demo de cliente/analista/panorama/propuesta/prueba/activación/catálogo/ficha. (1): acceso y errores de backoffice, app y web. (2): supervisión/colas/autoridades/auditoría. (3): automatización/panorama/árbol/catálogo/ficha/propuesta/prueba/activación. (4): administración de personas/roles, herramientas/permisos, políticas y retención. (5): app cliente, movimientos/contexto de transacción/productos/soporte/seguimiento. Las coincidencias base/(3) son vistas compartidas, no evidencia de evolución cronológica.

Notas completas: [A](ANALISIS_DESIGN_A.md), [B](ANALISIS_DESIGN_B.md), [C](ANALISIS_DESIGN_C.md). Inventario reproducible readonly: `python docs/validation/Inspect-Design.py`, que decodifica manifest y títulos sin ejecutar scripts. La lógica anidada fue inspeccionada por revisores; listar títulos no acredita revisión de handlers.

**Comprobación local del HTML (3):** servido por HTTP localhost, navegador muestra títulos de ocho boards pero sus frames quedan vacíos en la observación; no se obtuvo error de consola. No se atribuye una causa sin evidencia y no se modifican originales. La revisión de fuente y PDF sigue disponible; falta verificar visualmente los otros dominios HTML o una representación equivalente local de sus templates. Este inconveniente de exportación no es prueba de fallo del producto.
