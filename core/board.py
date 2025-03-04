from core.piece_factory import PieceFactory
from core.config import Config
from pieces.piece import Piece
from utils import Coord, fen_parser

class Board:
    def __init__(self, config: Config):
        self.config = config
        self.width = config.width
        self.height = config.height
        self.board = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        self.factory = PieceFactory()
        self.factory.register_pieces(config)
        
        self._init_pieces()
        
    def _init_pieces(self):
        grid = fen_parser(self.config.fen)
        for r, row in enumerate(grid):
            for c, piece in enumerate(row):
                if piece != " ":
                    position = Coord(r, c)
                    self.board[r][c] = self.factory.create_piece(piece, position)
    
    def __str__(self):
        return "\n".join(" ".join(piece.get_symbol(self.config) if piece else "_" for piece in row) for row in self.board)
  
    def __repr__(self):
        return "\n".join(" ".join(repr(piece) if piece else "_" for piece in row) for row in self.board)
    
    def __iter__(self):
        return iter(self.board)
    
    def at(self, position: Coord) -> Piece:
        """
        Get the piece at a given position.
        """
        return self.board[position.x][position.y]
    
    def set_at(self, position: Coord, piece: Piece):
        """
        Set a piece at a given position.
        """
        self.board[position.x][position.y] = piece
        
    def move_piece(self, start: Coord, end: Coord):
        piece = self.board[start.x][start.y]
        if piece is None:
            raise ValueError("No piece at starting position")
        if not piece.is_valid_move(end):
            raise ValueError("Invalid move")
        self.board[start.x][start.y] = None
        self.board[end.x][end.y] = piece
        piece.position = end
        return piece