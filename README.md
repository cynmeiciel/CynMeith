# CynMeith 
**/'siːn.meɪt/**, by the way (If you are a linguistics nerd like me)

CynMeith is a modular board-game engine for building turn-based games with custom movement rules, side effects, turn policies, win conditions, phases, scoring, and resource systems.

It now includes built-in presets for common game-level patterns such as
piece-elimination wins, reach-square wins, move-limit draws, turn-count phase
changes, action points, piece-count scoring, material scoring, and
royal-safety/checkmate-style games.

Current release: `1.0.0` (It actually works, trust me bruh)

It includes playable Tk examples for chess and xiangqi.

CynMeith is a small, flexible board-game framework for prototyping original
turn-based games and custom rule sets.

___

### 🧠 The backstory

After cooking some spaghetti that made me refuse to look at them again, I decided to write a brand new one, with my brand new brain.

**Practice makes perfect**

This might be quite overengineering with a bunch of design patterns and extra classes, but I think it is okay.

___

## 🚀 Features

- **Tk Examples Included:** Comes with fully playable Tkinter examples for both Chess and Xiangqi (Cờ Tướng).
- **Small & Flexible:** Perfect for prototyping original turn-based games or proving your weird custom rule sets actually make sense.

## 📥 Install

Make sure you have [Poetry](https://python-poetry.org/) installed, then run:

```bash
poetry install
```
(No PyPI release yet because I lack the confidence.)

## 🎮 Run Example UI

```bash
poetry run python examples/tk_demo.py chess
poetry run python examples/tk_demo.py xiangqi
```

## 🛠️ Minimal Usage

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

## 📚 Documentation

- Start here: [docs/index.md](docs/index.md)
- Overview: [docs/overview.md](docs/overview.md)
- Python-enough guide: [docs/python-enough.md](docs/python-enough.md)
- First custom game: [docs/first-game.md](docs/first-game.md)
- API reference: [docs/api.md](docs/api.md)
- Examples launcher: [examples/tk_demo.py](examples/tk_demo.py)

## 📜 License & Give Me Credit (Or I'll Cry)

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

That means you can legally use, modify, and even sell this engine to buy more coffee. However, the law of the MIT license states that you MUST include my copyright notice and credit me.

If you use CynMeith in your spaghetti code, please put this line in your "About" section or Credits screen so I can flex with my friends:

> CynMeith Board-Game Engine by Cynmeiciel/Tran Van Duy (https://github.com/cynmeiciel/cynmeith)

If you made something cool with this, please open an Issue or PR, or just drop a Star to validate my existence to let me brag.