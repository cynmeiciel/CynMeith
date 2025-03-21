from __future__ import annotations
from dataclasses import dataclass
from math import trunc

from typing import Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from cynmeith.utils import Side2

@dataclass(frozen=True)
class Coord:
    """
    Represents a 2D coordinate.
    """
    r: int
    c: int
    
    @staticmethod
    def null() -> Coord:
        return Coord(-1, -1)
    
    @staticmethod
    def up() -> Coord:
        """
        Get the unit vector pointing up.
        """
        return Coord(-1, 0)
    
    @staticmethod
    def down() -> Coord:
        """
        Get the unit vector pointing down.
        """
        return Coord(1, 0)
    
    @staticmethod
    def left() -> Coord:
        """
        Get the unit vector pointing left.
        """
        return Coord(0, -1)
    
    @staticmethod
    def right() -> Coord:
        """
        Get the unit vector pointing right.
        """
        return Coord(0, 1)
    
    @staticmethod
    def from_str(coord_str: str, delimiter: str = ":") -> Coord:
        """
        Create a coordinate from a string.
        """
        r, c = coord_str.split(delimiter)
        return Coord(int(r), int(c))

    @staticmethod
    def batch(*coords: tuple[int, int]) -> list[Coord]:
        """
        Create a list of coordinates from a list of tuples.
        """
        return [Coord(*coord) for coord in coords]

    def __add__(self, other: Coord | int) -> Coord:
        if isinstance(other, int):
            return Coord(self.r + other, self.c + other)
        return Coord(self.r + other.r, self.c + other.c)
    
    def __sub__(self, other: Coord | int) -> Coord:
        if isinstance(other, int):
            return Coord(self.r - other, self.c - other)
        return Coord(self.r - other.r, self.c - other.c)
    
    def __mul__(self, other: Coord | int) -> Coord:
        if isinstance(other, int):
            return Coord(self.r * other, self.c * other)
        return Coord(self.r * other.r, self.c * other.c)
    
    def __truediv__(self, other: Coord | int) -> Coord:
        if isinstance(other, int):
            return Coord(self.r / other, self.c / other)
        return Coord(self.r / other.r, self.c / other.c)
    
    def __floordiv__(self, other: Coord | int) -> Coord:
        if isinstance(other, int):
            return Coord(trunc(self.r / other), trunc(self.c / other))
        return Coord(trunc(self.r / other.r), trunc(self.c / other.c))
    
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
    
    def is_omnidirectional(self, other: Coord) -> bool:
        """
        Check if the position is reachable in an orthogonal line or a diagonal line.
        """
        return self.is_orthogonal(other) or self.is_diagonal(other)
    
    def is_adjacent(self, other: Coord) -> bool:
        """
        Check if the position is adjacent to another position.
        """
        return abs(self.r - other.r) <= 1 and abs(self.c - other.c) <= 1
    
    def is_forward(self, other: Coord, side: Side2, criteria: Callable[[Coord, Coord], bool] | None = None) -> bool:
        """
        Check if the position is forward to another position, according to the side.
        A criteria function can be provided to further restrict the movement.
        """
        if side:
            return self.r < other.r and (not criteria or criteria(self, other))
        else:
            return self.r > other.r and (not criteria or criteria(self, other))
        
    
    def is_backward(self, other: Coord, side: Side2, criteria: Callable[[Coord, Coord], bool] | None = None) -> bool:
        """
        Check if the position is backward to another position, according to the side.
        A criteria function can be provided to further restrict the movement.
        """
        if side:
            return self.r > other.r and (not criteria or criteria(self, other))
        else:
            return self.r < other.r and (not criteria or criteria(self, other))
    
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
    
    def mirror(self, width: int, height: int, direction: str = "v") -> Coord:
        """
        Mirror the position across the board.
        
        Args:
            width (int): The width of the board.
            height (int): The height of the board.
            direction (str): The direction to mirror. Can be "h" (horizontal), "v" (vertical) or "hv" (both).
            
        Returns:
            Coord: The mirrored position.
        """
        
        if direction == "h":
            return Coord(self.r, width - self.c - 1)
        elif direction == "v":
            return Coord(height - self.r - 1, self.c)
        elif direction == "hv":
            return Coord(height - self.r - 1, width - self.c - 1)
        else:
            raise ValueError(f"Invalid direction {direction}: must be 'h', 'v', or 'hv'")
    
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