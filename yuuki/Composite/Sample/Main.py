from Directory import Directory
from File import File


def main():
    print("Making root entries...")
    root_dir = Directory("root")
    bin_dir = Directory("bin")
    tmp_dir = Directory("tmp")
    usr_dir = Directory("usr")
    root_dir.add(bin_dir)
    root_dir.add(tmp_dir)
    root_dir.add(usr_dir)
    bin_dir.add(File("vi", 10000))
    bin_dir.add(File("latex", 20000))
    root_dir.print_list()
    print()

    print("Making user entries...")
    yuki = Directory("yuki")
    hanako = Directory("hanako")
    tomura = Directory("tomura")
    usr_dir.add(yuki)
    usr_dir.add(hanako)
    usr_dir.add(tomura)
    yuki.add(File("diary.html", 100))
    yuki.add(File("Composite.java", 200))
    hanako.add(File("memo.tex", 300))
    tomura.add(File("game.doc", 400))
    tomura.add(File("junk.mail", 500))
    root_dir.print_list()


if __name__ == "__main__":
    main()
