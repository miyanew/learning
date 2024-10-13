from abc import ABC, abstractmethod


class Entry(ABC):
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
