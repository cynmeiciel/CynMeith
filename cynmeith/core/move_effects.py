from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from cynmeith.utils.coord import Coord

if TYPE_CHECKING:
    from cynmeith.core.board import Board
    from cynmeith.core.piece import Piece
    from cynmeith.utils.aliases import Move


class MoveEffect(ABC):
    """
    Side-effect unit executed after a move is applied.
    """

    @abstractmethod
    def apply(self, board: Board, move: Move, piece: Piece) -> None:
        pass


"""
This module defines reusable move effects and presets for common game actions like captures, promotions, and relocations.
Move effects are designed to be composable and can be used in custom move managers to implement complex move resolutions.
"""


@dataclass(frozen=True)
class RemovePieceEffect(MoveEffect):
    """
    Effect to remove a piece from the board, typically used for captures.

    Attributes:
        position: The coordinate of the piece to be removed.
    """

    position: Coord

    def apply(self, board: Board, move: Move, piece: Piece) -> None:
        board._set_at(self.position, None)


@dataclass(frozen=True)
class MovePieceEffect(MoveEffect):
    """
    Effect to move a piece from one coordinate to another, used for special moves that require additional relocations (e.g., castling).

    Attributes:
        start: The starting coordinate of the piece.
        end: The ending coordinate of the piece.
    """

    start: Coord
    end: Coord

    def apply(self, board: Board, move: Move, piece: Piece) -> None:
        moving_piece = board.at(self.start)
        if moving_piece is None:
            return
        board._set_at(self.start, None)
        board._set_at(self.end, moving_piece)
        moving_piece.move(self.end)


@dataclass(frozen=True)
class PromotePieceEffect(MoveEffect):
    """
    Effect to promote a piece to another type, typically used for pawn promotion in chess.
    Attributes:
        symbol: The symbol representing the piece to promote to (e.g., 'Q' for queen).
        position: The coordinate where the promotion occurs. If None, defaults to the move's end coordinate.
    """

    symbol: str
    position: Coord | None = None

    def apply(self, board: Board, move: Move, piece: Piece) -> None:
        target = self.position or move.end
        promotion_symbol = self.symbol.upper()
        if len(promotion_symbol) != 1:
            raise ValueError("Promotion symbol must be a single character.")
        final_symbol = promotion_symbol if piece.side else promotion_symbol.lower()
        promoted_piece = board.factory.create_piece(final_symbol, target)
        board._set_at(target, promoted_piece)


class EffectPresets:
    """
    Reusable effect builders for game-specific move managers.
    """

    @staticmethod
    def capture(position: Coord) -> list[MoveEffect]:
        return [RemovePieceEffect(position)]

    @staticmethod
    def captures(*positions: Coord) -> list[MoveEffect]:
        return [RemovePieceEffect(position) for position in positions]

    @staticmethod
    def relocate(start: Coord, end: Coord) -> list[MoveEffect]:
        return [MovePieceEffect(start, end)]

    @staticmethod
    def promote(symbol: str, position: Coord | None = None) -> list[MoveEffect]:
        return [PromotePieceEffect(symbol, position)]
