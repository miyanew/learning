from builder import Builder


class TextBuilder(Builder):
    def __init__(self):
        self.sb = []

    def make_title(self, title):
        self.sb.append("==============================\n")
        self.sb.append(f"『{title}』\n\n")

    def make_string(self, string):
        self.sb.append(f"■{string}\n\n")

    def make_items(self, items):
        for item in items:
            self.sb.append(f"　・{item}\n")
        self.sb.append("\n")

    def close(self):
        self.sb.append("==============================\n")

    def get_text_result(self):
        return "".join(self.sb)
