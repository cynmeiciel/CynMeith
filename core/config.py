import yaml
# from importlib import import_module
# from core.piece_factory import PieceFactory

class Config:
    """
    Class for storing and interacting with configuration data.
    This class should only be used when initializing the game.
    """
    def __init__(self, config_path: str):
        with open(config_path, "r") as file:
            _data = yaml.safe_load(file)
            self.pieces = _data["pieces"]
            self.width = _data["width"]
            self.height = _data["height"]
            self.fen = _data["fen"]
            
    def __str__(self):
        return f"Config: {self.pieces}, {self.pattern}"
    
    def get_piece_property(self, piece: str, prop: str):
        return self.pieces[piece][prop]
    
    def get_piece_path(self, piece: str):
        return self.pieces[piece]["class_path"]
    
    def get_piece_symbol(self, piece: str):
        return self.pieces[piece]["symbol"]
    
    # def register_pieces(self, factory: PieceFactory):
    #     """
    #     Register all pieces with the factory.
    #     """
    #     for piece_name, piece_data in self.pieces.items():
    #         module = import_module(piece_data["class_path"])
    #         piece_cls = getattr(module, piece_name)
    #         factory.register_piece(piece_data["symbol"], piece_cls)
            