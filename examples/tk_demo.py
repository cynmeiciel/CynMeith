from argparse import ArgumentParser
from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from examples.chess.game import build_game_spec as build_chess_spec
from examples.ui.app import TkGameApp
from examples.xiangqi.game import build_game_spec as build_xiangqi_spec


def main() -> None:
    parser = ArgumentParser(description="Play CynMeith examples in Tk.")
    parser.add_argument("game", choices=("chess", "xiangqi"), nargs="?", default="chess")
    args = parser.parse_args()

    spec = build_xiangqi_spec() if args.game == "xiangqi" else build_chess_spec()
    TkGameApp(spec).mainloop()


if __name__ == "__main__":
    main()
