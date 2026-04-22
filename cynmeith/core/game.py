from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from cynmeith.core.board import Board
from cynmeith.core.config import Config
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
    from collections.abc import Mapping


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
    ) -> None:
        self.config = config if isinstance(config, Config) else Config(config)
        self.board = Board(self.config, move_manager, move_history)
        self.turn_policy = turn_policy or FreeTurnPolicy()
        self._turn_snapshots: list[Any] = [self.turn_policy.snapshot()]
        self._redo_turn_snapshots: list[Any] = []

    @property
    def current_side(self) -> Side2 | None:
        return self.turn_policy.current_side

    def can_move(
        self,
        start: Coord,
        end: Coord,
        move_type: MoveType = "",
        extra_info: MoveExtraInfo | None = None,
    ) -> bool:
        try:
            piece = self.board.at(start)
            if piece is None:
                return False
            move = Move(start, end, move_type, extra_info)
            if not self.turn_policy.can_move(self, piece, move):
                return False
            resolved_move = self.board.manager.resolve_move(move)
        except PositionError:
            return False
        return resolved_move is not None

    def move(
        self,
        start: Coord,
        end: Coord,
        move_type: MoveType = "",
        extra_info: MoveExtraInfo | None = None,
    ) -> None:
        piece = self.board.at(start)
        if piece is None:
            raise PieceError("No piece at starting position")

        move = Move(start, end, move_type, extra_info)
        if not self.turn_policy.can_move(self, piece, move):
            raise InvalidMoveError("Move is not allowed by the active turn policy.")
        resolved_move = self.board.manager.resolve_move(move)
        if resolved_move is None:
            raise InvalidMoveError("Invalid move!")

        self.board.manager.apply_move(resolved_move, piece)
        self.turn_policy.after_move(self, piece, resolved_move)
        self._turn_snapshots.append(self.turn_policy.snapshot())
        self._redo_turn_snapshots.clear()

    def get_valid_moves(self, piece: Piece | None) -> list[Coord] | None:
        if piece is None:
            return None
        moves = self.board.get_valid_moves(piece)
        if moves is None:
            return None
        if self.current_side is None:
            return moves
        if piece.side != self.current_side:
            return []
        return [coord for coord in moves if self.can_move(piece.position, coord)]

    def reset(self) -> None:
        self.board.reset()
        self.turn_policy.reset()
        self._turn_snapshots = [self.turn_policy.snapshot()]
        self._redo_turn_snapshots.clear()

    def undo_move(self) -> None:
        if len(self._turn_snapshots) < 2:
            raise MoveHistoryError("No turn state to undo.")
        self.board.history.undo_move()
        snapshot = self._turn_snapshots.pop()
        self._redo_turn_snapshots.append(snapshot)
        self.turn_policy.restore(self._turn_snapshots[-1])

    def redo_move(self) -> None:
        if not self._redo_turn_snapshots:
            raise MoveHistoryError("No turn state to redo.")
        self.board.history.redo_move()
        snapshot = self._redo_turn_snapshots.pop()
        self._turn_snapshots.append(snapshot)
        self.turn_policy.restore(snapshot)
