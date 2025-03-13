from typing import TYPE_CHECKING

from utils import Move, MoveHistoryError

if TYPE_CHECKING:
    from core.board import Board
    
class MoveHistory:
    """
    Manages the history of moves, allowing undo/redo functionality.
    
    Stores both a move stack (for tracking move history) and a state stack 
    (for storing previous board states before each move).
    """
    def __init__(self, board: "Board"):
        self.num_moves = 0 # Number of moves made (half-moves)
        self.board = board
        self.move_stack: list[Move] = []  # List of moves
        self.state_stack: list[Board] = [] # List of board states
        self.redo_stack: list[Move] = []
        self.redo_state_stack: list[Board] = []

    def clear(self):
        """
        Clears the move history.
        """
        self.move_stack.clear()
        self.state_stack.clear()
        self.redo_stack.clear()
        self.redo_state_stack.clear()
        self.num_moves = 0
    
    def record_move(self, move: Move):
        """
        Records a move along with the current board state before execution.
        """
        self.state_stack.append(self.board.copy())  # Store board state
        self.move_stack.append(move)
        self.redo_stack.clear()
        self.redo_state_stack.clear()
        self.num_moves += 1

    def undo_move(self):
        """
        Reverts the last move, restoring the previous board state.
        """
        if not self.move_stack:
            raise MoveHistoryError("No moves to undo.")

        # Restore previous board state
        last_state = self.state_stack.pop()
        self.board.board = last_state.board
        self.redo_stack.append(self.move_stack.pop())
        self.redo_state_stack.append(last_state)
        self.num_moves -= 1
        
    def redo_move(self):
        """
        Redoes the last undone move.
        """
        if not self.redo_stack:
            raise MoveHistoryError("No moves to redo.")

        # Restore previous board state
        last_state = self.redo_state_stack.pop()
        self.board.board = last_state.board
        self.move_stack.append(self.redo_stack.pop())
        self.state_stack.append(last_state)
        self.num_moves += 1