#!/usr/bin/env python3
import math


def create_position(x: int, y: int, z: int) -> tuple[int, int, int]:
    """Return a 3D coordinate tuple."""
    return (x, y, z)


def distance_3d(p1: tuple[int, int, int], p2: tuple[int, int, int]) -> float:
    """Compute Euclidean distance between two 3D points."""
    return math.sqrt(
        (p2[0] - p1[0]) ** 2 +
        (p2[1] - p1[1]) ** 2 +
        (p2[2] - p1[2]) ** 2
    )


def parse_coordinates(coord_str: str) -> tuple[int, int, int]:
    """Parse 'x,y,z' into a coordinate tuple."""
    parts = coord_str.split(",")
    if (len(parts) != 3):
        raise ValueError("Coordinate must have exactly 3 values")
    try:
        x = int(parts[0])
        y = int(parts[1])
        z = int(parts[2])
        return (x, y, z)
    except ValueError as err:
        raise err


def main() -> None:
    """Demonstrate 3D coordinate creation and parsing."""
    print("=== Game Coordinate System ===")
    pos = create_position(10, 20, 5)
    print(f"Position created: {pos}")
    origin = (0, 0, 0)
    dist = distance_3d(origin, pos)
    print(f"Distance between {origin} and {pos}: {dist:.2f}")
    valid_str = "3,4,0"
    print(f'Parsing coordinates: "{valid_str}"')
    parsed = parse_coordinates(valid_str)
    print(f"Parsed position: {parsed}")
    print(
        f"Distance between {origin} and {parsed}: "
        f"{distance_3d(origin, parsed)}"
    )
    invalid_str = "abc,def,ghi"
    print(f'Parsing invalid coordinates: "{invalid_str}"')
    try:
        parse_coordinates(invalid_str)
    except ValueError as e:
        print(f"Error parsing coordinates: {e}")
        print(f"Error details - Type: {type(e).__name__}, Args: {e.args}")
    print("Unpacking demonstration:")
    x, y, z = parsed
    print(f"Player at x={x}, y={y}, z={z}")
    print(f"Coordinates: X={x}, Y={y}, Z={z}")


if __name__ == "__main__":
    main()
