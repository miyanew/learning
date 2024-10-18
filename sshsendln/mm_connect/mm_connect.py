import os
from typing import Any, Dict, List

from .session_managers import BastionServer, LeafServer
from .config_loader import load_json_file

# from .ssh_strategy_netmiko import NetmikoSSHSessionStrategy
from .ssh_strategy_paramiko import ParamikoSSHSessionStrategy
from .ssh_strategy_pexpect import PexpectSSHSessionStrategy

current_dir = os.path.dirname(os.path.abspath(__file__))


class SSHConnectionManager:
    def __init__(self, config_file: str = "ssh_host.json"):
        config_file = os.path.join(current_dir, config_file)
        self.ssh_configs = load_json_file(config_file)

    def get_connections(self, host_name: str) -> List[Any]:
        ssh_config = self.ssh_configs.get(host_name)
        if not ssh_config:
            raise ValueError(f"No configuration found for host: {host_name}")

        connections = []
        connect_type = ssh_config["connect_type"]

        if connect_type in ["ssh", "ssh_key"]:
            connections.append(self._create_ssh_session(host_name, ssh_config))
        elif connect_type == "sftp":
            # Implement SFTP connection logic here
            pass
        else:
            raise ValueError(f"Unsupported connection type: {connect_type}")

        self._establish_connection(connections)
        return connections

    def _create_ssh_session(self, host_name: str, ssh_config: Dict[str, Any]) -> Any:
        return session_ssh_pexpect(host_name, ssh_config)

    def _establish_connection(self, connections: List[Any]) -> None:
        try:
            if len(connections) > 1:
                connections[0].connect_all()
            else:
                connections[0].connect()
        except Exception as e:
            raise ConnectionError(f"Failed to establish connection: {e}")


# def get_host(host_name: str) -> list:
#     ssh_configs = load_json_file(os.path.join(current_dir, "ssh_host.json"))
#     ssh_config = ssh_configs[host_name]

#     hops = []

#     connect_type = ssh_config["connect_type"]
#     if connect_type in ["ssh", "ssh_key"]:
#         hops.append(session_ssh_pexpect(host_name, ssh_config))
#         # hops.append(session_ssh_paramiko(host_name, ssh_config))
#         # hops.append(session_ssh_netmiko(host_name, ssh_config))
#     elif connect_type == "sftp":
#         pass

#     try:
#         hops[0].connect()
#     except Exception as e:
#         print(e)

#     return hops


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


# def session_ssh_netmiko(host_name: str, ssh_config: Dict[str, Any]):
#     session_strategy = NetmikoSSHSessionStrategy(
#         ip_address=ssh_config["ip_address"],
#         username=ssh_config["username"],
#         password=ssh_config["password"],
#         device_type="linux",
#         key_filename=ssh_config["key_filename"],
#     )
#     return LeafServer(host_name, session_strategy)
