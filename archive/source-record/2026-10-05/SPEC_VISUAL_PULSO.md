# Pulso detección y automejora

## Guía de arquitectura y construcción

Pulso debe encontrar dónde falla o se queda corta la atención del banco, explicar qué sabemos de ese problema y proponer cambios que podamos probar antes de utilizarlos. El resultado no es solamente un agente más rápido. Es un servicio que puede ampliar su cobertura, corregir errores y reutilizar procedimientos útiles, conservando evidencia de cada decisión.

Este documento explica el sistema desde la experiencia hasta los mecanismos de implementación. Comenzamos con las piezas y un caso completo; después detallamos datos, decisiones, construcción de propuestas, pruebas y operación. Las palabras técnicas se definen antes de usarlas. Los ejemplos son ilustrativos y las elecciones de implementación son propuestas, no decisiones aprobadas ni resultados del banco.

Diseñamos para el histórico y la operación de un banco real. No suponemos acceso efectivo a esas fuentes. El framework que construye y ejecuta los agentes tiene una frontera propia: aquí definimos cómo pedirle candidatos, observarlos, evaluarlos y controlar sus versiones, no su implementación interna.

La arquitectura mantiene un núcleo Rust, exploración analítica libre dentro de bases desechables y artefactos versionados. Los modelos interpretan o proponen; el código comprueba datos, permisos, cálculos y efectos. Una simulación sirve para validar el mecanismo, pero no prueba ahorro, resolución ni seguridad productiva.

@diagram overview

La figura resume tres trabajos diferentes. Atención resuelve casos con capacidades estables. Evolución descubre y prueba mejoras sin tocar directamente cuentas o transacciones. Control registra decisiones y autoriza efectos concretos. Un incidente crítico tiene un camino de protección separado, para no esperar una investigación generativa.

## 1 Cómo leer la especificación

Si buscas entender el producto, lee las secciones 2 a 5 y el recorrido final. Si quieres construir el núcleo, continúa con datos, investigación, propuestas y evaluación. Las secciones de operación explican las garantías que deben verificarse antes de usar integraciones reales.

Las secciones 2 a 22 explican funcionamiento, interacciones y límites. Las secciones 23 a 26 forman la segunda parte: cómo implementar investigación y SQL, procedimientos, oráculos, cobertura y decisiones. Puedes profundizar en ellas desde los capítulos correspondientes sin memorizar todos los contratos al comenzar.

Llamamos contrato al acuerdo de entrada, salida y comportamiento entre dos componentes. No es solamente un objeto JSON: también explica qué ocurre con información faltante, un timeout o un intento repetido. Un puerto es la interfaz que permite reemplazar una integración real por un adaptador de prueba sin cambiar las reglas del dominio.

| Concepto | Qué representa | Qué no demuestra |
| Señal | Observación que merece investigación | Una causa o una solución correcta |
| Episodio | Un problema del cliente a través de varias interacciones | Que todo lo ocurrido cerca en el tiempo tenga la misma causa |
| Oportunidad | Expediente estable de un problema o mejora posible | Que deba automatizarse |
| Propuesta | Una intervención concreta y sus supuestos | Que ya exista un agente ejecutable |
| Candidato | Una versión preparada para una evaluación definida | Que esté autorizada para producción |
| Evaluación | Ensayo con entradas y versiones fijadas | Eficacia universal o beneficio realizado |
| Release | Aplicación de una versión a un alcance autorizado | Que el problema haya desaparecido |

Un snapshot es una fotografía de datos elegidos según una fecha de corte y una regla de resolución. Una revisión es una nueva versión lógica; no sobrescribe la anterior. Un hash identifica contenido y permite detectar modificaciones. No concede permisos ni demuestra quién lo produjo.

Los términos baseline, shadow y canary significan, respectivamente, versión de referencia, ejecución sin efectos reales y exposición gradual autorizada. Un oráculo de pruebas es una comprobación independiente del resultado esperado; no una impresión de que el cliente parece satisfecho.

## 2 Qué experimenta cada persona

El cliente del banco sigue un servicio continuo. Su consulta se clasifica; el sistema intenta resolverla con la capacidad apropiada y conserva lo que ya se verificó cuando escala. El cliente no ve una investigación interna ni necesita comprender las capas.

El equipo del banco sí necesita comprender el descubrimiento. Su punto de entrada es una bandeja de oportunidades, decisiones relevantes e incidentes. Cada elemento explica qué ocurre, a quién afecta, qué evidencia existe y qué intervención necesita. No es una cola para aprobar cada paso del motor.

@diagram experience

El expediente mantiene la continuidad. Desde allí el responsable puede pedir contraejemplos, cuestionar una explicación, comparar alternativas o revisar una propuesta. Al abrir una traza o la ficha de una tool, debe poder volver a la misma comparación y revisión. Una actualización automática no borra un borrador humano.

Las responsabilidades son distintas: negocio prioriza, el analista contrasta evidencia, el experto de atención aporta contexto, el diseñador revisa capacidades, riesgo y calidad aplican criterios y operación supervisa releases. Una persona puede reunir varias funciones; asignarle una oportunidad no le concede acceso a todas sus conversaciones o datos.

Una pregunta como «¿puede explicarse por una caída del canal?» es una hipótesis atribuida. El sistema puede investigarla dentro de su ámbito autorizado y mostrar progreso. «Se ve bien» no es permiso para publicar. Una autorización requiere una versión, una acción y un alcance inequívocos, independientemente de si se expresa mediante chat o un botón.

## 3 Arquitectura con responsabilidades claras

Proponemos una aplicación modular Rust para la API y el control del trabajo, con workers aislados para consultas y evaluación. Modular no significa desplegar un microservicio por cada caja. Sí significa que el LLM no puede escribir directamente en el registro de decisiones ni activar releases.

@diagram architecture

