from framework.factory import Factory
from framework.product import Product
from idcard.id_card_factory import IDCardFactory


def main() -> None:
    factory: Factory = IDCardFactory()
    card1: Product = factory.create("Hiroshi Yuki")
    card2: Product = factory.create("Tomura")
    card3: Product = factory.create("Hanako Sato")
    card1.use()
    card2.use()
    card3.use()


if __name__ == "__main__":
    main()
