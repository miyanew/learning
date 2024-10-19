from abc import ABC, abstractmethod
import copy


class Product(ABC):
    @abstractmethod
    def use(self, s: str) -> None:
        pass

    def create_copy(self):
        return copy.deepcopy(self)
