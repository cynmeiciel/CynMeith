from pathlib import Path

from examples.ui.spec import BoardTheme, GameSpec

from .chess_manager import ChessManager


def build_game_spec() -> GameSpec:
    return GameSpec(
        title="Chess",
        config_path=Path(__file__).with_name("chess.yaml"),
        move_manager=ChessManager,
        theme=BoardTheme(
            light_color="#f7f1e3",
            dark_color="#b08d57",
            highlight_color="#ffe066",
            selected_color="#3a86ff",
            piece_color_true="#111111",
            piece_color_false="#7f1d1d",
        ),
        status_hint="Chess: click a piece, then a highlighted target square.",
    )
