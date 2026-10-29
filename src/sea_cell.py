"""Ein Vektorfeld im Seeraster, mit Maus- und Tastaturbedienung."""
import tkinter as tk

from ship_art import draw_svg


SEA = "#143c50"
GRID = "#28576b"
FOAM = "#d8eef3"
CORAL = "#ff8b70"


class SeaCell(tk.Canvas):
    """Zeichnet Schiffsausschnitte und Treffer; ``text`` bleibt das Feldsymbol.

    Ein Schiff wird in voller Laenge in jedem seiner Felder gezeichnet. Die
    Canvas-Grenze schneidet den jeweiligen Ausschnitt ohne Rasterbilder aus.
    """

    def __init__(self, master, field, *, size=32, command=None):
        super().__init__(
            master, width=size, height=size, background=SEA, borderwidth=0,
            highlightthickness=0, takefocus=command is not None,
            cursor="crosshair" if command else "",
        )
        self.field = field
        self.size = size
        self.command = command
        self.symbol = ""
        self.ship = None
        self.bind("<Button-1>", self._click)
        self.bind("<Return>", lambda event: self.invoke())
        self.bind("<space>", lambda event: self.invoke())
        self.bind("<Enter>", self._hover)
        self.bind("<Leave>", lambda event: self.delete("hover"))
        self.bind("<FocusIn>", self._hover)
        self.bind("<FocusOut>", lambda event: self.delete("hover"))
        for key, dx, dy in (("Left", -1, 0), ("Right", 1, 0), ("Up", 0, -1), ("Down", 0, 1)):
            self.bind(f"<{key}>", lambda event, x=dx, y=dy: self._move_focus(x, y))

    def cget(self, key):
        if key == "text":
            return self.symbol
        return super().cget(key)

    def invoke(self):
        if self.command is not None and str(self.cget("state")) == "normal":
            return self.command()

    def _click(self, event):
        if self.command is not None:
            self.focus_set()
            self.invoke()

    def _move_focus(self, dx, dy):
        column = ord(self.field[0]) - ord("A") + dx
        row = int(self.field[1:]) + dy
        if 0 <= column < 10 and 1 <= row <= 10:
            field = f"{chr(ord('A') + column)}{row}"
            for widget in self.master.winfo_children():
                if isinstance(widget, SeaCell) and widget.field == field:
                    widget.focus_set()
                    break
        return "break"

    def _hover(self, event=None):
        self.delete("hover")
        if self.command is None or str(self.cget("state")) != "normal":
            return
        n = self.size
        self.create_rectangle(2, 2, n - 2, n - 2, outline="#72d5dd", width=2, tags="hover")

    def set_content(self, symbol, *, ship=None, background=SEA, state="normal"):
        self.symbol, self.ship = symbol, ship
        self.configure(background=background, state=state)
        if state == "disabled":
            self.delete("hover")
        self.delete("art")
        n = self.size
        self.create_line(n - 1, 0, n - 1, n, fill=GRID, tags="art")
        self.create_line(0, n - 1, n, n - 1, fill=GRID, tags="art")
        if ship:
            ship_type, index, count, vertical = ship
            draw_svg(
                self, ship_type, 0 if vertical else -index * n,
                -index * n if vertical else 0, count * n, n,
                vertical=vertical, tags=("art", "ship"),
            )
        if symbol == "·":
            self.create_oval(n / 2 - 3, n / 2 - 3, n / 2 + 3, n / 2 + 3,
                             fill="#8bafc0", outline="", tags="art")
        elif symbol in ("X", "#"):
            self.create_oval(6, 6, n - 6, n - 6, fill="#6b3a3b", outline=CORAL, tags="art")
            self.create_line(11, 11, n - 11, n - 11, fill="#ffe1b4", width=2, tags="art")
            self.create_line(n - 11, 11, 11, n - 11, fill="#ffe1b4", width=2, tags="art")
            if symbol == "#":
                self.create_oval(3, 3, n - 3, n - 3, outline=CORAL, width=2, tags="art")
        self.tag_raise("explosion")
        self.tag_raise("hover")
