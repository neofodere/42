from functools import reduce, partial, lru_cache, singledispatch
import operator


def spell_reducer(spells, operation: str):
    ops = {
        "add": operator.add,
        "multiply": operator.mul,
        "max": max,
        "min": min
    }
    if operation in ("max", "min"):
        return ops[operation](spells)
    return reduce(ops[operation], spells)


def partial_enchanter(base_enchantment):
    return {
        "fire_enchant": partial(base_enchantment, 50, "fire"),
        "ice_enchant": partial(base_enchantment, 50, "ice"),
        "lightning_enchant": partial(base_enchantment, 50, "lightning"),
    }


@lru_cache(maxsize=None)
def memoized_fibonacci(n: int) -> int:
    if n < 2:
        return n
    return memoized_fibonacci(n - 1) + memoized_fibonacci(n - 2)


def spell_dispatcher():
    @singledispatch
    def cast(arg):
        return "Unknown spell type"

    @cast.register(int)
    def _(arg):
        return f"Damage spell hits for {arg} power"

    @cast.register(str)
    def _(arg):
        return f"Enchantment applied: {arg}"

    @cast.register(list)
    def _(arg):
        return [cast(a) for a in arg]
    return cast
