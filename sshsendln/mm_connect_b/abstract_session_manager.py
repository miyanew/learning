from abc import ABC, abstractmethod
from typing import Any, List, Optional


class SessionManager(ABC):
    def __init__(self, host_name: str) -> None:
        self.host_name = host_name
        self.parent_session: Optional["SessionManager"] = None

    def set_parent(self, parent_session: "SessionManager") -> None:
        self.parent_session = parent_session

    @abstractmethod
    def start_session(self) -> Any:
        pass

    @abstractmethod
    def end_session(self) -> None:
        pass

    @abstractmethod
    def send_command(self) -> str:
        pass

    def get_session_chain(self) -> List["SessionManager"]:
        chain: List["SessionManager"] = []
        current_session: Optional["SessionManager"] = self
        while current_session:
            chain.insert(0, current_session)
            current_session = current_session.parent_session
        return chain

    def end_session_all(self) -> None:
        for session in reversed(self.get_session_chain()):
            session.end_session()


class TargetNode(SessionManager):
    def __init__(self, host_name: str, session_strategy, send_command_strategy):
        self.host_name = host_name
        self.session_strategy = session_strategy
        self.send_command_strategy = send_command_strategy
        self.session = None
        self.parent_session = None

    def start_session(self, parent_session: Optional[Any] = None) -> None:
        self.session = self.session_strategy.start_session(parent_session)

    def end_session(self) -> None:
        self.session = self.session_strategy.end_session(self.session)

    def send_command(self, command: str, timeout: float = 30.0) -> str:
        if self.session is None:
            raise ConnectionError("Not connected")
        return self.send_command_strategy.send_command(self.session, command, timeout)


class BastionNode(SessionManager):
    def __init__(self, host_name: str, session_strategy):
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

    def add(self, session_manager) -> None:
        session_manager.set_parent(self)
        self.next_nodes.append(session_manager)
