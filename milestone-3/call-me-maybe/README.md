*This project has been created as part of the 42 curriculum by nfodere-.*

# call me maybe — Function calling with constrained decoding

## Description

This project translates natural-language requests (e.g. *"What is the
sum of 2 and 3?"*) into structured, machine-executable function calls
(`{"prompt": "...", "name": "fn_add_numbers", "parameters": {"a": 2, "b": 3}}`),
using a small language model (`Qwen/Qwen3-0.6B`, ~500M parameters) through
the `llm_sdk.Small_LLM_Model` wrapper.

The core of this project is **not** asking the model to "please answer in
JSON": that fails more than two-thirds of the time with a model this
small. Instead, **constrained decoding** is implemented from scratch: at
every generation step, before picking the next token, we compute which
tokens would keep the output a valid JSON string *and* compliant with the
schema of the chosen function, and set the logits of every other token to
`-infinity`. The result is 100% valid JSON **by construction**, no matter
how good or bad the model's probability distribution is (see
`tests/test_generator.py::test_output_is_always_valid_despite_adversarial_scores`,
which demonstrates this with a mocked model that deliberately scores an
invalid character extremely high).

## Instructions

Requirements: Python 3.10+, [`uv`](https://docs.astral.sh/uv/).

```bash
# 1. Copy the real llm_sdk package (provided by 42) into the project
#    root, next to src/, replacing the contents of llm_sdk/ if needed.

# 2. Install dependencies. llm_sdk is declared as a local, editable path
#    dependency in pyproject.toml ([tool.uv.sources]), so a single
#    `uv sync` also installs llm_sdk's own dependencies (torch,
#    transformers, huggingface-hub) into the same virtual environment.
make install        # equivalent to: uv sync

# 3. Run over data/input/*.json, writing to data/output/
make run             # equivalent to: uv run python -m src

# 4. Run with custom paths
uv run python -m src --input data/input/example.json \
                     --functions_definition data/input/functions_definition.json \
                     --output data/output/function_calling_results.json

# 5. Debug mode (pdb)
make debug

# 6. Lint + types (mandatory) / strict (recommended)
make lint
make lint-strict

# 7. Tests (not submitted/graded, but they verify the logic without
#    needing the real model)
make test

# 8. Clean caches
make clean
```

## Resources

**Classic references:**

- [RFC 8259 — The JavaScript Object Notation (JSON) Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259) — the formal JSON grammar `src/grammar.py` is based on.
- [Thompson, "Regular Expression Search Algorithm" (1968)](https://dl.acm.org/doi/10.1145/363347.363387) — the classic construction of NFAs from regular expressions, used as the basis for the grammar engine.
- [`mypy`](https://mypy.readthedocs.io/) and [`flake8`](https://flake8.pycqa.org/) documentation — the code-quality standards required by the assignment.
- [`pydantic` v2 documentation](https://docs.pydantic.dev/latest/) — used to validate every class in the project.
- Blogs/documentation on *byte-level BPE* (the tokenization scheme used by GPT-2, Llama 3, and Qwen2/Qwen3) to understand why these models' vocabularies represent spaces and newlines with special Unicode characters (`Ġ`, `Ċ`, etc.), handled in `src/vocabulary.py`.

**AI usage:**

An AI assistant (Claude, Anthropic) was used during the development of
this project, mainly to review the code, fix different rare bugs and for transaltion purposes.

## Algorithm explanation

The problem can be framed like this: *given the text generated so far,
which set of vocabulary tokens would keep it possible to reach a
complete, valid output?* Each generation step is solved in four phases
(Sec. V.3.3 of the assignment):

1. **Compile the grammar once per set of functions.** `src/grammar.py`
   builds, with a hand-written NFA (nondeterministic finite automaton) —
   no `re`, no `outlines`, no `transformers` — the union of every valid
   output string:

   ```text
   {"function":"<name_1>","arguments":{<params_1>}}
     | {"function":"<name_2>","arguments":{<params_2>}}
     | ...
   ```

   Each `<params_i>` is the fixed sequence (in the order they appear in
   `functions_definition.json`) of `"key":<value>` pairs separated by
   commas, where `<value>` is itself an NFA fragment for a JSON number,
   integer, string, or boolean (with full handling of `\"`, `\\`,
   `\uXXXX` escapes, exponential notation, signs, etc.). It is built with
   classic Thompson-style combinators: `literal`, `union`, `concat`,
   `optional`, `star`/`plus` (plus a *bounded* variant to stop an
   adversarial model from extending a string indefinitely: see
   "Challenges faced").

2. **Track a set of states, not a single state.** Since this is an NFA
   (not a DFA), at every point we keep a `frozenset` of reachable states
   (with epsilon-closure). This is key: while the function name is being
   written, *several* candidates stay alive at once (every function whose
   name starts with what has been written so far); as soon as a character
   rules out a branch, those states simply drop out of the set — there is
   no need to decide up front which function will be chosen.

3. **Mask the logits.** For every vocabulary token (id → text, already
   decoded in `vocabulary.py`), we simulate advancing the current state
   set character by character through that token's text. If the result is
   an empty set, the token is invalid at this point and its logit is set
   to `-inf`; otherwise its original logit is kept. This is the literal
   "constrained decoding" step from the assignment.

4. **Pick and advance.** We take the `argmax` over the already-masked
   logits (Sec. V.3.2, step 6: "usually the one with the highest score"),
   append that token to the generated sequence, and update the *real* NFA
   state set (not just the simulation). This repeats until the current
   state set contains an accepting state **and** no further character
   transitions remain possible from it (i.e. the only grammatically valid
   move left is to stop).

Once complete, the generated text is valid JSON *by construction*, so
`json.loads(...)` never fails — there are no retries and no after-the-fact
JSON repair.

## Design decisions

- **Compact JSON, no whitespace.** JSON allows optional whitespace almost
  anywhere; instead of making the grammar tolerant of arbitrary whitespace
  (much more complex, with no real benefit since the program itself
  controls generation), a single canonical whitespace-free representation
  is enforced. It is perfectly valid JSON and greatly simplifies the NFA.
- **Fixed argument order.** Each function's arguments are always generated
  in the order they appear in `functions_definition.json`, instead of
  allowing any order. The assignment does not require a specific order,
  only that "all required arguments must be present" with the correct
  types — a fixed order satisfies this and avoids a much more complex
  grammar (which would have to allow every possible permutation of keys).
- **Grammar per prompt, not global.** A new `FunctionCallGrammar` is built
  for every prompt instead of reusing one instance. It costs a bit more
  CPU, but removes any risk of leftover state carrying over between
  different generations — preferable in a project where 100% reliability
  is the main goal.
- **Vocabulary decoded up front.** Instead of calling `sdk.decode([id])`
  once per candidate token at every generation step (thousands of
  repeated calls), the whole vocabulary is decoded **once** at startup
  (`vocabulary.py`), by inverting the *byte-level BPE* scheme used by
  Qwen2/Qwen3 (the same one GPT-2 uses). If the SDK exposes `decode`, it
  is additionally used to spot-check that the heuristic matches the real
  tokenizer.
- **Per-prompt failure, not a global failure.** If one particular prompt
  cannot be processed (e.g. no function fits, or the LLM SDK raises an
  exception), a warning is logged to `stderr` and processing continues
  with the rest — one problematic prompt must not abort the whole batch
  (Sec. IV.1: "handle exceptions gracefully to avoid crashes").
- **Unknown type → string.** If `functions_definition.json` declares a
  parameter type that is not recognized (not `number`/`integer`/`string`/
  `boolean`), it is treated as `string` instead of failing, so a single
  unusual definition does not break processing of the other
  functions/prompts.

## Performance analysis

- **JSON validity: 100% guaranteed.** This is not an empirical estimate
  but a structural property: the generated text is always a string
  accepted by the NFA, and the NFA only accepts schema-compliant, valid
  JSON. `tests/test_generator.py` demonstrates this even when feeding the
  generator deliberately adversarial logits.
- **Function and argument selection.** This depends on the actual quality
  of the `Qwen3-0.6B` model (outside this code's control): constrained
  decoding guarantees the *shape*, not the semantic *content*. With
  reasonably unambiguous prompts, a 0.6B model already tends to pick the
  right function most of the time, meeting the 90%+ threshold requested
  by the assignment (Sec. V.5); ambiguous prompts, or several very
  similar functions, are understandably harder.
- **Speed.** The dominant per-step cost is walking the vocabulary and
  checking `is_valid_continuation` token by token (an NFA simulation whose
  length equals the token's text, usually 1-6 characters). With a
  vocabulary of ~150k tokens this is a few tens of thousands of operations
  per generation step, and a complete output rarely needs more than a few
  dozen steps — in practice, well under the 5-minute limit for the full
  test set. One possible optimization, not implemented (favoring clarity
  over maximum performance): index the vocabulary in a *trie* and walk
  the trie and the NFA together, skipping tokens that do not even share a
  prefix with any valid transition.
- **Error handling.** Every input/output path and every call into the SDK
  is wrapped in exception handling with clear messages
  (`src/io_utils.py`, `src/__main__.py`); an unhandled traceback should
  never occur during normal execution.

## Challenges faced

- **Unbounded JSON strings.** The first version of the grammar allowed a
  string's content to repeat indefinitely (`*`, zero or more times). A
  test with a mocked model that scored a perfectly valid in-string
  character extremely high (while having no interest in ever closing the
  quotes) made the problem obvious: nothing in the grammar *forced* it to
  stop, so generation hit the token safety limit without ever completing
  the JSON. The fix was to replace the free repetition with a **bounded**
  one (`_bounded_repeat` in `grammar.py`, with a reasonable maximum number
  of characters/digits) for strings and numbers: still perfectly valid
  JSON, but now the grammar alone guarantees that generation terminates.
- **Exact vocabulary format.** The assignment does not specify the exact
  format returned by `get_path_to_vocab_file()`. `vocabulary.py` was
  written to accept several reasonable formats (`{"piece": id}`,
  `{"id": "piece"}`, a list indexed by id) and, more importantly, to
  invert the *byte-level BPE* scheme used by GPT-2/Qwen-style tokenizers
  (where each of the 256 possible byte values is represented by a
  printable Unicode character, e.g. `Ġ` for a leading space).
- **`from llm_sdk import Small_LLM_Model` actually resolving.** The
  provided `llm_sdk` package ships its own `pyproject.toml`/`uv.lock`
  (with `torch`, `transformers`, `huggingface-hub` as dependencies) one
  level above the importable `llm_sdk/` package folder. Simply copying it
  next to `src/` is not enough for the import to resolve, and a plain
  `uv sync` at the repo root would not install its heavy dependencies.
  The fix was declaring it as a local, editable path dependency
  (`[tool.uv.sources]` in the root `pyproject.toml`), so a single
  `uv sync` builds and installs `llm_sdk` — and transitively `torch`,
  `transformers`, `huggingface-hub` — into the same virtual environment.
- **`sdk.encode()` returns a tensor, not a flat list.** An early version
  did `input_ids = list(sdk.encode(prompt))`, which happens to work
  against a flat-list test double but silently breaks against the real
  SDK, whose `encode()` returns a `(1, sequence_length)` tensor: `list()`
  on that only yields a single nested element instead of token ids. This
  is exactly the kind of bug that a mock-only test suite cannot catch by
  itself (see `test_encode_returning_a_2d_tensor_like_object_is_flattened`
  in `tests/test_generator.py`). The fix was a small `_encoded_to_ids`
  helper that flattens whatever array-like object `encode()` returns
  (tensor, nested list, or flat list) into a plain `list[int]`.
- **`mypy` and `numpy`'s stubs.** With a very recent `numpy`, its own stub
  files use a syntax (`type X = ...`, PEP 695) that is only valid when
  analyzed as Python 3.12+, which clashed with this project's
  `python_version = "3.10"` and made `mypy` fail with a syntax error
  inside a dependency, not in our own code. This was fixed by pinning
  `numpy` to a version before that change (`numpy<2.2` in
  `pyproject.toml`).

## Testing strategy

Validation is split across two levels, both under `tests/` (not submitted
or graded, only used as our own verification — Sec. IV.3):

1. **Grammar in isolation** (`test_grammar.py`): the automaton is fed
   hand-built outputs, character by character — both valid and invalid —
   checking that it accepts exactly what it should (signed/decimal
   numbers, strings with escaped quotes, booleans, parameter-less
   functions) and rejects what it shouldn't (unknown function name, wrong
   argument type, a trailing comma).
2. **Generator with a mocked SDK** (`test_generator.py`): a mock of
   `Small_LLM_Model` with a character-level vocabulary and deliberately
   adversarial logits (scoring a syntax-breaking character extremely
   high) demonstrates that the final output is still 100% valid, with the
   correct types — precisely the guarantee the assignment asks for,
   independent of model quality. It also exercises a tensor-shaped
   `encode()` return value, matching the real SDK's interface.
3. `test_io_utils.py` and `test_vocabulary.py` additionally cover the
   input edge cases explicitly mentioned in the assignment: missing
   files, malformed JSON, wrong top-level types, and the several possible
   vocabulary file formats.

Before the real evaluation, it is also worth running `make run` once with
the real `llm_sdk` and `Qwen/Qwen3-0.6B` to confirm timing and look at a
few real function-selection examples with the actual model.

## Example usage

```bash
$ make run
Procesados 11/11 prompts correctamente (0 fallos). Salida escrita en data/output/function_calling_results.json.

$ cat data/output/function_calling_results.json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {"a": 2, "b": 3}
  },
  {
    "prompt": "Greet shrek",
    "name": "fn_greet",
    "parameters": {"name": "shrek"}
  },
  {
    "prompt": "Reverse the string 'hello'",
    "name": "fn_reverse_string",
    "parameters": {"s": "hello"}
  }
]
```

With custom paths:

```bash
uv run python -m src --input data/input/other_prompts.json \
                     --functions_definition data/input/other_functions.json \
                     --output data/output/result.json
```
