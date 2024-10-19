import tkinter as tk
from command.macro_command import MacroCommand
from drawer.draw_canvas import DrawCanvas
from drawer.draw_command import DrawCommand, Point


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
