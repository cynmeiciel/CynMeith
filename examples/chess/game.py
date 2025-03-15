from core.board import Board
from core.config import Config
from utils import Coord, Side
from core.piece import Piece

class Game:
    """
    Class representing a chess game. 
    """
    def __init__(self, config_path: str):
        # Load the configuration
        self.config = Config(config_path)
        
        self.board = Board(self.config)    
        self.turn: Side = Side.FIRST
        self.state = None
            
    def get_valid_moves(self, position: Coord) -> list[Coord]:
        """
        Get the valid moves for a piece at a given position.
        """
        piece = self.board.at(position)
        if piece is None:
            return []
        return piece.get_valid_moves()
    
    def next_turn(self):
        """
        Switch the turn.
        """
        self.turn = not self.turn
        
    def select_piece(self, position: Coord) -> Piece:
        """
        Select a piece at a given position.
        """
        piece = self.board.at(position)
        if piece is None:
            return None
        if piece.get_side() != self.turn:
            return None
        return piece