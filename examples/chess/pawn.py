from cynmeith import Piece, Board
from cynmeith.utils import Coord

class Pawn(Piece):
    def __init__(self, color: str, position: Coord):
        super().__init__(color, position)
        self.distance = 2
    
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        if not self.position.is_forward(new_position, self.side):
            return False
        
        if board.is_empty_line(self.position, new_position, Coord.is_vertical) and self.position.manhattan_to(new_position) <= self.distance and board.is_empty(new_position):
            return True
        
        if self.position.is_diagonal(new_position) and self.position.chebyshev_to(new_position) == 1 and board.is_enemy(new_position, self.side):
            return True
        
        return False
        
        
    def move(self, new_position: Coord):
        self.position = new_position
        self.distance = 1