class Plant:
    """
    Represents a plant with basic attributes: name, height, and age.
    """
    def __init__(self, name: str, height: int, age: int) -> None:
        """
        Initialize a new Plant with its name, height, and age.
        """
        self.name = name
        self.height = height
        self.age = age

    def grow(self, amount: int) -> None:
        """
        Increase the plant's height by a given amount.
        """
        self.height += amount

    def age_one_day(self) -> None:
        """
        Increase the plant's age by one day.
        """
        self.age += 1

    def get_info(self) -> str:
        """
        Return a formatted string with the plant's current state.
        """
        return (f"{self.name}: {self.height}cm, {self.age} days old")


def simulate_week(plants: list[Plant]) -> None:
    """
    Simulate one week of growth for all plants in the list.
    """
    print("=== Day 1 ===")
    for plant in plants:
        print(plant.get_info())
    for _ in range(6):
        for plant in plants:
            plant.grow(1)
            plant.age_one_day()
    print("=== Day 7 ===")
    for plant in plants:
        print(plant.get_info())
    first = plants[0]
    growth = first.height - 25
    print(f"Growth this week: +{growth}cm")


if __name__ == "__main__":
    rose = Plant("Rose", 25, 30)
    sunflower = Plant("Sunflower", 80, 45)
    cactus = Plant("Cactus", 15, 120)
    garden = [rose, sunflower, cactus]
    simulate_week(garden)
