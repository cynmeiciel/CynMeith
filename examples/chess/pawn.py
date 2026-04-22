from cynmeith import Board, Piece
from cynmeith.utils import Coord


class Pawn(Piece):
    def __init__(self, side, position: Coord):
        super().__init__(side, position)
        if side:
            self.distance = 2 if position.r == 1 else 1
        else:
            self.distance = 2 if position.r == 6 else 1

    def is_valid_move(self, new_position: Coord, board: Board) -> bool:
        if not self.position.is_forward(new_position, self.side):
            return False

        if (
            board.is_empty_line(self.position, new_position, Coord.is_vertical)
            and self.position.manhattan_to(new_position) <= self.distance
            and board.is_empty(new_position)
        ):
            return True

        if (
            self.position.is_diagonal(new_position)
            and self.position.chebyshev_to(new_position) == 1
            and board.is_enemy(new_position, self.side)
        ):
            return True

        return False

    def iter_move_candidates(self, board: Board):
        direction = Coord.down() if self.side else Coord.up()
        one_step = self.position + direction
        if board.is_in_bounds(one_step):
            yield one_step

        if self.distance > 1:
            two_step = one_step + direction
            if board.is_in_bounds(two_step):
                yield two_step

        diagonal_offsets = (
            Coord(direction.r, -1),
            Coord(direction.r, 1),
        )
        for offset in diagonal_offsets:
            position = self.position + offset
            if board.is_in_bounds(position):
                yield position

    def move(self, new_position: Coord):
        self.position = new_position
        self.distance = 1
