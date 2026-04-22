from cynmeith import Board, Piece
from cynmeith.utils import Coord


class Bishop(Piece):
    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        return board.is_empty_line(self.position, new_position, Coord.is_diagonal)

    def iter_move_candidates(self, board: Board):
        for direction in (
            Coord(-1, -1),
            Coord(-1, 1),
            Coord(1, -1),
            Coord(1, 1),
        ):
            for position in board.iter_positions_towards(
                self.position + direction, direction
            ):
                yield position
                if board.at(position) is not None:
                    break
