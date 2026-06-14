#!/usr/bin/env python3
import time


def event_stream(n: int):
    """Yield n simulated game events."""
    players = ["alice", "bob", "charlie"]
    actions = ["killed monster", "found treasure", "leveled up"]
    levels = [5, 12, 8]
    for pos in range(1, n + 1):
        idx = (pos - 1) % 3
        yield (pos, players[idx], levels[idx], actions[idx])


def fibonacci_stream():
    """Yield infinite Fibonacci numbers."""
    a, b = 0, 1
    while (True):
        yield a
        a, b = b, a + b


def prime_stream():
    """Yield infinite prime numbers."""
    num = 2
    while (True):
        if all(num % p != 0 for p in range(2, int(num ** 0.5) + 1)):
            yield num
        num += 1


def main() -> None:
    """Demonstrate streaming data processing with generators."""
    print("=== Game Data Stream Processor ===")
    total_events = 1000
    print(f"Processing {total_events} game events...")
    stream = event_stream(total_events)
    count = 0
    high_level = 0
    treasure = 0
    level_up = 0
    start = time.time()
    for event_id, player, level, action in stream:
        count += 1
        if count <= 3:
            print(
                f"Event {event_id}: Player {player} (level {level}) {action}"
            )
        if level >= 10:
            high_level += 1
        if action == "found treasure":
            treasure += 1
        if action == "leveled up":
            level_up += 1
    end = time.time()
    print("=== Stream Analytics ===")
    print(f"Total events processed: {count}")
    print(f"High-level players (10+): {high_level}")
    print(f"Treasure events: {treasure}")
    print(f"Level-up events: {level_up}")
    print("Memory usage: Constant (streaming)")
    print(f"Processing time: {end - start:.3f} seconds")
    print("=== Generator Demonstration ===")
    fib = fibonacci_stream()
    fib_values = [next(fib) for _ in range(10)]
    print(f"Fibonacci sequence (first 10): {', '.join(map(str, fib_values))}")
    primes = prime_stream()
    prime_values = [next(primes) for _ in range(5)]
    print(f"Prime numbers (first 5): {', '.join(map(str, prime_values))}")


if __name__ == "__main__":
    main()
