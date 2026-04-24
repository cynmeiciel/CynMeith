from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from cynmeith.core.board import Board
from cynmeith.core.config import Config
from cynmeith.core.game_systems import (
    GameOutcome,
    PhaseSystem,
    ResourceSystem,
    ScoringSystem,
    WinCondition,
)
from cynmeith.core.move_history import MoveHistory
from cynmeith.core.move_manager import MoveManager
from cynmeith.core.piece import Piece
from cynmeith.utils.aliases import (
    InvalidMoveError,
    Move,
    MoveExtraInfo,
    MoveHistoryError,
    MoveType,
    PieceError,
    PositionError,
    Side2,
)
from cynmeith.utils.coord import Coord

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


class TurnPolicy(ABC):
    """
    Strategy object that controls turn progression.

    Game owns orchestration; policies only decide when a side may move and how
    turn state changes after each move.
    """

    @abstractmethod
    def can_move(self, game: "Game", piece: Piece, move: Move) -> bool:
        pass

    @abstractmethod
    def after_move(self, game: "Game", piece: Piece, move: Move) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def snapshot(self) -> Any:
        pass

    @abstractmethod
    def restore(self, snapshot: Any) -> None:
        pass

    @property
    @abstractmethod
    def current_side(self) -> Side2 | None:
        pass


class FreeTurnPolicy(TurnPolicy):
    """
    No enforced turn order.
    """

    def can_move(self, game: "Game", piece: Piece, move: Move) -> bool:
        return True

    def after_move(self, game: "Game", piece: Piece, move: Move) -> None:
        return None

    def reset(self) -> None:
        return None

    def snapshot(self) -> None:
        return None

    def restore(self, snapshot: None) -> None:
        return None

    @property
    def current_side(self) -> Side2 | None:
        return None


@dataclass(frozen=True)
class QuotaTurnSnapshot:
    side: Side2
    moves_left: int
    turn_index: int


class QuotaTurnPolicy(TurnPolicy):
    """
    Turn policy that keeps the same side active for a fixed number of moves.
    """

    def __init__(self, moves_per_turn: int = 1, starting_side: Side2 = True) -> None:
        if moves_per_turn < 1:
            raise ValueError("moves_per_turn must be at least 1")
        self.moves_per_turn = moves_per_turn
        self.starting_side = starting_side
        self._state = QuotaTurnSnapshot(starting_side, moves_per_turn, 0)

    def can_move(self, game: "Game", piece: Piece, move: Move) -> bool:
        return piece.side == self._state.side

    def after_move(self, game: "Game", piece: Piece, move: Move) -> None:
        moves_left = self._state.moves_left - 1
        turn_index = self._state.turn_index
        side = self._state.side

        if moves_left <= 0:
            side = not side
            moves_left = self.moves_per_turn
            turn_index += 1

        self._state = QuotaTurnSnapshot(side, moves_left, turn_index)

    def reset(self) -> None:
        self._state = QuotaTurnSnapshot(self.starting_side, self.moves_per_turn, 0)

    def snapshot(self) -> QuotaTurnSnapshot:
        return self._state

    def restore(self, snapshot: QuotaTurnSnapshot) -> None:
        self._state = snapshot

    @property
    def current_side(self) -> Side2:
        return self._state.side


@dataclass(frozen=True)
class GameStateSnapshot:
    turn_policy: Any
    phase_system: Any
    resource_system: Any
    scoring_system: Any
    outcome: GameOutcome | None


