# Detección y evolución: propuesta técnica inicial

Fecha: 2026-09-29. Estado: enfoque general aprobado por el usuario; no implementación. Premisa actual: histórico recopilado del banco y operación real, no dataset de hackathon. El detalle de contratos, componentes y responsabilidades se propone en ARQUITECTURA_PULSO.md y DETALLE_MOTOR_Y_DATOS.md. Alcance confirmado: CONTEXTO_PULSO.md.

## Tres unidades de análisis

Evento: mensaje, decisión, llamada de herramienta, transición de capa, respuesta o resultado. Interacción: una sesión de atención. Episodio: contactos y hechos relacionados con un mismo problema de un cliente a lo largo del tiempo. Un mismo cliente puede tener episodios distintos. No convertir coincidencia temporal en relación causal ni compartir expediente automáticamente entre temas.

Cada evento conserva identificadores disponibles de cliente pseudonimizado, interacción/episodio, fecha de ocurrencia y de ingesta, tema y versión de taxonomía, capa, versión de capacidad, acción, resultado, evidencia, procedencia y elegibilidad de evaluación. Vínculos por llave son exactos; vínculos por cliente/tiempo/tema son candidatos etiquetados. Faltantes permanecen desconocidos.

Resultado separado en: herramienta ejecutada, objetivo del caso verificado, valoración del cliente y recontacto observado. Ausencia de recontacto requiere ventana completa y cobertura; sin ello es censurado/no evaluable. Resuelto en una tabla no demuestra todo lo anterior.

## Descubrimiento

Detectores numéricos generan candidatos por concentración de dolor, crecimiento ajustado por demanda, recontactos, fallos de tools, escalamiento repetido y cobertura inexistente. Evaluaciones generan candidatos por regresión. Analizar también casos exitosos en capas superiores que podrían bajar a capas más baratas.

La taxonomía comienza con campos existentes; puede extenderse con familias semánticas provisionales cuando haya texto. No asumir que existen transcripciones. Una clasificación cerrada necesita alternativa desconocida. Descubrimientos semánticos abiertos pueden producir etiquetas nuevas que luego se revisan y versionan.

Cada candidato tiene numerador, denominador, periodo, comparadores, incertidumbre, casos y contraejemplos, consulta reproducible, cobertura de datos y dependencias. Deduplicar oportunidades superpuestas; evitar alertas repetidas por el mismo problema. Supuestos y umbrales son versionados y visibles, no constantes ocultas.

## Investigación y patrones de resolución

Para cohortes comparables, reconstruir secuencias de herramientas, precondiciones y respuestas. Separar acciones verificables de lenguaje. Agrupar variaciones semánticas de un mismo procedimiento. Encontrar también fracaso, excepción, restricciones y necesidad legítima de humano. Comparar patrones por motivo, producto y complejidad; no ordenar asesores por tasa bruta de cierre.

Una secuencia repetida que termina bien es una candidata, no prueba causal. Traducirla a condiciones de elegibilidad, pasos autorizados, evidencia de salida y escalamiento. Un patrón inseguro no se vuelve válido por frecuencia. Beneficio potencial de migración entre capas se calcula solo sobre casos elegibles y diferencia de costo; no sobre todo el tema.

## Propuesta para el framework

Salida independiente del runtime: problema, población, evidencia/contraevidencia, estrategia mínima, capa destino, dependencias, fuentes, contratos de tools/skills, escenarios de elegibilidad y excepción, evaluaciones, beneficio por escenarios y riesgos. Declara qué es real y qué mock. Falta de tool o datos puede impedir ejecutar una propuesta; no inventar disponibilidad.

El catálogo de capacidades actuales es una entrada necesaria: árboles, preguntas de clasificación, skills, tools, permisos y versiones. Sin ese catálogo no se puede afirmar novedad ni una brecha de automatización. Mockearlo explícitamente para el MVP.

## Evaluación de dos productos

Evaluar el detector: encuentra oportunidades demostrables, no afirma causas sin evidencia, no duplica propuestas y distingue no automatizable. Un banco de referencia con oportunidades conocidas y casos negativos permite medir recuperación y precisión de detección. Si se insertan patrones, etiquetarlos como benchmark controlado; esto no prueba detectar patrones naturales del dataset.

Evaluar el candidato: objetivo verificado, seguridad, escalamiento correcto, cobertura elegible, costo, latencia y calidad. Usar oráculos deterministas independientes del texto del cliente simulado. Mocks con contratos y fallos coherentes; no cambiar respuestas del mock para beneficiar al candidato.

Separar desarrollo, validación iterativa y prueba final reservada por episodio/cliente/tiempo según el caso. Generadores reciben solo datos de desarrollo. Familias derivadas del mismo caso permanecen en un conjunto. El agente adversarial ve un perfil y objetivo; no los secretos de evaluación ni estado interno del soporte. Variar idioma, ambigüedad, datos incompletos, herramientas fallidas e inyección. Etiquetar prueba sintética y no estimar prevalencia desde su frecuencia.

## Promoción y feedback

El enum lineal anterior queda reemplazado por los estados separados de oportunidad, propuesta, job, evaluación y release definidos en SPEC_DETECCION_AUTOMEJORA.md. Aprobación es decisión sobre versiones/alcance, no progreso genérico de oportunidad. Shadow no ejecuta acciones externas. Canary asigna de manera estable y usa versiones fijadas y reglas de parada. Simulaciones se etiquetan sin limitar la arquitectura real. Recontactos requieren seguimiento diferido: no aprobar con resultado instantáneo como sustituto.

Guardar fallos, propuestas descartadas y razones para no repetir trabajo. Nuevas interacciones alimentan oportunidades y pruebas; cambios solo se promocionan al pasar controles. No hay garantía de mejora monotónica. Limitar rondas, costo y expansión sintética para evitar bucles sin valor.

## Recorridos iniciales recomendados, aún por acordar

Tres recorridos representativos: dolor operativo desde histórico, resolución exitosa en humano/IA2 transferible a árbol desde trazas y fallo descubierto por evaluación adversarial. Elegir los temas concretos tras consultar evidencia disponible. Implementar detector/investigador/propuestas/evaluación; usar adaptador del framework para probar un cambio. Si se simulan trazas, atención o promoción, declarar esa procedencia sin convertirla en límite arquitectónico.