Ingesta adapta fuentes y valida registros. Evidencia materializa snapshots, conserva procedencia y deriva episodios y resultados. Discovery organiza misiones, monitores y exploración abierta. Oportunidades publica afirmaciones y alternativas en el expediente. Evaluación ejecuta comparaciones. Gobierno aplica permisos y criterios. Operación reconcilia efectos con el framework.

El catálogo conecta estos módulos con árboles, agentes, equipos, conocimiento, skills y tools. Guarda identidades y versiones exactas, elegibilidad, permisos, dependencias y evidencia de cobertura. «Esta capacidad dice que resuelve pagos» y «esta versión pasó estos escenarios» son afirmaciones diferentes.

En el primer entorno proponemos un controlador escritor sobre metadata SQLite local, blobs para contenido y DuckDB por laboratorio analítico. Los workers usan puertos del controlador; no abren el archivo SQLite desde varios hosts. Si throughput, concurrencia o disponibilidad exigen otro almacenamiento, cambia el adaptador de metadata, no el significado de oportunidad o decisión.

Atención debe continuar con versiones previamente activas aunque la investigación esté temporalmente detenida. Los mecanismos de contención independientes solo se consideran disponibles cuando el framework o el control de routing los implementan y se han verificado.

## 4 Un recorrido completo antes de los detalles

Imaginemos contactos por operaciones pendientes. El motor encuentra recontactos y eventos digitales relacionados. Eso no demuestra todavía que la demora los causó. Construye un expediente, muestra el universo observado y busca explicaciones competidoras: caída de canal, comunicación incompleta o un cambio de mezcla de productos.

@diagram journey

El responsable pregunta por una caída del canal. El sistema registra esa hipótesis, investiga una fotografía autorizada y produce una nueva revisión. La anterior sigue disponible. Si aparecen contraejemplos, puede acotar o refutar su explicación en lugar de defenderla.

Una alternativa podría ampliar el árbol para explicar estados y escalar excepciones. Otra podría mejorar una skill utilizada por IA2. Una tercera es no cambiar atención si el verdadero problema pertenece al core bancario. Una tool que solo consulta el estado no permite prometer que se reparará una transacción.

La propuesta que avance según política o decisión humana se prepara mediante el mismo framework. Después se compara con la versión actual usando escenarios y comprobaciones independientes. Solo una decisión autorizada permite avanzar a la etapa definida. El expediente continúa después: muestra exposición, errores, resultados observados y qué supuestos siguen sin verificarse.

Una vuelta ilustrativa de aprendizaje: el árbol falla en un caso de desarrollo con estado contradictorio y explica la operación sin escalar. Se conserva como regresión; el planner propone una revisión con handoff explícito, el framework prepara otro candidato y se repiten las pruebas aplicables. La versión estable no cambia durante esa iteración. Si no mejora o agota rondas, queda bloqueado o inconcluso. No estamos revelando un caso final reservado.

La alternativa de skill podría preferirse si cubre suficientes casos con menor integración y riesgo. El menor costo por interacción que promete el árbol no basta para que gane: también cuentan cobertura, excepciones y esfuerzo.

## 5 Atención estable y aprendizaje fuera del camino crítico

La clasificación es la puerta de entrada, no una quinta capa. Después existen cuatro capas: árbol determinista especializado, agente IA1 basado en decisiones Jev, agente IA2 generativo y humano. Una regla de seguridad puede saltar directamente a una capa apropiada; no se obliga a recorrerlas todas.

@diagram layers

El árbol se construye e itera fuera del camino de atención. Durante ejecución usa condiciones y acciones tipadas. IA1 combina juicios acotados de Jev con estado y tools del framework. IA2 admite razonamiento y generación abierta bajo sus límites. El humano recibe contexto, verificación aplicable y operaciones pendientes.

HandoffContext define esa transferencia: episodio e interacción, versiones utilizadas, motivo de escalamiento, hechos verificados con evidencia, preguntas respondidas, pendientes, operaciones externas y vista autorizada del destinatario. La autenticación lleva vigencia y aplicabilidad; no se copia un booleano «verificado» entre cualquier canal y acción.

Si una tool tiene resultado desconocido, el siguiente agente ve la operación y consulta su estado antes de repetirla. Un cambio de versión no debería desarmar un episodio en curso; una contención crítica puede reencaminarlo con una política explícita y dejando historial.

## 6 De las fuentes a una fotografía utilizable

Las entradas posibles incluyen contactos y PQR, clientes y productos, transacciones y eventos digitales, información de canales, trazas de agentes y humanos, encuestas, políticas y versiones del catálogo. Cada adaptador declara qué campos realmente tiene. Un registro histórico de cierre no permite inventar mensajes ni acciones del asesor.

@diagram sources

SourceRecordVersion identifica fuente, registro, revisión, hash y tipo de cambio. Si llega otra vez el mismo contenido, es un duplicado idempotente. Si llega el mismo registro y revisión con contenido diferente, se registra conflicto y cuarentena. No gana arbitrariamente el último recibido.

SnapshotResolutionSpec define el corte de ingesta y de negocio, la precedencia de revisiones, borrados y versión de esquema. La vista analítica contiene una versión resuelta por identidad lógica. El historial completo vive aparte. Una corrección retroactiva produce una fotografía nueva; no modifica lo que vio una investigación anterior.

El manifiesto registra fuentes, diccionario, tratamiento, cobertura, conteos excluidos y datos en cuarentena. Los identificadores pseudónimos permiten joins dentro del ámbito autorizado, pero no constituyen anonimización irreversible. Credenciales de producción y mapas de identificación no entran en el laboratorio.

La autorización se verifica por propósito, usuario o servicio, ámbito, partición y política vigente. Etiquetar un blob con el tenant correcto no basta: también se revisa su procedencia real. Si una fuente falta o no es observable, el dato queda desconocido, no se convierte en cero.

## 7 Modelar interacciones episodios y resultados

ServiceEvent conserva identidad de fuente, fecha ocurrida y fecha ingerida, actor, capa, versión ejecutada, interacción, payload tipado y evidencia. Una invocación de tool tiene un identificador que conecta solicitud y resultado. Error, éxito técnico y resultado desconocido son diferentes.

