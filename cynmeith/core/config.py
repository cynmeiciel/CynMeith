from collections.abc import Mapping
from pathlib import Path
from typing import Any

from yaml import safe_load

from cynmeith.utils import PieceName


class Config:
    """
    Class for storing and interacting with configuration data.
    This class should only be used when initializing the game.
    """

    def __init__(self, source: str | Path | Mapping[str, Any] | "Config"):
        _data = self._normalize_source(source)
        self.pieces = _data["pieces"]
        self.width = _data["width"]
        self.height = _data["height"]
        self.fen = _data["fen"]

    @staticmethod
    def _normalize_source(
        source: str | Path | Mapping[str, Any] | "Config",
    ) -> dict[str, Any]:
        if isinstance(source, Config):
            return {
                "pieces": source.pieces,
                "width": source.width,
                "height": source.height,
                "fen": source.fen,
            }

        if isinstance(source, Mapping):
            return dict(source)

        with open(source, "r") as file:
            data = safe_load(file)
            if not isinstance(data, dict):
                raise TypeError("Config source must resolve to a mapping.")
            return data

    @classmethod
    def from_data(cls, data: Mapping[str, Any]) -> "Config":
        return cls(data)

    @classmethod
    def from_file(cls, config_path: str | Path) -> "Config":
        return cls(config_path)

    def get_piece_path(self, piece: PieceName) -> str:
        return self.pieces[piece].get("class_path", piece.lower())

    def get_piece_symbol(self, piece: PieceName) -> str:
        return self.pieces[piece].get("symbol", piece[0].upper())
