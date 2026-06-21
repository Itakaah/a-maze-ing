*This project has been created as part of the 42 curriculum by Itakaah.*

## Description

A-Maze-ing is a Python maze generator that reads a configuration file,
builds a random maze using the Recursive Backtracker algorithm, embeds
a visible "42" pattern, solves the maze with BFS, writes a hexadecimal
output file, and provides an interactive ASCII terminal display.

## Instructions

### Requirements

- Python 3.10 or later
- Tested on Python 3.14

### Setup and run

```bash
# Create virtual environment and install dependencies
make install

# Run the maze generator (reads config.txt)
make run

# Or run directly:
python3 a_maze_ing.py config.txt
```

### Makefile targets

| Target       | Description                                      |
|--------------|--------------------------------------------------|
| `install`    | Create `.venv` and install flake8, mypy, pytest  |
| `run`        | Launch the maze program with `config.txt`        |
| `debug`      | Launch with `pdb` debugger                       |
| `clean`      | Remove `__pycache__`, `.mypy_cache`, build files |
| `lint`       | Run `flake8` and `mypy` with required flags      |
| `lint-strict`| Run `mypy --strict`                              |
| `test`       | Run the pytest test suite                        |
| `build`      | Build `mazegen-1.0.0-py3-none-any.whl`          |

### Interactive menu

Once the maze is displayed, use number keys then Enter:

- `1` — Regenerate a new maze
- `2` — Show / hide the solution path
- `3` — Cycle wall colours (white → yellow → green → blue → magenta → red)
- `4` — Quit

## Configuration file

The configuration file uses `KEY=VALUE` pairs, one per line.
Lines starting with `#` are comments and are ignored.

| Key           | Required | Description                                    | Example        |
|---------------|----------|------------------------------------------------|----------------|
| `WIDTH`       | Yes      | Number of columns (≥ 2)                        | `WIDTH=20`     |
| `HEIGHT`      | Yes      | Number of rows (≥ 2)                           | `HEIGHT=15`    |
| `ENTRY`       | Yes      | Entry cell as `col,row` (0-indexed, top-left)  | `ENTRY=0,0`    |
| `EXIT`        | Yes      | Exit cell as `col,row`                         | `EXIT=19,14`   |
| `OUTPUT_FILE` | Yes      | Path for the hex output file                   | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | Yes      | `True` = single path, `False` = multiple paths | `PERFECT=True` |
| `SEED`        | No       | Integer seed for reproducible generation       | `SEED=42`      |

### Output file format

```
[hex grid — one row per line, one hex character per cell]
[blank line]
entry_col,entry_row
exit_col,exit_row
[path as direction letters: N E S W]
```

Wall encoding per cell (4-bit, one hex digit):

| Bit | Direction | Value |
|-----|-----------|-------|
| 0   | North     | 1     |
| 1   | East      | 2     |
| 2   | South     | 4     |
| 3   | West      | 8     |

`1` = wall closed, `0` = wall open.  `f` = all walls closed (reserved cell).

## Maze generation algorithm

**Algorithm chosen: Recursive Backtracker (iterative DFS with an explicit stack)**

The algorithm works as follows:
1. Start at the entry cell; mark it visited; push it onto a stack.
2. While the stack is not empty:
   - Look at the top cell. Find its unvisited, non-reserved neighbours.
   - If none: pop the stack (backtrack).
   - Otherwise: choose a neighbour at random, carve the passage between
     them (clear the shared wall from both sides), mark the neighbour as
     visited, push it.

**Why this algorithm?**

- **Simplest to explain** — the call stack (replaced by an explicit list)
  maps directly to the DFS mental model: go forward, hit a dead end,
  backtrack.
- **Produces perfect mazes** — a spanning-tree structure means there is
  exactly one path between any two cells, satisfying `PERFECT=True`.
- **No recursion limit** — the iterative version uses a Python list as
  the stack, so large mazes (e.g. 100×100) do not risk a stack overflow.
- **Reproducible** — seeding `random.Random` with `SEED` gives the same
  maze on every run.

For `PERFECT=False`, after the DFS each internal wall has a small
probability (12 %) of being opened, provided it would not create a 3×3+
fully-open region.

The "42" pattern is formed by marking cells as *reserved* before the DFS
starts: those cells keep all four walls closed (`0xF`) and are skipped
during traversal, making them appear as solid blocks in the output.

## Reusable module

The `mazegen` package provides a standalone `MazeGenerator` class that
can be installed independently from the main application.

### Install

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Usage

```python
from mazegen import MazeGenerator

gen = MazeGenerator(
    width=20,
    height=15,
    seed=42,        # optional: makes generation reproducible
    perfect=True,   # optional: single-path maze
    entry=(0, 0),   # optional: defaults to top-left
    exit_pos=(19, 14),  # optional: defaults to bottom-right
)
gen.generate()

grid = gen.get_grid()
# list[list[int]] — wall bitmask per cell (0–15)
# Bit 0 = North, Bit 1 = East, Bit 2 = South, Bit 3 = West

path = gen.get_solution()
# list[str] | None — e.g. ['N', 'E', 'E', 'S'] or None if unsolvable

entry = gen.get_entry()   # (col, row)
exit_ = gen.get_exit()    # (col, row)
```

### Rebuild from sources

```bash
pip install build
python -m build --wheel --outdir .
```

## Resources

### Documentation and references

- [Python 3.10+ type hints](https://docs.python.org/3/library/typing.html)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive Backtracker explained — jamisbuck.org](http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [BFS for shortest path — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [flake8 documentation](https://flake8.pycqa.org/)
- [mypy documentation](https://mypy.readthedocs.io/)

### AI usage

Claude (Anthropic) was used in this project for the following tasks:

- Generating the initial structure of each module with correct type hints,
  docstrings, and flake8/mypy-compliant code.
- Suggesting the pixel-art bitmap for the "42" pattern and the coordinate
  mapping to grid cells.
- Writing the pytest test suite (assertions, fixtures, edge cases).
- Reviewing lint errors and proposing fixes.

All generated code was read, understood, and validated before inclusion.
The algorithm choices (Recursive Backtracker, BFS) and the overall
architecture were decided before prompting the AI.

## Team management

**Team:** solo project (Itakaah).

**Planning:** The build order followed the dependency chain —
data model → config → generation → solver → output → renderer → menu.
Each module was linted immediately after writing, before moving on.

**What worked well:** Writing tests alongside each module caught issues
early (e.g. wall coherence after DFS, reserved-cell isolation).

**What to improve:** The renderer output could benefit from a curses-based
display to avoid screen flicker on each redraw.
