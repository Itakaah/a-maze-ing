"""Tests for src/pattern_42.py."""

from src.maze_model import ALL_WALLS, MazeGrid
from src.pattern_42 import (
    MIN_MAZE_HEIGHT,
    MIN_MAZE_WIDTH,
    apply_pattern_42,
    get_pattern_cells,
)


class TestGetPatternCells:
    """Tests for get_pattern_cells."""

    def test_returns_none_if_too_small(self) -> None:
        """Should return None when the maze is too small for the pattern."""
        assert get_pattern_cells(1, 1) is None
        assert get_pattern_cells(MIN_MAZE_WIDTH - 1, MIN_MAZE_HEIGHT) is None
        assert get_pattern_cells(MIN_MAZE_WIDTH, MIN_MAZE_HEIGHT - 1) is None

    def test_returns_list_when_large_enough(self) -> None:
        """Should return a non-empty list for a maze that is large enough."""
        cells = get_pattern_cells(MIN_MAZE_WIDTH, MIN_MAZE_HEIGHT)
        assert cells is not None
        assert len(cells) > 0

    def test_cells_within_bounds(self) -> None:
        """All returned positions must be inside the maze boundaries."""
        width, height = 20, 15
        cells = get_pattern_cells(width, height)
        assert cells is not None
        for col, row in cells:
            assert 0 <= col < width
            assert 0 <= row < height


class TestApplyPattern42:
    """Tests for apply_pattern_42."""

    def test_small_maze_returns_false(self) -> None:
        """Should return False without modifying the grid for small mazes."""
        grid = MazeGrid(2, 2, (0, 0), (1, 1))
        result = apply_pattern_42(grid)
        assert result is False

    def test_large_maze_returns_true(self) -> None:
        """Should return True and mark cells as reserved."""
        grid = MazeGrid(20, 15, (0, 0), (19, 14))
        result = apply_pattern_42(grid)
        assert result is True

    def test_reserved_cells_have_all_walls(self) -> None:
        """Reserved cells should keep walls = ALL_WALLS."""
        grid = MazeGrid(20, 15, (0, 0), (19, 14))
        apply_pattern_42(grid)
        reserved_count = 0
        for row in range(grid.height):
            for col in range(grid.width):
                cell = grid.get_cell(col, row)
                if cell.reserved:
                    assert cell.walls == ALL_WALLS
                    reserved_count += 1
        assert reserved_count > 0

    def test_no_reserved_cells_if_too_small(self) -> None:
        """No cell should be marked reserved when the maze is too small."""
        grid = MazeGrid(2, 2, (0, 0), (1, 1))
        apply_pattern_42(grid)
        for row in range(grid.height):
            for col in range(grid.width):
                assert not grid.get_cell(col, row).reserved
