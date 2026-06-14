from alchemy.transmutation import (
    lead_to_gold,
    stone_to_gem,
    philosophers_stone,
    elixir_of_life,
)
import alchemy.transmutation as trans

print("=== Pathway Debate Mastery ===\n")
print("Testing Absolute Imports (from basic.py):")
print("lead_to_gold():", lead_to_gold())
print("stone_to_gem():", stone_to_gem())
print("\nTesting Relative Imports (from advanced.py):")
print("philosophers_stone():", philosophers_stone())
print("elixir_of_life():", elixir_of_life())
print("\nTesting Package Access:")
print("alchemy.transmutation.lead_to_gold():", trans.lead_to_gold())
print(
    "alchemy.transmutation.philosophers_stone():", trans.philosophers_stone()
)
print("\nBoth pathways work! Absolute: clear, Relative: concise")
