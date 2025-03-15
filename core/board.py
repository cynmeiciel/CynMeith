from core.piece_factory import PieceFactory
from core.config import Config
from core.move_validator import MoveValidator
from core.move_history import MoveHistory
from core.piece import Piece
from utils import Coord, PieceClass, Side, Move, PieceError, InvalidMoveError, PositionError
from utils import fen_parser

class Board:
    """
    The Board class represents the game board and acts as the central interface for managing game state.
    
    It provides methods for placing, removing, and moving pieces while ensuring that the core game mechanics remain 
    stable.
    """
    def __init__(self, config: Config, move_validator: type[MoveValidator] = MoveValidator, move_history: type[MoveHistory] = MoveHistory):
        self.config = config
        self.width = config.width
        self.height = config.height
        self.board = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        self.factory = PieceFactory()
        self.factory.register_pieces(config)
        
        self.validator = move_validator(self)
        self.history = move_history(self)
        
        self._init_pieces()
        
        self.log = []
        
    def _init_pieces(self):
        grid = fen_parser(self.config.fen, self.config.width, self.config.height)
        for r, row in enumerate(grid):
            for c, piece in enumerate(row):
                if piece != " ":
                    position = Coord(r, c)
                    self.set_at(position, self.factory.create_piece(piece, position))
    
    def __str__(self):
        return "\n".join(" ".join(piece.get_symbol(self.config) if piece else "_" for piece in row) for row in self.board)
  
    def __repr__(self):
        return "\n".join(" ".join(repr(piece) if piece else "_" for piece in row) for row in self.board)
    
    def __iter__(self):
        return iter(self.board)
    
    def reset(self):
        """
        Reset the board to its initial state.
        """
        self.clear()
        self._init_pieces()
    
    def clear(self):
        """
        Clear the board.
        """
        self.board = [[None for _ in range(self.width)] for _ in range(self.height)]
        
    def pieces(self, piece_type: PieceClass, side: Side) -> list[Piece]:
        """
        Get all pieces of a given criteria.
        """
        return [piece for row in self.board for piece in row if piece is not None and isinstance(piece, piece_type) and piece.get_side() == side]
    
    def at(self, position: Coord) -> Piece:
        """
        Get the piece at a given position.
        """
        if not self.is_in_bounds(position):
            raise PositionError(f"Position out of bounds {position}")
        return self.board[position.r][position.c]
    
    def set_at(self, position: Coord, piece: Piece):
        """
        Set a piece at a given position.s
        """
        if not self.is_in_bounds(position):
            raise PositionError(f"Position out of bounds {position}")
        self.board[position.r][position.c] = piece
        
    def type_at(self, position: Coord) -> PieceClass:
        """
        Get the type of piece at a given position.
        """
        piece = self.at(position)
        return type(piece) if piece is not None else None
    
    def side_at(self, position: Coord) -> Side:
        """
        Get the side of the piece at a given position.
        """
        piece = self.at(position)
        return piece.get_side() if piece is not None else None    
        
    def move(self, move: Move):
        """
        Move a piece from one position to another.
        """
        piece = self.move_from_coord(move.fr, move.to)
        self.history.add_move(move, piece)
        self.update_valid_moves(piece, move.fr, move.to)
    
    def move_from_coord(self, start: Coord, end: Coord):
        """
        Move a piece from one position to another.
        """
        piece = self.at(start)
        if piece is None:
            raise PieceError("No piece at starting position")
        if not piece.is_valid_move(end, self):
            raise InvalidMoveError("Invalid move!")
        self.set_at(start, None)
        self.set_at(end, piece)
        piece.move(end)
        return piece
    
    def get_valid_moves(self, position: Coord) -> list[Coord]:
        """
        Get the valid moves for a piece at a given position.
        """
        piece = self.at(position)
        if piece is None:
            return []
        return self.validator.get_validated_moves(piece)
    
    def update_valid_moves(self, moved_piece: Piece, start: Coord, end: Coord):
        """
        Update the valid moves for all pieces.
        """
        for row in self.board:
            for piece in row:
                if piece is not None and piece.get_side() != moved_piece.get_side():
                    piece.update_valid_moves(self)
    
    ### Helpers
    def is_in_bounds(self, position: Coord) -> bool:
        """
        Check if a position is in bounds.
        """
        return position.r >= 0 and position.r < self.width and position.c >= 0 and position.c < self.height
    
    def is_empty(self, position: Coord) -> bool:
        """
        Check if a position is empty.
        """
        return self.at(position) is None
    
    def is_empty_line(self, start: Coord, end: Coord) -> bool:
        """
        Check if the line (including diagonals) between two positions is empty.
        """
        if not (start.is_orthogonal(end) or start.is_diagonal(end)):
            return False
        direction = start.direction_unit(end)
        position = start + direction
        while position != end:
            if not self.is_empty(position):
                return False
            position += direction
        return True
    
    def is_enemy(self, position: Coord, side: Side) -> bool:
        """
        Check if a position contains an enemy piece.
        """
        piece = self.at(position)
        return piece is not None and piece.get_side() != side
    
    