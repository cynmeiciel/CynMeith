from utils import BoardPattern
from pieces.piece import Piece
from utils import Coord


class Board:
    def __init__(self, pattern: type):
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
    
    def at(self, position: Coord | tuple | list) -> Piece:
        """
        Get the piece at a given position.
        """
        if isinstance(position, Coord):
            return self.grid[position.x][position.y]
        return self.grid[position[0]][position[1]]
    
    def init_pieces(self, pattern: type):
        self.width = pattern.width
        self.height = pattern.height
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        for piece in pattern.get_pieces():
            self.grid[piece.position.x][piece.position.y] = piece
        
    def move_piece(self, start: Coord, end: Coord):
        piece = self.grid[start.x][start.y]
        if piece is None:
            raise ValueError("No piece at starting position")
        if not piece.is_valid_move(end):
            raise ValueError("Invalid move")
        self.grid[start.x][start.y] = None
        self.grid[end.x][end.y] = piece
        piece.position = end
        return piece