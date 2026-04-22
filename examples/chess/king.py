from cynmeith import Board, Piece
from cynmeith.utils import Coord


class King(Piece):
    def __init__(self, side, position: Coord):
        super().__init__(side, position)
        self.has_moved = False

    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        return self.position.is_adjacent(new_position)

    def iter_move_candidates(self, board: Board):
        deltas = tuple(
            Coord(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc
        )
        for delta in deltas:
            position = self.position + delta
            if board.is_in_bounds(position):
                yield position

    def move(self, new_position: Coord) -> None:
        self.position = new_position
        self.has_moved = True
