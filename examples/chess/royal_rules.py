from cynmeith import RoyalRuleset
from cynmeith.utils import Coord

from .king import King
from .pawn import Pawn


class ChessRoyalRules(RoyalRuleset):
    def __init__(self) -> None:
        super().__init__("K")

    def is_square_attacked(self, board, target: Coord, by_side: bool) -> bool:
        for position, piece in board.iter_enumerate():
            if piece is None or piece.side != by_side:
                continue

            if isinstance(piece, Pawn):
                dr = target.r - position.r
                dc = target.c - position.c
                expected = 1 if piece.side else -1
                if dr == expected and abs(dc) == 1:
                    return True
                continue

            if isinstance(piece, King):
                if piece.position.is_adjacent(target):
                    return True
                continue

            if piece.is_valid_move(target, board):
                return True

        return False


CHESS_ROYAL_RULES = ChessRoyalRules()
