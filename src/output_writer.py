from src.maze_model import MazeGrid

NO_PATH_MARKER: str = "NO_PATH"


def grid_to_hex_lines(grid: MazeGrid) -> list[str]:
    """Convert the maze grid to a list of hex-encoded row strings.

    Each row becomes one string of hex characters (one per cell), with
    no separators.  The value for each cell is its wall bitmap (0–15).

    Args:
        grid: The fully generated maze grid.

    Returns:
        A list of strings, one per maze row, each ending without '\\n'.
    """
    lines: list[str] = []
    for row in range(grid.height):
        row_str = ""
        for col in range(grid.width):
            row_str += grid.get_cell(col, row).to_hex()
        lines.append(row_str)
    return lines


def path_to_string(path: list[str] | None) -> str:
    """Convert a direction list to the compact string for the output file.

    Args:
        path: List of direction letters, or None if no path exists.

    Returns:
        A concatenated string like 'NNEESS', or NO_PATH_MARKER if None.
    """
    if path is None:
        return NO_PATH_MARKER
    return "".join(path)


def write_maze_output(
    filepath: str,
    grid: MazeGrid,
    path: list[str] | None,
) -> None:
    """Write the maze output file in the required three-section format.

    Section 1: hex grid (one row per line).
    Section 2: blank line.
    Section 3: entry coordinates, exit coordinates, path string.

    All lines end with '\\n'.

    Args:
        filepath: Path to the output file to create or overwrite.
        grid: The fully generated maze grid.
        path: Shortest path as direction letters, or None.

    Raises:
        OSError: If the file cannot be written.
    """
    hex_lines = grid_to_hex_lines(grid)
    path_str = path_to_string(path)
    entry_col, entry_row = grid.entry
    exit_col, exit_row = grid.exit_pos
    with open(filepath, "w", encoding="utf-8") as output_file:
        for line in hex_lines:
            output_file.write(line + "\n")
        output_file.write("\n")
        output_file.write(f"{entry_col},{entry_row}\n")
        output_file.write(f"{exit_col},{exit_row}\n")
        output_file.write(path_str + "\n")
