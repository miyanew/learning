from typing import Any, List, Optional

from .abstract_session_manager import SessionManager


class BastionNode(SessionManager):
    def __init__(self, host_name: str, session_strategy):
        self.host_name = host_name
        self.session_strategy = session_strategy
        self.session = None
        self.parent_session = None
        self.child_nodes: List[SessionManager] = []

    def start_session(self, parent_session: Optional[Any] = None) -> None:
        self.session = self.session_strategy.start_session(parent_session)

    def start_session_all(self) -> None:
        self.start_session(self.parent_session)
        for child_node in self.child_nodes:
            child_node.start_session(self.session)

    def end_session(self) -> None:
        self.session = self.session_strategy.end_session(self.session)

    def end_session_all(self) -> None:
        for child_node in self.child_nodes:
            child_node.end_session()
        self.end_session()

    def send_command(self, command: str) -> str:
        if self.session is None:
            raise ConnectionError("Not connected")
        return self.session_strategy.send_command(self.session, command)

    def add(self, session_manager) -> None:
        session_manager.set_parent(self)
        self.child_nodes.append(session_manager)
