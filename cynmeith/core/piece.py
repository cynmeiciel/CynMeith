from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from warnings import warn

from cynmeith.utils.aliases import Side2
from cynmeith.utils.coord import Coord

if TYPE_CHECKING:
    from cynmeith.core.board import Board


class Piece(ABC):
    symbol = ""

    def __init__(self, side: Side2, position: Coord):
        self.side: Side2 = side  # "True" for white, "False" for black
        self.position: Coord = position

    def __str__(self) -> str:
        return f"{self.side} {self.__class__.__name__}"

    def __repr__(self) -> str:
        return f"{self.side} {self.__class__.__name__}@{self.position}"

    def get_symbol_with_side(self) -> str:
        if self.side:
            return self.symbol.upper()
        else:
            return self.symbol.lower()

    def move(self, new_position: Coord) -> None:
        """
        Move the piece to a new position.

        This should be overridden to update the piece's internal state, if necessary.
        """
        self.position = new_position

    @abstractmethod
    def is_valid_move(self, new_position: Coord, board: "Board") -> bool:
        pass

    def get_valid_moves(self, board: "Board") -> list[Coord]:
        """
        Get the valid moves for the piece.

        Although this default implementation works, this should be overridden to improve performance since it iterates over the entire board, and some pieces might not need `is_valid_move`.
        However, you must implement `is_valid_move` and use this method first to ensure your piece is working correctly.
        """
        warn(
            f"This is the default implementation of get_valid_moves at {self.__class__.__name__}.\n Overriding this method is recommended."
        )
        valid_moves = []
        for position in board.iter_positions():
            if self.is_valid_move(position, board):
                valid_moves.append(position)
        return valid_moves
