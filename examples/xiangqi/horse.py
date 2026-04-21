from cynmeith import Board, Piece
from cynmeith.utils import Coord


class Horse(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        if not board.is_in_bounds(new_position):
            return False
        dr = new_position.r - self.position.r
        dc = new_position.c - self.position.c
        if not ((abs(dr) == 2 and abs(dc) == 1) or (abs(dr) == 1 and abs(dc) == 2)):
            return False

        if abs(dr) == 2:
            leg = Coord(self.position.r + dr // 2, self.position.c)
        else:
            leg = Coord(self.position.r, self.position.c + dc // 2)
        return board.is_empty(leg)
