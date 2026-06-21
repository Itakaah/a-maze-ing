PYTHON = python3
VENV   = .venv
PIP    = $(VENV)/bin/pip
FLAKE8 = $(VENV)/bin/flake8
MYPY   = $(VENV)/bin/mypy
PYTEST = $(VENV)/bin/pytest
BUILD  = $(VENV)/bin/python -m build

PYTHON_VERSION := $(shell python3 -c \
	"import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
             --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test build

install:
	@if ! $(PYTHON) -m venv $(VENV) 2>/dev/null; then \
		$(PYTHON) -m pip install --user --quiet virtualenv 2>/dev/null || \
		$(PYTHON) -m pip install --user --quiet --break-system-packages virtualenv; \
		$(PYTHON) -m virtualenv $(VENV); \
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
