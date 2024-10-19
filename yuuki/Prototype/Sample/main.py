from framework.manager import Manager
from message_box import MessageBox
from underline_pen import UnderlinePen


def main():
    # 準備
    manager = Manager()
    upen = UnderlinePen("-")
    mbox = MessageBox("*")
    sbox = MessageBox("/")

    # 登録
    manager.register("strong message", upen)
    manager.register("warning box", mbox)
    manager.register("slash box", sbox)

    # 生成と使用
    p1 = manager.create("strong message")
    p1.use("Hello, world.")
    print()

    p2 = manager.create("warning box")
    p2.use("Hello, world.")
    print()

    p3 = manager.create("slash box")
    p3.use("Hello, world.")


if __name__ == "__main__":
    main()
