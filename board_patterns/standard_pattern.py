from board_pattern import BoardPattern

class StandardPattern(BoardPattern):
    def __init__(self):
        super().__init__(8, 8)
        self.grid = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]

class EmptyPattern(BoardPattern):
    def __init__(self):
        super().__init__(8, 8)
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]