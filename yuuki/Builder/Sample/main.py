import sys

from director import Director
from html_builder import HTMLBuilder
from text_builder import TextBuilder


def usage():
    print("Usage: python main.py text       テキストで文書作成")
    print("Usage: python main.py html       HTMLファイルで文書作成")


def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(0)

    if sys.argv[1] == "text":
        text_builder = TextBuilder()
        director = Director(text_builder)
        director.construct()
        result = text_builder.get_text_result()
        print(result)
    elif sys.argv[1] == "html":
        html_builder = HTMLBuilder()
        director = Director(html_builder)
        director.construct()
        filename = html_builder.get_html_result()
        print(f"HTMLファイル {filename} が作成されました。")
    else:
        usage()
        sys.exit(0)


if __name__ == "__main__":
    main()
