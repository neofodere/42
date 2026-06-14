from typing import Tuple, List, Set, Deque
from collections import deque
from maze.maze import Maze


def find_shortest_path(maze: Maze) -> List[Tuple[int, int]]:
    """_summary_

    Args:
        maze (Maze): _description_

    Returns:
        List[Tuple[int, int]]: _description_
    """
    start = maze.config.entry
    end = maze.config.exit
    queue: Deque[
        Tuple[Tuple[int, int], List[Tuple[int, int]]]
    ] = deque([(start, [start])])
    visited: Set[Tuple[int, int]] = {start}
    directions = [(0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8)]

    while queue:
        (cx, cy), path = queue.popleft()
        if (cx, cy) == end:
            return path
        cell_walls = maze.grid[cy][cx]

        for dx, dy, bit in directions:
            nx, ny = cx + dx, cy + dy
            if not (cell_walls & bit):
                if (0 <= nx < maze.w and 0 <= ny < maze.h
                        and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
    return []


def get_solution_string(path: List[Tuple[int, int]]) -> str:
    """_summary_

    Args:
        path (List[Tuple[int, int]]): _description_

    Returns:
        str: _description_
    """
    if not path or len(path) < 2:
        return ""
    solution = ""
    for i in range(len(path) - 1):
        curr_x, curr_y = path[i]
        next_x, next_y = path[i+1]
        if next_y < curr_y:
            solution += "N"
        elif next_y > curr_y:
            solution += "S"
        elif next_x > curr_x:
            solution += "E"
        elif next_x < curr_x:
            solution += "W"
    return solution
