PYTHON = python3
PIP    = $(PYTHON) -m pip
FLAKE8 = $(PYTHON) -m flake8
MYPY   = $(PYTHON) -m mypy
PYTEST = $(PYTHON) -m pytest
BUILD  = $(PYTHON) -m build

MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
             --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test build

install:
	$(PIP) install --user --quiet flake8 mypy pytest build 2>/dev/null || \
	$(PIP) install --user --quiet --break-system-packages flake8 mypy pytest build

run: install
	$(PYTHON) a_maze_ing.py config.txt

debug: install
	$(PYTHON) -m pdb a_maze_ing.py config.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	rm -f maze.txt

lint: install
	$(FLAKE8) .
	$(MYPY) . $(MYPY_FLAGS)

lint-strict: install
	$(MYPY) . --strict

test: install
	$(PYTEST) tests/ -v

build: install
	$(BUILD) --wheel --outdir .
