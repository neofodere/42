def mage_counter():
    count = 0

    def counter():
        nonlocal count
        count += 1
        return count
    return counter


def spell_accumulator(initial_power: int):
    total = initial_power

    def accumulator(amount: int):
        nonlocal total
        total += amount
        return total
    return accumulator


def enchantment_factory(enchantment_type: str):
    return lambda item: f"{enchantment_type} {item}"


def memory_vault():
    storage = {}

    def store(key, value):
        storage[key] = value

    def recall(key):
        return storage.get(key, "Memory not found")
    return {"store": store, "recall": recall}
