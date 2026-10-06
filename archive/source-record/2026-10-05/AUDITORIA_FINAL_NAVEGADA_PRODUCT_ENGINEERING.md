# Auditoría final independiente — frontend y product engineering

Fecha: 2026-10-01. Fuentes leídas: `AUDITORIA_NAVEGADA_PRODUCTO.md` y `TECH_SPEC_PULSO_AUTOMEJORA_V2.md`, §§20, 24, 25, 29 y 30. La navegación fue realizada por el principal, no por este revisor. El informe no acredita implementación, pruebas runtime ni cobertura de los 77 artboards.

## Veredicto

**Listo para comenzar implementación incremental en los frentes revisados.** No queda bloqueo de contrato frontend/product engineering tras incorporar y revalidar las precisiones de §25. Esto no es aprobación de despliegue ni de un producto ya construido: cada corte requiere RED→GREEN, integración real y revisión independiente.

El éxito sigue siendo detección no dirigida → evidencia → propuesta Core → evaluación independiente → autoridad excepcional cuando corresponde → aprendizaje. No es un wizard y no requiere implementar F7/F8.

## Contraste publicado → spec

| Evidencia registrada por el principal | Resultado del contraste |
|---|---|
| Copiloto/herramientas y acciones con identidad/autoridad | §24.1 separa sugerencia, envío, permiso y efecto; el motor no ejecuta operaciones financieras. Conforme. |
| Evidencia/comparación/pruebas/activación gradual | §20.1 ofrece expedientes, comparación, trial, readiness y decisiones. `simulated/unsupported` impide confundir selector de exposición con despliegue real. Conforme; números del diseño no son resultados. |
| Nota `[object Object]` y verificación posterior a solicitud | §20.2 exige texto tratado y evidencia temporal diferenciada. Corrección contractual suficiente; no se afirma haber corregido el artefacto externo. |
| Movimiento → contacto → respuesta solicitada | §24 distingue requested_reply, mitigación, cierre y resolución, sin inferir identidad o fallo. Conforme. |
| Permisos, aprobación financiera y activación separados | §§20.2/24 exigen autoridad por objeto/operación, step-up y revocación. Roles visibles no son grants. Conforme. |
| Paleta con texto junto a color | Es referencia visual, no certificado WCAG. La consola propia tiene aceptación verificable en §25. |

## Hallazgos y revalidación

**PE-01 — cursor purgado. Cerrado.** Inicialmente §25 exigía recuperación de gaps sin fijar explícitamente el caso after_sequence purgado. §29 ya contenía `410 cursor_expired`; el nuevo párrafo de §25 lo aplica a la consola, con snapshot/cursor autorizados, cobertura parcial por retención, aislamiento y recuperación sin bucle. No necesita otro protocolo ni otra tabla. U07/U24 deben ejecutar sus tests antes de aceptación; el cierre es documental.

**PE-02 — accesibilidad/foco. Cerrado como contrato.** El nuevo párrafo de §25 fija teclado, foco del panel/restauración, alternativa textual al grafo, estados sin color exclusivo y anuncios acotados sin robar foco/scroll. Esto hace observable la aceptación y evita que SSE convierta navegación en re-render destructivo. Las pruebas browser siguen pendientes de implementar; una captura o chequeo automatizado aislado no las acredita.

**Stack frontend. Definido; sin hallazgo.** Aunque §4 sólo presenta debug-console, el contrato browser de §29 fija React/TypeScript/Vite, lockfile, Vitest/Testing Library y Playwright. También fija sesión same-origin, CSRF y SSE sin JWT en URL. No hace falta añadir otro framework, BFF o decisión abierta; el equipo debe usar esa definición existente.

## Definiciones suficientes para construir

- 202/CommandRef/status separan aceptación de ejecución; responded no es succeeded y unknown exige reconciliar.
- Step-up mantiene el mismo comando/actor/target/operación; callback duplicado no genera otra firma ni dispatch.
- Trial dev tiene CAS por turno, aislamiento y readback sin contaminar KPI ni final_locked.
- Revisiones de dominio/proyección, fuente/calidad/denominadores y razones están separados; la UI no debe inventar éxito ni conflictos.
- Debug es consola real de ingeniería, no atención; grants técnicos no heredan aprobación financiera/Registry.
- U24 y detalles U32 son cortes incrementales con dependencias explícitas, no una historia gigantesca de todas las pantallas.

## Aceptación por corte

| Corte | Preparación documental | Evidencia de implementación exigida |
|---|---|---|
| U07 | Listo | API/PG/stream reales, duplicado/gap/410/tenant/reconnect |
| U24 | Listo | API real + browser E2E de navegación, foco, scroll, degraded y a11y |
| U32 y variantes | Listo por tipos | Receipts autorizados, redacción/holdout y fallo de dependencia |
| U34 y sucesores | Listo | CAS/idempotencia/receipts; pausa/cancel sin fingir ausencia de efecto externo |
| F7/F8 | Externo al motor | Contract-consumer y simulador, no implementar 77 artboards |

## Límites

Revalidación de cierre: el registro actualizado documenta sandbox full screen, cambio visible de escenarios de fallo de tool/idioma, navegación a activación y selección de rama de árbol de pago pendiente >48h. Es evidencia suficiente para cerrar el contraste contractual representativo de evaluación/árbol: también identifica gates preaprobados e inconsistencias de estado como fixtures, no resultados ejecutados. No se probaron los 77 artboards/controles ni se pulsaron acciones de activación o bancarias. Este informe no certifica accesibilidad del prototipo, seguridad, rendimiento, CI ni runtime. Aprueba claridad y viabilidad del contrato en el frente revisado, no sustituye auditorías AI/data/backend/infra ni las pruebas futuras.
