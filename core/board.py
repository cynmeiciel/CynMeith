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
    
    def update_valid_moves(self, moved_piece: Piece, start: Coord, end: Coord):
        """
        Update the valid moves for all pieces.
        """
        
    
        for row in self.board:
            for piece in row:
                if piece is not None and piece.is_white() != moved_piece.is_white():
                    piece.update_valid_moves(self)
    
    ### Helpers
    
    def is_empty(self, position: Coord) -> bool:
        """
        Check if a position is empty.
        """
        return self.board[position.x][position.y] is None
    
    def is_empty_line(self, start: Coord, end: Coord) -> bool:
        """
        Check if the line (including diagonals) between two positions is empty.
        """
        if not (start.is_straight(end) or start.is_diagonal(end)):
            return False
        direction = start.direction_unit(end)
        position = start + direction
        while position != end:
            if not self.is_empty(position):
                return False
            position += direction
        return True
    
    def is_enemy(self, position: Coord, side: bool) -> bool:
        """
        Check if a position contains an enemy piece.
        """
        piece = self.board[position.x][position.y]
        return piece is not None and piece.is_white() != side
    
    