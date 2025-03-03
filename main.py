from core.board import Board
# from core.game import Game
from utils import Coord, BoardPattern, EmptyPattern
import yaml

if __name__ == "__main__":
    with open("config/standard.yaml", "r") as file:
        piece_data = yaml.safe_load(file)["pieces"]
        
    print(piece_data)    
    for data in piece_data:
        print(data)
    
    # a = input()
    # if a == "0":
    #     game = Game()