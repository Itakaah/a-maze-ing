"""Tests for src/config_parser.py."""

import pytest

from src.config_parser import (
    ConfigError,
    MazeConfig,
    parse_config,
    parse_coordinate,
    parse_line,
    validate_config_values,
)


class TestParseLine:
    """Tests for the parse_line helper."""

    def test_blank_line_returns_none(self) -> None:
        """Blank lines should be ignored."""
        assert parse_line("") is None
        assert parse_line("   ") is None

    def test_comment_line_returns_none(self) -> None:
        """Lines starting with '#' should be ignored."""
        assert parse_line("# comment") is None
        assert parse_line("  # another") is None

    def test_valid_key_value(self) -> None:
        """A 'KEY=VALUE' line should return a (key, value) tuple."""
        result = parse_line("WIDTH=20")
        assert result == ("WIDTH", "20")

    def test_strips_whitespace(self) -> None:
        """Keys and values should have surrounding whitespace removed."""
        result = parse_line("  HEIGHT = 15  ")
        assert result == ("HEIGHT", "15")

    def test_missing_equals_raises(self) -> None:
        """Lines without '=' should raise ConfigError."""
        with pytest.raises(ConfigError):
            parse_line("BADLINE")


class TestParseCoordinate:
    """Tests for the parse_coordinate helper."""

    def test_valid_coordinate(self) -> None:
        """'x,y' format should return an integer tuple."""
        assert parse_coordinate("0,0", "ENTRY") == (0, 0)
        assert parse_coordinate("19,14", "EXIT") == (19, 14)

    def test_with_spaces(self) -> None:
        """Spaces around the comma should be tolerated."""
        assert parse_coordinate("1 , 2", "ENTRY") == (1, 2)

    def test_non_integer_raises(self) -> None:
        """Non-integer values should raise ConfigError."""
        with pytest.raises(ConfigError):
            parse_coordinate("a,b", "ENTRY")

    def test_wrong_format_raises(self) -> None:
        """Missing comma should raise ConfigError."""
        with pytest.raises(ConfigError):
            parse_coordinate("10", "EXIT")

    def test_negative_raises(self) -> None:
        """Negative coordinates should raise ConfigError."""
        with pytest.raises(ConfigError):
            parse_coordinate("-1,0", "ENTRY")


class TestValidateConfigValues:
    """Tests for validate_config_values."""

    def _valid_raw(self) -> dict[str, str]:
        """Return a minimal valid config dict."""
        return {
            "WIDTH": "10",
            "HEIGHT": "10",
            "ENTRY": "0,0",
            "EXIT": "9,9",
            "OUTPUT_FILE": "out.txt",
            "PERFECT": "True",
        }

    def test_valid_config(self) -> None:
        """A complete valid config should produce a MazeConfig."""
        config = validate_config_values(self._valid_raw())
        assert isinstance(config, MazeConfig)
        assert config.width == 10
        assert config.height == 10
        assert config.entry == (0, 0)
        assert config.exit_pos == (9, 9)
        assert config.perfect is True
        assert config.seed is None

    def test_missing_key_raises(self) -> None:
        """Missing required keys should raise ConfigError."""
        raw = self._valid_raw()
        del raw["WIDTH"]
        with pytest.raises(ConfigError, match="Missing required keys"):
            validate_config_values(raw)

    def test_entry_outside_bounds_raises(self) -> None:
        """Entry outside maze bounds should raise ConfigError."""
        raw = self._valid_raw()
        raw["ENTRY"] = "10,0"
        with pytest.raises(ConfigError, match="ENTRY"):
            validate_config_values(raw)

    def test_entry_equals_exit_raises(self) -> None:
        """Identical entry and exit should raise ConfigError."""
        raw = self._valid_raw()
        raw["EXIT"] = "0,0"
        with pytest.raises(ConfigError, match="different"):
            validate_config_values(raw)

    def test_invalid_perfect_raises(self) -> None:
        """An unrecognised PERFECT value should raise ConfigError."""
        raw = self._valid_raw()
        raw["PERFECT"] = "yes"
        with pytest.raises(ConfigError, match="PERFECT"):
            validate_config_values(raw)

    def test_optional_seed(self) -> None:
        """A SEED key should be parsed into an integer."""
        raw = self._valid_raw()
        raw["SEED"] = "42"
        config = validate_config_values(raw)
        assert config.seed == 42

    def test_dimension_too_small_raises(self) -> None:
        """Width or height < 2 should raise ConfigError."""
        raw = self._valid_raw()
        raw["WIDTH"] = "1"
        with pytest.raises(ConfigError):
            validate_config_values(raw)


class TestParseConfig:
    """Tests for parse_config (reads a real file)."""

    def test_nonexistent_file_raises(self) -> None:
        """A missing file should raise ConfigError."""
        with pytest.raises(ConfigError, match="Cannot open"):
            parse_config("/nonexistent/path/config.txt")

    def test_valid_file(self, tmp_path: pytest.TempPathFactory) -> None:
        """A well-formed config file should parse successfully."""
        config_file = tmp_path / "config.txt"  # type: ignore[operator]
        config_file.write_text(
            "WIDTH=10\nHEIGHT=10\nENTRY=0,0\n"
            "EXIT=9,9\nOUTPUT_FILE=out.txt\nPERFECT=True\n"
        )
        config = parse_config(str(config_file))
        assert config.width == 10
        assert config.output_file == "out.txt"
