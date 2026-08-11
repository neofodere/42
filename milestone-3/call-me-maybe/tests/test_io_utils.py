"""Tests for defensive input/output handling."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.io_utils import InputFileError, load_function_definitions, load_prompts, save_results


def test_load_prompts_missing_file(tmp_path: Path) -> None:
    with pytest.raises(InputFileError, match="no existe"):
        load_prompts(tmp_path / "missing.json")


def test_load_prompts_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "tests.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(InputFileError, match="JSON valido"):
        load_prompts(path)


def test_load_prompts_wrong_top_level_type(tmp_path: Path) -> None:
    path = tmp_path / "tests.json"
    path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
    with pytest.raises(InputFileError, match="array JSON"):
        load_prompts(path)


def test_load_prompts_happy_path(tmp_path: Path) -> None:
    path = tmp_path / "tests.json"
    path.write_text(json.dumps(["a", "b"]), encoding="utf-8")
    assert load_prompts(path) == ["a", "b"]


def test_load_function_definitions_missing_file(tmp_path: Path) -> None:
    with pytest.raises(InputFileError, match="no existe"):
        load_function_definitions(tmp_path / "missing.json")


def test_load_function_definitions_invalid_entry(tmp_path: Path) -> None:
    path = tmp_path / "defs.json"
    path.write_text(json.dumps([{"description": "missing name"}]), encoding="utf-8")
    with pytest.raises(InputFileError, match="invalida"):
        load_function_definitions(path)


def test_load_function_definitions_happy_path(tmp_path: Path) -> None:
    path = tmp_path / "defs.json"
    path.write_text(
        json.dumps(
            [
                {
                    "name": "fn_add_numbers",
                    "description": "Add",
                    "parameters": {"a": {"type": "number"}, "b": {"type": "number"}},
                    "returns": {"type": "number"},
                }
            ]
        ),
        encoding="utf-8",
    )
    definitions = load_function_definitions(path)
    assert definitions[0].name == "fn_add_numbers"
    assert definitions[0].parameters["a"].type == "number"


def test_save_results_creates_parent_dirs(tmp_path: Path) -> None:
    out_path = tmp_path / "nested" / "output.json"
    save_results(out_path, [{"prompt": "p", "fn_name": "f", "args": {}}])
    assert out_path.exists()
    assert json.loads(out_path.read_text(encoding="utf-8")) == [
        {"prompt": "p", "fn_name": "f", "args": {}}
    ]
