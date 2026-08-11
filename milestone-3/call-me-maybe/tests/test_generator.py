"""End-to-end tests for the constrained-decoding generation loop.

We stand in for ``llm_sdk.Small_LLM_Model`` with a tiny mock that hands out
character-level tokens and *deliberately* scores an invalid "poison"
character far above everything else. If the resulting output is still
100% valid, grammar-masking is doing its job -- exactly the property the
assignment asks us to guarantee (Sec. V.1: "asegurando una fiabilidad casi
perfecta incluso con un modelo pequeno").
"""

from __future__ import annotations

import string
from typing import Any

import numpy as np
import pytest

from src.generator import GenerationError, generate_function_call
from src.schema import FunctionDefinition
from src.vocabulary import Vocabulary

POISON_CHAR = "#"


def _build_char_vocabulary() -> Vocabulary:
    alphabet = string.ascii_letters + string.digits + '{}[]":,.-+_ \n' + POISON_CHAR
    id_to_text = {i: ch for i, ch in enumerate(sorted(set(alphabet)))}
    return Vocabulary(id_to_text)


class _AdversarialMockSDK:
    """Always scores the poison token far above every legitimate token."""

    def __init__(self, vocabulary: Vocabulary) -> None:
        self._vocabulary = vocabulary

    def encode(self, text: str) -> list[int]:
        return [0]  # content is irrelevant to this mock's fixed logits

    def get_path_to_vocabulary_json(self) -> str:
        return ""  # unused: tests build the Vocabulary directly

    def get_logits_from_input_ids(self, input_ids: list[int]) -> np.ndarray[Any, Any]:
        scores = np.zeros(self._vocabulary.size)
        for token_id in range(self._vocabulary.size):
            char = self._vocabulary.piece(token_id)
            if char == POISON_CHAR:
                scores[token_id] = 1000.0
            else:
                scores[token_id] = float(ord(char))
        return scores


@pytest.fixture()
def functions() -> list[FunctionDefinition]:
    return [
        FunctionDefinition.model_validate(
            {
                "name": "fn_add_numbers",
                "description": "Add two numbers",
                "parameters": {"a": {"type": "number"}, "b": {"type": "number"}},
                "returns": {"type": "number"},
            }
        ),
        FunctionDefinition.model_validate(
            {
                "name": "fn_reverse_string",
                "description": "Reverse a string",
                "parameters": {"s": {"type": "string"}},
                "returns": {"type": "string"},
            }
        ),
    ]


def test_output_is_always_valid_despite_adversarial_scores(
    functions: list[FunctionDefinition],
) -> None:
    vocabulary = _build_char_vocabulary()
    sdk = _AdversarialMockSDK(vocabulary)

    result = generate_function_call(sdk, vocabulary, "What is the sum of 2 and 3?", functions)

    # Structural validity holds no matter how adversarial the raw scores
    # are: a real function name, exactly the right argument keys, and
    # values of the declared types.
    assert result["fn_name"] in {fn.name for fn in functions}
    chosen = next(fn for fn in functions if fn.name == result["fn_name"])
    assert set(result["args"].keys()) == set(chosen.parameters.keys())
    for key, spec in chosen.parameters.items():
        value = result["args"][key]
        if spec.type in ("number", "integer"):
            assert isinstance(value, (int, float))
            # '#' is not a legal JSON number character: if masking ever
            # failed, this is exactly where it would leak through.
            assert POISON_CHAR not in str(value)
        elif spec.type == "string":
            assert isinstance(value, str)
        elif spec.type == "boolean":
            assert isinstance(value, bool)


def test_poison_token_never_leaks_into_a_numeric_argument() -> None:
    # Force a numeric-only function so the poison character (legal inside a
    # JSON *string* but not inside a *number*) has no legal way to appear
    # anywhere in the output -- proving the mask, not luck, keeps it out.
    functions = [
        FunctionDefinition.model_validate(
            {
                "name": "fn_add_numbers",
                "description": "Add two numbers",
                "parameters": {"a": {"type": "number"}, "b": {"type": "number"}},
            }
        )
    ]
    vocabulary = _build_char_vocabulary()
    sdk = _AdversarialMockSDK(vocabulary)

    result = generate_function_call(sdk, vocabulary, "2 plus 3", functions)

    assert result["fn_name"] == "fn_add_numbers"
    assert POISON_CHAR not in str(result)
    assert isinstance(result["args"]["a"], (int, float))
    assert isinstance(result["args"]["b"], (int, float))


def test_raises_generation_error_when_no_function_fits_alphabet() -> None:
    # A function whose name uses a character absent from the vocabulary can
    # never be produced; this must fail loudly instead of hanging forever.
    vocabulary = Vocabulary({0: "{", 1: "}"})
    functions = [
        FunctionDefinition.model_validate({"name": "fn_add_numbers", "parameters": {}})
    ]

    class _EmptySDK:
        def encode(self, text: str) -> list[int]:
            return [0]

        def get_path_to_vocabulary_json(self) -> str:
            return ""

        def get_logits_from_input_ids(self, input_ids: list[int]) -> np.ndarray[Any, Any]:
            return np.zeros(vocabulary.size)

    with pytest.raises(GenerationError):
        generate_function_call(_EmptySDK(), vocabulary, "hi", functions)
