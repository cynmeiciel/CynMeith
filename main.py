from cynmeith import Board, Config
from cynmeith.utils import Coord, MoveType


board = Board(Config("examples/chess/chess.yaml"))
for c in board.iter_positions():
    print(c, board.at(c))
