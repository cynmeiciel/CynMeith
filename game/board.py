from board_patterns import BoardPattern
from pieces import Piece
from utils import Coord


class Board:
    def __init__(self, width: int, height: int, pattern: BoardPattern):
        self.width = 0
        self.height = 0
        self.grid : list[list[Piece]] = [[]]
        self.init_pieces(pattern)
        
    def __getitem__(self, key):
        return self.grid[key]
    
    def __setitem__(self, key, value):
        self.grid[key] = value
        
    def __str__(self):
        return "\n".join(str(row) for row in self.grid)
    
    def __repr__(self):
        return self.__str__()
    
    def __iter__(self):
        return iter(self.grid)

    
    def init_pieces(self, pattern: BoardPattern):
        self.width = pattern.width
        self.height = pattern.height
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        # TODO
        