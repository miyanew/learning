from dataclasses import dataclass
from command.command import Command
from .drawable import Drawable


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
