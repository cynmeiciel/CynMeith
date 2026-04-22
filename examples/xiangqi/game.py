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

from .royal_rules import XIANGQI_ROYAL_RULES
from .xiangqi_manager import XiangqiManager

XIANGQI_MATERIAL_VALUES = {
    "G": 0,
    "A": 2,
    "E": 2,
    "H": 4,
    "R": 9,
    "C": 4,
    "S": 1,
}


def _build_xiangqi_config_data() -> dict:
    return {
        "pieces": {
            "General": {
                "symbol": "G",
                "class_path": "examples.xiangqi.general",
            },
            "Advisor": {
                "symbol": "A",
                "class_path": "examples.xiangqi.advisor",
            },
            "Elephant": {
                "symbol": "E",
                "class_path": "examples.xiangqi.elephant",
            },
            "Horse": {"symbol": "H", "class_path": "examples.xiangqi.horse"},
            "Chariot": {
                "symbol": "R",
                "class_path": "examples.xiangqi.chariot",
            },
            "Cannon": {
                "symbol": "C",
                "class_path": "examples.xiangqi.cannon",
            },
            "Soldier": {
                "symbol": "S",
                "class_path": "examples.xiangqi.soldier",
            },
        },
        "width": 9,
        "height": 10,
        "fen": "rheagaehr/9/1c5c1/s1s1s1s1s/9/9/S1S1S1S1S/1C5C1/9/RHEAGAEHR",
    }


def _build_config(config_source: Literal["yaml", "data"]) -> Config:
    if config_source == "data":
        return Config.from_data(_build_xiangqi_config_data())
    return Config.from_file(Path(__file__).with_name("xiangqi.yaml"))


def _build_win_conditions() -> list:
    return [
        RoyalCheckmateCondition(XIANGQI_ROYAL_RULES, reason="Checkmate."),
        RoyalStalemateCondition(
            XIANGQI_ROYAL_RULES,
            kind="win",
            reason="No legal moves.",
        ),
    ]


def _build_scoring_system() -> MaterialScoreSystem:
    return MaterialScoreSystem(XIANGQI_MATERIAL_VALUES)


def build_game_spec(config_source: Literal["yaml", "data"] = "yaml") -> GameSpec:
    return GameSpec(
        title="Xiangqi",
        create_game=lambda: Game(
            _build_config(config_source),
            XiangqiManager,
            turn_policy=QuotaTurnPolicy(moves_per_turn=1),
            scoring_system=_build_scoring_system(),
            win_conditions=_build_win_conditions(),
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
        status_hint=(
            "Xiangqi standard turns with material scoring. "
            f"Checkmate wins and stalemate loses. Config: {config_source}."
        ),
    )
