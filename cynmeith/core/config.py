from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from yaml import safe_load

from cynmeith.utils import ConfigError, PieceName


class Config:
    """
    Class for storing and interacting with configuration data.
    This class should only be used when initializing the game.
    """

    def __init__(self, source: str | Path | Mapping[str, Any] | "Config"):
        _data = self._normalize_source(source)
        self._validate_data(_data)
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

    @staticmethod
    def _validate_data(data: Mapping[str, Any]) -> None:
        required_keys = ("pieces", "width", "height", "fen")
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise ConfigError(f"Config is missing required field(s): {missing}")

        pieces = data["pieces"]
        if not isinstance(pieces, Mapping):
            raise ConfigError("Config field `pieces` must be a mapping.")

        width = data["width"]
        if isinstance(width, bool) or not isinstance(width, int) or width < 1:
            raise ConfigError("Config field `width` must be a positive integer.")

        height = data["height"]
        if isinstance(height, bool) or not isinstance(height, int) or height < 1:
            raise ConfigError("Config field `height` must be a positive integer.")

        fen = data["fen"]
        if not isinstance(fen, str) or not fen:
            raise ConfigError("Config field `fen` must be a non-empty string.")

        for piece_name, piece_info in pieces.items():
            if not isinstance(piece_name, str) or not piece_name:
                raise ConfigError("Piece names must be non-empty strings.")
            if not isinstance(piece_info, Mapping):
                raise ConfigError(f"Config for piece `{piece_name}` must be a mapping.")

            symbol = piece_info.get("symbol")
            if symbol is not None and (
                not isinstance(symbol, str) or not symbol.strip()
            ):
                raise ConfigError(
                    f"Piece `{piece_name}` has an invalid `symbol` value."
                )

            class_path = piece_info.get("class_path")
            if class_path is not None and (
                not isinstance(class_path, str) or not class_path.strip()
            ):
                raise ConfigError(
                    f"Piece `{piece_name}` has an invalid `class_path` value."
                )

    @classmethod
    def from_data(cls, data: Mapping[str, Any]) -> "Config":
        return cls(data)

    @classmethod
    def from_file(cls, config_path: str | Path) -> "Config":
        return cls(config_path)

    def get_piece_path(self, piece: PieceName) -> str:
        value = self.pieces[piece].get("class_path", piece.lower())
        assert isinstance(value, str)
        return value

    def get_piece_symbol(self, piece: PieceName) -> str:
        value = self.pieces[piece].get("symbol", piece[0].upper())
        assert isinstance(value, str)
        return value