@diagram entities

Una Interaction representa una sesión. EpisodeRevision agrupa interacciones y hechos relacionados con un problema. Cada membresía guarda método y evidencia de vínculo: exacto, inferido o ambiguo. Cliente y proximidad temporal no bastan para fusionar problemas. Los monitores declaran qué tipos de vínculo aceptan y cómo cambia el resultado al excluir inferencias.

OutcomeObservation separa objetivo del cliente verificado, ejecución técnica, cierre administrativo, satisfacción, recontacto y costo. No deduce resolución del cierre ni de una respuesta amable. Para ausencia de recontacto se necesita una ventana completa y cobertura de canales; si faltan observaciones, el resultado está censurado o es desconocido.

Las relaciones del diagrama son conceptuales. Una interacción puede participar en una reconstrucción revisada; esas membresías no significan que una llave demuestre causalidad. Las métricas siempre referencian una revisión del episodio y de su población.

## 8 Cómo decide cuándo y qué investigar

ExplorationMission define un objetivo continuo, datos y capacidades autorizados, disparadores, cadencia, prioridades, presupuesto y autonomía. Puede buscar automatización desaprovechada, nuevos motivos, fallos de herramientas o conocimiento insuficiente. No se limita a dos temas conocidos.

@diagram hybrid

La agenda recibe nuevas fuentes, resultados de seguimiento maduros, cambios de capacidades, fallos de evaluación y solicitudes humanas. Consolida disparadores repetidos y reserva recursos antes de ejecutar. Un run fija las versiones de entrada: cambiar datos durante la ejecución no actualiza silenciosamente su significado.

Los monitores numéricos son consultas y reglas versionadas. Jev etiqueta atributos semánticos cerrados. El investigador LLM explora preguntas abiertas, escribe SQL y contrasta hipótesis. Los tres producen candidatos de señal; ninguno necesita que la persona dirija cada paso.

La agenda conserva espacio para explorar cosas nuevas y evita repetir la misma hipótesis sin nueva información. Los límites incluyen tiempo, consultas, tokens, costo, CPU y salida. Agotar presupuesto conserva el avance y puede suspender el trabajo; no demuestra que una hipótesis sea falsa.

## 9 Quién hace cada decisión

| Trabajo | Mecanismo propuesto | Por qué |
| Cálculos ventanas joins permisos estados | Rust y SQL | Deben ejecutarse y comprobarse con reglas explícitas |
| Motivo conocido atributo de texto juicio puntual | Jev | Respuesta acotada a opciones o criterios versionados |
| Tema nuevo hipótesis SQL alternativas abiertas | LLM | Requiere exploración y construcción de nuevas posibilidades |
| Diseño de árbol agente o equipo | LLM y framework | El modelo propone y el framework valida y prepara |
| Objetivo del caso efectos seguridad | Oráculo y reglas | Se comprueba estado o acción no una impresión lingüística |
| Cliente adversarial | LLM aislado | Simula conversación sin recibir secretos del soporte |
| Gate promoción y contención | Rust y política autorizada | Una probabilidad no concede autoridad |

Jev ofrece Choice para elegir opciones, Score para una rúbrica y Noul para una condición. Choice y Score incluyen confidence; Noul no tiene confidence separado. Las preguntas de una petición son independientes; una respuesta no alimenta a otra sin una composición explícita en código.

No usamos Jev para inventar SQL, calcular tasas o diseñar procedimientos abiertos. Su confianza tampoco equivale a exactitud empírica. Preguntas, modelo, configuración y resultados se versionan; se necesita evaluar desempeño por idioma y tarea. Unknown o abstención son resultados legítimos.

El LLM no ejecuta libremente herramientas del banco. Produce solicitudes tipadas a brokers autorizados. Un JSON válido tampoco es una decisión válida de dominio: Rust comprueba referencias, restricciones y autoridad antes de materializar un efecto.

## 10 Cómo se ejecuta la investigación

El investigador recibe un objetivo, un diccionario, cobertura y datos tratados dentro de un workspace. Puede inspeccionar esquema, ejecutar SQL libre, crear derivaciones y buscar contraejemplos. La libertad está en las preguntas y el análisis; no en acceder a red, archivos del host o credenciales.

@diagram research

El controlador presenta cada resultado real mediante QueryReceipt: SQL y parámetros, versiones, columnas, conteos, hash del resultado, límites y errores. Un resultado truncado no demuestra ausencia en todo el universo. Un receipt demuestra qué se ejecutó, no que el razonamiento de negocio sea correcto.

ReadQuery consulta un estado fijo. DerivationCommand cambia el workspace mediante una operación explícita; registra revisión, dependencias y manifiesto. Una tabla temporal modificada cambia la clave de caché. Si el workspace desaparece, se reconstruye desde sus entradas o falla explícitamente; no continúa sobre una base vacía.

Cada afirmación indica si es observada, inferida, hipótesis o supuesto, con población, periodo, método, evidencia y contraevidencia. Acción mencionada en una conversación no prueba acción ejecutada. Si el sistema no tiene trazas suficientes, puede investigar, pero no presentar un procedimiento como verificado.

El sandbox es un proceso aislado sin red ni privilegios, con input protegido y derivaciones escribibles. DuckDB tiene capacidades de archivos y extensiones: configurar el motor no sustituye aislamiento del sistema operativo. El broker de modelos está fuera y autoriza toda salida antes de enviarla al proveedor.

Las secciones 23 y 24 describen el bucle ejecutable y cómo publicar una derivación sin depender de scratch mutable.

## 11 Evitar evidencia aparentemente correcta pero equivocada

DetectorSpec declara unidad de medición, llave de unidad, universo elegible, cardinalidades de joins, cobertura, comparador y semántica de agregación. Primero se construye un universo único; luego indicadores por unidad; al final tasas y diferencias. Las exclusiones y los resultados desconocidos siguen visibles.

