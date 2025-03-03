from core.board import Board
from core.config import Config
from core.game import Game
from utils import Coord, BoardPattern, EmptyPattern
import yaml

if __name__ == "__main__":
    game = Game()
    print(game.board)  