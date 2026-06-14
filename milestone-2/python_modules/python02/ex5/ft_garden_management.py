class GardenError(Exception):
    """Base error for garden issues."""
    pass


class PlantError(GardenError):
    """Error related to plant problems."""
    pass


class WaterError(GardenError):
    """Error related to watering problems."""
    pass


def check_plant_health(plant_name: str, water_level: int,
                       sunlight_hours: int) -> str:
    """Validate plant health and raise errors if needed."""
    if plant_name == "":
        raise ValueError("Plant name cannot be empty!")
    if water_level < 1:
        raise ValueError(f"Water level {water_level} is too low (min 1)")
    if water_level > 10:
        raise ValueError(f"Water level {water_level} is too high (max 10)")
    if sunlight_hours < 2:
        raise ValueError(f"Sunlight hours {sunlight_hours} is too low (min 2)")
    if sunlight_hours > 12:
        raise ValueError(
            f"Sunlight hours {sunlight_hours} is too high (max 12)"
        )
    return (
        f"{plant_name}: healthy "
        f"(water: {water_level}, sun: {sunlight_hours})"
    )


class GardenManager:
    """Manage plants and garden operations."""
    def __init__(self) -> None:
        """Initialize an empty garden."""
        self.plants = {}

    def add_plant(self, name: str) -> None:
        """Add a plant to the garden."""
        try:
            if name == "":
                raise PlantError("Plant name cannot be empty!")
            self.plants[name] = {"water": 5, "sun": 8}
            print(f"Added {name} successfully")
        except PlantError as err:
            print(f"Error adding plant: {err}")

    def water_plants(self) -> None:
        """Water all plants with cleanup."""
        print("Watering plants...")
        print("Opening watering system")
        try:
            for name in self.plants:
                if name == "broken":
                    raise WaterError("Not enough water in tank")
                print(f"Watering {name} - success")
        except WaterError as err:
            print(f"Error: {err}")
        finally:
            print("Closing watering system (cleanup)")

    def check_all_plants(self) -> None:
        """Check health of all plants."""
        print("Checking plant health...")
        for name, stats in self.plants.items():
            try:
                result = check_plant_health(
                    name, stats["water"], stats["sun"]
                )
                print(result)
            except ValueError as err:
                print(f"Error checking {name}: {err}")


def test_garden_management() -> None:
    """Run full garden management test."""
    print("=== Garden Management System ===")
    manager = GardenManager()
    print("Adding plants to garden...")
    manager.add_plant("tomato")
    manager.add_plant("lettuce")
    manager.add_plant("")  # invalid
    manager.water_plants()
    manager.check_all_plants()
    print("Testing error recovery...")
    try:
        raise GardenError("Not enough water in tank")
    except GardenError as err:
        print(f"Caught GardenError: {err}")
        print("System recovered and continuing...")
    print("Garden management system test complete!")


if __name__ == "__main__":
    test_garden_management()
