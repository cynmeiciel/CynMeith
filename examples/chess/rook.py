from cynmeith import Board, Piece
from cynmeith.utils import Coord


class Rook(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        return board.is_empty_line(self.position, new_position, Coord.is_orthogonal)