@diagram grain

Ejemplo ilustrativo: un contacto tiene tres eventos digitales y dos transacciones. El join combinado puede producir seis filas, pero sigue existiendo un contacto. Contar filas sería medir combinaciones, no contactos. El monitor prueba unicidad y cardinalidad, o usa pesos declarados si otra unidad es la intención.

Cada métrica informa población objetivo conocida o desconocida, unidades observadas, elegibles y evaluables, exclusiones y cobertura. Una tasa entre casos evaluables no se llama tasa total del banco. Los registros problemáticos en cuarentena no desaparecen del contexto de la medición.

El sistema contrasta composición de productos, temas y canales, temporalidad y explicaciones competidoras. Explorar muchos segmentos produce hallazgos aparentes por azar; la confirmación usa información independiente y una política estadística explícita. Si falta soporte, termina inconcluso en lugar de fabricar una causa.

## 12 Publicar un expediente y comparar alternativas

La señal es un candidato a investigar. La oportunidad es una identidad estable que puede reunir varios runs, afirmaciones, propuestas y decisiones. Una ejecución nueva no crea automáticamente otro expediente ni otra notificación.

@diagram opportunity

La deduplicación exacta evita repetir la misma señal de un run. Para oportunidades, el sistema busca coincidencias por ámbito, tema, población y evidencia; la similitud semántica sugiere una relación, no prueba una misma causa. Puede relacionar dos problemas sin fusionarlos. Merge o split conserva sus referencias originales.

La prioridad muestra volumen elegible, evidencia, beneficio por escenarios, esfuerzo, dependencias, riesgo y urgencia. El esfuerzo se descompone en construcción, integración, pruebas, autorizaciones y operación. Una tool faltante no significa costo cero. No conocer esfuerzo tampoco permite etiquetarlo como fácil.

Las cifras económicas llevan unidad, horizonte, fuente y supuestos. Para comparar USD se conserva el valor original y la referencia de cambio. Ahorro de atención y ahorro de recontacto pueden solaparse; no se suman sin un baseline común. Una estimación no se convierte en beneficio observado por haberse aprobado.

Posponer afecta la atención humana, no la verdad de la evidencia. El motor puede seguir dentro de su política. Un cambio material o un incidente crítico puede pedir intervención de nuevo. Si el grupo responsable no tiene miembros disponibles, el sistema muestra routing_failed y escala a un fallback autorizado.

La sección 26 concreta DecisionComparison y las consecuencias distintas del feedback.

## 13 Convertir patrones en cambios concretos

Para aprender de humanos o IA2 necesitamos acciones verificables, no solamente conversaciones cerradas. Normalizamos cada acción en un token: tipo, contrato y versión de tool, precondiciones observadas, resultado, actor y orden temporal. Conservamos ambigüedad cuando no existe secuencia fiable.

@diagram procedure

El código busca secuencias repetidas dentro de límites de longitud y soporte. El LLM interpreta variaciones y propone procedimientos; Jev puede etiquetar categorías conocidas. Se comparan éxitos y excepciones en cohortes comparables. Una secuencia frecuente pero insegura no se vuelve admisible.

ProcedureSpec define guards verificables, acciones tipadas, comprobación de resultado y caminos de error, unknown y handoff. Una condición ausente se convierte en RequiredEvidence, nunca en true. La parte automatizable puede ser pequeña; mantener humano en casos complejos puede ser la solución correcta.

CapabilityDelta es el cambio propuesto sobre una base exacta. ImprovementProposalRevision reúne problema, evidencia, elegibilidad, exclusiones, ese cambio, dependencias, escenarios, valor, esfuerzo y riesgos. No aplica un parche arbitrario generado por el modelo a la versión activa.

El planner debe distinguir mejorar soporte de reparar causa bancaria. Una mejor explicación no corrige un fallo de core. Puede recomendar una intervención externa al catálogo de atención y asignarla al equipo correspondiente, sin fingir que otro agente resolverá cualquier problema.

La sección 25 define nodos, predicados y el algoritmo inicial para convertir estas secuencias en un contrato comprobable.

## 14 Construcción de capacidades e integración con el catálogo

El builder conversacional conserva una AuthoringSession y un DraftSpec. El usuario puede describir un objetivo o modificar una propuesta. El modelo produce estructura y preguntas pendientes; Rust valida referencias, esquemas, permisos y compatibilidad. Finalizar crea una revisión inmutable, no un release.

El mismo flujo acepta propuestas automáticas de Evolución y solicitudes humanas. Dentro de la autonomía concedida, el motor prepara candidatos y ejecuta evaluaciones sin pedir aprobación por cada paso. Las personas intervienen cuando una decisión, excepción o dependencia necesita su autoridad; no existe otro builder especial para la automejora.

@diagram authoring

| Salida | Qué debe especificar | Quién la prepara |
| Árbol | Guards acciones errores resultado y handoff | Framework con compilador o validador |
| Agente | Objetivo estado decisiones tools skills límites y escalamiento | Framework mediante contrato |
| Equipo | Roles delegación tareas compartidas límites y coordinación | Framework mediante contrato |
| Skill | Procedimiento precondiciones entradas salidas dependencias | Catálogo y framework según ejecución |
| Knowledge | Fuente versión vigencia ámbito tratamiento y consumidores | Pipeline de conocimiento |
| Tool | Schema efectos permisos errores disponibilidad y recuperación | Owner de integración no el modelo |
| Data request | Campos finalidad cobertura tratamiento y dependencia | Data broker con autorización |

Registrar un contrato de tool no instala la tool ni amplía permisos. Una versión nueva de conocimiento tampoco actualiza todos los releases fijados. Importación externa y edición humana sobre bases distintas generan conflicto, no overwrite silencioso.

FrameworkAdapter prepara el candidato y devuelve ready, pending, dependency_block o failed. CandidateManifest fija propuesta, paquete, versiones, dependencias y nivel de evidencia: solo spec, runtime simulado o runtime ejecutable. El nivel ejecutable se deriva de un productor autenticado, no del campo escrito por un LLM.

