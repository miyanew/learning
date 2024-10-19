from .product import Product


class Manager:
    def __init__(self):
        self.showcase = {}

    def register(self, name: str, prototype: Product) -> None:
        self.showcase[name] = prototype

    def create(self, prototype_name: str) -> Product:
        p = self.showcase.get(prototype_name)
        return p.create_copy() if p else None
