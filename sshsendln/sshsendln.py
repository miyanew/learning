import argparse
import json
import os
import sys
from typing import Dict, Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(SCRIPT_DIR, "config")

sys.path.append(CONFIG_DIR)


def main(opts):
    ssh_config = load_ssh_config()
    print(ssh_config)
    print(opts.host)


def load_ssh_config() -> Dict[str, Any]:
    file_path = os.path.join(CONFIG_DIR, "ssh_host.json")
    return load_json_file(file_path)


def load_json_file(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}") from None
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {file_path}: {str(e)}") from None
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}") from None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("command", type=str, nargs="?", help="送信コマンド")
    parser.add_argument("--host", "-H", type=str, help="ホスト名")
    args, unknown = parser.parse_known_args()
    if unknown:
        print(f"Unknown arguments: {unknown}")
        parser.print_help()
        exit(1)

    try:
        main(args)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
