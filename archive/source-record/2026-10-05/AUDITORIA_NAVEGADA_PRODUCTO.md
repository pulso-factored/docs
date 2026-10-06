# Auditoría del artefacto publicado — cierre contractual

Fuente: https://claude.ai/artifact/ASnUw7wFmaY5EULgTbCUud. Fecha: 2026-10-01. Evidencia de navegación del principal; no acredita implementación ni métricas reales.

## Inventario publicado

El selector del visor muestra 77 artboards: demo 9, acceso 15, analista 21, supervisora 8, automatización 8, administración 4, app del cliente 8 y paleta 4. Inventario no equivale a cobertura de pruebas.

## Evidencia confirmada

- Analista: abierto en modo full screen, visto visualmente el centro de trabajo y cambiado Copiloto→Herramientas. La selección cambia el panel y muestra acciones realizadas, acciones que requieren confirmación/identidad y consultas de lectura con auditoría. Contraste: §§20/24; no convertir sugerencia en efecto ni delegar autoridad financiera al motor.
- Automatización: leídas las ocho pantallas renderizadas del canvas y vista visualmente la propuesta en full screen. Se distingue evidencia histórica, comparación humano/agente, holdout, prueba adversarial, autorización y exposición gradual. Contraste: §§18/20/27/29. Las cifras son ejemplos, no resultados ejecutados.
- Árbol publicado: distingue cerrar consultas de mitigar y pasar; conserva hechos verificados y cuestiones pendientes. Coincide con §24; no inferir resolución por tarjeta bloqueada o reclamo abierto.
- Anotación de roles: quien cambia permisos y activa un agente que los usa requiere otra persona aprobadora. Debe seguir comprobándose autoridad efectiva, no sólo una etiqueta de rol.
- Nueva sesión del navegador: vuelto a abrir el grupo demo y leído el primer contacto y centro de trabajo; las otras áreas e interacciones se contrastaron en el recorrido adicional registrado abajo.

## Revisores independientes y correcciones

### Recorrido adicional publicado

- Supervisión: leídos equipo/colas y auditoría; vista full screen solicitud de analista, probado filtro Todas→De analistas (lista cambia correctamente). No ejecutadas aprobaciones financieras. La auditoría distingue juez/árbol/AI/persona, lectura/cambio y servicio de identidad que descarta respuestas. Contraste §§9/20/24: logs auxiliares no sustituyen hechos durables; aprobación financiera no es release.
- Defectos visibles en esa solicitud: nota inicial `[object Object]`; hora de solicitud 10:30 frente a verificación citada 11:12. Son problemas del prototipo, no evidencia válida de causalidad. Añadido contrato/test de texto y evidencia temporal en §20.2. No se modifica artefacto externo.
- Administración: leídos usuarios/roles y herramientas/permisos; retención vista full screen. Separación de cuatro ojos y permisos en executor, no prompt. Retención está rotulada propuesta pendiente de validación: sus años/cadencias no son autorización regulatoria vigente. Contraste §§19/21/24.2.
- App: seguimiento visto full screen, navegados Seguimiento→Soporte→Movimientos→Detalle→Pedir ayuda. El movimiento acompaña el contacto; respuesta solicitada no significa nueva queja ni identidad validada. Reclamo pendiente, primera respuesta y resolución final son estados distintos. Coincide con §24; plazo de 15 días del fixture no se universaliza.
- Acceso: inventariados 15 estados; leídos login y segundo factor, visto full screen bloqueo de cuenta. No ingresadas credenciales ni ejecutado login/reset. Microsoft/OTP es plataforma externa, no módulo nuevo del motor. Límites 5 intentos/15 minutos son fixture/política externa, no grant implícito.
- Paleta: vistos los cuatro artboards en canvas, incluidas variantes salvia/azul/lima y tokens de colores/tipografía. Salvia figura elegida. Etiquetas acompañan color en estados. No se acredita contraste WCAG con captura ni prueba de teclado.

Se han visitado los ocho grupos entre las sesiones, con interacciones representativas verificadas. No se afirma que todos los 77 controles/artboards hayan sido probados: esta revisión del contrato no es una certificación exhaustiva del prototipo externo ni reemplaza el E2E del producto construido.

