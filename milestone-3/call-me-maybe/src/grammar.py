"""Hand-rolled constrained-decoding grammar for the function-call JSON.

We never rely on the model spontaneously producing valid JSON (explicitly
forbidden by the assignment). Instead we build, once per set of available
functions, a small NFA (nondeterministic finite automaton) describing every
byte-for-byte valid output string:

    {"function":"<one of the known names>","arguments":{<params...>}}

where ``<params...>`` is the comma-separated, fixed-order list of
``"key":<value>`` pairs required by whichever function got chosen, and
``<value>`` is a proper JSON string/number/integer/boolean literal.

At every generation step we walk the *current* NFA state set forward by one
candidate token's text and keep only the tokens that keep at least one path
alive -- this is "decodificacion restringida" from Sec. V.3.3 of the
assignment: invalid tokens get their logits set to -inf before sampling.

No third-party constrained-decoding library (outlines, guidance, etc.) is
used anywhere in this module, only the standard library, per the
assignment's "Requisitos adicionales".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.schema import FunctionDefinition

CharPredicate = Callable[[str], bool]


# --------------------------------------------------------------------------
# Low-level NFA plumbing
# --------------------------------------------------------------------------


class _StateGraph:
    """Owns every state and transition of one compiled grammar."""

    def __init__(self) -> None:
        self._char_transitions: dict[int, list[tuple[CharPredicate, int]]] = {}
        self._epsilon_transitions: dict[int, list[int]] = {}
        self._next_id = 0

    def new_state(self) -> int:
        """Allocate and return a fresh state id."""
        state = self._next_id
        self._next_id += 1
        return state

    def add_char_transition(self, src: int, predicate: CharPredicate, dst: int) -> None:
        """Register a transition ``src --char matching predicate--> dst``."""
        self._char_transitions.setdefault(src, []).append((predicate, dst))

    def add_epsilon(self, src: int, dst: int) -> None:
        """Register a free (no input consumed) transition ``src -> dst``."""
        self._epsilon_transitions.setdefault(src, []).append(dst)

    def epsilon_closure(self, states: frozenset[int]) -> frozenset[int]:
        """Return every state reachable from ``states`` via epsilon edges."""
        stack = list(states)
        closure = set(states)
        while stack:
            state = stack.pop()
            for nxt in self._epsilon_transitions.get(state, ()):
                if nxt not in closure:
                    closure.add(nxt)
                    stack.append(nxt)
        return frozenset(closure)

    def step(self, states: frozenset[int], char: str) -> frozenset[int]:
        """Advance a state set by one character, returning the new state set."""
        raw_next: set[int] = set()
        for state in states:
            for predicate, dst in self._char_transitions.get(state, ()):
                if predicate(char):
                    raw_next.add(dst)
        if not raw_next:
            return frozenset()
        return self.epsilon_closure(frozenset(raw_next))


@dataclass(frozen=True)
class _Fragment:
    """A partial NFA: one entry point, one or more accepting exit points."""

    start: int
    accepts: frozenset[int]


# --------------------------------------------------------------------------
# Regex-like combinators (Thompson-style construction)
# --------------------------------------------------------------------------


def _make_equals_predicate(expected: str) -> CharPredicate:
    """Return a predicate matching exactly the given single character.

    Written as a proper closure factory (rather than a default-argument
    lambda trick) so each predicate captures its own ``expected`` value
    correctly and the type checker can infer it cleanly.
    """

    def predicate(char: str) -> bool:
        return char == expected

    return predicate


def _literal(graph: _StateGraph, text: str) -> _Fragment:
    """Build a fragment matching ``text`` exactly, character by character."""
    start = graph.new_state()
    current = start
    for char in text:
        nxt = graph.new_state()
        graph.add_char_transition(current, _make_equals_predicate(char), nxt)
        current = nxt
    return _Fragment(start=start, accepts=frozenset({current}))


def _char_class(graph: _StateGraph, predicate: CharPredicate) -> _Fragment:
    """Build a fragment matching exactly one character satisfying ``predicate``."""
    start = graph.new_state()
    end = graph.new_state()
    graph.add_char_transition(start, predicate, end)
    return _Fragment(start=start, accepts=frozenset({end}))


def _epsilon_fragment(graph: _StateGraph) -> _Fragment:
    """Build a fragment matching the empty string."""
    state = graph.new_state()
    return _Fragment(start=state, accepts=frozenset({state}))


def _concat(graph: _StateGraph, fragments: list[_Fragment]) -> _Fragment:
    """Chain fragments so each one's accepts feed the next one's start."""
    if not fragments:
        return _epsilon_fragment(graph)
    head, *rest = fragments
    prev_accepts = head.accepts
    for frag in rest:
        for acc in prev_accepts:
            graph.add_epsilon(acc, frag.start)
        prev_accepts = frag.accepts
    return _Fragment(start=head.start, accepts=prev_accepts)


def _union(graph: _StateGraph, fragments: list[_Fragment]) -> _Fragment:
    """Match any one of the given fragments (used for the name enum)."""
    start = graph.new_state()
    accepts: set[int] = set()
    for frag in fragments:
        graph.add_epsilon(start, frag.start)
        accepts |= set(frag.accepts)
    return _Fragment(start=start, accepts=frozenset(accepts))


def _optional(graph: _StateGraph, frag: _Fragment) -> _Fragment:
    """Match ``frag`` zero or one time."""
    start = graph.new_state()
    end = graph.new_state()
    graph.add_epsilon(start, frag.start)
    graph.add_epsilon(start, end)
    for acc in frag.accepts:
        graph.add_epsilon(acc, end)
    return _Fragment(start=start, accepts=frozenset({end}))


def _plus(graph: _StateGraph, frag: _Fragment) -> _Fragment:
    """Match ``frag`` one or more times, by looping its accepts to its start."""
    for acc in frag.accepts:
        graph.add_epsilon(acc, frag.start)
    return frag


def _star(graph: _StateGraph, frag: _Fragment) -> _Fragment:
    """Match ``frag`` zero or more times."""
    return _optional(graph, _plus(graph, frag))


def _bounded_repeat(
    graph: _StateGraph, builder: Callable[[], _Fragment], min_count: int, max_count: int
) -> _Fragment:
    """Match a fresh instance of ``builder()`` between ``min_count`` and
    ``max_count`` times (inclusive), unrolled explicitly.

    Unlike :func:`_star`/:func:`_plus` (which loop back over the *same*
    states and can therefore match arbitrarily long input), this always
    terminates after ``max_count`` repetitions. We use it anywhere a
    pathological/adversarial model could otherwise stall generation forever
    by always preferring "one more character" over closing the value (e.g.
    an unbounded JSON string). Each repetition gets its own fresh states
    (``builder`` is called once per slot), which is required because a
    single NFA state cannot be reused at two different unrolled positions.
    """
    if max_count <= 0:
        return _epsilon_fragment(graph)
    slots: list[_Fragment] = []
    for index in range(max_count):
        frag = builder()
        slots.append(frag if index < min_count else _optional(graph, frag))
    return _concat(graph, slots)


# Safety caps for otherwise-unbounded JSON values: long enough for any
# realistic function-calling argument, short enough to guarantee the
# decoding loop always terminates well within MAX_NEW_TOKENS even if the
# model always prefers "keep going" over closing the value.
MAX_STRING_CHARS = 120
MAX_NUMBER_DIGITS = 18


# --------------------------------------------------------------------------
# JSON value grammars
# --------------------------------------------------------------------------


def _is_digit(char: str) -> bool:
    return "0" <= char <= "9"


def _is_nonzero_digit(char: str) -> bool:
    return "1" <= char <= "9"


def _json_escape_literal(text: str) -> str:
    """Escape a plain identifier so it is safe to splice into a JSON literal."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _number_fragment(graph: _StateGraph, allow_fraction: bool = True) -> _Fragment:
    """Build a fragment matching a JSON number (optionally integer-only)."""
    parts: list[_Fragment] = []
    parts.append(_optional(graph, _literal(graph, "-")))

    zero = _literal(graph, "0")
    nonzero_head = _char_class(graph, _is_nonzero_digit)
    nonzero_tail = _bounded_repeat(
        graph, lambda: _char_class(graph, _is_digit), 0, MAX_NUMBER_DIGITS - 1
    )
    nonzero = _concat(graph, [nonzero_head, nonzero_tail])
    parts.append(_union(graph, [zero, nonzero]))

    if allow_fraction:
        frac_dot = _literal(graph, ".")
        frac_digits = _bounded_repeat(
            graph, lambda: _char_class(graph, _is_digit), 1, MAX_NUMBER_DIGITS
        )
        frac = _concat(graph, [frac_dot, frac_digits])
        parts.append(_optional(graph, frac))

        exp_marker = _char_class(graph, lambda c: c in ("e", "E"))
        exp_sign = _optional(graph, _char_class(graph, lambda c: c in ("+", "-")))
        exp_digits = _bounded_repeat(graph, lambda: _char_class(graph, _is_digit), 1, 6)
        exponent = _concat(graph, [exp_marker, exp_sign, exp_digits])
        parts.append(_optional(graph, exponent))

    return _concat(graph, parts)


