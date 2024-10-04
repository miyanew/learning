import argparse
import traceback


def contains_string(options: argparse.Namespace) -> bool:
    try:
        with open(options.file, "r", encoding="utf-8") as f:
            return any(options.keyword in line for line in f)
    except FileNotFoundError:
        raise FileNotFoundError("file not found error") from None
    except IOError:
        raise IOError("file load error") from None


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
        print(contains_string(args))
    except (FileNotFoundError, IOError) as e:
        print(f"unexpected error: {e}")
        traceback.print_exc()
