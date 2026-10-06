# Pulso: mapa integrado de producto y arquitectura

Fecha: 2026-09-29. Estado: propuesta de diseño, no implementación ni decisiones aprobadas. Consolidación de tres revisiones independientes: experiencia de producto, arquitectura y dominio/contratos. Complementa ARQUITECTURA_PULSO.md y DETALLE_MOTOR_Y_DATOS.md. El enfoque es un banco real con histórico y trazas autorizados; no implica acceso efectivo ni permiso para operar.

## 1. Qué faltaba en el enfoque anterior

Habíamos descrito con más profundidad el procesamiento que el trabajo de las personas alrededor de sus resultados. Una cadena señal → investigación → propuesta → evaluación no explica quién entiende el hallazgo, cómo lo cuestiona, cómo compara alternativas ni cómo observa consecuencias.

La propuesta es diseñar conjuntamente tres circuitos:

- Atención: resolver el problema del cliente con capacidades estables y escalamiento seguro.
- Evolución: descubrir, investigar, proponer y evaluar mejoras continuamente.
- Colaboración y operación: explicar resultados, organizar decisiones autorizadas, proteger el servicio y comprobar qué ocurrió después.

No son tres pantallas ni tres microservicios obligatorios. Son responsabilidades conectadas. El cliente del banco no recibe la bandeja interna de oportunidades: recibe atención y continuidad; el equipo del banco recibe la experiencia de investigación y gestión.

## 2. Dos experiencias y varias responsabilidades

**Cliente del banco.** Clasificación y cuatro capas conocidas, sin obligarle a conocerlas. Conservación del contexto entre canales y escalamiento cuando sea posible; información clara sobre acciones realizadas, pendientes y límites. El handoff no debe hacerle empezar de nuevo. Cambiar una capacidad no permite experimentar libremente con una acción bancaria real.

**Equipo del banco.** Responsable de servicio/producto, analista, experto operativo, diseñador de capacidades, revisor de calidad/riesgo y responsable de releases. Son responsabilidades; una persona puede cubrir varias. La bandeja y los permisos dependen de ellas. Usuario primario inicial sugerido: responsable de servicio apoyado por analista, pendiente de acuerdo.

El usuario no opera cada paso del detector. El motor trabaja automáticamente bajo una política de ámbito, presupuesto y autonomía. La persona interviene para comprender, cuestionar, aportar contexto, comparar, priorizar y tomar decisiones que requieren su autoridad.

## 3. La unidad de trabajo: expediente de oportunidad

Una Opportunity mantiene identidad estable y puede reunir múltiples investigaciones, propuestas, evaluaciones y releases. El expediente es su vista de trabajo, no otra entidad con un lifecycle paralelo.

Su vista contiene:

1. Problema y población: qué sucede, a quién, desde cuándo y respecto a qué comparación.
2. Evidencia: métricas con unidades/denominadores, ejemplos, contraejemplos, consultas, procedencia, actualidad y límites.
3. Explicaciones: observaciones, inferencias, hipótesis y supuestos diferenciados. Un insight es una afirmación respaldada/versionada dentro del expediente, no necesariamente otra entidad.
4. Alternativas: no cambiar, mejorar conocimiento, ampliar árbol, mejorar skill/agente/equipo o trasladar un problema fuera de soporte.
5. Comparación: cobertura elegible, exclusiones, beneficio por escenarios, costo, esfuerzo, dependencias, riesgo e incertidumbre.
6. Trabajo y decisiones: responsable, solicitudes humanas, trabajos automáticos, revisiones, objeciones y razones.
7. Seguimiento: pruebas, alcance del release, guardrails y resultados posteriores con su madurez.

La identidad puede permanecer mientras cambian las conclusiones. La proyección actual es reconstruible; evidencias, propuestas, evaluaciones y decisiones referencian versiones exactas. No se sobrescribe el pasado para que coincida con la última explicación. Conservar historial no exige conservar datos personales indefinidamente.

## 4. Superficies del producto, no una presentación del pipeline

| Superficie | Trabajo del usuario | Soporte del sistema |
|---|---|---|
| Centro de mando | Entender qué merece atención y qué está ocurriendo | Bandeja por rol, incidentes, oportunidades, decisiones pendientes y salud del motor/servicio |
| Expediente | Comprender, cuestionar y profundizar | Afirmaciones/evidencia, actividad, investigaciones y continuidad |
| Comparación de propuestas | Elegir el cambio mínimo que merece avanzar | Alternativas, escenarios de valor, esfuerzo, exclusiones y riesgo |
| Laboratorio | Entender qué se probó, falló y sigue desconocido | Baseline/candidato, casos, particiones, evaluaciones y replay seguro |
| Catálogo de capacidades | Gestionar agentes/equipos, árboles, conocimiento, skills y tools | Versiones, permisos, propietarios, dependencias y cobertura declarada/evaluada/observada |
| Observabilidad y releases | Inspeccionar una decisión y sus efectos | Trazas, exposición, condiciones de parada, versiones y resultados posteriores |

