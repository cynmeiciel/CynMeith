from core.game import Game
from utils import Coord
import time

if __name__ == "__main__":
    game = Game()
    for i in range(8):
        for j in range(8):
            piece = game.board.at(Coord(i, j))
            if piece is not None:
                print(piece.get_valid_moves(game.board))
    print(game.board)
    