from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from cynmeith.utils.aliases import Move, Side2

if TYPE_CHECKING:
    from cynmeith import Game


TurnKind = Literal["capture", "non_capture"] | None


@dataclass(frozen=True)
class ExistTurnSnapshot:
    side: Side2
    turn_index: int
    actions_this_turn: int
    turn_kind: TurnKind
    last_action_type: str | None


class ExistTurnPolicy:
    """
    Exist turn flow:
    - capture turn: exactly one capturing action
    - non-capture turn: one or two actions, with different action types
    - after one non-capture action, the player may explicitly end the turn

    Important implementation detail:
    this policy does not decide whether a move should capture; it only reacts to
    the already-resolved move metadata (`RemovePieceEffect` presence) and then
    enforces the turn-structure consequences.
    """

    def __init__(self, starting_side: Side2 = True) -> None:
        self.starting_side = starting_side
        self._state = ExistTurnSnapshot(
            side=starting_side,
            turn_index=0,
            actions_this_turn=0,
            turn_kind=None,
            last_action_type=None,
        )

    def can_move(self, game: "Game", piece, move: Move) -> bool:
        action_type = self._normalize_action_type(move.move_type)
        has_capture = self._move_has_captures(move)

        if action_type == "END_TURN":
            return (
                self._state.actions_this_turn == 1
                and self._state.turn_kind == "non_capture"
            )

        if self._state.actions_this_turn == 0:
            # First action may be either a future capture-turn action or the
            # first half of a non-capture turn.
            return True

        if self._state.turn_kind != "non_capture":
            return False

        if has_capture:
            # Second action of a non-capture turn may not turn into a capture.
            return False

        return action_type != self._state.last_action_type

    def after_move(self, game: "Game", piece, move: Move) -> None:
        """Advance or preserve turn state after a resolved action is applied."""
        action_type = self._normalize_action_type(move.move_type)
        has_capture = self._move_has_captures(move)

        if action_type == "END_TURN":
            self._advance_to_next_side()
            return

        if self._state.actions_this_turn == 0:
            if has_capture:
                # Any capturing first action becomes a 1-action capture turn.
                self._advance_to_next_side()
                return

            # Otherwise we are now mid-turn in a non-capture turn.
            self._state = ExistTurnSnapshot(
                side=self._state.side,
                turn_index=self._state.turn_index,
                actions_this_turn=1,
                turn_kind="non_capture",
                last_action_type=action_type,
            )
            return

        self._advance_to_next_side()

    def reset(self) -> None:
        self._state = ExistTurnSnapshot(
            side=self.starting_side,
            turn_index=0,
            actions_this_turn=0,
            turn_kind=None,
            last_action_type=None,
        )

    def snapshot(self) -> ExistTurnSnapshot:
        return self._state

    def restore(self, snapshot: ExistTurnSnapshot) -> None:
        self._state = snapshot

    @property
    def current_side(self) -> Side2:
        return self._state.side

    def get_turn_info(self) -> dict[str, Any]:
        if self._state.actions_this_turn == 0:
            turn_type = "New Turn"
            max_actions = 2
        elif self._state.turn_kind == "capture":
            turn_type = "Capture Turn"
            max_actions = 1
        else:
            turn_type = "Non-Capture Turn"
            max_actions = 2

        return {
            "side": "Black" if self._state.side else "White",
            "turn_type": turn_type,
            "actions_used": self._state.actions_this_turn,
            "max_actions": max_actions,
            "last_action": self._state.last_action_type or "None",
            "turn_number": self._state.turn_index + 1,
            "can_end_turn": (
                self._state.actions_this_turn == 1
                and self._state.turn_kind == "non_capture"
            ),
        }

    def _advance_to_next_side(self) -> None:
        """Commit the turn and hand control to the other player."""
        self._state = ExistTurnSnapshot(
            side=not self._state.side,
            turn_index=self._state.turn_index + 1,
            actions_this_turn=0,
            turn_kind=None,
            last_action_type=None,
        )

    @staticmethod
    def _normalize_action_type(move_type: str) -> str:
        normalized = move_type.strip().upper()
        return normalized or "MOVE"

    @staticmethod
    def _move_has_captures(move: Move) -> bool:
        if not isinstance(move.extra_info, dict):
            return False
        effects = move.extra_info.get("effects")
        if not isinstance(effects, list):
            return False
        return any(
            effect.__class__.__name__ == "RemovePieceEffect" for effect in effects
        )
