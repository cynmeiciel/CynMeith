import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from examples.ui.app import TkGameApp
from examples.xiangqi.game import build_game_spec


if __name__ == "__main__":
    TkGameApp(build_game_spec()).mainloop()
