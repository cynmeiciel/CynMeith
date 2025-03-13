"""
Contains type aliases and dataclasses for the game.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias

class Side(Enum):
    FIRST = True
    SECOND = False
    
PieceSymbol: TypeAlias = str
PieceClass: TypeAlias = type
PieceName: TypeAlias = str

@dataclass(frozen=True)
class Coord:
    """
    Represents a 2D coordinate.
    """
    r: int
    c: int
    
    @classmethod
    def null(cls) -> Coord:
        return cls(-1, -1)

    def __add__(self, other: Coord) -> Coord:
        return Coord(self.r + other.r, self.c + other.c)
    
    def __sub__(self, other: Coord) -> Coord:
        return Coord(self.r - other.r, self.c - other.c)
    
    def __str__(self):
        return f"({self.r}, {self.c})"
    
    def __bool__(self):
        return self.r != -1 and self.c != -1
    
    def is_lshape(self, other: Coord) -> bool:
        """
        Check if the position is reachable in an L-shape (Knight's movement).
        """
        return (abs(self.r - other.r) == 2 and abs(self.c - other.c) == 1) or (abs(self.r - other.r) == 1 and abs(self.c - other.c) == 2)

    def is_diagonal(self, other: Coord) -> bool:
        """
        Check if the position is reachable in a diagonal line.
        """
        return abs(self.r - other.r) == abs(self.c - other.c)
    
    def is_horizontal(self, other: Coord) -> bool:
        """
        Check if the position is reachable in a horizontal line.
        """
        return self.r == other.r
    
    def is_vertical(self, other: Coord) -> bool:
        """
        Check if the position is reachable in a vertical line.
        """
        return self.c == other.c
    
    def is_orthogonal(self, other: Coord) -> bool:
        """
        Check if the position is reachable in an orthogonal line.
        """
        return self.is_horizontal(other) or self.is_vertical(other)
    
    def is_queen_move(self, other: Coord) -> bool:
        """
        Check if the position is reachable in a straight line or a diagonal line.
        """
        return self.is_orthogonal(other) or self.is_diagonal(other)
    
    def is_adjacent(self, other: Coord) -> bool:
        """
        Check if the position is adjacent to another position.
        """
        return abs(self.r - other.r) <= 1 and abs(self.c - other.c) <= 1
    
    def is_forward(self, other: Coord, side: Side) -> bool:
        """
        Check if the position is forward to another position, according to the side.
        """
        return (side and self.r < other.r) or (not side and self.r > other.r)
    
    def is_backward(self, other: Coord, side: Side) -> bool:
        """
        Check if the position is backward to another position.
        """
        return (side and self.c > other.c) or (not side and self.c < other.c)
    
    ###
    
    def chebyshev_to(self, other: Coord) -> int:
        """
        Get the Chebyshev distance to another position.
        """
        return max(abs(self.r - other.r), abs(self.c - other.c))
    
    def manhattan_to(self, other: Coord) -> int:
        """
        Get the Manhattan distance to another position.
        """
        return abs(self.r - other.r) + abs(self.c - other.c)
    
    def mirror(self, width: int, height: int) -> Coord:
        """
        Mirror the position across the board.
        """
        return Coord(width - self.r - 1, height - self.c - 1)
    
    def direction_unit(self, other: Coord) -> Coord:
        """
        Get the unit direction vector to another position.
        """
        dx = other.r - self.r
        dy = other.c - self.c
        return Coord(dx // abs(dx) if dx else 0, dy // abs(dy) if dy else 0)    

MoveType: TypeAlias = str

@dataclass(frozen=True)
class Move:
    """
    Represents a move from one position to another, with a `move_type` and `piece` field for extra information (promotion, drop, etc.).
    Supports null.
    """
    fr: Coord
    to: Coord
    move_type: MoveType = "move"
    piece: PieceSymbol | None = None
    
    @classmethod
    def null(cls) -> Move:
        return cls(Coord.null(), Coord.null())
    
    def __bool__(self):
        return bool(self.fr) and bool(self.to)

class Ending(Enum):
    """
    Represents the ending of a game.
    """
    pass

FENStr: TypeAlias = str


### ERRORS
class InvalidMoveError(ValueError):
    """
    Raised when an invalid move is attempted.
    """

class PositionError(ValueError):
    """
    Raised when an invalid position is attempted.
    """

class PieceError(ValueError):
    """
    Raised when an invalid piece is attempted.
    """

class MoveHistoryError(IndexError):
    """
    Raised when an invalid move history operation is attempted.
    """

class FENError(ValueError):
    """
    Raised when an invalid FEN string is attempted.
    """