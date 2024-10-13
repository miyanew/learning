from Directory import Directory
from File import File


def main():
    root_dir = Directory("root")

    usr_dir = Directory("usr")
    root_dir.add(usr_dir)

    yuki = Directory("yuki")
    usr_dir.add(yuki)

    file = File("Composite.py", 100)
    yuki.add(file)
    root_dir.print_list()

    print()
    print(f"file = {file.get_full_name()}")
    print(f"yuki = {yuki.get_full_name()}")


if __name__ == "__main__":
    main()
