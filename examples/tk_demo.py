import sys
from argparse import ArgumentParser
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from examples.chess.game import build_game_spec as build_chess_spec
from examples.ui.app import TkGameApp
from examples.xiangqi.game import build_game_spec as build_xiangqi_spec


def main() -> None:
    parser = ArgumentParser(description="Play CynMeith examples in Tk.")
    parser.add_argument(
        "game", choices=("chess", "xiangqi"), nargs="?", default="chess"
    )
    parser.add_argument(
        "--config-source",
        choices=("yaml", "data"),
        default="yaml",
        help="Choose where config comes from: yaml file or in-code data mapping.",
    )
    args = parser.parse_args()

    spec = (
        build_xiangqi_spec(args.config_source)
        if args.game == "xiangqi"
        else build_chess_spec(args.config_source)
    )
    TkGameApp(spec).mainloop()


if __name__ == "__main__":
    main()
