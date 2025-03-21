from yaml import safe_load
from cynmeith.utils import PieceName

class Config:
    """
    Class for storing and interacting with configuration data.
    This class should only be used when initializing the game.
    """
    def __init__(self, config_path: str):
        with open(config_path, "r") as file:
            _data = safe_load(file)
            self.pieces = _data["pieces"]
            self.width = _data["width"]
            self.height = _data["height"]
            self.fen = _data["fen"]
            
    def __str__(self):
        return f"Config: {self.pieces}, {self.pattern}"
    
    def get_piece_property(self, piece: PieceName, prop: str):
        return self.pieces[piece][prop]
    
    def get_piece_path(self, piece: PieceName):
        return self.pieces[piece].get("class_path", piece.lower())
    
    def get_piece_symbol(self, piece: PieceName):
        return self.pieces[piece].get("symbol", piece[0].upper())
