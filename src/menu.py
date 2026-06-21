import os
from dataclasses import dataclass

from src.config_parser import MazeConfig
from src.generation import generate_maze
from src.maze_model import MazeGrid
from src.output_writer import write_maze_output
from src.renderer import WALL_COLOR_NAMES, render_maze
from src.solver import path_to_cells, solve_maze

MENU_OPTIONS: str = "1: regen | 2: path | 3: color | 4: quit"
OPTION_REGEN: str = "1"
OPTION_PATH: str = "2"
OPTION_COLOR: str = "3"
OPTION_QUIT: str = "4"


@dataclass
class MazeState:
    """Holds the current display state of the maze session."""

    grid: MazeGrid
    path: list[str] | None
    path_cells: set[tuple[int, int]]
    show_path: bool
    wall_color_index: int
    config: MazeConfig


def _clear_screen() -> None:
    """Clear the terminal screen using the system clear command."""
    os.system("clear")


def _build_state(config: MazeConfig) -> MazeState:
    """Generate a new maze and build a fresh MazeState from it.

    Args:
        config: The maze configuration to use for generation.

    Returns:
        A MazeState with a freshly generated maze and its solution.
    """
    grid = generate_maze(config)
    path = solve_maze(grid, config.entry, config.exit_pos)
    cells = path_to_cells(config.entry, path) if path else set()
    try:
        write_maze_output(config.output_file, grid, path)
    except OSError as error:
        print(f"Warning: could not write output file: {error}")
    return MazeState(
        grid=grid,
        path=path,
        path_cells=cells,
        show_path=False,
        wall_color_index=0,
        config=config,
    )


def _display(state: MazeState) -> None:
    """Clear the screen and render the current maze state.

    Args:
        state: The current maze session state to display.
    """
    _clear_screen()
    print(render_maze(
        state.grid,
        state.path_cells,
        state.show_path,
        state.wall_color_index,
    ))
    color_name = WALL_COLOR_NAMES[
        state.wall_color_index % len(WALL_COLOR_NAMES)
    ]
    path_status = "visible" if state.show_path else "hidden"
    print(f"\nWall colour: {color_name} | Path: {path_status}")
    if state.path is None:
        print("No path from entry to exit was found.")
    else:
        print(f"Shortest path length: {len(state.path)} steps")
    print(f"\n{MENU_OPTIONS}")


def _handle_regen(state: MazeState) -> MazeState:
    """Regenerate the maze and return a new state.

    Args:
        state: The current state (provides config and colour preference).

    Returns:
        A new MazeState with a freshly generated maze.
    """
    new_state = _build_state(state.config)
    new_state.wall_color_index = state.wall_color_index
    new_state.show_path = state.show_path
    return new_state


def _handle_toggle_path(state: MazeState) -> MazeState:
    """Toggle the path visibility in the current state.

    Args:
        state: The current maze session state.

    Returns:
        The same state with show_path flipped.
    """
    state.show_path = not state.show_path
    return state


def _handle_change_color(state: MazeState) -> MazeState:
    """Cycle to the next wall colour in the current state.

    Args:
        state: The current maze session state.

    Returns:
        The same state with wall_color_index incremented.
    """
    state.wall_color_index += 1
    return state


def run_menu(config: MazeConfig) -> None:
    """Run the interactive maze menu loop until the user quits.

    Generates an initial maze, displays it, then reads one-character
    choices in a loop until option 4 (quit) is selected.

    Args:
        config: The maze configuration used for generation.
    """
    state = _build_state(config)
    while True:
        _display(state)
        try:
            choice = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if choice == OPTION_REGEN:
            state = _handle_regen(state)
        elif choice == OPTION_PATH:
            state = _handle_toggle_path(state)
        elif choice == OPTION_COLOR:
            state = _handle_change_color(state)
        elif choice == OPTION_QUIT:
            print("Goodbye!")
            break
        else:
            print(f"Unknown option '{choice}'. Press Enter to continue.")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                break
