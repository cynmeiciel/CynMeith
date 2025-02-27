from .piece import Piece
from .pawn import Pawn
from .rook import Rook
from .knight import Knight
from .bishop import Bishop
from .queen import Queen
from .king import King
from utils import Coord

class PieceFactory:
    piece_classes = {
        'P': Pawn,
        'R': Rook,
        'N': Knight,
        'B': Bishop,
        'Q': Queen,
        'K': King
    }
    
    @staticmethod
    def create_piece(piece_type: str, position: Coord) -> Piece:
        """
        Creates a piece object given a piece type, color, and position.
        """
        
        piece: Piece = PieceFactory.piece_classes.get(piece_type)
        if piece is not None:
            return piece("white", position)
        else:
            piece = PieceFactory.piece_classes.get(piece_type.upper())
            if piece is not None:
                return piece("black", position)
            else:
                raise ValueError(f"Invalid piece type: {piece}")
            

def test():
    piece = PieceFactory.create_piece("P", Coord(0, 0))
    print(piece)
    piece = PieceFactory.create_piece("p", Coord(3, 0))
    print(piece)
    piece = PieceFactory.create_piece("R", Coord(0, 0))
    print(piece)
    piece = PieceFactory.create_piece("r", Coord(0, 0))
    print(piece)
    piece = PieceFactory.create_piece("N", Coord(0, 0))
    print(piece)
    piece = PieceFactory.create_piece("n", Coord(0, 0))
    print(piece)
    piece = PieceFactory.create_piece("B", Coord(0, 0))
    print(piece)
    piece = PieceFactory.create_piece("b", Coord(0, 0))
    print(piece)
    piece = PieceFactory.create_piece("Q", Coord(0, 0))
    print(piece)
    piece = PieceFactory.create_piece("q", Coord(0, 0))
    print(piece)
    piece = PieceFactory.create_piece("K", Coord(0, 0))
    print(piece)
    piece = PieceFactory.create_piece("k", Coord(0, 0))
    print(piece)
    piece = PieceFactory.create_piece("Z", Coord(0, 0))
    print(piece)