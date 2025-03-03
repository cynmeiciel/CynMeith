from .piece import Piece
from utils import Coord

class Queen(Piece):
    def __init__(self, color: str, position: Coord):
        super().__init__(color, position)
        
    def is_valid_move(self, new_position: Coord) -> bool:
        return new_position.x == self.position.x or new_position.y == self.position.y or abs(new_position.x - self.position.x) == abs(new_position.y - self.position.y)