Si falta la implementación interna de un agente, se puede validar su contrato. No se puede presentar esa validación como tasa de resolución. La oficina visual muestra definiciones e instancias trabajando a partir de eventos reales; un avatar activo no certifica eficacia.

## 15 Diseñar escenarios y comprobar resultados

Un ScenarioCase contiene precondiciones, objetivo del cliente, entorno inicial, hechos visibles, fixtures de tools, acciones permitidas, criterios de resultado y límites. ScenarioFamily conserva el origen y linaje de variantes. Cambiar idioma o frase de un caso no produce una muestra independiente.

@diagram evaluation

PartitionBroker asigna familias a desarrollo, validación iterativa o final reservada. El investigador y builder no ven el final. El runner adversarial sí recibe la vista mínima de cliente del caso asignado; no el oráculo ni el estado privado del soporte. Su memoria y sus conversaciones reservadas no vuelven al constructor.

El baseline y el candidato reciben entornos equivalentes y aislados. Cada caso resetea los fixtures. El oráculo verifica acciones, permisos y objetivo en el estado final. Un timeout de tool deliberado puede ser un caso aprobado si el sistema escala correctamente; si el harness no logró producir el escenario, es inconcluso.

Jev puede juzgar un criterio cerrado de claridad. Un LLM independiente puede criticar aspectos abiertos. Ninguno compensa una violación de seguridad ni convierte «gracias» en resolución. Las rúbricas, modelos, prompts y criterios se fijan antes del ensayo.

El reporte muestra cobertura, resultados por escenarios y cohortes, fallos críticos, costo y latencia, incertidumbre y lo no probado. La política del gate establece pass, fail o inconclusive. Pass no autoriza publicar; todavía faltan autoridad, compatibilidad actual y alcance.

La sección 26 concreta de dónde proviene el oráculo, qué devuelve cada comprobación y cómo medimos cobertura sin confundir etiquetas de casos con ejecución real.

EvaluationPlan congela comparison_population_ref, cohort_membership, elegibilidades por versión, denominadores y routing_cost_boundary. Reporta población común y cobertura específica separadamente. Escalar todos los casos caros no los elimina del universo; si no ejecutamos la continuación humana, el costo es parcial o supuesto explícito, no ahorro total probado. Las ramas nuevas no borran regresiones protegidas del baseline.

## 16 Automejora con límites y feedback útil

El sistema aprende mediante nuevas propuestas, casos y detectores versionados. No modifica prompts, pesos o capacidades activas cada vez que aparece una conversación. Conserva por qué una hipótesis se refutó o una propuesta se rechazó para no repetir trabajo sin novedad.

@diagram learning

Una consulta exploratoria útil puede convertirse en DetectorVersion. Su evaluación comprueba semántica, cardinalidad, estabilidad fuera del periodo explorado, calidad, costo y límites. MonitorRegistrationDecision autoriza vincular una versión a una misión. Ese registro pertenece a discovery; no activa un agente de atención.

Un nuevo tema requiere TaxonomyRevision y preguntas de clasificación compatibles. Etiquetas provisionales no reescriben el histórico. Si cambian categorías, las comparaciones deben registrar cómo se mapearon o declarar incompatibilidad. Un modelo nominalmente igual puede cambiar comportamiento: se conserva la identidad resuelta cuando el proveedor la expone y se declara incertidumbre cuando no.

El feedback humano tiene tipos diferentes: evidencia aportada, objeción, restricción, preferencia o autorización. Rechazar por falta de prioridad no demuestra hipótesis falsa. Aprobar tampoco demuestra eficacia. Los outcomes posteriores permiten revisar supuestos solo cuando ventana y cobertura son suficientes.

La sección 26 desarrolla mappings de taxonomía y consecuencias de aprendizaje sin entrenar automáticamente con clicks o aprobaciones.

## 17 Aplicar cambios sin confundir aprobación y efecto

PromotionAuthorization fija candidato, evaluación, política, etapa, ámbito, vigencia, autoridad y precondiciones. El sistema revalida dependencias y evidencia actuales antes de usarla. Una corrección material de fuente o una tool incompatible bloquea su uso; no borra lo que se aprobó históricamente.

@diagram release

ReleasePlan define referencia, objetivo, exposición, asignación estable y condiciones de parada. RuntimeOperation identifica el efecto solicitado y su clave idempotente. Si la respuesta se pierde, consultamos la misma operación antes de repetir. Un receipt de aceptación no prueba que el routing cambió.

El runtime aplica precondiciones de generación, autoridad y fencing en el momento del efecto. Fencing es el mecanismo que rechaza una operación antigua después de que otra obtuvo autoridad más reciente. Un stop invalida una activación pendiente para que una respuesta tardía no reactive el servicio.

ReleaseReconciliationState muestra plan deseado y estado observado por ámbito: baseline, candidato, unknown o stopped. Un release parcial puede haber expuesto clientes; no se resume como pendiente sin explicar alcance. Promociones solapadas incompatibles esperan reconciliación.

Shadow no ejecuta efectos reales. Canary requiere autorización aparte y ventanas de observación. Rollback cambia versión o routing; no revierte por arte de magia una transferencia. Una compensación bancaria necesita otro contrato y otra autoridad.

## 18 Proactividad antes del contacto

El sistema también puede descubrir fricción anterior a un contacto: repetición de intentos, errores digitales o transacciones con estados problemáticos. Separar esa observación de una probabilidad estimada de contacto evita que el lenguaje parezca una predicción validada.

@diagram proactive

PredictionCutoff fija qué datos se conocían en ese momento. Una queja posterior o una corrección llegada después no puede usarse como feature retrospectiva. El benchmark usa orden temporal, casos negativos y censura; informa anticipación, falsas alertas y costo cuando existe evidencia suficiente.

