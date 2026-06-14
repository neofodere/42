# Makefile for A-Maze-ing

# Variables
PYTHON = python3
PIP = pip3
MAIN_SCRIPT = a_maze_ing.py
CONFIG = config.txt
VENV = venv
VENV_PIP = $(VENV)/bin/pip
MLX_DIR = mlx_CLXV
MLX_TGZ = mlx_CLXV-2.2.tgz

# Rules
.PHONY: all install run debug clean lint lint-strict build re

all: run

# Install dependencies (flake8, mypy, etc.)
install:
	@echo "\n[*] Creating virtual environment '$(VENV)'..."
	@$(PYTHON) -m venv $(VENV)
	@echo "[*] Extracting MLX source..."
	@tar -xzf $(MLX_TGZ)
	@echo "[*] Compiling MLX (C to Python wheel)..."
	@$(MAKE) -C $(MLX_DIR)
	@echo "[*] Installing MLX into virtual environment..."
	@$(VENV_PIP) install $(MLX_DIR)/*.whl
	@echo "[*] Cleaning up extracted MLX folder to hide it from linters..."
	@rm -rf $(MLX_DIR)
	@echo "[*] Installing project dependencies..."
	@$(VENV_PIP) install -r requirements.txt
	@echo "\n[+] Installation complete! MLX is safely inside $(VENV)."

# Run the main program
run:
	$(PYTHON) $(MAIN_SCRIPT) $(CONFIG)

# Run in debug mode (pdb)
debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT) $(CONFIG)

# Clean up cache files
# Clean up cache and build files
clean:
	@echo "[*] Cleaning cache and build artifacts..."
	# 1. Borrar cachés de Python y Mypy en todo el proyecto
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@rm -rf .mypy_cache
	
	# 2. Borrar la carpeta extraída de MLX para evitar errores en el linter
	@rm -rf mlx_CLXV
	
	# 3. Borrar el archivo de salida del laberinto
	@rm -f maze.txt
	
	# 4. Borrar los artefactos de compilación del paquete pip
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@rm -rf maze/*.egg-info
	@rm -f mazegen-*.tar.gz
	@rm -f mazegen-*.whl
	
	@echo "[*] Clean complete!"

# Mandatory Linting Rule (Subject III.2)
# Mandatory Linting Rule
# Mandatory Linting Rule
lint:
	@echo "[*] Running standard linting..."
	flake8 . --exclude=venv
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
# Optional Strict Linting
lint-strict:
	@echo "[*] Running strict linting..."
	flake8 . --exclude=venv
	mypy . --strict

# Build the pip package (mazegen-*)
build:
	@echo "[*] Building the pip package..."
	$(PYTHON) -m build --outdir .

re: clean all