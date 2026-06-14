def garden_operations() -> None:
    """
    Demonstrates common Python errors.
    """
    print("Testing ValueError...")
    try:
        int("abc")
    except ValueError as err:
        print(f"Caught ValueError: {err}")
    print("Testing ZeroDivisionError...")
    try:
        10 / 0
    except ZeroDivisionError as err:
        print(f"Caught ZeroDivisionError: {err}")
    print("Testing FileNotFoundError...")
    try:
        f = open("missing.txt", "r")
        f.close()
    except FileNotFoundError as err:
        print(f"Caught FileNotFoundError: {err}")
    print("Testing KeyError...")
    try:
        plants = {"tomato": 30, "lettuce": 20}
        print(plants["missing_plant"])
    except KeyError as err:
        print(f"Caught KeyError: {err}")
    print("Testing multiple errors together...")
    try:
        int("oops")
        5 / 0
    except (ValueError, ZeroDivisionError):
        print("Caught an error, but program continues!")


def test_error_types() -> None:
    """
    Runs error type demonstrations.
    """
    print("=== Garden Error Types Demo ===")
    garden_operations()
    print("All error types tested successfully!")


if __name__ == "__main__":
    test_error_types()