def _string_fragment(graph: _StateGraph) -> _Fragment:
    """Build a fragment matching a JSON string literal (with escapes)."""
    open_quote = _literal(graph, '"')

    def is_unescaped_char(char: str) -> bool:
        return char not in ('"', "\\") and ord(char) >= 0x20

    simple_escapes = '"\\/bfnrt'

    def is_hex_digit(char: str) -> bool:
        return char in "0123456789abcdefABCDEF"

    def build_content_char() -> _Fragment:
        return _union(
            graph,
            [
                _char_class(graph, is_unescaped_char),
                _concat(
                    graph,
                    [_literal(graph, "\\"), _char_class(graph, lambda c: c in simple_escapes)],
                ),
                _concat(
                    graph,
                    [
                        _literal(graph, "\\u"),
                        _char_class(graph, is_hex_digit),
                        _char_class(graph, is_hex_digit),
                        _char_class(graph, is_hex_digit),
                        _char_class(graph, is_hex_digit),
                    ],
                ),
            ],
        )

    content = _bounded_repeat(graph, build_content_char, 0, MAX_STRING_CHARS)
    close_quote = _literal(graph, '"')
    return _concat(graph, [open_quote, content, close_quote])


def _boolean_fragment(graph: _StateGraph) -> _Fragment:
    return _union(graph, [_literal(graph, "true"), _literal(graph, "false")])


