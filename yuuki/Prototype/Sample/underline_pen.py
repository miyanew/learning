from framework.product import Product


class UnderlinePen(Product):
    def __init__(self, ulchar: str):
        self.ulchar = ulchar

    def use(self, s: str) -> None:
        ulen = len(s)
        print(s)
        print(self.ulchar * ulen)
