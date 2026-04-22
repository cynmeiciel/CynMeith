from cynmeith import Board, Piece
from cynmeith.utils import Coord

from .rules import in_palace


class Advisor(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        if not in_palace(new_position, self.side):
            return False
        return (
            self.position.is_diagonal(new_position)
            and self.position.chebyshev_to(new_position) == 1
        )

    def iter_move_candidates(self, board: Board):
        deltas = (
            Coord(-1, -1),
            Coord(-1, 1),
            Coord(1, -1),
            Coord(1, 1),
        )
        for delta in deltas:
            position = self.position + delta
            if board.is_in_bounds(position):
                yield position
