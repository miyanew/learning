import json
from typing import Dict, List


def create_ssh_config(hosts: List[Dict[str, str]]) -> str:
    config = {host["host_name"]: host for host in hosts}
    return json.dumps(config, indent=2, ensure_ascii=False)


hosts = [
    {
        "host_name": "web",
        "ip_address": "192.168.1.1",
        "port": "22",
        "username": "user",
        "password": "pw",
        "password_prompt": "Password:",
        "command_prompt": "$",
        "logout_command": "exit",
        "connect_type": "ssh",
        "key_filename": "",
        "gateway": [],
    },
    {
        "host_name": "app",
        "ip_address": "192.168.1.2",
        "port": "22",
        "username": "user",
        "password": "pw",
        "password_prompt": "Password:",
        "command_prompt": "$",
        "logout_command": "exit",
        "connect_type": "ssh",
        "key_filename": "",
        "gateway": [],
    },
    {
        "host_name": "app2",
        "ip_address": "192.168.1.2",
        "port": "22",
        "username": "user",
        "password": "pw",
        "password_prompt": "Password:",
        "command_prompt": "$",
        "logout_command": "exit",
        "connect_type": "ssh",
        "key_filename": "",
        "gateway": [],
    },
]

config = create_ssh_config(hosts)
fn = "ssh_host.json"

with open(fn, "w", encoding="utf-8") as f:
    f.write(config)

print(f"SSH設定ファイルが生成されました: {fn}")
