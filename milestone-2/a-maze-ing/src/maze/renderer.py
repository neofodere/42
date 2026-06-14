import shutil
import sys
from typing import List, Tuple, Any, Dict
from maze.maze import Maze
from maze.solver import find_shortest_path
from maze.generator import MazeGenerator
from maze import exporter

try:
    from mlx import Mlx
except ModuleNotFoundError:
    print("Missing MLX import")


# ==========================================
# RENDERIZADO ASCII (TERMINAL)
# ==========================================

def _build_ascii_grid(maze: Maze) -> List[List[int]]:
    """
    Builds the expanded 2D grid required for ASCII representation.
    """
    vis_w: int = maze.w * 2 + 1
    vis_h: int = maze.h * 2 + 1
    vis: List[List[int]] = [
        [1 for _ in range(vis_w)] for _ in range(vis_h)]

    n_bit, e_bit, s_bit, w_bit = 1, 2, 4, 8

    # Carve paths and break walls
    for y in range(maze.h):
        for x in range(maze.w):
            vx: int = x * 2 + 1
            vy: int = y * 2 + 1
            vis[vy][vx] = 0  # Cell center

            cell_val: int = maze.grid[y][x]
            if not (cell_val & n_bit):
                vis[vy - 1][vx] = 0
            if not (cell_val & s_bit):
                vis[vy + 1][vx] = 0
            if not (cell_val & e_bit):
                vis[vy][vx + 1] = 0
            if not (cell_val & w_bit):
                vis[vy][vx - 1] = 0

    # Mark Entry (2) and Exit (3)
    ex, ey = maze.config.entry
    vis[ey * 2 + 1][ex * 2 + 1] = 2

    xx, xy = maze.config.exit
    vis[xy * 2 + 1][xx * 2 + 1] = 3

    return vis


