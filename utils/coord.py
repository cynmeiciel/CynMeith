from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Coord:
    """
    A class to represent a 2D coordinate.
    """
    x: int
    y: int

    def __add__(self, other: Coord | tuple[int, int]) -> Coord:
        if isinstance(other, tuple):
            other = Coord(*other)
        return Coord(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: Coord | tuple[int, int]) -> Coord:
        if isinstance(other, tuple):
            other = Coord(*other)
        return Coord(self.x - other.x, self.y - other.y)
    
    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Position({self.x}, {self.y})"
