"""Entrypoint for ``uv run python -m src [--input <file>] [--output <file>]``.

Per the assignment (Sec. IV.3.2), by default input is read from
``data/input/`` and output written to ``data/output/``; ``--input``/
``--output`` let the caller override the paths.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.generator import GenerationError, generate_function_call
from src.io_utils import InputFileError, load_function_definitions, load_prompts, save_results
from src.vocabulary import load_vocabulary

DEFAULT_TESTS_FILE = Path("data/input/function_calling_tests.json")
DEFAULT_DEFINITIONS_FILE = Path("data/input/function_definitions.json")
DEFAULT_OUTPUT_FILE = Path("data/output/function_calling_results.json")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m src",
        description=(
            "Traduce peticiones en lenguaje natural en llamadas a funcion "
            "estructuradas, usando decodificacion restringida."
        ),
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help=(
            "Ruta al archivo de prompts (function_calling_tests.json). "
            "Por defecto: data/input/function_calling_tests.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help="Ruta del JSON de salida. Por defecto: data/output/function_calling_results.json",
    )
    parser.add_argument(
        "--definitions",
        type=Path,
        default=DEFAULT_DEFINITIONS_FILE,
        help=(
            "Ruta al archivo de definiciones de funcion. "
            "Por defecto: data/input/function_definitions.json"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the full pipeline; returns a process exit code."""
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    tests_path = args.input if args.input is not None else DEFAULT_TESTS_FILE

    try:
        prompts = load_prompts(tests_path)
        functions = load_function_definitions(args.definitions)
    except InputFileError as exc:
        print(f"Error de configuracion: {exc}", file=sys.stderr)
        return 1

    try:
        from llm_sdk import Small_LLM_Model  # imported lazily: heavy dependency
    except ImportError as exc:
        print(
            "Error: no se pudo importar 'llm_sdk.Small_LLM_Model'. "
            "Asegurate de haber copiado el directorio llm_sdk/ junto a src/. "
            f"Detalle: {exc}",
            file=sys.stderr,
        )
        return 1

    try:
        sdk = Small_LLM_Model()
    except Exception as exc:
        print(f"Error al inicializar el modelo LLM: {exc}", file=sys.stderr)
        return 1

    try:
        vocabulary = load_vocabulary(Path(sdk.get_path_to_vocabulary_json()), sdk=sdk)
    except Exception as exc:
        print(f"Error al cargar el vocabulario del modelo: {exc}", file=sys.stderr)
        return 1

    results = []
    failures = 0
    for prompt in prompts:
        try:
            call = generate_function_call(sdk, vocabulary, prompt, functions)
        except GenerationError as exc:
            failures += 1
            print(f"Aviso: no se pudo procesar el prompt {prompt!r}: {exc}", file=sys.stderr)
            continue
        results.append({"prompt": prompt, "fn_name": call["fn_name"], "args": call["args"]})

    try:
        save_results(args.output, results)
    except InputFileError as exc:
        print(f"Error al guardar los resultados: {exc}", file=sys.stderr)
        return 1

    print(
        f"Procesados {len(results)}/{len(prompts)} prompts correctamente "
        f"({failures} fallos). Salida escrita en {args.output}."
    )
    # Exit 0 on full or partial success (individual prompt failures are
    # reported above but do not abort the batch); only exit 1 when every
    # single prompt failed, since then the output file is effectively empty.
    total_failure = failures > 0 and not results
    return 1 if total_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
