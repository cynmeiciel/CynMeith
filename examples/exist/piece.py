from cynmeith import Board, Piece
from cynmeith.utils import Coord


class ExistPiece(Piece):
    """
    In Exist, all pieces are identical and can move to any adjacent square
    (orthogonal or diagonal). The capture logic and restrictions are handled
    by the ExistManager, not by piece rules.
    """

    symbol = "X"

    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        """
        Basic check: is the target adjacent and different color allowed?
        Actual validity (considering line/tile restrictions) is checked by ExistManager.
        """
        if not board.is_in_bounds(new_position):
            return False
        if board.is_allied(new_position, self.side):
            return False
        if self.position.chebyshev_to(new_position) != 1:
            return False
        return True

    def iter_move_candidates(self, board: Board):
        """
        Generate all 8 adjacent squares.
        """
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                position = self.position + Coord(dr, dc)
                if board.is_in_bounds(position) and board.is_empty(position):
                    yield position