def _value_fragment(graph: _StateGraph, value_type: str) -> _Fragment:
    """Dispatch to the right JSON value grammar for a parameter's type."""
    if value_type == "string":
        return _string_fragment(graph)
    if value_type == "boolean":
        return _boolean_fragment(graph)
    if value_type == "integer":
        return _number_fragment(graph, allow_fraction=False)
    if value_type == "number":
        return _number_fragment(graph, allow_fraction=True)
    # Unknown/unsupported declared type: fall back to a JSON string so the
    # decoder always stays well-defined instead of crashing on odd input.
    return _string_fragment(graph)


def _function_fragment(graph: _StateGraph, fn: FunctionDefinition) -> _Fragment:
    """Build the fragment for one *specific* function's full JSON output."""
    name = _json_escape_literal(fn.name)
    header = _literal(graph, f'{{"function":"{name}","arguments":{{')

    param_items = list(fn.parameters.items())
    param_parts: list[_Fragment] = []
    for index, (key, spec) in enumerate(param_items):
        safe_key = _json_escape_literal(key)
        param_parts.append(_literal(graph, f'"{safe_key}":'))
        param_parts.append(_value_fragment(graph, spec.type))
        if index != len(param_items) - 1:
            param_parts.append(_literal(graph, ","))
    params_fragment = _concat(graph, param_parts) if param_parts else _epsilon_fragment(graph)

    footer = _literal(graph, "}}")
    return _concat(graph, [header, params_fragment, footer])


# --------------------------------------------------------------------------
# Public grammar object
# --------------------------------------------------------------------------


class FunctionCallGrammar:
    """Tracks decoding progress against the function-call output grammar.

    One instance is created per prompt (functions are the same across
    prompts in a given run, but the object is cheap enough to rebuild, and
    keeping it stateful/per-prompt avoids any risk of leftover state).
    """

    def __init__(self, functions: list[FunctionDefinition]) -> None:
        if not functions:
            raise ValueError("FunctionCallGrammar necesita al menos una funcion.")
        self._graph = _StateGraph()
        per_function = [_function_fragment(self._graph, fn) for fn in functions]
        self._nfa = _union(self._graph, per_function)
        self._current_states = self._graph.epsilon_closure(frozenset({self._nfa.start}))
        self.generated_text = ""

    def _simulate(self, states: frozenset[int], text: str) -> frozenset[int]:
        for char in text:
            if not states:
                return frozenset()
            states = self._graph.step(states, char)
        return states

    def is_valid_continuation(self, piece: str) -> bool:
        """Would appending ``piece`` keep at least one valid parse alive?"""
        if not piece:
            return True
        return bool(self._simulate(self._current_states, piece))

    def advance(self, piece: str) -> None:
        """Commit ``piece`` as generated text, updating internal progress.

        Raises:
            ValueError: If ``piece`` is not a valid continuation. Callers
                must only pass pieces already checked with
                :meth:`is_valid_continuation`.
        """
        new_states = self._simulate(self._current_states, piece)
        if not new_states:
            raise ValueError(
                f"Token invalido para la gramatica: {piece!r} tras "
                f"{self.generated_text!r}"
            )
        self._current_states = new_states
        self.generated_text += piece

    def is_complete(self) -> bool:
        """Is the text generated so far already a fully valid JSON output?"""
        return any(state in self._nfa.accepts for state in self._current_states)

    def has_pending_transitions(self) -> bool:
        """Could any further character still extend the current text?"""
        for state in self._current_states:
            if self._graph._char_transitions.get(state):
                return True
        return False
