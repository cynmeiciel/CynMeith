from core.piece import Piece
from utils import Coord

class Queen(Piece):
    def __init__(self, color: str, position: Coord):
        super().__init__(color, position)
        
    def is_valid_move(self, new_position: Coord, board) -> bool:
        return self.position.is_queen_move(new_position)
