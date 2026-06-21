WALL_NORTH: int = 1
WALL_EAST: int = 2
WALL_SOUTH: int = 4
WALL_WEST: int = 8
ALL_WALLS: int = 15

OPPOSITE_WALL: dict[int, int] = {
    WALL_NORTH: WALL_SOUTH,
    WALL_SOUTH: WALL_NORTH,
    WALL_EAST: WALL_WEST,
    WALL_WEST: WALL_EAST,
}


class MazeCell:
    """Represents a single cell in the maze with its wall state."""

    def __init__(self) -> None:
        """Initialize cell with all four walls closed."""
        self.walls: int = ALL_WALLS
        self.reserved: bool = False

    def has_wall(self, direction: int) -> bool:
        """Return True if the wall in the given direction is closed.

        Args:
            direction: One of WALL_NORTH, WALL_EAST, WALL_SOUTH, WALL_WEST.

        Returns:
            True if the wall is present (closed), False if open.
        """
        return bool(self.walls & direction)

    def open_wall(self, direction: int) -> None:
        """Remove (open) the wall in the given direction.

        Args:
            direction: One of WALL_NORTH, WALL_EAST, WALL_SOUTH, WALL_WEST.
        """
        self.walls = self.walls & ~direction

    def to_hex(self) -> str:
        """Return the single hex character encoding this cell's walls.

        Returns:
            A lowercase hex digit ('0' to 'f').
        """
        return format(self.walls, 'x')


class MazeGrid:
    """Stores the 2D grid of cells and maze metadata (entry, exit)."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
    ) -> None:
        """Create a grid of the given size with all walls closed.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            entry: (col, row) coordinates of the entry point.
            exit_pos: (col, row) coordinates of the exit point.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos
        self.cells: list[list[MazeCell]] = [
            [MazeCell() for _ in range(width)]
            for _ in range(height)
        ]

    def get_cell(self, col: int, row: int) -> MazeCell:
        """Return the cell at position (col, row).

        Args:
            col: Column index (0 = leftmost).
            row: Row index (0 = top).

        Returns:
            The MazeCell at that position.
        """
        return self.cells[row][col]

    def is_valid(self, col: int, row: int) -> bool:
        """Return True if (col, row) is within the maze boundaries.

        Args:
            col: Column index to check.
            row: Row index to check.

        Returns:
            True if inside the maze, False otherwise.
        """
        return 0 <= col < self.width and 0 <= row < self.height
