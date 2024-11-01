import os
from typing import Any, List

from .config_loader import load_json_file
from .session_interfaces import SessionManager, SessionStrategy
from .session_managers import BastionNode, TargetNode
from .sftp_strategy_paramiko import ParamikoSFTPSessionStrategy

# from .ssh_strategy_netmiko import NetmikoSSHSessionStrategy
from .ssh_strategy_paramiko import ParamikoSSHSessionStrategy
from .ssh_strategy_paramiko_intaract import ParamikoSSHIntaractSessionStrategy
from .ssh_strategy_paramiko_pod import ParamikoSSHSessionStrategyPod


class SessionManagerFactory:
    def __init__(self, config_file: str = "ssh_host.json"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(current_dir, config_file)
        self.ssh_configs = load_json_file(config_file)

    def create_session(self, host_name: str) -> SessionManager:
        """
        Facade method to create and establish a single session.
        """
        return self.create_sessions(host_name)[-1]

    def create_sessions(self, host_name: str) -> List[SessionManager]:
        """
        Facade method to create and establish all required sessions including bastions.
        """
        ssh_config = self._get_config(host_name)
        hosts = self._create_bastions(ssh_config.get("bastions", []))
        hosts.append(self._create_target(host_name))
        self._establish_connection(hosts)
        return hosts

    def _get_config(self, host_name: str) -> dict:
        if host_name not in self.ssh_configs:
            raise ValueError(f"No configuration found for host: {host_name}")
        return self.ssh_configs[host_name]

    def _create_bastions(self, host_names: List[str]) -> List[SessionManager]:
        return [self._create_bastion(bastion) for bastion in host_names]

    def _create_bastion(self, host_name: str) -> SessionManager:
        session_strategy = self._create_session_strategy(host_name)
        return BastionNode(host_name, session_strategy)

    def _create_target(self, host_name: str) -> SessionManager:
        session_strategy = self._create_session_strategy(host_name)
        return TargetNode(host_name, session_strategy)

    def _create_session_strategy(self, host_name: str) -> Any:
        ssh_config = self.ssh_configs[host_name]
        connect_type = ssh_config.get("connect_type", "")

        if connect_type == "paramiko_intaract":
            return ParamikoSSHIntaractSessionStrategy(
                ip_address=ssh_config["ip_address"],
                username=ssh_config["username"],
                password=ssh_config.get("password"),
                key_filename=ssh_config.get("key_filename"),
                command_prompt=ssh_config["command_prompt"],
                logout_command=ssh_config["logout_command"],
                port=ssh_config["port"],
                timeout=ssh_config["timeout"],
            )
        elif connect_type == "paramiko_pod":
            return ParamikoSSHSessionStrategyPod(
                hostname=ssh_config["hostname"],
                username=ssh_config["username"],
                password=ssh_config["password"],
                bastion_user=ssh_config["bastion_user"],
                timeout=ssh_config.get("timeout"),
            )
        elif connect_type == "paramiko_sftp":
            return ParamikoSFTPSessionStrategy(
                ip_address=ssh_config["ip_address"],
                username=ssh_config["username"],
                password=ssh_config["password"],
                key_filename=ssh_config["key_filename"],
                # port=ssh_config["port"],
                # timeout=ssh_config["timeout"],
            )
        else:
            return ParamikoSSHSessionStrategy(
                ip_address=ssh_config["ip_address"],
                username=ssh_config["username"],
                password=ssh_config["password"],
                key_filename=ssh_config["key_filename"],
                # port=ssh_config["port"],
                # timeout=ssh_config["timeout"],
            )

    def _establish_connection(self, hosts: List[Any]) -> None:
        ini_host, *remaining_hosts = hosts

        try:
            if remaining_hosts:
                for host in remaining_hosts:
                    ini_host.add(host)
                ini_host.start_session_all()
            else:
                ini_host.start_session()
        except Exception as e:
            raise ConnectionError(f"Failed to establish connection: {e}")
