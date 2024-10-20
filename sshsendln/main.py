import argparse

from mm_connect.mm_connect import SessionManagerFactory


def main(opts):
    hosts = SessionManagerFactory().create_sessions(opts.host)
    for host in hosts:
        print(f"==={host.host_name}===")
        print(host.send_command(opts.command))

    # host = SSHConnectionManager().get_host(opts.host)
    # print(f"==={host.host_name}===")
    # print(host.send_command(opts.command))


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
