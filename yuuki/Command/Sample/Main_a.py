# main.py
import tkinter as tk
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Protocol


# Command interface
class Command(Protocol):
    def execute(self) -> None:
        pass


# MacroCommand class
class MacroCommand:
    def __init__(self):
        self.commands: deque[Command] = deque()

    def execute(self) -> None:
        for cmd in self.commands:
            cmd.execute()

    def append(self, cmd: Command) -> None:
        if cmd is self:
            raise ValueError("infinite loop caused by append")
        self.commands.append(cmd)

    def undo(self) -> None:
        if self.commands:
            self.commands.pop()

    def clear(self) -> None:
        self.commands.clear()


# Drawable interface
class Drawable(Protocol):
    def draw(self, x: int, y: int) -> None:
        pass


# DrawCommand class
@dataclass
class Point:
    x: int
    y: int


class DrawCommand:
    def __init__(self, drawable: Drawable, position: Point):
        self.drawable = drawable
        self.position = position

    def execute(self) -> None:
        self.drawable.draw(self.position.x, self.position.y)


# DrawCanvas class
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


# Main application class
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Command Pattern Sample")
        self.history = MacroCommand()
        self.canvas = DrawCanvas(400, 400, self.history)

        # Create clear button
        clear_button = tk.Button(self, text="clear", command=self.clear)
        clear_button.pack(pady=5)

        # Pack canvas
        self.canvas.pack(pady=5)

        # Bind mouse events
        self.canvas.bind("<B1-Motion>", self.mouse_dragged)

        # Window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def mouse_dragged(self, event) -> None:
        point = Point(event.x, event.y)
        cmd = DrawCommand(self.canvas, point)
        self.history.append(cmd)
        cmd.execute()

    def clear(self) -> None:
        self.history.clear()
        self.canvas.redraw()

    def on_closing(self) -> None:
        self.quit()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
