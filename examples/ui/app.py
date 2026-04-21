import tkinter as tk

from cynmeith import Board, Config
from cynmeith.core.piece import Piece
from cynmeith.utils import Coord, InvalidMoveError, MoveHistoryError

from .canvas import BoardCanvas
from .spec import GameSpec
from .widgets import ControlBar, StatusBar


class TkGameApp(tk.Tk):
    def __init__(self, spec: GameSpec):
        super().__init__()

        self.spec = spec
        self.title(spec.title)
        self.board = Board(Config(str(spec.config_path)), spec.move_manager)
        self.selected_piece: Piece | None = None
        self.valid_moves = []

        self.board_canvas = BoardCanvas(
            self,
            self.board,
            spec.theme,
            show_river=spec.show_river,
        )
        self.board_canvas.pack()
        self.board_canvas.bind("<Button-1>", self.on_click)

        self.controls = ControlBar(
            self, self.undo_move, self.redo_move, self.reset_board
        )
        self.controls.pack(fill="x", pady=4)

        self.status_bar = StatusBar(self, spec.status_hint)
        self.status_bar.pack(fill="x")

        self.bind("<Control-z>", lambda _event: self.undo_move())
        self.bind("<Control-y>", lambda _event: self.redo_move())
        self.bind("<Control-r>", lambda _event: self.reset_board())

        self.refresh()

    def refresh(self) -> None:
        self.board_canvas.render(self.selected_piece, self.valid_moves)

    def clear_selection(self) -> None:
        self.selected_piece = None
        self.valid_moves = []

    def reset_board(self) -> None:
        self.board.reset()
        self.clear_selection()
        self.status_bar.set("Board reset.")
        self.refresh()

    def undo_move(self) -> None:
        try:
            self.board.history.undo_move()
        except MoveHistoryError as exc:
            self.status_bar.set(str(exc))
            return
        self.clear_selection()
        self.status_bar.set("Move undone.")
        self.refresh()

    def redo_move(self) -> None:
        try:
            self.board.history.redo_move()
        except MoveHistoryError as exc:
            self.status_bar.set(str(exc))
            return
        self.clear_selection()
        self.status_bar.set("Move redone.")
        self.refresh()

    def select_piece(self, position: Coord) -> None:
        piece = self.board.at(position)
        if piece is None:
            self.clear_selection()
            self.status_bar.set("Empty square.")
            return

        self.selected_piece = piece
        self.valid_moves = self.board.get_valid_moves(piece) or []
        self.status_bar.set(f"Selected {piece.__class__.__name__} at {piece.position}.")

    def move_selected_piece(self, position: Coord) -> None:
        if self.selected_piece is None:
            return
        try:
            self.board.move(self.selected_piece.position, position)
        except InvalidMoveError as exc:
            self.status_bar.set(str(exc))
        else:
            self.status_bar.set(f"Moved to {position}.")
        self.clear_selection()

    def on_click(self, event: tk.Event) -> None:
        position = self.board_canvas.position_from_event(event)
        if position is None:
            return

        clicked_piece = self.board.at(position)

        if self.selected_piece is None:
            self.select_piece(position)
        elif position in self.valid_moves:
            self.move_selected_piece(position)
        elif clicked_piece is None:
            self.clear_selection()
            self.status_bar.set("Selection cleared.")
        else:
            self.select_piece(position)

        self.refresh()
