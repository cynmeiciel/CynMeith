from typing import TYPE_CHECKING

from cynmeith.core.piece import Piece
from cynmeith.utils.aliases import Move
from cynmeith.utils.coord import Coord

if TYPE_CHECKING:
    from cynmeith.core.board import Board


class MoveManager:
    """
    This class is responsible for determining whether an move is legal based on general game rules that apply to all pieces.

    This class is intended to be subclassed if users wish to implement custom rules.
    """

    def __init__(self, board: "Board"):
        self.board = board

    def validate_move(self, move: Move) -> bool:
        """
        Validate a move for a given piece.
        """
        piece = self.board.at(move.start)
        if piece is None:
            return False
        new_position = move.end
        return piece.is_valid_move(new_position, self.board)

    def get_validated_moves(self, piece: Piece) -> list[Coord]:
        """
        Get the valid moves for a piece.
        """
        return [
            coord
            for coord in piece.get_valid_moves(self.board)
            if self.validate_move(Move(piece.position, coord))
        ]
