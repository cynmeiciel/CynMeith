from pieces.piece import Piece
from utils import Coord

class PieceFactory:
    """
    Factory class for creating pieces.
    """
    piece_classes = {}
    
    @classmethod
    def register_piece(cls, piece_name: str, piece_class: Piece) -> None:
        """
        Register a piece class with the factory.
        """
        cls.piece_classes[piece_name] = piece_class

    @classmethod
    def create_piece(cls, piece_name: str, position: Coord) -> Piece:
        """
        Create a piece. Upper case for white, lower case for black.
        """
        side = piece_name.isupper() # True if piece is white, False if black
        piece_cls = cls.piece_classes.get(piece_name.upper())
        if piece_cls:
            return piece_cls(side, position)
        else:
            raise ValueError(f"Piece `{piece_name}` was not registered with the factory.")
        