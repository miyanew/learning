import sys

from director import Director
from html_builder import HTMLBuilder
from text_builder import TextBuilder


class Main:
    def main(self, args):
        if len(args) != 1:
            self.usage()
            sys.exit(0)

        if args[0] == "text":
            text_builder = TextBuilder()
            director = Director(text_builder)
            director.construct()
            result = text_builder.get_text_result()
            print(result)

        elif args[0] == "html":
            html_builder = HTMLBuilder()
            director = Director(html_builder)
            director.construct()
            filename = html_builder.get_html_result()
            print(f"HTMLファイル {filename} が作成されました。")

        else:
            self.usage()
            sys.exit(0)

    def usage(self):
        print("Usage: python main.py text       テキストで文書作成")
        print("Usage: python main.py html       HTMLファイルで文書作成")


if __name__ == "__main__":
    main_instance = Main()
    main_instance.main(sys.argv[1:])
