"""Input/output helpers with defensive error handling.

The assignment explicitly warns that input files "pueden contener JSON no
valido o directamente no existir" (Sec. V.2.2), so every read here fails
loudly with a clear, actionable message instead of crashing with a raw
traceback.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.schema import FunctionDefinition


class InputFileError(Exception):
    """Raised when an input file is missing, unreadable, or malformed."""


def _read_json_file(path: Path) -> Any:
    """Read and parse a JSON file, raising :class:`InputFileError` on failure.

    Args:
        path: Path to the JSON file to read.

    Returns:
        The parsed JSON content (list, dict, etc.).

    Raises:
        InputFileError: If the file does not exist, cannot be read, or does
            not contain valid JSON.
    """
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise InputFileError(f"El archivo de entrada no existe: {path}") from exc
    except PermissionError as exc:
        raise InputFileError(f"Sin permisos para leer: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InputFileError(
            f"El archivo {path} no contiene un JSON valido "
            f"(linea {exc.lineno}, columna {exc.colno}): {exc.msg}"
        ) from exc
    except OSError as exc:
        raise InputFileError(f"No se pudo leer {path}: {exc}") from exc


def load_prompts(path: Path) -> list[str]:
    """Load the list of natural-language prompts to process.

    Args:
        path: Path to ``function_calling_tests.json``.

    Returns:
        A list of prompt strings. Non-string or empty entries are skipped
        with a warning-free, best-effort approach so that one bad row does
        not prevent processing the rest of a large batch.

    Raises:
        InputFileError: If the file is missing, malformed, or is not a
            JSON array.
    """
    data = _read_json_file(path)
    if not isinstance(data, list):
        raise InputFileError(
            f"{path} debe contener un array JSON de prompts, "
            f"se encontro: {type(data).__name__}"
        )
    prompts: list[str] = []
    for index, item in enumerate(data):
        if not isinstance(item, str):
            raise InputFileError(
                f"{path}: el elemento en la posicion {index} no es una "
                f"cadena de texto ({item!r})"
            )
        prompts.append(item)
    return prompts


def load_function_definitions(path: Path) -> list[FunctionDefinition]:
    """Load and validate the available function definitions.

    Args:
        path: Path to ``function_definitions.json``.

    Returns:
        A list of validated :class:`FunctionDefinition` objects.

    Raises:
        InputFileError: If the file is missing, malformed, is not a JSON
            array, or an entry fails schema validation.
    """
    data = _read_json_file(path)
    if not isinstance(data, list):
        raise InputFileError(
            f"{path} debe contener un array JSON de definiciones de "
            f"funcion, se encontro: {type(data).__name__}"
        )
    definitions: list[FunctionDefinition] = []
    for index, item in enumerate(data):
        try:
            definitions.append(FunctionDefinition.model_validate(item))
        except ValidationError as exc:
            raise InputFileError(
                f"{path}: la definicion de funcion en la posicion {index} "
                f"es invalida: {exc}"
            ) from exc
    if not definitions:
        raise InputFileError(f"{path} no define ninguna funcion utilizable.")
    return definitions


def save_results(path: Path, results: list[dict[str, Any]]) -> None:
    """Write the final results array as pretty-printed JSON.

    Args:
        path: Destination path (parent directories are created if needed).
        results: List of plain dict entries, each matching the required
            output schema (``prompt``, ``fn_name``, ``args``).

    Raises:
        InputFileError: If the output file cannot be written.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(results, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    except OSError as exc:
        raise InputFileError(f"No se pudo escribir la salida en {path}: {exc}") from exc
