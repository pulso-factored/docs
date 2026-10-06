# ASK al equipo agent-core: principal asesor en escenarios de `evaluate`

Verificado contra `origin/main` de agent-core (`5e3fef9`, clon `tmp/shared/agent-core`).

**Problema.** El copiloto (`copiloto-asesor`, `invocable_by: [advisor]`, `subject_kinds: [customer]`;
`tests/fixtures/registry-e2e/agents/copiloto-asesor@1.0.0.yaml:5-7`) no se puede evaluar de forma nativa:

- `agent_core/composition/evaluation.py:95` fija el principal del escenario en `"type": "customer"`.
- `engine.start_run(principal, None, ...)` y `engine.handle_turn(principal, None, ...)` pasan `on_behalf_of=None`
  (`evaluation.py:121-131`) y el `RunInput` no lleva `subject` (el campo existe, `domain/turn.py:38`).
- `ScenarioPrincipal` solo acepta `id` y `attrs` (`agent_core/registry/suite.py:70-72`) y el modelo base es
  `extra="forbid"` (`suite.py:34-35`): un escenario con `type` o `subject` es rechazado.

Sin `OnBehalfOf` ni sujeto el escenario no representa a un asesor actuando sobre un cliente (`domain/identity.py`, `grantee` debe ser advisor); hoy solo se evalúan agentes de cliente y Pulso no puede medir regresiones del copiloto.

**Cambio mínimo aditivo propuesto.**

1. `ScenarioPrincipal`: agregar `type: Literal["customer","advisor"] = "customer"` y
   `subject: {kind, ref} | None = None` (opcional; para `advisor` obligatorio, validado en el modelo).
2. `Evaluator._principal`: usar `scenario.principal.type`; para `advisor` construir un `OnBehalfOf` sintético
   (`subject`, `grant_ref="eval"`, `grantee=PrincipalKey(advisor, id)`, `exp`=ahora+1 h) y pasarlo a `start_run`/`handle_turn`
   en lugar de `None`; para `customer` el comportamiento no cambia.
3. Los escenarios existentes siguen siendo válidos (sin los campos nuevos), sin cambio de hash de las suites ya
   publicadas si los campos por defecto se omiten al serializar.

**Pruebas sugeridas:** un escenario `type: advisor` contra `copiloto-asesor` arranca y responde; sin `subject` se
rechaza al validar la suite; los escenarios `customer` existentes dan el mismo resultado.

**Impacto para nosotros:** hasta que exista, `export-suite` de la batería deja fuera al copiloto (solo disputas,
consultas, recepcion).
