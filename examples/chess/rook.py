from cynmeith import Board, Piece
from cynmeith.utils import Coord


class Rook(Piece):
    def __init__(self, side, position: Coord):
        super().__init__(side, position)
        self.has_moved = False

    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        return board.is_empty_line(self.position, new_position, Coord.is_orthogonal)

    def iter_move_candidates(self, board: Board):
        for direction in (Coord.up(), Coord.down(), Coord.left(), Coord.right()):
            for position in board.iter_positions_towards(
                self.position + direction, direction
            ):
                yield position
                if board.at(position) is not None:
                    break

    def move(self, new_position: Coord) -> None:
        self.position = new_position
        self.has_moved = True
