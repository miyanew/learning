import argparse
import traceback


def search_keyword_in_file(file_path: str, keyword: str) -> bool:
    content = load_file_contents(file_path)
    return contains_string(content, keyword)


def load_file_contents(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError("file not found error") from None
    except IOError:
        raise IOError("file load error") from None


def contains_string(text: str, keyword: str) -> bool:
    return keyword in text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--file", "-F", type=str, help="テキストファイルのパス")
    parser.add_argument("--keyword", "-K", type=str, help="検索ワード")

    args, unknown = parser.parse_known_args()

    if unknown:
        print(f"Unknown arguments: {unknown}")
        parser.print_help()
        exit(1)

    try:
        print(search_keyword_in_file(args.file, args.keyword))
    except (FileNotFoundError, IOError) as e:
        print(f"unexpected error: {e}")
        traceback.print_exc()
