import tkinter as tk


class ControlBar(tk.Frame):
    def __init__(self, master: tk.Misc, on_undo, on_redo, on_reset):
        super().__init__(master)
        tk.Button(self, text="Undo", command=on_undo).pack(side="left", padx=4)
        tk.Button(self, text="Redo", command=on_redo).pack(side="left", padx=4)
        tk.Button(self, text="Reset", command=on_reset).pack(side="left", padx=4)


class StatusBar(tk.Frame):
    def __init__(self, master: tk.Misc, initial_text: str):
        super().__init__(master)
        self.text_var = tk.StringVar(value=initial_text)
        tk.Label(self, textvariable=self.text_var, anchor="w").pack(fill="x")

    def set(self, text: str) -> None:
        self.text_var.set(text)
