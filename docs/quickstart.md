# Quickstart

## Prerequisites

- Python 3.10+
- Poetry

## Install

```bash
poetry install
```

## Run the Included Tk Examples

```bash
poetry run python examples/tk_demo.py chess
poetry run python examples/tk_demo.py xiangqi
```

## Create a Game from YAML

```python
from pathlib import Path

from cynmeith import Config, Game, QuotaTurnPolicy
from examples.chess.chess_manager import ChessManager

game = Game(
    Config.from_file(Path("examples/chess/chess.yaml")),
    move_manager=ChessManager,
    turn_policy=QuotaTurnPolicy(moves_per_turn=1),
)
```

## Create a Game from Python Mapping

```python
from cynmeith import Config, Game

cfg = Config.from_data(
    {
        "pieces": {
            "Pawn": {
                "class_path": "examples.chess.pawn",
                "symbol": "P",
            }
        },
        "width": 8,
        "height": 8,
        "fen": "8/8/8/8/8/8/8/8",
    }
)

game = Game(cfg)
```

## Make Moves

Positions are `Coord(row, col)` values. Pass a start and an end:

```python
from cynmeith.utils import Coord

start, end = Coord(6, 4), Coord(4, 4)  # row 6 -> row 4, column 4
if game.can_move(start, end):
    game.move(start, end)
```

Out-of-bounds coordinates simply return `False` from `game.can_move(...)`.

A "side" is a boolean: `True` is the first side, `False` is the second.
`game.current_side` tells you who is to move.

Promotion (programmatic usage):

```python
game.move(start, end, extra_info={"promotion": "Q"})
```

Allowed promotion symbols in chess example are `Q`, `R`, `B`, `N`.

Undo/redo:

```python
game.undo_move()
game.redo_move()
```

## Next Step

Continue with [Python Enough for CynMeith](python-enough.md),
[Your First Custom Game](first-game.md), and [Extending the Engine](extending.md).
