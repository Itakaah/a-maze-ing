from dataclasses import dataclass


REQUIRED_KEYS: set[str] = {
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
}
MIN_DIMENSION: int = 2


class ConfigError(Exception):
    """Raised when the configuration file contains an error."""

    pass


@dataclass
class MazeConfig:
    """Holds all validated configuration values for maze generation."""

    width: int
    height: int
    entry: tuple[int, int]
    exit_pos: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None


def parse_coordinate(value: str, key: str) -> tuple[int, int]:
    """Parse a 'x,y' string into an integer coordinate tuple.

    Args:
        value: Raw string from config file (e.g. '0,14').
        key: Config key name, used in error messages.

    Returns:
        A tuple (x, y) of non-negative integers.

    Raises:
        ConfigError: If the format or values are invalid.
    """
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(
            f"{key} must be in 'x,y' format, got '{value}'"
        )
    try:
        x_coord = int(parts[0].strip())
        y_coord = int(parts[1].strip())
    except ValueError as error:
        raise ConfigError(
            f"{key} coordinates must be integers, got '{value}'"
        ) from error
    if x_coord < 0 or y_coord < 0:
        raise ConfigError(
            f"{key} coordinates must be >= 0, got ({x_coord},{y_coord})"
        )
    return (x_coord, y_coord)


def parse_line(line: str) -> tuple[str, str] | None:
    """Parse one config line into a (key, value) pair.

    Blank lines and comment lines (starting with '#') return None.

    Args:
        line: A single raw line from the config file.

    Returns:
        A (key, value) pair, or None for blank/comment lines.

    Raises:
        ConfigError: If the line is not blank, comment, or KEY=VALUE.
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if "=" not in stripped:
        raise ConfigError(
            f"Invalid line (missing '='): '{stripped}'"
        )
    key, _, value = stripped.partition("=")
    return (key.strip(), value.strip())


def validate_config_values(raw: dict[str, str]) -> MazeConfig:
    """Validate a dict of raw key/value strings and build a MazeConfig.

    Args:
        raw: Dictionary of config keys to their raw string values.

    Returns:
        A fully validated MazeConfig instance.

    Raises:
        ConfigError: If any required key is missing or any value is invalid.
    """
    missing = REQUIRED_KEYS - raw.keys()
    if missing:
        raise ConfigError(
            f"Missing required keys: {', '.join(sorted(missing))}"
        )
    try:
        width = int(raw["WIDTH"])
        height = int(raw["HEIGHT"])
    except ValueError as error:
        raise ConfigError(
            f"WIDTH and HEIGHT must be integers: {error}"
        ) from error
    if width < MIN_DIMENSION or height < MIN_DIMENSION:
        raise ConfigError(
            f"WIDTH and HEIGHT must be >= {MIN_DIMENSION},"
            f" got {width}x{height}"
        )
    entry = parse_coordinate(raw["ENTRY"], "ENTRY")
    exit_pos = parse_coordinate(raw["EXIT"], "EXIT")
    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ConfigError(
            f"ENTRY {entry} is outside maze bounds ({width}x{height})"
        )
    if not (0 <= exit_pos[0] < width and 0 <= exit_pos[1] < height):
        raise ConfigError(
            f"EXIT {exit_pos} is outside maze bounds ({width}x{height})"
        )
    if entry == exit_pos:
        raise ConfigError("ENTRY and EXIT must be different positions")
    perfect_str = raw["PERFECT"].strip().lower()
    if perfect_str not in ("true", "false"):
        raise ConfigError(
            f"PERFECT must be 'True' or 'False', got '{raw['PERFECT']}'"
        )
    perfect = perfect_str == "true"
    seed: int | None = None
    if "SEED" in raw:
        try:
            seed = int(raw["SEED"])
        except ValueError as error:
            raise ConfigError(
                f"SEED must be an integer: {error}"
            ) from error
    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit_pos=exit_pos,
        output_file=raw["OUTPUT_FILE"],
        perfect=perfect,
        seed=seed,
    )


def parse_config(filepath: str) -> MazeConfig:
    """Read and parse a maze configuration file.

    Args:
        filepath: Path to the config file (e.g. 'config.txt').

    Returns:
        A validated MazeConfig instance.

    Raises:
        ConfigError: If the file cannot be opened or contains errors.
    """
    raw: dict[str, str] = {}
    try:
        with open(filepath, "r", encoding="utf-8") as config_file:
            for line_number, line in enumerate(config_file, start=1):
                try:
                    parsed = parse_line(line)
                except ConfigError as error:
                    raise ConfigError(
                        f"Line {line_number}: {error}"
                    ) from error
                if parsed is not None:
                    key, value = parsed
                    raw[key] = value
    except OSError as error:
        raise ConfigError(
            f"Cannot open config file '{filepath}': {error}"
        ) from error
    return validate_config_values(raw)
