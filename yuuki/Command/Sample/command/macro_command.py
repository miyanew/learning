from collections import deque
from .command import Command


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
