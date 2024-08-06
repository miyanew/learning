#! /usr/bin/env python3

import argparse
import sys


def main(options):
    if options["list"] is None:
        inp = sys.stdin.read()
    else:
        inp = options["list"]

    if options["d"] is None:
        delim = ", "
    else:
        delim = options["d"]

    # splitted = inp.strip().split()
    enclosed = [f'"{s}"' for s in inp]
    joined = f"{delim}".join(enclosed)
    print(joined)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("list", nargs='*', help="スペース区切りの文字列リスト")
    parser.add_argument("-d", nargs='?', help="区切り文字")
    args = parser.parse_args()
    arguments = vars(args)

main(arguments)
