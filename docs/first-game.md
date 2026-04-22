# Your First Custom Game

This guide walks through a tiny custom prototype so you can see how CynMeith is
supposed to be used.

The example game is intentionally small:

- one board
- two piece types
- standard alternating turns
- one custom capture rule

The point is not to make a great game. The point is to show the extension flow.

## Step 1: Define the Pieces

Create a package such as `examples/duel`.

Start with a step-based piece:

```python
from cynmeith import Piece
from cynmeith.utils import Coord


class Scout(Piece):
    symbol = "S"

    def is_valid_move(self, new_position: Coord, board) -> bool:
        if board.is_allied(new_position, self.side):
            return False
        return self.position.manhattan_to(new_position) == 1

    def iter_move_candidates(self, board):
        for delta in (Coord(-1, 0), Coord(1, 0), Coord(0, -1), Coord(0, 1)):
            position = self.position + delta
            if board.is_in_bounds(position):
                yield position
```

Now add a rider piece:

```python
from cynmeith import Piece
from cynmeith.utils import Coord


class Lancer(Piece):
    symbol = "L"

    def is_valid_move(self, new_position: Coord, board) -> bool:
        if board.is_allied(new_position, self.side):
            return False
        if not self.position.is_orthogonal(new_position):
            return False
        return board.is_empty_line(self.position, new_position, Coord.is_orthogonal)

    def iter_move_candidates(self, board):
        for direction in (Coord.up(), Coord.down(), Coord.left(), Coord.right()):
            for position in board.iter_positions_towards(
                self.position + direction, direction
            ):
                yield position
                if board.at(position) is not None:
                    break
```

## Step 2: Add a Move Manager

Now add a custom rule: `Scout` can also capture by striking an adjacent piece
without moving.

```python
from cynmeith import EffectPresets, MoveManager
from cynmeith.utils import Coord, Move

from .scout import Scout


class DuelManager(MoveManager):
    def resolve_move(self, move: Move) -> Move | None:
        piece = self.board.at(move.start)
        if piece is None:
            return None

        if isinstance(piece, Scout) and move.start == move.end:
            target = Coord(move.start.r, move.start.c + 1)
            target_piece = self.board.at(target) if self.board.is_in_bounds(target) else None
            if target_piece is None or target_piece.side == piece.side:
                return None

            extra = dict(move.extra_info or {})
            extra["effects"] = EffectPresets.capture(target)
            extra["move_actor"] = False
            return Move(move.start, move.end, move.move_type, extra)

        if self.board.is_allied(move.end, piece.side):
            return None
        if not piece.is_valid_move(move.end, self.board):
            return None
        return move
```

This shows the usual split:

- piece classes define local movement rules
- manager defines cross-piece or irregular behavior

## Step 3: Create Config Data

You can start with Python data before committing to a YAML file.

```python
from cynmeith import Config


config = Config.from_data(
    {
        "pieces": {
            "Scout": {"symbol": "S", "class_path": "examples.duel.scout"},
            "Lancer": {"symbol": "L", "class_path": "examples.duel.lancer"},
        },
        "width": 5,
        "height": 5,
        "fen": "l3s/5/5/5/S3L",
    }
)
```

## Step 4: Build a Game

```python
from cynmeith import Game, QuotaTurnPolicy

from .duel_manager import DuelManager


game = Game(
    config,
    move_manager=DuelManager,
    turn_policy=QuotaTurnPolicy(moves_per_turn=1),
)
```

At this point you can already call:

```python
game.can_move(start, end)
game.move(start, end)
game.undo_move()
```

## Step 5: Decide What Belongs Where

Use this rule of thumb:

- if the rule belongs to one piece shape, put it on the piece
- if the rule depends on other pieces or special consequences, put it in the manager
- if the rule changes whose turn it is, put it in a turn policy

## Step 6: Move From Prototype To Package

Once the prototype feels promising:

1. move config data into a YAML file
2. add tests for your piece movement and manager rules
3. create a `build_game_spec()` function if you want UI integration
4. only then start polishing the visual presentation

## Common Mistakes

- putting every rule into one giant `is_valid_move(...)`
- mutating the board directly during validation
- mixing UI concerns into the engine layer
- optimizing performance before the rules are stable

## Next Reads

- [Python Enough for CynMeith](python-enough.md)
- [Extending the Engine](extending.md)
- [Examples Guide](examples.md)

