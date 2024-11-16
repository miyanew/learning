import csv
import sys
from typing import Any, Iterator, List


def check_memory_usage(data: Any) -> None:
    """メモリ使用量を確認する補助関数"""
    print(f"Object size: {sys.getsizeof(data)} bytes")


def any_example(file: str) -> List[str]:
    """
    ほかの例：ファイルをリストにセットする
    """
    lines = []
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for line in reader:
            lines.append(line)
        check_memory_usage(lines)
        return lines


def bad_example(file: str) -> List[str]:
    """
    悪い例：ファイル全体を一度にメモリに読み込む
    """
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        check_memory_usage(content)
        return content.splitlines()


def good_example(file: str) -> Iterator[List[str]]:
    """
    良い例：ファイルを1行ずつ読み込む
    """
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        check_memory_usage(reader)
        for row in reader:
            yield row


def main(file_path):
    print("Any example (reading entire file):")
    try:
        data = any_example(file_path)
        for i, row in enumerate(data):
            if i < 5:
                print(f"Row {i}: {row}")
            else:
                break
    except Exception as e:
        print(f"Error: {e}")

    print("Bad example (reading entire file):")
    try:
        data = bad_example(file_path)
        for i, row in enumerate(data):
            if i < 5:
                print(f"Row {i}: {row}")
            else:
                break
    except Exception as e:
        print(f"Error: {e}")

    print("\nGood example (reading line by line):")
    data_iterator = good_example(file_path)
    for i, row in enumerate(data_iterator):
        if i < 5:
            print(f"Row {i}: {row}")
        else:
            break


if __name__ == "__main__":
    main("./test_data.csv")
