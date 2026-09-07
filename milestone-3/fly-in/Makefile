.PHONY: install run debug clean lint lint-strict test

MAP ?= maps/easy/01_linear_path.txt
PY  ?= python3

install:
	$(PY) -m pip install --user flake8 mypy

run:
	$(PY) drone_system.py $(MAP)

debug:
	$(PY) -m pdb drone_system.py $(MAP)

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -name "*.pyc" -delete

lint:
	flake8 drone_system.py
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs drone_system.py

lint-strict:
	flake8 drone_system.py
	mypy --strict drone_system.py

test:
	$(PY) -m pytest tests -v
