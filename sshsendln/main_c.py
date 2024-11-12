import argparse
import os

from mm_connect_c.build_session_manager import BuildSessionManager

CONFIG_NAME = "ssh_host.json"


def main(opts: argparse.Namespace) -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_dir, CONFIG_NAME)

    mm_connect = BuildSessionManager(config_file)
    target_node = mm_connect.build(opts.host)

    print(f"==={target_node.host_name}===")
    print(target_node.send_command(opts.command))


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
