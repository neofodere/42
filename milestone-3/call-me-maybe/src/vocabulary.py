"""Vocabulary loading and token-piece decoding.

``Small_LLM_Model.get_path_to_vocabulary_json`` gives us a JSON file mapping
between token ids and token pieces. Modern byte-level BPE tokenizers (GPT-2,
Llama-3, Qwen2/Qwen3, ...) store vocabularies where each *byte* 0-255 is
remapped to a printable unicode character, so that arbitrary binary data can
be represented as a normal JSON/text string. To reconstruct exactly what a
token *means*, we have to invert that byte<->unicode mapping.

We do not assume this is the only possible layout: at load time we probe a
handful of tokens through the (optional) ``decode`` method of the SDK, if
available, to sanity-check which decoding scheme is in play. If ``decode``
is unavailable we fall back to the byte-level heuristic described above,
which is what Qwen's own tokenizer uses.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol


class DecodeCapable(Protocol):
    """Structural type for an SDK that optionally exposes ``decode``."""

    def decode(self, token_ids: list[int]) -> str:
        ...


def _gpt2_byte_to_unicode() -> dict[int, str]:
    """Build the reversible byte(0-255) -> printable-unicode-char mapping.

    This is the classic scheme used by GPT-2-style byte-level BPE
    tokenizers (also used by Qwen2/Qwen3): printable ASCII/Latin-1 bytes map
    to themselves, and the remaining ~68 byte values are remapped to unused
    codepoints starting at 256, so every byte value has a unique, always
    printable, single-character representation.

    Returns:
        Mapping from byte value (0-255) to its unicode character.
    """
    printable = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("\xa1"), ord("\xac") + 1))
        + list(range(ord("\xae"), ord("\xff") + 1))
    )
    byte_to_char: dict[int, str] = {b: chr(b) for b in printable}
    extra_index = 0
    for byte_value in range(256):
        if byte_value not in byte_to_char:
            byte_to_char[byte_value] = chr(256 + extra_index)
            extra_index += 1
    return byte_to_char


class Vocabulary:
    """Maps token ids to their decoded text piece.

    Attributes:
        id_to_text: Best-effort decoded text for every known token id.
        size: Number of tokens known to the vocabulary.
    """

    def __init__(self, id_to_text: dict[int, str]) -> None:
        self.id_to_text = id_to_text
        self.size = len(id_to_text)

    def piece(self, token_id: int) -> str:
        """Return the decoded text piece for a token id (empty if unknown)."""
        return self.id_to_text.get(token_id, "")


def _load_raw_mapping(path: Path) -> dict[int, str]:
    """Load the raw vocabulary JSON into an ``id -> piece`` dict.

    Handles the two common layouts transparently:
      * ``{"token_piece": id, ...}``  (HuggingFace ``vocab.json`` style)
      * ``{"id": "token_piece", ...}`` or ``[piece0, piece1, ...]``

    Args:
        path: Path to the vocabulary JSON file.

    Returns:
        Mapping from integer token id to its raw (possibly byte-mapped)
        string piece.

    Raises:
        ValueError: If the JSON structure is not one of the supported
            layouts.
    """
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, list):
        return {i: str(piece) for i, piece in enumerate(data)}

    if isinstance(data, dict):
        # Peek at one item to decide which side holds the integer id.
        sample_key, sample_value = next(iter(data.items()))
        if isinstance(sample_value, int) and not str(sample_key).lstrip("-").isdigit():
            # {"piece": id, ...}
            return {int(v): str(k) for k, v in data.items()}
        # {"id": "piece", ...} (ids as string keys) or already {id: piece}.
        return {int(k): str(v) for k, v in data.items()}

    raise ValueError(f"Formato de vocabulario no soportado en {path}")


def load_vocabulary(vocabulary_path: Path, sdk: DecodeCapable | None = None) -> Vocabulary:
    """Load the vocabulary and decode every piece to plain text.

    Args:
        vocabulary_path: Path returned by
            ``Small_LLM_Model.get_path_to_vocabulary_json``.
        sdk: The LLM SDK instance, used opportunistically to validate (and,
            for a handful of tokens, cross-check) the decoding scheme via
            its optional ``decode`` method.

    Returns:
        A ready-to-use :class:`Vocabulary`.
    """
    raw = _load_raw_mapping(vocabulary_path)
    byte_to_char = _gpt2_byte_to_unicode()
    char_to_byte = {char: byte for byte, char in byte_to_char.items()}

    def decode_piece(piece: str) -> str:
        raw_bytes = bytearray()
        for char in piece:
            if char in char_to_byte:
                raw_bytes.append(char_to_byte[char])
            else:
                # Not part of the byte-level alphabet: likely a literal
                # special token (e.g. "<|im_end|>"); keep it verbatim by
                # re-encoding through utf-8 so the byte buffer stays valid.
                raw_bytes.extend(char.encode("utf-8"))
        return raw_bytes.decode("utf-8", errors="replace")

    id_to_text = {token_id: decode_piece(piece) for token_id, piece in raw.items()}

    if sdk is not None and hasattr(sdk, "decode"):
        # Cross-check on a small, cheap sample; if our heuristic disagrees
        # with the SDK's own decoder, trust the SDK for those ids instead.
        sample_ids = list(id_to_text)[:20]
        for token_id in sample_ids:
            try:
                reference = sdk.decode([token_id])
            except Exception:  # pragma: no cover - defensive, SDK-dependent
                break
            if reference and reference != id_to_text[token_id]:
                id_to_text[token_id] = reference

    return Vocabulary(id_to_text)
