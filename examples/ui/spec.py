from collections.abc import Callable
from dataclasses import dataclass

from cynmeith import Game


@dataclass(frozen=True)
class BoardTheme:
    light_color: str
    dark_color: str
    highlight_color: str
    selected_color: str
    piece_color_true: str
    piece_color_false: str
    board_line_color: str = "#2f2f2f"
    river_color: str = "#264653"


@dataclass(frozen=True)
class GameSpec:
    title: str
    create_game: Callable[[], Game]
    theme: BoardTheme
    show_river: bool = False
    status_hint: str = "Click a piece to select it."
