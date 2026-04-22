from pathlib import Path
from typing import Literal

from cynmeith import Config, Game, QuotaTurnPolicy
from examples.ui.spec import BoardTheme, GameSpec

from .xiangqi_manager import XiangqiManager


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


def build_game_spec(config_source: Literal["yaml", "data"] = "yaml") -> GameSpec:
    return GameSpec(
        title="Xiangqi",
        create_game=lambda: Game(
            _build_config(config_source),
            XiangqiManager,
            turn_policy=QuotaTurnPolicy(moves_per_turn=1),
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
            "Xiangqi standard turns: one move per side, river is shown, "
            f"generals must stay in palace. Config: {config_source}."
        ),
    )
