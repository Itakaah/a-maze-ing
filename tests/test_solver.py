"""Tests for src/solver.py — BFS maze solver."""

from src.config_parser import MazeConfig
from src.generation import generate_maze
from src.maze_model import MazeGrid
from src.solver import path_to_cells, solve_maze


def _make_config(
    width: int = 8,
    height: int = 8,
    seed: int = 0,
) -> MazeConfig:
    """Build a minimal MazeConfig for testing.

    Args:
        width: Maze width.
        height: Maze height.
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
        perfect=True,
        seed=seed,
    )


class TestSolveMaze:
    """Tests for solve_maze."""

    def test_finds_path_in_perfect_maze(self) -> None:
        """BFS must find a path in every perfect maze."""
        config = _make_config(seed=0)
        grid = generate_maze(config)
        path = solve_maze(grid, config.entry, config.exit_pos)
        assert path is not None

    def test_path_is_a_list_of_directions(self) -> None:
        """The path should only contain valid direction letters."""
        config = _make_config(seed=1)
        grid = generate_maze(config)
        path = solve_maze(grid, config.entry, config.exit_pos)
        assert path is not None
        valid_directions = {"N", "E", "S", "W"}
        for step in path:
            assert step in valid_directions

    def test_path_leads_to_exit(self) -> None:
        """Following the path from entry must reach the exit."""
        config = _make_config(seed=2)
        grid = generate_maze(config)
        path = solve_maze(grid, config.entry, config.exit_pos)
        assert path is not None
        delta = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
        col, row = config.entry
        for step in path:
            dc, dr = delta[step]
            col += dc
            row += dr
        assert (col, row) == config.exit_pos

    def test_path_follows_open_walls(self) -> None:
        """Each step of the path must go through an open wall."""
        from src.maze_model import (
            WALL_EAST,
            WALL_NORTH,
            WALL_SOUTH,
            WALL_WEST,
        )
        wall_for_direction = {
            "N": WALL_NORTH,
            "E": WALL_EAST,
            "S": WALL_SOUTH,
            "W": WALL_WEST,
        }
        delta = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
        config = _make_config(seed=3)
        grid = generate_maze(config)
        path = solve_maze(grid, config.entry, config.exit_pos)
        assert path is not None
        col, row = config.entry
        for step in path:
            wall = wall_for_direction[step]
            assert not grid.get_cell(col, row).has_wall(wall)
            dc, dr = delta[step]
            col += dc
            row += dr

    def test_entry_equals_exit_returns_empty(self) -> None:
        """When entry and exit are the same, the path should be empty."""
        config = _make_config()
        grid = generate_maze(config)
        path = solve_maze(grid, config.entry, config.entry)
        assert path == []

    def test_returns_none_on_blocked_maze(self) -> None:
        """Returns None when entry and exit are completely separated."""
        grid = MazeGrid(2, 1, (0, 0), (1, 0))
        path = solve_maze(grid, (0, 0), (1, 0))
        assert path is None


class TestPathToCells:
    """Tests for path_to_cells."""

    def test_includes_entry(self) -> None:
        """The entry cell must be in the returned set."""
        cells = path_to_cells((0, 0), ["E", "S"])
        assert (0, 0) in cells

    def test_correct_cells_for_path(self) -> None:
        """All cells visited along the path must be present."""
        cells = path_to_cells((0, 0), ["E", "E", "S"])
        assert (0, 0) in cells
        assert (1, 0) in cells
        assert (2, 0) in cells
        assert (2, 1) in cells

    def test_empty_path_returns_entry_only(self) -> None:
        """An empty path should return a set with just the entry."""
        cells = path_to_cells((3, 4), [])
        assert cells == {(3, 4)}
