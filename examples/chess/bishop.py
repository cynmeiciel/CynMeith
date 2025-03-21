from cynmeith import Piece, Board
from cynmeith.utils import Coord

class Bishop(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        return board.is_empty_line(self.position, new_position, Coord.is_diagonal)