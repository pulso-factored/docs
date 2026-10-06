# Revisión Agent Core — 01/10/2026

Auditoría documental del agente principal. Pin `53e729d624c8284e906249df84c1a1df84cc8d40`, fast-forward desde 98d3836. No tests ejecutados ni integración certificada.

| Evidencia fuente | Conclusión y corrección |
|---|---|
| contracts/VERSION y domain/version.py = 0.5.0; docs transferencia = 1.2.0 | Versionado inconsistente: pin por SHA/digest; no afirmar downgrade compatible |
| composition/serve.py y serve_registry.py | Servidor arrancable y registry opt-in existentes; corregido spec que los listaba inexistentes |
| registry/http.py verifier opcional + staff_verifier en serve | Emisores staff/client separados soportados; aún deben probarse/configurarse en nuestro despliegue |
| knowledge/service.py, nodes.py y composition/engine.py | read/citas implementados e inyectables; navigate no ejecutado, source no cableado por serve |
| registry/candidate.py REG-KNOWLEDGE | Snapshot nuevo no publicable mediante propuesta actual; wiki libre independiente |
| composition/builder_tools.py, actions/manager.py, flows/draft_schema.py | write_draft y cambios schema exactos habilitan construcción autónoma con act→verify |
| registry/service.py get_write/key y registry/http.py | Idempotencia/readback interno no equivale a endpoint REST; tabla de recuperación conserva esa diferencia |
| registry/quotas.py y service.py | Topes auto_detect 10/24 h y 20 evaluaciones por defecto; costo pendiente |
| registry/entities.py importa registry.suite; evaluation/suite.py y gate.py existen aparte | Dos familias de suite/gate; wire disponible antiguo, ADR0020 no integrado al servicio |
| domain/transfer.py, nodes.py, turn/engine.py frente a entities.Agent/Agent.json | Transferencia parcial sin routing/accepts de Agent en este snapshot; no extrapolar tests de rama a runtime listo |
| agent LLMAgentPort/input_view y G0-22 | Entrada explícita y salida no autoritativa; draft es excepción acotada, no libertad de escritura bancaria |

V2 §29 describe el runtime propio de automejora con Agents/Flows/Core, control plane Rust, escenarios E0 y pruebas granulares. El adapter de salida de facts y tools SQL/wiki debe construirse bajo permisos y contratos explícitos. No se promete HTTP de results inexistente, grupos task nativos, publicación autónoma, canary ni autoaprobación del propio detector.

Validación realizada: inspección de símbolos, imports y schemas JSON, fences/enlaces Markdown. Validación pendiente: instalación Python 3.12/dependencias, pytest/contract regeneration/import smoke/serve smoke y E2E real. El spec conserva estado propuesto, pendiente de aprobación.
