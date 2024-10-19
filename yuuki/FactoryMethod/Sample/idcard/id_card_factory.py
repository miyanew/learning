from framework.factory import Factory
from framework.product import Product
from .id_card import IDCard


class IDCardFactory(Factory):
    def create_product(self, owner: str) -> Product:
        return IDCard(owner)

    def register_product(self, product: Product) -> None:
        print(f"{product}を登録しました。")
