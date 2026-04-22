# CynMeith 
**/'siːn.meɪt/**, by the way

CynMeith is a modular board-game engine for building turn-based games with custom movement rules, side effects, and turn policies.

Current release: 1.0.0

It includes playable Tk examples for chess and xiangqi.

CynMeith is a small, flexible board-game framework for prototyping turn-based games and custom rule sets.

After cooking some spaghetti that made me refuse to look at them again, I decided to write a brand new one, with my brand new brain.

**Practice makes perfect**

This might be quite overengineering with a bunch of design patterns and extra classes, but I think it is okay.

## Install

```bash
poetry install
```

## Run Example UI

```bash
poetry run python examples/tk_demo.py chess
poetry run python examples/tk_demo.py xiangqi
```

## Minimal Usage

```python
from pathlib import Path

from cynmeith import Config, Game, QuotaTurnPolicy
from examples.chess.chess_manager import ChessManager

game = Game(
	Config.from_file(Path("examples/chess/chess.yaml")),
	move_manager=ChessManager,
	turn_policy=QuotaTurnPolicy(moves_per_turn=1),
)

game.move(...)
```

## Documentation

- Start here: [docs/index.md](docs/index.md)
- API reference: [docs/api.md](docs/api.md)
- Examples launcher: [examples/tk_demo.py](examples/tk_demo.py)