from typing import Any, List, Optional

from .abstract_session_manager import SessionManager
from .connect_strategy_new_session import NewSessionStrategy
from .sendln_strategy_general_send_command import GeneralSendCommandStrategy


class BastionNode(SessionManager):
    def __init__(self, host_name: str, ssh_config: dict):
        self.host_name = host_name
        self.ssh_config = ssh_config
        self.connect_strategy = None
        self.sendln_strategy = None
        self.session = None
        self.parent_session = None
        self.child_nodes: List[SessionManager] = []

    def build(self) -> "BastionNode":
        self.connect_strategy = NewSessionStrategy(
            host_name=self.host_name,
            ip_address=self.ssh_config["ip_address"],
            username=self.ssh_config["username"],
            password=self.ssh_config["password"],
            key_filename=self.ssh_config["key_filename"],
            port=self.ssh_config.get("port"),
            timeout=self.ssh_config.get("timeout"),
        )

        self.sendln_strategy = GeneralSendCommandStrategy()
        return self

    def connect(self, parent_session: Optional[Any] = None) -> None:
        self.session = self.connect_strategy.connect(parent_session)

    def connect_all(self) -> None:
        self.connect(self.parent_session)
        for child_node in self.child_nodes:
            child_node.connect(self.session)

    def disconnect(self) -> None:
        self.session = self.connect_strategy.disconnect(self.session)

    def disconnect_all(self) -> None:
        for child_node in self.child_nodes:
            child_node.disconnect()
        self.disconnect()

    def send_command(self, command: str) -> str:
        if self.session is None:
            raise ConnectionError("Not connected")
        return self.sendln_strategy.send_command(self.session, command)

    def add(self, session_manager) -> None:
        session_manager.set_parent(self)
        self.child_nodes.append(session_manager)
