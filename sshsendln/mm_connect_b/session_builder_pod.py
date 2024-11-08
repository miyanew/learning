from .abstract_session_builder import SessionBuilder
from .abstract_session_manager import SessionManager, BastionNode, TargetNode
from .ssh_strategy_paramiko_pod import ParamikoSSHSessionStrategyPod
from typing import List


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

    def create_bastions(self):
        host_names = self.host_config.get("bastions", [])
        self.hosts = [self._create_bastion(bastion) for bastion in host_names]

    def _create_bastion(self, host_name: str):
        session_strategy = self._create_session_strategy(host_name)
        return BastionNode(host_name, session_strategy)

    def create_target(self):
        session_strategy = self._create_session_strategy(self.host_name)
        self.hosts.append(TargetNode(self.host_name, session_strategy))

    def _create_session_strategy(self, host_name: str):
        ssh_config = self.ssh_configs[host_name]
        return ParamikoSSHSessionStrategyPod(
            hostname=host_name,
            username=ssh_config["username"],
            password=ssh_config["password"],
            bastion_user=ssh_config.get("bastion_user"),
            timeout=ssh_config.get("timeout"),
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
