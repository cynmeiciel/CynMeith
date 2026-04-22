from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from cynmeith.core.piece import Piece
from cynmeith.utils.aliases import Move, Side2
from cynmeith.utils.coord import Coord

if TYPE_CHECKING:
    from collections.abc import Mapping

    from cynmeith.core.game import Game


@dataclass(frozen=True)
class GameOutcome:
    """
    Represents the current outcome of a game.
    """

    winner: Side2 | None
    kind: str
    reason: str


class GameSystem(ABC):
    """
    Base class for game-level systems that need reset/snapshot support.
    """

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def snapshot(self) -> Any:
        pass

    @abstractmethod
    def restore(self, snapshot: Any) -> None:
        pass


class WinCondition(ABC):
    """
    Evaluates whether the game has reached a terminal state.
    """

    @abstractmethod
    def evaluate(self, game: "Game") -> GameOutcome | None:
        pass


class PhaseSystem(GameSystem):
    """
    Controls phase-specific move restrictions and phase progression.
    """

    @abstractmethod
    def can_move(self, game: "Game", piece: Piece, move: Move) -> bool:
        pass

    @abstractmethod
    def after_move(self, game: "Game", piece: Piece, move: Move) -> None:
        pass

    @property
    @abstractmethod
    def current_phase(self) -> str | None:
        pass


class ResourceSystem(GameSystem):
    """
    Tracks game-level resources that can restrict or react to moves.
    """

    @abstractmethod
    def can_move(self, game: "Game", piece: Piece, move: Move) -> bool:
        pass

    @abstractmethod
    def after_move(self, game: "Game", piece: Piece, move: Move) -> None:
        pass


class ScoringSystem(GameSystem):
    """
    Computes or tracks side scores.
    """

    @abstractmethod
    def get_scores(self, game: "Game") -> Mapping[Side2, int]:
        pass


class EliminatePieceCondition(WinCondition):
    """
    Ends the game when a matching piece type no longer exists.
    """

    def __init__(
        self,
        piece_symbol: str,
        side: Side2 | None = None,
        winner: Side2 | None = None,
        kind: str = "win",
        reason: str | None = None,
    ) -> None:
        self.piece_symbol = piece_symbol.upper()
        self.side = side
        self.winner = winner
        self.kind = kind
        self.reason = reason

    def evaluate(self, game: "Game") -> GameOutcome | None:
        for piece in game.board.iter_pieces():
            if piece is None:
                continue
            if piece.symbol.upper() != self.piece_symbol:
                continue
            if self.side is not None and piece.side != self.side:
                continue
            return None

        winner = self.winner
        if winner is None and self.side is not None:
            winner = not self.side

        reason = self.reason
        if reason is None:
            if self.side is None:
                reason = f"All `{self.piece_symbol}` pieces were eliminated."
            else:
                reason = (
                    f"Side {self.side} has no `{self.piece_symbol}` pieces remaining."
                )
        return GameOutcome(winner, self.kind, reason)


class ReachSquareCondition(WinCondition):
    """
    Ends the game when a side reaches a target coordinate.
    """

    def __init__(
        self,
        side: Side2,
        target: Coord,
        piece_symbol: str | None = None,
        winner: Side2 | None = None,
        kind: str = "win",
        reason: str | None = None,
    ) -> None:
        self.side = side
        self.target = target
        self.piece_symbol = piece_symbol.upper() if piece_symbol else None
        self.winner = winner if winner is not None else side
        self.kind = kind
        self.reason = reason

    def evaluate(self, game: "Game") -> GameOutcome | None:
        piece = game.board.at(self.target)
        if piece is None or piece.side != self.side:
            return None
        if self.piece_symbol is not None and piece.symbol.upper() != self.piece_symbol:
            return None

        reason = self.reason or f"Side {self.side} reached {self.target}."
        return GameOutcome(self.winner, self.kind, reason)


class NoLegalMovesCondition(WinCondition):
    """
    Ends the game when the tested side has no legal moves.
    """

    def __init__(
        self,
        side: Side2 | None = None,
        winner: Side2 | None = None,
        kind: str = "win",
        reason: str | None = None,
    ) -> None:
        self.side = side
        self.winner = winner
        self.kind = kind
        self.reason = reason

    def evaluate(self, game: "Game") -> GameOutcome | None:
        side = self.side if self.side is not None else game.current_side
        if side is None:
            return None
        if game.current_side is not None and side != game.current_side:
            return None

        for piece in game.board.iter_pieces():
            if piece is None or piece.side != side:
                continue
            for coord in game.board.get_valid_moves(piece) or []:
                if game.can_move(piece.position, coord):
                    return None

        winner = self.winner
        if winner is None:
            winner = not side

        reason = self.reason or f"Side {side} has no legal moves."
        return GameOutcome(winner, self.kind, reason)


class MoveLimitDrawCondition(WinCondition):
    """
    Declares a terminal outcome after a fixed number of recorded moves.
    """

    def __init__(
        self,
        move_limit: int,
        kind: str = "draw",
        winner: Side2 | None = None,
        reason: str | None = None,
    ) -> None:
        if move_limit < 1:
            raise ValueError("move_limit must be at least 1")
        self.move_limit = move_limit
        self.kind = kind
        self.winner = winner
        self.reason = reason

    def evaluate(self, game: "Game") -> GameOutcome | None:
        if game.board.history.num_moves < self.move_limit:
            return None
        reason = self.reason or f"Move limit {self.move_limit} reached."
        return GameOutcome(self.winner, self.kind, reason)


