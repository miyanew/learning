from abc import ABC, abstractmethod


class Entry(ABC):
    def __init__(self):
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_size(self) -> int:
        pass

    def print_list(self, prefix: str = ""):
        print(f"{prefix}/{self}")

    def __str__(self):
        return f"{self.get_name()} ({self.get_size()})"

    def get_full_name(self) -> str:
        full_name = []
        entry = self
        while entry:
            full_name.insert(0, entry.get_name())
            entry = entry.parent
        return "/" + "/".join(full_name)
