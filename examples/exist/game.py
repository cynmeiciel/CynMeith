from __future__ import annotations

from pathlib import Path
from typing import Any

from cynmeith import Config, Game, GameOutcome, WinCondition
from cynmeith.core.game import GameStateSnapshot
from cynmeith.core.move_effects import RemovePieceEffect
from cynmeith.utils import Coord
from cynmeith.utils.aliases import InvalidMoveError, Move, MoveHistoryError
from examples.ui.spec import BoardTheme, GameSpec

from .exist_manager import ExistManager
from .exist_turn_policy import ExistTurnPolicy
from .reserve_manager import ReserveManager
from .ui import ExistTkGameApp


class ExistGame(Game):
    """
    Game wrapper for Exist.

    Why this subclass exists:
    - reserves are part of Exist state but not part of base `Game`
    - PLACE and END_TURN are synthetic actions that need side metadata injected
    - undo/redo must restore reserve counts alongside board and turn state
    """

    def __init__(self) -> None:
        self.reserves = ReserveManager()
        self._reserve_snapshots: list[dict[bool, int]] = []
        self._redo_reserve_snapshots: list[dict[bool, int]] = []
        super().__init__(
            _build_exist_config(),
            ExistManager,
            turn_policy=ExistTurnPolicy(),
            win_conditions=_build_win_conditions(),
        )

    def can_move(
        self,
        start: Coord,
        end: Coord,
        move_type: str = "",
        extra_info: dict[str, Any] | None = None,
    ) -> bool:
        normalized_type = self._normalize_action_type(move_type)
        if normalized_type == "PLACE" and not self.reserves.has_pieces(
            self.current_side
        ):
            return False
        return super().can_move(
            start,
            end,
            normalized_type,
            self._augment_extra_info(normalized_type, extra_info),
        )

    def move(
        self,
        start: Coord,
        end: Coord,
        move_type: str = "",
        extra_info: dict[str, Any] | None = None,
    ) -> None:
        if self.is_over:
            raise InvalidMoveError("Game is already over.")

        normalized_type = self._normalize_action_type(move_type)
        if normalized_type == "PLACE" and not self.reserves.has_pieces(
            self.current_side
        ):
            raise InvalidMoveError("No reserve pieces available to place.")

        resolved_extra = self._augment_extra_info(normalized_type, extra_info)
        move = Move(start, end, normalized_type, resolved_extra)
        resolved_move = self.board.manager.resolve_move(move)
        if resolved_move is None:
            raise InvalidMoveError("Invalid move!")

        piece = self.board.manager.get_actor_piece(resolved_move)
        if piece is None:
            raise InvalidMoveError("No actor piece found for this move.")
        if not self.turn_policy.can_move(self, piece, resolved_move):
            raise InvalidMoveError("Move is not allowed by the active turn policy.")

        self.board.manager.apply_move(resolved_move, piece)
        # Reserve bookkeeping is game-level state, so it happens here rather
        # than inside the generic board/move-manager pipeline.
        self._apply_reserve_updates(piece.side, resolved_move)
        self.turn_policy.after_move(self, piece, resolved_move)
        self._outcome = self._evaluate_outcome()
        self._state_snapshots.append(self._capture_state_snapshot())
        self._redo_state_snapshots.clear()
        self._reserve_snapshots.append(self.reserves.snapshot())
        self._redo_reserve_snapshots.clear()

    def undo_move(self) -> None:
        if len(self._state_snapshots) < 2:
            raise MoveHistoryError("No game state to undo.")
        self.board.history.undo_move()
        snapshot = self._state_snapshots.pop()
        self._redo_state_snapshots.append(snapshot)
        reserve_snapshot = self._reserve_snapshots.pop()
        self._redo_reserve_snapshots.append(reserve_snapshot)
        self._restore_state_snapshot(self._state_snapshots[-1])
        self.reserves.restore(self._reserve_snapshots[-1])

    def redo_move(self) -> None:
        if not self._redo_state_snapshots:
            raise MoveHistoryError("No game state to redo.")
        self.board.history.redo_move()
        snapshot = self._redo_state_snapshots.pop()
        self._state_snapshots.append(snapshot)
        reserve_snapshot = self._redo_reserve_snapshots.pop()
        self._reserve_snapshots.append(reserve_snapshot)
        self._restore_state_snapshot(snapshot)
        self.reserves.restore(reserve_snapshot)

    def end_turn(self) -> None:
        """Expose the synthetic END_TURN action to the UI layer."""
        self.move(
            Coord.null(),
            Coord.null(),
            "END_TURN",
            {"side": self.current_side},
        )

    def _reset_game_systems(self) -> None:
        super()._reset_game_systems()
        self.reserves.reset()

    def _reseed_state(self) -> None:
        super()._reseed_state()
        # Manual board edits rebuild reserves from current on-board piece counts.
        counts = {
            True: sum(
                1
                for piece in self.board.iter_pieces()
                if piece is not None and piece.side
            ),
            False: sum(
                1
                for piece in self.board.iter_pieces()
                if piece is not None and piece.side is False
            ),
        }
        self.reserves.sync_from_board_counts(counts)
        self._reserve_snapshots = [self.reserves.snapshot()]
        self._redo_reserve_snapshots.clear()

    def _capture_state_snapshot(self) -> GameStateSnapshot:
        return super()._capture_state_snapshot()

    def _apply_reserve_updates(self, moving_side: bool, move: Move) -> None:
        """Apply reserve gain/spend rules after a committed move."""
        action_type = self._normalize_action_type(move.move_type)
        if action_type == "PLACE":
            self.reserves.spend_piece(moving_side)

        capture_count = 0
        if isinstance(move.extra_info, dict):
            effects = move.extra_info.get("effects")
            if isinstance(effects, list):
                capture_count = sum(
                    1 for effect in effects if isinstance(effect, RemovePieceEffect)
                )
        if capture_count:
            self.reserves.gain_pieces(moving_side, capture_count)

    def _augment_extra_info(
        self,
        move_type: str,
        extra_info: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        """Inject side metadata required by synthetic Exist actions."""
        if extra_info is None:
            merged: dict[str, Any] = {}
        else:
            merged = dict(extra_info)

        if move_type in {"PLACE", "END_TURN"} and "side" not in merged:
            merged["side"] = self.current_side

        return merged or None

    @staticmethod
    def _normalize_action_type(move_type: str) -> str:
        normalized = move_type.strip().upper()
        return normalized or "MOVE"


class ExistStalemateCondition(WinCondition):
    """Lose if the side to start its turn has no legal PLACE or MOVE actions."""

    def evaluate(self, game: "Game") -> GameOutcome | None:
        if not isinstance(game, ExistGame):
            return None
        if game.turn_policy.snapshot().actions_this_turn != 0:
            # Exist terminal checks only happen at turn boundaries.
            return None

        current_side = game.current_side
        if current_side is None:
            return None

        if game.reserves.has_pieces(current_side):
            for position in game.board.iter_positions():
                if game.can_move(Coord.null(), position, "PLACE"):
                    return None

        for piece in game.board.iter_pieces():
            if piece is None or piece.side != current_side:
                continue
            for destination in piece.iter_move_candidates(game.board):
                if game.can_move(piece.position, destination, "MOVE"):
                    return None

        return GameOutcome(not current_side, "win", "No legal actions available.")


class ExistAllPiecesCondition(WinCondition):
    """Draw if all 16 pieces are on the board at the end of a turn."""

    def evaluate(self, game: "Game") -> GameOutcome | None:
        if not isinstance(game, ExistGame):
            return None
        if game.turn_policy.snapshot().actions_this_turn != 0:
            return None

        piece_count = sum(1 for _ in game.board.iter_pieces())
        if piece_count == 16:
            return GameOutcome(None, "draw", "All 16 pieces are on the board.")
        return None


def _build_exist_config() -> Config:
    return Config.from_file(Path(__file__).with_name("exist.yaml"))


def _build_win_conditions() -> list[WinCondition]:
    return [ExistAllPiecesCondition(), ExistStalemateCondition()]


def _create_exist_game() -> ExistGame:
    return ExistGame()


def build_game_spec() -> GameSpec:
    return GameSpec(
        title="Exist",
        create_game=_create_exist_game,
        theme=BoardTheme(
            light_color="#efe4c8",
            dark_color="#7f6a4f",
            highlight_color="#f0c94d",
            selected_color="#28536b",
            piece_color_true="#111111",
            piece_color_false="#faf7f0",
        ),
        status_hint=(
            "Use Place for reserve drops, Move for adjacent steps, and End Turn "
            "after a one-action non-capture turn."
        ),
        app_class=ExistTkGameApp,
    )
