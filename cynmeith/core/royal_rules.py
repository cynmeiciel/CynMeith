from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from cynmeith.core.board import BoardLike, BoardSimulation
from cynmeith.core.game_systems import GameOutcome, WinCondition
from cynmeith.core.move_manager import MoveManager
from cynmeith.core.piece import Piece
from cynmeith.utils.aliases import Move, Side2
from cynmeith.utils.coord import Coord

if TYPE_CHECKING:
    from cynmeith.core.game import Game


class RoyalRuleset(ABC):
    """
    Defines attack detection and royal identity for checkmate-style games.
    """

    def __init__(self, royal_symbol: str) -> None:
        self.royal_symbol = royal_symbol.upper()

    def is_royal_piece(self, piece: Piece | None) -> bool:
        return piece is not None and piece.symbol.upper() == self.royal_symbol

    def royal_position(self, board: BoardLike, side: Side2) -> Coord | None:
        for position, piece in board.iter_enumerate():
            if piece is None:
                continue
            if piece.side == side and self.is_royal_piece(piece):
                return position
        return None

    def is_royal_in_check(self, board: BoardLike, side: Side2) -> bool:
        position = self.royal_position(board, side)
        if position is None:
            return False
        return self.is_square_attacked(board, position, not side)

    def side_has_legal_move(self, game: "Game", side: Side2) -> bool:
        if game.current_side is not None and game.current_side != side:
            return False
        for piece in game.board.iter_pieces():
            if piece is None or piece.side != side:
                continue
            for coord in game.board.get_valid_moves(piece) or []:
                if game.can_move(piece.position, coord):
                    return True
        return False

    @abstractmethod
    def is_square_attacked(
        self, board: BoardLike, target: Coord, by_side: Side2
    ) -> bool:
        pass


class RoyalSafetyMoveManager(MoveManager, ABC):
    """
    Move manager helper that rejects moves exposing the moving side's royal piece.
    """

    @property
    @abstractmethod
    def royal_rules(self) -> RoyalRuleset:
        pass

    def _targets_enemy_royal(self, move: Move, side: Side2) -> bool:
        target_piece = self.board.at(move.end)
        return (
            target_piece is not None
            and target_piece.side != side
            and self.royal_rules.is_royal_piece(target_piece)
        )

    def _is_royal_safe_after_move(self, move: Move, side: Side2) -> bool:
        simulated_board = self._simulate_resolved_board(move)
        return not self.royal_rules.is_royal_in_check(simulated_board, side)

    def _simulate_resolved_board(self, move: Move) -> BoardSimulation:
        simulated_board = BoardSimulation(self.board)
        simulated_piece = simulated_board.at(move.start)
        if simulated_piece is None:
            raise ValueError(f"No simulated piece at {move.start}")

        extra = self._build_extra_info(move)
        move_actor = bool(extra.get("move_actor", True))

        if move_actor:
            simulated_board._apply_move(move, simulated_piece)

        for effect in self._build_effects(move):
            effect.apply(simulated_board, move, simulated_piece)

        return simulated_board


class RoyalCheckmateCondition(WinCondition):
    """
    Declares a win when the active side is in check and has no legal moves.
    """

    def __init__(
        self,
        royal_rules: RoyalRuleset,
        kind: str = "win",
        reason: str | None = None,
    ) -> None:
        self.royal_rules = royal_rules
        self.kind = kind
        self.reason = reason

    def evaluate(self, game: "Game") -> GameOutcome | None:
        side = game.current_side
        if side is None:
            return None
        if not self.royal_rules.is_royal_in_check(game.board, side):
            return None
        if self.royal_rules.side_has_legal_move(game, side):
            return None

        reason = self.reason or f"Side {side} is checkmated."
        return GameOutcome(not side, self.kind, reason)


class RoyalStalemateCondition(WinCondition):
    """
    Declares an outcome when the active side has no legal moves and is not in check.
    """

    def __init__(
        self,
        royal_rules: RoyalRuleset,
        kind: str = "draw",
        winner: Side2 | None = None,
        reason: str | None = None,
    ) -> None:
        self.royal_rules = royal_rules
        self.kind = kind
        self.winner = winner
        self.reason = reason

    def evaluate(self, game: "Game") -> GameOutcome | None:
        side = game.current_side
        if side is None:
            return None
        if self.royal_rules.is_royal_in_check(game.board, side):
            return None
        if self.royal_rules.side_has_legal_move(game, side):
            return None

        winner = self.winner
        if winner is None and self.kind != "draw":
            winner = not side

        reason = self.reason or f"Side {side} has no legal moves."
        return GameOutcome(winner, self.kind, reason)
