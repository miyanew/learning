from typing import Protocol


class Drawable(Protocol):
    def draw(self, x: int, y: int) -> None:
        pass
