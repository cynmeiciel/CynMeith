from cynmeith import Piece, Board
from cynmeith.utils import Coord

class Knight(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        return self.position.is_lshape(new_position)