"""Unit tests for the constrained-decoding grammar engine.

These tests never touch ``llm_sdk`` on purpose: the grammar's correctness
should be verifiable in complete isolation from any actual model, which is
exactly why it is implemented as a standalone character-level automaton.
"""

from __future__ import annotations

import json

import pytest

from src.grammar import FunctionCallGrammar
from src.schema import FunctionDefinition


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
        FunctionDefinition.model_validate(
            {
                "name": "fn_toggle_flag",
                "description": "Flip a boolean flag",
                "parameters": {"enabled": {"type": "boolean"}},
                "returns": {"type": "boolean"},
            }
        ),
    ]


def _feed(grammar: FunctionCallGrammar, text: str) -> None:
    """Feed a string one character at a time, like real generation would."""
    for char in text:
        assert grammar.is_valid_continuation(char), (
            f"char {char!r} rejected after {grammar.generated_text!r}"
        )
        grammar.advance(char)


def test_accepts_exact_valid_output_for_numbers(functions: list[FunctionDefinition]) -> None:
    grammar = FunctionCallGrammar(functions)
    target = '{"function":"fn_add_numbers","arguments":{"a":40,"b":2}}'
    _feed(grammar, target)
    assert grammar.is_complete()
    assert json.loads(grammar.generated_text) == json.loads(target)


def test_accepts_negative_and_decimal_numbers(functions: list[FunctionDefinition]) -> None:
    grammar = FunctionCallGrammar(functions)
    target = '{"function":"fn_add_numbers","arguments":{"a":-3.5,"b":0}}'
    _feed(grammar, target)
    assert grammar.is_complete()


def test_accepts_string_argument_with_escaped_quote(
    functions: list[FunctionDefinition],
) -> None:
    grammar = FunctionCallGrammar(functions)
    target = r'{"function":"fn_reverse_string","arguments":{"s":"he said \"hi\""}}'
    _feed(grammar, target)
    assert grammar.is_complete()
    parsed = json.loads(grammar.generated_text)
    assert parsed["arguments"]["s"] == 'he said "hi"'


def test_accepts_boolean_argument(functions: list[FunctionDefinition]) -> None:
    grammar = FunctionCallGrammar(functions)
    target = '{"function":"fn_toggle_flag","arguments":{"enabled":true}}'
    _feed(grammar, target)
    assert grammar.is_complete()


def test_rejects_unknown_function_name(functions: list[FunctionDefinition]) -> None:
    grammar = FunctionCallGrammar(functions)
    prefix = '{"function":"fn_does_not_exist'
    valid_so_far = True
    for char in prefix:
        if not grammar.is_valid_continuation(char):
            valid_so_far = False
            break
        grammar.advance(char)
    assert not valid_so_far


def test_rejects_wrong_argument_type(functions: list[FunctionDefinition]) -> None:
    grammar = FunctionCallGrammar(functions)
    # "a" expects a number, not a quoted string.
    prefix = '{"function":"fn_add_numbers","arguments":{"a":"'
    with pytest.raises(AssertionError):
        _feed(grammar, prefix)


def test_rejects_trailing_comma(functions: list[FunctionDefinition]) -> None:
    grammar = FunctionCallGrammar(functions)
    prefix = '{"function":"fn_toggle_flag","arguments":{"enabled":true,'
    with pytest.raises(AssertionError):
        _feed(grammar, prefix)


def test_no_parameters_function_produces_empty_arguments() -> None:
    functions = [
        FunctionDefinition.model_validate(
            {"name": "fn_ping", "description": "Ping", "parameters": {}}
        )
    ]
    grammar = FunctionCallGrammar(functions)
    target = '{"function":"fn_ping","arguments":{}}'
    _feed(grammar, target)
    assert grammar.is_complete()
