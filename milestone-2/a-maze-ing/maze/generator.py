"""
Standalone Maze Generator Module.
This module provides the MazeGenerator class, which generates perfect and
imperfect mazes, injects the mandatory '42' pattern, and provides a solution.

Usage Example:
    from generator import MazeGenerator

    # Instantiate the generator
    generator = MazeGenerator(width=20, height=15, entry=(0, 0),
                                exit=(19, 14), perfect=False, seed=42)

    # Generate the maze
    generator.generate()

    # Access the maze structure (2D list of hex values)
    grid = generator.get_maze()

    # Access the solution (List of (x, y) coordinates)
    solution = generator.get_solution()
"""

import random
from collections import deque
from typing import List, Tuple, Set, Optional

# Constants for bitwise wall representation
N, E, S, W = 1, 2, 4, 8
OPPOSITE = {N: S, E: W, S: N, W: E}
DIR_MATH = {N: (0, -1), E: (1, 0), S: (0, 1), W: (-1, 0)}

# Shapes for the '42' pattern
SHAPE_4 = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4)]
SHAPE_2 = [(0, 0), (1, 0), (2, 0), (2, 1), (0, 2), (1, 2), (2, 2),
           (0, 3), (0, 4), (1, 4), (2, 4)]


class MazeGenerator:
    """
    A standalone class to generate mazes.
    It encapsulates the grid state, the generation logic (DFS),
    and the solver (BFS).
    """

    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], perfect: bool = True,
                 seed: Optional[int] = None):
        """
        Initializes the MazeGenerator with custom parameters.

        Args:
            width (int): The width of the maze.
            height (int): The height of the maze.
            entry (Tuple[int, int]): The (x, y) coordinates for the start.
            exit (Tuple[int, int]): The (x, y) coordinates for the end.
            perfect (bool): True for a single-path maze, False to allow loops.
            seed (int, optional): Random seed for reproducibility.
        """
        self.w = width
        self.h = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect

        # Initialize grid with all walls closed (0xF = 15)
        self.grid: List[List[int]] = [
            [0xF for _ in range(self.w)] for _ in range(self.h)]
        self.pattern_cells: Set[Tuple[int, int]] = set()
        """ ANADIR CUSTOM ARGS#####################################################################"""

        if seed is not None:
            random.seed(seed)

    def generate(self) -> None:
        """Executes the full generation pipeline."""
        self.grid = [[0xF for _ in range(self.w)] for _ in range(self.h)]
        self._calculate_42_pattern()
        self._generate_dfs()
        self._inject_42_pattern()

        if not self.perfect:
            self._make_imperfect()

    def get_maze(self) -> List[List[int]]:
        """
        Returns the generated maze structure.

        Returns:
            List[List[int]]: A 2D array where each cell is an integer (0-15)
                             representing its walls.
        """
        return self.grid

    def get_solution(self) -> List[Tuple[int, int]]:
        """
        Finds and returns the shortest path from entry to exit using BFS.

        Returns:
            List[Tuple[int, int]]: A list of (x, y)
            coordinates forming the path.
        """
        queue = deque([(self.entry, [self.entry])])
        visited = {self.entry}
        directions = [(0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8)]

        while queue:
            (cx, cy), path = queue.popleft()
            if (cx, cy) == self.exit:
                return path

            cell_walls = self.grid[cy][cx]
            for dx, dy, bit in directions:
                nx, ny = cx + dx, cy + dy
                # Check if there is NO wall in that direction
                if not (cell_walls & bit):
                    if (0 <= nx < self.w and 0 <= ny < self.h and (nx, ny)
                            not in visited):
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + [(nx, ny)]))
        return []

    def _remove_wall(self, x: int, y: int, direction: int) -> None:
        """Removes a wall between the given cell and its neighbor."""
        self.grid[y][x] &= ~direction
        dx, dy = DIR_MATH[direction]
        nx, ny = x + dx, y + dy
        if 0 <= nx < self.w and 0 <= ny < self.h:
            opp_dir = OPPOSITE[direction]
            self.grid[ny][nx] &= ~opp_dir

    def _calculate_42_pattern(self) -> None:
        """Calculates the coordinates for the '42'
            pattern to protect them during generation."""
        required_w, required_h = 7, 5
        if self.w < required_w + 2 or self.h < required_h + 2:
            self.pattern_cells = set()
            return

        start_x = (self.w - required_w) // 2
        start_y = (self.h - required_h) // 2

        protected_cells = set()
        for dx, dy in SHAPE_4:
            protected_cells.add((start_x + dx, start_y + dy))
        for dx, dy in SHAPE_2:
            protected_cells.add((start_x + dx + 4, start_y + dy))

        if self.entry in protected_cells or self.exit in protected_cells:
            self.pattern_cells = set()
        else:
            self.pattern_cells = protected_cells

    def _generate_dfs(self) -> None:
        """Core DFS generation algorithm ensuring a perfect spanning tree."""
        visited = [[False for _ in range(self.w)] for _ in range(self.h)]
        for y in range(self.h):
            for x in range(self.w):
                if (x, y) in self.pattern_cells:
                    visited[y][x] = True

        start_x, start_y = self.entry
        stack = [(start_x, start_y)]
        visited[start_y][start_x] = True

        while stack:
            cx, cy = stack[-1]
            unvisited_neighbors = []
            for direction, (dx, dy) in DIR_MATH.items():
                nx, ny = cx + dx, cy + dy
                if (0 <= nx < self.w and 0 <= ny < self.h
                        and not visited[ny][nx]):
                    unvisited_neighbors.append((direction, nx, ny))

            if unvisited_neighbors:
                direction, nx, ny = random.choice(unvisited_neighbors)
                self._remove_wall(cx, cy, direction)
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

    def _inject_42_pattern(self) -> None:
        """Forces the '42' pattern cells to be fully closed walls (0xF)."""
        for x, y in self.pattern_cells:
            self.grid[y][x] = 0xF

    def _is_3x3_open_at(self, sx: int, sy: int) -> bool:
        """Checks if a 3x3 block has internal walls.
            Prevents large open areas."""
        if sx < 0 or sy < 0 or sx + 2 >= self.w or sy + 2 >= self.h:
            return False
        for x in range(sx, sx + 2):
            for y in range(sy, sy + 3):
                if self.grid[y][x] & E:
                    return False
        for x in range(sx, sx + 3):
            for y in range(sy, sy + 2):
                if self.grid[y][x] & S:
                    return False
        return True

    def _make_imperfect(self) -> None:
        """Randomly removes extra walls to create loops, avoiding 3x3 areas."""
        candidates = []
        for y in range(self.h):
            for x in range(self.w):
                if (x, y) in self.pattern_cells:
                    continue
                if (y + 1 < self.h and (x, y + 1) not in self.pattern_cells
                        and (self.grid[y][x] & 4)):
                    candidates.append((x, y, 4, x, y + 1, 1))
                if (x + 1 < self.w and (x + 1, y) not in self.pattern_cells
                        and (self.grid[y][x] & 2)):
                    candidates.append((x, y, 2, x + 1, y, 8))

        random.shuffle(candidates)
        walls_to_break = (self.w * self.h) // 10
        broken_count = 0

        def creates_large_open_area(mx: int, my: int) -> bool:
            for cy in range(my - 2, my + 2):
                for cx in range(mx - 2, mx + 2):
                    if self._is_3x3_open_at(cx, cy):
                        return True
            return False

        for x, y, dir_out, nx, ny, dir_in in candidates:
            if broken_count >= walls_to_break:
                break
            # Break wall temporarily
            self.grid[y][x] &= ~dir_out
            self.grid[ny][nx] &= ~dir_in

            if creates_large_open_area(x, y):
                # Revert if it creates a 3x3 open area
                self.grid[y][x] |= dir_out
                self.grid[ny][nx] |= dir_in
            else:
                broken_count += 1
