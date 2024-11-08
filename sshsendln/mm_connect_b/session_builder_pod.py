from typing import List

from .abstract_builder import SessionBuilder
from .abstract_session_manager import BastionNode, SessionManager, TargetNode
from .sendln_strategy_pod import SendLineStrategyPod
from .ssh_strategy_paramiko import ParamikoSSHSessionStrategy
from .ssh_strategy_paramiko_pod import ParamikoSSHSessionStrategyPod


class SessionBuilderPod(SessionBuilder):
    def __init__(self, host_name, ssh_configs):
        super().__init__(host_name)
        self.ssh_configs = ssh_configs
        self.host_config = self.get_config()
        self.hosts: List[SessionManager] = []
        self.session_manager = None

    def get_instance_pod(self):
        return self.hosts[-1]

    def get_config(self):
        return self.ssh_configs[self.host_name]

    def create_hosts(self):
        self._create_bastions()
        self._create_target()

    def _create_bastions(self):
        host_names = self.host_config.get("bastions", [])
        self.hosts = [self._create_bastion(bastion) for bastion in host_names]

    def _create_bastion(self, host_name: str):
        ssh_config = self.ssh_configs[host_name]
        session_strategy = ParamikoSSHSessionStrategy(
            ip_address=ssh_config["ip_address"],
            username=ssh_config["username"],
            password=ssh_config["password"],
            key_filename=ssh_config["key_filename"],
        )

        return BastionNode(host_name, session_strategy)

    def _create_target(self):
        ssh_config = self.ssh_configs[self.host_name]
        session_strategy = ParamikoSSHSessionStrategyPod(
            hostname=self.host_name,
            username=ssh_config["username"],
            password=ssh_config["password"],
            bastion_user=ssh_config.get("bastion_user"),
            timeout=ssh_config.get("timeout"),
        )
        send_line_strategy = SendLineStrategyPod(session_strategy)

        self.hosts.append(
            TargetNode(self.host_name, session_strategy, send_line_strategy)
        )

    def establish_connection(self) -> None:
        ini_host, *remaining_hosts = self.hosts

        try:
            if remaining_hosts:
                for host in remaining_hosts:
                    ini_host.add(host)
                ini_host.start_session_all()
            else:
                ini_host.start_session()
        except Exception as e:
            raise ConnectionError(f"Failed to establish connection: {e}")
