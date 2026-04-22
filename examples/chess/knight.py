from cynmeith import Board, Piece
from cynmeith.utils import Coord


class Knight(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        return self.position.is_lshape(new_position)

    def iter_move_candidates(self, board: Board):
        deltas = (
            Coord(-2, -1),
            Coord(-2, 1),
            Coord(-1, -2),
            Coord(-1, 2),
            Coord(1, -2),
            Coord(1, 2),
            Coord(2, -1),
            Coord(2, 1),
        )
        for delta in deltas:
            position = self.position + delta
            if board.is_in_bounds(position):
                yield position
