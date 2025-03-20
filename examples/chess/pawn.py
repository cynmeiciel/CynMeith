from cynmeith import Piece, Board
from cynmeith.utils import Coord

class Pawn(Piece):
    def __init__(self, color: str, position: Coord):
        super().__init__(color, position)
        self.has_moved = False
    
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        return self.position.is_forward(new_position, self.side) and self.position.is_vertical(new_position) and self.position.manhattan_to(new_position) <= 2
    
    def move(self, new_position: Coord):
        self.position = new_position
        self.has_moved = True