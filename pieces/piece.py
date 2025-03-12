from core.config import Config
from abc import ABC, abstractmethod
from utils.aliases import Coord, Side

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.board import Board

class Piece(ABC):
    def __init__(self, side: Side, position: Coord):
        self.side: bool = side # "True" for white, "False" for black
        self.position: Coord = position
        self.valid_moves: list[Coord] = [] # Cache for valid moves
     
    def __str__(self) -> str:
        return f"{self.get_side_str()} {self.__class__.__name__}"
    
    def __repr__(self) -> str:
        return f"{self.get_side_str()} {self.__class__.__name__} at {self.position}"
    
    def get_side_str(self) -> str:
        return "White" if self.side else "Black"
    
    def get_symbol(self, config: Config) -> str:
        symbol = config.get_piece_symbol(self.__class__.__name__)
        if self.side:
            return symbol.upper()
        else:    
            return symbol.lower()
    
    def is_white(self) -> bool:
        return self.side
    
    def move(self, new_position: Coord):
        self.position = new_position
    
    ### RULES
    
    @abstractmethod
    def is_valid_move(self, new_position: Coord, board: "Board") -> bool:
        pass
    
    def get_valid_moves(self, board: "Board") -> list[Coord]:
        valid_moves = []
        for x in range(8):
            for y in range(8):
                if self.is_valid_move(Coord(x, y), board):
                    valid_moves.append(Coord(x, y))
        return valid_moves
    
    def update_valid_moves(self, board: "Board"):
        self.valid_moves = self.get_valid_moves(board)