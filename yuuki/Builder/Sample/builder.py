from abc import ABC, abstractmethod


class Builder(ABC):
    @abstractmethod
    def make_title(self, title: str):
        pass

    @abstractmethod
    def make_string(self, string: str):
        pass

    @abstractmethod
    def make_items(self, items: list):
        pass

    @abstractmethod
    def close(self):
        pass
