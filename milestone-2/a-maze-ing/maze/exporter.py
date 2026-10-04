from maze.maze import Maze
from maze.solver import find_shortest_path, get_solution_string


def save_to_file(maze: Maze, filename: str) -> None:
    path = find_shortest_path(maze)
    solution_str = get_solution_string(path)

    try:
        with open(filename, 'w') as f:
            for row in maze.grid:
                hex_row = "".join([f"{cell:X}" for cell in row])
                f.write(hex_row + "\n")
            f.write("\n")
            f.write(f"{maze.config.entry[0]},{maze.config.entry[1]}\n")
            f.write(f"{maze.config.exit[0]},{maze.config.exit[1]}\n")
            f.write(solution_str + "\n")
    except Exception as e:
        raise OSError(f"Could not save file '{filename}': {e}")
