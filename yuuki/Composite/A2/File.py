from Entry import Entry


class File(Entry):
    def __init__(self, name: str, size: int):
        super().__init__()
        self.name = name
        self.size = size

    def get_name(self) -> str:
        return self.name

    def get_size(self) -> int:
        return self.size
