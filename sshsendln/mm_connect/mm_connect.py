import os
from typing import Any, Dict, List

from .config_loader import load_json_file
from .session_interfaces import SessionManager, SessionStrategy
from .session_managers import BastionServer, LeafServer

# from .ssh_strategy_netmiko import NetmikoSSHSessionStrategy
from .ssh_strategy_paramiko import ParamikoSSHSessionStrategy
from .ssh_strategy_pexpect import PexpectSSHSessionStrategy

# from .sftp_strategy_paramiko import ParamikoSFTPSessionStrategy
# from .sftp_strategy_pexpect import PexpectSFTPSessionStrategy

current_dir = os.path.dirname(os.path.abspath(__file__))


class SSHConnectionManager:
    def __init__(self, config_file: str = "ssh_host.json"):
        config_file = os.path.join(current_dir, config_file)
        self.ssh_configs = load_json_file(config_file)

    def get_hosts(self, host_name: str) -> List[SessionManager]:
        ssh_config = self.ssh_configs.get(host_name)
        if not ssh_config:
            raise ValueError(f"No configuration found for host: {host_name}")

        hosts = self._set_jump_hosts(ssh_config.get("jump_hosts", []))
        hosts.append(self._set_leaf_host(host_name))
        self._establish_connection(hosts)
        return hosts

    def get_host(self, host_name: str) -> SessionManager:
        """Get the leaf host for the given host name.

        Args:
            host_name: Name of the host to get configuration for

        Returns:
            The leaf host configuration

        Raises:
            ValueError: If no configuration exists for the host name
        """
        hosts = self.get_hosts(host_name)
        if not hosts:
            raise IndexError("No hosts found after configuration")
        return hosts[-1]

    def _set_jump_hosts(self, jump_host_names: List[str]) -> List[SessionManager]:
        return [self._set_jump_host(jump_host) for jump_host in jump_host_names]

    def _set_jump_host(self, host_name: str) -> SessionManager:
        session_strategy = self._get_session_strategy(host_name)
        return BastionServer(host_name, session_strategy)

    def _set_leaf_host(self, host_name: str) -> SessionManager:
        session_strategy = self._get_session_strategy(host_name)
        return LeafServer(host_name, session_strategy)

    def _get_session_strategy(self, host_name: str) -> Any:
        library = "pexpect"
        ssh_config = self.ssh_configs[host_name]
        connect_type = ssh_config["connect_type"]

        if library == "pexpect":
            if connect_type == "ssh":
                return PexpectSSHSessionStrategy(
                    ip_address=ssh_config["ip_address"],
                    username=ssh_config["username"],
                    password=ssh_config["password"],
                    password_prompt=ssh_config["password_prompt"],
                    key_filename=ssh_config["key_filename"],
                    command_prompt=ssh_config["command_prompt"],
                    logout_command=ssh_config["logout_command"],
                )
            # else:
            #     return PexpectSFTPSessionStrategy(
            #         ip_address=ssh_config["ip_address"],
            #         username=ssh_config["username"],
            #         password=ssh_config["password"],
            #         password_prompt=ssh_config["password_prompt"],
            #         key_filename=ssh_config["key_filename"],
            #         command_prompt=ssh_config["command_prompt"],
            #         logout_command=ssh_config["logout_command"],
            #     )
        elif library == "paramiko":
            if connect_type in ["ssh"]:
                return ParamikoSSHSessionStrategy(
                    ip_address=ssh_config["ip_address"],
                    username=ssh_config["username"],
                    password=ssh_config["password"],
                    key_filename=ssh_config["key_filename"],
                )
            # else:
            #     return ParamikoSFTPSessionStrategy(
            #         ip_address=ssh_config["ip_address"],
            #         username=ssh_config["username"],
            #         password=ssh_config["password"],
            #         key_filename=ssh_config["key_filename"],
            # )
        else:
            ValueError(f"Unsupported connection type: {connect_type}")

    def _establish_connection(self, hosts: List[Any]) -> None:
        ini_host, *remaining_hosts = hosts

        try:
            if remaining_hosts:
                for host in remaining_hosts:
                    ini_host.add(host)
                ini_host.connect_all()
            else:
                ini_host.connect()
        except Exception as e:
            raise ConnectionError(f"Failed to establish connection: {e}")


# def session_ssh_netmiko(host_name: str, ssh_config: Dict[str, Any]):
#     session_strategy = NetmikoSSHSessionStrategy(
#         ip_address=ssh_config["ip_address"],
#         username=ssh_config["username"],
#         password=ssh_config["password"],
#         device_type="linux",
#         key_filename=ssh_config["key_filename"],
#     )
#     return LeafServer(host_name, session_strategy)
