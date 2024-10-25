from .session_interfaces import SessionManager, SessionStrategy
from typing import Any, Optional

class TargetNode(SessionManager):
    def __init__(self, host_name: str, session_strategy: SessionStrategy):
        self.host_name = host_name
        self.session_strategy = session_strategy
        self.session = None
        self.parent_session = None

    # def start_session(self) -> None:
    #     self.session = self.session_strategy.start_session(self.session)

    def start_session(self, parent_session: Optional[Any] = None) -> None:
        self.session = self.session_strategy.start_session(parent_session)

    def end_session(self) -> None:
        self.session = self.session_strategy.end_session(self.session)

    def send_command(self, command: str) -> str:
        if self.session is None:
            raise ConnectionError("Not connected")
        return self.session_strategy.send_command(self.session, command)


class BastionNode(SessionManager):
    def __init__(self, host_name: str, session_strategy: SessionStrategy):
        self.host_name = host_name
        self.session_strategy = session_strategy
        self.session = None
        self.parent_session = None
        self.next_nodes = []

    def start_session(self, parent_session: Optional[Any] = None) -> None:
        self.session = self.session_strategy.start_session(parent_session)

    def start_session_all(self) -> None:
        self.start_session(self.parent_session)
        for next_hop in self.next_nodes:
            next_hop.start_session(self.session)

    def end_session(self) -> None:
        self.session = self.session_strategy.end_session(self.session)

    def end_session_all(self) -> None:
        for next_hop in self.next_nodes:
            next_hop.end_session()
        self.end_session()

    def send_command(self, command: str) -> str:
        if self.session is None:
            raise ConnectionError("Not connected")
        return self.session_strategy.send_command(self.session, command)

    def add(self, session_manager: SessionManager) -> None:
        session_manager.set_parent(self)
        self.next_nodes.append(session_manager)
