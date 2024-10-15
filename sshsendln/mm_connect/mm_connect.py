import os
from typing import Any, Dict

from .session_managers import BastionServer, LeafServer
from .ssh_config_loader import load_json_file
from .ssh_strategy_netmiko import NetmikoSSHSessionStrategy
from .ssh_strategy_paramiko import ParamikoSSHSessionStrategy
from .ssh_strategy_pexpect import PexpectSSHSessionStrategy

current_dir = os.path.dirname(os.path.abspath(__file__))


def get_host(host_name: str) -> str:
    ssh_configs = load_json_file(os.path.join(current_dir, "ssh_host.json"))
    ssh_config = ssh_configs[host_name]

    hops = []

    connect_type = ssh_config["connect_type"]
    if connect_type == "ssh":
        hops.append(session_ssh_netmiko(host_name, ssh_config))
        # hops.append(session_ssh_pexpect(host_name, ssh_config))
        # hops.append(session_ssh_paramiko(host_name, ssh_config))
    elif connect_type == "sftp":
        hops.append(session_ssh_pexpect(host_name, ssh_config))

    return hops[0]


def session_ssh_pexpect(host_name: str, ssh_config: Dict[str, Any]):
    session_strategy = PexpectSSHSessionStrategy(
        ip_address=ssh_config["ip_address"],
        username=ssh_config["username"],
        password=ssh_config["password"],
        password_prompt=ssh_config["password_prompt"],
        key_filename=ssh_config["key_filename"],
        command_prompt=ssh_config["command_prompt"],
        logout_command=ssh_config["logout_command"],
    )
    return LeafServer(host_name, session_strategy)


def session_ssh_paramiko(host_name: str, ssh_config: Dict[str, Any]):
    session_strategy = ParamikoSSHSessionStrategy(
        ip_address=ssh_config["ip_address"],
        username=ssh_config["username"],
        password=ssh_config["password"],
        key_filename=ssh_config["key_filename"],
    )
    return LeafServer(host_name, session_strategy)


def session_ssh_netmiko(host_name: str, ssh_config: Dict[str, Any]):
    session_strategy = NetmikoSSHSessionStrategy(
        ip_address=ssh_config["ip_address"],
        username=ssh_config["username"],
        password=ssh_config["password"],
        device_type="linux",
        key_filename=ssh_config["key_filename"],
    )
    return LeafServer(host_name, session_strategy)
