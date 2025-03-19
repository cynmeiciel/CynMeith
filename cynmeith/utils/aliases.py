"""
Contains type aliases and dataclasses for the game.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias

Side2: TypeAlias = bool
S_FIRST = True
S_SECOND = False

SideN: TypeAlias = int

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
    
    def __repr__(self):
        return f"{self.r}:{self.c}"
        
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
    
    def is_omnistraight(self, other: Coord) -> bool:
        """
        Check if the position is reachable in an orthogonal line or a diagonal line.
        """
        return self.is_orthogonal(other) or self.is_diagonal(other)
    
    def is_adjacent(self, other: Coord) -> bool:
        """
        Check if the position is adjacent to another position.
        """
        return abs(self.r - other.r) <= 1 and abs(self.c - other.c) <= 1
    
    def is_forward(self, other: Coord, side: Side2) -> bool:
        """
        Check if the position is forward to another position, according to the side.
        """
        return (side and self.r < other.r) or (not side and self.r > other.r)
    
    def is_backward(self, other: Coord, side: Side2) -> bool:
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
        Calculates the unit direction vector from this coordinate to another coordinate.

        The unit direction vector represents the movement direction in a straight line,
        normalized to either (-1, 0, 1) for both row (`r`) and column (`c`).

        Args:
            other (Coord): The target coordinate.

        Returns:
            Coord: A unit vector (dr, dc) where:
                - dr = -1 (up), 0 (same row), or 1 (down)
                - dc = -1 (left), 0 (same column), or 1 (right)
        
        Example:
            >>> start = Coord(2, 3)
            >>> end = Coord(5, 6)
            >>> start.direction_unit(end)
            Coord(1, 1)  # Moving diagonally down-right

            >>> start = Coord(4, 4)
            >>> end = Coord(4, 7)
            >>> start.direction_unit(end)
            Coord(0, 1)  # Moving right

        Notes:
            - If `self` and `other` are the same, returns (0, 0).
            - If moving strictly in a row or column, one of dr or dc will be 0.
        """
        dr = other.r - self.r
        dc = other.c - self.c
        return Coord(dr // abs(dr) if dr else 0, dc // abs(dc) if dc else 0)    

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

