PYTHON   = python3
VENV     = .venv
PIP      = $(VENV)/bin/pip
PYTEST   = $(VENV)/bin/pytest
FLAKE8   = $(VENV)/bin/flake8
MYPY     = $(VENV)/bin/mypy
BUILD    = $(VENV)/bin/python -m build

MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
             --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test build

install:
	@if ! $(PYTHON) -m venv $(VENV) 2>/dev/null; then \
		sudo apt-get install -y python3-venv python3.10-venv python3-pip 2>/dev/null || true; \
		$(PYTHON) -m venv $(VENV); \
	fi
	$(PIP) install --quiet flake8 mypy pytest build

run: install
	$(VENV)/bin/python a_maze_ing.py config.txt

debug: install
	$(VENV)/bin/python -m pdb a_maze_ing.py config.txt

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
	$(PIP) install --quiet build
	$(BUILD) --wheel --outdir .
