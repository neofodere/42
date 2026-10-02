"""Orchestrates one full constrained-decoding generation for one prompt.

This module is where "el proceso de generacion" described in Sec. V.3.2 of
the assignment actually happens: Prompt -> Tokenization -> Input IDs -> LLM
-> Logits -> Next Token Selection, with the grammar masking invalid tokens
at the "Next Token Selection" step (Sec. V.3.3).
"""

from __future__ import annotations

import json
from typing import Any, Protocol

import numpy as np

from src.grammar import FunctionCallGrammar
from src.schema import FunctionDefinition
from src.vocabulary import Vocabulary

MAX_NEW_TOKENS = 300


class LLMSDK(Protocol):
    """Structural type matching ``llm_sdk.Small_LLM_Model``.

    Only the public methods documented in the assignment are used; private
    attributes/methods of the real SDK are intentionally never touched, per
    the "Requisitos adicionales" ("Esta prohibido usar cualquier metodo o
    atributo privado del paquete llm_sdk.").
    """

    def get_logits_from_input_ids(self, input_ids: Any) -> Any:
        ...

    def get_path_to_vocab_file(self) -> str:
        ...

    def encode(self, text: str) -> Any:
        ...


class GenerationError(Exception):
    """Raised when a constrained generation cannot be completed safely."""


_FEW_SHOT = (
    "Example functions:\n"
    "- fn_multiply(a: number, b: number): Multiply two numbers.\n"
    "- fn_uppercase(text: string): Convert a text to uppercase.\n"
    "- fn_welcome(person: string): Write a welcome message for a person.\n"
    "- fn_remove_pattern(text: string, pattern: string): "
    "Remove everything matching a regex from a text.\n"
    "\n"
    "Request: Multiply 6 by 7\n"
    "JSON:\n"
    '{"function":"fn_multiply","arguments":{"a":6,"b":7}}\n'
    "\n"
    "Request: Say hello to Maria\n"
    "JSON:\n"
    '{"function":"fn_welcome","arguments":{"person":"Maria"}}\n'
    "\n"
    "Request: Make the text 'good morning' uppercase\n"
    "JSON:\n"
    '{"function":"fn_uppercase","arguments":{"text":"good morning"}}\n'
    "\n"
    'Request: Remove all digits from "abc123"\n'
    "JSON:\n"
    '{"function":"fn_remove_pattern","arguments":{"text":"abc123",'
    '"pattern":"\\\\d+"}}\n'
)


def build_prompt(user_request: str, functions: list[FunctionDefinition]) -> str:
    """Build the natural-language prompt shown to the LLM.

    The prompt gives instructions, a short few-shot example in the exact
    compact format the grammar enforces, the real function list, and the
    request. Correctness of the JSON *structure* never depends on the prompt
    (constrained decoding guarantees it); the prompt only steers which
    function and which argument values the model prefers.

    Args:
        user_request: The natural-language request to translate.
        functions: The available function definitions.

    Returns:
        The full prompt text to feed to the tokenizer.
    """
    lines = [
        "You translate a user request into exactly one function call, "
        "written as compact JSON:",
        '{"function":"<name>","arguments":{...}}',
        "",
        "Rules:",
        "- Choose the function whose description best matches the request.",
        "- Copy every argument value exactly from the request. Never leave "
        "a string argument empty.",
        "- Do not include the quotation marks that surround a value in the "
        "request.",
        "- Numbers are written without quotes.",
        "- Inside a JSON string a backslash must be written twice, e.g. "
        'the regex \\d+ is written "\\\\d+".',
        "",
        _FEW_SHOT,
        "Now the real task.",
        "Functions:",
    ]
    for fn in functions:
        params_desc = ", ".join(
            f"{name}: {spec.type}" for name, spec in fn.parameters.items()
        )
        lines.append(f"- {fn.name}({params_desc}): {fn.description}")
    lines.append("")
    lines.append(f"Request: {user_request}")
    lines.append("JSON:")
    lines.append("")
    return "\n".join(lines)


def _logits_to_array(logits: Any) -> np.ndarray[Any, Any]:
    """Coerce whatever tensor type the SDK returns into a flat numpy array.

    Handles the common case of a ``(sequence_length, vocab_size)`` shaped
    tensor (we only need the last position's distribution) as well as an
    SDK that already returns just the next-token logits.
    """
    array: np.ndarray[Any, Any] = np.asarray(logits)
    if array.ndim >= 2:
        array = array[-1]
    return np.asarray(array.reshape(-1))


def _encoded_to_ids(encoded: Any) -> list[int]:
    """Coerce whatever ``sdk.encode`` returns into a flat ``list[int]``.

    Per Sec. V.3.1 of the assignment, ``encode(text: str) -> Tensor``: the
    real SDK returns a 2-D tensor shaped ``(1, sequence_length)``. We also
    accept an already-flat ``list[int]`` (used by lightweight test
    doubles), or any other nested array-like structure, by round-tripping
    through numpy and flattening.
    """
    raw = encoded.tolist() if hasattr(encoded, "tolist") else encoded
    array = np.asarray(raw)
    return [int(x) for x in array.reshape(-1)]


CHUNK_SIZE = 4096

_FIRST_CODES_CACHE: dict[int, tuple[Vocabulary, np.ndarray[Any, Any]]] = {}


