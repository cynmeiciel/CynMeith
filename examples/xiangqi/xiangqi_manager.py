from copy import deepcopy

from cynmeith import MoveManager
from cynmeith.utils import Move

from .general import General


class XiangqiManager(MoveManager):
    def resolve_move(self, move: Move) -> Move | None:
        piece = self.board.at(move.start)
        if piece is None:
            return None
        if self.board.is_allied(move.end, piece.side):
            return None

        simulated_board = deepcopy(self.board.board)
        simulated_board[move.start.r][move.start.c] = None
        simulated_board[move.end.r][move.end.c] = piece
        if self._generals_face(simulated_board):
            return None

        if not piece.is_valid_move(move.end, self.board):
            return None

        return move

    def _generals_face(self, board_state: list[list[object | None]]) -> bool:
        generals: dict[bool, tuple[int, int]] = {}
        for row_index, row in enumerate(board_state):
            for col_index, piece in enumerate(row):
                if isinstance(piece, General):
                    generals[piece.side] = (row_index, col_index)

        if len(generals) != 2:
            return False

        top = generals[True]
        bottom = generals[False]
        if top[1] != bottom[1]:
            return False

        col = top[1]
        start_row = min(top[0], bottom[0]) + 1
        end_row = max(top[0], bottom[0])
        for row_index in range(start_row, end_row):
            if board_state[row_index][col] is not None:
                return False
        return True
