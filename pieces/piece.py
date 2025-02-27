from abc import ABC, abstractmethod
from utils.coord import Coord

class Piece(ABC):
    def __init__(self, color: str, position: Coord):
        self.color = color # "white" or "black"
        self.position = position
        
    @abstractmethod
    def is_valid_move(self, new_position: Coord) -> bool:
        pass
    
    @abstractmethod
    def get_valid_moves(self) -> list[Coord]:
        pass
    
    def move(self, new_position: Coord):
        self.position = new_position