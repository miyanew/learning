import argparse
import os

from mm_connect_b.config_loader import load_json_file
from mm_connect_b.director import Director
from mm_connect_b.session_builder_pod import SessionBuilderPod
# from mm_connect_b.session_builder_intaract import SessionBuilderIntaract
# from mm_connect_b.session_builder_nonintaract import SessionBuilderNonintaract

CONFIG_NAME = "ssh_host.json"

def main(opts: argparse.Namespace) -> None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_dir, CONFIG_NAME)
    ssh_configs = load_json_file(config_file)

    host_config = ssh_configs[opts.host]
    connect_type = host_config.get("connect_type", "")

    if connect_type == "paramiko_pod":
        builder = SessionBuilderPod(opts.host, ssh_configs) 
        director = Director(builder)
        director.construct()
        host = builder.get_instance_pod()
    elif connect_type == "paramiko_intaract":
        pass
    else:
        pass

    # return host

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
