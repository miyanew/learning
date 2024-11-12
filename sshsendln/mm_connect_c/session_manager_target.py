from typing import Any, List, Optional

from .abstract_session_manager import SessionManager
from .connect_strategy_new_session import NewSessionStrategy
from .connect_strategy_oc_login import OcLoginStrategy
from .sendln_strategy_general_send_command import GeneralSendCommandStrategy
from .sendln_strategy_interactive_cxc import InteractiveCxcStrategy
from .sendln_strategy_pod import SendLineStrategyPod


class TargetNode(SessionManager):
    def __init__(
        self, host_name: str, ssh_config: dict, bastions: List[SessionManager]
    ):
        self.host_name = host_name
        self.ssh_config = ssh_config
        self.connect_strategy = None
        self.sendln_strategy = None
        self.session = None
        # self.bastions = bastions

    def build(self) -> 'TargetNode':
        self._setup_strategies()
        return self

    def _setup_strategies(self) -> None:
        node_type = self.ssh_config.get("node_type")
        if node_type == "pod":
            self.connect_strategy = self._create_oc_login_strategy()
            self.sendln_strategy = SendLineStrategyPod(self.connect_strategy)
        elif node_type == "interactive":
            self.connect_strategy = self._create_new_session_strategy()
            self.sendln_strategy = InteractiveCxcStrategy(self.connect_strategy)
        else:
            self.connect_strategy = self._create_new_session_strategy()
            self.sendln_strategy = GeneralSendCommandStrategy()

    def _create_oc_login_strategy(self) -> OcLoginStrategy:
        return OcLoginStrategy(
            hostname=self.host_name,
            username=self.ssh_config["username"],
            password=self.ssh_config["password"],
            bastion_user=self.ssh_config["bastion_user"],
            timeout=self.ssh_config.get("timeout"),
        )

    def _create_new_session_strategy(self) -> NewSessionStrategy:
        return NewSessionStrategy(
            host_name=self.host_name,
            ip_address=self.ssh_config["ip_address"],
            username=self.ssh_config["username"],
            password=self.ssh_config["password"],
            key_filename=self.ssh_config["key_filename"],
            port=self.ssh_config.get("port"),
            timeout=self.ssh_config.get("timeout"),
        )

    def connect(self, parent_session: Optional[Any] = None) -> None:
        self.session = self.connect_strategy.connect(parent_session)

    def disconnect(self) -> None:
        self.session = self.connect_strategy.disconnect(self.session)

    def send_command(self, command: str, timeout: float = 30.0) -> str:
        if self.session is None:
            raise ConnectionError("Not connected")
        return self.sendln_strategy.send_command(self.session, command, timeout)
