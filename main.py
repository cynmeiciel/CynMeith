from cynmeith import Board, Config

board = Board(Config("examples/chess/timetest.yaml"))
for pieces in board:
    for piece in pieces:
        if piece:
            pass