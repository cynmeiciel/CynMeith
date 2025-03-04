from core.config import Config
from abc import ABC, abstractmethod
from utils.coord import Coord

class Piece(ABC):
    def __init__(self, side: bool, position: Coord):
        self.side: bool = side # "True" for white, "False" for black
        self.position: Coord = position
    
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
    
    @abstractmethod
    def is_valid_move(self, new_position: Coord) -> bool:
        pass
    
    def get_valid_moves(self) -> list[Coord]:
        valid_moves = []
        for x in range(8):
            for y in range(8):
                if self.is_valid_move(Coord(x, y)):
                    valid_moves.append(Coord(x, y))
        return valid_moves
    
    def move(self, new_position: Coord):
        self.position = new_position
        

