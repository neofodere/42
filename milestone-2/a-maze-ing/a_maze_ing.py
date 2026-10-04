#!/usr/bin/env python3

import sys
from maze.config_parser import MazeConfig, DisplayMode
from maze.maze import Maze
from maze.generator import MazeGenerator
from maze import exporter
from maze import renderer
from pydantic import ValidationError


def main() -> None:
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: python3 a_maze_ing.py <config_file>")

        config_file = sys.argv[1]
        config = MazeConfig.from_file(config_file)
        config.apply_seed()

        if config.verbose:
            print(f"[*] Initializing {config.width}x{config.height} Maze...")

        # 1. Instanciar el generador independiente (maze/generator.py)
        gen = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit,
            perfect=config.perfect,
            seed=config.seed
        )

        # 2. Generar el laberinto
        gen.generate()

        # 3. Crear estructura puente para UI/Exportador (maze/maze.py)
        maze = Maze(config)
        maze.grid = gen.get_maze()
        maze.pattern_cells = gen.pattern_cells

        # 4. Guardar a disco (maze/exporter.py)
        exporter.save_to_file(maze, config.output_file)
        if config.verbose:
            print(f"[*] Saved to {config.output_file}")

        # 5. Renderizar (maze/renderer.py)
        if config.display_mode == DisplayMode.ASCII:
            renderer.handle_ascii_interactive(maze)
        elif config.display_mode == DisplayMode.MLX:
            try:
                vis = renderer.MazeVisualizer(maze)
                vis.render()
            except ImportError:
                print("\n[ERROR] MLX library is not installed.")
                sys.exit(1)
    except ValidationError as e:
        print("[ERROR] Invalid configuration file.")
        print("Detailed validation errors:")

        # Iteramos sobre cada error que haya detectado Pydantic
        for error in e.errors():
            campo = " -> ".join(str(loc) for loc in error['loc'])
            mensaje = error['msg']

            print(f"  - Field '{campo}': {mensaje}")

        sys.exit(1)
    except Exception as e:
        print(f"\n[GLOBAL ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
