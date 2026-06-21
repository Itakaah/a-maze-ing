"""Tests for src/output_writer.py — output file format."""

import os

import pytest

from src.config_parser import MazeConfig
from src.generation import generate_maze
from src.output_writer import (
    NO_PATH_MARKER,
    grid_to_hex_lines,
    path_to_string,
    write_maze_output,
)
from src.solver import solve_maze


def _make_config(width: int = 6, height: int = 6) -> MazeConfig:
    """Build a minimal config for a small test maze.

    Args:
        width: Maze width.
        height: Maze height.

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
        seed=5,
    )


class TestGridToHexLines:
    """Tests for grid_to_hex_lines."""

    def test_correct_number_of_lines(self) -> None:
        """Should produce one line per maze row."""
        config = _make_config()
        grid = generate_maze(config)
        lines = grid_to_hex_lines(grid)
        assert len(lines) == grid.height

    def test_correct_line_length(self) -> None:
        """Each line should contain exactly width hex characters."""
        config = _make_config(width=8, height=4)
        grid = generate_maze(config)
        for line in grid_to_hex_lines(grid):
            assert len(line) == 8

    def test_only_valid_hex_characters(self) -> None:
        """Each character should be a valid lowercase hex digit (0-9, a-f)."""
        config = _make_config()
        grid = generate_maze(config)
        valid_chars = set("0123456789abcdef")
        for line in grid_to_hex_lines(grid):
            for char in line:
                assert char in valid_chars


class TestPathToString:
    """Tests for path_to_string."""

    def test_valid_path(self) -> None:
        """A list of directions should be joined without separators."""
        assert path_to_string(["N", "E", "S", "W"]) == "NESW"

    def test_empty_path(self) -> None:
        """An empty path list should return an empty string."""
        assert path_to_string([]) == ""

    def test_none_path(self) -> None:
        """None should return the NO_PATH_MARKER constant."""
        assert path_to_string(None) == NO_PATH_MARKER


class TestWriteMazeOutput:
    """Tests for write_maze_output."""

    def test_creates_file(self, tmp_path: pytest.TempPathFactory) -> None:
        """The output file must be created."""
        filepath = str(tmp_path / "maze.txt")  # type: ignore[operator]
        config = _make_config()
        grid = generate_maze(config)
        path = solve_maze(grid, config.entry, config.exit_pos)
        write_maze_output(filepath, grid, path)
        assert os.path.isfile(filepath)

    def test_file_format(self, tmp_path: pytest.TempPathFactory) -> None:
        """The file must follow the three-section format."""
        filepath = str(tmp_path / "maze.txt")  # type: ignore[operator]
        config = _make_config(width=4, height=4)
        grid = generate_maze(config)
        path = solve_maze(grid, config.entry, config.exit_pos)
        write_maze_output(filepath, grid, path)
        with open(filepath, "r", encoding="utf-8") as out:
            lines = out.readlines()
        assert len(lines) >= 7
        for line in lines:
            assert line.endswith("\n")
        hex_lines = lines[:4]
        for line in hex_lines:
            assert len(line.strip()) == 4
        assert lines[4] == "\n"
        assert lines[5].strip() == "0,0"
        assert lines[6].strip() == "3,3"
