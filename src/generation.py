import random

from src.config_parser import MazeConfig
from src.maze_model import (
    OPPOSITE_WALL,
    WALL_EAST,
    WALL_NORTH,
    WALL_SOUTH,
    WALL_WEST,
    MazeGrid,
)
from src.pattern_42 import apply_pattern_42

DIRECTION_MOVES = [
    (0, -1, WALL_NORTH, WALL_SOUTH),
    (1, 0, WALL_EAST, WALL_WEST),
    (0, 1, WALL_SOUTH, WALL_NORTH),
    (-1, 0, WALL_WEST, WALL_EAST),
]

EXTRA_PASSAGE_CHANCE = 0.12


def open_passage(
    grid: MazeGrid,
    col: int,
    row: int,
    neighbour_col: int,
    neighbour_row: int,
    wall_current: int,
) -> None:
    """Open the shared wall between two adjacent cells.

    Args:
        grid: The maze grid to modify.
        col: Column of the current cell.
        row: Row of the current cell.
        neighbour_col: Column of the neighbour cell.
        neighbour_row: Row of the neighbour cell.
        wall_current: Direction constant of the wall to remove on current.
    """
    grid.get_cell(col, row).open_wall(wall_current)
    wall_neighbour = OPPOSITE_WALL[wall_current]
    grid.get_cell(neighbour_col, neighbour_row).open_wall(wall_neighbour)


def get_unvisited_neighbours(
    grid: MazeGrid,
    col: int,
    row: int,
    visited: set[tuple[int, int]],
) -> list[tuple[int, int, int]]:
    """Return all unvisited, non-reserved neighbours of a cell.

    Args:
        grid: The maze grid.
        col: Column of the current cell.
        row: Row of the current cell.
        visited: Set of already-visited (col, row) positions.

    Returns:
        List of (neighbour_col, neighbour_row, wall_current)
        for each eligible neighbour.
    """
    neighbours: list[tuple[int, int, int]] = []
    for delta_col, delta_row, wall_current, _ in DIRECTION_MOVES:
        new_col = col + delta_col
        new_row = row + delta_row
        if not grid.is_valid(new_col, new_row):
            continue
        if (new_col, new_row) in visited:
            continue
        if grid.get_cell(new_col, new_row).reserved:
            continue
        neighbours.append((new_col, new_row, wall_current))
    return neighbours


def run_dfs(
    grid: MazeGrid,
    start_col: int,
    start_row: int,
    rng: random.Random,
) -> None:
    """Carve passages through the grid using iterative DFS (backtracker).

    Starts from (start_col, start_row) and visits every non-reserved cell
    exactly once, opening walls to create a spanning-tree maze.

    Args:
        grid: The maze grid to carve in place.
        start_col: Column of the starting cell.
        start_row: Row of the starting cell.
        rng: Seeded random number generator for reproducibility.
    """
    visited: set[tuple[int, int]] = {(start_col, start_row)}
    stack: list[tuple[int, int]] = [(start_col, start_row)]
    while stack:
        col, row = stack[-1]
        neighbours = get_unvisited_neighbours(grid, col, row, visited)
        if not neighbours:
            stack.pop()
            continue
        next_col, next_row, wall_current = rng.choice(neighbours)
        open_passage(grid, col, row, next_col, next_row, wall_current)
        visited.add((next_col, next_row))
        stack.append((next_col, next_row))


def add_extra_passages(grid: MazeGrid, rng: random.Random) -> None:
    """Randomly open additional walls to create a non-perfect maze.

    Iterates over every internal wall and opens it with probability
    EXTRA_PASSAGE_CHANCE.

    Args:
        grid: The maze grid to modify in place.
        rng: Seeded random number generator.
    """
    for row in range(grid.height):
        for col in range(grid.width):
            if grid.get_cell(col, row).reserved:
                continue
            for delta_col, delta_row, wall_current, _ in DIRECTION_MOVES:
                new_col = col + delta_col
                new_row = row + delta_row
                if not grid.is_valid(new_col, new_row):
                    continue
                if grid.get_cell(new_col, new_row).reserved:
                    continue
                if not grid.get_cell(col, row).has_wall(wall_current):
                    continue
                if rng.random() <= EXTRA_PASSAGE_CHANCE:
                    open_passage(
                        grid, col, row, new_col, new_row, wall_current
                    )


def generate_maze(config: MazeConfig) -> MazeGrid:
    """Build and generate a complete maze from the given configuration.

    Steps:
    1. Create an empty grid (all walls closed).
    2. Apply the '42' pattern (marks reserved cells).
    3. Run DFS from the entry cell to carve passages.
    4. If not perfect, add extra passages to create cycles.

    Args:
        config: Parsed and validated maze configuration.

    Returns:
        A fully generated MazeGrid.
    """
    grid = MazeGrid(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit_pos=config.exit_pos,
    )
    apply_pattern_42(grid)
    entry_col, entry_row = config.entry
    exit_col, exit_row = config.exit_pos
    grid.get_cell(entry_col, entry_row).reserved = False
    grid.get_cell(exit_col, exit_row).reserved = False
    rng = random.Random(config.seed)
    run_dfs(grid, entry_col, entry_row, rng)
    if not config.perfect:
        add_extra_passages(grid, rng)
    return grid
