from dataclasses import dataclass

@dataclass
class MazeConfig:
    """Validated configuration of the labyrinth.

    Attributes:
        width: Width of the maze.
        height: Height of the maze.
        entry_pos: Coords of the entry point.
        exit_pos: Coords of the exit.
        output_file: File containing the encoded maze.
        perfect: Wether the maze is perfect or not.
        seed: Random number to always generate the same maze.
    """
    width: int
    height: int
    entry_pos: tuple[int, int]
    exit_pos: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def parse_config_file(path: str) -> dict[str, str]:
    """Reads a configuration file and returns key-value pairs as a dictionary.

    Args:
        path: The path to the config file

    Returns:
        A dict that has the name of the parameter for key and its value.

    Raises:
        FileNotFoundError: When the file path doesn't exist.
    """
    res: dict[str, str] = {}

    try:
        with open(path, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith("#"):
                    continue
                if line == "":
                    continue
                tmp: list[str] = line.split("=", 1)
                if len(tmp) != 2:
                    continue
                res[tmp[0]] = tmp[1]
    except FileNotFoundError as e:
        raise FileNotFoundError(e)
    
    return res


def validate_and_build_config(brut_dict: dict[str, str]) -> MazeConfig:
    """Creates and returns a MazeConfig from a dict with all args.

    Args:
        brut_dict: The dict that contains all args in the config file

    Returns:
        A MazeConfig with all the values from config file.

    Raises:
        ValueError: When the arg values are wrong.
    """
    arg_list: list[str] = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
        ]
    
    for i in arg_list:
        if i not in brut_dict:
            raise ValueError(f"Missing key in the config file : {i}")
    
    try:
        width: int = int(brut_dict["WIDTH"])
    except ValueError:
        raise ValueError(
            f"WIDTH must be an integer, got '{brut_dict['WIDTH']}'"
        )

    try:
        height: int = int(brut_dict["HEIGHT"])
    except ValueError:
        raise ValueError(
            f"HEIGHT must be an integer, got '{brut_dict['HEIGHT']}'"
        )

    try:
        entry_pos: tuple[int, int] = (
            int(brut_dict["ENTRY"].split(",")[0]),
            int(brut_dict["ENTRY"].split(",")[1])
        )
    except ValueError:
        raise ValueError(
            f"ENTRY must be two integers separated by a comma, "
            f"got {brut_dict['ENTRY']}"
        )

    try:
        exit_pos: tuple[int, int] = (
            int(brut_dict["EXIT"].split(",")[0]),
            int(brut_dict["EXIT"].split(",")[1])
        )
    except ValueError:
        raise ValueError(
            f"EXIT must be two integers separated by a comma, "
            f"got {brut_dict['EXIT']}"
        )
    
    output_file: str = brut_dict["OUTPUT_FILE"]
    perfect: bool = brut_dict["PERFECT"] == "True"

    if "SEED" in brut_dict:
        try:
            seed: int | None = int(brut_dict["SEED"])
        except ValueError:
            raise ValueError(
                f"SEED must be an integer, got {brut_dict['SEED']}"
            )
    else:
        seed: int | None = None

    return MazeConfig(
        width=width,
        height=height,
        entry_pos=entry_pos,
        exit_pos=exit_pos,
        output_file=output_file,
        perfect=perfect,
        seed=seed
    )


def load_config(path: str) -> MazeConfig:
    """Parses the config file and create and returns a MazeConfig with the right
        values

    Args:
        path: The path to the config file

    Returns:
        The final MazeConfig with all the good values from config file.
    """
    brut_dict: dict[str, str] = parse_config_file(path)
    return validate_and_build_config(brut_dict)
