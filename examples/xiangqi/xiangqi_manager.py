from cynmeith import RoyalSafetyMoveManager
from cynmeith.utils import Move

from .royal_rules import XIANGQI_ROYAL_RULES


class XiangqiManager(RoyalSafetyMoveManager):
    @property
    def royal_rules(self):
        return XIANGQI_ROYAL_RULES

    def resolve_move(self, move: Move) -> Move | None:
        piece = self.board.at(move.start)
        if piece is None:
            return None
        if self.board.is_allied(move.end, piece.side):
            return None
        if self._targets_enemy_royal(move, piece.side):
            return None

        if not piece.is_valid_move(move.end, self.board):
            return None
        if not self._is_royal_safe_after_move(move, piece.side):
            return None

        return move
