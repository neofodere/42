try:
    from pydantic import (BaseModel, Field, ConfigDict,
                          model_validator, field_validator)
    import random
    import sys
    from enum import Enum
    from typing import Tuple, Optional, Dict, Any
except ModuleNotFoundError:
    print("[ERROR] Please executa: make install")
    print("To install missing dependencies (Pydantic)")
    exit(1)


class Algorithm(str, Enum):
    DFS = "DFS"
    KRUSKAL = "KRUSKAL"
    PRIM = "PRIM"


class DisplayMode(str, Enum):
    ASCII = "ASCII"
    MLX = "MLX"


class MazeConfig(BaseModel):
    """Handles file parsing and CLI validation."""
    # Freezes the class so values cannot be modified after instantiation
    model_config = ConfigDict(frozen=True)
    config_file: str = Field(
        ...,
        description="Path to the configuration file"
    )
    width: int = Field(
        gt=1,
        description="Width of the maze (must be greater than 1)"
    )
    height: int = Field(
        gt=1,
        description="Height of the maze (must be greater than 1)"
    )
    entry: Tuple[int, int] = Field(
        ...,
        description="X and Y coordinates for the maze entry"
    )
    exit: Tuple[int, int] = Field(
        ...,
        description="X and Y coordinates for the maze exit"
    )
    output_file: str = Field(
        ...,
        description="Path for the output file"
    )
    perfect: bool = Field(
        ...,
        description="True if the maze should be perfect (no loops)"
    )
    seed: Optional[int] = Field(
        default=None,
        description="Seed for random generation"
    )
    algorithm: Optional[Algorithm] = Field(
        default=None,
        description="Maze generation algorithm"
    )
    display_mode: Optional[DisplayMode] = Field(
        default=DisplayMode.ASCII,
        description="Visual output mode"
    )
    verbose: Optional[bool] = Field(
        default=False,
        description="True if show messages on terminal"
    )

    @model_validator(mode='after')
    def validate_maze_logic(self) -> "MazeConfig":
        ex, ey = self.entry
        xx, xy = self.exit
        w, h = self.width, self.height

        # 1. Check for negative coordinates
        if ex < 0 or ey < 0:
            raise ValueError("Entry coordinates cannot be negative")
        if xx < 0 or xy < 0:
            raise ValueError("Exit coordinates cannot be negative")

        # 2. Check that coordinates are within the maze bounds
        if ex >= w or ey >= h:
            raise ValueError(f"Entry point ({ex}, {ey}) is out of bounds "
                             f"for a {w}x{h} maze")
        if xx >= w or xy >= h:
            raise ValueError(f"Exit point ({xx}, {xy}) is out of bounds "
                             f"for a {w}x{h} maze")

        # 3. Check that entry and exit are not the exact same spot
        if self.entry == self.exit:
            raise ValueError("Entry and exit points cannot be the exact "
                             "same coordinates")

        return self

    @staticmethod
    def _parse_line(line: str, data: Dict[str, Any]) -> None:
        """Parses a single line from the config file and updates the data."""
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            return

        key, value = line.split('=', 1)
        key = key.strip().upper()
        value = value.strip()

        if key.lower() in data:
            raise ValueError(
                f"Duplicate key found in configuration file: {key}")

        # Grouping similar assignments reduces complexity
        if key in ('WIDTH', 'HEIGHT', 'SEED'):
            data[key.lower()] = int(value)
        elif key in ('ENTRY', 'EXIT'):
            coords = value.split(',')
            data[key.lower()] = (int(coords[0]), int(coords[1]))
        elif key in ('PERFECT', 'VERBOSE'):
            data[key.lower()] = value.lower() == 'true'
        elif key in ('ALGORITHM', 'DISPLAY_MODE'):
            data[key.lower()] = value.upper()
        elif key == 'OUTPUT_FILE':
            data['output_file'] = value

    @classmethod
    def from_file(cls, filepath: str) -> "MazeConfig":
        """Reads a .txt config file and returns a MazeConfig."""
        data: Dict[str, Any] = {'config_file': filepath}
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    cls._parse_line(line, data)
        except PermissionError:
            print(f"[ERROR] Permission denied. Cannot read configuration file:"
                  f"'{filepath}'")
            sys.exit(1)

        except FileNotFoundError:
            print(f"[ERROR] Configuration file '{filepath}' not found.")
            sys.exit(1)

        except OSError as e:
            # El cajón de sastre por si falla el disco duro u otra cosa rara
            print(
                f"[ERROR] An unexpected OS error occurred while reading: {e}")
            sys.exit(1)

        return cls(**data)

    def apply_seed(self) -> None:
        """Applies the random seed if one was provided in the config."""
        if self.seed is not None:
            random.seed(self.seed)
            print(f"Configuration: Random seed set to {self.seed}")

    @field_validator('output_file')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Sanitizes the output filename to prevent
            Path Traversal attacks."""
        # Avoid suba de directorio o especifique rutas absolutas
        if '/' in v or '\\' in v or '..' in v:
            raise ValueError("Output filename cannot contain directories or "
                             "path traversal characters.")

        # Opcional: Forzar a que siempre termine en .txt
        if not v.endswith('.txt'):
            v += '.txt'

        return v
