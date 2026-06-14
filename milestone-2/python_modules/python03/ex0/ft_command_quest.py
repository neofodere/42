#!/usr/bin/env python3
import sys


def main() -> None:
    print("=== Command Quest ===")
    program_name: str = sys.argv[0]
    arguments: list[str] = sys.argv[1:]
    total_args: int = len(sys.argv)
    if (len(arguments) == 0):
        print("No arguments provided!")
        print(f"Program name: {program_name}")
        print(f"Total arguments: {total_args}")
        return
    print(f"Program name: {program_name}")
    print(f"Arguments received: {len(arguments)}")
    for index, arg in enumerate(arguments, start=1):
        print(f"Argument {index}: {arg}")
    print(f"Total arguments: {total_args}")


if __name__ == "__main__":
    main()
