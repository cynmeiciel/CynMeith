# CynMeith API
## Core Objects

- `Board`: owns board state, piece placement, and primitive move application.
- `Game`: owns orchestration, turn policy, and undo/redo coordination.
- `MoveManager`: validates a single move.
- `MoveHistory`: stores board snapshots for undo/redo.
- `Piece`: implements move legality for each piece.

## Configuration

`Config` is hybrid on purpose:

- `Config.from_file(path)` for YAML-driven presets.
- `Config.from_data(mapping)` for code-first setup.
- `Config(existing_config)` when you want to reuse an already-built config.

## Turn Policy

`Game` does not force a single turn model.

- `FreeTurnPolicy` allows any side to move.
- `QuotaTurnPolicy(moves_per_turn=2)` can keep the same side active for two moves before switching.
- Custom policies can subclass `TurnPolicy`.

This keeps the engine flexible for games that do not alternate after every move.

## Example Shape

```python
from cynmeith import Config, Game, QuotaTurnPolicy
from examples.chess.chess_manager import ChessManager

game = Game(
    Config.from_file("examples/chess/chess.yaml"),
    move_manager=ChessManager,
    turn_policy=QuotaTurnPolicy(moves_per_turn=2),
)

game.move(...)
```

For the Tk examples, start from [examples/tk_demo.py](../examples/tk_demo.py).
