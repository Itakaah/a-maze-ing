from collections import deque

from src.maze_model import (
    WALL_EAST,
    WALL_NORTH,
    WALL_SOUTH,
    WALL_WEST,
    MazeGrid,
)

# (delta_col, delta_row, wall_to_cross, direction_letter)
SOLVER_MOVES = [
    (0, -1, WALL_NORTH, "N"),
    (1, 0, WALL_EAST, "E"),
    (0, 1, WALL_SOUTH, "S"),
    (-1, 0, WALL_WEST, "W"),
]


def get_open_neighbours(
    grid: MazeGrid,
    col: int,
    row: int,
) -> list[tuple[int, int, str]]:
    """Return all neighbours reachable from (col, row) through open walls.

    Args:
        grid: The maze grid.
        col: Current column.
        row: Current row.

    Returns:
        List of (neighbour_col, neighbour_row, direction_letter) tuples.
    """
    neighbours = []
    for delta_col, delta_row, wall, direction in SOLVER_MOVES:
        new_col = col + delta_col
        new_row = row + delta_row
        if not grid.is_valid(new_col, new_row):
            continue
        if grid.get_cell(col, row).has_wall(wall):
            continue
        neighbours.append((new_col, new_row, direction))
    return neighbours


def solve_maze(
    grid: MazeGrid,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
) -> list[str] | None:
    """Find the shortest path from entry to exit using BFS.

    Args:
        grid: The maze grid.
        entry: (col, row) of the starting cell.
        exit_pos: (col, row) of the destination cell.

    Returns:
        A list of direction letters ('N', 'E', 'S', 'W') representing
        the shortest path, or None if no path exists.
    """
    if entry == exit_pos:
        return []
    visited = {entry}
    queue: deque[tuple[int, int]] = deque([entry])
    parent: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
    while queue:
        col, row = queue.popleft()
        for new_col, new_row, direction in get_open_neighbours(
            grid, col, row
        ):
            if (new_col, new_row) in visited:
                continue
            visited.add((new_col, new_row))
            parent[(new_col, new_row)] = ((col, row), direction)
            if (new_col, new_row) == exit_pos:
                directions = []
                current = exit_pos
                while current != entry:
                    prev_cell, step = parent[current]
                    directions.append(step)
                    current = prev_cell
                directions.reverse()
                return directions
            queue.append((new_col, new_row))
    return None


def path_to_cells(
    entry: tuple[int, int],
    path: list[str],
) -> set[tuple[int, int]]:
    """Convert a direction path into the set of cells it visits.

    Args:
        entry: Starting (col, row) before the first move.
        path: List of direction letters from solve_maze.

    Returns:
        Set of (col, row) tuples for every cell on the path (incl. entry).
    """
    direction_delta = {
        "N": (0, -1),
        "E": (1, 0),
        "S": (0, 1),
        "W": (-1, 0),
    }
    cells: set[tuple[int, int]] = {entry}
    col, row = entry
    for direction in path:
        delta_col, delta_row = direction_delta[direction]
        col += delta_col
        row += delta_row
        cells.add((col, row))
    return cells
