import time
from functools import wraps


def spell_timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Casting {func.__name__} ...")
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Spell completed in {round(end - start, 3)} seconds")
        return result
    return wrapper


def power_validator(min_power: int):
    def decorator(func):
        @wraps(func)
        def wrapper(self, power, *args, **kwargs):
            if power < min_power:
                return "Insufficient power for this spell"
            return func(self, power, *args, **kwargs)
        return wrapper
    return decorator


def retry_spell(max_attempts: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    print(
                        "Spell failed, retrying ... "
                        f"({attempt}/{max_attempts})"
                    )
            return f"Spell casting failed after {max_attempts} attempts"
        return wrapper
    return decorator


class MageGuild:

    @staticmethod
    def validate_mage_name(name: str) -> bool:
        return len(name) >= 3 and all(c.isalpha() or c.isspace() for c in name)

    @power_validator(10)
    def cast_spell(self, power: int, spell_name: str) -> str:
        return f"Successfully cast {spell_name} with {power} power"
