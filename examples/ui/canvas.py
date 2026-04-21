import tkinter as tk

from cynmeith import Board
from cynmeith.core.piece import Piece
from cynmeith.utils import Coord

from .spec import BoardTheme


class BoardCanvas(tk.Canvas):
    def __init__(
        self,
        master: tk.Misc,
        board: Board,
        theme: BoardTheme,
        cell_size: int = 60,
        margin: int = 28,
        show_river: bool = False,
    ):
        self.board = board
        self.theme = theme
        self.cell_size = cell_size
        self.margin = margin
        self.show_river = show_river
        super().__init__(
            master,
            width=board.width * cell_size + margin * 2,
            height=board.height * cell_size + margin * 2,
            highlightthickness=0,
        )

    def position_from_event(self, event: tk.Event) -> Coord | None:
        row = (event.y - self.margin) // self.cell_size
        col = (event.x - self.margin) // self.cell_size
        position = Coord(row, col)
        if not self.board.is_in_bounds(position):
            return None
        return position

    def _cell_origin(self, row: int, col: int) -> tuple[int, int, int, int]:
        x0 = self.margin + col * self.cell_size
        y0 = self.margin + row * self.cell_size
        x1 = x0 + self.cell_size
        y1 = y0 + self.cell_size
        return x0, y0, x1, y1

    def _draw_coordinates(self) -> None:
        for col in range(self.board.width):
            label = chr(ord("A") + col) if self.board.width <= 26 else str(col + 1)
            x = self.margin + col * self.cell_size + self.cell_size // 2
            self.create_text(
                x, self.margin // 2, text=label, font=("Arial", 11, "bold")
            )
            self.create_text(
                x,
                self.margin + self.board.height * self.cell_size + self.margin // 2,
                text=label,
                font=("Arial", 11, "bold"),
            )

        for row in range(self.board.height):
            label = str(self.board.height - row)
            y = self.margin + row * self.cell_size + self.cell_size // 2
            self.create_text(
                self.margin // 2, y, text=label, font=("Arial", 11, "bold")
            )
            self.create_text(
                self.margin + self.board.width * self.cell_size + self.margin // 2,
                y,
                text=label,
                font=("Arial", 11, "bold"),
            )

    def render(self, selected_piece: Piece | None, valid_moves: list[Coord]) -> None:
        self.delete("all")
        self._draw_coordinates()

        for row in range(self.board.height):
            for col in range(self.board.width):
                color = (
                    self.theme.light_color
                    if (row + col) % 2 == 0
                    else self.theme.dark_color
                )
                x0, y0, x1, y1 = self._cell_origin(row, col)
                self.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill=color,
                    outline=self.theme.board_line_color,
                )

        if self.show_river and self.board.width == 9 and self.board.height == 10:
            river_y = self.margin + 5 * self.cell_size
            self.create_line(
                self.margin,
                river_y,
                self.margin + self.board.width * self.cell_size,
                river_y,
                fill=self.theme.river_color,
                width=3,
                dash=(10, 6),
            )

        for move in valid_moves:
            x0, y0, x1, y1 = self._cell_origin(move.r, move.c)
            x0 += 20
            y0 += 20
            x1 -= 20
            y1 -= 20
            self.create_oval(
                x0, y0, x1, y1, fill=self.theme.highlight_color, outline=""
            )

        if selected_piece is not None:
            position = selected_piece.position
            x0, y0, x1, y1 = self._cell_origin(position.r, position.c)
            x0 += 4
            y0 += 4
            x1 -= 4
            y1 -= 4
            self.create_rectangle(
                x0, y0, x1, y1, outline=self.theme.selected_color, width=3
            )

        for row in range(self.board.height):
            for col in range(self.board.width):
                piece = self.board.at(Coord(row, col))
                if piece is None:
                    continue
                fill = (
                    self.theme.piece_color_true
                    if piece.side
                    else self.theme.piece_color_false
                )
                x0, y0, _, _ = self._cell_origin(row, col)
                self.create_text(
                    x0 + self.cell_size // 2,
                    y0 + self.cell_size // 2,
                    text=piece.get_symbol_with_side(),
                    font=("Arial", 24, "bold"),
                    fill=fill,
                )
