import random
from collections import deque

WALL_NORTH: int = 1
WALL_EAST: int = 2
WALL_SOUTH: int = 4
WALL_WEST: int = 8
ALL_WALLS: int = 15

OPPOSITE: dict[int, int] = {
    WALL_NORTH: WALL_SOUTH,
    WALL_SOUTH: WALL_NORTH,
    WALL_EAST: WALL_WEST,
    WALL_WEST: WALL_EAST,
}

DFS_MOVES: list[tuple[int, int, int, int]] = [
    (0, -1, WALL_NORTH, WALL_SOUTH),
    (1, 0, WALL_EAST, WALL_WEST),
    (0, 1, WALL_SOUTH, WALL_NORTH),
    (-1, 0, WALL_WEST, WALL_EAST),
]

BFS_MOVES: list[tuple[int, int, int, str]] = [
    (0, -1, WALL_NORTH, "N"),
    (1, 0, WALL_EAST, "E"),
    (0, 1, WALL_SOUTH, "S"),
    (-1, 0, WALL_WEST, "W"),
]

DIGIT_4: list[list[int]] = [
    [1, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]

DIGIT_2: list[list[int]] = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]

PATTERN_HEIGHT: int = 5
PATTERN_DIGIT_WIDTH: int = 3
PATTERN_GAP: int = 1
PATTERN_MARGIN: int = 1
PATTERN_TOTAL_WIDTH: int = (
    PATTERN_DIGIT_WIDTH + PATTERN_GAP + PATTERN_DIGIT_WIDTH
)
MIN_MAZE_WIDTH: int = PATTERN_TOTAL_WIDTH + 2 * PATTERN_MARGIN
MIN_MAZE_HEIGHT: int = PATTERN_HEIGHT + 2 * PATTERN_MARGIN
EXTRA_PASSAGE_CHANCE: float = 0.12


def _compute_pattern_cells(
    width: int, height: int
) -> list[tuple[int, int]] | None:
    """Return the (col, row) positions of cells forming the '42' pattern.

    Returns None if the maze is too small.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        List of (col, row) tuples, or None.
    """
    if width < MIN_MAZE_WIDTH or height < MIN_MAZE_HEIGHT:
        return None
    start_col = (width - PATTERN_TOTAL_WIDTH) // 2
    start_row = height // 4
    cells: list[tuple[int, int]] = []
    for digit_row in range(PATTERN_HEIGHT):
        for digit_col in range(PATTERN_DIGIT_WIDTH):
            if DIGIT_4[digit_row][digit_col] == 1:
                cells.append((start_col + digit_col, start_row + digit_row))
        gap_start = start_col + PATTERN_DIGIT_WIDTH + PATTERN_GAP
        for digit_col in range(PATTERN_DIGIT_WIDTH):
            if DIGIT_2[digit_row][digit_col] == 1:
                cells.append((gap_start + digit_col, start_row + digit_row))
    return cells


def _open_wall(
    grid: list[list[int]], col: int, row: int,
    n_col: int, n_row: int, wall: int
) -> None:
    """Open the shared wall between (col, row) and its neighbour.

    Args:
        grid: 2D list of wall bitmasks (modified in place).
        col: Current cell column.
        row: Current cell row.
        n_col: Neighbour cell column.
        n_row: Neighbour cell row.
        wall: Wall constant on the current cell to open.
    """
    grid[row][col] = grid[row][col] & ~wall
    grid[n_row][n_col] = grid[n_row][n_col] & ~OPPOSITE[wall]


def _run_dfs(
    grid: list[list[int]],
    reserved: set[tuple[int, int]],
    width: int,
    height: int,
    start_col: int,
    start_row: int,
    rng: random.Random,
) -> None:
    """Carve passages with iterative DFS (Recursive Backtracker).

    Args:
        grid: 2D list of wall bitmasks (modified in place).
        reserved: Set of (col, row) positions to skip.
        width: Grid width.
        height: Grid height.
        start_col: Starting column.
        start_row: Starting row.
        rng: Seeded random generator.
    """
    visited: set[tuple[int, int]] = {(start_col, start_row)}
    stack: list[tuple[int, int]] = [(start_col, start_row)]
    while stack:
        col, row = stack[-1]
        neighbours: list[tuple[int, int, int]] = []
        for dc, dr, wall, _ in DFS_MOVES:
            nc, nr = col + dc, row + dr
            if nc < 0 or nc >= width or nr < 0 or nr >= height:
                continue
            if (nc, nr) in visited or (nc, nr) in reserved:
                continue
            neighbours.append((nc, nr, wall))
        if not neighbours:
            stack.pop()
            continue
        nc, nr, wall = rng.choice(neighbours)
        _open_wall(grid, col, row, nc, nr, wall)
        visited.add((nc, nr))
        stack.append((nc, nr))


def _add_extra_passages(
    grid: list[list[int]],
    reserved: set[tuple[int, int]],
    width: int,
    height: int,
    rng: random.Random,
) -> None:
    """Randomly open extra walls to create cycles (non-perfect mode).

    Args:
        grid: 2D list of wall bitmasks (modified in place).
        reserved: Set of reserved (col, row) positions.
        width: Grid width.
        height: Grid height.
        rng: Seeded random generator.
    """
    for row in range(height):
        for col in range(width):
            if (col, row) in reserved:
                continue
            for dc, dr, wall, _ in DFS_MOVES:
                nc, nr = col + dc, row + dr
                if nc < 0 or nc >= width or nr < 0 or nr >= height:
                    continue
                if (nc, nr) in reserved:
                    continue
                if not (grid[row][col] & wall):
                    continue
                if rng.random() <= EXTRA_PASSAGE_CHANCE:
                    _open_wall(grid, col, row, nc, nr, wall)


