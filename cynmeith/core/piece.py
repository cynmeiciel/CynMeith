from abc import ABC, abstractmethod

from .config import Config
from ..utils.aliases import Coord, Side2

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .board import Board

class Piece(ABC):
    symbol = ""
    
    def __init__(self, side: Side2, position: Coord):
        self.side: Side2 = side # "True" for white, "False" for black
        self.position: Coord = position
     
    def __str__(self) -> str:
        return f"{self.get_side_str()} {self.__class__.__name__}"
    
    def __repr__(self) -> str:
        return f"{self.get_side_str()} {self.__class__.__name__}@{self.position}"
    
    def get_symbol_with_side(self) -> str:
        if self.side:
            return self.symbol.upper()
        else:    
            return self.symbol.lower()
       
    def move(self, new_position: Coord):
        """
        Move the piece to a new position.
       
        This should be overridden to update the piece's internal state, if necessary.
        """
        self.position = new_position
    
    
    ### RULES    
    @abstractmethod
    def is_valid_move(self, new_position: Coord, board: "Board") -> bool:
        pass
    
    def get_valid_moves(self, board: "Board") -> list[Coord]:
        """
        Get the valid moves for the piece.
       
        This should be overridden to improve performance since it iterates over the entire board, and some pieces might not need `is_valid_move`.
        """
        valid_moves = []
        for coord in board.iter_positions():
            if self.is_valid_move(coord, board):
                valid_moves.append(coord)
        return valid_moves    
