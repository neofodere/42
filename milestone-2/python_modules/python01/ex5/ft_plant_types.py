class Plant:
    """
    Base plant class with common attributes.
    """
    def __init__(self, name: str, height: int, age: int) -> None:
        """
        Initialize a plant with name, height, and age.
        """
        self.name = name
        self.height = height
        self.age = age

    def get_info(self) -> str:
        """
        Return a formatted description of the plant.
        """
        return f"{self.name}: {self.height}cm, {self.age} days"


class Flower(Plant):
    """
    A flowering plant with a specific color.
    """
    def __init__(self, name: str, height: int, age: int, color: str) -> None:
        """
        Initialize a Flower with its color.
        """
        super().__init__(name, height, age)
        self.color = color

    def bloom(self) -> None:
        """
        Display a message indicating the flower is blooming.
        """
        print(f"{self.name} is blooming beautifully!")

    def get_info(self) -> str:
        """
        Return a formatted description of the flower.
        """
        return (
            f"{self.name} (Flower): {self.height}cm, "
            f"{self.age} days, {self.color} color"
        )


class Tree(Plant):
    """
    A tree with a trunk diameter and shade production ability.
    """
    def __init__(
        self, name: str, height: int, age: int, trunk_diameter: int
    ) -> None:
        """
        Initialize a Tree with its trunk diameter.
        """
        super().__init__(name, height, age)
        self.trunk_diameter = trunk_diameter

    def produce_shade(self) -> None:
        """
        Calculate and display the amount of shade produced by the tree.
        """
        shade = self.trunk_diameter * 1.56
        print(f"{self.name} provides {int(shade)} square meters of shade")

    def get_info(self) -> str:
        """
        Return a formatted description of the tree.
        """
        return (
            f"{self.name} (Tree): {self.height}cm, {self.age} days, "
            f"{self.trunk_diameter}cm diameter"
        )


class Vegetable(Plant):
    """
    A vegetable plant with harvest season and nutritional value.
    """
    def __init__(
        self, name: str, height: int, age: int,
        harvest_season: str, nutritional_value: str
    ) -> None:
        """
        Initialize a Vegetable with harvest season and nutrition info.
        """
        super().__init__(name, height, age)
        self.harvest_season = harvest_season
        self.nutritional_value = nutritional_value

    def get_info(self) -> str:
        """
        Return a formatted description of the vegetable.
        """
        return (
            f"{self.name} (Vegetable): {self.height}cm, {self.age} days, "
            f"{self.harvest_season} harvest"
        )

    def show_nutrition(self) -> None:
        """
        Display the vegetable's nutritional value.
        """
        print(f"{self.name} is rich in {self.nutritional_value}")


if __name__ == "__main__":
    print("=== Garden Plant Types ===")
    rose = Flower("Rose", 25, 30, "red")
    tulip = Flower("Tulip", 20, 25, "yellow")
    oak = Tree("Oak", 500, 1825, 50)
    pine = Tree("Pine", 600, 2000, 40)
    tomato = Vegetable("Tomato", 80, 90, "summer", "vitamin C")
    carrot = Vegetable("Carrot", 40, 70, "autumn", "beta-carotene")
    plants = [rose, tulip, oak, pine, tomato, carrot]
    for plant in plants:
        print(plant.get_info())
        if isinstance(plant, Flower):
            plant.bloom()
        elif isinstance(plant, Tree):
            plant.produce_shade()
        elif isinstance(plant, Vegetable):
            plant.show_nutrition()
