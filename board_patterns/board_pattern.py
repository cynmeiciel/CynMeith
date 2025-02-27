from abc import ABC, abstractmethod
from utils.coord import Coord
from pieces.piece import Piece

class BoardPattern(ABC):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[]]
        
    def get_pieces(self) -> list[Piece]:
        pass