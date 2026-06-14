from __future__ import annotations
from ex3.FantasyCardFactory import FantasyCardFactory
from ex3.AggressiveStrategy import AggressiveStrategy
from ex3.GameEngine import GameEngine


def main() -> None:
    print("=== DataDeck Game Engine ===\n")
    factory = FantasyCardFactory()
    strategy = AggressiveStrategy()
    engine = GameEngine()
    engine.configure_engine(factory, strategy)
    print("Configuring Fantasy Card Game...\n")
    print(f"Factory: {factory.__class__.__name__}\n")
    print(f"Strategy: {strategy.get_strategy_name()}\n")
    print(f"Available types: {factory.get_supported_types()}\n")
    print("Simulating aggressive turn...\n")
    res = engine.simulate_turn()
    print(f"Turn execution:\n{res}\n")
    print("Game Report:\n")
    print(f"{engine.get_engine_status()}\n")


if __name__ == "__main__":
    main()
