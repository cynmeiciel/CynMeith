from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Callable, Iterable

from cynmeith.core.game_systems import GameOutcome, WinCondition
from cynmeith.core.move_manager import MoveManager
from cynmeith.core.piece import Piece
from cynmeith.utils.aliases import Move, Side2
from cynmeith.utils.coord import Coord

if TYPE_CHECKING:
    from cynmeith.core.board import Board
    from cynmeith.core.game import Game


class BoardSimulation:
    """
    Lightweight board-like view used for royal-safety simulation.
    """

    def __init__(self, board: "Board") -> None:
        self.width = board.width
        self.height = board.height
        self.board = deepcopy(board.board)
        self.factory = board.factory

    def at(self, position: Coord) -> Piece | None:
        if not self.is_in_bounds(position):
            raise ValueError(f"Position out of bounds {position}")
        return self.board[position.r][position.c]

    def _set_at(self, position: Coord, piece: Piece | None) -> None:
        if not self.is_in_bounds(position):
            raise ValueError(f"Position out of bounds {position}")
        self.board[position.r][position.c] = piece

    def set_at(self, position: Coord, piece: Piece | None) -> None:
        self._set_at(position, piece)

    def _apply_move(self, move: Move, piece: Piece) -> None:
        self._set_at(move.start, None)
        self._set_at(move.end, piece)
        piece.move(move.end)

    def is_in_bounds(self, position: Coord) -> bool:
        return (
            position.r >= 0
            and position.r < self.height
            and position.c >= 0
            and position.c < self.width
        )

    def is_empty(self, position: Coord) -> bool:
        return self.at(position) is None

    def side_at(self, position: Coord) -> Side2 | None:
        piece = self.at(position)
        return piece.side if piece is not None else None

    def is_enemy(self, position: Coord, side: Side2) -> bool:
        enemy_side = self.side_at(position)
        if enemy_side is None:
            return False
        return enemy_side != side

    def is_allied(self, position: Coord, side: Side2) -> bool:
        return self.side_at(position) == side

    def iter_positions(self) -> Iterable[Coord]:
        for r in range(self.height):
            for c in range(self.width):
                yield Coord(r, c)

    def iter_enumerate(self) -> Iterable[tuple[Coord, Piece | None]]:
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece is not None:
                    yield Coord(r, c), piece

    def iter_positions_line(
        self,
        start: Coord,
        end: Coord,
        criteria: Callable[[Coord, Coord], bool] = Coord.is_omnidirectional,
    ) -> Iterable[Coord]:
        if not criteria(start, end):
            raise StopIteration
        direction = start.direction_unit(end)
        while start != end + direction:
            yield start
            start += direction

    def iter_positions_towards(self, start: Coord, direction: Coord) -> Iterable[Coord]:
        while self.is_in_bounds(start):
            yield start
            start += direction

    def is_empty_line(
        self,
        start: Coord,
        end: Coord,
        criteria: Callable[[Coord, Coord], bool] = Coord.is_omnidirectional,
    ) -> bool:
        if not criteria(start, end):
            return False
        for position in self.iter_positions_line(start, end, criteria):
            if position == start or position == end:
                continue
            if self.at(position) is not None:
                return False
        return True


class RoyalRuleset(ABC):
    """
    Defines attack detection and royal identity for checkmate-style games.
    """

    def __init__(self, royal_symbol: str) -> None:
        self.royal_symbol = royal_symbol.upper()

    def is_royal_piece(self, piece: Piece | None) -> bool:
        return piece is not None and piece.symbol.upper() == self.royal_symbol

    def royal_position(self, board: Any, side: Side2) -> Coord | None:
        for position, piece in board.iter_enumerate():
            if piece is None:
                continue
            if piece.side == side and self.is_royal_piece(piece):
                return position
        return None

    def is_royal_in_check(self, board: Any, side: Side2) -> bool:
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
    def is_square_attacked(self, board: Any, target: Coord, by_side: Side2) -> bool:
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
