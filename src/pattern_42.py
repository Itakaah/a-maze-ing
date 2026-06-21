import sys

from src.maze_model import MazeGrid

# Each digit is 5 rows x 3 cols. 1 = reserved cell, 0 = passage cell.
DIGIT_4 = [
    [1, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]

DIGIT_2 = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]

PATTERN_HEIGHT: int = 5       # rows used by each digit
PATTERN_DIGIT_WIDTH: int = 3  # cols used by each digit
PATTERN_GAP: int = 1          # gap column between '4' and '2'
PATTERN_MARGIN: int = 1       # minimum margin around the pattern

PATTERN_TOTAL_WIDTH: int = (
    PATTERN_DIGIT_WIDTH + PATTERN_GAP + PATTERN_DIGIT_WIDTH
)
MIN_MAZE_WIDTH: int = PATTERN_TOTAL_WIDTH + 2 * PATTERN_MARGIN
MIN_MAZE_HEIGHT: int = PATTERN_HEIGHT + 2 * PATTERN_MARGIN


def get_pattern_cells(
    width: int, height: int
) -> list[tuple[int, int]] | None:
    """Compute the grid positions of all cells forming the '42' pattern.

    The pattern is centred horizontally and placed in the upper quarter
    of the maze vertically.  Returns None if the maze is too small to
    fit the pattern.

    Args:
        width: Number of columns in the maze.
        height: Number of rows in the maze.

    Returns:
        A list of (col, row) tuples for each reserved cell,
        or None if the pattern does not fit.
    """
    if width < MIN_MAZE_WIDTH or height < MIN_MAZE_HEIGHT:
        return None
    start_col = (width - PATTERN_TOTAL_WIDTH) // 2
    start_row = height // 4
    gap_start = start_col + PATTERN_DIGIT_WIDTH + PATTERN_GAP
    cells: list[tuple[int, int]] = []
    for digit_row in range(PATTERN_HEIGHT):
        for digit_col in range(PATTERN_DIGIT_WIDTH):
            if DIGIT_4[digit_row][digit_col] == 1:
                col = start_col + digit_col
                row = start_row + digit_row
                cells.append((col, row))
        for digit_col in range(PATTERN_DIGIT_WIDTH):
            if DIGIT_2[digit_row][digit_col] == 1:
                col = gap_start + digit_col
                row = start_row + digit_row
                cells.append((col, row))
    return cells


def apply_pattern_42(grid: MazeGrid) -> bool:
    """Mark '42' pattern cells as reserved in the grid.

    Reserved cells keep ALL_WALLS and are excluded from DFS traversal.
    If the maze is too small for the pattern, a message is printed to
    stderr and the function returns False without modifying the grid.

    Args:
        grid: The MazeGrid to modify in place.

    Returns:
        True if the pattern was applied, False if the maze is too small.
    """
    cells = get_pattern_cells(grid.width, grid.height)
    if cells is None:
        print(
            "Warning: maze is too small for the '42' pattern"
            f" (need {MIN_MAZE_WIDTH}x{MIN_MAZE_HEIGHT},"
            f" got {grid.width}x{grid.height}). Skipping pattern.",
            file=sys.stderr,
        )
        return False
    for col, row in cells:
        cell = grid.get_cell(col, row)
        cell.reserved = True
    return True
