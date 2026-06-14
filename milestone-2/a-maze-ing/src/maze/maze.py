from typing import List, Set
from maze.config_parser import MazeConfig
import random
from enum import IntEnum


SHAPE_4 = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4)]
# Relative (x, y) coordinates for a 3x5 "2"
SHAPE_2 = [(0, 0), (1, 0), (2, 0), (2, 1), (0, 2), (1, 2), (2, 2), (0, 3),
           (0, 4), (1, 4), (2, 4)]


class Direction(IntEnum):
    N = 1  # 0001
    E = 2  # 0010
    S = 4  # 0100
    W = 8  # 1000


OPPOSITES = {
    Direction.N: Direction.S,
    Direction.S: Direction.N,
    Direction.E: Direction.W,
    Direction.W: Direction.E,
}

# Directional math to find neighbors: (dx, dy)
# Assuming grid[y][x], so North is y-1, South is y+1
DIR_MATH = {
    Direction.N: (0, -1),
    Direction.E: (1, 0),
    Direction.S: (0, 1),
    Direction.W: (-1, 0)
}


class Maze:
    def __init__(self, config: MazeConfig) -> None:
        self.config = config
        self.w = config.width
        self.h = config.height
        self.grid: List[List[int]] = [
            [0xF for _ in range(self.w)] for _ in range(self.h)]
        self.pattern_cells: Set[int] = set()

    def remove_wall(self, x: int, y: int, direction: int) -> None:
        self.grid[y][x] &= ~direction
        dx, dy = DIR_MATH[direction]
        nx, ny = x + dx, y + dy
        if 0 <= nx < self.w and 0 <= ny < self.h:
            opp_dir = OPPOSITES[direction]
            self.grid[ny][nx] &= ~opp_dir

    def is_3x3_open_at(self, sx: int, sy: int) -> bool:
        """
        Checks if the 3x3 block starting at (sx, sy)
        has NO internal walls.
        """
        # Check if the 3x3 block goes out of the maze bounds
        if sx < 0 or sy < 0 or sx + 2 >= self.w or sy + 2 >= self.h:
            return False

        # 1. Check all internal East-West walls within this 3x3
        for x in range(sx, sx + 2):
            for y in range(sy, sy + 3):
                if self.grid[y][x] & Direction.E:  # If an East wall exists
                    return False

        # 2. Check all internal North-South walls within this 3x3
        for x in range(sx, sx + 3):
            for y in range(sy, sy + 2):
                if self.grid[y][x] & Direction.S:  # If a South wall exists
                    return False

        return True  # It is a 3x3 open area!


def generate_dfs(self) -> None:
    """
    Generates a perfect maze using an iterative Depth-First Search.
    Every cell will be visited exactly once, ensuring full
    connectivity and no loops.
    """
    # Create a grid to track which cells we've visited
    frozen_cells = self.get_42_pattern()

    # 2. Initialize visited grid:
    # Mark 'True' if the cell is in frozen_cells, 'False' otherwise.
    visited = [
        [False for _ in range(self._width)] for _ in range(self._height)
        ]
    for y in range(self._height):
        for x in range(self._width):
            if (x, y) in frozen_cells:
                visited[y][x] = True
    # Start digging from the entry point
    start_x, start_y = self.entry
    # The stack keeps track of our current path so we can backtrack
    stack = [(start_x, start_y)]
    visited[start_y][start_x] = True

    while stack:
        # Look at the cell we are currently in (the top of the stack)
        cx, cy = stack[-1]

        # 1. Find all neighbors we haven't visited yet
        unvisited_neighbors = []
        for direction, (dx, dy) in DIR_MATH.items():
            nx, ny = cx + dx, cy + dy

            # Check if neighbor is inside the bounds AND unvisited
            if (0 <= nx < self._width and 0 <= ny < self._height and not
                    visited[ny][nx]):
                unvisited_neighbors.append((direction, nx, ny))

        if unvisited_neighbors:
            # 2. Pick a random unvisited neighbor
            direction, nx, ny = random.choice(unvisited_neighbors)

            # 3. Knock down the wall between the current cell and
            # the chosen neighbor
            self.remove_wall(cx, cy, direction)

            # 4. Mark the neighbor as visited and step into it
            visited[ny][nx] = True
            stack.append((nx, ny))
        else:
            # 5. We have no unvisited neighbors. Backtrack by popping.
            stack.pop()
    if not self._perfect:
        self.make_imperfect()
