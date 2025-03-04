from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Coord:
    """
    A class to represent a 2D coordinate.
    """
    x: int
    y: int

    def __add__(self, other: Coord) -> Coord:
        return Coord(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: Coord) -> Coord:
        return Coord(self.x - other.x, self.y - other.y)
    
    def __str__(self):
        return f"({self.x}, {self.y})"

    def is_lshape(self, other: Coord) -> bool:
        """
        Check if the position is reachable in an L-shape (Knight's movement).
        """
        return (abs(self.x - other.x) == 2 and abs(self.y - other.y) == 1) or (abs(self.x - other.x) == 1 and abs(self.y - other.y) == 2)

    def is_diagonal(self, other: Coord) -> bool:
        """
        Check if the position is reachable in a diagonal line.
        """
        return abs(self.x - other.x) == abs(self.y - other.y)
    
    def is_horizontal(self, other: Coord) -> bool:
        """
        Check if the position is reachable in a horizontal line.
        """
        return self.x == other.x
    
    def is_vertical(self, other: Coord) -> bool:
        """
        Check if the position is reachable in a vertical line.
        """
        return self.y == other.y
    
    def is_straight(self, other: Coord) -> bool:
        """
        Check if the position is reachable in a straight line.
        """
        return self.is_horizontal(other) or self.is_vertical(other)
    
    def is_queen_move(self, other: Coord) -> bool:
        """
        Check if the position is reachable in a straight line or a diagonal line.
        """
        return self.is_straight(other) or self.is_diagonal(other)
    
    def is_adjacent(self, other: Coord) -> bool:
        """
        Check if the position is adjacent to another position.
        """
        return abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1
    
    def is_forward(self, other: Coord, side: bool) -> bool:
        """
        Check if the position is forward to another position.
        """
        return (side and self.y < other.y) or (not side and self.y > other.y)
    
    def is_backward(self, other: Coord, side: bool) -> bool:
        """
        Check if the position is backward to another position.
        """
        return (side and self.y > other.y) or (not side and self.y < other.y)
    
    ###