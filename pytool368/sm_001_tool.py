import json
import os


def main():
    hosts = load_target_hosts(node_type="sm")

    username_node_dict = extract_username_node(hosts)
    print("ユーザー名@ノード リスト:")
    for host, info in username_node_dict.items():
        print(f"{host}: {info}")

    # print("全ホスト情報:")
    # print_host_info(hosts)


def load_target_hosts(node_type=None):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "config", "sa_nf.json")
    with open(json_path, "r") as file:
        hosts_config = json.load(file)
        if node_type is None:
            return hosts_config
        else:
            return {h: c for h, c in hosts_config.items() if c["node"] == node_type}


def extract_username_node(hosts):
    return {
        host: {"username": config["username"], "node": config["node"]}
        for host, config in hosts.items()
    }


# def print_host_info(hosts):
#     for host, config in hosts.items():
#         print(f"ホスト: {host}")
#         print(f"  IPアドレス: {config['ip_address']}")
#         print(f"  ユーザー名: {config['username']}")
#         print(f"  ノード: {config['node']}")
#         print()


if __name__ == "__main__":
    main()
