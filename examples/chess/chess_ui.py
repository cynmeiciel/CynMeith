import tkinter as tk
from cynmeith import Board, Config
from cynmeith.utils import Coord
from chess_manager import ChessManager

class ChessUI(tk.Tk):
    def __init__(self, config_path: str):
        super().__init__()

        self.title("Chess")
        self.board = Board(Config(config_path), ChessManager)
        self.selected_piece = None
        self.valid_moves = []

        self.cell_size = 60
        self.canvas = tk.Canvas(self, width=self.board.width * self.cell_size, height=self.board.height * self.cell_size)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()

    def draw_board(self):
        """Draws the board and pieces."""
        self.canvas.delete("all")

        # Draw grid
        for x in range(self.board.width):
            for y in range(self.board.height):
                color = "#EEE" if (x + y) % 2 == 0 else "#888"
                self.canvas.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=color, outline="black"
                )

        # Highlight valid moves
        for move in self.valid_moves:
            y, x = move.r, move.c
            self.canvas.create_oval(
                x * self.cell_size + 20, y * self.cell_size + 20,
                (x + 1) * self.cell_size - 20, (y + 1) * self.cell_size - 20,
                fill="yellow"
            )

        # Draw pieces
        for x in range(self.board.width):
            for y in range(self.board.height):
                piece = self.board.at(Coord(y, x))
                if piece:
                    self.canvas.create_text(
                        x * self.cell_size + self.cell_size // 2,
                        y * self.cell_size + self.cell_size // 2,
                        text=piece.get_symbol_with_side(),
                        font=("Arial", 24, "bold")
                    )

    def on_click(self, event):
        """Handles clicking on the board."""
        y, x = event.x // self.cell_size, event.y // self.cell_size
        position = Coord(x, y)

        if self.selected_piece:
            # If a piece is already selected, try to move it
            if position in self.valid_moves:
                self.board.move(self.selected_piece.position, position)
                self.selected_piece = None
                self.valid_moves = []
            else:
                self.selected_piece = None
                self.valid_moves = []
        else:
            # Select a piece
            piece = self.board.at(position)
            if piece:
                self.selected_piece = piece
                self.valid_moves = self.board.get_valid_moves(position)
            else:
                self.valid_moves = []

        print(f"Selected piece: {self.selected_piece.position if self.selected_piece else None}")
        self.draw_board()
