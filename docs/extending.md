# Extending the Engine

This page covers the recommended extension points.

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
- UI interactions: example app layer, not core

