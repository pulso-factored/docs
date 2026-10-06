# ASK a agent-core: seguimiento de `serve` tras el ensayo prod-like (imagen de los PR 62 a 70)

De: equipo del motor de mejora / infra (Claude, lane PRODLIKE). Fecha: 2026-10-05. Para reenviar al equipo de agent-core.
Base probada: `origin/main` `edd65df` (merge del PR 70), imagen construida con su `Dockerfile` (podman, `linux/amd64`, 316 MB, 40 s en frio), compose de infra (`deploy/hackathon/core/compose.agents.yaml`) con `serve` como `agent_app`, Postgres 16 con roles separados, llm-gateway real (mimo flash), tool-service con una publicacion SINTETICA, `AGENTCORE_ALLOW_DOUBLES` sin definir (el arranque dice `serve mode=production`). Resultados completos y evidencia en `PRODLIKE_SERVE_RESULTS_2026-10-05.md`.

Lo que funciono y no hay que tocar: `/healthz` y `/readyz` por dependencia (postgres, keys, schema, llm_gateway, tool_service), DB caida (503 y `/healthz` 200) y recuperacion sola, variable requerida ausente (salida 2, nombra la variable, no imprime valores), SIGTERM con gracia (el turno en vuelo termina), credencial `builder` minteada por el motor aceptada y limitada (crear 201, aprobar/publicar 403, firma ajena 401), exportacion de runs y linaje.

Orden de prioridad: A1 bloquea el flujo de transferencia, el flujo de disputas y toda `eval_suite` sobre `serve`.

## A1 (P0, bloqueante). El proveedor `classifier` exige la clave `text`; los nodos `decide` entregan vistas con clave por ruta

Sintoma sobre `serve` (modo produccion, fabricas reales, artefacto `sintetico` de `scripts/serve_state.py`):
- `recepcion`: cualquier mensaje de disputa o consulta termina en «No entendi bien que necesitas» (nunca transfiere). Probado con tres frases cuyo vocabulario esta en el artefacto («disputa cargo reconozco duplicado»); fuera de `serve`, el clasificador da 0.98 para `disputas` sobre esas frases.
- `disputas` directo: `match-cargo` no puede elegir cargo, el run no pasa de «pide aclaracion».
- `POST /v1/registry/proposals/{id}/evaluate` con `disputas-suite@1.0.0`: `{"verdict":"failed_infra","detail":"HarnessUnavailable: un proveedor de decision fallo durante el escenario: ['classifier']"}` (1 s, sin llamar al LLM).

Evidencia del mecanismo: el evento `decision_made` de `elegir-especialista` trae `provider_used: "none"`, `fallback_depth: 1`, `value: {}`. En proceso, con el mismo artefacto: `ClassifierProvider.predict(spec, {"slots.problema": "disputa cargo reconozco", "facts.directorio.value.entries": []}, {}, "es")` lanza `ProviderError: classifier: la entrada necesita 'text' (string)` (`agent_core/decision/providers/classifier.py`, `predict`). `handle_decide` → `_decide_choice` arma el diccionario con `model_inputs(cfg.input_view)`, cuyas claves son las rutas completas (`slots.problema`), asi que `text` nunca existe. Los dobles de la demo lo ocultan porque no pasan por este proveedor.

Peticion precisa:
1. Que el proveedor reciba el texto sin depender de una clave magica: por ejemplo `config.text_from: slots.problema` en el decision model, o concatenar los valores `str` de la vista (en ese orden) cuando no hay `text`. Aditivo, sin cambiar hashes publicados.
2. Un test de composicion en modo `serve` (fabricas reales, sin `testing.*`) que corra: `recepcion` -> transferencia a `disputas` con una frase del vocabulario del artefacto sintetico, un turno de `disputas` que elija un cargo (`match-cargo`) y una `evaluate` de `disputas-suite` con veredicto distinto de `failed_infra`. Hoy ninguno de los 3,235 tests cubre esa combinacion.
3. Verificar tambien el campo `problema`: nuestro catalogo sintetico lo clasifica `untrusted_text` (agregado a mano porque `scripts/e2e/field-overlay.json` no lo trae, ni `descripcion_cargo`, `radicado`, `pedido`); sin clasificar es `pii_direct` y llega tokenizado al clasificador. No pudimos comprobar si hace falta mientras A1 siga abierto: incluirlo en el overlay del repo y en el test del punto 2.

## A2 (P1). `/readyz` no ve artefactos faltantes y el fallo sale como 500

Con `AGENTCORE_CLASSIFIER_ARTIFACTS_DIR` apuntando a un directorio sin `sintetico.json` (error nuestro de montaje), `/readyz` respondio 200 `ready` y cada turno de `recepcion` devolvio `500 internal_error` (log: `DecisionConfigError en classifier.py:125`, 7 de 7 turnos). Pedimos: (a) un chequeo `artifacts` en `/readyz` que verifique, para las releases `prod` de `AGENTCORE_SERVE_AGENTS`, que las calibraciones (`thresholds_from`) y los artefactos de clasificador referenciados existen y parsean; (b) que `DecisionConfigError` en un turno salga como problema tipado (por ejemplo 503 `artifact_unavailable` con el nombre del artefacto, no su ruta), no como 500 generico.

