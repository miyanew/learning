import json
from typing import List, Dict

def create_ssh_config(hosts: List[Dict[str, str]]) -> str:
    config = {host["host_name"]: host for host in hosts}
    return json.dumps(config, indent=2, ensure_ascii=False)

hosts = [
    {
        "host_name": "web",
        "ip_address": "192.168.1.1",
        "port": "22",
        "user_name": "user",
        "password": "pw"
    },
    {
        "host_name": "app",
        "ip_address": "192.168.1.2",
        "port": "22",
        "user_name": "user",
        "password": "pw"
    }
]

config = create_ssh_config(hosts)
fn = "ssh_host.json"

with open(fn, "w", encoding="utf-8") as f:
    f.write(config)

print(f"SSH設定ファイルが生成されました: {fn}")
