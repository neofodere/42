def check_temperature(temp_str: str) -> int | None:
    """
    Validates a temperature reading.
    """
    try:
        temp = int(temp_str)
    except ValueError:
        print(f"Error: '{temp_str}' is not a valid number")
        return (None)
    if (temp < 0):
        print(f"Error: {temp}°C is too cold for plants (min 0°C)")
        return (None)
    if (temp > 40):
        print(f"Error: {temp}°C is too hot for plants (max 40°C)")
        return (None)
    print(f"Temperature {temp}°C is perfect for plants!")
    return (temp)


def test_temperature_input() -> None:
    """
    Runs temperature validation tests.
    """
    print("=== Garden Temperature Checker ===")
    tests = ["25", "abc", "100", "-50"]
    for test in tests:
        print(f"Testing temperature: {test}")
        check_temperature(test)
    print("All tests completed - program didn't crash!")


if __name__ == "__main__":
    test_temperature_input()
