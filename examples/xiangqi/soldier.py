from cynmeith import Board, Piece
from cynmeith.utils import Coord

from .rules import crossed_river


class Soldier(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        if not board.is_in_bounds(new_position):
            return False

        dr = new_position.r - self.position.r
        dc = new_position.c - self.position.c

        if self.side:
            if dr == 1 and dc == 0:
                return True
            if crossed_river(self.position, self.side) and dr == 0 and abs(dc) == 1:
                return True
            return False

        if dr == -1 and dc == 0:
            return True
        if crossed_river(self.position, self.side) and dr == 0 and abs(dc) == 1:
            return True
        return False

    def iter_move_candidates(self, board: Board):
        deltas = [Coord(1, 0) if self.side else Coord(-1, 0)]
        if crossed_river(self.position, self.side):
            deltas.extend([Coord(0, -1), Coord(0, 1)])
        for delta in deltas:
            position = self.position + delta
            if board.is_in_bounds(position):
                yield position