def _first_codes(vocabulary: Vocabulary, size: int) -> np.ndarray[Any, Any]:
    """Return, for each token id, the code point of its first character.

    Tokens with an empty text piece (special tokens, unknown ids) get -1.
    The table is built once per vocabulary and reused on every step.
    """
    cached = _FIRST_CODES_CACHE.get(id(vocabulary))
    if cached is not None and cached[0] is vocabulary and cached[1].shape[0] == size:
        return cached[1]
    codes = np.full(size, -1, dtype=np.int64)
    for token_id, text in vocabulary.id_to_text.items():
        if text and 0 <= token_id < size:
            codes[token_id] = ord(text[0])
    _FIRST_CODES_CACHE[id(vocabulary)] = (vocabulary, codes)
    return codes


def _pick_best_valid_token(
    scores: np.ndarray[Any, Any],
    vocabulary: Vocabulary,
    grammar: FunctionCallGrammar,
) -> int | None:
    """Return the highest-scoring token id that the grammar accepts.

    Equivalent to masking every invalid logit with ``-inf`` and taking the
    argmax (Sec. V.3.3), but lazy and cheap:

    * Tokens are visited from the most to the least probable and the search
      stops at the first valid one, so normally only a few are validated
      instead of all ~151k.
    * Before simulating a whole token through the grammar we only check its
      *first character*, once per distinct character (not per token). Each
      block of candidates is filtered with numpy, so Python only simulates
      the tokens whose first character the grammar can accept.

    Tokens whose text piece is empty (special tokens such as
    ``<|im_end|>``, or ids missing from the vocabulary) are skipped: the
    grammar treats an empty piece as trivially valid, but picking one
    would make no progress and loop until MAX_NEW_TOKENS.

    Args:
        scores: Next-token logits, one per token id.
        vocabulary: Id -> text mapping.
        grammar: Grammar tracking the text generated so far.

    Returns:
        The chosen token id, or ``None`` if no token can extend the text.
    """
    size = int(scores.shape[0])
    first_codes = _first_codes(vocabulary, size)
    order = np.argsort(scores)[::-1]
    first_ok: dict[int, bool] = {}

    for lo in range(0, size, CHUNK_SIZE):
        chunk = order[lo:lo + CHUNK_SIZE]
        codes = first_codes[chunk]
        for code in np.unique(codes).tolist():
            if code >= 0 and code not in first_ok:
                first_ok[code] = grammar.is_valid_continuation(chr(code))
        usable = [code for code, ok in first_ok.items() if ok]
        for token_id in chunk[np.isin(codes, usable)].tolist():
            piece = vocabulary.piece(token_id)
            if len(piece) == 1 or grammar.is_valid_continuation(piece):
                return int(token_id)
    return None


def generate_function_call(
    sdk: LLMSDK,
    vocabulary: Vocabulary,
    prompt_text: str,
    functions: list[FunctionDefinition],
) -> dict[str, Any]:
    """Run one constrained-decoding generation and parse its JSON output.

    Args:
        sdk: The LLM SDK wrapper instance.
        vocabulary: Preloaded id<->text vocabulary for ``sdk``.
        prompt_text: The natural-language user request.
        functions: The available function definitions.

    Returns:
        A dict with keys ``name`` and ``parameters``, guaranteed to satisfy
        the grammar built from ``functions``.

    Raises:
        GenerationError: If the model cannot produce a valid completion
            within :data:`MAX_NEW_TOKENS`, or if the SDK misbehaves.
    """
    grammar = FunctionCallGrammar(functions)
    full_prompt = build_prompt(prompt_text, functions)

    try:
        input_ids = _encoded_to_ids(sdk.encode(full_prompt))
    except Exception as exc:  # pragma: no cover - depends on external SDK
        raise GenerationError(f"Fallo al tokenizar el prompt: {exc}") from exc

    generated_ids: list[int] = []

    for _ in range(MAX_NEW_TOKENS):
        try:
            logits = sdk.get_logits_from_input_ids(input_ids + generated_ids)
        except Exception as exc:  # pragma: no cover - depends on external SDK
            raise GenerationError(f"Fallo al llamar al LLM: {exc}") from exc

        scores = _logits_to_array(logits)
        next_id = _pick_best_valid_token(scores, vocabulary, grammar)

        if next_id is None:
            if grammar.is_complete():
                break
            raise GenerationError(
                "La gramatica llego a un callejon sin salida sin completar "
                "un JSON valido. Texto generado hasta ahora: "
                f"{grammar.generated_text!r}"
            )

        piece = vocabulary.piece(next_id)
        grammar.advance(piece)
        generated_ids.append(next_id)

        if grammar.is_complete() and not grammar.has_pending_transitions():
            break
    else:
        raise GenerationError(
            f"Se alcanzo el limite de {MAX_NEW_TOKENS} tokens sin completar "
            f"un JSON valido. Texto generado: {grammar.generated_text!r}"
        )

    try:
        parsed = json.loads(grammar.generated_text)
    except json.JSONDecodeError as exc:  # pragma: no cover - grammar bug guard
        raise GenerationError(
            f"El texto generado no es JSON valido pese a pasar la "
            f"gramatica: {grammar.generated_text!r} ({exc})"
        ) from exc

    name = parsed.get("function")
    parameters: dict[str, Any] = parsed.get("arguments", {})

    declared = next((fn for fn in functions if fn.name == name), None)
    if declared is not None:
        for key, spec in declared.parameters.items():
            value = parameters.get(key)
            if (
                spec.type == "number"
                and isinstance(value, int)
                and not isinstance(value, bool)
            ):
                parameters[key] = float(value)

    return {"name": name, "parameters": parameters}
