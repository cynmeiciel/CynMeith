from cynmeith import Board, Piece
from cynmeith.utils import Coord

from .rules import pieces_between


class Cannon(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        if not self.position.is_orthogonal(new_position):
            return False

        between = pieces_between(board, self.position, new_position)
        target = board.at(new_position)
        if target is None:
            return between == 0
        return between == 1

    def iter_move_candidates(self, board: Board):
        for direction in (Coord.up(), Coord.down(), Coord.left(), Coord.right()):
            yield from board.iter_positions_towards(
                self.position + direction, direction
            )
