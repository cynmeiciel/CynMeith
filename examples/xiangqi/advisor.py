from cynmeith import Board, Piece
from cynmeith.utils import Coord

from .rules import in_palace


class Advisor(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        if not board.is_in_bounds(new_position):
            return False
        if not in_palace(new_position, self.side):
            return False
        return (
            self.position.is_diagonal(new_position)
            and self.position.chebyshev_to(new_position) == 1
        )