La oficina visual de agentes, sus fichas y métricas, el constructor conversacional y la gestión de conocimiento/skills/tools siguen dentro de la visión integral. Aquí se define cómo se conectan con el núcleo de evolución; no se implementa la construcción interna del framework. La oficina es una representación de actividad real, no fuente de verdad sobre éxito. Una animación de tests debe reflejar estados y resultados verificables.

El copiloto acompaña las superficies. Puede explicar evidencia existente o abrir una investigación nueva; debe indicar cuál está haciendo. Permite solicitudes abiertas —«busca contraejemplos», «compara con el otro canal», «excluye este producto»— sin sustituir la comparación visual ni los controles de autorización. Regresar desde una traza/tool conserva expediente, filtros y versión seleccionados.

## 5. Arquitectura lógica y propiedad

Mantener aplicación modular Rust y workers aislados como propuesta, sin obligar microservicios.

**Atención:** framework propio, clasificador, árbol, IA1/Jev, IA2/LLM, humano; ejecución estable, acciones autorizadas, handoff y trazas de versiones utilizadas.

**Inteligencia y evolución:** agenda de exploración, detección híbrida, agrupación de señales, investigación SQL libre dentro del sandbox, explicaciones y alternativas. Es propietario del contenido analítico de las oportunidades y propuestas; estima valor, no lo declara realizado.

**Control y colaboración:** coordina comandos/tareas humanas, políticas, permisos, presupuestos, catálogo/grafo de impacto, decisiones y operación de releases. No reescribe la evidencia del investigador ni se convierte en un segundo propietario del contenido analítico. Las vistas del expediente agregan información de estos módulos.

**Evaluación:** Evolución puede generar casos y candidatos; el laboratorio ejecuta comparaciones aisladas; Control aplica gates y autoriza progresión. El generador no decide su propia aprobación ni recibe casos reservados mediante el copiloto o feedback humano.

**API/read models:** consultas orientadas a trabajo humano, con revisión, actualidad y acceso apropiados. La interfaz no es propietaria de las reglas. Los comandos autorizados cambian estado mediante el módulo correspondiente y eventos de dominio; las vistas se reconstruyen.

## 6. Continuidad: agenda, no solo ejecuciones aisladas

ExplorationMission representa objetivo, ámbito autorizado, cadencia/disparadores, prioridad, presupuesto y política de autonomía. Ejemplos de objetivos: descubrir automatización desaprovechada, nuevos motivos, conocimiento desactualizado o regresiones. Son ejemplos de diseño, no hallazgos del banco.

La agenda reacciona a datos nuevos, resultados maduros, cambios de capacidades, evaluaciones, solicitudes humanas y calendario. Reserva espacio para explorar problemas desconocidos; no se limita a perseguir alertas predefinidas. Limita ciclos, evita repetir investigaciones sin información nueva y no permite que una oportunidad monopolice recursos.

Una actualización silenciosa no es una notificación. Se pide atención cuando aparece un riesgo, una decisión relevante, evidencia que cambia una conclusión o un bloqueo que requiere autoridad humana. Agrupar señales relacionadas; posponer con motivo/alcance/vencimiento. Silenciar ahorro potencial no silencia incidentes de seguridad.

## 7. Tres recorridos completos

### A. Hallazgo cuestionado

Ejemplo ilustrativo, sin cifras ni afirmaciones sobre el banco: el motor detecta recontactos sobre operaciones pendientes. Abre o actualiza una oportunidad y explica población/comparación/límites. El responsable pregunta si una caída del canal explica el patrón. La pregunta queda como hipótesis atribuida y origina investigación sobre información ya autorizada. El sistema contrasta cohortes y contraejemplos, registra una nueva revisión y conserva la anterior. Puede mantener, matizar o refutar la afirmación. Presenta alternativas, no fuerza aprobar una solución.

### B. Procedimiento humano a automatización parcial

El sistema encuentra una secuencia asociada a buenos resultados en casos comparables. Muestra precondiciones, acciones y excepciones; no convierte asociación en causa. Un experto excluye casos que requieren juicio humano. Se comparan árbol, skill o mantener escalamiento; preparar candidato pertenece al adaptador del framework. Evaluación fija versiones y distingue fixtures/simulaciones de comportamiento real. Una aprobación para shadow no autoriza canary ni acciones externas. El expediente continúa después del release.

### C. Regresión a protección y aprendizaje

Un fallo crítico activa contención determinista según una política previamente autorizada: detener, enrutar o revertir. Se abre un incidente operacional sin esperar una investigación LLM. Después se vincula una oportunidad de corrección, se buscan causas/contraejemplos y se añaden pruebas. El release fallido permanece visible. Una corrección requiere nuevas evaluaciones y autorización según riesgo.

## 8. Contratos adicionales derivados de la experiencia

