from .piece import Piece
from utils import Coord

class Pawn(Piece):
    def __init__(self, color: str, position: Coord):
        super().__init__(color, position)
        self.has_moved = False
    
    def is_valid_move(self, new_position: Coord) -> bool:
        return self.position.is_forward(new_position, self.side)
    
    def move(self, new_position: Coord) -> None:
        self.position = new_position
        self.has_moved = True
        return None