from typing import Callable
from cynmeith.core.piece_factory import PieceFactory
from cynmeith.core.config import Config
from cynmeith.core.move_manager import MoveManager
from cynmeith.core.move_history import MoveHistory
from cynmeith.core.piece import Piece
from cynmeith.utils import Coord, PieceSymbol, PieceClass, Side2, Move, PieceError, InvalidMoveError, PositionError
from cynmeith.utils import fen_parser

class Board:
    """
    The Board class represents the game board and acts as the central interface for managing game state.
    
    It provides methods for placing, removing, and moving pieces.
    """
    def __init__(self, config: Config, move_manager: type[MoveManager] = MoveManager, move_history: type[MoveHistory] = MoveHistory):
        self.config = config
        self.width = config.width
        self.height = config.height
        self.board = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        self.factory = PieceFactory()
        self.factory.register_pieces(config)
        
        self.manager = move_manager(self)
        self.history = move_history(self)
        
        self._init_pieces()
        
    def _init_pieces(self):
        grid = fen_parser(self.config.fen, self.config.width, self.config.height)
        for r, row in enumerate(grid):
            for c, piece in enumerate(row):
                if piece != " ":
                    position = Coord(r, c)
                    self.set_at(position, self.factory.create_piece(piece, position))
    
    def __str__(self):
        return "\n".join(" ".join(piece.symbol if piece else "□" for piece in row) for row in self.board)
  
    def __repr__(self):
        return "\n".join(" ".join(repr(piece) if piece else "□" for piece in row) for row in self.board)
    
    def __iter__(self):
        return iter(self.board)
    
    def print_highlighted(self, highlights: list[Coord] = []):
        """
        Print the board with highlighted positions.
        """
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece is None:
                    symbol = "□"
                else:
                    symbol = piece.symbol if piece.side else piece.symbol.lower()
                position = Coord(r, c)
                if position in highlights:
                    print(f"\033[93m{symbol}\033[0m", end=" ")
                else:
                    print(symbol, end=" ")
            print()
    
    def iter_pieces(self, none_piece: bool = False):
        """
        Iterate over all pieces on the board.
        
        If none_piece is True, the iteration will also include empty positions.
        """
        for row in self.board:
            for piece in row:
                if piece is not None or none_piece:
                    yield piece
                                
    def iter_pieces_by_side(self, side: Side2):
        """
        Iterate over all pieces by side.
        """
        for piece in self.iter_pieces():
            if piece.side == side:
                yield piece
    
    def iter_pieces_by_type(self, piece_symbol: PieceSymbol):
        """
        Iterate over all pieces by type.
        """
        for piece in self.iter_pieces():
            if piece.symbol == piece_symbol:
                yield piece
    
    def iter_positions(self):
        """
        Iterate over all coordinates on the board.
        """
        for r in range(self.height):
            for c in range(self.width):
                yield Coord(r, c)
        
    def iter_enumerate(self, none_piece: bool = False):
        """
        Iterate over all pieces on the board with their positions.
        """
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece is not None or none_piece:
                    yield Coord(r, c), piece
    
    def iter_positions_line(self, start: Coord, end: Coord, criteria: Callable[[Coord, Coord], bool] = Coord.is_omnidirectional):
        """
        Iterate over all positions in a line between two positions.
        """
        if not criteria(start, end):
            return []
        direction = start.direction_unit(end)
        position = start + direction
        while position != end:
            yield position
            position += direction
    
    def iter_pieces_line(self, start: Coord, end: Coord, criteria: Callable[[Coord, Coord], bool] = Coord.is_omnidirectional, none_piece: bool = False):
        """
        Iterate over all pieces in a line between two positions.
        
        If none_piece is True, the iteration will also include empty positions.
        """
        for position in self.iter_positions_line(start, end, criteria):
            piece = self.at(position)
            if piece is not None or none_piece:
                yield piece
                if piece is not None:
                    break
                
    def iter_enumerate_line(self, start: Coord, end: Coord, criteria: Callable[[Coord, Coord], bool] = Coord.is_omnidirectional, none_piece: bool = False):
        """
        Iterate over all pieces with their positions in a line between two positions.
        
        If none_piece is True, the iteration will also include empty positions.
        """
        for position in self.iter_positions_line(start, end, criteria):
            piece = self.at(position)
            if piece is not None or none_piece:
                yield position, piece
                if piece is not None:
                    break
            
    def iter_positions_towards(self, start: Coord, direction: Coord):
        """
        Iterate over all positions in a direction from a starting position.
        """
        position = start + direction
        while self.is_in_bounds(position):
            yield position
            position += direction
    
    def iter_pieces_towards(self, start: Coord, direction: Coord):
        """
        Iterate over all pieces in a direction from a starting position.
        """
        for position in self.iter_positions_towards(start, direction):
            piece = self.at(position)
            if piece is not None:
                yield piece
                break
            
    def iter_enumerate_towards(self, start: Coord, direction: Coord, none_piece: bool = False):
        """
        Iterate over all pieces with their positions in a direction from a starting position.
        
        If none_piece is True, the iteration will also include empty positions.
        """
        for position in self.iter_positions_towards(start, direction):
            piece = self.at(position)
            if piece is not None or none_piece:
                yield position, piece
                if piece is not None:
                    break
                
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
        self.history.clear()       
    
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
    
    def side_at(self, position: Coord) -> Side2 | None:
        """
        Get the side of the piece at a given position, returns None if the position is empty.
        """
        piece = self.at(position)
        return piece.side if piece is not None else None    
        
    def move(self, start: Coord, end: Coord):
        """
        Perform a move by a player, not a piece.
        """
        piece = self.at(start)
        if piece is None:
            raise PieceError("No piece at starting position")
        if not piece.is_valid_move(end, self):
            raise InvalidMoveError("Invalid move!")
        self.set_at(start, None)
        self.set_at(end, piece)
        piece.move(end)
        self.history.record_move(Move(start, end))
    
    def get_valid_moves(self, piece: Piece | Coord) -> list[Coord]:
        """
        Get the valid moves for a piece at a given position.
        """
        if isinstance(piece, Coord):
            piece = self.at(piece)
            if piece is None:
                return []
        return self.manager.get_validated_moves(piece)
    
    def is_in_bounds(self, position: Coord) -> bool:
        """
        Check if a position is in bounds.
        """
        return position.r >= 0 and position.r < self.height and position.c >= 0 and position.c < self.width
    
    def is_empty(self, position: Coord) -> bool:
        """
        Check if a position is empty.
        """
        return self.at(position) is None
    
    def is_empty_line(self, start: Coord, end: Coord, criteria: Callable[[Coord, Coord], bool] = Coord.is_omnidirectional) -> bool:
        """
        Checks if the line between two coordinates is empty, following a specific movement rule.

        This method verifies whether all squares along the path from `start` to `end`
        are unoccupied, based on a criteria that must be a `Coord`'s method.

        Args:
            start: The starting coordinate.
            end: The target coordinate.
            criteria: A Coord method that determines the movement rule to follow, must be is_orthogonal, is_diagonal or is_omnidirectional.

        Returns:
            bool: True if the path between `start` and `end` is completely empty; False otherwise.

        Example:
            >>> board.is_empty_line(Coord(0, 0), Coord(0, 7))  # Check if the column is empty
            True

            >>> board.is_empty_line(Coord(2, 2), Coord(5, 5), Coord.is_diagonal)  # Check diagonal path
            False

        Notes:
            - The empty line check is exclusive, meaning that the start and end positions are not included in the check.
        """
        if not (criteria(start, end)):
            return False
        for piece in self.iter_pieces_line(start, end):
            if piece is not None:
                return False
        return True
    
    def is_enemy(self, position: Coord, side: Side2) -> bool:
        """
        Check if a position contains an enemy piece.
        """
        enemy_side = self.side_at(position)
        if enemy_side is None:
            return False
        return enemy_side != side
    
    def is_allied(self, position: Coord, side: Side2) -> bool:
        """
        Check if a position contains an allied piece.
        """
        return self.side_at(position) == side
    