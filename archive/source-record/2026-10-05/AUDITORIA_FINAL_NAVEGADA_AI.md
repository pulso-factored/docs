# Auditoría independiente final — AI, Agent Core y evaluación

Fecha: 2026-10-01. Rol: ingeniería AI / integración Agent Core / evaluación adversarial. Alcance: lectura del spec V2 vigente y análisis de producto; contrastes puntuales con código upstream local. No ejecuté modelos, upstream, API o prototipo en esta revisión. La navegación online y su evidencia corresponden a la auditoría principal, no a esta nota.

## Veredicto

**Listo para comenzar implementación incremental con TDD, no prueba de integración ya funcionando.** No encontré un bloqueante nuevo que exija rediseñar la cadena autónoma descrita. Los puertos de identidad humana, executors y capacidades upstream no disponibles conservan estados bloqueados/simulados explícitos; no constituyen éxitos ficticios del producto. El primer corte debe demostrar el runtime task con inputs autorizados, razonamiento, salida tratada y receipt antes de ampliar roles.

## Lectura hacia delante y hacia atrás

| Paso | Contrato comprobado | Riesgo rechazado y prueba requerida |
|---|---|---|
| Fuente → detección | §§18, 24, 28: MetricSpec calcula; scout investiga; verifier independiente refuta; gate determinista decide elegibilidad | No precargar signal/labels ni ganador. Eliminar referencia evaluadora no altera entrada; alterar evidencia sí altera soporte |
| Investigación → propuesta | §§16–18: bridge construible, mismo outcome o proxy declarado, alternativas/do_nothing y precondiciones | Error humano repetido no es política; tool nueva sin executor queda dependency_blocked (§24.2) |
| Propuesta → objetos Core | §§17, 27, 29: EntityDraft, closure, semver exacta y hash evaluado; Flow/decide/agent | Schema válido no concede permiso; payload cambiado tras compiler exige nueva validación/grant |
| Ejecución del motor | §29.3/29.8: task descriptor, contexto privado, pin previo, single-flight y binding durable | Salida agent no se convierte en fact bancario/rule autorizado; revocación tras bootstrap detiene nueva acción |
| Objetos → evaluación | §§18, 29.8: dos gates, baseline sellada y pares aislados, oracle independiente | Pass Core no equivale a mejora Pulso. Unknown, cobertura diferencial y unsafe no fabrican subida condicional |
| Trial → decisión | §20.1/20.2: sandbox dev, oneOf input/fixture, resultado consultable y CAS por turno | No filtrar final_locked a trial/expert/debug ni convertir trial en KPI observado |
| Decisión → publicación | §§18, 20.2, 27: intención distinta de efecto, JWS fresco en dispatch, staging distinto de prod | Token vencido exige reautenticación; ACK perdido conserva unknown y readback antes de repetir |
| Resultado → memoria → detección | §§21, 28.4, 29.6/29.8: scratch libre/publicación gobernada, particiones/replay y aprendizaje posterior | No aprender futuro ni datos finales; candidato evolution no cambia su juez/guardrails |

## Hechos upstream comprobados

- `references/agent-core/agent_core/registry/suite.py`: suite vigente contiene 1–200 escenarios, 1–50 pasos, máximo 10 repeticiones; primer paso start único. Conforme con §29.8: no introducir 1.800 reproducciones como una suite única ni truncarlas silenciosamente.
- Existen implementaciones separadas de suite en registry/suite.py y registry/evaluation/suite.py; el spec distingue ambos wire y no presupone que la doble vara nueva sea el gate de RegistryService.
- Estas comprobaciones de fuentes no acreditan tests de integración ni smoke runtime.

## Condiciones a preservar, sin agregar servicios

1. U09/U17/U18/U19 deben demostrar engine/executor/harness real y receipts, no sólo shapes. Mock contractual permite avanzar pero se etiqueta.
2. U20-E/U36 cubren identidad negativa/acciones indebidas; policies/tools generadas no adquieren autoridad automáticamente.
3. Projection y links aplican partición/grant antes de leer; feedback/trial es entrada no confiable aun de experto autenticado.
4. U31 conserva baseline/oracle/guardrails externos; sensor candidato pasa shadow/new windows, no se activa por producir más hallazgos.
5. Disponibilidad del dato, reloj de replay, sesión humana y lease del job son fronteras diferentes; probar expiraciones/revocaciones/callback tardío.

Estas condiciones ya están especificadas/asignadas: son gates de construcción, no pendientes que exijan nueva arquitectura. El spec no debe crecer para sustituir primeras pruebas verticales. La revisión global debe confirmar que cambios de navegación no debilitan estas barreras.

## Segunda pasada: evidencia publicada versus contrato

Contrasté la versión actual de `AUDITORIA_NAVEGADA_PRODUCTO.md` con §§18, 20, 24, 28 y 29; esta pasada no sustituye navegación propia.

- **Autonomía:** la propuesta visible del diseño no convierte su apertura en trigger; GET abre una proyección, scheduler/sensores investigan por debajo, y trials/feedback son opcionales. Sin aprobación de release el éxito autónomo es candidato evaluado listo para decisión, no publicación ficticia. Conforme al objetivo del producto.
- **Aprender del copiloto y del humano:** las consultas repetidas de E0 y los intentos de asistencia/acciones externas sugieren tool/Flow/contexto. La frecuencia abre investigación, no convierte respuesta frecuente en verdad. Edición/aceptación/envío requieren procedencia separada de execution receipt y outcome maduro. Los eventos `assistance_suggested`/`assistance_sent` y `human_action_recorded` son la extensión externa, no EngineEvent inventado.
- **Mitigación y cierre:** árbol que bloquea una tarjeta y abre reclamo puede completar ese subobjetivo y escalar la disputa aún pendiente. §24.1 y MetricProjection conservan outcome por objetivo, estado operativo y continuidad; no atribuyen ahorro/resolución bancaria al cierre del chat.
- **Árbol, evaluación y trial:** Flow es artefacto nativo, no Agent obligatorio. Comparación de ejemplos no sustituye suite; trial interactivo usa sandbox dev, no final ni producción. La exposición gradual del diseño conserva capacidad unsupported/simulated hasta recibo real de plataforma; publish staging no implica prod/canary.
- **Cuatro ojos:** nota publicada de cambio de permisos+activación coincide con tres autoridades separadas y policy de separación de funciones; selector de rol no es autorización.

No aparece un gap AI nuevo confirmado en esta evidencia. Detalle a materializar en schemas/tests de U29/U30, sin ampliar servicios: representar explícitamente rechazado/editado/no enviado cuando la fuente lo entregue; si no lo entrega, cobertura unknown, nunca inferir aceptación de un silencio. El contrato ya prohíbe equiparar estos estados con efectos; este recordatorio evita perderlo al producir fixtures.

La nota navegada aún declara pendientes variantes lazy-loaded y recorrido completo evaluación/árbol. Mi veredicto AI no acredita esos pendientes visuales ni permite cerrar el objetivo global por sí solo.
