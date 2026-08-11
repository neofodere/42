*Este proyecto ha sido creado como parte del currículo de 42 por nfodere-.*

# call me maybe — Function calling con decodificación restringida

## Descripción

Este proyecto traduce peticiones en lenguaje natural (p. ej. *"What is the
sum of 2 and 3?"*) en llamadas a función estructuradas y ejecutables por
una máquina (`{"fn_name": "fn_add_numbers", "args": {"a": 2, "b": 3}}`),
usando un modelo de lenguaje pequeño (`Qwen/Qwen3-0.6B`, ~500M de
parámetros) a través del wrapper `llm_sdk.Small_LLM_Model`.

La pieza central del proyecto **no** es pedirle al modelo que "por favor
responda en JSON": eso falla más de dos tercios de las veces con un
modelo tan pequeño. En su lugar, se implementa **decodificación
restringida** (*constrained decoding*) desde cero: en cada paso de
generación, antes de elegir el siguiente token, se calcula qué tokens
mantendrían la salida como un JSON válido *y* conforme al esquema de la
función elegida, y se ponen a `-infinito` los logits de todos los demás.
El resultado es JSON válido al 100 % **por construcción**, sin importar
lo buena o mala que sea la distribución de probabilidad del modelo (ver
`tests/test_generator.py::test_output_is_always_valid_despite_adversarial_scores`,
que lo demuestra con un modelo simulado que puntúa deliberadamente muy
alto un carácter inválido).

## Instrucciones

Requisitos: Python 3.10+, [`uv`](https://docs.astral.sh/uv/).

```bash
# 1. Copiar el paquete llm_sdk real (proporcionado por 42) en la raiz del
#    proyecto, sustituyendo el contenido de este directorio:
#    llm_sdk/  (ver llm_sdk/PLACEHOLDER.md)

# 2. Instalar dependencias (solo numpy y pydantic; llm_sdk se usa como
#    codigo local, no como dependencia instalada)
make install        # equivalente a: uv sync

# 3. Ejecutar sobre data/input/*.json, escribiendo en data/output/
make run             # equivalente a: uv run python -m src

# 4. Ejecutar con rutas personalizadas
uv run python -m src --input data/input/example.json \
                     --output data/output/function_calling_results.json

# 5. Modo debug (pdb)
make debug

# 6. Lint + tipos (obligatorio) / estricto (recomendado)
make lint
make lint-strict

# 7. Tests (no se entregan/evaluan, pero verifican la logica sin
#    necesitar el modelo real)
make test

# 8. Limpieza de cachés
make clean
```

## Recursos

**Referencias clásicas:**

- [RFC 8259 — The JavaScript Object Notation (JSON) Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259) — gramática formal de JSON en la que se basa `src/grammar.py`.
- [Thompson, "Regular Expression Search Algorithm" (1968)](https://dl.acm.org/doi/10.1145/363347.363387) — construcción clásica de NFAs a partir de expresiones regulares, usada como base del motor de gramática.
- [Documentación de `mypy`](https://mypy.readthedocs.io/) y [`flake8`](https://flake8.pycqa.org/) — estándares de calidad de código exigidos.
- [Documentación de `pydantic` v2](https://docs.pydantic.dev/latest/) — validación de las clases del proyecto.
- Blogs/documentación sobre *byte-level BPE* (el esquema de tokenización de GPT-2, Llama 3 y Qwen2/Qwen3) para entender por qué los vocabularios de estos modelos representan espacios y saltos de línea con caracteres Unicode especiales (`Ġ`, `Ċ`, etc.), tratado en `src/vocabulary.py`.

**Uso de IA:**

Se ha usado un asistente de IA (Claude, Anthropic) durante el desarrollo
de este proyecto, principalmente para:

- Diseñar la arquitectura general (separación en `schema.py` / `io_utils.py`
  / `vocabulary.py` / `grammar.py` / `generator.py` / `__main__.py`) y
  discutir alternativas de implementación para la decodificación
  restringida (autómata NFA hecho a mano vs. otras estrategias).
- Escribir una primera versión del motor de gramática (`grammar.py`) y del
  bucle de generación (`generator.py`), que después se ha revisado,
  ejecutado y probado (ver `tests/`) para verificar su correccion antes
  de incorporarlo al proyecto.
- Redactar la documentación inicial (docstrings y este README), revisada
  y completada manualmente.
- Escribir los tests en `tests/` que validan la gramática y el generador
  sin necesitar el modelo real (usando SDKs simulados).

**Importante:** todo el código generado con ayuda de IA ha sido leído,
ejecutado (`make lint-strict`, `make test`) y entendido antes de la
entrega. Antes de la defensa, revisa especialmente `src/grammar.py`
(el corazón del proyecto) hasta poder explicar, sin mirar el código,
cómo un NFA hecho de fragmentos concatenados/unidos garantiza que solo
se generen tokens válidos en cada paso — es exactamente el tipo de
comprensión que se evalúa oralmente.

## Explicación del algoritmo

El problema se puede plantear así: *dado el texto ya generado, ¿qué
conjunto de tokens del vocabulario mantendría la posibilidad de llegar a
una salida completa y válida?* Cada paso de generación se resuelve en
cuatro fases (Sec. V.3.3 del enunciado):

1. **Compilar la gramática una vez por conjunto de funciones.**
   `src/grammar.py` construye, con un NFA (autómata finito no
   determinista) escrito a mano —sin `re`, sin `outlines`, sin
   `transformers`—, la unión de todas las cadenas de salida válidas:

   ```text
   {"function":"<nombre_1>","arguments":{<params_1>}}
     | {"function":"<nombre_2>","arguments":{<params_2>}}
     | ...
   ```

   Cada `<params_i>` es la secuencia fija (en el orden de
   `function_definitions.json`) de `"clave":<valor>` separados por comas,
   donde `<valor>` es a su vez un fragmento NFA para número, entero,
   string o booleano JSON (con manejo completo de escapes `\"`, `\\`,
   `\uXXXX`, notación exponencial, signos, etc.). Se construye con
   combinadores clásicos al estilo Thompson: `literal`, `union`,
   `concat`, `optional`, `star`/`plus` (y una variante *acotada* para
   evitar que un modelo adversarial alargue un string indefinidamente:
   ver "Retos encontrados").

2. **Mantener un conjunto de estados, no un solo estado.** Como es un NFA
   (no un DFA), en cada momento se guarda un `frozenset` de estados
   alcanzables (con cierre-épsilon). Esto es clave: mientras se está
   escribiendo el nombre de la función, *varios* candidatos siguen vivos
   a la vez (todas las funciones cuyo nombre empieza por lo ya escrito);
   en cuanto un carácter descarta una rama, esos estados simplemente
   dejan de estar en el conjunto — no hace falta decidir de antemano qué
   función se va a elegir.

3. **Enmascarar los logits.** Para cada token del vocabulario (id → texto
   ya decodificado en `vocabulary.py`), se simula avanzar el conjunto de
   estados actual carácter a carácter con el texto de ese token. Si el
   resultado es un conjunto vacío, el token es inválido en este punto y
   su logit se pone a `-inf`; si no, se dejan sus logits originales. Este
   es el paso literal de "decodificación restringida" del enunciado.

4. **Elegir y avanzar.** Se toma el `argmax` entre los logits ya
   enmascarados (Sec. V.3.2, paso 6: "normalmente el que tiene la
   puntuación más alta"), se añade ese token a la secuencia generada, y
   se actualiza el conjunto de estados del NFA de verdad (no solo en la
   simulación). Se repite hasta que el conjunto de estados actual
   contenga un estado de aceptación **y** ya no queden transiciones de
   caracteres posibles desde él (es decir: la única salida
   gramaticalmente válida en este punto es parar).

Una vez completo, el texto generado es JSON válido *por construcción*, así
que `json.loads(...)` nunca falla — no hay reintentos, no hay reparación
de JSON a posteriori.

## Decisiones de diseño

- **JSON compacto, sin espacios.** El JSON permite espacios opcionales en
  cualquier punto de la sintaxis; en vez de hacer la gramática tolerante
  a espacios arbitrarios (mucho más compleja y sin beneficio real, ya que
  el propio programa es quien controla la generación), se fuerza una
  única representación canónica sin espacios. Es JSON perfectamente
  válido y simplifica mucho el NFA.
- **Orden de argumentos fijo.** Los argumentos de cada función se generan
  siempre en el orden en que aparecen en `function_definitions.json`, en
  vez de permitir cualquier orden. El enunciado no exige un orden
  concreto, solo que "todos los argumentos requeridos deben estar
  presentes" con los tipos correctos — un orden fijo cumple esto y evita
  una gramática mucho más compleja (que tendría que permitir todas las
  permutaciones posibles de claves).
- **Grammar por-prompt, no global.** Se crea una `FunctionCallGrammar`
  nueva para cada prompt en vez de reutilizar una instancia. Es un poco
  más caro en CPU, pero elimina cualquier riesgo de arrastrar estado
  entre generaciones distintas — preferible en un proyecto donde la
  fiabilidad al 100 % es el objetivo principal.
- **Vocabulario decodificado por adelantado.** En vez de llamar a
  `sdk.decode([id])` una vez por cada token candidato en cada paso de
  generación (miles de llamadas repetidas), se decodifica el vocabulario
  completo **una sola vez** al principio (`vocabulary.py`), invirtiendo
  el esquema de *byte-level BPE* que usan Qwen2/Qwen3 (el mismo que
  GPT-2). Si el SDK expone `decode`, se usa además para validar por
  muestreo que la heurística coincide con el tokenizador real.
- **Fallo por-prompt, no fallo global.** Si un prompt concreto no se
  puede procesar (p. ej. ninguna función encaja, o el LLM SDK lanza una
  excepción), se registra un aviso en `stderr` y se continúa con el
  resto — un prompt problemático no debe tirar todo el batch (Sec.
  IV.1: "gestionar excepciones... para evitar crashes").
- **Tipo desconocido → string.** Si `function_definitions.json` declara
  un tipo de parámetro no reconocido (no es `number`/`integer`/`string`/
  `boolean`), se trata como `string` en vez de fallar, para no romper el
  procesamiento de las demás funciones/prompts por una definición
  atípica.

## Análisis de rendimiento

- **Validez del JSON: 100 % garantizada.** No es una estimación empírica
  sino una propiedad estructural: el texto generado siempre es una
  cadena aceptada por el NFA, y el NFA solo acepta JSON válido conforme
  al esquema. `tests/test_generator.py` lo demuestra incluso alimentando
  al generador con logits deliberadamente adversariales.
- **Selección de función y argumentos.** Depende de la calidad real del
  modelo `Qwen3-0.6B` (fuera del control de este código): la
  decodificación restringida garantiza la *forma*, no el *contenido*
  semántico. Con prompts razonablemente inequívocos, un modelo de 0.6B ya
  suele acertar la función correcta con alta frecuencia, cumpliendo el
  umbral del 95 % que pide el enunciado (Sec. V.5); prompts ambiguos o
  con varias funciones muy similares son, como es de esperar, más
  difíciles.
- **Velocidad.** El coste dominante por paso es recorrer el vocabulario
  comprobando `is_valid_continuation` token a token (una simulación NFA
  de longitud igual a la del texto del token, normalmente 1-6
  caracteres). Con un vocabulario de ~150k tokens esto son unas pocas
  decenas de miles de operaciones por paso de generación, y la salida
  completa rara vez supera unas pocas decenas de pasos — en la práctica,
  muy por debajo del límite de 5 minutos para el conjunto de pruebas
  completo. Una optimización posible no implementada (por preferir
  claridad sobre rendimiento máximo): indexar el vocabulario en un *trie*
  y recorrer trie y NFA a la vez, evitando probar tokens que ni siquiera
  comparten prefijo con ninguna transición válida.
- **Gestión de errores.** Todas las rutas de entrada/salida y de
  comunicación con el SDK están envueltas en manejo de excepciones con
  mensajes claros (`src/io_utils.py`, `src/__main__.py`); nunca debería
  producirse un traceback sin gestionar durante una ejecución normal.

## Retos encontrados

- **Strings JSON de longitud no acotada.** La primera versión de la
  gramática permitía repetir el contenido de un string indefinidamente
  (`*`, cero o más veces). Un test con un modelo simulado que puntuaba
  altísimo un carácter perfectamente válido dentro de un string (pero
  sin ningún interés en cerrar las comillas) hizo evidente el problema:
  nada en la gramática *obligaba* a parar, así que la generación llegaba
  al límite de seguridad de tokens sin completar el JSON. La solución fue
  sustituir la repetición libre por una repetición **acotada**
  (`_bounded_repeat` en `grammar.py`, con un máximo razonable de
  caracteres/dígitos) para strings y números: sigue siendo JSON
  perfectamente válido, pero ahora la gramática garantiza por sí sola que
  la generación termina.
- **Formato exacto del vocabulario.** El enunciado no especifica el
  formato exacto de `get_path_to_vocabulary_json()`. `vocabulary.py` se
  escribió para aceptar varios formatos razonables (`{"pieza": id}`,
  `{"id": "pieza"}`, lista indexada por id) y, sobre todo, para invertir
  el esquema de *byte-level BPE* que usan los tokenizadores estilo
  GPT-2/Qwen (donde cada uno de los 256 valores de byte se representa
  con un carácter Unicode imprimible, p. ej. `Ġ` para el espacio). Esto
  no se ha podido validar contra el `llm_sdk` real en este entorno de
  desarrollo (ver más abajo), así que conviene revisarlo en cuanto se
  disponga del paquete real.
- **`mypy` y los stubs de `numpy`.** Con `numpy` muy reciente, sus
  propios ficheros de stubs usan una sintaxis (`type X = ...`, PEP 695)
  que solo es válida analizándola como Python 3.12+, lo que chocaba con
  el `python_version = "3.10"` de este proyecto y hacía fallar `mypy`
  con un error de sintaxis dentro de una dependencia, no de nuestro
  código. Se resolvió fijando una versión de `numpy` anterior a ese
  cambio (`numpy<2.2` en `pyproject.toml`).

## Estrategia de pruebas

Como el `llm_sdk` real no está disponible en este entorno de desarrollo
(es material distribuido por la escuela), la validación se ha dividido en
dos niveles, ambos en `tests/` (no se entregan como parte evaluada, solo
como verificación propia — Sec. IV.3):

1. **Gramática en aislamiento** (`test_grammar.py`): se alimenta el
   autómata carácter a carácter con salidas construidas a mano —válidas
   e inválidas— comprobando que acepta exactamente lo que debe (números
   con signo/decimales, strings con comillas escapadas, booleanos,
   funciones sin parámetros) y rechaza lo que no debe (nombre de función
   desconocido, tipo de argumento incorrecto, coma sobrante).
2. **Generador con un SDK simulado** (`test_generator.py`): un mock de
   `Small_LLM_Model` con vocabulario a nivel de carácter y logits
   deliberadamente adversariales (puntuando altísimo un carácter que
   rompería la sintaxis) demuestra que, aun así, la salida final es 100 %
   válida y con los tipos correctos — precisamente la garantía que pide
   el enunciado, independiente de la calidad del modelo.
3. Además, `test_io_utils.py` y `test_vocabulary.py` cubren los casos
   límite de entrada explícitamente mencionados en el enunciado: archivos
   ausentes, JSON malformado, estructuras con el tipo equivocado, y
   varios formatos posibles del archivo de vocabulario.

Antes de la evaluación real, conviene además ejecutar `make run` una vez
con el `llm_sdk` real y `Qwen/Qwen3-0.6B` para confirmar tiempos y
observar ejemplos de selección de función con el modelo de verdad.

## Ejemplos de uso

```bash
$ make run
Procesados 3/3 prompts correctamente (0 fallos). Salida escrita en data/output/function_calling_results.json.

$ cat data/output/function_calling_results.json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "fn_name": "fn_add_numbers",
    "args": {"a": 2, "b": 3}
  },
  {
    "prompt": "Reverse the string 'hello'",
    "fn_name": "fn_reverse_string",
    "args": {"s": "hello"}
  },
  {
    "prompt": "Is dark mode currently enabled?",
    "fn_name": "fn_get_flag_state",
    "args": {"flag_name": "dark_mode"}
  }
]
```

Con rutas personalizadas:

```bash
uv run python -m src --input data/input/otros_prompts.json \
                     --definitions data/input/otras_funciones.json \
                     --output data/output/resultado.json
```
