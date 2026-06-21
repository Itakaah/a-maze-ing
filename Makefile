PYTHON = python3
VENV   = venv
PIP    = $(VENV)/bin/pip
FLAKE8 = $(VENV)/bin/flake8
MYPY   = $(VENV)/bin/mypy
PYTEST = $(VENV)/bin/pytest
BUILD  = $(VENV)/bin/python -m build

MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
             --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test build

install:
	pip3 install --quiet virtualenv
	$(PYTHON) -m virtualenv $(VENV)
	$(PIP) install --quiet flake8 mypy pytest build

run:
	$(VENV)/bin/python a_maze_ing.py config.txt

debug:
	$(VENV)/bin/python -m pdb a_maze_ing.py config.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	rm -f maze.txt

lint:
	$(FLAKE8) .
	$(MYPY) . $(MYPY_FLAGS)

lint-strict:
	$(MYPY) . --strict

test:
	$(PYTEST) tests/ -v

build:
	$(PIP) install --quiet build
	$(BUILD) --wheel --outdir .
