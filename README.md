# Pulso technical documentation

Technical documentation for the Pulso platform services (English).

| Service | Document | Source commit (`origin/main`) |
|---|---|---|
| data-pipeline | [data-pipeline/README.md](data-pipeline/README.md) | `0291edf` (infra `246ddf8`) |
| tool-service | [tool-service/README.md](tool-service/README.md) | `64c36bc` (infra `246ddf8`) |
| agent-core (includes the registry in depth) | [agent-core/README.md](agent-core/README.md) | `eb33f5c`, later changes through `da491b1` (infra `246ddf8`) |
| improvement-engine | [improvement-engine/README.md](improvement-engine/README.md) | documentation snapshot; implementation claims pinned in the guide |
| infra | [infra/README.md](infra/README.md) | documentation snapshot; Terraform status is explicitly qualified |

Each service document has an executive summary, quick facts, mermaid architecture diagrams, an AWS infrastructure and deployment section with an element inventory (declared / wired / applied), a list of documentation discrepancies, and a list of items that were not verified.

The [source record archive](archive/README.md) contains a sanitized snapshot of the project-level working documents and historical records. It excludes private Nexus receipts and binary repository bundles.