Podemos comenzar con reglas explicables Rust y SQL. Un predictor estadístico futuro necesita versión, contrato de features, calibración y validación temporal propios. Jev puede interpretar texto disponible, pero no reemplaza ese modelo con una conjetura sobre una tabla.

La salida inicial es una oportunidad agregada o contexto preventivo para la próxima atención autorizada. Enviar un mensaje, iniciar una campaña o actuar sobre la cuenta requiere OutreachProposal con finalidad, canal, elegibilidad, preferencias, límites y autorización. Detectar proactivamente no concede permiso para contactar.

## 19 Cómo implementar un trabajo durable

JobRun fija propósito, entradas, política, presupuesto y estado. JobStep fija tipo, dependencias, intento, lease, token de fencing y outputs. Un lease es una concesión temporal para que un worker ejecute ese paso. No equivale a propiedad permanente.

@diagram durable

El worker reclama un paso mediante transacción y recibe lease y token. Cada broker comprueba que siguen vigentes antes de despachar una query, llamada de modelo o efecto. Al confirmar, el controlador verifica el token otra vez. Un worker viejo no puede publicar encima de la ejecución recuperada.

Persistimos el blob completo, verificamos su hash y después confirmamos metadata, evento y outbox en una transacción. Outbox es una tabla de mensajes pendientes que evita perder el evento entre commit y publicación. Entrega repetida y fuera de orden se toleran con IDs, revisiones y replay; no prometemos exactly-once.

Cancelación bloquea trabajo nuevo, pero no prueba que una llamada externa ya iniciada se canceló. Usage desconocida se reconcilia; no se reembolsa presupuesto por asumir costo cero. Las keys de efecto no cambian por cada retry.

API de aplicación: query para una proyección autorizada, submit para un comando tipado y subscribe para progreso. El retry de un comando committed devuelve su operación anterior tras revalidar acceso; no reaplica una precondición vieja ni vuelve a ejecutar. Un cursor expirado obliga resync, manteniendo el estado del comando y sin recuperar evidencia revocada.

## 20 Operación recuperación y cambios del software

La plataforma necesita límites globales, además de presupuesto por investigación. Backfills, SQL y generación de casos no deben consumir la capacidad necesaria para registrar decisiones o contener incidentes. La agenda aplica colas limitadas, fairness y reserva operacional.

@diagram recovery

Si falla Jev o el LLM, investigación semántica espera y monitores válidos pueden continuar. Si falla el sandbox, no hay nueva evidencia SQL, no ausencia de problema. Si cae Pulso, el framework conserva capacidad estable; no se publican versiones nuevas. Falta de autoridad verificable bloquea nuevos efectos privilegiados.

Restore comienza en modo cerrado para efectos y salida de datos. Verifica referencias y hashes, aplica revocaciones y supresiones actuales, cambia recovery epoch, reconstruye proyecciones y reconcilia routing externo. No usa una generación antigua de backup como verdad del runtime. Si no puede comprobar autoridad actual, no reabre efectos.

PlatformDeploymentManifest distingue release de código, esquema y configuración de release de capacidades. Inicialmente pausamos o drenamos trabajos, protegemos escrituras, migramos, verificamos y reabrimos. Artefactos anteriores conservan bytes y hashes; conversiones de esquema producen nuevas derivaciones. Rollback de código solo si mantiene compatibilidad.

SLO, RPO y RTO son objetivos de latencia/disponibilidad, pérdida tolerable y recuperación. Se configuran y prueban en el entorno elegido; este diseño no inventa 99.9 por ciento ni cero pérdida. La auditoría requerida no se elimina mediante sampling de telemetría. Métricas usan dimensiones acotadas; IDs detallados viven en trazas con acceso y retención propios.

## 21 Seguridad y medición sin perder claridad

AuthorizationContext se obtiene del servidor y conserva principal, origen, finalidad, delegación, ámbito, partición, vigencia y epoch. La autoridad efectiva es la intersección de lo delegado y permitido. Un service account amplio no presta sus poderes a una solicitud limitada.

Cambiar autonomía también es una decisión. PolicyRevision propone; PolicyActivationDecision autoriza. Un worker puede pedir más permisos, nunca concedérselos. Toda referencia transitiva y salida al modelo se valida contra el contexto real.

El broker conserva un manifiesto del contexto completo, incluidos mensajes anteriores. Revocar una fuente invalida sesiones, caches y workspaces derivados; no basta quitar un link conservando el texto en el prompt. Ya enviado a proveedor no se puede retraer mediante una promesa local: requiere su procedimiento y confirmación.

NPS y CSAT son encuestas, no sentimiento inferido. NPS usa promotores 9 y 10, detractores 0 a 6 y todas las respuestas válidas como denominador. CSAT exige definición de escala y categorías favorables. No combinar escalas incompatibles; ninguna respuesta significa desconocido. Ambas muestran cobertura y tasa de respuesta.

Los casos de mora, contactos o ventas pueden orientar hipótesis, pero una asociación no describe por qué una persona dejó de pagar. De igual manera, una mejora observada después de release no es automáticamente efecto causal. Cada afirmación conserva su alcance y sus límites.

## 22 Construcción incremental y aceptación

Primero construiremos un recorrido completo sobre fixtures identificados, no todas las features a la vez. Ingesta, snapshot, monitor, expediente y pregunta humana deben producir evidencia real dentro del entorno de prueba. Después incorporaremos dos alternativas, candidato preparado y evaluación con oráculos.

@diagram implementation

El primer corte incluye permisos, identidad de fuente, revisiones, budget y progreso; no se agregan al final. Model adapters deterministas permiten probar controlador; model-in-loop evalúa comportamiento del proveedor aparte. El marco de atención se sustituye mediante su puerto, no mediante resultados exitosos inventados.

La matriz de aceptación cubre contratos, seguridad del sistema, benchmark de detección y evaluación de candidatos. Son suites distintas. Un caso cubre ejecución normal y también corrección tardía, dependencia inexistente, error de tool, timeout externo, cambio concurrente, revocación y restore. Ningún mock prueba aislamiento OS o idempotencia del banco real.

