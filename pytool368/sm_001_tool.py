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

    

# 前提:
#  - ツールのサポート対象 = ActivateなPython(いまなら3.8以上)が多い印象。つまり 3.6.8 はサポート外。
#  - VSCode拡張はインストールできず。WSL2はUbuntu20.04。謎のファイル更新権限エラー..
#  - pip install で入った。真偽不明ですが生成AIにきいた3.6系に対応しているツールVer。
#    - pip install isort==5.10.1
#    - pip install flake8==4.0.1
#    - pip install black==21.12b0

# python3.6 -m venv 環境名
# cd 環境名
# bin/activate
# pip install ...


# [Pythonのリンター・フォーマッターをしっかりと理解する（Flake8, Black, isort, mypy）](https://zenn.dev/tanny/articles/cdb555d6124a2a)
# [Blackできれいに自動整形！flake8とBlack導入と実行 \#Python \- Qiita](https://qiita.com/tsu_0514/items/2d52c7bf79cd62d4af4a)

# Python Package Index（PyPI）は、プログラミング言語Python用のソフトウェアのリポジトリです。
# https://pypi.org/


# 競合回避のための設定
# Flake8の設定ファイル（.flake8またはsetup.cfg）をプロジェクトのルートディレクトリに作成し、
# 以下の内容を追加。

# [flake8]
# max-line-length = 88
# extend-ignore = E203, W503
