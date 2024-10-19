from abc import ABC, abstractmethod
from .product import Product


class Factory(ABC):
    def create(self, owner: str) -> Product:
        p = self.create_product(owner)
        self.register_product(p)
        return p

    @abstractmethod
    def create_product(self, owner: str) -> Product:
        pass

    @abstractmethod
    def register_product(self, product: Product) -> None:
        pass
