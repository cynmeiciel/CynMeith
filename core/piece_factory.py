from importlib import import_module
from core.config import Config
from pieces.piece import Piece
from utils import Coord, PieceSymbol, PieceError

class PieceFactory:
    """
    Factory class for creating pieces.
    """
    def __init__(self):
        self.piece_classes = {}
    
    def register_piece(self, piece_symbol: PieceSymbol, piece_class: Piece) -> None:
        """
        Register a piece class with the factory.
        """
        self.piece_classes[piece_symbol] = piece_class

    def unregister_piece(self, piece_symbol: PieceSymbol) -> None:
        """
        Unregister a piece class from the factory.
        """
        del self.piece_classes[piece_symbol]
        
    def register_pieces(self, config: Config) -> None:
        """
        Register all pieces with the factory.
        """
        for piece_name in config.pieces:
            path = config.get_piece_path(piece_name)
            module = import_module(f"pieces.{path}")
            piece_cls = getattr(module, piece_name)
            self.register_piece(config.get_piece_symbol(piece_name), piece_cls)            

    def create_piece(self, piece_symbol: PieceSymbol, position: Coord) -> Piece:
        """
        Create a piece. Upper case for white, lower case for black.
        """
        if piece_symbol == " " or piece_symbol is None:
            return None
        
        side = piece_symbol.isupper() # True if piece is white, False if black
        piece_cls = self.piece_classes.get(piece_symbol.upper())
        if not piece_cls:
            raise PieceError(f"Piece `{piece_symbol}` is not registered.")
        return piece_cls(side, position)

        