Antes de integraciones reales se requiere verificar bindings, identidad, permisos, aislamiento, routing CAS y fencing, retención y recovery. Los umbrales de negocio, económicos y de evaluación se configuran con responsables, no se copian de ejemplos.

La siguiente unidad de implementación recomendada es el recorrido de la sección 4 con una intervención concreta de lectura y explicación. Permite comprobar el sistema que detecta y propone sin construir todavía todo el framework ni prometer acciones bancarias que no existen.

## 23 El coordinador que hace ejecutable la investigación

Para el primer corte proponemos una investigación secuencial por workspace. No varios agentes modificando la misma base simultáneamente. El investigador propone un siguiente paso; un coordinador Rust lo valida, lo ejecuta y registra su resultado antes de pedir otra decisión.

@diagram coordinator

NextAction admite DescribeSchema, ReadQuery, Derive, InspectResult, RequestSemanticJudgment, FinishResearch y DeclareBlocked. No admite PublishRelease ni escritura directa de metadata. Inspeccionar un resultado referencia un receipt y una selección autorizada. Finalizar produce un borrador que todavía debe validarse y publicarse.

FinishResearch crea pasos durables DraftCommitted, ValidateResearch y PublishResearch, antes de que el job pueda terminar Published, AwaitingConflictResolution o Rejected. El receipt de publicación es un output confirmado; un crash tras finalizar el texto no pierde el resultado. DeclareBlocked registra dependencia y estado pendiente; no finge investigación publicada.

@code coordinator

El contexto se reconstruye desde referencias committed, autorizadas y compatibles con la partición. Si cambia la evidencia externa, se crea otra investigación. Una reparación de SQL o JSON consume una ronda y presupuesto; el límite evita que el modelo itere indefinidamente para llegar a una respuesta convincente.

publish_research recibe revisión esperada del expediente, artefacto de investigación, evidencia, drafts de afirmaciones, señales y key idempotente. Evidence verifica referencias, disponibilidad y lineage; Opportunities aplica la revisión preservando actividad humana. Si alguien objetó mientras el investigador terminaba, se resuelve el conflicto, no se sobrescribe su objeción.

Comentario o asignación sin cambio analítico permite adjuntar resultado con inputs originales. Hipótesis nueva permite adjuntarlo indicando que no fue evaluada y, si procede, otra investigación. Restricción de scope exige revalidar o rehacer; evidencia corregida deja resultado histórico o stale; merge y split exigen resolver destino. Nunca sustituimos expected_revision por el último head y reintentamos ciegamente.

La identidad técnica de señal usa tenant y ámbito, versión de detector, snapshot, especificación de población, ventana y métrica. No usa la redacción generada. La recuperación de oportunidades parecidas es otra búsqueda por tema y overlap, no una llave que demuestre misma causa.

Ese snapshot se concreta en AnalysisInputManifest: fuentes, revisiones de episodios y outcomes, anotaciones y taxonomía, contexto de capacidades si afecta, corte temporal y política de madurez. Su hash entra en identidad, caché y run. Una reconstrucción distinta no se deduplica como si hubiera usado las mismas entradas.

## 24 Publicar derivaciones SQL y contabilizar modelos

ReadQuery lee una revisión concreta del workspace. Derive crea una rama temporal desde esa revisión, ejecuta la transformación y publica un estado nuevo solo después de verificar los blobs y confirmar el manifiesto. Para fixtures pequeños puede persistir una fotografía consistente completa de la base de trabajo; no copiar un archivo activo a ciegas.

@diagram derivation

DerivationRequest contiene operation_key, expected_workspace_revision, parent_manifest, SQL, parámetros, autorización y presupuesto. DerivationResult devuelve parent_revision, proposed_manifest, receipts y state_artifacts. Si cae antes del commit, el retry vuelve al último estado confirmado; si cae después, devuelve el receipt existente. Scratch sobreviviente no decide qué ocurrió.

ModelOperation registra step, contexto completo, invocación, reserva, dispatch_state, usage_state y output. El broker primero autoriza, consulta cache compatible y, si hay miss, reserva recursos y registra operación antes de enviar. Una respuesta permite liquidar con usage reportada; un timeout posterior al envío deja usage pendiente.

@diagram accounting

Cancelación o lease vencido no demuestra costo cero. Si el proveedor no tiene idempotencia, un retry puede cobrarse otra vez; se registra y limita. Si no ofrece una cota económica fiable, la reserva es una estimación conservadora, no una garantía de factura máxima. Un cache hit se informa como reutilización, no una llamada fresca.

## 25 Del procedimiento al contrato que recibe el framework

ProcedureSpec guarda esquema de entrada, condiciones iniciales, nodos, aristas, dependencias, resultados esperados y evidencia pendiente. Sus nodos son Check, Read, Act, Respond, Handoff y Finish. Los predicados incluyen Exists, Equals, In, Compare y composición And, Or, Not.

@diagram procedureTree

Cada predicado devuelve true, false o unknown. Exists puede ser falso si sabemos que el campo no existe; no conocerlo sigue siendo unknown. No usamos un resultado posterior como condición que supuestamente ya conocíamos antes de actuar. Una rama unknown necesita otro paso autorizado o handoff.

InputValue distingue Known(value), KnownAbsent y Unknown(reason); el schema define si null es valor o ausencia. Usamos lógica de tres valores: false AND unknown es false; true OR unknown es true; NOT unknown es unknown. Check tiene ramas true, false y unknown. Varias condiciones salientes exigen exclusividad comprobable o prioridad declarada; sin regla, falla validación. Un error de tool es resultado de ejecución separado, no un false implícito.

