from cynmeith import Board, Piece
from cynmeith.utils import Coord


class Chariot(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        if not board.is_in_bounds(new_position):
            return False
        return self.position.is_orthogonal(new_position) and board.is_empty_line(
            self.position, new_position, Coord.is_orthogonal
        )
