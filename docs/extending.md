# Extending the Engine

This page covers the recommended extension points.

If you are new to writing small Python classes, read
[Python Enough for CynMeith](python-enough.md) first.
If you want a guided example from blank slate to playable prototype, use
[Your First Custom Game](first-game.md).

## 1. Add a New Piece Class

Subclass `Piece` and implement `is_valid_move`.

```python
from cynmeith import Piece
from cynmeith.utils import Coord


class Scout(Piece):
    symbol = "S"

    def is_valid_move(self, new_position: Coord, board) -> bool:
        dr = abs(new_position.r - self.position.r)
        dc = abs(new_position.c - self.position.c)
        return dr + dc == 2
```

If scanning the whole board is too slow, override `iter_move_candidates`.

For sliding pieces, prefer Board traversal helpers:

```python
for position in board.iter_positions_towards(self.position + direction, direction):
    yield position
    if board.at(position) is not None:
        break
```

## 2. Add or Change Rule Logic with MoveManager

Create a subclass and override `resolve_move`.

```python
from cynmeith import MoveManager
from cynmeith.utils import Move


class MyManager(MoveManager):
    def resolve_move(self, move: Move) -> Move | None:
        piece = self.board.at(move.start)
        if piece is None:
            return None
        if not piece.is_valid_move(move.end, self.board):
            return None
        return move
```

Use this point to implement game-wide constraints and irregular rules.

## 3. Model Irregular Behavior with Effects

Attach effects in `move.extra_info["effects"]`.

```python
from cynmeith import EffectPresets
from cynmeith.utils import Move


def with_capture(move: Move, capture_position):
    extra = dict(move.extra_info or {})
    extra["effects"] = EffectPresets.capture(capture_position)
    return Move(move.start, move.end, move.move_type, extra)
```

Prefer effects over direct board mutation in `resolve_move`.

For input-driven rules (for example promotion choice), include required data in `move.extra_info` before move submission, then let manager apply that data when building effects.

## 4. Customize Turn Flow with TurnPolicy

Subclass `TurnPolicy` when alternating turns is not enough.

Required methods:

- `can_move`
- `after_move`
- `reset`
- `snapshot`
- `restore`
- `current_side` property

Keep policy state serializable/snapshot-friendly so undo/redo stays correct.

## 5. Decide Where to Put Logic

Use this checklist:

- Piece geometry and local movement constraints: piece class
- Cross-piece or board-wide rule constraints: manager
- Multi-piece side effects after successful move: effects
- Side-to-move lifecycle: turn policy
- Game-over checks: win condition
- Phase-specific restrictions and progression: phase system
- Resource budgets and move affordability: resource system
- Score calculation: scoring system
- UI interactions: example app layer, not core

## 6. Add Game-Level Systems

Use the game-level hooks when rules are larger than move geometry.

`WinCondition` is for terminal state checks:

- elimination
- target reach
- no-legal-moves conditions
- move-limit draws

`PhaseSystem` is for stage-based rule changes:

- setup phase vs battle phase
- turn-count phase shifts
- phase-specific move restrictions

`ResourceSystem` is for move affordability or side budgets:

- action points
- mana
- per-turn special move quotas

`ScoringSystem` is for score reporting:

- piece-count score
- material score
- checkpoint score

Each of these systems supports reset/snapshot/restore so `Game` can keep them in
sync with undo/redo.

Useful built-ins now included in the framework:

- `EliminatePieceCondition`
- `ReachSquareCondition`
- `NoLegalMovesCondition`
- `MoveLimitDrawCondition`
- `StaticPhaseSystem`
- `TurnCountPhaseSystem`
- `TwoStagePhaseSystem`
- `ActionPointSystem`
- `PieceCountScoringSystem`
- `MaterialScoreSystem`

For chess-like games where the royal piece cannot be captured directly, use the
royal-safety preset family:

- `RoyalRuleset`
- `RoyalSafetyMoveManager`
- `RoyalCheckmateCondition`
- `RoyalStalemateCondition`

## 7. Current Limits of the Extension Model

The current extension surface is now broad enough for:

- piece movement
- move side effects
- turn structure
- win conditions
- phase systems
- scoring
- resource systems

The current limitation is not that these hooks are missing. The current
limitation is that built-in presets are still intentionally minimal.

That follow-up work is described in [Roadmap](roadmap.md).
