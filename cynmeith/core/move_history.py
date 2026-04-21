from copy import deepcopy
from typing import TYPE_CHECKING

from cynmeith.core.piece import Piece
from cynmeith.utils import Move, MoveHistoryError

if TYPE_CHECKING:
    from cynmeith.core.board import Board


class MoveHistory:
    """
    Manages the history of moves, allowing undo/redo functionality.

    Stores both a move stack (for tracking move history) and a state stack
    (for storing previous board states before each move).
    """

    def __init__(self, board: "Board"):
        self.num_moves = 0  # Number of moves made (half-moves)
        self.board = board
        self.move_stack: list[Move] = []  # List of moves
        self.state_stack: list[list[list[Piece | None]]] = []
        self.redo_stack: list[Move] = []
        self.redo_state_stack: list[list[list[Piece | None]]] = []

    def clear(self) -> None:
        """
        Clears the move history.
        """
        self.move_stack.clear()
        self.state_stack.clear()
        self.redo_stack.clear()
        self.redo_state_stack.clear()
        self.num_moves = 0

    def seed_current_state(self) -> None:
        """
        Seed the history with the board's current state.
        """
        self.state_stack = [deepcopy(self.board.board)]
        self.redo_stack.clear()
        self.redo_state_stack.clear()
        self.num_moves = 0

    def record_move(self, move: Move) -> None:
        """
        Records a move along with the current board state after execution.
        """
        self.state_stack.append(deepcopy(self.board.board))
        self.move_stack.append(move)
        self.redo_stack.clear()
        self.redo_state_stack.clear()
        self.num_moves += 1

    def undo_move(self) -> None:
        """
        Reverts the last move, restoring the previous board state.
        """
        if len(self.state_stack) < 2 or not self.move_stack:
            raise MoveHistoryError("No moves to undo.")

        last_state = self.state_stack.pop()
        self.redo_state_stack.append(last_state)
        self.redo_stack.append(self.move_stack.pop())
        self.board.board = deepcopy(self.state_stack[-1])
        self.num_moves -= 1

    def redo_move(self) -> None:
        """
        Redoes the last undone move.
        """
        if not self.redo_stack:
            raise MoveHistoryError("No moves to redo.")

        last_state = self.redo_state_stack.pop()
        self.board.board = deepcopy(last_state)
        self.move_stack.append(self.redo_stack.pop())
        self.state_stack.append(deepcopy(last_state))
        self.num_moves += 1
