import sys

from src.config_parser import ConfigError, parse_config
from src.menu import run_menu

USAGE_MESSAGE: str = "Usage: python3 a_maze_ing.py <config_file>"
EXIT_CODE_ERROR: int = 1


def main() -> None:
    """Parse the config file and launch the interactive maze session.

    Reads the config file path from the command-line arguments, parses
    and validates it, then enters the interactive menu loop.
    Exits with a non-zero status code on any unrecoverable error.
    """
    if len(sys.argv) != 2:
        print(USAGE_MESSAGE, file=sys.stderr)
        sys.exit(EXIT_CODE_ERROR)
    config_path = sys.argv[1]
    try:
        config = parse_config(config_path)
    except ConfigError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        sys.exit(EXIT_CODE_ERROR)
    try:
        run_menu(config)
    except Exception as error:
        print(f"Unexpected error: {error}", file=sys.stderr)
        sys.exit(EXIT_CODE_ERROR)


if __name__ == "__main__":
    main()
