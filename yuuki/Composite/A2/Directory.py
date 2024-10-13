from Entry import Entry
from typing import List


class Directory(Entry):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.directory: List[Entry] = []

    def get_name(self) -> str:
        return self.name

    def get_size(self) -> int:
        return sum(entry.get_size() for entry in self.directory)

    def print_list(self, prefix: str = ""):
        super().print_list(prefix)
        for entry in self.directory:
            entry.print_list(f"{prefix}/{self.name}")

    def add(self, entry: Entry):
        self.directory.append(entry)
        entry.set_parent(self)
        return self