class Game:
    """
    High-level game orchestration.

    Board remains responsible for board state and move application. Game adds
    turn logic, move commitment, and policy-aware undo/redo coordination.
    """

    def __init__(
        self,
        config: Config | str | Mapping[str, Any],
        move_manager: type[MoveManager] = MoveManager,
        move_history: type[MoveHistory] = MoveHistory,
        turn_policy: TurnPolicy | None = None,
        phase_system: PhaseSystem | None = None,
        resource_system: ResourceSystem | None = None,
        scoring_system: ScoringSystem | None = None,
        win_conditions: Iterable[WinCondition] | None = None,
    ) -> None:
        self.config = config if isinstance(config, Config) else Config(config)
        self.board = Board(self.config, move_manager, move_history)
        self.turn_policy = turn_policy or FreeTurnPolicy()
        self.phase_system = phase_system
        self.resource_system = resource_system
        self.scoring_system = scoring_system
        self.win_conditions = list(win_conditions or [])
        self._outcome: GameOutcome | None = None
        self._state_snapshots: list[GameStateSnapshot] = []
        self._redo_state_snapshots: list[GameStateSnapshot] = []
        self._suspend_board_sync = False
        self.board.set_state_listener(self._handle_external_board_change)
        self._reseed_state()

    @property
    def current_side(self) -> Side2 | None:
        return self.turn_policy.current_side

    @property
    def current_phase(self) -> str | None:
        if self.phase_system is None:
            return None
        return self.phase_system.current_phase

    @property
    def outcome(self) -> GameOutcome | None:
        return self._outcome

    @property
    def is_over(self) -> bool:
        return self._outcome is not None

    def get_scores(self) -> dict[Side2, int] | None:
        if self.scoring_system is None:
            return None
        return dict(self.scoring_system.get_scores(self))

    def can_move(
        self,
        start: Coord,
        end: Coord,
        move_type: MoveType = "",
        extra_info: MoveExtraInfo | None = None,
    ) -> bool:
        if self.is_over:
            return False
        try:
            move = Move(start, end, move_type, extra_info)
            resolved_move = self.board.manager.resolve_move(move)
            if resolved_move is None:
                return False
            piece = self.board.manager.get_actor_piece(resolved_move)
            if piece is None:
                return False
            if not self.turn_policy.can_move(self, piece, resolved_move):
                return False
            if self.phase_system is not None and not self.phase_system.can_move(
                self, piece, resolved_move
            ):
                return False
            if self.resource_system is not None and not self.resource_system.can_move(
                self, piece, resolved_move
            ):
                return False
        except PositionError:
            return False
        return True

    def move(
        self,
        start: Coord,
        end: Coord,
        move_type: MoveType = "",
        extra_info: MoveExtraInfo | None = None,
    ) -> None:
        if self.is_over:
            raise InvalidMoveError("Game is already over.")

        move = Move(start, end, move_type, extra_info)
        resolved_move = self.board.manager.resolve_move(move)
        if resolved_move is None:
            raise InvalidMoveError("Invalid move!")
        piece = self.board.manager.get_actor_piece(resolved_move)
        if piece is None:
            raise PieceError("No actor piece found for this move")
        if not self.turn_policy.can_move(self, piece, resolved_move):
            raise InvalidMoveError("Move is not allowed by the active turn policy.")
        if self.phase_system is not None and not self.phase_system.can_move(
            self, piece, resolved_move
        ):
            raise InvalidMoveError("Move is not allowed in the current phase.")
        if self.resource_system is not None and not self.resource_system.can_move(
            self, piece, resolved_move
        ):
            raise InvalidMoveError("Move is not allowed by the active resource system.")

        self.board.manager.apply_move(resolved_move, piece)
        self.turn_policy.after_move(self, piece, resolved_move)
        if self.phase_system is not None:
            self.phase_system.after_move(self, piece, resolved_move)
        if self.resource_system is not None:
            self.resource_system.after_move(self, piece, resolved_move)
        self._outcome = self._evaluate_outcome()
        self._state_snapshots.append(self._capture_state_snapshot())
        self._redo_state_snapshots.clear()

    def get_valid_moves(self, piece: Piece | None) -> list[Coord] | None:
        if piece is None:
            return None
        if self.is_over:
            return []
        moves = self.board.get_valid_moves(piece)
        if moves is None:
            return None
        if self.current_side is not None and piece.side != self.current_side:
            return []
        return [coord for coord in moves if self.can_move(piece.position, coord)]

    def reset(self) -> None:
        self._suspend_board_sync = True
        try:
            self.board.reset()
        finally:
            self._suspend_board_sync = False
        self._reseed_state()

    def undo_move(self) -> None:
        if len(self._state_snapshots) < 2:
            raise MoveHistoryError("No game state to undo.")
        self.board.history.undo_move()
        snapshot = self._state_snapshots.pop()
        self._redo_state_snapshots.append(snapshot)
        self._restore_state_snapshot(self._state_snapshots[-1])

    def redo_move(self) -> None:
        if not self._redo_state_snapshots:
            raise MoveHistoryError("No game state to redo.")
        self.board.history.redo_move()
        snapshot = self._redo_state_snapshots.pop()
        self._state_snapshots.append(snapshot)
        self._restore_state_snapshot(snapshot)

    def _capture_state_snapshot(self) -> GameStateSnapshot:
        return GameStateSnapshot(
            turn_policy=self.turn_policy.snapshot(),
            phase_system=(
                self.phase_system.snapshot() if self.phase_system is not None else None
            ),
            resource_system=(
                self.resource_system.snapshot()
                if self.resource_system is not None
                else None
            ),
            scoring_system=(
                self.scoring_system.snapshot()
                if self.scoring_system is not None
                else None
            ),
            outcome=self._outcome,
        )

    def _restore_state_snapshot(self, snapshot: GameStateSnapshot) -> None:
        self.turn_policy.restore(snapshot.turn_policy)
        if self.phase_system is not None:
            self.phase_system.restore(snapshot.phase_system)
        if self.resource_system is not None:
            self.resource_system.restore(snapshot.resource_system)
        if self.scoring_system is not None:
            self.scoring_system.restore(snapshot.scoring_system)
        self._outcome = snapshot.outcome

    def _evaluate_outcome(self) -> GameOutcome | None:
        for condition in self.win_conditions:
            outcome = condition.evaluate(self)
            if outcome is not None:
                return outcome
        return None

    def _reset_game_systems(self) -> None:
        self.turn_policy.reset()
        if self.phase_system is not None:
            self.phase_system.reset()
        if self.resource_system is not None:
            self.resource_system.reset()
        if self.scoring_system is not None:
            self.scoring_system.reset()

    def _reseed_state(self) -> None:
        self._reset_game_systems()
        self._outcome = self._evaluate_outcome()
        self._state_snapshots = [self._capture_state_snapshot()]
        self._redo_state_snapshots.clear()

    def _handle_external_board_change(self) -> None:
        if self._suspend_board_sync:
            return
        self._reseed_state()
