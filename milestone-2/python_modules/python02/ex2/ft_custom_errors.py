class GardenError(Exception):
    """Base error for garden issues."""
    pass


class PlantError(GardenError):
    """Error related to plant problems."""
    pass


class WaterError(GardenError):
    """Error related to watering problems."""
    pass


def raise_plant_error() -> None:
    """Raises a PlantError."""
    raise PlantError("The tomato plant is wilting!")


def raise_water_error() -> None:
    """Raises a WaterError."""
    raise WaterError("Not enough water in the tank!")


def test_custom_errors() -> None:
    """Runs custom error demonstrations."""
    print("=== Custom Garden Errors Demo ===")
    print("Testing PlantError...")
    try:
        raise_plant_error()
    except PlantError as err:
        print(f"Caught PlantError: {err}")
    print("Testing WaterError...")
    try:
        raise_water_error()
    except WaterError as err:
        print(f"Caught WaterError: {err}")
    print("Testing catching all garden errors...")
    for func in (raise_plant_error, raise_water_error):
        try:
            func()
        except GardenError as err:
            print(f"Caught a garden error: {err}")
    print("All custom error types work correctly!")


if __name__ == "__main__":
    test_custom_errors()