Algoritmo inicial: seleccionar trazas verificables; normalizar firmas de acciones y estado previo; agrupar por objetivo y elegibilidad; contar prefijos compartidos; contrastar excepciones y fallos; construir un grafo candidato; pedir al LLM condiciones propuestas; validar referencias y campos; conservar huecos como RequiredEvidence. Este algoritmo puede comenzar con prefijos simples; no requiere minería sofisticada para el primer corte.

validate_procedure_spec comprueba tipos, refs, nodos alcanzables, bindings de campos, rutas de salida y tratamiento de unknown/error. Un ciclo requiere límite o salida. Orden parcial de acciones concurrentes no se inventa como orden total. Frecuencia no demuestra que el guard sea causa del éxito.

ChangeSpec tiene variantes: TreeChange, SkillChange, AgentChange, TeamChange, KnowledgeChange, ToolRequirement, DataRequirement y ClassifierChange. AgentChange especifica objetivo, elegibilidad, inputs/outputs, skills/tools, límites y escalamiento. TeamChange agrega responsabilidades, delegación, contexto compartido y regla de agregación. Un equipo sin owner de tareas o con delegación circular ilimitada falla validación.

Cada requirement queda satisfied, unresolved o incompatible con evidencia. DataRequirement precisa campos, grain, frescura, joins y finalidad. ToolRequirement precisa inputs, outputs, efectos, errores y disponibilidad. Ninguna de las dos implementa el sistema externo por escribir un schema.

## 26 Oráculos cobertura taxonomías y decisiones

OracleSpec fija objetivo, fuentes de autoridad, assertions, dimensiones desconocidas y procedencia: regla autorizada, experto, histórico verificado o supuesto sintético. El LLM puede proponer un draft, pero no otorgarle autoridad. Si solo hay cierre administrativo, resolución real sigue desconocida.

Assertions interpretadas por Rust pueden comprobar FinalState, TraceContains, ActionForbidden, HandoffRequired, OutputContractSatisfied y BudgetWithin. Un mundo sintético permite probar condicionales explícitos; no demuestra que esos estados existieron en el banco. Un test metamórfico cambia una dimensión: mismo objetivo en otro idioma debe mantener efecto estructurado; retirar permiso debe impedir la acción. Eso no prueba por sí solo que el primer caso fuera correcto.

AssertionResult devuelve pass, fail, unknown o not_applicable, con evidence_refs, observed_fields o effects y reason. Unknown conserva falta de observación; not_applicable exige condición de aplicación comprobada falsa. ActionForbidden solo pasa con captura suficiente, no por ausencia de traza incompleta. Un schema válido prueba forma, no resolución. Cada assertion declara requisito objetivo, seguridad, contrato o calidad; sin objetivo comprobado el gate no permite afirmar resolución.

@diagram coverage

CoverageRequirement conecta requisito, condición, criticidad, casos, assertions y observaciones de ejecución. Se distingue caso generado, condición realmente alcanzada y comprobación ejecutada. Diez paráfrasis no cubren diez ramas. Si un caso etiquetado timeout no produce timeout, esa excepción sigue sin cubrirse.

El juez semántico ve solo lo necesario para su criterio, sin identidad o justificación del candidato. Comparamos con rúbrica común y orden alternado cuando corresponda; calibramos con referencias y reportamos desacuerdo. Claridad no sustituye corrección del estado final.

@diagram taxonomy

TopicRevision conserva definición, ejemplos positivos, exclusiones, ambiguos y status provisional, accepted o retired. TaxonomyChange registra mappings equivalent, broader, narrower, split, merge o unresolved. Un split exige nuevas anotaciones elegibles o declarar comparabilidad parcial; nunca repartir cifras históricas proporcionalmente sin evidencia. Una categoría aceptada sin ruta de atención usa fallback definido, no elimina contactos.

DecisionComparison primero separa alternativas inviables, después calcula escenarios con baseline y horizonte común. Puede identificar dominancia solo cuando unidades, alcance, evidencia y criterio de preferencia son comparables. El LLM explica tradeoffs; no convierte riesgo, horas y USD a equivalencias ocultas. Mostramos el supuesto que podría invertir la recomendación.

@diagram intervention

La prioridad de investigar difiere de la de construir. Un problema incierto podría merecer un análisis barato sin justificar implementación todavía. El mecanismo de intervención explica qué efecto espera cada propuesta y por qué esa capacidad puede producirlo. Solo recomendamos equipos si la coordinación es necesaria, no por ser una opción supuestamente superior.

El aprendizaje tiene salidas tipadas. Hipótesis refutada conserva contraevidencia; candidato fallido agrega regresión y propone revisión; harness inconcluso pide reparar entorno; baja prioridad pospone; dependencia pendiente bloquea implementación; riesgo inaceptable agrega restricción; detector confirmado crea monitor; outcome maduro diferente reabre investigación. Ninguna salida modifica silenciosamente el agente estable.

## 27 Referencias y contratos de consulta

La especificación técnica de referencia es SPEC_DETECCION_AUTOMEJORA.md. ESCENARIOS_VALIDACION_PULSO.md contiene el catálogo de aceptación. REVISIONES_SPEC_PULSO.md mantiene hallazgos y cambios. Esta guía desarrolla el mismo diseño para lectura y añade contratos HOW derivados de las nuevas revisiones; los documentos deben permanecer alineados.

Fuentes técnicas para las capacidades de Jev y las fronteras del motor analítico:

- Jev preguntas tipadas https://docs.typesafe.ai/primitives
- Jev confidence https://docs.typesafe.ai/confidence
- Jev routing https://docs.typesafe.ai/patterns/intent-routing
- DuckDB aislamiento https://duckdb.org/docs/current/operations_manual/securing_duckdb/overview
- JSON canónico https://www.rfc-editor.org/rfc/rfc8785
- SQLite backup https://www.sqlite.org/backup.html
- NPS https://www.netpromotersystem.com/about/measuring-your-net-promoter-score

Estas fuentes describen tecnologías o definiciones. La arquitectura de Pulso y sus elecciones de implementación son propuestas del equipo y deben validarse con contratos y pruebas del entorno objetivo.
