class Plant:
    """
    Represents a plant with a name, height, and age.
    """
    def __init__(self, name: str, height: int, age: int) -> None:
        """
        Initialize a new Plant with basic attributes.
        """
        self.name = name
        self.height = height
        self.age = age


def display_garden(plants: list[Plant]) -> None:
    """
    Display all plants in the garden with their details.
    """
    print("=== Garden Plant Registry ===")
    for plant in plants:
        print(f"{plant.name}: {plant.height}cm, {plant.age} days old")


if __name__ == "__main__":
    rose = Plant("Rose", 25, 30)
    sunflower = Plant("Sunflower", 80, 45)
    cactus = Plant("Cactus", 15, 120)
    garden_plants = [rose, sunflower, cactus]
    display_garden(garden_plants)
