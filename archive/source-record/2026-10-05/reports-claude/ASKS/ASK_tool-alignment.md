# ASK a agent-core y tool-service: alinear las definiciones de tools (registry-e2e vs `GET /v1/tools`)

Verificado el 2026-10-05 contra `origin/main`: agent-core `2ad5d08` (`tests/fixtures/registry-e2e/tools/`) y tool-service `64c36bc` (`registry/tools/`, que su test `test_registry_export` mantiene igual a su `CATALOG`, la fuente de `GET /v1/tools`).
Herramienta: `scripts/contracts/tool_alignment/check_tool_alignment.py` en improvement-engine (rama `claude/sig1-platform-signals`). Compara ToolDef de fixtures con el listado del proveedor y falla ante drift nuevo. 19 hallazgos conocidos quedan registrados en `known_drift.json`, cada uno con el ask que lo cubre.

**Por que importa.** El motor compila "enlaces de tool" (artefacto `tool_link`, ART2) y los rechaza si el `source` de la tool no coincide con el del proveedor (`source_mismatch`) o falta (`source_missing`). Ademas, `FieldClassifier` de agent-core decide que ve el modelo a partir del `source` que devuelve el servicio. Con los fixtures actuales el motor rechaza todo enlace sobre 5 de las 6 tools servidas, y el modelo no puede pasar argumentos que el servicio si acepta.

## A1. agent-core: `source` de los ToolDef de registry-e2e

| Tool | fixture agent-core | tool-service (oraculo) |
|---|---|---|
| `leer_productos` | `productos` | `customer_products` |
| `leer_movimientos` | `movimientos` | `customer_transactions` |
| `leer_pqr_cliente` | `pqr` | `customer_cases` |
| `obtener_pqr` | (falta) | `customer_cases` |
| `buscar_transacciones` | (falta) | `customer_transactions` |
| `radicar_pqr` | (falta) | `customer_cases` |

(`radicar_pqr` no estaba en la lista de ART2: tambien le falta `source`.) Cambio: poner el `source` del proveedor en cada ToolDef del fixture. Aditivo; no cambia el contrato.

## A2. agent-core: `args_schema` de esos ToolDef

Los fixtures declaran `additionalProperties: false` con `properties: {}` (o sin propiedades) mientras tool-service acepta y declara, por ejemplo: `leer_productos.limite`, `leer_pqr_cliente.limite`, `leer_movimientos.limite` (con `default: 10`) y `product_id`, `obtener_pqr.idempotency_key` (requerido), `radicar_pqr.transaction_id` y `descripcion` (ambos requeridos), `buscar_transacciones.{texto,desde,hasta,monto_min,monto_max,limite}`. Si agent-core valida los argumentos del modelo contra el ToolDef, el modelo no puede usar esos argumentos; si no los valida, el fixture miente. Cambio: copiar el `args_schema` del listado del proveedor. El archivo `scripts/contracts/tool_alignment/aligned_tool_defs.json` del motor es exactamente ese resultado (datos, no codigo).

## A3. agent-core: `leer_perfil`

tool-service sirve `leer_perfil` (`customer_profile`); registry-e2e no la declara, asi que ningun flujo puede usarla. Pedir: declararla en el fixture, o decir que es deliberado.

## T1. tool-service: mantener `GET /v1/tools` como oraculo y publicar su clasificacion de `source`

Lo unico que solo ustedes pueden dar: (a) congelar en `contracts/` un export versionado de `GET /v1/tools` (hoy `contracts/tool-provider.openapi.json` describe la forma, no el catalogo), con un check de CI como el de `export_contract.py --check`; (b) confirmar que el `source` (nombre de tabla) es parte del contrato estable y que un cambio de nombre se anuncia con version; (c) decir si las tools de agent-core (`convertir_moneda`, `leer_transcript`, `obtener_handoff`, `seleccionar`) seguiran fuera del proveedor (el motor asume que si: son del runtime, no hallazgo).

## Que hizo el motor (sin tocar nada de ustedes)

- Datos alineados aditivos en el motor: `aligned_tool_defs.json` (ToolDef de agent-core con la vista del proveedor) y los dos snapshots con SHA.
- Check ejecutable: `python scripts/contracts/tool_alignment/check_tool_alignment.py --fixtures <dir de ToolDef YAML|snapshot.json> --provider <listado.json> --baseline known_drift.json`, o `--provider-url http://host:port --token-env <VAR>` para un `GET /v1/tools` real (un solo GET; el token sale del entorno y no se imprime). Sale 1 con drift nuevo y 1 con entradas de baseline que ya no son ciertas (cuando ustedes corrijan, la baseline debe encogerse).
- Limite honesto: el listado de tool-service usado es el snapshot de su `registry/tools`, no una llamada en vivo (el servicio exige dataset para arrancar completo; el listado en si no lo usa).
