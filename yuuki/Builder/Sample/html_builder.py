from builder import Builder


class HTMLBuilder(Builder):
    def __init__(self):
        self.filename = "untitled.html"
        self.sb = []

    def make_title(self, title):
        self.filename = f"{title}.html"
        self.sb.append("<!DOCTYPE html>\n")
        self.sb.append("<html>\n")
        self.sb.append("<head><title>")
        self.sb.append(title)
        self.sb.append("</title></head>\n")
        self.sb.append("<body>\n")
        self.sb.append(f"<h1>{title}</h1>\n\n")

    def make_string(self, string):
        self.sb.append(f"<p>{string}</p>\n\n")

    def make_items(self, items):
        self.sb.append("<ul>\n")
        for item in items:
            self.sb.append(f"<li>{item}</li>\n")
        self.sb.append("</ul>\n\n")

    def close(self):
        self.sb.append("</body>\n</html>\n")
        with open(self.filename, "w") as file:
            file.write("".join(self.sb))

    def get_html_result(self):
        return self.filename