def print_ascii(maze: Maze, show_path: bool = False,
                color_idx: int = 0) -> None:
    """Prints the maze in the terminal using block characters and colors"""
    vis: List[List[int]] = _build_ascii_grid(maze)
    vis_w: int = maze.w * 2 + 1

    # Comprobar si cabe en la terminal
    term_size = shutil.get_terminal_size((80, 20))
    if vis_w > term_size.columns:
        print("\n\033[93m[WARNING] The maze is too "
              "wide for your terminal.\033[0m")
        return

    # 1. Inyectar el patrón 42 (ID 5)
    if hasattr(maze, 'pattern_cells') and maze.pattern_cells:
        for x, y in maze.pattern_cells:
            vx: int = x * 2 + 1
            vy: int = y * 2 + 1
            if vis[vy][vx] not in (2, 3):
                vis[vy][vx] = 5
            if ((x + 1, y) in maze.pattern_cells and
                    vis[vy][vx + 1] not in (2, 3)):
                vis[vy][vx + 1] = 5
            if ((x, y + 1) in maze.pattern_cells and
                    vis[vy + 1][vx] not in (2, 3)):
                vis[vy + 1][vx] = 5

    # 2. Inyectar el camino azul (ID 4)
    if show_path:
        # Aquí usamos el solver externo
        path: List[Tuple[int, int]] = find_shortest_path(maze)
        for i in range(len(path)):
            x, y = path[i]
            vx, vy = x * 2 + 1, y * 2 + 1
            if vis[vy][vx] not in (2, 3):
                vis[vy][vx] = 4
            if i < len(path) - 1:
                nx, ny = path[i + 1]
                cvx, cvy = ((vx + (nx * 2 + 1)) // 2, (vy + (ny * 2 + 1)) // 2)
                if vis[cvy][cvx] not in (2, 3):
                    vis[cvy][cvx] = 4

    # --- Paleta de colores para las paredes (GROSOR 1) ---
    wall_palettes = [
        "██",                  # 0: Blanco/Gris por defecto
        "\033[38;5;208m██\033[0m",   # 1: Orange
        "\033[35m██\033[0m",   # 2: Magenta
        "\033[33m██\033[0m"    # 3: Amarillo
    ]
    current_wall_color = wall_palettes[color_idx % len(wall_palettes)]

    char_map: Dict[int, str] = {
        1: current_wall_color,
        0: "  ",
        2: "\033[42m  \033[0m",
        3: "\033[41m  \033[0m",
        4: "\033[44m  \033[0m",
        5: "\033[46m  \033[0m"
    }

    for row in vis:
        line: str = "".join([char_map.get(cell, " ") for cell in row])
        print(line)


def handle_ascii_interactive(maze: Maze) -> None:
    """Handles the interactive CLI loop for ASCII mode."""
    show_path: bool = False
    color_idx: int = 0

    while True:
        print_ascii(maze, show_path=show_path, color_idx=color_idx)

        print("\n=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")

        opcion = input("Choice? (1-4) ").strip()

        if opcion == '1':
            # Instanciamos el nuevo generador independiente
            gen = MazeGenerator(
                width=maze.config.width,
                height=maze.config.height,
                entry=maze.config.entry,
                exit=maze.config.exit,
                perfect=maze.config.perfect,
                seed=maze.config.seed
            )
            gen.generate()

            # Actualizamos la entidad Maze actual
            maze.grid = gen.get_maze()
            maze.pattern_cells = gen.pattern_cells

            # Exportamos usando el nuevo exportador
            exporter.save_to_file(maze, maze.config.output_file)
            if maze.config.verbose:
                print(f"[*] Maze re-generated and saved to"
                      f"{maze.config.output_file}")

        elif opcion == '2':
            show_path = not show_path
        elif opcion == '3':
            color_idx = (color_idx + 1) % 4
            if maze.config.verbose:
                print("\n[*] Rotating ASCII wall colors...")
        elif opcion == '4' or opcion.lower() == 'q':
            if maze.config.verbose:
                print("\n[*] Closing visualizer ASCII...")
            break
        else:
            print("\n[ERROR] Invalid option.")

## MLX

class MazeVisualizer:
    def __init__(self, maze: 'Maze',
                 title: str = "A-Maze-Ing Visualizer") -> None:
        if 'Mlx' not in globals():
            print("[ERROR] MLX is not installed. Please run: make install")
            sys.exit(1)

        self.maze = maze
        self.app = Mlx()
        self.mlx_ptr = self.app.mlx_init()

        self.vis_w = maze.w * 2 + 1
        self.vis_h = maze.h * 2 + 1

        base_scale = min(1000 // self.vis_w, 800 // self.vis_h)
        if base_scale < 2:
            base_scale = 2

        self.cell_size = base_scale
        self.wall_size = max(1, base_scale // 3)

        self.win_w = maze.w * self.cell_size + (maze.w + 1) * self.wall_size
        maze_pixel_h = maze.h * self.cell_size + (maze.h + 1) * self.wall_size

        self.menu_height = 60
        self.win_h = maze_pixel_h + self.menu_height

        self.win_ptr = self.app.mlx_new_window(self.mlx_ptr, self.win_w,
                                               self.win_h, title)
        self.img_ptr = self.app.mlx_new_image(self.mlx_ptr, self.win_w,
                                              self.win_h)
        raw_data = self.app.mlx_get_data_addr(self.img_ptr)
        self.pixel_mem = raw_data[0]
        self.size_line = raw_data[2]

        self.drawn_flag = {"ready": False}
        self.show_path = False

        self.wall_palettes = [
            b'\x50\x3E\x2C\xFF',  # 0: Dark Slate Blue
            b'\x13\x45\x8B\xFF',  # 1: Brown
            b'\x4A\x4A\x4A\xFF',  # 2: Dark Gray
            b'\x22\x8B\x22\xFF'   # 3: Forest Green
        ]
        self.color_idx = 0
        self.setup_colors()

    def setup_colors(self) -> None:
        self.C_WALL = self.wall_palettes[self.color_idx]
        self.C_PATH = b'\x00\x00\x00\xFF'  # Black
        self.C_ENTRY = b'\xFF\x60\xAE\xFF'  # Pink
        self.C_EXIT = b'\x3C\x4C\xE7\xFF'  # Red
        self.C_SOL = b'\xED\x95\x64\xFF'  # Cornflower Blue
        self.C_PATTERN = self.wall_palettes[self.color_idx]

    def _get_coord(self, v: int) -> tuple[int, int]:
        count_cells = v // 2
        if v % 2 == 0:
            start = count_cells * self.cell_size + count_cells * self.wall_size
            size = self.wall_size
        else:
            start = (
                (count_cells + 1) * self.wall_size +
                count_cells * self.cell_size)
            size = self.cell_size
        return start, size

    def draw_block(self, vx: int, vy: int, color: bytes) -> None:
        px_start, pw = self._get_coord(vx)
        py_start, ph = self._get_coord(vy)
        row_bytes = color * pw
        for j in range(ph):
            py = py_start + j
            mem_start = py * self.size_line + px_start * 4
            mem_end = mem_start + len(row_bytes)
            self.pixel_mem[mem_start:mem_end] = row_bytes

    def _clear_background(self) -> None:
        black_row: bytes = b'\x00\x00\x00\xFF' * self.win_w
        for y in range(self.win_h):
            start: int = y * self.size_line
            self.pixel_mem[start: start + len(black_row)] = black_row

    def _build_vis_grid(self) -> List[List[int]]:
        vis_grid: List[List[int]] = [
            [1 for _ in range(self.vis_w)] for _ in range(self.vis_h)]
        n_bit, e_bit, s_bit, w_bit = 1, 2, 4, 8

        for y in range(self.maze.h):
            for x in range(self.maze.w):
                vx: int = x * 2 + 1
                vy: int = y * 2 + 1
                vis_grid[vy][vx] = 0
                val: int = self.maze.grid[y][x]

                if not (val & n_bit):
                    vis_grid[vy - 1][vx] = 0
                if not (val & e_bit):
                    vis_grid[vy][vx + 1] = 0
                if not (val & s_bit):
                    vis_grid[vy + 1][vx] = 0
                if not (val & w_bit):
                    vis_grid[vy][vx - 1] = 0

        for y in range(2, self.vis_h - 1, 2):
            for x in range(2, self.vis_w - 1, 2):
                if (vis_grid[y - 1][x] == 0 and vis_grid[y + 1][x] == 0 and
                        vis_grid[y][x - 1] == 0 and vis_grid[y][x + 1] == 0):
                    vis_grid[y][x] = 0
        return vis_grid

    def _draw_walls(self) -> None:
        vis_grid: List[List[int]] = self._build_vis_grid()
        for vy in range(self.vis_h):
            for vx in range(self.vis_w):
                color: bytes = (
                    self.C_WALL if vis_grid[vy][vx] == 1 else self.C_PATH)
                self.draw_block(vx, vy, color)

    def _draw_pattern(self) -> None:
        if (not hasattr(self.maze, 'pattern_cells')
                or not self.maze.pattern_cells):
            return

        for x, y in self.maze.pattern_cells:
            vx: int = x * 2 + 1
            vy: int = y * 2 + 1
            self.draw_block(vx, vy, self.C_PATTERN)
            if (x + 1, y) in self.maze.pattern_cells:
                self.draw_block(vx + 1, vy, self.C_PATTERN)
            if (x, y + 1) in self.maze.pattern_cells:
                self.draw_block(vx, vy + 1, self.C_PATTERN)

    def _draw_solution_path(self) -> None:
        if not self.show_path:
            return

        # Aquí ahora llamamos al solver independiente
        path: List[Tuple[int, int]] = find_shortest_path(self.maze)
        for i in range(len(path)):
            x, y = path[i]
            vx: int = x * 2 + 1
            vy: int = y * 2 + 1
            self.draw_block(vx, vy, self.C_SOL)

            if i < len(path) - 1:
                nx, ny = path[i + 1]
                cvx: int = (vx + (nx * 2 + 1)) // 2
                cvy: int = (vy + (ny * 2 + 1)) // 2
                self.draw_block(cvx, cvy, self.C_SOL)

    def _draw_entry_exit(self) -> None:
        ex, ey = self.maze.config.entry
        xx, xy = self.maze.config.exit
        self.draw_block(ex * 2 + 1, ey * 2 + 1, self.C_ENTRY)
        self.draw_block(xx * 2 + 1, xy * 2 + 1, self.C_EXIT)

    def draw_to_memory(self) -> None:
        self._clear_background()
        self._draw_walls()
        self._draw_pattern()
        self._draw_solution_path()
        self._draw_entry_exit()

    def render(self) -> None:
        self.exit_code = 0
        self.draw_to_memory()
        self.app.mlx_loop_hook(self.mlx_ptr, self.push_to_window, None)
        self.app.mlx_key_hook(self.win_ptr, self.handle_input, None)
        self.app.mlx_hook(self.win_ptr, 17, 0, self.close_window, None)
        self.app.mlx_loop(self.mlx_ptr)

        if self.exit_code != 0:
            print(f"[*] Exiting program cleanly with error {self.exit_code}.")
            sys.exit(self.exit_code)
        else:
            if self.maze.config.verbose:
                print("[*] Visualizer closed safely.")
            sys.exit(0)

    def push_to_window(self, _param: Any) -> int:
        if not self.drawn_flag["ready"]:
            try:
                self.app.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                                 self.img_ptr, 0, 0)
                menu = "1: regen; 2: path; 3: color; 4: quit"
                self.app.mlx_string_put(self.mlx_ptr, self.win_ptr,
                                        20, self.win_h - 30, 0xFFFFFF, menu)
                self.app.mlx_do_sync(self.mlx_ptr)
                self.drawn_flag["ready"] = True
            except Exception:
                self.drawn_flag["ready"] = True
        return 0

    def handle_input(self, key: int, _param: Any) -> int:
        if key in (65307, 53, 52):  # ESC or '4'
            self.close_window()
        elif key == 49:  # '1' (Regenerate)
            # Instanciamos el nuevo generador y actualizamos el laberinto
            gen = MazeGenerator(
                width=self.maze.config.width,
                height=self.maze.config.height,
                entry=self.maze.config.entry,
                exit=self.maze.config.exit,
                perfect=self.maze.config.perfect,
                seed=self.maze.config.seed
            )
            gen.generate()
            self.maze.grid = gen.get_maze()
            self.maze.pattern_cells = gen.pattern_cells

            try:
                # Usamos el exportador independiente
                exporter.save_to_file(self.maze, self.maze.config.output_file)
            except OSError as e:
                self.critical_error_exit(f"Failed to save maze: {e}")
                return 0

            self.draw_to_memory()
            self.drawn_flag["ready"] = False

        elif key == 50:  # '2' (Toggle Path)
            self.show_path = not self.show_path
            self.draw_to_memory()
            self.drawn_flag["ready"] = False

        elif key == 51:  # '3' (Change Color)
            self.color_idx = (self.color_idx + 1) % len(self.wall_palettes)
            self.setup_colors()
            self.draw_to_memory()
            self.drawn_flag["ready"] = False

        return 0

    def close_window(self, _param: Any = None, exit_code:
                     int = 0, error_msg: str = "") -> int:
        if error_msg:
            print(f"\n[CRITICAL ERROR] {error_msg}")
        elif self.maze.config.verbose:
            print("\n[*] Releasing MLX resources and closing visualizer...")

        if hasattr(self, 'img_ptr') and self.img_ptr:
            try:
                self.app.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
            except Exception:
                pass

        if hasattr(self, 'win_ptr') and self.win_ptr:
            try:
                self.app.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
            except Exception:
                pass

        self.exit_code = exit_code
        if hasattr(self.app, 'mlx_loop_exit'):
            self.app.mlx_loop_exit(self.mlx_ptr)
        return 0

    def critical_error_exit(self, error_msg: str) -> None:
        print(f"\n[CRITICAL ERROR] {error_msg}")
        print("[*] Releasing MLX resources...")

        if hasattr(self, 'img_ptr') and self.img_ptr:
            try:
                self.app.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
            except Exception:
                pass

        if hasattr(self, 'win_ptr') and self.win_ptr:
            try:
                self.app.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
            except Exception:
                pass

        self.exit_code = 1
        if hasattr(self.app, 'mlx_loop_exit'):
            self.app.mlx_loop_exit(self.mlx_ptr)
