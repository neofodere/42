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

# Hard safety cap so a pathological logits distribution (or a bug) can never
# spin forever. The grammar itself already bounds every value's length (see
# MAX_STRING_CHARS/MAX_NUMBER_DIGITS in grammar.py); this is a second,
# independent safety net sized generously above that worst case even if the
# tokenizer only ever produced single-character tokens.
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

    def get_path_to_vocabulary_json(self) -> str:
        ...

    def encode(self, text: str) -> list[int]:
        ...


class GenerationError(Exception):
    """Raised when a constrained generation cannot be completed safely."""


def build_prompt(user_request: str, functions: list[FunctionDefinition]) -> str:
    """Build the natural-language prompt shown to the LLM.

    The exact wording only nudges the model towards a sensible starting
    distribution; correctness of the final JSON never depends on the model
    "getting it right" from the prompt alone, since constrained decoding
    enforces validity regardless of what the prompt looks like.

    Args:
        user_request: The natural-language request to translate.
        functions: The available function definitions.

    Returns:
        The full prompt text to feed to the tokenizer.
    """
    lines = [
        "You are a function-calling engine. Given a user request and a list "
        "of available functions, respond with a single JSON object "
        'of the form {"function": <name>, "arguments": {...}} choosing the '
        "single best matching function and filling in its arguments from "
        "the request.",
        "",
        "Available functions:",
    ]
    for fn in functions:
        params_desc = ", ".join(
            f"{name}: {spec.type}" for name, spec in fn.parameters.items()
        )
        lines.append(f"- {fn.name}({params_desc}): {fn.description}")
    lines.append("")
    lines.append(f'User request: "{user_request}"')
    lines.append("JSON response:")
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
        A dict with keys ``fn_name`` and ``args``, guaranteed to satisfy the
        grammar built from ``functions``.

    Raises:
        GenerationError: If the model cannot produce a valid completion
            within :data:`MAX_NEW_TOKENS`, or if the SDK misbehaves.
    """
    grammar = FunctionCallGrammar(functions)
    full_prompt = build_prompt(prompt_text, functions)

    try:
        input_ids = list(sdk.encode(full_prompt))
    except Exception as exc:  # pragma: no cover - depends on external SDK
        raise GenerationError(f"Fallo al tokenizar el prompt: {exc}") from exc

    generated_ids: list[int] = []

    for _ in range(MAX_NEW_TOKENS):
        try:
            logits = sdk.get_logits_from_input_ids(input_ids + generated_ids)
        except Exception as exc:  # pragma: no cover - depends on external SDK
            raise GenerationError(f"Fallo al llamar al LLM: {exc}") from exc

        scores = _logits_to_array(logits)

        valid_token_ids = [
            token_id
            for token_id in range(min(vocabulary.size, scores.shape[0]))
            if grammar.is_valid_continuation(vocabulary.piece(token_id))
        ]

        if not valid_token_ids:
            if grammar.is_complete():
                break
            raise GenerationError(
                "La gramatica llego a un callejon sin salida sin completar "
                f"un JSON valido. Texto generado hasta ahora: "
                f"{grammar.generated_text!r}"
            )

        masked_scores = np.full_like(scores, -np.inf)
        valid_indices = np.array(valid_token_ids)
        masked_scores[valid_indices] = scores[valid_indices]
        next_id = int(np.argmax(masked_scores))

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

    return {"fn_name": parsed.get("function"), "args": parsed.get("arguments", {})}
