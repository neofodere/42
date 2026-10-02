"""Entrypoint for ``uv run python -m src [--functions_definition <file>]
[--input <file>] [--output <file>]``.

Per the assignment (Sec. IV.3.2), by default input is read from
``data/input/`` and output written to ``data/output/``;
``--functions_definition``/``--input``/``--output`` let the caller
override the paths.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.generator import GenerationError, generate_function_call
from src.io_utils import InputFileError, load_function_definitions, load_prompts, save_results
from src.vocabulary import load_vocabulary

DEFAULT_TESTS_FILE = Path("data/input/function_calling_tests.json")
DEFAULT_DEFINITIONS_FILE = Path("data/input/functions_definition.json")
DEFAULT_OUTPUT_FILE = Path("data/output/function_calling_results.json")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m src",
        description=(
            "Translate natural language requests into structured function "
            "calls using restricted decoding."
        ),
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help=(
            "Path to the prompts file (function_calling_tests.json). "
            "Default: data/input/function_calling_tests.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help="Path to the output JSON file. Default: data/output/function_calling_results.json",
    )
    parser.add_argument(
        "--functions_definition",
        type=Path,
        default=DEFAULT_DEFINITIONS_FILE,
        help=(
            "Path to the function definitions file. "
            "Default: data/input/functions_definition.json"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the full pipeline; returns a process exit code."""
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    tests_path = args.input if args.input is not None else DEFAULT_TESTS_FILE

    try:
        prompts = load_prompts(tests_path)
        functions = load_function_definitions(args.functions_definition)
    except InputFileError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1

    try:
        from llm_sdk import Small_LLM_Model
    except ImportError as exc:
        print(
            "Error: Could not import ‘llm_sdk.Small_LLM_Model’. "
            "Make sure you've copied the llm_sdk/ directory next to src/. "
            f"Details: {exc}",
            file=sys.stderr,
        )
        return 1

    try:
        sdk = Small_LLM_Model()
    except Exception as exc:
        print(f"Error initializing the LLM model: {exc}", file=sys.stderr)
        return 1

    try:
        vocabulary = load_vocabulary(Path(sdk.get_path_to_vocab_file()), sdk=sdk)
    except Exception as exc:
        print(f"Error loading the model vocabulary: {exc}", file=sys.stderr)
        return 1

    results = []
    failures = 0
    for prompt in prompts:
        try:
            call = generate_function_call(sdk, vocabulary, prompt, functions)
        except GenerationError as exc:
            failures += 1
            print(f"Notice: The prompt could not be processed {prompt!r}: {exc}", file=sys.stderr)
            continue
        results.append(
            {"prompt": prompt, "name": call["name"], "parameters": call["parameters"]}
        )

    try:
        save_results(args.output, results)
    except InputFileError as exc:
        print(f"Error at saving results: {exc}", file=sys.stderr)
        return 1

    print(
        f"Processed {len(results)}/{len(prompts)} prompts correctly "
        f"({failures} failures). Correct output at {args.output}."
    )
    total_failure = failures > 0 and not results
    return 1 if total_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
