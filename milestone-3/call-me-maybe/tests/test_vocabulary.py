"""Tests for vocabulary loading and byte-level piece decoding."""

from __future__ import annotations

import json
from pathlib import Path

from src.vocabulary import load_vocabulary


def test_decodes_gpt2_style_space_and_newline_markers(tmp_path: Path) -> None:
    # 'Ġ' (U+0120) marks a leading space, 'Ċ' (U+010A) marks a newline in
    # GPT-2/Qwen-style byte-level BPE vocabularies.
    vocab = {
        "Hello": 0,
        "Ġworld": 1,
        "Ċ": 2,
        '"': 3,
    }
    path = tmp_path / "vocab.json"
    path.write_text(json.dumps(vocab), encoding="utf-8")

    loaded = load_vocabulary(path)

    assert loaded.piece(0) == "Hello"
    assert loaded.piece(1) == " world"
    assert loaded.piece(2) == "\n"
    assert loaded.piece(3) == '"'


def test_supports_id_keyed_layout(tmp_path: Path) -> None:
    vocab = {"0": "foo", "1": "bar"}
    path = tmp_path / "vocab.json"
    path.write_text(json.dumps(vocab), encoding="utf-8")

    loaded = load_vocabulary(path)

    assert loaded.piece(0) == "foo"
    assert loaded.piece(1) == "bar"


def test_supports_list_layout(tmp_path: Path) -> None:
    vocab = ["alpha", "beta", "gamma"]
    path = tmp_path / "vocab.json"
    path.write_text(json.dumps(vocab), encoding="utf-8")

    loaded = load_vocabulary(path)

    assert loaded.piece(2) == "gamma"
    assert loaded.size == 3