### Pruebas y árbol: recorrido cerrado

Abierto sandbox full screen; cambiado escenario acceso a otra persona→tool falla→portugués: conversación y explicación cambian de forma visible. Tool falla muestra handoff sin inventar datos; idioma cambia respuesta. Navegado enlace continuar→activación; tres gates aparecen aprobados aunque sólo se observaron dos escenarios en esa sesión. Esto confirma que el prototipo representa fixtures, **no** que ejecuta suites o calcula gates. §20 exige receipts/TrialProjection, §27 no inventa canary y §29 separa dev/final; no adoptar ese botón como juez.

Navegado activación→árbol y seleccionada rama pago pendiente >48h: cambian condiciones, acciones, contexto entregado, asunto abierto y métricas de evaluación. La rama dice En prueba/sin clientes reales pero texto genérico dice activada por Automatización: inconsistencia de presentación del fixture, no recibo de publicación. 88% correctos offline no equivale 88% resueltos productivos. Spec conserva validation/environment separados y gates de receipts. No se pulsaron Activar, Pausar ni acciones bancarias.

## Auditoría de cumplimiento del objetivo

| Requisito | Evidencia actual | Límite |
|---|---|---|
| Navegar enlace y distintas experiencias | Ocho grupos visitados; full screen analista/propuesta/supervisión/retención/cliente/acceso/árbol, paleta en canvas; cambios de panel/filtro/escenario y rutas verificadas | No todas las variantes/control ni login/pagos |
| Leer hacia producto→spec | Hallazgos y cruces §§9/18/19/20/24/27/29 arriba | Cifras y permisos del fixture no son autoridad real |
| Leer hacia spec→producto | Contratos de async/receipts/reauth no se prueban por pantallas estáticas; se mantienen tests obligatorios; plataforma externa no se reconstruye | No se acredita runtime |
| Corregir brechas | Reauth; divulgación acumulada; restore; texto/notas y temporalidad | Gates de tests futuros explícitos |
| Revisiones por roles y rechecks | Informes backend/front, AI/Core, data/infra y rechecks independientes sobre cambios | Dictámenes documentales, no ejecución |
| Verificar estructura y plan | PASS 30 secciones/links/tablas/fences; PASS DAG 46 unidades acíclicas | Checks estructurales no prueban semántica |

Los cuatro frentes y sus rechecks concluyen que no quedan bloqueos documentales para comenzar implementación incremental. El recorrido representativo de evaluación/árbol está registrado arriba. El spec está listo como contrato de construcción sujeto a aprobación del usuario; no se declara listo para producción ni implementado.

Backend pidió vincular reautenticación a comando/actor/target/operación sin segunda decisión. Data/infra pidió control acumulado de divulgación SQL y objetivos RPO/RTO medidos por restore drill. Se incorporaron a §§19/20.2 y sus rechecks independientes los dan por cerrados documentalmente. AI/Core no detectó bloqueo nuevo y una segunda pasada confirmó separación de autonomía, sugerencias, efectos y resolución. Backend rechecked además notas/temporalidad. Los informes distinguen revisión documental de navegación:

- [Backend e integración frontend](AUDITORIA_FINAL_NAVEGADA_BACKEND.md).
- [AI/Core y evaluación](AUDITORIA_FINAL_NAVEGADA_AI.md).
- [Data, seguridad e infra](AUDITORIA_FINAL_NAVEGADA_DATA_INFRA.md).
- [Frontend/product engineering](AUDITORIA_FINAL_NAVEGADA_PRODUCT_ENGINEERING.md).

Validación final estructural: PASS sobre 1.543 líneas y 30 secciones, fences/tablas/links locales; DAG PASS, 46 unidades únicas, referencias existentes y sin ciclos. No prueban semántica ni runtime. Rechecks independientes cerrados. No hay hallazgo pendiente que requiera rediseño antes de P0; cada gate de seguridad, proveedor, integración y despliegue se materializa mediante TDD en el corte correspondiente.
