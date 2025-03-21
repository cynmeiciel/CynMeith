"""
Contains type aliases and dataclasses for the game.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

from cynmeith.utils.coord import Coord

if TYPE_CHECKING:
    from cynmeith.core.piece import Piece

Side2: TypeAlias = bool
S_FIRST = True
S_SECOND = False

SideN: TypeAlias = int

PieceSymbol: TypeAlias = str
PieceClass: TypeAlias = type["Piece"]
PieceName: TypeAlias = str

MoveType: TypeAlias = str  # "MOVE", "DROP", "PROMOTE", etc.


@dataclass(frozen=True)
class Move:
    """
    Represents a move from one position to another, with a `move_type` and `piece` field for extra information (promotion, drop, etc.).
    Supports null.
    """

    start: Coord = Coord.null()
    end: Coord = Coord.null()
    move_type: MoveType = ""
    extra_info = None  # For extra information, such as promotion piece, etc.

    @classmethod
    def null(cls) -> Move:
        return cls(Coord.null(), Coord.null())

    def __bool__(self) -> bool:
        return bool(self.start) and bool(self.end)


Ending: TypeAlias = str

FENStr: TypeAlias = str


### ERRORS
class InvalidMoveError(ValueError):
    """
    Raised when an invalid move is attempted.
    """


class PositionError(ValueError):
    """
    Raised when an invalid position is attempted.
    """


class PieceError(ValueError):
    """
    Raised when an invalid piece is attempted.
    """


class MoveHistoryError(IndexError):
    """
    Raised when an invalid move history operation is attempted.
    """


class FENError(ValueError):
    """
    Raised when an invalid FEN string is attempted.
    """
