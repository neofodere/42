class Plant:
    """
    Basic plant with a name and height.
    """
    def __init__(self, name: str, height: int) -> None:
        """
        Initialize a plant with name and height.
        """
        self.name = name
        self.height = height

    def grow(self) -> None:
        """
        Increase the plant's height by 1cm.
        """
        self.height += 1
        print(f"{self.name} grew 1cm")

    def get_info(self) -> str:
        """
        Return a formatted description of the plant.
        """
        return (f"{self.name}: {self.height}cm")


class FloweringPlant(Plant):
    """
    A plant capable of producing flowers with a specific color.
    """
    def __init__(self, name: str, height: int, color: str) -> None:
        """
        Initialize a flowering plant with its color.
        """
        super().__init__(name, height)
        self.color = color

    def get_info(self) -> str:
        """
        Return a formatted description of the flowering plant.
        """
        return (
            f"{self.name}: {self.height}cm, {self.color} flowers "
            "(blooming)"
        )


class PrizeFlower(FloweringPlant):
    """
    A special flowering plant that earns prize points.
    """
    def __init__(self, name: str, height: int, color: str, points: int):
        """
        Initialize a prize flower with its point value.
        """
        super().__init__(name, height, color)
        self.points = points

    def get_info(self) -> str:
        """
        Return a formatted description of the prize flower.
        """
        return (
            f"{self.name}: {self.height}cm, {self.color} flowers "
            f"(blooming), Prize points: {self.points}"
        )


class GardenManager:
    """
    Manage a garden containing multiple plants.
    """
    class GardenStats:
        """
        Utility class providing garden statistics.
        """
        @staticmethod
        def total_growth(plants: list) -> int:
            """
            Return the total height of all plants.
            """
            return (sum(p.height for p in plants))

        @staticmethod
        def count_types(plants: list) -> tuple:
            """
            Count regular, flowering, and prize plants.
            """
            regular = 0
            flowering = 0
            prize = 0
            for p in plants:
                if isinstance(p, PrizeFlower):
                    prize += 1
                elif isinstance(p, FloweringPlant):
                    flowering += 1
                else:
                    regular += 1
            return regular, flowering, prize

        @staticmethod
        def validate_height(height: int) -> bool:
            """
            Validate that a height value is non-negative.
            """
            return height >= 0

    gardens_managed = 0

    def __init__(self, owner: str) -> None:
        """
        Initialize a garden manager for a specific owner.
        """
        self.owner = owner
        self.plants = []
        GardenManager.gardens_managed += 1

    def add_plant(self, plant: Plant) -> None:
        """
        Add a plant to the manager's garden.
        """
        self.plants.append(plant)
        print(f"Added {plant.name} to {self.owner}'s garden")

    def help_garden_grow(self) -> None:
        """
        Make all plants in the garden grow.
        """
        print(f"{self.owner} is helping all plants grow...")
        for plant in self.plants:
            plant.grow()

    def report(self) -> None:
        """
        Display a detailed report of the garden's status.
        """
        print(f"=== {self.owner}'s Garden Report ===")
        print("Plants in garden:")
        for p in self.plants:
            print(f"- {p.get_info()}")
        total_growth = GardenManager.GardenStats.total_growth(self.plants)
        regular, flowering, prize = GardenManager.GardenStats.count_types(
            self.plants
        )

        print(
            f"Plants added: {len(self.plants)}, Total growth: {total_growth}cm"
        )
        print(
            f"Plant types: {regular} regular, {flowering} flowering, "
            f"{prize} prize flowers"
        )

    @classmethod
    def create_garden_network(cls, owners: list) -> list:
        """
        Create multiple garden managers from a list of owners.
        """
        return [cls(owner) for owner in owners]

    @staticmethod
    def compute_score(plant: Plant) -> int:
        """
        Compute a score for a plant based on height and prize points.
        """
        base = plant.height * 2
        if isinstance(plant, PrizeFlower):
            base += plant.points * 5
        return (base)


if __name__ == "__main__":
    print("=== Garden Management System Demo ===")
    alice, bob = GardenManager.create_garden_network(["Alice", "Bob"])
    oak = Plant("Oak Tree", 100)
    rose = FloweringPlant("Rose", 25, "red")
    sunflower = PrizeFlower("Sunflower", 50, "yellow", 10)
    alice.add_plant(oak)
    alice.add_plant(rose)
    alice.add_plant(sunflower)
    alice.help_garden_grow()
    alice.report()
    print(
        "Height validation test:",
        GardenManager.GardenStats.validate_height(10)
    )
    alice_score = sum(GardenManager.compute_score(p) for p in alice.plants)
    bob_score = 92
    print(f"Garden scores - Alice: {alice_score}, Bob: {bob_score}")
    print(f"Total gardens managed: {GardenManager.gardens_managed}")