def _bfs(
    grid: list[list[int]],
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
) -> list[str] | None:
    """Find the shortest path from entry to exit using BFS.

    Args:
        grid: 2D list of wall bitmasks.
        width: Grid width.
        height: Grid height.
        entry: (col, row) starting position.
        exit_pos: (col, row) destination.

    Returns:
        List of direction letters ('N','E','S','W'), or None if unreachable.
    """
    if entry == exit_pos:
        return []
    visited: set[tuple[int, int]] = {entry}
    queue: deque[tuple[int, int]] = deque([entry])
    parent: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
    while queue:
        col, row = queue.popleft()
        for dc, dr, wall, direction in BFS_MOVES:
            nc, nr = col + dc, row + dr
            if nc < 0 or nc >= width or nr < 0 or nr >= height:
                continue
            if grid[row][col] & wall:
                continue
            if (nc, nr) in visited:
                continue
            visited.add((nc, nr))
            parent[(nc, nr)] = ((col, row), direction)
            if (nc, nr) == exit_pos:
                path: list[str] = []
                current = (nc, nr)
                while current != entry:
                    prev, step = parent[current]
                    path.append(step)
                    current = prev
                path.reverse()
                return path
            queue.append((nc, nr))
    return None


class MazeGenerator:
    """Generate and solve a maze, packaged as a reusable standalone class.

    Example usage::

        from mazegen import MazeGenerator

        gen = MazeGenerator(width=20, height=15, seed=42)
        gen.generate()
        grid = gen.get_grid()
        path = gen.get_solution()  # list of 'N'/'E'/'S'/'W' or None
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        perfect: bool = True,
        entry: tuple[int, int] | None = None,
        exit_pos: tuple[int, int] | None = None,
    ) -> None:
        """Initialise the generator (does not generate yet).

        Args:
            width: Number of columns in the maze (>= 2).
            height: Number of rows in the maze (>= 2).
            seed: Optional RNG seed for reproducible mazes.
            perfect: If True, generate a perfect maze (single path).
                     If False, add extra passages to create loops.
            entry: (col, row) of the entry cell; defaults to (0, 0).
            exit_pos: (col, row) of the exit cell; defaults to
                      (width-1, height-1).
        """
        if width < 2 or height < 2:
            raise ValueError(
                f"Width and height must be >= 2, got {width}x{height}"
            )
        self._width = width
        self._height = height
        self._seed = seed
        self._perfect = perfect
        self._entry: tuple[int, int] = entry if entry is not None else (0, 0)
        self._exit_pos: tuple[int, int] = (
            exit_pos if exit_pos is not None else (width - 1, height - 1)
        )
        self._grid: list[list[int]] | None = None
        self._solution: list[str] | None = None
        self._solved: bool = False

    def generate(self) -> None:
        """Generate the maze and solve it (computes the shortest path).

        Applies the '42' pattern (if the maze is large enough), then runs
        the Recursive Backtracker DFS, then solves with BFS.
        """
        self._grid = [
            [ALL_WALLS] * self._width for _ in range(self._height)
        ]
        pattern = _compute_pattern_cells(self._width, self._height)
        reserved: set[tuple[int, int]] = (
            set(pattern) if pattern is not None else set()
        )
        reserved.discard(self._entry)
        reserved.discard(self._exit_pos)
        rng = random.Random(self._seed)
        start_col, start_row = self._entry
        _run_dfs(
            self._grid, reserved,
            self._width, self._height,
            start_col, start_row, rng,
        )
        if not self._perfect:
            _add_extra_passages(
                self._grid, reserved,
                self._width, self._height, rng,
            )
        self._solution = _bfs(
            self._grid, self._width, self._height,
            self._entry, self._exit_pos,
        )
        self._solved = True

    def get_grid(self) -> list[list[int]]:
        """Return the generated maze as a 2D list of wall bitmasks (0-15).

        Each value encodes which walls are closed: bit0=N, bit1=E,
        bit2=S, bit3=W.

        Returns:
            A list of rows, each a list of integers.

        Raises:
            RuntimeError: If generate() has not been called yet.
        """
        if self._grid is None:
            raise RuntimeError("Call generate() before get_grid().")
        return self._grid

    def get_solution(self) -> list[str] | None:
        """Return the shortest path from entry to exit as direction letters.

        Returns:
            A list of 'N', 'E', 'S', 'W' strings, or None if unsolvable.

        Raises:
            RuntimeError: If generate() has not been called yet.
        """
        if not self._solved:
            raise RuntimeError("Call generate() before get_solution().")
        return self._solution

    def get_entry(self) -> tuple[int, int]:
        """Return the (col, row) position of the maze entry.

        Returns:
            A (col, row) tuple.
        """
        return self._entry

    def get_exit(self) -> tuple[int, int]:
        """Return the (col, row) position of the maze exit.

        Returns:
            A (col, row) tuple.
        """
        return self._exit_pos
