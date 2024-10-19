from framework.product import Product


class IDCard(Product):
    def __init__(self, owner: str) -> None:
        print(f"{owner}のカードを作ります。")
        self.__owner = owner

    def use(self) -> None:
        print(f"{self}を使います。")

    def __str__(self) -> str:
        return f"[IDCard:{self.__owner}]"

    @property
    def owner(self) -> str:
        return self.__owner
