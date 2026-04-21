from pathlib import Path

from cynmeith import Config, Game, QuotaTurnPolicy
from examples.ui.spec import BoardTheme, GameSpec

from .chess_manager import ChessManager


def build_game_spec() -> GameSpec:
    return GameSpec(
        title="Chess",
        create_game=lambda: Game(
            Config.from_file(Path(__file__).with_name("chess.yaml")),
            ChessManager,
            turn_policy=QuotaTurnPolicy(moves_per_turn=1),
        ),
        theme=BoardTheme(
            light_color="#f7f1e3",
            dark_color="#b08d57",
            highlight_color="#ffe066",
            selected_color="#3a86ff",
            piece_color_true="#111111",
            piece_color_false="#7f1d1d",
        ),
        status_hint="Chess standard mode: one move per turn.",
    )
