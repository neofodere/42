class Plant:
    """
    Represents a plant with a name, height, and age.
    """
    def __init__(self, name: str, height: int, age: int) -> None:
        """
        Initialize a new Plant with its basic attributes.
        """
        self.name = name
        self.height = height
        self.age = age

    def get_info(self) -> str:
        """
        Return a formatted string describing the plant.
        """
        return (f"{self.name} ({self.height}cm, {self.age} days)")


def create_plants() -> list[Plant]:
    """
    Create and return a list of predefined Plant instances.
    """
    plant_data = [
        ("Rose", 25, 30),
        ("Oak", 200, 365),
        ("Cactus", 5, 90),
        ("Sunflower", 80, 45),
        ("Fern", 15, 120),
    ]
    plants = []
    for name, height, age in plant_data:
        plant = Plant(name, height, age)
        plants.append(plant)
    return (plants)


def display_factory_output(plants: list[Plant]) -> None:
    """
    Display all created plants and the total count.
    """
    print("=== Plant Factory Output ===")
    for plant in plants:
        print(f"Created: {plant.get_info()}")
    print(f"Total plants created: {len(plants)}")


if __name__ == "__main__":
    plants = create_plants()
    display_factory_output(plants)
