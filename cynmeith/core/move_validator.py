from typing import TYPE_CHECKING

from ..utils import Coord, Move
from .piece import Piece

if TYPE_CHECKING:
    from .board import Board
    

    
class MoveValidator:
    """
    This class is responsible for determining whether a move is legal based on general game rules that apply to all pieces.
    
    This class is intended to be subclassed if users wish to implement custom move validation rules.
    """
    
    def __init__(self, board: "Board"):
        self.board = board 
        
    def validate_move(self, move: Move) -> bool:
        """
        Validate a move for a given piece.
        """
        piece = self.board.at(move.fr)
        new_position = move.to
        if not piece.is_valid_move(new_position, self.board):
            return False
        if not self.board.is_empty(new_position):
            return False
        
        return True
    
    def get_validated_moves(self, piece: Piece) -> list[Coord]:
        """
        Get the valid moves for a piece.
        """
        return [coord for coord in piece.get_valid_moves(self.board) if self.validate_move(Move(piece.position, coord))]