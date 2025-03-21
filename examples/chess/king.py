from cynmeith import Board, Piece
from cynmeith.utils import Coord


class King(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        return self.position.is_adjacent(new_position)