Se mantienen los tres contratos fundacionales: evento de atención, observación de resultado y snapshot de capacidades. Estos contratos nuevos se apoyan en ellos; campos/transporte pendientes.

| Contrato | Contenido mínimo y garantía |
|---|---|
| OpportunityBrief | Problema, población/periodo, métricas/unidades, evidencia/límites, revisión/actualidad, alternativas y decisión necesaria |
| InvestigationRequest | Objetivo, expediente/mission, snapshots, restricciones, presupuesto, origen automático/humano y actor |
| CollaborationCommand | Actor, acción, objeto/revisión esperada, payload, evidencia referida, razón e idempotencia; autoridad verificada por backend |
| WorkItem | Información/decisión requerida, responsable o rol, motivo, versiones y resolución; no confundir tarea con notificación |
| DecisionRecord | Decisión, actor/autoridad, política, alcance, evidencia y versiones exactas; efectos derivados |
| ImpactAssessment | Dependencias, conflictos, población, cobertura y condiciones de revalidación |
| RuntimeOperation | Identidad idempotente, efecto solicitado, estado consultable y resultado; timeout no significa que no ocurrió |

Feedback humano se registra como actividad tipada: comentario, objeción, hipótesis, restricción o decisión. No necesita otra entidad con lifecycle. Una opinión no se vuelve evidencia bancaria ni dato de entrenamiento válido automáticamente. «Se ve bien» no es autorización de release; el sistema necesita una decisión explícita con alcance verificable.

## 9. Estados, concurrencia e invalidación

Sustituir el enum de oportunidad que mezclaba progreso/evidencia por dimensiones separadas:

- Oportunidad: abierta, archivada o fusionada, con disposición y razón. Asignación/prioridad/evidencia son dimensiones aparte.
- Propuesta: borrador, en evaluación, evaluada o retirada. Resultado de evaluación: pass/fail/inconclusive; disponibilidad/dependencias aparte.
- Release: shadow, canary, activo, pausado o revertido. Autorización es una decisión referenciada, no prueba de eficacia.
- Job: en cola, ejecutando, esperando, terminado, fallido o cancelado. Su fallo no rechaza una hipótesis.
- Actualidad: vigente o requiere revalidación, con motivo/versiones afectadas.

El catálogo es un grafo de dependencias e impacto, no solo una lista. Un cambio de tool, conocimiento, política, suite o capacidad puede invalidar la compatibilidad vigente, sin borrar la evaluación histórica. Dos propuestas sobre el mismo árbol pueden necesitar evaluación conjunta o rebase. Aprobaciones aplican a revisiones exactas; no se heredan por nuevas versiones.

Workflows persistentes permiten reanudar/reintentar pasos con límites. Efectos externos requieren idempotencia y consulta de estado; retries no deben activar dos veces un release. No prometer exactly-once. Fusiones/divisiones preservan procedencia: mismo tema no garantiza misma causa.

## 10. Valor, límites y seguridad

Priorizar mostrando dimensiones: población elegible, beneficio estimado, esfuerzo/dependencias, riesgo, calidad de evidencia y costo de investigar. Evitar score opaco o inventar cifras faltantes. No optimizar costo de una interacción empeorando resolución/recontacto del episodio. Beneficio previsto, resultado posterior observado y estimación causal son distintos.

Oportunidades fuera de soporte —canal/core/proceso/comercial— se identifican y asignan al owner adecuado. Proponer un agente no repara la causa bancaria. «No cambiar», «evidencia insuficiente» y «solución externa» son resultados útiles.

Autonomía graduada por acción/riesgo: explorar y generar propuestas puede ser automático dentro de límites; efectos reales/publicación dependen de política y autorización. Políticas cubren datos, modelos, presupuesto, pruebas y releases. Su diseño no autoriza operaciones reales ahora.

Privacidad y permisos se aplican también al expediente, copiloto, consultas y notificaciones. Agregados y evidencia detallada pueden requerir distintos accesos. Evidencia revocada/eliminada se declara no disponible; no garantizar replay eterno. Texto histórico no confiable y conocimiento humano no son instrucciones privilegiadas.

## 11. Qué validar a continuación

Antes de endpoints o implementación, recorrer un episodio completo de colaboración: descubrimiento automático → pregunta humana → investigación revisada → dos alternativas → evaluación → decisión con alcance → seguimiento.

Primer corte recomendado: una mission, un expediente persistente, evidencia versionada, objeción/solicitud humana, dos alternativas y evaluación mediante adaptador explícitamente simulado cuando corresponda. Desde el inicio: permisos, límites, revisión esperada y procedencia. Grafo/incident response se definen como contratos y no se presentan como integraciones reales ya hechas.

Pendientes de acuerdo: usuario primario, asignación transversal, límites de autonomía por clase de acción, criterios de prioridad, política de interrupciones y alcance inicial de colaboración multiusuario. No son bloqueos para este mapa; sí condicionan el próximo diseño detallado.
