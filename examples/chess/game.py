from pathlib import Path
from typing import Literal

from cynmeith import (
    Config,
    Game,
    MaterialScoreSystem,
    QuotaTurnPolicy,
    RoyalCheckmateCondition,
    RoyalStalemateCondition,
)
from examples.ui.spec import BoardTheme, GameSpec

from .chess_manager import ChessManager
from .royal_rules import CHESS_ROYAL_RULES

CHESS_MATERIAL_VALUES = {
    "P": 1,
    "N": 3,
    "B": 3,
    "R": 5,
    "Q": 9,
    "K": 0,
}


def _build_chess_config_data() -> dict:
    return {
        "pieces": {
            "Pawn": {"symbol": "P", "class_path": "examples.chess.pawn"},
            "Rook": {"symbol": "R", "class_path": "examples.chess.rook"},
            "Knight": {
                "symbol": "N",
                "class_path": "examples.chess.knight",
            },
            "Bishop": {
                "symbol": "B",
                "class_path": "examples.chess.bishop",
            },
            "Queen": {"symbol": "Q", "class_path": "examples.chess.queen"},
            "King": {"symbol": "K", "class_path": "examples.chess.king"},
        },
        "width": 8,
        "height": 8,
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
    }


def _build_config(config_source: Literal["yaml", "data"]) -> Config:
    if config_source == "data":
        return Config.from_data(_build_chess_config_data())
    return Config.from_file(Path(__file__).with_name("chess.yaml"))


def _build_win_conditions() -> list:
    return [
        RoyalCheckmateCondition(CHESS_ROYAL_RULES, reason="Checkmate."),
        RoyalStalemateCondition(CHESS_ROYAL_RULES, kind="draw", reason="Stalemate."),
    ]


def _build_scoring_system() -> MaterialScoreSystem:
    return MaterialScoreSystem(CHESS_MATERIAL_VALUES)


def build_game_spec(config_source: Literal["yaml", "data"] = "yaml") -> GameSpec:
    return GameSpec(
        title="Chess",
        create_game=lambda: Game(
            _build_config(config_source),
            ChessManager,
            turn_policy=QuotaTurnPolicy(moves_per_turn=1),
            scoring_system=_build_scoring_system(),
            win_conditions=_build_win_conditions(),
        ),
        theme=BoardTheme(
            light_color="#f7f1e3",
            dark_color="#b08d57",
            highlight_color="#ffe066",
            selected_color="#3a86ff",
            piece_color_true="#111111",
            piece_color_false="#7f1d1d",
        ),
        status_hint=(
            "Chess standard turns with material scoring. "
            f"Checkmate wins and stalemate draws. Config: {config_source}."
        ),
        promotion_choices=("Q", "R", "B", "N"),
        promotion_prompt="Choose promotion piece",
    )
