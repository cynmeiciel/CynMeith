from core.board import Board
from utils import Coord
from pieces import Piece

class MoveValidator:
    """
    Class for validating moves.
    """
    
    def __init__(self, board: Board):
        self.board = board 
        
        
    # def 