import yaml

class Config:
    """
    Class for storing configuration data.
    """
    def __init__(self, config_path: str):
        with open(config_path, "r") as file:
            _data = yaml.safe_load(file)
            self.pieces = _data["pieces"]
            self.pattern = _data["pattern"]
            