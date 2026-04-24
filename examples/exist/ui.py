from __future__ import annotations

import tkinter as tk

from cynmeith.utils import Coord, InvalidMoveError, MoveHistoryError
from examples.ui.app import TkGameApp
from examples.ui.spec import GameSpec


class ExistTkGameApp(TkGameApp):
    def __init__(self, spec: GameSpec):
        super().__init__(spec)

        self.place_mode = False
        self.reserves = self.game.reserves

        self.reserve_frame = tk.Frame(self)
        self.reserve_frame.pack(fill="x", pady=4)

        self.place_button = tk.Button(
            self.reserve_frame,
            text="Place From Reserve",
            command=self.toggle_place_mode,
            width=18,
        )
        self.place_button.pack(side="left", padx=4)

        self.end_turn_button = tk.Button(
            self.reserve_frame,
            text="End Turn",
            command=self.end_turn,
            width=12,
        )
        self.end_turn_button.pack(side="left", padx=4)

        self.reserve_label = tk.Label(self.reserve_frame, text="", width=28)
        self.reserve_label.pack(side="left", padx=4)

        self.turn_info_label = tk.Label(self.reserve_frame, text="", width=42)
        self.turn_info_label.pack(side="left", padx=4)

        self.update_reserve_display()

    def toggle_place_mode(self) -> None:
        current_side = self.game.current_side
        if current_side is None or not self.reserves.has_pieces(current_side):
            self.set_status("No reserve pieces available for the current player.")
            return

        self.place_mode = not self.place_mode
        if self.place_mode:
            self.place_button.config(bg="#f0c94d", fg="#111111")
            self.set_status("Place mode on. Click an empty square to place a piece.")
        else:
            self.place_button.config(bg="SystemButtonFace", fg="SystemButtonText")
            self.set_status("Place mode off.")
        self.refresh()

    def end_turn(self) -> None:
        try:
            self.game.end_turn()
        except InvalidMoveError as exc:
            self.set_status(str(exc))
            return

        self.place_mode = False
        self.clear_selection()
        self.set_status("Turn ended.")
        self.refresh()

    def update_reserve_display(self) -> None:
        if not hasattr(self, "reserve_label") or not hasattr(self, "turn_info_label"):
            return

        black_count = self.reserves.get_count(True)
        white_count = self.reserves.get_count(False)
        self.reserve_label.config(
            text=f"Reserves B/W: {black_count}/{white_count}"
        )

        turn_info = self.game.turn_policy.get_turn_info()
        can_end = "Yes" if turn_info["can_end_turn"] else "No"
        self.turn_info_label.config(
            text=(
                f"{turn_info['side']} | {turn_info['turn_type']} | "
                f"Actions {turn_info['actions_used']}/{turn_info['max_actions']} | "
                f"End now: {can_end}"
            )
        )

    def on_click(self, event: tk.Event) -> None:
        position = self.board_canvas.position_from_event(event)
        if position is None:
            return

        if self.game.is_over:
            self.clear_selection()
            self.set_status("Game is over.")
            return

        if self.place_mode:
            self.attempt_place(position)
            return

        super().on_click(event)

    def attempt_place(self, position: Coord) -> None:
        if not self.board.is_empty(position):
            self.set_status("That square is already occupied.")
            return

        try:
            self.game.move(Coord.null(), position, "PLACE")
        except InvalidMoveError as exc:
            self.set_status(f"Cannot place there: {exc}")
        else:
            self.set_status(f"Placed a piece at {position}.")

        self.place_mode = False
        self.place_button.config(bg="SystemButtonFace", fg="SystemButtonText")
        self.clear_selection()
        self.refresh()

    def move_selected_piece(self, position: Coord) -> None:
        if self.selected_piece is None:
            return

        try:
            self.game.move(self.selected_piece.position, position, "MOVE")
        except InvalidMoveError as exc:
            self.set_status(str(exc))
        else:
            self.set_status(f"Moved to {position}.")

        self.place_mode = False
        self.place_button.config(bg="SystemButtonFace", fg="SystemButtonText")
        self.clear_selection()
        self.refresh()

    def reset_board(self) -> None:
        self.place_mode = False
        self.place_button.config(bg="SystemButtonFace", fg="SystemButtonText")
        super().reset_board()
        self.update_reserve_display()

    def undo_move(self) -> None:
        try:
            self.game.undo_move()
        except MoveHistoryError as exc:
            self.set_status(str(exc))
            return

        self.place_mode = False
        self.place_button.config(bg="SystemButtonFace", fg="SystemButtonText")
        self.clear_selection()
        self.set_status("Move undone.")
        self.refresh()

    def redo_move(self) -> None:
        try:
            self.game.redo_move()
        except MoveHistoryError as exc:
            self.set_status(str(exc))
            return

        self.place_mode = False
        self.place_button.config(bg="SystemButtonFace", fg="SystemButtonText")
        self.clear_selection()
        self.set_status("Move redone.")
        self.refresh()

    def refresh(self) -> None:
        super().refresh()
        if hasattr(self, "reserves"):
            self.update_reserve_display()
