# Alcance de implementación: detección y automejora

Fecha: 2026-10-01. Autoridad: aclaración directa del usuario.

## Decisión

Nuestro producto de ingeniería es el servicio de detección y automejora. Integra las primitivas, runtime y artefactos del Agent Core del equipo; no reimplementa Agent Core ni construye un gateway LLM. Infra se versiona en https://github.com/pulso-factored/infra.git. Checkout local `infra/`, con ese origin. Su frontera es Terraform y recursos AWS de despliegue: red, IAM, state, compute, datos administrados, observabilidad y runbooks de despliegue; no el stack local ni el CI de integración del motor.

El repo del servicio confirmado es https://github.com/pulso-factored/improvement-engine.git, clonado vacío en `improvement-engine/`. `pulso-engine` era un nombre propuesto, no otro repo pendiente.

## Entorno: Windows primero

Decisión explícita del usuario: desarrollar y probar inicialmente en Windows/PowerShell. No migrar automáticamente a WSL ni alterar el entorno Standar. Evaluar WSL sólo después de documentar incompatibilidades importantes y alternativas Windows. Contenedores Linux necesitan backend Linux de Podman; usar su VM desde Windows no significa trasladar repos ni comandos de desarrollo a una distribución WSL.

Preflight inicial: Git, Rust/Cargo, Python, Node, uv y Podman disponibles. Terraform y just no aparecen en PATH (no demuestra ausencia total). Podman no muestra máquinas ni conexiones configuradas y no conecta al backend, comprobado también fuera del sandbox. No se inicializó VM ni se instaló tooling. Versiones detectadas no equivalen a compatibilidad validada con Core o a versiones elegidas para lockfiles.

## Fronteras

- Propio: ingesta/datos tratados, detección, investigación, memoria, propuestas compatibles, evaluación/gates del motor, API de visibilidad, debugging y operación de ese servicio.
- Propio de `improvement-engine`: manifests/fixtures, Podman Compose, PostgreSQL efímero de CI, LocalStack y perfiles de desarrollo/prueba. Estos recursos se versionan y prueban junto al consumidor que los necesita.
- Propio de `infra`: módulos y entornos Terraform, OIDC/IAM, state, despliegue, monitoreo/alarmas y runbooks AWS. No contiene un workflow reutilizable ni contenedores que ejecuten las pruebas del motor.
- Externo: ejecución de agentes/flows/Jev y configuración de proveedores en Agent Core; atención bancaria, herramientas/autoridades de plataforma; gateway de modelos si el ecosistema ofrece uno.
- Integración mediante adapters y contratos mínimos. No se asume gateway desplegado ni protocolo sin verificar al dueño. Capacidad faltante: simulador de contrato etiquetado o dependency_blocked, no construcción silenciosa del servicio vecino.
- Tratamiento/egreso, presupuesto, timeouts y receipt del uso siguen siendo responsabilidad verificable del consumidor. Si una dependencia no garantiza un gate necesario, se bloquea la ejecución correspondiente.

## Reconciliación antes de implementar

1. Reemplazar crate/servicio/proxy propio de §§4/23 por integración externa, sin segundo runtime.
2. Retirar imágenes, IAM, despliegues y CI del gateway propio; infra sólo administra el despliegue de nuestro servicio, no sus dependencias de laboratorio.
3. Reconducir U10 a conformidad/uso de proveedor externo vía Core; revisar P1-B, manifest, DAG y gates. No borrar gobierno de datos.
4. Confirmar endpoint/perfil/modelos y presupuesto disponibles con el equipo; secretos fuera del chat.
5. Revisar independientemente alcance/contratos y validar el plan modificado. El cierre del spec anterior no acredita este plan nuevo.

No se crearon commits, PRs, workflows ni recursos cloud en esta operación.

## I03 — Corrección de ownership de infraestructura local y CI

**Decisión:** cada repositorio prueba su propio producto. `improvement-engine` contiene y ejecuta su Compose, fixtures, PostgreSQL efímero, LocalStack y workflow de integración. `infra` no expone workflows reutilizables al motor ni conserva una segunda definición de esas dependencias; su CI sólo verifica Terraform y operaciones de infraestructura.

**Motivo:** un workflow PostgreSQL alojado en `infra` para tests de `improvement-engine` introdujo permisos GitHub entre repositorios, un SHA externo y una configuración organizacional como prerequisitos de cada PR. Esa dependencia falló antes de ejecutar el test y no aportaba confianza adicional sobre Terraform ni sobre el motor.

**Trade-off:** se duplica la responsabilidad de mantener los pins de imágenes locales frente a los módulos Terraform, pero se elimina el acoplamiento de release/CI. La coherencia necesaria se controla con contratos de interfaz y manifiestos de despliegue; no compartiendo un workflow. Si una imagen o variable debe coincidir por requisito de despliegue, `infra` consume un manifest aprobado del motor, no se vuelve dueño de su harness.

**Migración:** I03 mueve `local/`, scripts de doctor y el job PostgreSQL al repositorio del motor; elimina el caller cross-repo y cualquier referencia a SHA de workflow de `infra`; después se retira el acceso reusable otorgado a `infra` y se eliminan los recursos locales duplicados de ese repo. El PR de migración debe incluir una regresión que pruebe que el workflow del motor levanta PostgreSQL y ejecuta la migración sin secretos ni `uses: pulso-factored/infra/...`.
