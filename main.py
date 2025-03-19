from cynmeith import Board, Config
from cynmeith.utils import Coord, MoveType

board = Board(Config("examples/chess/timetest.yaml"))
for pieces in board:
    for piece in pieces:
        if piece:
            pass
        
print(board.at(Coord(0, 0)).symbol)

print(MoveType.drop)