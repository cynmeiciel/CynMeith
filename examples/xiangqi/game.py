from pathlib import Path

from cynmeith import Config, FreeTurnPolicy, Game
from examples.ui.spec import BoardTheme, GameSpec

from .xiangqi_manager import XiangqiManager


def build_game_spec() -> GameSpec:
    return GameSpec(
        title="Xiangqi",
        create_game=lambda: Game(
            Config.from_file(Path(__file__).with_name("xiangqi.yaml")),
            XiangqiManager,
            turn_policy=FreeTurnPolicy(),
        ),
        theme=BoardTheme(
            light_color="#f5deb3",
            dark_color="#d2a679",
            highlight_color="#7dd3fc",
            selected_color="#0284c7",
            piece_color_true="#b00020",
            piece_color_false="#111111",
        ),
        show_river=True,
        status_hint="Xiangqi: river is shown, generals must stay in palace.",
    )
