from abc import ABC, abstractmethod
from utils.coord import Coord

class Piece(ABC):
    def __init__(self, side: bool, position: Coord):
        self.side = side # "True" for white, "False" for black
        self.position = position
    
    def __str__(self) -> str:
        return f"{self.side} {self.__class__.__name__} at {self.position}"
    
    def __repr__(self) -> str:
        return self.__str__()    
    
    def get_side_str(self) -> str:
        return "White" if self.side else "Black"
    
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
        

