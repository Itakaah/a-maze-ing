from src.maze_model import (
    WALL_NORTH,
    WALL_SOUTH,
    WALL_WEST,
    MazeGrid,
)

# ANSI colour escape codes
COLOR_RESET: str = "\033[0m"
COLOR_MAGENTA: str = "\033[95m"   # entry marker
COLOR_RED: str = "\033[91m"       # exit marker
COLOR_PATH_BG: str = "\033[46m"   # cyan background for path cells
COLOR_RESERVED: str = "\033[90m"  # pattern-42 cells (dark grey)

# Wall colours the user can cycle through (option 3 in the menu)
WALL_COLORS: list[str] = [
    "\033[97m",   # bright white
    "\033[93m",   # bright yellow
    "\033[92m",   # bright green
    "\033[94m",   # bright blue
    "\033[95m",   # bright magenta
    "\033[91m",   # bright red
]
WALL_COLOR_NAMES: list[str] = [
    "white", "yellow", "green", "blue", "magenta", "red",
]

CHAR_CORNER: str = "+"
CHAR_H_WALL: str = "-"
CHAR_V_WALL: str = "|"
CHAR_OPEN: str = " "
CELL_INNER: int = 3  # chars per cell interior / horizontal wall segment
CHAR_ENTRY: str = "E"
CHAR_EXIT: str = "X"
CHAR_RESERVED: str = "#"


def _colored(text: str, color: str) -> str:
    """Wrap text with an ANSI colour code and the reset code.

    Args:
        text: The character(s) to colorise.
        color: An ANSI escape sequence like '\\033[97m'.

    Returns:
        The text surrounded by colour and reset codes.
    """
    return color + text + COLOR_RESET


def _render_top_border_line(grid: MazeGrid, wall_color: str) -> str:
    """Render the absolute top border of the maze (all walls closed).

    Args:
        grid: The maze grid.
        wall_color: ANSI colour to apply to wall characters.

    Returns:
        A single rendered line string.
    """
    corner = _colored(CHAR_CORNER, wall_color)
    h_wall = _colored(CHAR_H_WALL * CELL_INNER, wall_color)
    parts: list[str] = [corner]
    for _ in range(grid.width):
        parts.append(h_wall)
        parts.append(corner)
    return "".join(parts)


def _render_horizontal_border_line(
    grid: MazeGrid, row: int, wall_color: str
) -> str:
    """Render a horizontal border line between maze row-1 and row.

    A dash is shown where the South wall of row-1 (= North wall of row)
    is closed; a space where it is open.

    Args:
        grid: The maze grid.
        row: The maze row whose North wall we inspect (1 to height-1).
        wall_color: ANSI colour for wall characters.

    Returns:
        A single rendered line string.
    """
    corner = _colored(CHAR_CORNER, wall_color)
    parts: list[str] = [corner]
    for col in range(grid.width):
        cell = grid.get_cell(col, row)
        if cell.reserved or cell.has_wall(WALL_NORTH):
            parts.append(_colored(CHAR_H_WALL * CELL_INNER, wall_color))
        else:
            parts.append(CHAR_OPEN * CELL_INNER)
        parts.append(corner)
    return "".join(parts)


def _cell_body_char(col: int, row: int, grid: MazeGrid) -> str:
    """Choose the display character (with colour) for a cell's interior.

    Priority: entry > exit > reserved > empty.
    Path cells are handled separately in _render_cell_row_line.

    Args:
        col: Column of the cell.
        row: Row of the cell.
        grid: The maze grid.

    Returns:
        A single coloured character string.
    """
    pos = (col, row)
    if pos == grid.entry:
        return _colored(CHAR_ENTRY, COLOR_MAGENTA)
    if pos == grid.exit_pos:
        return _colored(CHAR_EXIT, COLOR_RED)
    if grid.get_cell(col, row).reserved:
        return _colored(CHAR_RESERVED, COLOR_RESERVED)
    return CHAR_OPEN


def _render_cell_row_line(
    grid: MazeGrid,
    row: int,
    path_cells: set[tuple[int, int]],
    show_path: bool,
    wall_color: str,
) -> str:
    """Render a row of cell bodies with their West and East walls.

    Args:
        grid: The maze grid.
        row: Which maze row to render.
        path_cells: Set of (col, row) cells on the solution path.
        show_path: Whether the solution path is visible.
        wall_color: ANSI colour for wall characters.

    Returns:
        A single rendered line string.
    """
    parts: list[str] = []
    for col in range(grid.width):
        cell = grid.get_cell(col, row)
        if col == 0 or cell.reserved or cell.has_wall(WALL_WEST):
            parts.append(_colored(CHAR_V_WALL, wall_color))
        else:
            parts.append(CHAR_OPEN)
        pos = (col, row)
        if (show_path and pos in path_cells
                and pos != grid.entry and pos != grid.exit_pos):
            parts.append(_colored(CHAR_OPEN * CELL_INNER, COLOR_PATH_BG))
        else:
            body = _cell_body_char(col, row, grid)
            parts.append(CHAR_OPEN + body + CHAR_OPEN)
    parts.append(_colored(CHAR_V_WALL, wall_color))
    return "".join(parts)


def _render_bottom_border_line(grid: MazeGrid, wall_color: str) -> str:
    """Render the absolute bottom border of the maze (all walls closed).

    Args:
        grid: The maze grid.
        wall_color: ANSI colour for wall characters.

    Returns:
        A single rendered line string.
    """
    last_row = grid.height - 1
    corner = _colored(CHAR_CORNER, wall_color)
    parts: list[str] = [corner]
    for col in range(grid.width):
        cell = grid.get_cell(col, last_row)
        if cell.reserved or cell.has_wall(WALL_SOUTH):
            parts.append(_colored(CHAR_H_WALL * CELL_INNER, wall_color))
        else:
            parts.append(CHAR_OPEN * CELL_INNER)
        parts.append(corner)
    return "".join(parts)


def render_maze(
    grid: MazeGrid,
    path_cells: set[tuple[int, int]],
    show_path: bool,
    wall_color_index: int,
) -> str:
    """Build the full ASCII representation of the maze.

    The maze is drawn on a character grid of (2*width+1) columns by
    (2*height+1) rows where corners are '+', walls are '-' or '|', and
    cell bodies hold markers (E, X, ., #) or spaces.

    Args:
        grid: The fully generated maze grid.
        path_cells: Set of (col, row) cells forming the solution path.
        show_path: Whether to display the solution path.
        wall_color_index: Index into WALL_COLORS for the wall colour.

    Returns:
        A multi-line string ready to print to the terminal.
    """
    wall_color = WALL_COLORS[wall_color_index % len(WALL_COLORS)]
    lines: list[str] = []
    lines.append(_render_top_border_line(grid, wall_color))
    for row in range(grid.height):
        lines.append(
            _render_cell_row_line(
                grid, row, path_cells, show_path, wall_color
            )
        )
        if row < grid.height - 1:
            lines.append(
                _render_horizontal_border_line(grid, row + 1, wall_color)
            )
    lines.append(_render_bottom_border_line(grid, wall_color))
    return "\n".join(lines)
