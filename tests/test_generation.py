"""Tests for src/generation.py — maze generation with DFS."""

from src.config_parser import MazeConfig
from src.generation import generate_maze
from src.maze_model import ALL_WALLS, MazeGrid
from src.maze_model import WALL_EAST, WALL_NORTH, WALL_SOUTH, WALL_WEST


def _make_config(
    width: int = 10,
    height: int = 10,
    perfect: bool = True,
    seed: int = 0,
) -> MazeConfig:
    """Build a minimal MazeConfig for testing.

    Args:
        width: Maze width.
        height: Maze height.
        perfect: Whether to generate a perfect maze.
        seed: RNG seed.

    Returns:
        A MazeConfig instance.
    """
    return MazeConfig(
        width=width,
        height=height,
        entry=(0, 0),
        exit_pos=(width - 1, height - 1),
        output_file="test_out.txt",
        perfect=perfect,
        seed=seed,
    )


def _walls_are_coherent(grid: MazeGrid) -> bool:
    """Check that every shared wall is consistent between adjacent cells.

    If cell A has an East wall open, its eastern neighbour must have
    its West wall open too.

    Args:
        grid: The maze grid to validate.

    Returns:
        True if all shared walls are consistent.
    """
    pairs = [
        (WALL_EAST, WALL_WEST, 1, 0),
        (WALL_SOUTH, WALL_NORTH, 0, 1),
    ]
    for row in range(grid.height):
        for col in range(grid.width):
            for wall_a, wall_b, dc, dr in pairs:
                n_col, n_row = col + dc, row + dr
                if not grid.is_valid(n_col, n_row):
                    continue
                cell_a = grid.get_cell(col, row)
                cell_b = grid.get_cell(n_col, n_row)
                if cell_a.has_wall(wall_a) != cell_b.has_wall(wall_b):
                    return False
    return True


def _all_non_reserved_reachable(
    grid: MazeGrid, entry: tuple[int, int]
) -> bool:
    """Check that every non-reserved cell is reachable from entry.

    Uses BFS through open walls.

    Args:
        grid: The maze grid.
        entry: Starting (col, row) for the BFS.

    Returns:
        True if all non-reserved cells are reachable from entry.
    """
    from collections import deque
    visited: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque([entry])
    visited.add(entry)
    moves = [
        (0, -1, WALL_NORTH),
        (1, 0, WALL_EAST),
        (0, 1, WALL_SOUTH),
        (-1, 0, WALL_WEST),
    ]
    while queue:
        col, row = queue.popleft()
        for dc, dr, wall in moves:
            nc, nr = col + dc, row + dr
            if not grid.is_valid(nc, nr):
                continue
            if grid.get_cell(col, row).has_wall(wall):
                continue
            if (nc, nr) in visited:
                continue
            visited.add((nc, nr))
            queue.append((nc, nr))
    for row in range(grid.height):
        for col in range(grid.width):
            if not grid.get_cell(col, row).reserved:
                if (col, row) not in visited:
                    return False
    return True


class TestGenerateMaze:
    """Tests for generate_maze."""

    def test_returns_maze_grid(self) -> None:
        """generate_maze should return a MazeGrid instance."""
        config = _make_config()
        grid = generate_maze(config)
        assert isinstance(grid, MazeGrid)

    def test_grid_dimensions(self) -> None:
        """The returned grid should have the correct dimensions."""
        config = _make_config(width=8, height=6)
        grid = generate_maze(config)
        assert grid.width == 8
        assert grid.height == 6

    def test_walls_are_coherent(self) -> None:
        """All shared walls must be consistent between adjacent cells."""
        config = _make_config(seed=7)
        grid = generate_maze(config)
        assert _walls_are_coherent(grid)

    def test_all_non_reserved_cells_reachable(self) -> None:
        """Every non-reserved cell must be reachable from the entry."""
        config = _make_config(seed=42)
        grid = generate_maze(config)
        assert _all_non_reserved_reachable(grid, config.entry)

    def test_reserved_cells_have_all_walls(self) -> None:
        """Reserved cells (pattern 42) must keep all walls closed."""
        config = _make_config(width=20, height=15, seed=1)
        grid = generate_maze(config)
        for row in range(grid.height):
            for col in range(grid.width):
                cell = grid.get_cell(col, row)
                if cell.reserved:
                    assert cell.walls == ALL_WALLS

    def test_reproducible_with_seed(self) -> None:
        """The same seed must produce the same maze."""
        config_a = _make_config(seed=99)
        config_b = _make_config(seed=99)
        grid_a = generate_maze(config_a)
        grid_b = generate_maze(config_b)
        for row in range(grid_a.height):
            for col in range(grid_a.width):
                assert (
                    grid_a.get_cell(col, row).walls
                    == grid_b.get_cell(col, row).walls
                )

    def test_different_seeds_differ(self) -> None:
        """Different seeds should generally produce different mazes."""
        grid_a = generate_maze(_make_config(seed=1))
        grid_b = generate_maze(_make_config(seed=2))
        walls_a = [
            grid_a.get_cell(col, row).walls
            for row in range(grid_a.height)
            for col in range(grid_a.width)
        ]
        walls_b = [
            grid_b.get_cell(col, row).walls
            for row in range(grid_b.height)
            for col in range(grid_b.width)
        ]
        assert walls_a != walls_b

    def test_perimeter_walls_closed(self) -> None:
        """The outer border cells must have closed walls on their edges."""
        config = _make_config(seed=5)
        grid = generate_maze(config)
        for col in range(grid.width):
            assert grid.get_cell(col, 0).has_wall(WALL_NORTH)
            assert grid.get_cell(col, grid.height - 1).has_wall(WALL_SOUTH)
        for row in range(grid.height):
            assert grid.get_cell(0, row).has_wall(WALL_WEST)
            assert grid.get_cell(grid.width - 1, row).has_wall(WALL_EAST)
