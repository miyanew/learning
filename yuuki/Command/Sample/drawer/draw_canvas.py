import tkinter as tk
from .drawable import Drawable
from command.macro_command import MacroCommand


class DrawCanvas(tk.Canvas, Drawable):
    def __init__(self, width: int, height: int, history: MacroCommand):
        super().__init__(width=width, height=height, bg="white")
        self.history = history
        self.radius = 6
        self.color = "red"

    def draw(self, x: int, y: int) -> None:
        x1 = x - self.radius
        y1 = y - self.radius
        x2 = x + self.radius
        y2 = y + self.radius
        self.create_oval(x1, y1, x2, y2, fill=self.color, outline=self.color)

    def redraw(self) -> None:
        self.delete("all")
        self.history.execute()
