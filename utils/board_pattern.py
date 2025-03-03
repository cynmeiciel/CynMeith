from utils.coord import Coord
from pieces.piece import Piece
from core.piece_factory import PieceFactory

class BoardPattern():
    grid = [
        ["R", "N", "B", "Q", "K", "B", "N", "R"],
        ["P", "P", "P", "P", "P", "P", "P", "P"],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        ["p", "p", "p", "p", "p", "p", "p", "p"],
        ["r", "n", "b", "q", "k", "b", "n", "r"]
    ]
    width = 8
    height = 8
    
    @classmethod
    def register_pieces(cls):
        "".rsplit()
    
    @classmethod
    def get_pieces(cls) -> list[Piece]:
        pieces = []
        for r, row in enumerate(cls.grid):
            for c, piece in enumerate(row):
                if piece:
                    pieces.append(PieceFactory.create_piece(piece, Coord(r, c)))
        return pieces
    
class EmptyPattern(BoardPattern):
    grid = [[None for _ in range(8)] for _ in range(8)]