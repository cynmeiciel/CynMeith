from cynmeith import MoveManager
from cynmeith.utils import Move

class ChessManager(MoveManager):
    def validate_move(self, move: Move) -> bool:
        piece = self.board.at(move.start)
        new_position = move.end
        if not piece.is_valid_move(new_position, self.board):
            return False
        
        if self.board.is_allied(move.end, piece.side):
            return False
        
        return True