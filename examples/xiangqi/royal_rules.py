from cynmeith import RoyalRuleset
from cynmeith.core.board import Board
from cynmeith.utils import Coord

from .general import General


class XiangqiRoyalRules(RoyalRuleset):
    def __init__(self) -> None:
        super().__init__("G")

    def is_square_attacked(self, board: Board, target: Coord, by_side: bool) -> bool:
        for position, piece in board.iter_enumerate():
            if piece is None or piece.side != by_side:
                continue

            if isinstance(piece, General):
                if piece.position.manhattan_to(target) == 1:
                    return True
                if piece.position.c == target.c and board.is_empty_line(
                    piece.position, target, Coord.is_vertical
                ):
                    return True
                continue

            if piece.is_valid_move(target, board):
                return True

        return False


XIANGQI_ROYAL_RULES = XiangqiRoyalRules()