class StaticPhaseSystem(PhaseSystem):
    """
    Fixed phase name with no move restrictions.
    """

    def __init__(self, phase: str = "main") -> None:
        self.phase = phase

    def can_move(self, game: "Game", piece: Piece, move: Move) -> bool:
        return True

    def after_move(self, game: "Game", piece: Piece, move: Move) -> None:
        return None

    def reset(self) -> None:
        return None

    def snapshot(self) -> str:
        return self.phase

    def restore(self, snapshot: str) -> None:
        self.phase = snapshot

    @property
    def current_phase(self) -> str:
        return self.phase


class TurnCountPhaseSystem(PhaseSystem):
    """
    Changes phase after configured move-count thresholds.
    """

    def __init__(
        self, schedule: Mapping[int, str], initial_phase: str = "opening"
    ) -> None:
        normalized = sorted(schedule.items())
        for threshold, _phase in normalized:
            if threshold < 0:
                raise ValueError("Phase thresholds must be non-negative.")
        self.schedule = normalized
        self.initial_phase = initial_phase
        self._current_phase = initial_phase

    def can_move(self, game: "Game", piece: Piece, move: Move) -> bool:
        return True

    def after_move(self, game: "Game", piece: Piece, move: Move) -> None:
        self._current_phase = self._phase_for_count(game.board.history.num_moves)

    def reset(self) -> None:
        self._current_phase = self.initial_phase

    def snapshot(self) -> str:
        return self._current_phase

    def restore(self, snapshot: str) -> None:
        self._current_phase = snapshot

    @property
    def current_phase(self) -> str:
        return self._current_phase

    def _phase_for_count(self, move_count: int) -> str:
        phase = self.initial_phase
        for threshold, threshold_phase in self.schedule:
            if move_count >= threshold:
                phase = threshold_phase
            else:
                break
        return phase


class TwoStagePhaseSystem(TurnCountPhaseSystem):
    """
    Convenience phase system with one threshold and two named stages.
    """

    def __init__(
        self,
        switch_after_moves: int,
        opening_phase: str = "opening",
        later_phase: str = "battle",
    ) -> None:
        if switch_after_moves < 0:
            raise ValueError("switch_after_moves must be non-negative.")
        super().__init__({switch_after_moves: later_phase}, initial_phase=opening_phase)


class ActionPointSystem(ResourceSystem):
    """
    Per-side action points that refresh when the active side changes.
    """

    def __init__(self, points_per_turn: int = 1, starting_side: Side2 = True) -> None:
        if points_per_turn < 1:
            raise ValueError("points_per_turn must be at least 1")
        self.points_per_turn = points_per_turn
        self.starting_side = starting_side
        self.points_left: dict[Side2, int] = {}
        self._active_side: Side2 | None = None
        self.reset()

    def can_move(self, game: "Game", piece: Piece, move: Move) -> bool:
        self._sync_active_side(game)
        return self.points_left[piece.side] > 0

    def after_move(self, game: "Game", piece: Piece, move: Move) -> None:
        self._sync_active_side(game, moving_side=piece.side)
        self.points_left[piece.side] -= 1
        self._sync_active_side(game)

    def reset(self) -> None:
        self.points_left = {
            True: self.points_per_turn,
            False: self.points_per_turn,
        }
        self._active_side = self.starting_side

    def snapshot(self) -> tuple[dict[Side2, int], Side2 | None]:
        return dict(self.points_left), self._active_side

    def restore(self, snapshot: tuple[dict[Side2, int], Side2 | None]) -> None:
        points_left, active_side = snapshot
        self.points_left = dict(points_left)
        self._active_side = active_side

    def _sync_active_side(self, game: "Game", moving_side: Side2 | None = None) -> None:
        current_side = game.current_side
        if current_side is None:
            return
        if self._active_side is None:
            self._active_side = current_side
            self.points_left[current_side] = self.points_per_turn
            return
        if current_side != self._active_side and current_side != moving_side:
            self._active_side = current_side
            self.points_left[current_side] = self.points_per_turn


class PieceCountScoringSystem(ScoringSystem):
    """
    Scores sides by the number of remaining pieces.
    """

    def reset(self) -> None:
        return None

    def snapshot(self) -> None:
        return None

    def restore(self, snapshot: None) -> None:
        return None

    def get_scores(self, game: "Game") -> Mapping[Side2, int]:
        return {
            True: sum(
                1
                for piece in game.board.iter_pieces()
                if piece is not None and piece.side is True
            ),
            False: sum(
                1
                for piece in game.board.iter_pieces()
                if piece is not None and piece.side is False
            ),
        }


class MaterialScoreSystem(ScoringSystem):
    """
    Scores sides by summing configured piece values.
    """

    def __init__(self, piece_values: Mapping[str, int], default_value: int = 0) -> None:
        self.piece_values = {
            symbol.upper(): value for symbol, value in piece_values.items()
        }
        self.default_value = default_value

    def reset(self) -> None:
        return None

    def snapshot(self) -> None:
        return None

    def restore(self, snapshot: None) -> None:
        return None

    def get_scores(self, game: "Game") -> Mapping[Side2, int]:
        scores: dict[Side2, int] = {True: 0, False: 0}
        for piece in game.board.iter_pieces():
            if piece is None:
                continue
            scores[piece.side] += self.piece_values.get(
                piece.symbol.upper(), self.default_value
            )
        return scores
