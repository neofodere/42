.PHONY: install run debug clean lint

install:
	pip install flake8 mypy

run:
	python3 drone_system.py map.txt

debug:
	python3 -m pdb drone_system.py map.txt

clean:
	rm -rf __pycache__ .mypy_cache

lint:
	flake8 drone_system.py
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs drone_system.py