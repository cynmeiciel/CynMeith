from cynmeith import Piece, Board
from cynmeith.utils import Coord

class King(Piece):
    def __init__(self, color: str, position: Coord):
        super().__init__(color, position)
        
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        return self.position.is_adjacent(new_position)