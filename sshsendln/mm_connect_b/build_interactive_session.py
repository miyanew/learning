from typing import List

from .abstract_builder import SessionBuilder
from .abstract_session_manager import SessionManager
from .connect_strategy_invoke_shell import InvokeShellStrategy
from .connect_strategy_new_session import NewSessionStrategy
from .sendln_strategy_interactive_cxc import InteractiveCxcStrategy
from .session_manager_bastion import BastionNode
from .session_manager_target import TargetNode


class InteractiveSessionBuilder(SessionBuilder):
    def __init__(self, host_name, ssh_configs):
        super().__init__(host_name)
        self.ssh_configs = ssh_configs
        self.host_config = self.get_config()
        self.hosts: List[SessionManager] = []
        self.session_manager = None

    def get_instance(self):
        return self.hosts[-1]

    def get_config(self):
        return self.ssh_configs[self.host_name]

    def create_hosts(self):
        self._create_bastions()
        self._create_target()

    def _create_bastions(self):
        host_names = self.host_config.get("bastions", [])

        for i, host_name in enumerate(host_names):
            ssh_config = self.ssh_configs[host_name]

            if i == 0:
                session_strategy = NewSessionStrategy(
                    host_name=host_name,
                    ip_address=ssh_config["ip_address"],
                    username=ssh_config["username"],
                    password=ssh_config["password"],
                    key_filename=ssh_config["key_filename"],
                    port=ssh_config.get("port"),
                    timeout=ssh_config.get("timeout"),
                )
            elif self.ssh_configs[host_names[i - 1]].get("allow_tcpforwading"):
                session_strategy = NewSessionStrategy(
                    host_name=host_name,
                    ip_address=ssh_config["ip_address"],
                    username=ssh_config["username"],
                    password=ssh_config["password"],
                    key_filename=ssh_config["key_filename"],
                    port=ssh_config.get("port"),
                    timeout=ssh_config.get("timeout"),
                )
            else:
                session_strategy = InvokeShellStrategy(
                    host_name=host_name,
                    ip_address=ssh_config["ip_address"],
                    username=ssh_config["username"],
                    password=ssh_config["password"],
                    key_filename=ssh_config["key_filename"],
                    prompt_host=ssh_config["prompt_host"],
                    port=ssh_config.get("port"),
                    timeout=ssh_config.get("timeout"),
                )
            self.hosts.append(BastionNode(host_name, session_strategy))

    def _create_target(self):
        ssh_config = self.ssh_configs[self.host_name]

        if self.ssh_configs[self.hosts[-1].host_name].get("allow_tcpforwading"):
            session_strategy = NewSessionStrategy(
                host_name=self.host_name,
                ip_address=ssh_config["ip_address"],
                username=ssh_config["username"],
                password=ssh_config["password"],
                key_filename=ssh_config["key_filename"],
                port=ssh_config.get("port"),
                timeout=ssh_config.get("timeout"),
            )
        else:
            session_strategy = InvokeShellStrategy(
                host_name=self.host_name,
                ip_address=ssh_config["ip_address"],
                username=ssh_config["username"],
                password=ssh_config["password"],
                key_filename=ssh_config["key_filename"],
                prompt_host=ssh_config["prompt_host"],
                port=ssh_config.get("port"),
                timeout=ssh_config.get("timeout"),
            )

        send_line_strategy = InteractiveCxcStrategy(session_strategy)

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