## A3 (P1). Sin `AGENTCORE_LANG_THRESHOLDS` el idioma nunca cambia; el compose de referencia y el kit no lo incluyen

`docs/serve-env.md` lo dice («sin el, el idioma nunca cambia»), pero el fixture `language_detection` apunta a `thresholds_from: lang-cal-demo` y ni `deploy/compose/docker-compose.yml` ni `scripts/serve_state.py` aportan el archivo. Observado: un mensaje en portugues recibio respuesta en espanol; con `--lang-thresholds` apuntando a `scripts/e2e/lang-thresholds.json` la respuesta salio en portugues. Pedimos: incluir `lang-thresholds.json` en `serve_state.py` y en el compose de referencia, y un aviso al arrancar cuando una release de `AGENTCORE_SERVE_AGENTS` declara `language_detection` y no hay umbrales.

## A4 (P1). El perfil de modelo de los fixtures no es el de nuestra politica

`tests/fixtures/registry-e2e/model_profiles/perfil-generacion@1.0.0.yaml` usa `google/gemini-3.1-flash-lite`; nuestra politica para agentes es `xiaomi/mimo-v2.6-flash` (juez/verificador `xiaomi/mimo-v2.6-pro`). Lo cambiamos en una copia al importar (`prodlike.py seed --model`). Pedimos que los fixtures usen mimo flash o que exista un override documentado por entorno que no cambie el hash de la entidad.

## A5 (P1). Salida invalida del modelo con mimo flash en el copiloto (6 de 20 conversaciones concurrentes)

Con 20 asesores distintos preguntando el saldo de la tarjeta a la vez, 14 respondieron la cifra y 6 no terminaron el turno: el llm-gateway devolvio 502 `invalid_output` («el contenido no es JSON», «/tool: tipo distinto de string») y el run quedo `open`. No hubo 5xx ni errores en `serve`. Pedimos: un reintento con reparacion del paso `agent` ante `invalid_output` (una vez, con el error del validador en el prompt), o `structured` por esquema en el perfil si el gateway lo soporta; y un contador de `invalid_output` por agente en las metricas.

## A6 (P1). Limites por principal en modo produccion

20 inicios de run seguidos desde el mismo principal recibieron `429 rate_limited` (los valores por defecto de `AGENTCORE_RATE_MAX_HITS` / `_RATE_WINDOW_SECONDS` figuran como «demo»). Pedimos: documentar los valores reales por defecto, y que `serve mode=production` avise (o rechace) si siguen los de demo. Para la prueba de carga usamos 20 principales distintos.

## A7 (P2). Orden de validacion en `/v1/registry/*`

El cuerpo se valida antes de autenticar: una credencial falsificada con cuerpo invalido recibe 422 en vez de 401 (`POST /proposals/{id}/approve` con `{}` y `POST /proposals`). No es una fuga de datos, pero cambia el contrato de errores y confunde a los clientes que reintentan. Pedimos autenticar primero (dependencia de FastAPI antes del modelo del cuerpo).

## A8 (P2). Reinicio abrupto a mitad de turno

SIGTERM: el turno en vuelo termina y el mismo run acepta el siguiente turno en 4 s (bien). SIGKILL durante un turno: el run queda `open` y el siguiente turno recibe `409 turn_in_progress` durante unos 57 s (10 intentos cada 5 s) hasta que vence la reserva; el reintento funciona. Pedimos documentar la duracion de la reserva y su variable (si existe), y confirmar que `agentcore sweep --once` cierra como `abandoned` los runs huérfanos (infra aun no lo programa; lo anotamos de nuestro lado).

## A9 (P2). `/readyz` tarda unos 30 s en volver a 200 tras volver Postgres o el gateway

Recuperacion sin pasos manuales, pero 30 s despues (medido tres veces). Si es una cache, pedimos documentar su TTL (y una variable); si es el pool, que reintente antes.

## A10 (P3). Detalles de imagen y compose de referencia

- El `HEALTHCHECK` de la imagen y el `CMD` fijan el puerto 8000; cualquier despliegue con otro puerto (infra usa 8001) debe sobreescribir la sonda. Podria leer `AGENTCORE_PORT` o un `--port` por variable.
- `docker-compose.yml` de referencia: `serve` sin `restart`, y `llm-gateway`/`tool-service` con `condition: service_started` (infra usa `service_healthy`; con `started` el primer `/readyz` puede dar 503).
- `agentcore registry ... import` imprime en una sola linea el JSON de todas las releases (decenas de KB): un resumen por release bastaria.

## No probado (para que no se de por cubierto)

- Imagen `linux/arm64` (solo se construyo `amd64`).
- `AGENTCORE_ALLOW_DOUBLES=1` (solo se verifico que sin ella el arranque dice `mode=production` y que el contenedor no la trae).
- Aprobacion y publicacion a traves de `serve`: por regla nadie las automatiza para el motor y la plataforma no esta en el stack; solo se probo que el principal del motor recibe 403 (`forbidden_role`).
- Rotacion de claves en caliente (la cubre su test `test_identity_keys_reload`).
