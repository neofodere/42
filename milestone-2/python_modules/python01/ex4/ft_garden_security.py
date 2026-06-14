class SecurePlant:
    """
    A plant model that protects its data.
    """
    def __init__(self, name: str, height: int, age: int) -> None:
        """
        Initialize a SecurePlant and validate its initial height and age.
        """
        self.name = name
        self._height = 0
        self._age = 0
        self.set_height(height)
        self.set_age(age)

    def set_height(self, new_height: int) -> None:
        """
        Safely update the plant's height, rejecting negative values.
        """
        if (new_height < 0):
            print(
                f"Invalid operation attempted: height {new_height}cm "
                "[REJECTED]"
            )
            print("Security: Negative height rejected")
        else:
            self._height = new_height
            print(f"Height updated: {self._height}cm [OK]")

    def set_age(self, new_age: int) -> None:
        """
        Safely update the plant's age, rejecting negative values.
        """
        if (new_age < 0):
            print(
                f"Invalid operation attempted: age {new_age} days "
                "[REJECTED]"
            )
            print("Security: Negative age rejected")
        else:
            self._age = new_age
            print(f"Age updated: {self._age} days [OK]")

    def get_height(self) -> int:
        """
        Return the plant's current height.
        """
        return (self._height)

    def get_age(self) -> int:
        """
        Return the plant's current age.
        """
        return (self._age)

    def get_info(self) -> str:
        """
        Return a formatted string with the plant's secure data.
        """
        return (f"{self.name} ({self._height}cm, {self._age} days)")


if __name__ == "__main__":
    print("=== Garden Security System ===")
    plant = SecurePlant("Rose", 25, 30)
    print(f"Plant created: {plant.name}")
    plant.set_height(25)
    plant.set_age(30)
    plant.set_height(-5)
    print(f"Current plant: {plant.get_info()}")
