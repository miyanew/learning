from framework.product import Product


class MessageBox(Product):
    def __init__(self, decochar: str):
        self.decochar = decochar

    def use(self, s: str) -> None:
        decolen = 1 + len(s) + 1
        print(self.decochar * decolen)
        print(f"{self.decochar}{s}{self.decochar}")
        print(self.decochar * decolen)
