from cynmeith import Board, Piece
from cynmeith.utils import Coord


class Elephant(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        if not self.position.is_diagonal(new_position):
            return False
        if self.position.chebyshev_to(new_position) != 2:
            return False

        if self.side and new_position.r > 4:
            return False
        if not self.side and new_position.r < 5:
            return False

        middle = Coord(
            (self.position.r + new_position.r) // 2,
            (self.position.c + new_position.c) // 2,
        )
        return board.is_empty(middle)

    def iter_move_candidates(self, board: Board):
        deltas = (
            Coord(-2, -2),
            Coord(-2, 2),
            Coord(2, -2),
            Coord(2, 2),
        )
        for delta in deltas:
            position = self.position + delta
            if board.is_in_bounds(position):
                yield position
