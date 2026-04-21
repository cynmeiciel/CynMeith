from cynmeith import Board, Piece
from cynmeith.utils import Coord

from .rules import in_palace


class General(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        if not board.is_in_bounds(new_position):
            return False
        if not in_palace(new_position, self.side):
            return False
        return self.position.manhattan_to(
            new_position
        ) == 1 and self.position.is_orthogonal(new_position)
